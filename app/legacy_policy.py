"""Compatibility policy for saved lessons; not a selector for new conversions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelPolicy:
    level: int
    name: str
    primary_language: str
    vocabulary_en: bool
    classroom_en: bool
    explanation_en: bool
    questions_en: bool
    visible_vi: bool
    scaffolding: str
    rescue_available: bool = True

    @classmethod
    def for_level(cls, level: int) -> "LevelPolicy":
        if isinstance(level, bool) or not isinstance(level, int) or level not in range(6):
            raise ValueError("Bilingual level must be an integer from 0 to 5")
        return POLICIES[level]


POLICIES = (
    LevelPolicy(0, "Familiarize", "vi", True, False, False, False, True, "keywords"),
    LevelPolicy(1, "Exposure", "vi", True, True, False, False, True, "classroom_phrases"),
    LevelPolicy(2, "Bridge", "vi", True, True, True, True, True, "easy_explanation"),
    LevelPolicy(3, "Mixed", "mixed", True, True, True, True, True, "alternating_support"),
    LevelPolicy(4, "English First", "en", True, True, True, True, False, "on_demand_support"),
    LevelPolicy(5, "Immersion", "en", True, True, True, True, False, "minimal_support"),
)
