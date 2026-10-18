"""Reuse native measurements only for identical PPTX bytes and verified PNGs."""

import hashlib
import json
import os
import shutil
from datetime import date
from pathlib import Path

VERSION = 3
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
        from .slide_fingerprint import SlideFingerprints, environment_key

        self.environment=environment_key()
        self.slide_keys=SlideFingerprints(path).keys()
        self.shared=self.directory/'temp/slide-quality/by-slide'
        self.shared_sources=[self.shared]
        if reuse_directory is not None:
            self.shared_sources.append(Path(reuse_directory)/'temp/slide-quality/by-slide')
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
        key=self.slide_keys.get(number) if self.slide_keys is not None else None
        if self.slide_keys is not None and key is None:
            return False
        candidates=[]
        for folder,entries in self.caches:
            if number in entries:
                candidates.append((folder/f'slide-{number}.png',entries[number]))
        if key:
            for shared in self.shared_sources:
                try:
                    item=json.loads((shared/(key+'.json')).read_text(encoding='utf-8'))
                    candidates.append((shared/(key+'.png'),item))
                except (OSError,ValueError,TypeError):
                    continue
        for image,item in candidates:
            try:
                issues = item["issues"]
                if (item.get('environment')!=self.environment or (key and item.get('slide_key')!=key)
                        or item.get('date_sensitive', True) and item.get('rendered_date') != date.today().isoformat()
                        or not isinstance(issues, list) or any(issue.get("code") not in NATIVE_CODES
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
                # A verified image imported from a request/library cache must
                # remain reusable after another slide is repaired here.
                # Otherwise the next pass redraws every unchanged slide.
                try:
                    self._share(row['slide'], item)
                except OSError:
                    pass  # A cache write failure cannot invalidate this hit.
                return True
            except (OSError, ValueError, TypeError, KeyError, AttributeError):
                continue
        return False

    def save_row(self, row):
        self.rows[str(row["slide"])] = {
            "image_sha256": digest(self.image(row["slide"])),
            "issues": [dict(issue,severity='FAIL' if issue['code']=='text_overflow' else issue['severity'])
                       for issue in row["issues"] if issue["code"] in NATIVE_CODES],
            'date_sensitive': row.get('date_sensitive', True), 'rendered_date': date.today().isoformat(),
            'environment':self.environment,
            'slide_key':self.slide_keys.get(str(row['slide'])) if self.slide_keys is not None else None,
        }
        self._share(row['slide'], self.rows[str(row['slide'])])
        self.save()

    def _share(self, number, item):
        # Publishing a single preview hit must not overwrite the manifest of
        # other slides, which this cache instance has not visited.
        key=item['slide_key']
        if key:
            self.shared.mkdir(parents=True,exist_ok=True)
            image=self.shared/(key+'.png')
            if not image.exists() or digest(image)!=item['image_sha256']:
                temporary=image.with_suffix('.png.tmp')
                temporary.unlink(missing_ok=True)
                try:
                    os.link(self.image(number),temporary)
                except OSError:
                    shutil.copyfile(self.image(number),temporary)
                temporary.replace(image)
            temporary=self.shared/(key+'.json.tmp')
            temporary.write_text(json.dumps(item),encoding='utf-8')
            temporary.replace(self.shared/(key+'.json'))

    def save(self):
        temporary = self.folder / "render-cache.tmp"
        temporary.write_text(json.dumps({"version": VERSION, "sha256": self.sha256, "slides": self.rows},
                                        ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.folder / "render-cache.json")
