"""Reuse native measurements only for identical PPTX bytes and verified PNGs."""

import hashlib
import json
import shutil
from pathlib import Path

VERSION = 1
NATIVE_CODES = {"text_overflow", "low_contrast"}
RENDER_CODES = NATIVE_CODES | {"visual_review", "render_unavailable"}


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class RenderCache:
    def __init__(self, path, directory, report, reuse_directory=None):
        self.sha256 = digest(path)
        if self.sha256 != report["sha256"]:
            raise ValueError("PowerPoint đã thay đổi sau khi kiểm tra; cần kiểm tra lại tệp.")
        self.directory = Path(directory)
        self.folder = self.directory / "temp" / "slide-quality" / self.sha256[:24]
        self.folder.mkdir(parents=True, exist_ok=True)
        self.rows = {}
        self.sources = [self.folder]
        if reuse_directory is not None:
            self.sources.append(Path(reuse_directory) / "temp" / "slide-quality" / self.sha256[:24])
        self.caches = []
        for folder in self.sources:
            try:
                cache = json.loads((folder / "render-cache.json").read_text(encoding="utf-8"))
                if (isinstance(cache, dict) and cache.get("version") == VERSION and cache.get("sha256") == self.sha256
                        and isinstance(cache.get("slides"), dict)):
                    self.caches.append((folder, cache["slides"]))
            except (OSError, ValueError, TypeError, KeyError):
                pass

    def image(self, number):
        return self.folder / f"slide-{number}.png"

    def reuse(self, row):
        number = str(row["slide"])
        for folder, entries in self.caches:
            try:
                item = entries[number]
                image = folder / f"slide-{number}.png"
                issues = item["issues"]
                if (not isinstance(issues, list) or any(issue.get("code") not in NATIVE_CODES
                        or issue.get("severity") not in {"FAIL", "CHECK"} for issue in issues)
                        or digest(image) != item["image_sha256"]):
                    continue
                with image.open("rb") as stream:
                    if stream.read(8) != b"\x89PNG\r\n\x1a\n":
                        continue
                destination = self.image(row["slide"])
                if image.resolve() != destination.resolve():
                    temporary = destination.with_suffix(".tmp")
                    shutil.copyfile(image, temporary)
                    temporary.replace(destination)
                row.update(rendered=True, render_image=destination.relative_to(self.directory).as_posix())
                row["issues"].extend(dict(issue) for issue in issues)
                self.rows[number] = item
                return True
            except (OSError, ValueError, TypeError, KeyError, AttributeError):
                continue
        return False

    def save_row(self, row):
        self.rows[str(row["slide"])] = {
            "image_sha256": digest(self.image(row["slide"])),
            "issues": [issue for issue in row["issues"] if issue["code"] in NATIVE_CODES],
        }
        self.save()

    def save(self):
        temporary = self.folder / "render-cache.tmp"
        temporary.write_text(json.dumps({"version": VERSION, "sha256": self.sha256, "slides": self.rows},
                                        ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.folder / "render-cache.json")
