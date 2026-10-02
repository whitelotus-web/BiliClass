import hashlib
import json
import zipfile

import pytest

from app.library import Library
from app.pack import export_pack, import_pack


@pytest.fixture
def library(tmp_path):
    value = Library(tmp_path / "library")
    yield value
    value.close()


def make_pack(library, tmp_path):
    source = tmp_path / "Bài nguồn.txt"
    source.write_text("Đây là nguồn gốc.", encoding="utf-8")
    lesson = library.create(
        "Bài", "Liên môn", "THPT", "11", [("Đoạn", "Đây là nguồn gốc.")], library.store_source(source)
    )
    library.edit_segment(
        lesson["id"], lesson["segments"][0]["id"], "Đây là nguồn gốc.", "This is the source.", True, True
    )
    return lesson, export_pack(library, lesson["id"], tmp_path / "Gói bài.biliclass")


def rewrite(path, change, update_manifest=False):
    with zipfile.ZipFile(path) as archive:
        contents = {name: archive.read(name) for name in archive.namelist()}
    change(contents)
    if update_manifest:
        manifest = json.loads(contents["manifest.json"])
        manifest["files"] = {
            k: {"sha256": hashlib.sha256(v).hexdigest(), "size": len(v)}
            for k, v in contents.items()
            if k != "manifest.json"
        }
        contents["manifest.json"] = json.dumps(manifest).encode()
    with zipfile.ZipFile(path, "w") as archive:
        for key, data in contents.items():
            info = zipfile.ZipInfo()
            info.filename = key  # preserve malicious backslashes on Windows for the test
            archive.writestr(info, data)


def test_roundtrip_creates_copy_and_requires_review(library, tmp_path):
    original, pack = make_pack(library, tmp_path)
    imported = import_pack(library, pack)
    assert imported["id"] != original["id"]
    assert imported["source"] == original["source"]
    assert imported["segments"][0]["en"] == "This is the source."
    assert not imported["segments"][0]["approved"]
    assert imported["segments"][0]["locked"]
    assert len(library.list_lessons()) == 2


def test_corruption_is_rejected_without_import(library, tmp_path):
    _, pack = make_pack(library, tmp_path)
    rewrite(pack, lambda entries: entries.update({"lesson.json": b"{}"}))
    with pytest.raises(ValueError, match="Checksum"):
        import_pack(library, pack)
    assert len(library.list_lessons()) == 1


@pytest.mark.parametrize("name", ["../outside.txt", "/absolute.txt", "C:/outside.txt", "source\\outside.txt"])
def test_traversal_rejected(library, tmp_path, name):
    _, pack = make_pack(library, tmp_path)
    rewrite(pack, lambda entries: entries.update({name: b"bad"}))
    # ZipInfo normalizes backslashes on Windows; an undeclared normalized entry
    # must still be rejected by the manifest check before any file is written.
    with pytest.raises(ValueError, match="không an toàn|không khớp manifest"):
        import_pack(library, pack)
    assert not (tmp_path / "outside.txt").exists()


def test_future_pack_rejected(library, tmp_path):
    _, pack = make_pack(library, tmp_path)

    def change(entries):
        manifest = json.loads(entries["manifest.json"])
        manifest["schema_version"] = 99
        entries["manifest.json"] = json.dumps(manifest).encode()

    rewrite(pack, change)
    with pytest.raises(ValueError, match="Phiên bản"):
        import_pack(library, pack)


def test_arbitrary_source_name_rejected(library, tmp_path):
    _, pack = make_pack(library, tmp_path)

    def change(entries):
        lesson = json.loads(entries["lesson.json"])
        data = entries.pop("source/" + lesson["source"]["file"])
        lesson["source"]["file"] = "overwrite.txt"
        entries["source/overwrite.txt"] = data
        entries["lesson.json"] = json.dumps(lesson).encode()

    rewrite(pack, change, True)
    with pytest.raises(ValueError, match="checksum"):
        import_pack(library, pack)
    assert not (library.directory / "sources/overwrite.txt").exists()


def test_changed_source_cannot_be_exported(library, tmp_path):
    lesson, _ = make_pack(library, tmp_path)
    (library.directory / "sources" / lesson["source"]["file"]).write_bytes(b"modified")
    with pytest.raises(ValueError, match="đã thay đổi"):
        export_pack(library, lesson["id"], tmp_path / "bad.biliclass")
