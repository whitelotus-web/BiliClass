import json

import pytest

from app import library_location as location
from app.library import Library
from app.paths import user_data


def fixture_library(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'control'))
    monkeypatch.delenv('BILICLASS_DATA', raising=False)
    source = location.default_root()
    library = Library(source)
    lesson = library.create('Dao động', 'Vật lý', 'THPT', '11', [('Slide 1', 'Vận tốc thay đổi.')])
    library.set_setting('chatgpt_request_folder', str(source / 'chatgpt' / 'request'))
    (source / 'audio').mkdir()
    (source / 'audio/voice.wav').write_bytes(b'WAV fixture')
    (source / 'temp').mkdir()
    (source / 'temp/job.json').write_text(json.dumps({'path': str(source / 'audio/voice.wav')}), encoding='utf-8')
    (source / 'dev-runtime').mkdir()
    (source / 'dev-runtime/helper.txt').write_text('machine runtime')
    (tmp_path / 'other-drive').mkdir()
    return library, lesson, tmp_path / 'other-drive/BiliClass-Data'


def test_transfer_verifies_preserves_source_then_restarts_and_cleans_exact_files(tmp_path, monkeypatch):
    library, lesson, target = fixture_library(tmp_path, monkeypatch)
    source = library.directory
    record = location.transfer(source, target)
    assert (source / 'audio/voice.wav').read_bytes() == (target / 'audio/voice.wav').read_bytes()
    assert user_data() == source.resolve(), 'Copy alone must not switch active data'
    # Last changes while the old UI shuts down must be included.
    library.set_setting('teacher', 'Thầy cô')
    library.close()
    location.finalize_transfer(record)
    assert user_data() == target.resolve()
    location.verify_transfer_start(target)
    replacement = Library(target)
    assert replacement.get(lesson['id'])['title'] == 'Dao động'
    assert replacement.setting('teacher', '') == 'Thầy cô'
    assert replacement.setting('chatgpt_request_folder', '') == str(target / 'chatgpt/request')
    replacement.close()
    assert json.loads((target / 'temp/job.json').read_text(encoding='utf-8'))['path'] == str(target / 'audio/voice.wav')
    assert not (target / 'dev-runtime').exists()
    assert location.cleanup_previous(target) > 0
    assert not (source / 'audio/voice.wav').exists()
    assert (source / 'dev-runtime/helper.txt').is_file()
    assert (source / location.CONTROL_FILE).is_file()
    assert location.cleanup_previous(target) == 0


def test_destination_failure_does_not_change_or_delete_source(tmp_path, monkeypatch):
    library, _, target = fixture_library(tmp_path, monkeypatch)
    library.close()
    target.mkdir()
    (target / 'keep.txt').write_text('keep')
    with pytest.raises(ValueError):
        location.transfer(library.directory, target)
    assert (target / 'keep.txt').read_text() == 'keep'
    assert (library.directory / 'library.db').is_file()
    with pytest.raises(ValueError):
        location.transfer(library.directory, library.directory / 'nested')


def test_partial_copy_failure_keeps_source_and_never_publishes_target(tmp_path, monkeypatch):
    library, _, target = fixture_library(tmp_path, monkeypatch)
    library.close()
    monkeypatch.setattr(location, 'copy_file', lambda *args: (_ for _ in ()).throw(OSError('disk full')))
    with pytest.raises(OSError):
        location.transfer(library.directory, target)
    assert not target.exists()
    assert not list(target.parent.glob('.biliclass-transfer-*'))
    assert (library.directory / 'audio/voice.wav').exists()


def test_corrupt_destination_fails_before_source_cleanup(tmp_path, monkeypatch):
    library, _, target = fixture_library(tmp_path, monkeypatch)
    record = location.transfer(library.directory, target)
    library.close()
    location.finalize_transfer(record)
    (target / 'audio/voice.wav').write_bytes(b'bad')
    with pytest.raises(ValueError):
        location.verify_transfer_start(target)
    assert (library.directory / 'audio/voice.wav').exists()


def test_missing_selected_drive_never_silently_opens_empty_default(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    root = location.default_root()
    root.mkdir()
    (root / location.CONTROL_FILE).write_text(json.dumps({'directory': str(tmp_path / 'unplugged')}))
    with pytest.raises(ValueError, match='Không tìm thấy'):
        user_data()
    monkeypatch.setenv('BILICLASS_DATA', str(tmp_path / 'isolated'))
    assert user_data() == (tmp_path / 'isolated').resolve()


def test_cleanup_keeps_old_files_changed_by_another_process(tmp_path, monkeypatch):
    library, _, target = fixture_library(tmp_path, monkeypatch)
    record = location.transfer(library.directory, target)
    library.close()
    location.finalize_transfer(record)
    location.verify_transfer_start(target)
    (library.directory / 'audio/voice.wav').write_bytes(b'changed elsewhere')
    location.cleanup_previous(target)
    assert (library.directory / 'audio/voice.wav').read_bytes() == b'changed elsewhere'


def test_safe_download_names_and_existing_files(tmp_path):
    from app.download_names import suggestion

    path = suggestion(tmp_path, 'CON', 'Anh/Việt', 'pptx')
    assert path.name == '_CON - Anh_Việt.pptx'
    path.touch()
    assert suggestion(tmp_path, 'CON', 'Anh/Việt', 'pptx').name.endswith('(2).pptx')


def test_finalize_reuses_verified_file_hashes_and_reports_progress(tmp_path, monkeypatch):
    library, _, target = fixture_library(tmp_path, monkeypatch)
    record = location.transfer(library.directory, target)
    library.close()
    calls, progress = [], []
    original_digest = location.digest

    def tracked(path):
        calls.append(path)
        return original_digest(path)

    monkeypatch.setattr(location, 'digest', tracked)
    location.finalize_transfer(record, lambda done, total: progress.append((done, total)))
    # Unchanged large WAV/model files are read only once on each drive.
    assert calls.count(library.directory / 'audio/voice.wav') == 1
    assert calls.count(target / 'audio/voice.wav') == 1
    assert progress[-1] == (len(record['files']), len(record['files']))
    location.verify_transfer_start(target)
