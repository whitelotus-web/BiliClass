"""Small, deterministic teaching blocks and presentation choices.

Classification only suggests a layout. It never supplies missing lesson facts.
"""

import re

PRESETS = ("standard", "visual", "practice")


def classify_block(text):
    value = text.strip()
    lowered = value.casefold()
    if not value:
        return "unknown"
    for kind, prefixes in (
        ("goal", ("mục tiêu", "yêu cầu cần đạt", "learning goal", "learning objective")),
        ("warmup", ("khởi động", "warm-up", "warm up")),
        ("vocabulary", ("từ khóa", "thuật ngữ", "vocabulary", "key words")),
        ("visual", ("hình:", "sơ đồ:", "quan sát hình", "diagram:", "observe the image")),
        ("compare", ("so sánh", "comparison", "compare")),
        ("check", ("kiểm tra hiểu bài", "check understanding", "exit ticket")),
        ("summary", ("tổng kết", "ghi nhớ", "summary")),
    ):
        if lowered.startswith(prefixes):
            return kind
    if re.search(r"(?:[A-Za-z][\w²³]*|\d+)\s*[=≤≥≈]\s*\S+", value):
        return "formula"
    if lowered.startswith(("ví dụ", "example", "minh họa")):
        return "example"
    if lowered.startswith(("bài tập", "luyện tập", "practice")):
        return "practice"
    if lowered.startswith(("định nghĩa", "khái niệm", "definition", "concept")):
        return "concept"
    if value.rstrip().endswith("?"):
        return "question"
    # Short length alone cannot tell a complete sentence from a heading.
    if len(value) <= 90 and "\n" not in value and not value.endswith((".", "!", ";")):
        return "heading"
    return "explanation"


def paired_pages(vi, en, limit=430):
    """Pack only corresponding lines together; never independently split languages."""
    left = [line.strip() for line in vi.splitlines() if line.strip()]
    right = [line.strip() for line in en.splitlines() if line.strip()]
    if len(left) != len(right):
        left, right = [vi.strip()], [en.strip()]
    pages = []
    current_vi = current_en = ""
    for vi_line, en_line in zip(left, right, strict=True):
        if len(vi_line) > limit or len(en_line) > limit:
            raise ValueError("Một ý quá dài để trình chiếu. Hãy tách đoạn và duyệt các cặp Việt–Anh tương ứng.")
        joined_vi = "\n".join(filter(None, (current_vi, vi_line)))
        joined_en = "\n".join(filter(None, (current_en, en_line)))
        if current_vi and (len(joined_vi) > limit or len(joined_en) > limit):
            pages.append((current_vi, current_en))
            current_vi, current_en = vi_line, en_line
        else:
            current_vi, current_en = joined_vi, joined_en
    if current_vi or current_en:
        pages.append((current_vi, current_en))
    return pages or [("", "")]
