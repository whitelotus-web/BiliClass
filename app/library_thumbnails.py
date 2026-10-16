"""Lazy first-slide covers; no library writes or Office work on the GUI thread."""

import hashlib
from contextlib import closing
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Property, QThread, QUrl, Signal, Slot

from .library import Library
from .slide_preview import PreviewSession


def cover_image(image, directory):
    """Small, content-addressed 16:9 image; preserve the entire original slide."""
    from PIL import Image, ImageOps

    data = Path(image).read_bytes()
    folder = Path(directory) / 'temp/library-covers'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (hashlib.sha256(data).hexdigest() + '.png')
    if target.is_file():
        try:
            with Image.open(target) as saved:
                saved.verify()
            return str(target)
        except (OSError, ValueError):
            pass
    with Image.open(image) as original:
        fitted = ImageOps.contain(original.convert('RGB'), (640, 360), Image.Resampling.LANCZOS)
    cover = Image.new('RGB', (640, 360), '#e9eef5')
    cover.paste(fitted, ((640 - fitted.width) // 2, (360 - fitted.height) // 2))
    pending = target.with_suffix('.pending.png')
    cover.save(pending)
    pending.replace(target)
    return str(target)


class CoverJob(QThread):
    ready = Signal(object)

    def __init__(self, directory, rows, parent):
        super().__init__(parent)
        self.directory, self.rows = Path(directory), rows
        self.cancel = Event()

    def publish(self, key, image=''):
        if not self.cancel.is_set():
            self.ready.emit((key, QUrl.fromLocalFile(image).toString() if image else ''))

    def run(self):
        try:
            self._run()
        except Exception:
            for key in self.rows:
                self.publish(key)

    def _run(self):
        from .chatgpt_handoff import external_preview
        from .quick_conversion import build_preview

        pending = []
        with closing(Library.read_only(self.directory)) as library:
            # Publish every existing cover before waiting for any new render.
            for key in self.rows:
                if self.cancel.is_set():
                    return
                try:
                    lesson = library.get(key[0])
                    if lesson['revision'] != key[1]:
                        self.publish(key)
                        continue
                    result = (external_preview(lesson, self.directory) if lesson.get('external_deck')
                              else build_preview(lesson, self.directory))
                    session = PreviewSession(self.directory)
                    try:
                        image = session.render(lesson, result, 1, cached_only=True)
                    except LookupError:
                        pending.append((key, session, lesson, result))
                    else:
                        self.publish(key, cover_image(image, self.directory))
                except Exception:
                    self.publish(key)
            for key, session, lesson, result in pending:
                if self.cancel.is_set():
                    return
                try:
                    try:
                        image = session.render(lesson, result, 1, neighbours=False)
                    except ValueError:
                        # Office can change NTFS metadata on first open. Recheck
                        # the exact deck and PNG hashes before accepting its
                        # existing render; changed source bytes still fail.
                        image = PreviewSession(self.directory).render(lesson, result, 1, cached_only=True)
                    self.publish(key, cover_image(image, self.directory))
                except Exception:
                    self.publish(key)


class LibraryThumbnails(QObject):
    changed = Signal()

    def __init__(self, directory, parent):
        super().__init__(parent)
        self.directory = Path(directory)
        self.worker = None
        self.wanted = ()
        self.results = {}
        self.closed = False
        parent.destroyed.connect(self.shutdown)

    @Property('QVariantMap', notify=changed)
    def images(self):
        return {key[0]: {'image': self.results.get(key, ''), 'loading': key not in self.results}
                for key in self.wanted}

    def request(self, rows):
        wanted = tuple((row['id'], row['revision']) for row in rows)
        if wanted == self.wanted or self.closed:
            return
        self.wanted = wanted
        self.results = {key: value for key, value in self.results.items() if key in wanted}
        self.changed.emit()
        if self.worker is not None:
            self.worker.cancel.set()
        else:
            self._start()

    def _start(self):
        rows = [key for key in self.wanted if key not in self.results]
        if not rows or self.closed:
            return
        self.worker = CoverJob(self.directory, rows, self)
        self.worker.ready.connect(self._ready)
        self.worker.finished.connect(self._finished)
        self.worker.start()

    @Slot(object)
    def _ready(self, result):
        key, image = result
        if not self.closed and self.sender() is self.worker and key in self.wanted:
            self.results[key] = image
            self.changed.emit()

    @Slot()
    def _finished(self):
        worker = self.sender()
        if worker is None or worker is not self.worker:
            return
        self.worker = None
        worker.deleteLater()
        self._start()

    @Slot()
    def shutdown(self):
        self.closed = True
        self.wanted = ()
        if self.worker is not None:
            worker, self.worker = self.worker, None
            worker.cancel.set()
            worker.wait()
            worker.deleteLater()

    def replace_library(self, directory):
        self.shutdown()
        self.directory = Path(directory)
        self.results = {}
        self.closed = False
        self.changed.emit()
