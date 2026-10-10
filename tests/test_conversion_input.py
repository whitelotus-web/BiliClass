from pathlib import Path

import pytest
from PySide6.QtCore import QUrl

from app.chatgpt_handoff import load_request, prepare_request
from app.conversion_formats import FORMATS, METHODS
from app.conversion_input import creation_config, document_selection, education_grades, prompt_preview
from app.document_limits import MAX_POWERPOINT_BYTES, check_document_size, document_limit
from app.importers import MAX_BYTES


@pytest.mark.parametrize("spec", FORMATS, ids=lambda spec: spec["id"])
@pytest.mark.parametrize("style", ["source", "template"])
@pytest.mark.parametrize("subject", ["Toán", "Giáo dục kinh tế và pháp luật", "STEM – dự án của lớp"])
def test_preview_matches_sent_prompt_with_unicode_filename_and_configuration(tmp_path, spec, style, subject):
    source = tmp_path / "Giáo án #1 – Toán.PPTX"
    source.write_bytes(b"source stays untouched")
    notes = "Giữ từng bước giải.\nDùng thuật ngữ dễ hiểu cho lớp 6; chú ý hình #1."
    config = creation_config("  Diện tích  ", f"  {subject}  ", "THCS", "6", spec["id"], "visual", style, notes)
    before = set(tmp_path.iterdir())
    preview = prompt_preview(config, QUrl.fromLocalFile(str(source)).toString())
    assert set(tmp_path.iterdir()) == before, "Typing a prompt must not create request files"
    sent = prepare_request(tmp_path / "library", config, source)
    assert preview["ready"] and preview["prompt"] == sent["prompt"]
    assert METHODS[spec["id"]] in preview["prompt"]
    assert source.name in preview["prompt"] and "THCS" in preview["prompt"]
    assert source.read_bytes() == b"source stays untouched"
    assert sent["config"]["title"] == "Diện tích" and sent["config"]["subject"] == subject
    assert subject in preview["prompt"]
    assert sent["config"]["teacher_notes"] == notes
    assert preview["prompt"].count(notes) == 1 and load_request(sent["folder"])["prompt"] == preview["prompt"]
    assert preview["prompt"].index(notes) > preview["prompt"].index(METHODS[spec["id"]])


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


def test_pending_powerpoint_choice_has_valid_preview_without_enabling_conversion():
    config = creation_config("Bài", "Toán", "THPT", "10", "parallel_columns", "standard", "source")
    preview = prompt_preview(config)
    assert not preview["ready"] and "CHỈNH BẢN SAO POWERPOINT GỐC" in preview["prompt"]
    assert "Chưa chọn tệp PowerPoint gốc" in preview["prompt"]
    assert "LƯU Ý BỔ SUNG CỦA GIÁO VIÊN" not in preview["prompt"]


@pytest.mark.parametrize("education,allowed", [("Tiểu học", list(map(str, range(1, 6)))),
                                               ("THCS", list(map(str, range(6, 10)))),
                                               ("THPT", ["10", "11", "12"])])
def test_new_conversion_requires_grade_from_selected_education(education, allowed):
    assert education_grades(education) == allowed
    for grade in allowed:
        assert creation_config("Bài", "Toán", education, grade, "english_only", "standard", "template")["grade"] == grade
    for grade in set(map(str, range(1, 13))) - set(allowed):
        with pytest.raises(ValueError, match="khối lớp"):
            creation_config("Bài", "Toán", education, grade, "english_only", "standard", "template")


def test_notes_limit_fails_before_writing_request_or_truncating_notes(tmp_path):
    config = creation_config("Bài", "Toán", "THPT", "10", "sentence_pairs", "standard", "template", "x" * 6001)
    with pytest.raises(ValueError, match="Ghi chú"):
        prepare_request(tmp_path, config, text="Bài học")
    assert not list(tmp_path.iterdir())


def test_powerpoint_limit_is_shared_and_other_document_limits_stay_bounded(tmp_path):
    source = tmp_path / "Bài nhiều hình.PPTX"
    with source.open("wb") as stream:
        stream.truncate(MAX_BYTES + 1)
    assert document_selection([QUrl.fromLocalFile(str(source)).toString()])["valid"]
    assert document_limit(source) == MAX_POWERPOINT_BYTES == 200 * 1024**2
    assert document_limit(source.with_suffix(".pdf")) == MAX_BYTES
    check_document_size(source, MAX_POWERPOINT_BYTES)
    with pytest.raises(ValueError, match="200 MB"):
        check_document_size(source, MAX_POWERPOINT_BYTES + 1)
    with source.open("wb") as stream:
        stream.truncate(MAX_POWERPOINT_BYTES + 1)
    config = creation_config("Bài", "Vật lý", "THPT", "11", "sentence_pairs", "standard", "source")
    with pytest.raises(ValueError, match="200 MB"):
        document_selection([QUrl.fromLocalFile(str(source)).toString()])
    with pytest.raises(ValueError, match="200 MB"):
        prepare_request(tmp_path / "library", config, source)
    assert not (tmp_path / "library").exists()
