"""Ship installed dependency metadata and complete bundled license notices."""
import importlib.metadata
import json
import re
import shutil
import sys
from pathlib import Path


def main():
    bundle = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "dist/BiliClass"
    root = bundle / "licenses"
    root.mkdir(parents=True, exist_ok=True)
    packages = []
    for dist in importlib.metadata.distributions():
        name, version = dist.metadata.get("Name", "package"), dist.version
        if name.lower() in {"biliclass", "pytest", "ruff", "pyinstaller", "pyinstaller-hooks-contrib"}:
            continue
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", name + "-" + version)
        folder = root / safe_name
        folder.mkdir(exist_ok=True)
        (folder / "METADATA.txt").write_text((dist.read_text("METADATA") or dist.read_text("PKG-INFO") or json.dumps(dict(dist.metadata), ensure_ascii=False)), encoding="utf-8")
        licenses = []
        for path in dist.files or []:
            if any(word in path.name.lower() for word in ("license", "copying", "notice", "copyright")):
                source = Path(dist.locate_file(path))
                if source.is_file() and source.stat().st_size < 5*1024**2:
                    relative = Path(*[part for part in path.parts if part not in ("..", ".")])
                    target = folder / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                    licenses.append(relative.as_posix())
        packages.append({"name": name, "version": version, "notices": licenses,
                         "project_urls": dist.metadata.get_all("Project-URL", [])})
    (root / "DEPENDENCIES.json").write_text(json.dumps(packages, indent=2), encoding="utf-8")
    print(json.dumps({"dependency_notices": len(packages)}))


if __name__ == "__main__":
    main()
