import hashlib
import io
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from app.updater import check_for_update, download_and_stage, version_key


def release(version, digest="sha256:" + "a" * 64, name=None):
    tag = "v" + version
    file_name = name or f"BiliClass-RC{version.rsplit('rc', 1)[1]}-Windows.zip"
    return {"tag_name": tag, "draft": False, "html_url": f"https://github.com/whitelotus-web/BiliClass/releases/tag/{tag}",
            "assets": [{"name": file_name, "size": 42, "digest": digest,
                        "browser_download_url": f"https://github.com/whitelotus-web/BiliClass/releases/download/{tag}/{file_name}"}]}


def archive_bytes(version="1.0.0rc12", extra=None):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("BiliClass/BiliClass.exe", b"exe fixture")
        archive.writestr("Install-BiliClass.ps1", b"installer fixture")
        archive.writestr("app-manifest.json", json.dumps({"product": "BiliClass", "version": version,
                            "files": {"BiliClass.exe": hashlib.sha256(b"exe fixture").hexdigest()}}))
        if extra:
            archive.writestr(extra, b"unsafe")
    return stream.getvalue()


def package_info(payload, version="1.0.0rc12"):
    info = release(version, "sha256:" + hashlib.sha256(payload).hexdigest())
    asset = info["assets"][0]
    asset["size"] = len(payload)
    return {"version": version, "tag": info["tag_name"], "asset_name": asset["name"],
            "asset_url": asset["browser_download_url"], "size": len(payload), "digest": asset["digest"][7:]}


def test_release_selection_includes_rc_and_rejects_untrusted_assets():
    assert version_key("1.0.0rc12") > version_key("1.0.0rc11")
    assert version_key("1.0.0") > version_key("1.0.0rc99")
    releases = [release("1.0.0rc13"), release("1.0.0rc12"), release("1.0.0rc14", digest=""),
                release("1.0.0rc15", name="wrong.zip")]
    selected = check_for_update("1.0.0rc11", fetch=lambda _: releases)
    assert selected["version"] == "1.0.0rc13"
    assert check_for_update("1.0.0rc13", fetch=lambda _: releases) is None
    assert check_for_update("1.0.0rc11", fetch=lambda _: [{**releases[0], "draft": True}]) is None


def test_download_verifies_digest_and_extracts_package(tmp_path):
    payload = archive_bytes()
    progress = []
    package = download_and_stage(package_info(payload), tmp_path, progress.append,
                                 opener=lambda request, timeout: io.BytesIO(payload))
    assert (package / "BiliClass" / "BiliClass.exe").read_bytes() == b"exe fixture"
    assert not (package.parent / "BiliClass-RC12-Windows.zip").exists()
    assert progress[-1] == 100
    bad = package_info(payload)
    bad["digest"] = "0" * 64
    with pytest.raises(ValueError, match="Checksum"):
        download_and_stage(bad, tmp_path, opener=lambda request, timeout: io.BytesIO(payload))


@pytest.mark.parametrize("entry", ["../outside.txt", "BiliClass/../../outside.txt", "C:/outside.txt"])
def test_archive_path_cannot_escape_staging(tmp_path, entry):
    payload = archive_bytes(extra=entry)
    with pytest.raises(ValueError, match="không an toàn"):
        download_and_stage(package_info(payload), tmp_path,
                           opener=lambda request, timeout: io.BytesIO(payload))
    assert not (tmp_path / "outside.txt").exists()


def test_archive_symlink_is_rejected(tmp_path):
    source = io.BytesIO(archive_bytes())
    output = io.BytesIO()
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, "w") as archive:
        for entry in original.infolist():
            archive.writestr(entry, original.read(entry))
        link = zipfile.ZipInfo("BiliClass/link")
        link.create_system = 3
        link.external_attr = 0o120777 << 16
        archive.writestr(link, "outside")
    payload = output.getvalue()
    with pytest.raises(ValueError, match="không an toàn"):
        download_and_stage(package_info(payload), tmp_path,
                           opener=lambda request, timeout: io.BytesIO(payload))


@pytest.mark.skipif(os.name != "nt", reason="PowerShell installer is Windows-only")
def test_new_version_installs_beside_old_without_touching_lessons(tmp_path):
    installer = Path(__file__).resolve().parents[1] / "scripts" / "Install-BiliClass.ps1"
    root = tmp_path / "Programs" / "BiliClass"
    library = tmp_path / "teacher-library"
    library.mkdir()
    (library / "library.db").write_bytes(b"personal lessons fixture")
    for version in ("1.0.0rc11", "1.0.0rc12"):
        package = tmp_path / version
        application = package / "BiliClass"
        application.mkdir(parents=True)
        executable = application / "BiliClass.exe"
        executable.write_bytes(version.encode())
        shutil.copy2(installer, package / "Install-BiliClass.ps1")
        (package / "app-manifest.json").write_text(json.dumps({
            "product": "BiliClass", "version": version,
            "files": {"BiliClass.exe": hashlib.sha256(executable.read_bytes()).hexdigest()},
        }), encoding="utf-8")
        result = subprocess.run([
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
            str(package / "Install-BiliClass.ps1"), "-InstallRoot", str(root),
            "-NoShortcuts", "-WaitForProcessId", "999999999",
        ], capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
    assert (root / "1.0.0rc11" / "BiliClass.exe").is_file()
    assert (root / "1.0.0rc12" / "BiliClass.exe").is_file()
    assert json.loads((root / ".biliclass-install.json").read_text(encoding="utf-8-sig"))["version"] == "1.0.0rc12"
    assert (library / "library.db").read_bytes() == b"personal lessons fixture"
