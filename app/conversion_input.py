"""Shared document selection and conversion config for the draft and sent prompt."""

from pathlib import Path

from PySide6.QtCore import QUrl

from .chatgpt_handoff import make_prompt, validate_config
from .conversion_formats import format_config
from .document_limits import check_document_size

DOCUMENT_SUFFIXES = {".pptx", ".docx", ".pdf", ".txt", ".png", ".jpg", ".jpeg"}
EDUCATION_GRADES = {"Tiểu học": ("1", "2", "3", "4", "5"), "THCS": ("6", "7", "8", "9"),
                    "THPT": ("10", "11", "12")}


def education_grades(education):
    return list(EDUCATION_GRADES.get(education, ()))


def local_document(file_url):
    url = QUrl(str(file_url))
    if not url.isLocalFile():
        raise ValueError("Chọn tài liệu trên máy tính; không dùng đường dẫn web.")
    path = Path(url.toLocalFile())
    if not path.is_file():
        raise ValueError("Không đọc được tài liệu. Chọn lại một tệp trên máy tính.")
    if path.suffix.casefold() not in DOCUMENT_SUFFIXES:
        raise ValueError("Chọn PPTX, DOCX, PDF, TXT hoặc ảnh PNG/JPG.")
    check_document_size(path)
    return path.resolve()


def document_selection(urls):
    if len(urls) != 1:
        raise ValueError("Mỗi lần chuyển đổi dùng một tài liệu. Kéo thả hoặc chọn một tệp.")
    path = local_document(urls[0])
    return {"valid": True, "url": QUrl.fromLocalFile(str(path)).toString(), "name": path.name}


def creation_config(title, subject, education, grade, conversion_format, preset, style, teacher_notes=""):
    education, grade = education.strip(), grade.strip()
    if grade not in education_grades(education):
        raise ValueError("Chọn khối lớp thuộc cấp học đã chọn.")
    return format_config({"title": title.strip(), "subject": subject.strip(),
        "education_level": education, "grade": grade, "teacher_notes": teacher_notes.strip(),
        "conversion_format": conversion_format, "preset": preset, "style": style, "provider": "browser_web"})


def prompt_preview(config, file_url="", text=""):
    """No copies, account checks, browser actions or filesystem reads while typing."""
    draft = dict(config)
    ready = bool(draft["title"] and draft["subject"] and (file_url or text.strip()))
    draft["title"] = draft["title"] or "[Tên bài học]"
    draft["subject"] = draft["subject"] or "[Môn học]"
    if file_url:
        original = Path(QUrl(file_url).toLocalFile()).name
        suffix = Path(original).suffix.casefold()
    elif draft["style"] == "source" and not text.strip():
        original, suffix = "[Chưa chọn tệp PowerPoint gốc]", ".pptx"
    else:
        original, suffix = "noi-dung-bai.txt", ".txt"
    if suffix not in DOCUMENT_SUFFIXES:
        raise ValueError("Tài liệu chưa hợp lệ để xem prompt.")
    if draft["style"] == "source" and suffix != ".pptx":
        raise ValueError("Giữ thiết kế gốc cần tệp PPTX; tài liệu khác dùng mẫu mới.")
    draft["source_original_name"] = original
    return {"prompt": make_prompt(validate_config(draft), "tai-lieu-goc" + suffix), "ready": ready}
