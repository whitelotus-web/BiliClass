"""Local release folder: application, user installer and license notices."""
import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
import os
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    dist_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / "dist"
    if not dist_root.is_relative_to(root) or dist_root == root:
        raise ValueError("Release output must stay inside the project.")
    bundle = dist_root / "BiliClass"
    if not (bundle / "BiliClass.exe").is_file():
        raise ValueError("Build BiliClass.exe first.")
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    sys.path.insert(0, str(root))
    from app import __version__
    if version != __version__:
        raise ValueError('Application and package versions differ; refuse a mislabeled release.')
    previous = json.loads((bundle/'BUILD_INFO.json').read_text(encoding='utf-8-sig')) if (bundle/'BUILD_INFO.json').exists() else {}
    if previous and (previous.get('version') != version or previous.get('source_commit') != commit):
        raise ValueError('The built application does not match this source commit/version.')
    build_info = {**previous, "product": "BiliClass", "version": version, "source_commit": commit,
                  "packaged_at_utc": datetime.now(timezone.utc).isoformat()}
    (bundle / "BUILD_INFO.json").write_text(json.dumps(build_info, indent=2), encoding="utf-8")
    # Keep the existing onedir bundle in place; installer and packs sit beside it.
    files = {
        p.relative_to(bundle).as_posix(): file_sha256(p)
        for p in bundle_files(bundle)
        if (
            "models" not in p.relative_to(bundle).parts
            or p.relative_to(bundle).parts[:2] in {
                ("models", "vieneu-hf"), ("models", "ocr-vi-en-v1"), ("models", "ocr-vi-en-v2")
            }
        )
    }
    (dist_root / "app-manifest.json").write_text(json.dumps({"product": "BiliClass", "version": version, "files": files}, indent=2), encoding="utf-8")
    shutil.copy2(root / "scripts/Install-BiliClass.ps1", dist_root / "Install-BiliClass.ps1")
    (dist_root / "Setup.cmd").write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-BiliClass.ps1"\r\npause\r\n', encoding="ascii")
    shutil.copy2(root / "docs/USER_GUIDE.md", dist_root / "HUONG_DAN.md")
    print(json.dumps({"application_files": len(files), "version": version, "source_commit": commit,
                      "release_folder": str(dist_root)}))


def bundle_files(bundle):
    # On Windows, rglob may omit linked runtime/model directories. The archive
    # and installer need actual files, never junctions to this build machine.
    seen = set()
    for folder, _, names in os.walk(bundle, followlinks=True):
        resolved = Path(folder).resolve()
        if resolved in seen:
            raise ValueError('Repeated runtime directory or link cycle in release.')
        seen.add(resolved)
        for name in names:
            path = Path(folder)/name
            if not path.is_file():
                raise ValueError('Missing runtime file: ' + str(path))
            yield path


def file_sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


if __name__ == "__main__":
    main()
