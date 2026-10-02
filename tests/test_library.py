import sqlite3

import pytest

from app.library import Library, RevisionConflict, lesson_status


@pytest.fixture
def library(tmp_path):
    value = Library(tmp_path / "Thư viện")
    yield value
    value.close()


def create(library):
    return library.create("Bài giảng mở", "Môn tự tạo", "THPT", "12", [("Đoạn 1", "Nêu ý kiến của em.")])


def test_edit_approval_and_persistence(library):
    lesson = create(library)
    identity, segment = lesson["id"], lesson["segments"][0]["id"]
    assert lesson_status(lesson["segments"]) == "DRAFT"
    draft = library.edit_segment(identity, segment, "Nêu ý kiến của em.", "Share your opinion.")
    assert lesson_status(draft["segments"]) == "REVIEW_REQUIRED"
    approved = library.edit_segment(identity, segment, "Nêu ý kiến của em.", "Share your opinion.", True)
    assert lesson_status(approved["segments"]) == "READY_TO_TEACH"
    reopened = Library(library.directory)
    assert reopened.get(identity) == approved
    reopened.close()
    changed = library.edit_segment(identity, segment, "Nêu hai ý kiến.", "Share two opinions.")
    assert not changed["segments"][0]["approved"]
    assert changed["revision"] > approved["revision"]


def test_translation_cannot_overwrite_new_edits_or_locked_content(library):
    lesson = create(library)
    identity, segment = lesson["id"], lesson["segments"][0]["id"]
    locked = library.edit_segment(identity, segment, "Nêu ý kiến.", "My edit", True, True)
    with pytest.raises(RevisionConflict):
        library.apply_translation(identity, segment, "Late translation", lesson["revision"])
    with pytest.raises(RevisionConflict):
        library.apply_translation(identity, segment, "Overwrite", locked["revision"])
    assert library.get(identity)["segments"][0]["en"] == "My edit"


def test_terms_isolated_by_subject_and_teacher(library):
    library.save_term("Toán", "tập", "set", teacher_id="A")
    library.save_term("Thể chất", "tập", "practice", teacher_id="A")
    library.save_term("Toán", "tập", "collection", teacher_id="B")
    assert library.exact_translation("Toán", "tập", "A") == "set"
    assert library.exact_translation("Thể chất", "tập", "A") == "practice"
    assert library.exact_translation("Toán", "tập", "B") == "collection"
    assert library.exact_translation("Tin học", "tập", "A") is None
    library.save_term("Toán", "tập", "revised set", teacher_id="A")
    assert len(library.glossary("Toán", "A")) == 1
    assert library.exact_translation("Toán", "tập", "A") == "revised set"


def test_invalid_edits_do_not_change_saved_lesson(library):
    lesson = create(library)
    with pytest.raises(ValueError):
        library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "", "text")
    with pytest.raises(ValueError):
        library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "VI", "", True)
    assert library.get(lesson["id"]) == lesson


def test_level_layout_are_independent_and_persist(library):
    lesson = create(library)
    for level in range(6):
        for layout in ("keyword_overlay", "line_pair", "split_view", "english_rescue"):
            updated = library.set_presentation(lesson["id"], level, layout)
            assert (updated["level"], updated["layout"]) == (level, layout)
            assert updated["segments"] == lesson["segments"]
    with pytest.raises(ValueError):
        library.set_presentation(lesson["id"], True, "line_pair")


def test_future_database_version_is_not_downgraded(tmp_path):
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.execute("PRAGMA user_version=99")
    conn.close()
    with pytest.raises(ValueError, match="mới hơn"):
        Library(tmp_path)


def test_settings_persist_and_source_bytes_unchanged(library, tmp_path):
    original = tmp_path / "Bài nguồn.txt"
    original.write_text("x² + 3 = 7; 25%", encoding="utf-8")
    before = original.read_bytes()
    source = library.store_source(original)
    assert original.read_bytes() == before
    assert (library.directory / "sources" / source["file"]).read_bytes() == before
    library.set_setting("mascot", "Lumi")
    reopened = Library(library.directory)
    assert reopened.setting("mascot", "Milo") == "Lumi"
    reopened.close()
