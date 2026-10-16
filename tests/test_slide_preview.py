"""Exact-file preview hits must avoid PPTX reparsing and reject changed bytes."""

import hashlib
import json
import os
from pathlib import Path

import pytest
from PIL import Image

from app.slide_preview import PreviewSession


def fixture(tmp_path, monkeypatch):
    deck = tmp_path / "source.pptx"
    deck.write_bytes(b"original presentation")
    sha = hashlib.sha256(deck.read_bytes()).hexdigest()
    lesson = {"id": "lesson", "revision": 1}
    result = {"path": str(deck), "sha256": sha, "total": 2}
    calls = []

    def verify(lesson, result, directory):
        calls.append(str(deck))
        if hashlib.sha256(deck.read_bytes()).hexdigest() != result["sha256"]:
            raise ValueError("changed")
        return deck

    monkeypatch.setattr("app.quick_conversion.verify_preview", verify)
    monkeypatch.setattr("app.slide_fingerprint.environment_key", lambda: "fixture")
    folder = tmp_path / "temp/slide-quality" / sha[:24]
    folder.mkdir(parents=True)
    index = {}
    for n in (1, 2):
        image = folder / f"slide-{n}.png"
        Image.new("RGB", (128, 72), "blue" if n == 1 else "green").save(image)
        index[str(n)] = {
            "environment": "fixture",
            "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
        }
    (folder / "render-cache.json").write_text(
        json.dumps({"version": 2, "sha256": sha, "slides": index}), encoding="utf-8"
    )
    return deck, lesson, result, calls, folder


def test_repeated_pages_verify_deck_once_and_do_not_start_office(tmp_path, monkeypatch):
    deck, lesson, result, calls, folder = fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "app.powerpoint_review.render_preview_pages", lambda *_: pytest.fail("Office started on cache hit")
    )
    monkeypatch.setattr(
        "app.slide_fingerprint.SlideFingerprints.keys", lambda *_: pytest.fail("PPTX parsed per click")
    )
    session = PreviewSession(tmp_path)
    for page in [1, 2, 1, 2, 2, 1]:
        assert Path(session.render(lesson, result, page)) == folder / f"slide-{page}.png"
    assert len(calls) == 1


def test_same_size_deck_change_invalidates_verification(tmp_path, monkeypatch):
    deck, lesson, result, calls, folder = fixture(tmp_path, monkeypatch)
    session = PreviewSession(tmp_path)
    session.render(lesson, result, 1)
    state = deck.stat()
    deck.write_bytes(b"changed! presentation")
    os.utime(deck, ns=(state.st_atime_ns, state.st_mtime_ns))
    with pytest.raises(ValueError, match="changed"):
        session.render(lesson, result, 2)
    assert len(calls) == 2


def test_changed_png_never_returns_a_stale_verified_image(tmp_path, monkeypatch):
    deck, lesson, result, calls, folder = fixture(tmp_path, monkeypatch)
    session = PreviewSession(tmp_path)
    session.render(lesson, result, 1)
    image = folder / "slide-1.png"
    image.write_bytes(b"broken png")

    def fallback(*_):
        raise ValueError("needs fresh render")

    monkeypatch.setattr("app.powerpoint_review.render_preview_pages", fallback)
    with pytest.raises(ValueError, match="fresh render"):
        session.render(lesson, result, 1)


def test_revision_change_revalidates_even_with_same_source_file(tmp_path, monkeypatch):
    deck, lesson, result, calls, folder = fixture(tmp_path, monkeypatch)
    session = PreviewSession(tmp_path)
    session.render(lesson, result, 1)
    session.render({**lesson, "revision": 2}, result, 2)
    assert len(calls) == 2


def test_library_cover_checks_cache_before_rendering_only_page_one(tmp_path, monkeypatch):
    deck, lesson, result, calls, folder = fixture(tmp_path, monkeypatch)
    session = PreviewSession(tmp_path)
    assert session.render(lesson, result, 1, cached_only=True) == str(folder / 'slide-1.png')
    (folder / 'slide-1.png').unlink()
    with pytest.raises(LookupError):
        session.render(lesson, result, 1, cached_only=True)
    rendered = []

    def render(path, pages, directory, digest):
        rendered.extend(pages)
        return folder, {'slides': {}}

    monkeypatch.setattr('app.powerpoint_review.render_preview_pages', render)
    session.render(lesson, result, 1, neighbours=False)
    assert rendered == [1]
