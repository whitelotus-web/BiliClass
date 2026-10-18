"""Save the verified presentation users are viewing, without rebuilding its design."""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from .quick_conversion import verify_preview


def save_presentation(lesson, preview, directory, destination, *, with_voice=False, report=None):
    source = verify_preview(lesson, preview, directory).resolve()
    destination = Path(destination).resolve()
    if destination.suffix.lower() != ".pptx":
        raise ValueError("Lưu bài giảng thành tệp .pptx.")
    if destination.is_relative_to(Path(directory).resolve()) or destination == source:
        raise ValueError("Chọn thư mục ngoài dữ liệu BiliClass, ví dụ Downloads hoặc Desktop.")
    if not destination.parent.is_dir():
        raise ValueError("Thư mục lưu chưa tồn tại. Chọn lại vị trí lưu.")
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

            result = embed_audio(source, pending, lesson, directory)
            if report is not None:
                report.update(result)
        os.replace(pending, destination)
    finally:
        if pending:
            pending.unlink(missing_ok=True)
    return destination
