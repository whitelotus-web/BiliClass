import copy
from threading import Event

import pytest

from app.bulk_translation import plan_batch, translate_batch
from app.input_analysis import assess_blocks
from app.library import Library, RevisionConflict


def new_lesson(library, blocks):
    profile = assess_blocks(blocks)
    return library.create("Bài thử", "Toán", "THPT", "10", blocks,
                          source_language=profile["primary_language"], analysis=profile)


def test_batch_preserves_bilingual_locked_and_reviewed_segments_and_uses_teacher_priority(tmp_path):
    library = Library(tmp_path)
    try:
        lesson = new_lesson(library, [("Ý 1", "Hàm số"), ("Ý 2", "Each input has one value."),
                                      ("Ý 3", "VI: Có một giá trị.\nEN: There is one value."),
                                      ("Ý 4", "Đoạn khóa"), ("Ý 5", "Đoạn duyệt"), ("Ý 6", "25% + 3 = 28")])
        locked, approved = lesson["segments"][3:5]
        library.edit_segment(lesson["id"], locked["id"], locked["vi"], "", locked=True)
        lesson = library.edit_segment(lesson["id"], approved["id"], approved["vi"], "Reviewed text", True)
        memory = new_lesson(library, [("Ý 1", "Hàm số")])
        library.edit_segment(memory["id"], memory["segments"][0]["id"], "Hàm số", "Memory wording", True)
        library.save_term("Toán", "Hàm số", "teacher function")
        before = copy.deepcopy(lesson)
        plans = plan_batch(library, lesson)
        assert [p["language"] for p in plans] == ["vi", "en"]
        assert plans[0]["draft"] == "teacher function" and plans[0]["provenance"] == "teacher_glossary"
        assert "draft" not in plans[1]
        plans[1].update(draft="Mỗi đầu vào có một giá trị.", provenance="machine_draft")
        drafts = translate_batch(plans, [])
        updated = library.apply_batch_translations(lesson["id"], drafts["drafts"], lesson["revision"])
        assert updated["revision"] == before["revision"] + 1
        assert updated["segments"][0]["en"] == "teacher function"
        assert updated["segments"][1]["vi"] == "Mỗi đầu vào có một giá trị."
        assert not any(s["approved"] for s in updated["segments"][:2])
        assert updated["segments"][2:] == before["segments"][2:]
        assert [s["source_text"] for s in updated["segments"]] == [s["source_text"] for s in before["segments"]]
    finally:
        library.close()


def test_batch_does_not_choose_between_conflicting_teacher_memories(tmp_path):
    library = Library(tmp_path)
    try:
        for value in ("First choice", "Second choice"):
            memory = new_lesson(library, [("Ý 1", "Hàm số")])
            library.edit_segment(memory["id"], memory["segments"][0]["id"], "Hàm số", value, True)
        lesson = new_lesson(library, [("Ý 1", "Hàm số")])
        result = translate_batch(plan_batch(library, lesson), [])
        assert not result["drafts"] and len(result["warnings"]) == 1
        updated = library.apply_batch_translations(lesson["id"], [], lesson["revision"])
        assert updated == lesson
    finally:
        library.close()


@pytest.mark.parametrize("stale", [False, True])
def test_batch_apply_is_atomic_if_any_segment_changed_or_result_is_invalid(tmp_path, stale):
    library = Library(tmp_path)
    try:
        lesson = new_lesson(library, [("Ý 1", "Hàm số"), ("Ý 2", "Giá trị")])
        drafts = [{**p, "draft": "A draft"} for p in plan_batch(library, lesson)]
        if stale:
            segment = lesson["segments"][1]
            current = library.edit_segment(lesson["id"], segment["id"], segment["vi"], "New wording")
        else:
            current = lesson
            drafts[1]["draft"] = ""
        with pytest.raises(RevisionConflict if stale else ValueError):
            library.apply_batch_translations(lesson["id"], drafts, lesson["revision"])
        assert library.get(lesson["id"]) == current
    finally:
        library.close()


@pytest.mark.parametrize("cancel_after_first", [False, True])
def test_batch_reuses_model_per_direction_deduplicates_and_unloads_on_cancel(monkeypatch, cancel_after_first):
    cancelled = Event()
    calls, loaded, unloaded = [], [], []

    class Translator:
        def __init__(self, language):
            self.language = language

        def unload_model(self):
            unloaded.append(self.language)

    def resources(language):
        loaded.append(language)
        return object(), Translator(language)

    def translate(text, language, terms, tokenizer, translator):
        calls.append((text, language))
        if cancel_after_first:
            cancelled.set()
        return f"Draft {language}: {text}"

    monkeypatch.setattr("app.translation.draft_resources", resources)
    monkeypatch.setattr("app.translation.translate_with_resources", translate)
    plans = [{"id": str(i), "locator": f"Ý {i}", "language": language, "source": text}
             for i, (language, text) in enumerate([("vi", "Hàm số"), ("vi", "Hàm số"), ("en", "Each value")])]
    result = translate_batch(plans, [], cancelled)
    assert loaded == unloaded
    if cancel_after_first:
        assert not result["drafts"] and loaded == ["vi"]
    else:
        assert loaded == ["vi", "en"] and len(calls) == 2 and len(result["drafts"]) == 3
        assert all(d["provenance"] == "machine_draft" for d in result["drafts"])
