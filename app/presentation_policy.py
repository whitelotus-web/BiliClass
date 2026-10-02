"""Presentation mode controls visible text; L0–L4 controls teaching support."""
import re

from biliclass_m0.contracts import LevelPolicy

LAYOUTS = {"keyword_overlay", "line_pair", "split_view", "english_rescue"}


def inline_keywords(text, terms):
    """Insert only teacher-curated English terms beside matching Vietnamese words."""
    lookup = {item["vi"].strip().casefold(): item["en"].strip()
              for item in terms if item.get("vi", "").strip() and item.get("en", "").strip()}
    if not lookup:
        return text
    pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(term) for term in sorted(lookup, key=len, reverse=True)) + r")(?!\w)", re.IGNORECASE)
    return pattern.sub(lambda match: f"{match.group(0)} ({lookup[match.group(0).casefold()]})", text)


def presentation_content(segment, level, layout, rescue=False, terms=()):
    policy = LevelPolicy.for_level(level)
    if layout not in LAYOUTS:
        raise ValueError("Layout không hợp lệ.")
    original_vi = segment.get("vi", "")
    en = segment.get("en", "")
    approved_easy = next((item["en"] for item in segment.get("support", [])
                          if item.get("approved") and item.get("kind") == "easy_en" and item.get("en")), "")
    if level == 2 and approved_easy:
        en = approved_easy
    inline_vi = inline_keywords(original_vi, terms) if layout == "keyword_overlay" else original_vi
    return {
        "vi": inline_vi, "en": en,
        "show_vi": layout != "english_rescue" or rescue,
        "show_en": layout != "keyword_overlay",
        "columns": 2 if layout == "split_view" else 1,
        "terms": [],
        "needs_keywords": layout == "keyword_overlay" and inline_vi == original_vi,
        "needs_easy_en": level == 2 and layout != "keyword_overlay" and not approved_easy,
        "classroom_en": policy.classroom_en, "questions_en": policy.questions_en,
    }
