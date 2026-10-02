import pytest

from app.library import Library
from app.powerpoint import slide_for_locator, verified_presentation


def test_slide_locator_survives_split():
    assert slide_for_locator("Slide 12 · phần 2") == 12
    assert slide_for_locator("Trang 12") is None
    assert slide_for_locator("Slide 3") == 3


def test_companion_rejects_changed_missing_or_non_pptx_source(tmp_path):
    library = Library(tmp_path / "library")
    path = tmp_path / "Thử.pptx"
    path.write_bytes(b"mock deck")
    source = library.store_source(path)
    saved = verified_presentation({"source": source}, library.directory)
    assert saved.read_bytes() == b"mock deck"
    saved.write_bytes(b"changed")
    with pytest.raises(ValueError, match="thay đổi"):
        verified_presentation({"source": source}, library.directory)
    with pytest.raises(ValueError, match="không có"):
        verified_presentation({"source": None}, library.directory)
    library.close()
