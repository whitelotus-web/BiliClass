import json
from pathlib import Path
from threading import Event
from types import SimpleNamespace

import pytest
from PIL import Image

from app.powerpoint_review import render_slide
from app.slide_quality import render_quality
from app.slide_render_cache import RenderCache, digest


def report(path, count=2):
    return {"sha256": digest(path), "slides": [{"slide": i, "rendered": False, "issues": [
        {"code": "formula_needs_review", "severity": "CHECK"}]} for i in range(1, count+1)]}


def office_fixture(monkeypatch, cancel=None, *, date_slides=()):
    calls = []

    class Slide:
        Shapes = [SimpleNamespace(Type=17, Rotation=0, HasTextFrame=True, TextFrame2=SimpleNamespace(HasText=True,
            TextRange=SimpleNamespace(BoundHeight=50, BoundWidth=50, Text='Overflowing fixture text')), Height=20, Width=20,
            Fill=SimpleNamespace(Visible=False), Id=7)]

        def __init__(self, index):
            self.HeadersFooters = SimpleNamespace(DateAndTime=SimpleNamespace(Visible=index in date_slides))

        def Export(self, path, kind, width, height):
            calls.append(Path(path).name)
            Image.new("RGB", (16, 9), "white").save(path)
            if cancel:
                cancel.set()

    deck = SimpleNamespace(Slides=lambda index: Slide(index), Close=lambda: None,
                           PageSetup=SimpleNamespace(SlideHeight=9, SlideWidth=16))
    office = SimpleNamespace(Presentations=SimpleNamespace(Open=lambda *a, **kw: deck, Count=0), Quit=lambda: None)
    monkeypatch.setattr("win32com.client.DispatchEx", lambda name: office)
    return calls


def test_import_and_preview_reuse_native_images_and_measurements_without_office(tmp_path, monkeypatch):
    path = tmp_path / "deck.pptx"
    path.write_bytes(b"immutable pptx")
    calls = office_fixture(monkeypatch)
    initial = render_quality(path, tmp_path / "web", report(path))
    assert len(calls) == 2 and initial["counts"]["FAIL"] == 2
    monkeypatch.setattr("win32com.client.DispatchEx", lambda *_: pytest.fail("Must reuse native checks"))
    fresh = report(path)
    fresh["slides"][0]["issues"] = [{"code": "english_body_missing", "severity": "CHECK"}]
    imported = render_quality(path, tmp_path / "library", fresh, reuse_directory=tmp_path / "web")
    assert imported["render_cache"] == {"reused": 2, "rendered": 0, "total": 2}
    assert imported["counts"]["FAIL"] == 2
    codes = [i["code"] for i in imported["slides"][0]["issues"]]
    assert "english_body_missing" in codes and "formula_needs_review" not in codes
    assert codes.count("visual_review") == 1 and codes.count("text_overflow") == 1
    assert Path(render_slide(path, 1, tmp_path / "library")).is_file()
    render_quality(path, tmp_path / "library", imported)
    assert len(imported["slides"][0]["issues"]) == 3


def test_changed_pptx_corrupt_png_and_cache_version_are_never_trusted(tmp_path, monkeypatch):
    path = tmp_path / "deck.pptx"
    path.write_bytes(b"original")
    calls = office_fixture(monkeypatch)
    quality = render_quality(path, tmp_path, report(path))
    folder = tmp_path / "temp" / "slide-quality" / quality["sha256"][:24]
    (folder / "slide-1.png").write_bytes(b"broken")
    quality = render_quality(path, tmp_path, report(path))
    assert quality["render_cache"]["reused"] == 1 and len(calls) == 3
    checkpoint = folder / "render-cache.json"
    saved = json.loads(checkpoint.read_text())
    saved["version"] = -1
    checkpoint.write_text(json.dumps(saved))
    render_quality(path, tmp_path, report(path))
    assert len(calls) == 5
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="thay đổi"):
        RenderCache(path, tmp_path, quality)
    render_quality(path, tmp_path, report(path))
    assert len(calls) == 7


def test_cancelled_partial_render_resumes_only_missing_slides(tmp_path, monkeypatch):
    path = tmp_path / "deck.pptx"
    path.write_bytes(b"original")
    cancel = Event()
    calls = office_fixture(monkeypatch, cancel)
    quality = render_quality(path, tmp_path, report(path), cancel)
    assert len(calls) == 1 and quality["render_cache"]["total"] == 2
    cancel.clear()
    calls = office_fixture(monkeypatch)
    quality = render_quality(path, tmp_path, report(path), cancel)
    assert len(calls) == 1 and quality["render_cache"]["reused"] == 1


def test_missing_office_is_not_cached_as_a_success(tmp_path, monkeypatch):
    path = tmp_path / "deck.pptx"
    path.write_bytes(b"original")
    monkeypatch.setattr("win32com.client.DispatchEx", lambda *_: (_ for _ in ()).throw(RuntimeError("missing Office")))
    quality = render_quality(path, tmp_path, report(path))
    assert not any(row["rendered"] for row in quality["slides"])
    calls = office_fixture(monkeypatch)
    quality = render_quality(path, tmp_path, report(path))
    assert len(calls) == 2 and quality["render_cache"]["reused"] == 0


def test_table_overflow_keeps_owner_and_cell_while_empty_formatted_cells_are_ignored(tmp_path, monkeypatch):
    path = tmp_path/'table.pptx'
    path.write_bytes(b'fixture table')
    office_fixture(monkeypatch)
    cell = SimpleNamespace(HasTextFrame=True, TextFrame2=SimpleNamespace(HasText=True,
        TextRange=SimpleNamespace(Text='A long translated cell', BoundHeight=50, BoundWidth=50)),
        Width=20, Height=20, Fill=SimpleNamespace(Visible=False))
    empty = SimpleNamespace(HasTextFrame=True, TextFrame2=SimpleNamespace(HasText=True,
        TextRange=SimpleNamespace(Text='\r ', BoundHeight=99, BoundWidth=99)), Width=20, Height=20)
    # A real PowerPoint cell shape raises when its Id is accessed.
    monkeypatch.setattr('app.native_layout.office_table_cells', lambda *_: [(cell, 44, [1, 0]), (empty, 44, [1, 1])])
    quality = render_quality(path, tmp_path, report(path, 1))
    issues = quality['slides'][0]['issues']
    cells = [issue for issue in issues if 'cell' in issue]
    assert len(cells) == 1
    assert cells[0]['shape_id'] == 44 and cells[0]['cell'] == [1, 0] and cells[0]['severity'] == 'FAIL'
