"""Fail before a costly web/voice job when its destination disk is full."""

import errno
import shutil
import sqlite3
from pathlib import Path

MIB = 1024**2


class StorageProblem(ValueError):
    code = "storage"


def require_space(directory, required=128 * MIB):
    path = Path(directory).resolve()
    existing = path
    while not existing.exists() and existing.parent != existing:
        existing = existing.parent
    free = shutil.disk_usage(existing).free
    if free < required:
        raise StorageProblem(f"Ổ đĩa lưu dữ liệu {path.anchor} còn {free / MIB:.0f} MB; "
                             f"cần ít nhất {required / MIB:.0f} MB trống để xử lý. "
                             "Giải phóng dung lượng rồi tiếp tục; bài đã có vẫn được giữ.")


def full_disk_error(error):
    return (isinstance(error, OSError) and (error.errno == errno.ENOSPC or getattr(error, 'winerror', None) == 112)
            or isinstance(error, sqlite3.Error) and getattr(error, 'sqlite_errorcode', None) == sqlite3.SQLITE_FULL)


FULL_DISK_MESSAGE = "Ổ đĩa lưu dữ liệu đã hết dung lượng. Giải phóng dung lượng rồi tiếp tục; bài đã có vẫn được giữ."
