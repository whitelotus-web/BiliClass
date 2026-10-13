import zipfile
from pathlib import Path

import pytest
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt

from app.chatgpt_handoff import inspect_returned_deck
from app.library import Library, RevisionConflict
from app.slide_refinement import improved, source_media_preserved
from app.slide_repair import normalize_titles, repair_layout


def presentation(path):
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    shape = slide.shapes.add_textbox(Inches(1), Inches(.4), Inches(6), Inches(1))
    shape.text = "Năng lượng cơ học\nMechanical energy"
    shape.text_frame.paragraphs[0].runs[0].font.name = "Arial"
    shape.text_frame.paragraphs[0].runs[0].font.size = Pt(32)
    shape.text_frame.paragraphs[1].runs[0].font.name = "Courier New"
    shape.text_frame.paragraphs[1].runs[0].font.size = Pt(24)
    slide.notes_slide.notes_text_frame.text = "VI: Năng lượng cơ học.\nEN: Mechanical energy."
    image = path.with_suffix(".png")
    Image.new("RGB", (40, 40), "blue").save(image)
    slide.shapes.add_picture(str(image), Inches(1), Inches(2))
    deck.save(path)
    return shape.shape_id


def test_title_style_preserves_words_media_notes_and_unrelated_parts(tmp_path):
    source = tmp_path / "original.pptx"
    shape_id = presentation(source)
    before = source.read_bytes()
    result = normalize_titles(source, tmp_path, "parallel_columns")
    assert result["changes"] and source.read_bytes() == before
    fixed = Presentation(result["path"])
    shape = next(s for s in fixed.slides[0].shapes if s.shape_id == shape_id)
    vi, en = shape.text_frame.paragraphs
    assert shape.text == "Năng lượng cơ học\nMechanical energy"
    assert en.runs[0].font.name == vi.runs[0].font.name == "Arial"
    assert en.runs[0].font.italic and en.runs[0].font.size < vi.runs[0].font.size
    with zipfile.ZipFile(source) as a, zipfile.ZipFile(result["path"]) as b:
        assert a.namelist() == b.namelist()
        for name in a.namelist():
            if name != "ppt/slides/slide1.xml":
                assert a.read(name) == b.read(name), name
    assert source_media_preserved(source, result["path"], "source")


def test_layout_rejects_stale_report_and_never_touches_original(tmp_path):
    source = tmp_path / "original.pptx"
    presentation(source)
    before = source.read_bytes()
    with pytest.raises(ValueError, match="thay đổi"):
        repair_layout(source, tmp_path, {"sha256": "f" * 64, "slides": []})
    assert source.read_bytes() == before


def test_regression_cannot_hide_an_incorrect_quiz_answer():
    def q(code): return {"slides": [{"slide": 1, "issues": [{"severity": "FAIL", "code": code}]}]}
    assert not improved(q("text_overflow"), q("quiz_mismatch"))


def test_reducing_overflows_cannot_hide_new_missing_body_translation():
    before = {"slides": [{"slide": 1, "issues": [
        {"severity": "FAIL", "code": "text_overflow", "shape_id": n} for n in (1, 2, 3)]}]}
    after = {"slides": [{"slide": 1, "issues": [{"severity": "FAIL", "code": "english_body_missing"}]}]}
    assert not improved(before, after)


def test_saved_correction_keeps_id_history_and_requires_new_teacher_confirmation(tmp_path):
    path = tmp_path / "original.pptx"
    presentation(path)
    library = Library(tmp_path / "library")
    try:
        inspection = inspect_returned_deck(path, conversion_format="parallel_columns")
        source = library.store_source(path)
        config = {"title": "Test", "subject": "Vật lý", "education_level": "THPT", "grade": "10",
                  "conversion_format": "parallel_columns", "style": "source", "preset": "standard"}
        lesson = library.create_external_lesson(config, source, inspection)
        result = normalize_titles(path, tmp_path, "parallel_columns")
        corrected = inspect_returned_deck(result["path"], conversion_format="parallel_columns")
        new_source = library.store_source(Path(result["path"]))
        changed = library.replace_external_presentation(lesson["id"], lesson["revision"], new_source, corrected)
        assert changed["id"] == lesson["id"] and changed["revision"] == lesson["revision"] + 1
        assert changed["segments"][0]["id"] == lesson["segments"][0]["id"]
        assert not any(s["approved"] for s in changed["segments"])
        assert changed["external_deck"]["reviewed_revision"] == 0
        assert (library.directory / "sources" / source["file"]).read_bytes() == path.read_bytes()
        with pytest.raises(RevisionConflict):
            library.replace_external_presentation(lesson["id"], lesson["revision"], new_source, corrected)
    finally:
        library.close()
