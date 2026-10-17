"""Verified library transfer; old files are removed only after a successful start."""

import hashlib
import json
import os
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4

CONTROL_FILE = 'data-location.json'
TRANSFER_FILE = 'library-transfer.json'
EXCLUDED = {'dev-runtime', 'updates', 'diagnostics', 'logs', CONTROL_FILE, TRANSFER_FILE}


def default_root():
    return Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'BiliClass'


def selected_directory():
    selector = default_root() / CONTROL_FILE
    if not selector.exists():
        return default_root()
    directory = Path(json.loads(selector.read_text(encoding='utf-8'))['directory'])
    if not (directory / 'library.db').is_file():
        raise ValueError('Không tìm thấy thư viện đã chọn: ' + str(directory) + '. Kết nối lại ổ lưu dữ liệu rồi mở BiliClass.')
    return directory


def select_directory(directory):
    directory = Path(directory).resolve(strict=True)
    if not (directory / 'library.db').is_file():
        raise ValueError('Thư mục chưa có thư viện BiliClass.')
    with closing(sqlite3.connect((directory / 'library.db').as_uri() + '?mode=ro', uri=True)) as database:
        tables = {row[0] for row in database.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'lessons', 'settings'}.issubset(tables) or database.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('Thư viện chưa hợp lệ; vẫn giữ nơi lưu hiện tại.')
    selector = default_root() / CONTROL_FILE
    selector.parent.mkdir(parents=True, exist_ok=True)
    pending = selector.with_suffix('.tmp')
    pending.write_text(json.dumps({'directory': str(directory)}, ensure_ascii=False), encoding='utf-8')
    pending.replace(selector)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_record(path, record):
    pending = path.with_name(path.name + '.' + uuid4().hex + '.tmp')
    try:
        pending.write_text(json.dumps(record, ensure_ascii=False), encoding='utf-8')
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)


def inventory(source):
    source = Path(source).resolve(strict=True)
    files = []
    for parent, directories, names in os.walk(source, followlinks=False):
        base = Path(parent)
        directories[:] = [name for name in directories if not (base == source and name in EXCLUDED)]
        for name in directories + names:
            path = base / name
            if path.is_symlink() or path.is_junction():
                raise ValueError('Thư viện có liên kết thư mục/tệp; hãy chọn bản dữ liệu lưu trực tiếp.')
        for name in names:
            path = base / name
            if base == source and name in EXCLUDED or name.endswith(('-wal', '-shm', '-journal')):
                continue
            files.append(path.relative_to(source).as_posix())
    return sorted(files)


def validate_destination(source, target):
    source, target = Path(source).resolve(strict=True), Path(target).resolve()
    if target == source or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Chọn thư mục riêng, không nằm trong hoặc bao ngoài thư viện hiện tại.')
    if target.exists():
        raise ValueError('Thư mục BiliClass-Data đã tồn tại. Chọn nơi khác để không ghi đè dữ liệu.')
    if not target.parent.is_dir() or target.parent.is_symlink() or target.parent.is_junction():
        raise ValueError('Chọn thư mục có thật trên ổ lưu dữ liệu.')
    return source, target


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix in {'.db', '.sqlite', '.sqlite3'}:
        with closing(sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True)) as original:
            with closing(sqlite3.connect(target)) as snapshot:
                original.backup(snapshot)
                if snapshot.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise ValueError('Không xác minh được cơ sở dữ liệu.')
    else:
        shutil.copy2(source, target)
        if digest(source) != digest(target):
            raise ValueError('Tệp sao chép chưa khớp: ' + source.name)


def transfer(source, target, progress=None):
    source, target = validate_destination(source, target)
    names = inventory(source)
    total = sum((source / name).stat().st_size for name in names)
    if shutil.disk_usage(target.parent).free < total + max(64 * 1024**2, total // 20):
        raise ValueError('Ổ đích chưa đủ chỗ cho cả thư viện và vùng làm việc.')
    staging = target.parent / ('.biliclass-transfer-' + uuid4().hex)
    staging.mkdir()
    try:
        for index, name in enumerate(names, 1):
            copy_file(source / name, staging / name)
            if progress:
                progress(index, len(names))
        # Publish only a complete destination. Never merge into an existing folder.
        if target.exists():
            raise ValueError('Thư mục đích vừa được tạo bởi tác vụ khác; chưa chuyển thư viện.')
        staging.rename(target)
    except BaseException:
        # This folder was created by this transfer, beneath the checked parent.
        if staging.parent == target.parent and staging.name.startswith('.biliclass-transfer-'):
            shutil.rmtree(staging, ignore_errors=True)
        raise
    return {'source': str(source), 'target': str(target), 'files': names, 'bytes': total}


def rebase(value, source, target):
    if isinstance(value, dict):
        return {key: rebase(item, source, target) for key, item in value.items()}
    if isinstance(value, list):
        return [rebase(item, source, target) for item in value]
    if isinstance(value, str):
        for old, new in ((str(source), str(target)), (source.as_posix(), target.as_posix()),
                         (source.as_uri(), target.as_uri())):
            if value == old or value.startswith(old + '/') or value.startswith(old + '\\'):
                return new + value[len(old):]
    return value


def finalize_transfer(record, progress=None):
    """After every old-library worker/connection has closed, refresh and rebase."""
    source, target = Path(record['source']).resolve(strict=True), Path(record['target']).resolve(strict=True)
    if source == target or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Đường dẫn chuyển thư viện không hợp lệ.')
    names = inventory(source)
    verified = {}
    for index, name in enumerate(names, 1):
        original, copied = source / name, target / name
        original_hash = digest(original)
        copied_hash = digest(copied) if copied.is_file() else None
        if original.suffix in {'.db', '.sqlite', '.sqlite3'} or original_hash != copied_hash:
            copy_file(original, copied)
            copied_hash = digest(copied)
        if copied.suffix == '.json':
            try:
                value = json.loads(copied.read_text(encoding='utf-8'))
            except (ValueError, UnicodeError):
                pass
            else:
                updated = rebase(value, source, target)
                if value != updated:
                    write_record(copied, updated)
                    copied_hash = digest(copied)
        verified[name] = {'source': original_hash, 'target': copied_hash}
        if progress:
            progress(index, len(names))
    database = target / 'library.db'
    with closing(sqlite3.connect(database)) as db:
        for table, column in [('lessons', 'content'), ('lesson_revisions', 'content'), ('settings', 'value')]:
            for rowid, raw in db.execute(f'SELECT rowid,{column} FROM {table}').fetchall():
                value = json.loads(raw)
                updated = rebase(value, source, target)
                if value != updated:
                    db.execute(f'UPDATE {table} SET {column}=? WHERE rowid=?', (json.dumps(updated, ensure_ascii=False), rowid))
        db.commit()
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    # Only the database changed after the file pass. Do not reread every model,
    # source deck and WAV a second time just to build the transfer manifest.
    verified['library.db']['target'] = digest(database)
    manifest = {**record, 'files': verified, 'activated': False}
    write_record(target / TRANSFER_FILE, manifest)
    select_directory(target)
    return target


def verify_transfer_start(directory):
    """Run before opening the destination database, so corruption fails closed."""
    root = Path(directory).resolve()
    marker = root / TRANSFER_FILE
    if not marker.exists():
        return
    record = json.loads(marker.read_text(encoding='utf-8'))
    if Path(record['target']).resolve() != root:
        raise ValueError('Bản chuyển không thuộc thư mục đang mở.')
    if record.get('activated'):
        return
    for name, hashes in record['files'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or digest(path) != hashes['target']:
            raise ValueError('Bản chuyển thư viện chưa khớp. Bản gốc vẫn được giữ: ' + record['source'])


def cleanup_previous(directory):
    """Only call after the destination library and its UI have opened successfully."""
    root = Path(directory).resolve()
    marker = root / TRANSFER_FILE
    if not marker.exists():
        return 0
    record = json.loads(marker.read_text(encoding='utf-8'))
    if Path(record['target']).resolve() != root:
        raise ValueError('Bản chuyển không thuộc thư mục đang mở.')
    if record.get('cleaned'):
        return 0
    source = Path(record['source']).resolve(strict=True)
    if source == root or root.is_relative_to(source) or source.is_relative_to(root):
        raise ValueError('Không dọn được đường dẫn cũ.')
    # Startup already verified the destination before opening its databases.
    # Its live DB may now change normally, even if old-file cleanup is interrupted.
    record['activated'] = True
    write_record(marker, record)
    removed = 0
    for name, hashes in record['files'].items():
        old, new = (source / name).resolve(), (root / name).resolve()
        if not old.is_relative_to(source) or not new.is_relative_to(root) or old.name in EXCLUDED:
            raise ValueError('Đường dẫn trong bản chuyển không hợp lệ.')
        # A changed old file may belong to another process. Leave it untouched.
        if old.is_file() and new.is_file() and digest(old) == hashes['source']:
            old.unlink()
            removed += 1
    record['cleaned'] = True
    write_record(marker, record)
    return removed
