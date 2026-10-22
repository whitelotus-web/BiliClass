"""Consistent, bounded local backups and diagnostic logging without lesson text."""

import hashlib
import json
import logging
import os
import re
import sqlite3
import tempfile
import zipfile
from collections import Counter
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path, PurePosixPath

MAX_BACKUP_BYTES = 64 * 1024**3
MAX_RESTORE_BYTES = 128 * 1024**3
MAX_BACKUP_FILES = 200000
MAX_FILE_BYTES = 16 * 1024**3
MAX_MANIFEST_BYTES = 32 * 1024**2
CHUNK_BYTES = 1024**2
BACKUP_TREES = ('sources', 'audio', 'assets', 'templates', 'custom_templates', 'google_jobs', 'chatgpt')
BACKUP_SCOPE = ('Bài, lịch sử, cấu hình, giọng, mẫu, tác vụ chuyển đổi và dữ liệu lớp; '
                'không gồm model, key, phiên đăng nhập, cache.')


def _snapshot(database, target):
    source = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
    copied = sqlite3.connect(target)
    try:
        source.backup(copied)
        if copied.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Cơ sở dữ liệu chưa hợp lệ; bản sao lưu cũ được giữ.')
    finally:
        source.close()
        copied.close()


def _library_files(root):
    for category in BACKUP_TREES:
        folder = root / category
        if not folder.is_dir():
            continue
        if folder.is_symlink() or folder.is_junction():
            raise ValueError('Dữ liệu sao lưu có liên kết; chọn dữ liệu lưu trực tiếp.')
        for parent, directories, names in os.walk(folder, followlinks=False):
            for name in directories + names:
                path = Path(parent) / name
                if path.is_symlink() or path.is_junction():
                    raise ValueError('Dữ liệu sao lưu có liên kết; chọn dữ liệu lưu trực tiếp.')
            for name in names:
                path = Path(parent) / name
                if not name.endswith(('.tmp', '.pending', '.lock', '-wal', '-shm', '-journal')):
                    yield path.relative_to(root).as_posix(), path


def _check_space(parent, required):
    from .storage_space import require_space

    require_space(parent, required + 128 * 1024**2)


def prune_backups(folder, *, keep=14, budget=16 * 1024**3):
    """Keep the latest good automatic backup, even when it alone exceeds budget."""
    automatic = sorted((p for p in folder.glob('BiliClass-*.bcbackup')
                        if re.fullmatch(r'BiliClass-\d{8}\.bcbackup', p.name)), reverse=True)
    used = 0
    for index, path in enumerate(automatic):
        size = path.stat().st_size
        if index and (index >= keep or used + size > budget):
            path.unlink()
        else:
            used += size


def backup_state(directory):
    path = Path(directory) / 'backup-state.json'
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def record_backup(directory, *, path=None, error=None):
    from .library_location import write_record

    state = backup_state(directory)
    state.update(last_attempt=datetime.now().astimezone().isoformat(), running=False)
    if error:
        state.update(last_error=str(error), status='failed')
    elif path:
        stamp = Path(path).stat()
        state.update(last_success=state['last_attempt'], last_path=str(path),
                     last_bytes=stamp.st_size, last_mtime_ns=stamp.st_mtime_ns,
                     last_error='', status='passed')
    write_record(Path(directory) / 'backup-state.json', state)
    return state


def _copy_hashed(source, target, limit):
    """Bound memory and validate actual bytes, including files that grow mid-copy."""
    digest = hashlib.sha256()
    size = 0
    while chunk := source.read(CHUNK_BYTES):
        size += len(chunk)
        if size > limit:
            raise ValueError("Một tệp vượt giới hạn sao lưu/khôi phục.")
        digest.update(chunk)
        target.write(chunk)
    return digest.hexdigest()


def _file_signature(path):
    info = path.stat()
    return info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_ino


def _backup_plan(files, progress):
    """Hash possible duplicates only; never stage another copy of source files."""
    signatures = {name: _file_signature(path) for name, path in files}
    sizes = Counter(value[0] for value in signatures.values())
    hashes, originals, aliases = {}, {}, {}
    for index, (name, path) in enumerate(files, 1):
        signature = signatures[name]
        if sizes[signature[0]] > 1:
            digest, size = hashlib.sha256(), 0
            with path.open('rb') as source:
                while chunk := source.read(CHUNK_BYTES):
                    size += len(chunk)
                    if size > MAX_FILE_BYTES:
                        raise ValueError('Một tệp vượt giới hạn sao lưu/khôi phục.')
                    digest.update(chunk)
            if _file_signature(path) != signature:
                raise ValueError('Tệp thay đổi trong lúc sao lưu; hãy thử lại sau khi lưu bài xong.')
            hashes[name] = digest.hexdigest()
            key = size, hashes[name]
            if key in originals:
                aliases[name] = originals[key]
            else:
                originals[key] = name
        if progress:
            progress(index, len(files) * 2)
    return signatures, hashes, aliases


def _valid_backup_name(name):
    parts = PurePosixPath(name)
    valid = name in ('library.db', 'classroom.db') or (
        len(parts.parts) >= 2 and parts.parts[0] in BACKUP_TREES)
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
                *(f'LPT{i}' for i in range(1, 10))}
    return (valid and '..' not in parts.parts and ':' not in name and '\\' not in name
            and not parts.is_absolute() and parts.as_posix() == name
            and not any(part.endswith((' ', '.')) or part.split('.')[0].upper() in reserved
                        for part in parts.parts))


def configure_logging(directory):
    path = Path(directory) / "logs"
    path.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("biliclass")
    if not logger.handlers:
        handler = RotatingFileHandler(path / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def backup_library(directory, destination=None, daily=False, *, progress=None):
    try:
        return _create_backup(directory, destination, daily, progress=progress)
    except Exception as exc:
        try:
            record_backup(directory, error=exc)
        except OSError:
            pass  # A full disk must not hide the original failure.
        raise


def _create_backup(directory, destination=None, daily=False, *, progress=None):
    root = Path(directory)
    database = root / "library.db"
    if not database.exists():
        return None
    folder = root / "backups"
    folder.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d" if daily else "%Y%m%d-%H%M%S-%f")
    output = Path(destination) if destination else folder / f"BiliClass-{stamp}.bcbackup"
    if daily and output.exists():
        state, info = backup_state(root), output.stat()
        if (state.get('status') == 'passed' and state.get('last_path') == str(output)
                and state.get('last_bytes') == info.st_size and state.get('last_mtime_ns') == info.st_mtime_ns):
            return output  # Reuse our unchanged package without claiming a new backup time.
        # Unknown, failed or externally changed archives are replaced only after
        # a fresh snapshot has passed the normal checks below.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="biliclass-backup-", dir=output.parent) as work:
        snapshot = Path(work) / "library.db"
        _snapshot(database, snapshot)
        files = [("library.db", snapshot)]
        files.extend(_library_files(root))
        classroom_db = root / "classroom.db"
        if classroom_db.exists():
            class_snapshot = Path(work) / "classroom.db"
            _snapshot(classroom_db, class_snapshot)
            files.append(("classroom.db", class_snapshot))
        manifest = {"version": 2, "root": str(root.resolve()),
                    'created_at': datetime.now().astimezone().isoformat(), 'scope': BACKUP_SCOPE, "files": {}}
        if len(files) + 1 > MAX_BACKUP_FILES or sum(path.stat().st_size for _, path in files) > MAX_RESTORE_BYTES:
            raise ValueError("Thư viện vượt giới hạn bản sao lưu; chưa tạo tệp không thể khôi phục.")
        if any(path.stat().st_size > MAX_FILE_BYTES for _, path in files):
            raise ValueError("Một tệp vượt giới hạn sao lưu/khôi phục.")
        signatures, hashes, aliases = _backup_plan(files, progress)
        if aliases:
            manifest.update(version=3, aliases=aliases)
        _check_space(output.parent, sum(value[0] for name, value in signatures.items() if name not in aliases))
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".tmp", delete=False) as pending:
            temporary = Path(pending.name)
        try:
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                for index, (name, path) in enumerate(files, 1):
                    if name in aliases:
                        manifest['files'][name] = manifest['files'][aliases[name]]
                    else:
                        info = zipfile.ZipInfo(name)
                        info.compress_type = (zipfile.ZIP_STORED if path.suffix.lower() in
                                              {'.pptx', '.zip', '.bcbackup', '.png', '.jpg', '.jpeg', '.webp'}
                                              else zipfile.ZIP_DEFLATED)
                        with path.open('rb') as source_file, archive.open(info, 'w', force_zip64=True) as entry:
                            checksum = _copy_hashed(source_file, entry, MAX_FILE_BYTES)
                        if name in hashes and checksum != hashes[name]:
                            raise ValueError('Tệp thay đổi trong lúc sao lưu; hãy thử lại sau khi lưu bài xong.')
                        manifest['files'][name] = checksum
                    if temporary.stat().st_size > MAX_BACKUP_BYTES:
                        raise ValueError('Bản sao lưu vượt giới hạn 64 GiB.')
                    if progress:
                        progress(len(files) + index, len(files) * 2)
                if any(_file_signature(path) != signatures[name] for name, path in files):
                    raise ValueError('Tệp thay đổi trong lúc sao lưu; hãy thử lại sau khi lưu bài xong.')
                encoded_manifest = json.dumps(manifest).encode('utf-8')
                if len(encoded_manifest) > MAX_MANIFEST_BYTES:
                    raise ValueError("Danh mục bản sao lưu vượt giới hạn.")
                if sum(value[0] for value in signatures.values()) + len(encoded_manifest) > MAX_RESTORE_BYTES:
                    raise ValueError("Thư viện vượt giới hạn bản sao lưu; chưa tạo tệp không thể khôi phục.")
                archive.writestr("manifest.json", encoded_manifest)
            if temporary.stat().st_size > MAX_BACKUP_BYTES:
                raise ValueError("Bản sao lưu vượt giới hạn dung lượng khôi phục.")
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    record_backup(root, path=output)
    if daily:
        prune_backups(folder)
    return output


def restore_backup(path, destination):
    """Restore into a new empty directory; never overwrite a live library."""
    destination = Path(destination)
    if destination.is_symlink() or destination.is_junction():
        raise ValueError("Chọn thư mục trống lưu trực tiếp, không dùng liên kết.")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Chọn một thư mục trống để khôi phục; bản đang dùng được giữ nguyên.")
    if Path(path).stat().st_size > MAX_BACKUP_BYTES:
        raise ValueError("Bản sao lưu vượt giới hạn 64 GiB.")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if (len(entries) > MAX_BACKUP_FILES or len(set(names)) != len(names)
                or len({name.casefold() for name in names}) != len(names)):
            raise ValueError("Bản sao lưu có entry không hợp lệ.")
        if sum(entry.file_size for entry in entries) > MAX_RESTORE_BYTES:
            raise ValueError("Bản sao lưu giải nén vượt 128 GiB.")
        if any(entry.file_size > (MAX_MANIFEST_BYTES if entry.filename == 'manifest.json' else MAX_FILE_BYTES)
               for entry in entries):
            raise ValueError("Một tệp vượt giới hạn sao lưu/khôi phục.")
        try:
            manifest = json.loads(archive.read("manifest.json"))
        except (KeyError, ValueError, UnicodeError) as exc:
            raise ValueError('Manifest bản sao lưu không hợp lệ.') from exc
        if not isinstance(manifest, dict):
            raise ValueError('Manifest bản sao lưu không hợp lệ.')
        if manifest.get('version') not in {1, 2, 3} or not isinstance(manifest.get('files'), dict):
            raise ValueError("Định dạng bản sao lưu không được hỗ trợ.")
        files = manifest['files']
        aliases = manifest.get('aliases', {}) if manifest['version'] == 3 else {}
        if (not isinstance(aliases, dict) or not set(aliases).issubset(files)
                or any(not isinstance(target, str) or target not in files or target in aliases
                       or files[name] != files[target] for name, target in aliases.items())
                or set(names) != {'manifest.json', *(set(files) - set(aliases))}
                or len({name.casefold() for name in files}) != len(files)
                or len(files) + 1 > MAX_BACKUP_FILES):
            raise ValueError('Danh mục tệp trong bản sao lưu không hợp lệ.')
        if any(not _valid_backup_name(name) for name in files):
            raise ValueError('Đường dẫn trong bản sao lưu không hợp lệ.')
        if any(((entry.external_attr >> 16) & 0o170000) == 0o120000 for entry in entries):
            raise ValueError('Đường dẫn trong bản sao lưu không hợp lệ.')
        if any(not isinstance(checksum, str) or not re.fullmatch(r'[0-9a-f]{64}', checksum)
               for checksum in files.values()):
            raise ValueError('Checksum bản sao lưu không hợp lệ.')
        expanded_bytes = sum(archive.getinfo(aliases.get(name, name)).file_size for name in files)
        if expanded_bytes + archive.getinfo('manifest.json').file_size > MAX_RESTORE_BYTES:
            raise ValueError('Bản sao lưu giải nén vượt 128 GiB.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        _check_space(destination.parent, expanded_bytes + archive.getinfo('manifest.json').file_size)
        with tempfile.TemporaryDirectory(prefix="biliclass-restore-", dir=destination.parent) as temporary:
            staging = Path(temporary) / 'library'
            staging.mkdir()
            for name in files:
                entry = archive.getinfo(aliases.get(name, name))
                output = Path(staging) / name
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source_file, output.open('wb') as target_file:
                    checksum = _copy_hashed(source_file, target_file, MAX_FILE_BYTES)
                if checksum != manifest["files"][name]:
                    raise ValueError("Checksum bản sao lưu không khớp.")
            for name in ("library.db", "classroom.db"):
                database = Path(staging) / name
                if not database.exists():
                    if name == "library.db":
                        raise ValueError("Bản sao lưu thiếu thư viện.")
                    continue
                conn = sqlite3.connect(database)
                try:
                    if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("Database trong bản sao lưu bị hỏng.")
                finally:
                    conn.close()
            _rebase_restored(staging, manifest.get('root'), destination.resolve())
            from .library_location import rebase, write_record

            if manifest.get('root'):
                for folder in ('google_jobs', 'chatgpt', 'templates', 'custom_templates'):
                    for path in (staging / folder).rglob('*.json'):
                        try:
                            value = json.loads(path.read_text(encoding='utf-8'))
                        except (ValueError, UnicodeError):
                            continue
                        updated = rebase(value, Path(manifest['root']), destination.resolve())
                        if updated != value:
                            write_record(path, updated)
            # Publish on the chosen drive only after all checks pass. A failed
            # extraction never leaves a partially restored library visible.
            if destination.exists():
                destination.rmdir()  # fails safely if another process added a file
            staging.rename(destination)
    return destination


def _rebase_restored(staging, original, destination):
    from .library_location import rebase

    database = staging / 'library.db'
    conn = sqlite3.connect(database)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        values = []
        for table, column in (('lessons', 'content'), ('lesson_revisions', 'content'), ('settings', 'value')):
            if table in tables:
                values.extend((table, column, rowid, json.loads(raw)) for rowid, raw in
                              conn.execute(f'SELECT rowid,{column} FROM {table}').fetchall())
        origins = {original} if original else set()
        if not original:
            def infer(value):
                if isinstance(value, dict):
                    for item in value.values():
                        infer(item)
                elif isinstance(value, list):
                    for item in value:
                        infer(item)
                elif isinstance(value, str):
                    normalized = value.replace('\\', '/')
                    for category in BACKUP_TREES:
                        if '/' + category + '/' in normalized:
                            prefix, relative = normalized.rsplit('/' + category + '/', 1)
                            if (staging / category / relative).is_file():
                                origins.add(prefix)
            for _, _, _, value in values:
                infer(value)
        for table, column, rowid, value in values:
            updated = value
            for origin in origins:
                updated = rebase(updated, Path(origin), destination)
            if value != updated:
                conn.execute(f'UPDATE {table} SET {column}=? WHERE rowid=?',
                             (json.dumps(updated, ensure_ascii=False), rowid))
        conn.commit()
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    finally:
        conn.close()
