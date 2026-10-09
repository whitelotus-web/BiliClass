import copy
import hashlib
import json
import sys
from types import SimpleNamespace

import pytest

from app.chatgpt_handoff import load_request, make_prompt, prepare_request
from app.legacy_support import checked_ai_support
from app.library import Library
from app.pack import export_pack, import_pack
from app.quick_conversion import review_snapshot


def test_retired_request_keeps_teacher_files_and_never_regenerates_old_prompt(tmp_path):
    config = {"title": "Bài cũ", "subject": "Toán", "level": 2, "layout": "line_pair",
              "style": "template", "preset": "standard", "mode": "level", "provider": "manual_web"}
    request = prepare_request(tmp_path, config, text="Hãy giải thích cách làm.")
    from pathlib import Path

    folder = Path(request["folder"])
    records = {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}
    saved = json.loads(records["config.json"])
    saved["provider"] = "chatgpt_plan"
    (folder / "config.json").write_text(json.dumps(saved), encoding="utf-8")
    expected = (folder / "config.json").read_bytes()
    with pytest.raises(ValueError, match="OAuth cũ"):
        load_request(folder)
    with pytest.raises(ValueError, match="OAuth cũ"):
        make_prompt(saved, saved["source_file"])
    assert (folder / "config.json").read_bytes() == expected
    for name, content in records.items():
        if name != "config.json":
            assert (folder / name).read_bytes() == content


def test_saved_ai_lesson_pack_and_preview_work_without_retired_modules(tmp_path):
    library = Library(tmp_path / "library")
    try:
        lesson = library.create("Bài đã lưu", "Toán", "THPT", "11", [("Đoạn 1", "Cấp số cộng.")])
        segment = lesson["segments"][0]
        lesson = library.edit_segment(lesson["id"], segment["id"], "Cấp số cộng.", "Arithmetic progression.", True)
        segment = lesson["segments"][0]
        pair = {"vi": segment["vi"], "en": segment["en"]}
        basis = hashlib.sha256(json.dumps(pair, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        segment.update(ai_provider="chatgpt_plan", source_ref="slide-1", ai_issues=[],
                       support=[{"id": "support", "kind": "easy_en", "vi": "", "en": "A sequence with a common difference.",
                                 "provider": "chatgpt_plan", "source_refs": ["slide-1"], "basis_sha256": basis, "approved": False}])
        lesson["ai_conversion"] = {"provider": "chatgpt_plan"}
        library._write(lesson)
        snapshot = review_snapshot(library.get(lesson["id"]), library.directory)
        assert snapshot["segments"][0]["support"][0]["approved"]
        assert not library.get(lesson["id"])["segments"][0]["support"][0]["approved"]
        path = export_pack(library, lesson["id"], tmp_path / "old.biliclass")
        imported = import_pack(library, path)
        assert imported["segments"][0]["en"] == segment["en"]
        assert not imported["segments"][0]["approved"]
        assert "app.chatgpt_auth" not in sys.modules and "app.chatgpt_plan" not in sys.modules
        damaged = copy.deepcopy(snapshot)
        damaged["segments"][0]["support"][0]["source_refs"] = ["other-slide"]
        with pytest.raises(ValueError, match="khớp nguồn"):
            checked_ai_support(damaged)
    finally:
        library.close()


def test_vietnamese_engine_honors_offline_when_hub_was_already_imported(tmp_path, monkeypatch):
    from huggingface_hub import constants

    from app import speech

    monkeypatch.setattr(constants, "HF_HUB_OFFLINE", False)
    monkeypatch.setattr(constants, "HF_HOME", constants.HF_HOME)
    monkeypatch.setattr(constants, "HF_HUB_CACHE", constants.HF_HUB_CACHE)
    monkeypatch.setattr(constants, "HUGGINGFACE_HUB_CACHE", constants.HUGGINGFACE_HUB_CACHE)
    for name in ("HF_HOME", "HF_HUB_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        monkeypatch.setenv(name, "fixture")
    monkeypatch.setattr(speech, "vieneu_ready", lambda: True)

    def factory(**options):
        assert constants.HF_HUB_OFFLINE
        assert constants.HF_HUB_CACHE == str(tmp_path / "hub")
        assert options["backend"] == "onnx" and options["device"] == "cpu"
        return object()

    monkeypatch.setitem(sys.modules, "vieneu", SimpleNamespace(Vieneu=factory))
    speech._vieneu_engine.cache_clear()
    try:
        speech._vieneu_engine(str(tmp_path))
    finally:
        speech._vieneu_engine.cache_clear()
