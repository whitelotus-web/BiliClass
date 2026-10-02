"""Download benchmark candidates explicitly; the app never downloads models at runtime."""

import hashlib
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

from biliclass_m0.paths import model_root

INDEX = "https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json"


def main():
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    entries = json.load(urllib.request.urlopen(INDEX, timeout=30))
    root = model_root()
    for source, target in (("vi", "en"), ("en", "vi")):
        entry = next(p for p in entries if p["from_code"] == source and p["to_code"] == target)
        version = entry["package_version"]
        folder = root / f"{source}-{target}-{version}"
        archive = root / f"{source}-{target}-{version}.argosmodel"
        if (folder / "provenance.json").exists():
            print(f"Already prepared: {folder.name}", flush=True)
            continue
        # Official public mirror; the index's argos-net endpoint returned HTTP 403 here.
        filename = f"translate-{source}_{target}-{version.replace('.', '_')}.argosmodel"
        url = "https://data.argosopentech.com/argospm/v1/" + filename
        if not url.startswith("https://"):
            raise ValueError("Only HTTPS model sources are accepted")
        temporary = archive.with_suffix(".download")
        if not archive.exists():
            print(f"Downloading candidate {source} → {target}: {url}", flush=True)
            with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as out:
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > 500 * 1024**2:
                        raise ValueError("Candidate package exceeds 500 MiB")
                    out.write(chunk)
            temporary.replace(archive)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        with zipfile.ZipFile(archive) as package:
            entries_zip = package.infolist()
            if sum(item.file_size for item in entries_zip) > 1024**3:
                raise ValueError("Unpacked model exceeds 1 GiB")
            for item in entries_zip:
                relative = Path(item.filename)
                destination = (folder / relative).resolve()
                if not destination.is_relative_to(folder.resolve()) or ".." in relative.parts:
                    raise ValueError("Unsafe archive path")
                if ((item.external_attr >> 16) & 0o170000) == 0o120000:
                    raise ValueError("Symlink in model archive")
            folder.mkdir(parents=True, exist_ok=True)
            package.extractall(folder)
        metadata = {
            "candidate": "Argos Translate",
            "index": INDEX,
            "url": url,
            "metadata": entry,
            "sha256": digest,
            "download_bytes": archive.stat().st_size,
            "purpose": "M0 benchmark only; not a final model choice",
        }
        (folder / "provenance.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(
            f"Prepared {folder.name}: {archive.stat().st_size / 1024**2:.1f} MiB; SHA-256 {digest}",
            flush=True,
        )


if __name__ == "__main__":
    main()
