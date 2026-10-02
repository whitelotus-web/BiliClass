import json
import sqlite3

import pytest

from app.library import Library, lesson_status
from app.pack import export_pack, import_pack


@pytest.fixture
def library(tmp_path):
    value = Library(tmp_path / "data")
    yield value
    value.close()


def test_english_source_can_be_saved_translated_and_exported(library, tmp_path):
    lesson = library.create(
        "Discussion",
        "Interdisciplinary",
        "THPT",
        "11",
        [("Paragraph", "Discuss in groups.")],
        source_language="en",
    )
    segment = lesson["segments"][0]
    assert segment["vi"] == "" and segment["source_text"] == segment["en"]
    assert lesson_status(lesson["segments"]) == "DRAFT"
    translated = library.apply_translation(lesson["id"], segment["id"], "Thảo luận theo nhóm.", 1, "en")
    assert translated["segments"][0]["en"] == "Discuss in groups."
    assert translated["segments"][0]["source_text"] == "Discuss in groups."
    assert lesson_status(translated["segments"]) == "REVIEW_REQUIRED"
    path = export_pack(library, lesson["id"], tmp_path / "english.biliclass")
    copied = import_pack(library, path)
    assert copied["source_language"] == "en" and copied["segments"][0]["vi"] == "Thảo luận theo nhóm."


def test_restore_adds_revision_and_preserves_previous_current(library):
    original = library.create("Bài", "Môn", "THPT", "10", [("Đoạn", "Một. Hai.")])
    item = original["segments"][0]
    edited = library.edit_segment(original["id"], item["id"], "Bản sửa.", "Edited.", True)
    assert library.history(original["id"])[0]["revision"] == 1
    restored = library.restore_revision(original["id"], 1)
    assert restored["segments"][0]["vi"] == "Một. Hai."
    assert restored["revision"] == 3 and not restored["segments"][0]["approved"]
    undo = library.restore_revision(original["id"], edited["revision"])
    assert undo["segments"][0]["en"] == "Edited."
    assert undo["segments"][0]["source_text"] == "Một. Hai."
    assert not undo["segments"][0]["approved"]


def test_history_retention_and_failed_edit_atomicity(library):
    lesson = library.create("Bài", "Môn", "THPT", "10", [("Đoạn", "Nội dung")])
    for index in range(40):
        lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "Nội dung", str(index))
    history = library.history(lesson["id"])
    assert len(history) == 30
    assert history[0]["revision"] == 40 and history[-1]["revision"] == 11
    with pytest.raises(ValueError):
        library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "", "Invalid")
    assert library.history(lesson["id"]) == history
    assert library.get(lesson["id"]) == lesson


def test_split_requires_bilingual_alignment_and_preserves_original(library):
    original = library.create("Bài", "Môn", "THPT", "10", [("Slide 1", "Một. Hai.")])
    item = original["segments"][0]
    library.edit_segment(original["id"], item["id"], "Một. Hai.", "One. Two.", True)
    with pytest.raises(ValueError):
        library.split_segment(original["id"], item["id"], 5, 0)
    split = library.split_segment(original["id"], item["id"], 5, 5)
    assert [(s["vi"], s["en"]) for s in split["segments"]] == [("Một.", "One."), ("Hai.", "Two.")]
    assert all(not s["approved"] and s["source_text"] == "Một. Hai." for s in split["segments"])
    assert all(s["split_from"] == item["id"] for s in split["segments"])
    restored = library.restore_revision(original["id"], 2)
    assert len(restored["segments"]) == 1


def test_reverse_glossary_ambiguity_not_silently_chosen(library):
    library.save_term("Môn", "bộ", "set")
    assert library.exact_translation("Môn", "set", source_language="en") == "bộ"
    library.save_term("Môn", "tập hợp", "set")
    assert library.exact_translation("Môn", "set", source_language="en") is None


def test_v1_library_migrates_without_losing_approval(tmp_path):
    lesson = {
        "id": "old-id",
        "title": "Bài cũ",
        "subject": "Môn",
        "grade": "12",
        "education_level": "THPT",
        "revision": 1,
        "segments": [
            {"id": "s", "vi": "Gốc", "en": "Source", "approved": True, "locked": False, "locator": "Đoạn"}
        ],
        "updated_at": "2026-09-29",
        "level": 2,
        "layout": "line_pair",
    }
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.execute(
        "CREATE TABLE lessons(id TEXT PRIMARY KEY,title TEXT,subject TEXT,education_level TEXT,grade TEXT,revision INTEGER,content TEXT,updated_at TEXT)"
    )
    conn.execute(
        "INSERT INTO lessons VALUES(?,?,?,?,?,?,?,?)",
        ("old-id", "Bài cũ", "Môn", "THPT", "12", 1, json.dumps(lesson), "2026-09-29"),
    )
    conn.execute("PRAGMA user_version=1")
    conn.commit()
    conn.close()
    library = Library(tmp_path)
    recovered = library.get("old-id")
    assert recovered["source_language"] == "vi"
    assert recovered["segments"][0]["source_text"] == "Gốc"
    assert recovered["segments"][0]["approved"]
    assert library.db.execute("PRAGMA user_version").fetchone()[0] == 2
    library.close()
