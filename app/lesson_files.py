"""Save the verified presentation users are viewing, without rebuilding its design."""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from .quick_conversion import verify_preview


def save_presentation(lesson, preview, directory, destination, *, with_voice=False, report=None,
                      overwrite=True, managed_output=False, expected_sha256=None, gap_ms=None):
    source = verify_preview(lesson, preview, directory).resolve()
    destination = Path(destination).resolve()
    if destination.suffix.lower() != ".pptx":
        raise ValueError("Lưu bài giảng thành tệp .pptx.")
    internal = destination.is_relative_to(Path(directory).resolve())
    managed = managed_output and destination.parent == Path(directory).resolve() / 'exports'
    if (internal and not managed) or destination == source:
        raise ValueError("Chọn thư mục ngoài dữ liệu BiliClass, ví dụ Downloads hoặc Desktop.")
    if not destination.parent.is_dir():
        raise ValueError("Thư mục lưu chưa tồn tại. Chọn lại vị trí lưu.")

    def check_owned_output():
        if expected_sha256 is None:
            return
        locked = destination.with_name('~$' + destination.name).exists()
        try:
            with destination.open('rb') as stream:
                unchanged = hashlib.file_digest(stream, 'sha256').hexdigest() == expected_sha256
        except OSError:
            unchanged = False
        if locked or not unchanged:
            raise FileExistsError('Bản tự lưu đang mở hoặc đã thay đổi; giữ tệp đó và chọn tên mới.')

    check_owned_output()
    pending = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".biliclass-", suffix=".pptx", dir=destination.parent, delete=False) as handle:
            pending = Path(handle.name)
        shutil.copyfile(source, pending)
        with pending.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != preview["sha256"]:
                raise ValueError("Bản trình chiếu đã thay đổi khi lưu. Xem lại bài trước khi tải.")
        if with_voice:
            from .presentation_audio import embed_audio

            result = embed_audio(source, pending, lesson, directory, gap_ms=gap_ms)
            if report is not None:
                report.update(result)
        if overwrite:
            check_owned_output()  # Embedding can take time; check again immediately before publication.
            os.replace(pending, destination)
        elif os.name == 'nt':
            os.rename(pending, destination)  # Windows refuses an existing destination atomically.
        else:
            os.link(pending, destination)  # Atomic, exclusive publication on POSIX.
    finally:
        if pending:
            pending.unlink(missing_ok=True)
    return destination
