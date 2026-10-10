from pathlib import Path

import pytest
from PySide6.QtCore import QUrl

from app.chatgpt_handoff import prepare_request
from app.conversion_formats import FORMATS, METHODS
from app.conversion_input import creation_config, document_selection, prompt_preview
from app.importers import MAX_BYTES


@pytest.mark.parametrize("spec", FORMATS, ids=lambda spec: spec["id"])
@pytest.mark.parametrize("style", ["source", "template"])
def test_preview_matches_sent_prompt_with_unicode_filename_and_configuration(tmp_path, spec, style):
    source = tmp_path / "Giáo án #1 – Toán.PPTX"
    source.write_bytes(b"source stays untouched")
    config = creation_config("  Diện tích  ", "  Toán  ", "THCS", "6", spec["id"], "visual", style)
    before = set(tmp_path.iterdir())
    preview = prompt_preview(config, QUrl.fromLocalFile(str(source)).toString())
    assert set(tmp_path.iterdir()) == before, "Typing a prompt must not create request files"
    sent = prepare_request(tmp_path / "library", config, source)
    assert preview["ready"] and preview["prompt"] == sent["prompt"]
    assert METHODS[spec["id"]] in preview["prompt"]
    assert source.name in preview["prompt"] and "THCS" in preview["prompt"]
    assert source.read_bytes() == b"source stays untouched"
    assert sent["config"]["title"] == "Diện tích" and sent["config"]["subject"] == "Toán"


def test_pasted_content_uses_same_template_prompt_and_empty_inputs_are_not_ready(tmp_path):
    config = creation_config("Bài dán", "Ngữ văn", "THPT", "11", "sentence_pairs", "practice", "template")
    assert not prompt_preview(config)["ready"]
    text = "Nội dung do giáo viên soạn."
    preview = prompt_preview(config, text=text)
    sent = prepare_request(tmp_path, config, text=text)
    assert preview["ready"] and preview["prompt"] == sent["prompt"]
    assert Path(sent["folder"]).joinpath(sent["config"]["source_file"]).read_text(encoding="utf-8") == text
    config["title"] = ""
    assert not prompt_preview(config, text=text)["ready"]


def test_drag_and_chooser_share_local_file_validation(tmp_path):
    source = tmp_path / "Bài #2 tiếng Việt.png"
    source.write_bytes(b"image")
    url = QUrl.fromLocalFile(str(source)).toString()
    selection = document_selection([url])
    assert selection == {"valid": True, "url": url, "name": source.name}
    for urls in ([], [url, url], ["https://example.test/bai.pptx"], [QUrl.fromLocalFile(str(tmp_path)).toString()]):
        with pytest.raises(ValueError):
            document_selection(urls)
    bad = tmp_path / "unsupported.exe"
    bad.write_bytes(b"not supported")
    with pytest.raises(ValueError, match="PPTX"):
        document_selection([QUrl.fromLocalFile(str(bad)).toString()])
    with source.open("wb") as stream:
        stream.truncate(MAX_BYTES + 1)
    with pytest.raises(ValueError, match="50 MB"):
        document_selection([url])


def test_non_powerpoint_cannot_request_preserved_design():
    config = creation_config("Bài ảnh", "Sinh học", "THCS", "8", "english_only", "standard", "source")
    with pytest.raises(ValueError, match="PPTX"):
        prompt_preview(config, "file:///C:/lesson.png")
