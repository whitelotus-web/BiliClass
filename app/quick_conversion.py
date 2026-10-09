"""Generate a reviewable presentation without silently approving teacher data."""

import copy
import hashlib
import json
from pathlib import Path

from .readiness import text_readiness
from .text_quality import review_warnings


def pair_issues(lesson):
    missing, warnings = [], []
    for segment in lesson.get("segments", []):
        if not (segment.get("vi", "").strip() and segment.get("en", "").strip()):
            missing.append(segment["locator"])
        else:
            warnings.extend(segment["locator"] + ": " + issue
                            for issue in review_warnings(segment["vi"], segment["en"]))
    return missing, warnings


def review_snapshot(lesson, directory):
    """Private export snapshot; the caller must explicitly authorize persistence."""
    missing, _ = pair_issues(lesson)
    if not lesson.get("segments") or missing:
        raise ValueError("Chưa đủ cặp Việt–Anh: " + ", ".join(missing[:5]))
    snapshot = copy.deepcopy(lesson)
    for segment in snapshot["segments"]:
        segment["approved"] = True
    if lesson.get("ai_conversion"):
        from .legacy_support import checked_ai_support

        checked_ai_support(snapshot)
    if not text_readiness(snapshot, directory)["source_ok"]:
        raise ValueError("Bản nguồn đã thay đổi hoặc không còn; chưa thể dùng để dạy.")
    return snapshot


def build_preview(lesson, directory, profile=None, terms=()):
    from pptx import Presentation

    from .deck_export import export_deck
    from .source_deck import is_source_style, prepare_source_deck

    snapshot = review_snapshot(lesson, directory)
    if is_source_style(lesson):
        artifact = prepare_source_deck(snapshot, directory, terms)
    else:
        key = hashlib.sha256(json.dumps({"lesson": snapshot, "profile": profile, "terms": terms},
                                       sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
        path = Path(directory) / "temp/lesson-preview" / (key + ".pptx")
        segment_map = []
        export_deck(snapshot, directory, path, profile, terms, segment_map=segment_map)
        artifact = {"path": str(path), "slide_map": [], "segment_map": segment_map, "report": []}
    path = Path(artifact["path"])
    total = len(Presentation(path).slides)
    _, warnings = pair_issues(lesson)
    warnings = list(dict.fromkeys(warnings + (lesson.get("source") or {}).get("warnings", [])
                                  + lesson.get("input_profile", {}).get("warnings", [])
                                  + [warning for item in artifact.get("report", []) for warning in item.get("warnings", [])]))
    return {**artifact, "lesson_id": lesson["id"], "revision": lesson["revision"],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "total": total,
            "draft": any(not s.get("approved") for s in lesson["segments"]),
            "missing": [], "warnings": warnings, "image": "", "slide": 1}


def verify_preview(lesson, result, directory):
    if result.get("lesson_id") != lesson.get("id") or result.get("revision") != lesson.get("revision"):
        raise ValueError("Bài vừa được sửa. Bấm Chuyển đổi để xem bản mới trước khi dạy.")
    path = Path(result.get("path", ""))
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != result.get("sha256"):
        raise ValueError("Bản trình chiếu đã thay đổi. Bấm Chuyển đổi để tạo lại.")
    if result.get("external"):
        from .chatgpt_handoff import external_preview

        if not lesson.get("external_deck") or external_preview(lesson, directory)["sha256"] != result["sha256"]:
            raise ValueError("PowerPoint nhận về không khớp bài học.")
    else:
        review_snapshot(lesson, directory)
    return path
