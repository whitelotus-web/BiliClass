import pytest

from biliclass_m0.contracts import (
    Concept,
    EducationProfile,
    LevelPolicy,
    PreparedText,
    ReadinessInput,
    WebQuizProvider,
    assistant_text,
    readiness_checks,
)


@pytest.mark.parametrize(
    "level,primary,explanation,visible_vi",
    [
        (0, "vi", False, True),
        (1, "vi", False, True),
        (2, "vi", True, True),
        (3, "mixed", True, True),
        (4, "en", True, False),
        (5, "en", True, False),
    ],
)
def test_level_language_contract(level, primary, explanation, visible_vi):
    policy = LevelPolicy.for_level(level)
    assert policy.primary_language == primary
    assert policy.explanation_en == explanation
    assert policy.visible_vi == visible_vi
    assert policy.rescue_available


@pytest.mark.parametrize("level", [-1, 6, True, 2.0, "2"])
def test_invalid_level_is_rejected(level):
    with pytest.raises(ValueError):
        LevelPolicy.for_level(level)


def test_levels_distinguish_support_and_do_not_contain_layout():
    assert LevelPolicy.for_level(4).scaffolding != LevelPolicy.for_level(5).scaffolding
    assert LevelPolicy.for_level(0).classroom_en is False
    assert LevelPolicy.for_level(1).classroom_en is True
    assert not hasattr(LevelPolicy.for_level(2), "layout")


@pytest.mark.parametrize(
    "level,grade,subject",
    [
        ("THPT", "12", "Ngữ văn"),
        ("THCS", "6", "Khoa học tự nhiên"),
        ("Tự cấu hình", "Nhóm học A", "Chuyên đề do giáo viên tạo"),
    ],
)
def test_education_profile_does_not_hard_code_grades_or_subjects(level, grade, subject):
    profile = EducationProfile(education_level=level, grade=grade, subject=subject)
    assert profile.grade == grade and profile.subject == subject


def test_unapproved_content_never_becomes_assistant_answer():
    concept = Concept(id="c", title_vi="Thảo luận", explanation_en="Draft explanation")
    assert "chưa được chuẩn bị" in assistant_text(concept, "explain")
    concept.approved = True
    assert assistant_text(concept, "explain") == "Draft explanation"


def test_assistant_uses_only_prepared_items_and_never_invents_missing_content():
    concept = Concept(
        id="c",
        title_vi="Chủ đề",
        approved=True,
        examples=[PreparedText(en="Unapproved"), PreparedText(en="Reviewed", approved=True)],
    )
    assert assistant_text(concept, "example") == "Reviewed"
    assert "chưa được chuẩn bị" in assistant_text(concept, "rescue")
    assert "chưa được chuẩn bị" in assistant_text(concept, "unknown")


def test_non_quiz_lesson_does_not_require_network_or_quiz():
    checks = readiness_checks(ReadinessInput(source_valid=True))
    assert not {"network", "quiz"}.intersection(item["id"] for item in checks)
    assert all(item["severity"] == "warning" for item in checks if not item["ok"])


def test_quiz_readiness_has_explicit_warning_and_invalid_source_is_error():
    checks = readiness_checks(ReadinessInput(source_valid=False, quiz_requested=True))
    assert next(item for item in checks if item["id"] == "source")["severity"] == "error"
    assert next(item for item in checks if item["id"] == "network")["ok"] is False


def test_web_response_provider_controls_source():
    data = WebQuizProvider().normalize(
        {
            "participant_id": "s",
            "question_id": "q",
            "round_id": "r",
            "answer": "B",
            "submission_id": "m",
            "timestamp": "2026-09-29",
            "source": "camera",
        }
    )
    assert data.source == "web"
