"""Local release folder: application, user installer and license notices."""
import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
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
    build_info = {"product": "BiliClass", "version": version, "source_commit": commit,
                  "packaged_at_utc": datetime.now(timezone.utc).isoformat()}
    (bundle / "BUILD_INFO.json").write_text(json.dumps(build_info, indent=2), encoding="utf-8")
    # Keep the existing onedir bundle in place; installer and packs sit beside it.
    files = {
        p.relative_to(bundle).as_posix(): file_sha256(p)
        for p in bundle.rglob("*")
        if p.is_file() and (
            "models" not in p.relative_to(bundle).parts
            or p.relative_to(bundle).parts[:2] in {
                ("models", "kokoro-multi-lang-v1_0"), ("models", "vieneu-hf")
            }
        )
    }
    (dist_root / "app-manifest.json").write_text(json.dumps({"product": "BiliClass", "version": version, "files": files}, indent=2), encoding="utf-8")
    shutil.copy2(root / "scripts/Install-BiliClass.ps1", dist_root / "Install-BiliClass.ps1")
    (dist_root / "Setup.cmd").write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-BiliClass.ps1"\r\npause\r\n', encoding="ascii")
    shutil.copy2(root / "docs/USER_GUIDE.md", dist_root / "HUONG_DAN.md")
    print(json.dumps({"application_files": len(files), "version": version, "source_commit": commit,
                      "release_folder": str(dist_root)}))


def file_sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


if __name__ == "__main__":
    main()
