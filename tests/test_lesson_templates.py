import copy

import pytest

from app.lesson_templates import catalog, example_plan, slide_pages, slide_plan
from app.library import Library
from app.pack import export_pack, import_pack
from app.readiness import preparation_current


def test_block_change_preserves_review_and_invalidates_preparation(tmp_path):
    library = Library(tmp_path)
    try:
        lesson = library.create("Bài", "Toán", "THPT", "10", [("Ý 1", "Quy tắc đã kiểm tra.")])
        segment = lesson["segments"][0]
        lesson = library.edit_segment(lesson["id"], segment["id"], segment["vi"], "A checked rule.", True)
        lesson = library.mark_prepared(lesson["id"], lesson["revision"])
        before = copy.deepcopy(lesson)
        updated = library.set_block_type(lesson["id"], segment["id"], "formula")
        assert not preparation_current(updated)
        assert updated["segments"][0] == {**before["segments"][0], "kind": "formula"}
        assert library.set_block_type(lesson["id"], segment["id"], "formula")["revision"] == updated["revision"]
        with pytest.raises(ValueError, match="loại slide"):
            library.set_block_type(lesson["id"], segment["id"], "made-up")
    finally:
        library.close()


def test_templates_do_not_create_or_reorder_lesson_content():
    segment = {"vi": "F = ma", "en": "F = ma", "kind": "formula", "locator": "Slide 3"}
    original = copy.deepcopy(segment)
    for preset in catalog()["presets"]:
        plan = slide_plan({"teaching_preset": preset["id"], "level": 4, "layout": "english_rescue"}, segment)
        assert [item["text"] for item in plan["elements"] if item["body"]] == ["F = ma"]
        assert plan["elements"][-1]["align"] == "center"
    assert segment == original


def test_pagination_keeps_pairs_within_regions():
    vi = "\n".join(f"Ý thứ {i}: học sinh trình bày cách làm và giải thích kết quả." for i in range(8))
    en = "\n".join(f"Idea {i}: students present their method and explain the result." for i in range(8))
    plans = slide_pages({"level": 3, "layout": "line_pair"}, {"vi": vi, "en": en, "locator": "Đoạn 1"})
    assert len(plans) > 1
    pairs = [[item["text"] for item in plan["elements"] if item["body"]] for plan in plans]
    assert "\n".join(pair[0] for pair in pairs) == vi
    assert "\n".join(pair[1] for pair in pairs) == en
    assert all(not plan["overflow"] for plan in plans)


def test_samples_have_14_blocks_and_no_overflow():
    for preset in catalog()["presets"]:
        assert len(catalog()["blocks"]) == 14
        for block in catalog()["blocks"]:
            for layout in ("keyword_overlay", "line_pair", "split_view", "english_rescue", "level_auto"):
                for level in range(5):
                    plan = example_plan(preset["id"], block["id"], level, layout)
                    assert not plan["overflow"], (preset["id"], block["id"], level, layout)
                    assert plan["image"] and plan["image_box"]
                    assert not any("[" in item["text"] for item in plan["elements"])


def test_pack_keeps_template_and_slide_type_but_requires_review(tmp_path):
    library = Library(tmp_path / "library")
    try:
        lesson = library.create("Bài", "Sinh", "THPT", "10", [("Ý 1", "Quan sát hình.")])
        lesson = library.set_teaching_preset(lesson["id"], "visual")
        lesson = library.set_block_type(lesson["id"], lesson["segments"][0]["id"], "visual")
        imported = import_pack(library, export_pack(library, lesson["id"], tmp_path / "lesson.biliclass"))
        assert imported["teaching_preset"] == "visual"
        assert imported["segments"][0]["kind"] == "visual"
        assert not imported["segments"][0]["approved"]
    finally:
        library.close()
