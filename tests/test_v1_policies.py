import pytest

from app.analytics import compare_languages, safe_csv
from app.library import Library
from app.model_packs import build_model_pack, install_model_pack
from app.presentation_policy import presentation_content


@pytest.mark.parametrize("level", range(6))
@pytest.mark.parametrize("layout", ["keyword_overlay", "line_pair", "split_view", "english_rescue"])
def test_every_layout_preserves_level_and_vi_rescue(level, layout):
    segment = {"vi": "Bản Việt", "en": "Full English", "support": [{"kind": "easy_en", "en": "Easy English", "approved": True}]}
    result = presentation_content(segment, level, layout, terms=[{"vi": "thuật ngữ", "en": "term"}])
    assert result["show_vi"] == (layout != "english_rescue")
    assert result["show_en"] == (layout != "keyword_overlay")
    assert result["columns"] == (2 if layout == "split_view" else 1)
    if level == 2 and layout != "keyword_overlay":
        assert result["en"] == "Easy English" and not result["needs_easy_en"]
    assert presentation_content(segment, level, layout, rescue=True)["show_vi"]


def test_inline_keywords_only_annotates_matching_curated_terms():
    from app.presentation_policy import inline_keywords

    text = "Tế bào là đơn vị sống; tế bào chất khác tế bào."
    terms = [{"vi": "tế bào", "en": "cell"}, {"vi": "tế bào chất", "en": "cytoplasm"},
             {"vi": "không xuất hiện", "en": "unrelated"}]
    assert inline_keywords(text, terms) == "Tế bào (cell) là đơn vị sống; tế bào chất (cytoplasm) khác tế bào (cell)."
    assert inline_keywords("Không có từ khóa", terms) == "Không có từ khóa"


def test_fuzzy_memory_does_not_cross_subject_and_never_changes_content(tmp_path):
    library = Library(tmp_path)
    try:
        lesson = library.create("Bài cũ", "Môn riêng", "THPT", "11", [("Đoạn", "Hãy phân tích dữ liệu theo nhóm.")])
        lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "Hãy phân tích dữ liệu theo nhóm.", "Analyze the data in groups.", True)
        result = library.similar_translations("Môn riêng", "Hãy phân tích dữ liệu theo cặp.")
        assert result and 75 <= result[0]["similarity"] < 100
        assert library.get(lesson["id"]) == lesson
        assert not library.similar_translations("Môn khác", "Hãy phân tích dữ liệu theo cặp.")
    finally:
        library.close()


def test_language_recommendation_needs_equivalent_distinct_questions_and_same_cohort():
    items = [{"group": group, "concept": "s", "question": group+language, "language": language, "eligible": 12,
              "responses": {str(i): i < correct for i in range(12)}} for group in ("pair1", "pair2") for language, correct in (("vi", 11), ("en", 6))]
    assert compare_languages(items, 2)["suggested_formats"] == ["parallel_columns", "sentence_pairs"]
    assert not compare_languages(items[:2], 2)["eligible"]
    items[1]["responses"]["outsider"] = items[1]["responses"].pop("0")
    assert not compare_languages(items, 2)["eligible"]


@pytest.mark.parametrize("value", ["=1+1", " +SUM(A1)", "\tname", "\nformula", "@DDE"])
def test_csv_does_not_execute_formula_like_cells(value):
    assert safe_csv(value).startswith("'")


def test_model_pack_integrity_and_no_silent_replacement(tmp_path):
    source = tmp_path / "vi-en-test1"
    source.mkdir()
    for name in ("provenance.json", "model.bin", "sentencepiece.model"):
        (source / name).write_bytes(b"fixture")
    pack = build_model_pack(source, tmp_path / "test.bclanguage")
    installed = install_model_pack(pack, tmp_path / "installed")
    assert (installed / "model.bin").read_bytes() == b"fixture"
    with pytest.raises(ValueError, match="đã có"):
        install_model_pack(pack, tmp_path / "installed")
