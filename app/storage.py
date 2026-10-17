"""Consistent, bounded local backups and diagnostic logging without lesson text."""

import hashlib
import json
import logging
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path, PurePosixPath

MAX_BACKUP_BYTES = 2 * 1024**3
MAX_RESTORE_BYTES = 4 * 1024**3
MAX_BACKUP_FILES = 20000
MAX_FILE_BYTES = 200 * 1024**2
MAX_MANIFEST_BYTES = 4 * 1024**2
CHUNK_BYTES = 1024**2


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


def backup_library(directory, destination=None, daily=False):
    root = Path(directory)
    database = root / "library.db"
    if not database.exists():
        return None
    folder = root / "backups"
    folder.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d" if daily else "%Y%m%d-%H%M%S-%f")
    output = Path(destination) if destination else folder / f"BiliClass-{stamp}.bcbackup"
    if daily and output.exists():
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="biliclass-backup-", dir=output.parent) as work:
        snapshot = Path(work) / "library.db"
        source = sqlite3.connect(database)
        target = sqlite3.connect(snapshot)
        try:
            source.backup(target)
            assert target.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            source.close()
            target.close()
        files = [("library.db", snapshot)]
        for category in ("sources", "audio", "assets"):
            directory_path = root / category
            if directory_path.is_dir():
                files.extend((category + "/" + path.name, path) for path in directory_path.iterdir()
                             if path.is_file() and not path.is_symlink())
        classroom_db = root / "classroom.db"
        if classroom_db.exists():
            class_snapshot = Path(work) / "classroom.db"
            source = sqlite3.connect(classroom_db)
            target = sqlite3.connect(class_snapshot)
            try:
                source.backup(target)
            finally:
                source.close()
                target.close()
            files.append(("classroom.db", class_snapshot))
        manifest = {"version": 1, "files": {}}
        if len(files) + 1 > MAX_BACKUP_FILES or sum(path.stat().st_size for _, path in files) > MAX_RESTORE_BYTES:
            raise ValueError("Thư viện vượt giới hạn bản sao lưu; chưa tạo tệp không thể khôi phục.")
        if any(path.stat().st_size > MAX_FILE_BYTES for _, path in files):
            raise ValueError("Một tệp vượt giới hạn sao lưu/khôi phục.")
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".tmp", delete=False) as pending:
            temporary = Path(pending.name)
        try:
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, path in files:
                    with path.open('rb') as source_file, archive.open(name, 'w', force_zip64=True) as entry:
                        manifest["files"][name] = _copy_hashed(source_file, entry, MAX_FILE_BYTES)
                encoded_manifest = json.dumps(manifest).encode('utf-8')
                if len(encoded_manifest) > MAX_MANIFEST_BYTES:
                    raise ValueError("Danh mục bản sao lưu vượt giới hạn.")
                if sum(entry.file_size for entry in archive.infolist()) + len(encoded_manifest) > MAX_RESTORE_BYTES:
                    raise ValueError("Thư viện vượt giới hạn bản sao lưu; chưa tạo tệp không thể khôi phục.")
                archive.writestr("manifest.json", encoded_manifest)
            if temporary.stat().st_size > MAX_BACKUP_BYTES:
                raise ValueError("Bản sao lưu vượt giới hạn dung lượng khôi phục.")
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    if daily:
        import re
        automatic = sorted((p for p in folder.glob("BiliClass-*.bcbackup") if re.fullmatch(r"BiliClass-\d{8}\.bcbackup", p.name)), reverse=True)
        for old in automatic[14:]:
            old.unlink()
    return output


def restore_backup(path, destination):
    """Restore into a new empty directory; never overwrite a live library."""
    destination = Path(destination)
    if destination.is_symlink() or destination.is_junction():
        raise ValueError("Chọn thư mục trống lưu trực tiếp, không dùng liên kết.")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Chọn một thư mục trống để khôi phục; bản đang dùng được giữ nguyên.")
    if Path(path).stat().st_size > MAX_BACKUP_BYTES:
        raise ValueError("Bản sao lưu vượt giới hạn 2 GB.")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(entries) > MAX_BACKUP_FILES or len(set(names)) != len(names):
            raise ValueError("Bản sao lưu có entry không hợp lệ.")
        if sum(entry.file_size for entry in entries) > MAX_RESTORE_BYTES:
            raise ValueError("Bản sao lưu giải nén vượt 4 GB.")
        if any(entry.file_size > (MAX_MANIFEST_BYTES if entry.filename == 'manifest.json' else MAX_FILE_BYTES)
               for entry in entries):
            raise ValueError("Một tệp vượt giới hạn sao lưu/khôi phục.")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("version") != 1 or set(names) != {"manifest.json", *manifest.get("files", {})}:
            raise ValueError("Định dạng bản sao lưu không được hỗ trợ.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="biliclass-restore-", dir=destination.parent) as temporary:
            staging = Path(temporary) / 'library'
            staging.mkdir()
            for entry in entries:
                name = entry.filename
                if name == "manifest.json":
                    continue
                parts = PurePosixPath(name)
                valid = name in ("library.db", "classroom.db") or (
                    len(parts.parts) == 2 and parts.parts[0] in ("sources", "audio", "assets")
                )
                if (not valid or ".." in parts.parts or ":" in name or "\\" in name
                        or parts.is_absolute() or ((entry.external_attr >> 16) & 0o170000) == 0o120000):
                    raise ValueError("Đường dẫn trong bản sao lưu không hợp lệ.")
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
            # Publish on the chosen drive only after all checks pass. A failed
            # extraction never leaves a partially restored library visible.
            if destination.exists():
                destination.rmdir()  # fails safely if another process added a file
            staging.rename(destination)
    return destination
