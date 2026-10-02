import json
import zipfile

import pytest

from app.knowledge import builtin_pack, load_pack, validate_pack


def test_builtin_foundation_has_official_sources_and_provenance():
    pack = builtin_pack()
    assert pack["manifest"]["pack_id"] == "vn-education-foundation"
    assert len(pack["sources"]) >= 4
    assert all(source["official"] for source in pack["sources"])
    assert all(entry["source_ids"] for entry in pack["entries"])
    assert all(source_id in {source["id"] for source in pack["sources"]}
               for entry in pack["entries"] for source_id in entry["source_ids"])


def test_validate_rejects_non_https_or_missing_source():
    pack = builtin_pack()
    pack["sources"][0]["source_url"] = "http://example.com"
    with pytest.raises(ValueError, match="HTTPS"):
        validate_pack(pack)

    pack = builtin_pack()
    pack["entries"][0]["source_ids"] = ["missing-source"]
    with pytest.raises(ValueError, match="chưa có"):
        validate_pack(pack)


def test_pack_round_trip_and_zip_allowlist(tmp_path):
    pack = builtin_pack()
    path = tmp_path / "foundation.biliknowledge"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in ("manifest", "sources", "entries"):
            archive.writestr(name + ".json", json.dumps(pack[name], ensure_ascii=False))
    loaded = load_pack(path)
    assert loaded["manifest"] == pack["manifest"]
    assert len(loaded["entries"]) == len(pack["entries"])

    unsafe = tmp_path / "unsafe.biliknowledge"
    with zipfile.ZipFile(unsafe, "w") as archive:
        for name in ("manifest", "sources", "entries"):
            archive.writestr(name + ".json", json.dumps(pack[name]))
        archive.writestr("unexpected.txt", "no")
    with pytest.raises(ValueError, match="cấu trúc"):
        load_pack(unsafe)


def test_install_pack_is_separate_from_teacher_glossary(tmp_path):
    from app.knowledge import ensure_builtin_foundation
    from app.library import Library

    library = Library(tmp_path / "library")
    library.save_term("Toán", "hàm số", "function", True)
    assert ensure_builtin_foundation(library)
    assert library.knowledge_stats()["entries"] >= 20
    assert library.knowledge_entries("competence")[0]["vi"] == "Năng lực"
    assert library.glossary("Toán")[0]["en"] == "function"
    assert not ensure_builtin_foundation(library)
    library.close()


def test_foundation_wins_over_online_and_newer_pack_survives_restart(tmp_path):
    from app.knowledge import ensure_builtin_foundation
    from app.library import Library

    library = Library(tmp_path)
    ensure_builtin_foundation(library)
    pack = builtin_pack()
    pack["manifest"]["pack_id"] = "online-test"
    pack["sources"] = [dict(pack["sources"][0], id="online-source", source_type="online_reference")]
    pack["entries"] = [dict(pack["entries"][2], id="online-entry", en="Online alternative",
                            source_ids=["online-source"])]
    library.install_knowledge_pack(pack)
    assert library.knowledge_translation("Toán", "Năng lực")["text"] == "Competence"
    foundation = builtin_pack()
    foundation["manifest"]["version"] = "2026.10.03"
    library.install_knowledge_pack(foundation)
    assert not ensure_builtin_foundation(library)
    assert library.knowledge_pack("vn-education-foundation")["version"] == "2026.10.03"
    library.close()
