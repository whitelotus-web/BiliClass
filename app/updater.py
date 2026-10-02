"""Public-release updater; lesson data remains outside versioned app folders."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from . import __version__

RELEASES_API = "https://api.github.com/repos/whitelotus-web/BiliClass/releases?per_page=30"
DOWNLOAD_PREFIX = "/whitelotus-web/BiliClass/releases/download/"
MAX_ARCHIVE = 2 * 1024**3 - 1
MAX_UNPACKED = 4 * 1024**3
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "BiliClass-Updater"}
VERSION_PATTERN = re.compile(r"v?(\d+)\.(\d+)\.(\d+)(?:rc(\d+))?\Z")


def version_key(value):
    match = VERSION_PATTERN.fullmatch(value or "")
    if not match:
        raise ValueError("Phiên bản không hợp lệ.")
    major, minor, patch, rc = match.groups()
    return int(major), int(minor), int(patch), int(rc is None), int(rc or 0)


def _fetch_json(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Thông tin phát hành quá lớn.")
    return json.loads(data)


def _asset_name(version):
    match = VERSION_PATTERN.fullmatch(version)
    if not match:
        raise ValueError("Phiên bản không hợp lệ.")
    suffix = f"RC{match.group(4)}" if match.group(4) else version.lstrip("v")
    return f"BiliClass-{suffix}-Windows.zip"


def _valid_url(url, tag, name):
    parsed = urlparse(url)
    return (parsed.scheme == "https" and parsed.netloc == "github.com" and not parsed.query
            and not parsed.fragment and parsed.path == DOWNLOAD_PREFIX + tag + "/" + name)


def check_for_update(current=__version__, fetch=None):
    """Include prereleases: GitHub's /releases/latest endpoint omits them."""
    releases = (fetch or _fetch_json)(RELEASES_API)
    if not isinstance(releases, list):
        raise ValueError("Không đọc được danh sách phiên bản GitHub.")
    available = []
    for release in releases:
        tag = release.get("tag_name", "")
        try:
            if release.get("draft") or version_key(tag) <= version_key(current):
                continue
            name = _asset_name(tag)
        except ValueError:
            continue
        for asset in release.get("assets", []):
            url = asset.get("browser_download_url", "")
            digest = asset.get("digest", "")
            size = asset.get("size", 0)
            if (asset.get("name") == name and _valid_url(url, tag, name)
                    and isinstance(size, int) and 0 < size <= MAX_ARCHIVE
                    and re.fullmatch(r"sha256:[0-9a-f]{64}", digest or "")):
                available.append({"version": tag.lstrip("v"), "tag": tag, "url": release.get("html_url", ""),
                                  "asset_url": url, "asset_name": name, "size": size, "digest": digest[7:]})
                break
    return max(available, key=lambda value: version_key(value["version"])) if available else None


def _safe_entries(archive, version):
    entries = archive.infolist()
    names = [entry.filename for entry in entries if not entry.is_dir()]
    if len(entries) > 10000 or len(set(names)) != len(names):
        raise ValueError("Gói cập nhật có danh sách tệp không hợp lệ.")
    if sum(entry.file_size for entry in entries) > MAX_UNPACKED:
        raise ValueError("Gói cập nhật giải nén vượt giới hạn.")
    for entry in entries:
        name = entry.filename
        path = PurePosixPath(name)
        kind = (entry.external_attr >> 16) & 0o170000
        if (not path.parts or path.is_absolute() or ".." in path.parts or ":" in name or "\\" in name
                or kind == 0o120000 or path.parts[0] not in (
                    "BiliClass", "app-manifest.json", "Setup.cmd", "Install-BiliClass.ps1", "HUONG_DAN.md")
                or (path.parts[0] != "BiliClass" and len(path.parts) != 1)
                or (name == "BiliClass" and not entry.is_dir())):
            raise ValueError("Gói cập nhật chứa đường dẫn không an toàn.")
    required = {"BiliClass/BiliClass.exe", "app-manifest.json", "Install-BiliClass.ps1"}
    if not required.issubset(names):
        raise ValueError("Gói cập nhật thiếu tệp cài đặt.")
    manifest = json.loads(archive.read("app-manifest.json"))
    if (manifest.get("product") != "BiliClass" or manifest.get("version") != version
            or not isinstance(manifest.get("files"), dict)
            or not {"BiliClass/" + name for name in manifest["files"]}.issubset(names)):
        raise ValueError("Manifest của gói cập nhật không khớp phiên bản.")
    return entries


def download_and_stage(release, data_root, progress=None, cancelled=None, opener=None):
    """Download, verify the GitHub SHA-256, then extract only safe archive paths."""
    if not _valid_url(release["asset_url"], release["tag"], release["asset_name"]):
        raise ValueError("Địa chỉ tải bản cập nhật không hợp lệ.")
    updates = Path(data_root).resolve() / "updates"
    updates.mkdir(parents=True, exist_ok=True)
    required_space = release["size"] * 3 + 512 * 1024**2
    if shutil.disk_usage(updates).free < required_space:
        raise ValueError("Ổ đĩa thiếu chỗ để tải và cài bản mới.")
    staging = Path(tempfile.mkdtemp(prefix="biliclass-update-", dir=updates)).resolve()
    if staging.parent != updates:
        raise ValueError("Thư mục cập nhật không hợp lệ.")
    archive_path = staging / release["asset_name"]
    try:
        request = urllib.request.Request(release["asset_url"], headers=HEADERS)
        digest = hashlib.sha256()
        count = 0
        with (opener or urllib.request.urlopen)(request, timeout=60) as response, archive_path.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                if cancelled and cancelled.is_set():
                    raise ValueError("Đã hủy tải bản cập nhật.")
                count += len(chunk)
                if count > MAX_ARCHIVE or count > release["size"]:
                    raise ValueError("Gói tải về vượt kích thước công bố.")
                output.write(chunk)
                digest.update(chunk)
                if progress:
                    progress(round(count / release["size"] * 100))
        if count != release["size"] or digest.hexdigest() != release["digest"]:
            raise ValueError("Checksum gói cập nhật không khớp GitHub.")
        package = staging / "package"
        package.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            entries = _safe_entries(archive, release["version"])
            for entry in entries:
                if cancelled and cancelled.is_set():
                    raise ValueError("Đã hủy tải bản cập nhật.")
                archive.extract(entry, package)
        archive_path.unlink()
        return package
    except Exception:
        if staging.parent == updates:
            shutil.rmtree(staging, ignore_errors=True)
        raise


def launch_install(package, process_id):
    """Install in a separate process after the running application exits."""
    script = Path(package).resolve() / "Install-BiliClass.ps1"
    if not script.is_file() or os.name != "nt" or not getattr(sys, "frozen", False):
        raise ValueError("Chỉ bản Windows đóng gói mới có thể tự cài cập nhật.")
    log_path = script.parent.parent / "install.log"
    command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
               "-WaitForProcessId", str(process_id), "-LaunchAfterInstall"]
    with log_path.open("wb") as log:
        subprocess.Popen(command, cwd=script.parent, stdout=log, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NO_WINDOW)
