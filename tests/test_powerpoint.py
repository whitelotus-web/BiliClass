import pytest

from app.library import Library
from app.powerpoint import slide_for_locator, slide_segment_indexes, verified_presentation


def test_slide_locator_survives_split():
    assert slide_for_locator("Slide 12 · phần 2") == 12
    assert slide_for_locator("Trang 12") is None
    assert slide_for_locator("Slide 3") == 3


def test_displayed_slide_resolves_all_source_sections_and_reordered_output():
    lesson = {"segments": [
        {"id": "a", "locator": "Slide 1 · ý 1"},
        {"id": "b", "locator": "Slide 1 · ý 2"},
        {"id": "c", "locator": "Slide 2"},
    ]}
    assert slide_segment_indexes(lesson, 1) == [0, 1]
    assert slide_segment_indexes(lesson, 1, [2, 1, 1]) == [2]
    assert slide_segment_indexes(lesson, 3, [2, 1, 1]) == [0, 1]
    assert slide_segment_indexes(lesson, 4, [2, 1, 1]) == []


def test_blank_external_slide_must_never_fall_back_to_another_slide():
    lesson = {"segments": [{"id": "a", "locator": "Slide 2"}]}
    assert slide_segment_indexes(lesson, 1, segment_map=["a", "", "a"]) == [0]
    assert slide_segment_indexes(lesson, 2, segment_map=["a", "", "a"]) == []
    assert slide_segment_indexes(lesson, 4, segment_map=["a", "", "a"]) == []
    assert slide_segment_indexes(lesson, 0) == []


def test_companion_rejects_changed_missing_or_non_pptx_source(tmp_path):
    library = Library(tmp_path / "library")
    path = tmp_path / "Thử.pptx"
    path.write_bytes(b"mock deck")
    source = library.store_source(path)
    saved = verified_presentation({"source": source}, library.directory)
    assert saved.read_bytes() == b"mock deck"
    saved.write_bytes(b"changed")
    with pytest.raises(ValueError, match="thay đổi"):
        verified_presentation({"source": source}, library.directory)
    with pytest.raises(ValueError, match="không có"):
        verified_presentation({"source": None}, library.directory)
    library.close()
