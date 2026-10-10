"""Local file limits shared by selection, browser handoff and source storage.

PowerPoint decks often contain large media. These are BiliClass limits, not a
promise about an account's web upload quota. Legacy text extraction stays bounded.
"""

from pathlib import Path

MAX_DOCUMENT_BYTES = 50 * 1024**2
MAX_POWERPOINT_BYTES = 200 * 1024**2


def document_limit(path):
    return MAX_POWERPOINT_BYTES if Path(path).suffix.casefold() == ".pptx" else MAX_DOCUMENT_BYTES


def check_document_size(path, size=None):
    path = Path(path)
    size = path.stat().st_size if size is None else size
    limit = document_limit(path)
    if size > limit:
        raise ValueError(f"Tệp «{path.name}» có dung lượng {size / 1024**2:.1f} MB, "
                         f"vượt mức {limit // 1024**2} MB. Chọn tệp nhỏ hơn hoặc giảm dung lượng bản sao.")
