import hashlib
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QUrl

from app.export_origin import bind_lesson, destination, remember_source
from app.library import Library
from app.ui import Bridge


def test_source_folder_name_and_lesson_binding_survive_restart_without_entering_lesson(tmp_path):
    source_dir = tmp_path/'Giáo án #1'
    source_dir.mkdir()
    source = source_dir/'Bài gốc tiếng Việt.pptx'
    source.write_bytes(b'original immutable source fixture')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    data = tmp_path/'library'
    with closing(Library(data)) as library:
        lesson = library.create('Tên hiển thị khác', 'Vật lý', 'THPT', '11', [('Mở đầu', 'Năng lượng')])
        remember_source(library, source, digest)
        bind_lesson(library, lesson, digest)
        assert library.get(lesson['id']) == lesson
    with closing(Library(data)) as library:
        assert destination(library, lesson, tmp_path) == (source_dir, source.stem)
        # An identical file imported from another folder cannot move the first
        # lesson's default location once its own origin has been bound.
        copy = tmp_path/'Bản sao.pptx'
        copy.write_bytes(source.read_bytes())
        remember_source(library, copy, digest)
        assert destination(library, lesson, tmp_path) == (source_dir, source.stem)
        assert source.read_bytes() == b'original immutable source fixture'


def test_missing_source_folder_falls_back_but_keeps_original_stem_and_rejects_internal_paths(tmp_path):
    data, source_dir = tmp_path/'library', tmp_path/'Bài gốc'
    source_dir.mkdir()
    source = source_dir/'Cơ năng.pptx'
    source.write_bytes(b'fixture')
    with closing(Library(data)) as library:
        lesson = library.create('Bài mới', 'Vật lý', 'THPT', '11', [('Mở đầu', 'Năng lượng')])
        remember_source(library, source, 'fixture')
        bind_lesson(library, lesson, 'fixture')
        source.unlink()
        source_dir.rmdir()
        assert destination(library, lesson, tmp_path) == (tmp_path, 'Cơ năng')
        internal = data/'sources/source.pptx'
        internal.parent.mkdir(exist_ok=True)
        internal.write_bytes(b'internal')
        remember_source(library, internal, 'internal')
        assert not library.setting('export_origin_source:internal', {})


def test_single_presentation_downloads_use_origin_and_current_suffix_while_bulk_keeps_global_folder(tmp_path):
    source_dir, downloads = tmp_path/'Giáo án', tmp_path/'Downloads'
    source_dir.mkdir()
    downloads.mkdir()
    source = source_dir/'Bài Việt gốc.pptx'
    source.write_bytes(b'fixture')
    with closing(Library(tmp_path/'library')) as library:
        lesson = library.create('Tên đã sửa', 'Vật lý', 'THPT', '11', [('Mở đầu', 'Năng lượng')])
        lesson['narration'] = {'mode': 'both'}
        remember_source(library, source, 'source')
        bind_lesson(library, lesson, 'source')
        bridge = SimpleNamespace(
            library=library, _lesson=lesson, selectedNarrationVariant='ready', lessonNarration={'ready': True},
            downloadsDirectory=QUrl.fromLocalFile(str(downloads)).toString(),
            _catalog=SimpleNamespace(rows=lambda: [{'id': lesson['id'], 'narration': {
                'variants': [{'mode': 'both', 'ready': True}]}}]),
        )
        for url in (Bridge.presentationDownloadSuggestion(bridge, False),
                    Bridge.presentationDownloadSuggestion(bridge, True),
                    Bridge.libraryDownloadSuggestion(bridge, [lesson['id']], True),
                    Bridge.exportSuggestion(bridge, 'pptx')):
            path = Path(QUrl(url).toLocalFile())
            assert path.parent == source_dir and path.name.startswith('Bài Việt gốc (Song ngu VI-EN')
            assert path != source
        bulk = Bridge.libraryDownloadSuggestion(bridge, ['one', 'two'], True)
        assert Path(QUrl(bulk).toLocalFile()).parent == downloads


def test_google_job_remembers_uploaded_origin_and_conversion_binding(tmp_path):
    from app.conversion_input import creation_config
    from app.google_conversion import prepare

    source = tmp_path/'Bài gốc.txt'
    source.write_text('Năng lượng được bảo toàn.', encoding='utf-8')
    data = tmp_path/'library'
    config = creation_config('Tên mới', 'Vật lý', 'THPT', '11', 'parallel_columns', 'standard', 'template')
    job = prepare(data, config, source)
    with closing(Library(data)) as library:
        lesson = library.create('Tên mới', 'Vật lý', 'THPT', '11', [('Mở đầu', 'Năng lượng')])
        bind_lesson(library, lesson, job['config']['source_sha256'])
        assert destination(library, lesson, data) == (tmp_path, 'Bài gốc')
