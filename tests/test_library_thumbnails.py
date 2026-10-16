import threading

from PIL import Image
from PySide6.QtCore import QCoreApplication, QObject, QUrl

from app.library import Library
from app.library_thumbnails import LibraryThumbnails, cover_image
from test_library_catalog import pump_until


def test_cover_preserves_whole_four_by_three_slide_and_repairs_bad_cache(tmp_path):
    image = tmp_path / 'slide.png'
    Image.new('RGB', (400, 300), '#ff0000').save(image)
    path = cover_image(image, tmp_path)
    with Image.open(path) as cover:
        assert cover.size == (640, 360)
        assert cover.getpixel((80, 0)) == (255, 0, 0)
        assert cover.getpixel((559, 359)) == (255, 0, 0)
        assert cover.getpixel((0, 180)) != (255, 0, 0)
    from pathlib import Path
    Path(path).write_bytes(b'bad thumbnail')
    assert cover_image(image, tmp_path) == path
    with Image.open(path) as restored:
        restored.verify()


def test_queue_is_lazy_background_revision_scoped_and_does_not_edit_lessons(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    first = library.create('Một', 'Toán', 'THCS', '6', [('Slide 1', 'Một')])
    second = library.create('Hai', 'Toán', 'THCS', '6', [('Slide 1', 'Hai')])
    image = tmp_path / 'slide.png'; Image.new('RGB', (320, 180), 'blue').save(image)
    main_thread = threading.get_ident()
    entered, release = threading.Event(), threading.Event()
    calls = []

    def build(lesson, directory):
        assert threading.get_ident() != main_thread
        return {'lesson_id': lesson['id']}

    def render(session, lesson, result, number, **options):
        assert threading.get_ident() != main_thread
        calls.append((lesson['id'], options))
        if lesson['id'] == first['id']:
            entered.set(); assert release.wait(5)
        return str(image)

    monkeypatch.setattr('app.quick_conversion.build_preview', build)
    monkeypatch.setattr('app.slide_preview.PreviewSession.render', render)
    owner = QObject()
    covers = LibraryThumbnails(tmp_path, owner)
    snapshot = library.db.execute('SELECT id, content FROM lessons ORDER BY id').fetchall()
    try:
        app.processEvents()
        assert not calls and covers.worker is None
        covers.request([first])
        pump_until(app, entered.is_set)
        covers.request([second])
        release.set()
        pump_until(app, lambda: covers.worker is None and second['id'] in covers.images and not covers.images[second['id']]['loading'])
        assert first['id'] not in covers.images
        assert QUrl(covers.images[second['id']]['image']).isLocalFile()
        assert list(library.db.execute('SELECT id, content FROM lessons ORDER BY id')) == snapshot
        covers.request([])
        assert not covers.images
        library.trash_lesson(second['id'])
        covers.request([second])
        pump_until(app, lambda: covers.worker is None)
        assert not covers.images[second['id']]['image'] and not covers.images[second['id']]['loading']
    finally:
        release.set(); covers.shutdown(); app.processEvents(); library.close()
