"""Evidence-based lesson readiness; no quiz dependency for bilingual teaching."""

import hashlib
from pathlib import Path

from .portable_audio import available_audio


def text_readiness(lesson, directory):
    segments = lesson.get("segments", [])
    total = len(segments)
    approved = sum(bool(s.get("approved")) and bool(s.get("vi", "").strip() and s.get("en", "").strip())
                   for s in segments)
    source = lesson.get("source")
    if source:
        path = Path(directory) / "sources" / source["file"]
        source_ok = path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
    else:
        source_ok = bool(segments) and all(
            bool(s.get("source_text", s.get("vi", "")).strip()) for s in segments
        )
    return {"total": total, "approved": approved, "source_ok": source_ok,
            "text_ready": source_ok and total > 0 and approved == total}


def preparation_current(lesson):
    prepared = lesson.get("prepared") or {}
    return (prepared.get("revision") == lesson.get("revision")
            and prepared.get("source_sha256") == (lesson.get("source") or {}).get("sha256", ""))


def assess(lesson, directory, voices, selections, rate):
    segments = lesson.get("segments", [])
    text = text_readiness(lesson, directory)
    total, approved, source_ok = text["total"], text["approved"], text["source_ok"]
    checks = [
        {
            "id": "source",
            "ok": source_ok,
            "label": "Bản nguồn còn nguyên vẹn",
            "detail": "Kiểm tra SHA-256 tệp nguồn hoặc bản trích xuất nội dung dán.",
        },
        {
            "id": "review",
            "ok": total > 0 and approved == total,
            "label": "Duyệt nội dung Anh–Việt",
            "detail": f"{approved}/{total} đoạn có đủ hai ngôn ngữ và đã duyệt.",
        },
    ]
    voice_ids = {v["id"] for v in voices}
    for language, label in (("en", "tiếng Anh"), ("vi", "tiếng Việt")):
        selected = selections.get(language, "")
        cached = sum(
            bool(available_audio(directory, s[language], language, selected, rate))
            for s in segments
            if s[language].strip() and s.get("approved")
        )
        checks.extend(
            [
                {
                    "id": "voice_" + language,
                    "ok": selected in voice_ids,
                    "label": "Giọng đọc " + label,
                    "detail": "Đã chọn giọng trên máy."
                    if selected in voice_ids
                    else "Chưa có giọng phù hợp. Vẫn dùng được nội dung dạng chữ.",
                },
                {
                    "id": "audio_" + language,
                    "ok": total > 0 and cached == total,
                    "label": "Âm thanh " + label,
                    "detail": f"{cached}/{total} đoạn đã duyệt có âm thanh đúng nội dung, giọng và tốc độ hiện tại.",
                },
            ]
        )
    prepared_ready = text["text_ready"] and preparation_current(lesson)
    checks.append({"id": "prepared", "ok": prepared_ready,
                   "label": "Bản chuẩn bị của bài hiện tại",
                   "detail": "Đã chốt nội dung và phiên bản để dạy." if prepared_ready
                   else "Duyệt đủ nội dung rồi bấm Chốt bản chuẩn bị. Sửa bài sẽ cần chốt lại."})
    return {
        "checks": checks,
        "text_ready": text["text_ready"],
        "prepared_ready": prepared_ready,
        "total": total,
        "approved": approved,
    }
