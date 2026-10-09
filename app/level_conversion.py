"""Select reviewed language support for L0–L4 without inventing lesson facts."""

import re

from .legacy_policy import LevelPolicy


def layout_for_level(level):
    LevelPolicy.for_level(level)
    return "keyword_overlay" if level == 0 else "line_pair" if level < 3 else "split_view" if level == 3 else "english_rescue"


def support_for_level(segment, level, terms=()):
    policy = LevelPolicy.for_level(level)
    reviewed = [item for item in segment.get("support", []) if item.get("approved")]
    pairs = [(item.get("vi", ""), item.get("en", "")) for item in reviewed if item.get("kind") == "vocabulary"]
    for term in terms:
        vi, en = term.get("vi", ""), term.get("en", "")
        if vi and en and re.search(r"(?<!\w)" + re.escape(vi) + r"(?!\w)", segment.get("vi", ""), re.I):
            pairs.append((vi, en))
    vocabulary = list(dict.fromkeys(f"{vi} — {en}" for vi, en in pairs if vi and en))
    texts = vocabulary if level < 2 else []
    if level == 1:
        texts = texts + [item["en"] for item in reviewed if item.get("kind") == "prompt" and item.get("en")]
    if level == 2:
        easy = [item["en"] for item in reviewed if item.get("kind") == "easy_en" and item.get("en")]
        if easy:
            texts = easy
        elif segment.get("en"):
            # Selecting an existing reviewed sentence is not simplifying or
            # generating it. The teacher sees this fallback in the export report.
            texts = [re.split(r"(?<=[.!?])\s+", segment["en"].strip())[0]]
    if level >= 3:
        texts = [segment.get("en", "")]
    return {"text": "\n".join(dict.fromkeys(value for value in texts if value)),
            "vocabulary": vocabulary, "classroom_en": policy.classroom_en,
            "questions_en": policy.questions_en, "rescue_available": policy.rescue_available,
            "missing_easy": level == 2 and not any(item.get("kind") == "easy_en" for item in reviewed),
            "missing_vocabulary": level < 2 and not vocabulary}


def narration_text(segment, language, level, terms=()):
    """English narration uses the same reviewed level support as the slide."""
    if language == "vi" or segment.get("ai_provider") != "chatgpt_plan":
        return segment.get(language, "")
    if level < 2:
        reviewed = [item for item in segment.get("support", []) if item.get("approved")]
        words = [item["en"] for item in reviewed if item.get("kind") == "vocabulary" and item.get("en")]
        words += [term["en"] for term in terms if term.get("vi") and term.get("en")
                  and re.search(r"(?<!\w)" + re.escape(term["vi"]) + r"(?!\w)", segment.get("vi", ""), re.I)]
        if level == 1:
            words += [item["en"] for item in reviewed if item.get("kind") == "prompt" and item.get("en")]
        return "\n".join(dict.fromkeys(words))
    return support_for_level(segment, level, terms)["text"]
