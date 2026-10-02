"""Executable design contracts for the M0 feasibility gate."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field


class EducationProfile(BaseModel):
    education_level: str = "THPT"
    grade: str = "10"
    subject: str = "Môn học của tôi"
    teacher_id: str = "local-teacher"


class ReviewState(StrEnum):
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    READY_TO_TEACH = "READY_TO_TEACH"


class PreparedText(BaseModel):
    vi: str = ""
    en: str = ""
    approved: bool = False
    source_refs: list[str] = Field(default_factory=list)


class Concept(BaseModel):
    id: str
    title_vi: str
    title_en: str = ""
    explanation_vi: str = ""
    explanation_en: str = ""
    easy_en: str = ""
    examples: list[PreparedText] = Field(default_factory=list)
    teacher_prompts: list[PreparedText] = Field(default_factory=list)
    questions: list[PreparedText] = Field(default_factory=list)
    vi_rescue: str = ""
    vocabulary: list[PreparedText] = Field(default_factory=list)
    quiz_refs: list[str] = Field(default_factory=list)
    misconceptions: dict[str, str] = Field(default_factory=dict)
    audio_scripts: list[PreparedText] = Field(default_factory=list)
    audio_cache_refs: list[str] = Field(default_factory=list)
    approved: bool = False


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


def assistant_text(concept: Concept, action: str, language: str = "en") -> str:
    unavailable = "Nội dung này chưa được chuẩn bị cho bài học."
    if not concept.approved:
        return unavailable
    if action == "explain":
        return (concept.explanation_en if language == "en" else concept.explanation_vi) or unavailable
    if action == "rescue":
        return concept.vi_rescue or unavailable
    collection = {"example": concept.examples, "ask": concept.questions}.get(action, [])
    for item in collection:
        if item.approved:
            text = item.en if language == "en" else item.vi
            if text:
                return text
    return unavailable


@dataclass(frozen=True)
class ReadinessInput:
    source_valid: bool
    unreviewed_count: int = 0
    missing_explanations: int = 0
    voice_available: bool = False
    audio_cached: bool = False
    quiz_requested: bool = False
    quiz_ready: bool = False
    network_ready: bool = False


def readiness_checks(value: ReadinessInput) -> list[dict]:
    checks = [
        {"id": "source", "ok": value.source_valid, "severity": "error", "label": "Nguồn bài học hợp lệ"}
    ]
    for key, ok, label in (
        ("review", value.unreviewed_count == 0, f"Nội dung chưa duyệt: {value.unreviewed_count}"),
        (
            "explanation",
            value.missing_explanations == 0,
            f"Giải thích còn thiếu: {value.missing_explanations}",
        ),
        ("voice", value.voice_available, "Giọng đọc trên máy"),
        ("audio", value.audio_cached, "Âm thanh đã chuẩn bị"),
    ):
        checks.append({"id": key, "ok": ok, "severity": "warning", "label": label})
    if value.quiz_requested:
        checks.extend(
            [
                {"id": "quiz", "ok": value.quiz_ready, "severity": "warning", "label": "Câu hỏi đã duyệt"},
                {"id": "network", "ok": value.network_ready, "severity": "warning", "label": "Mạng lớp học"},
            ]
        )
    return checks


class ClassroomResponse(BaseModel):
    participant_id: str
    question_id: str
    round_id: str
    answer: str
    submission_id: str
    timestamp: str
    source: str  # web now; BiliCard/camera later, no transport coupling


class ResponseProvider(Protocol):
    def normalize(self, payload: dict) -> ClassroomResponse: ...


class WebQuizProvider:
    def normalize(self, payload: dict) -> ClassroomResponse:
        return ClassroomResponse.model_validate({**payload, "source": "web"})
