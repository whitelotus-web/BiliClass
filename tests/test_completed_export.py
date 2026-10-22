import copy
from pathlib import Path
from zipfile import ZipFile

import pytest
from test_presentation_audio import fixture

from app.chatgpt_handoff import external_preview
from app.completed_export import save_finished
from app.export_origin import bind_lesson, remember_source
from app.lesson_files import save_presentation


def prepared(tmp_path):
    library, lesson, source = fixture(tmp_path)
    remember_source(library, source, lesson['source']['sha256'])
    bind_lesson(library, lesson, lesson['source']['sha256'])
    return library, lesson, source, external_preview(lesson, library.directory)


def test_finished_voice_automatically_creates_standalone_pptx_next_to_source_without_changing_library_or_wavs(tmp_path, monkeypatch):
    library, lesson, source, preview = prepared(tmp_path)
    source_bytes = source.read_bytes()
    wavs = {p.name: p.read_bytes() for p in (library.directory/'audio').glob('*.wav')}
    monkeypatch.setattr('app.speech.synthesize', lambda *_: pytest.fail('Export reuses existing WAVs'))
    try:
        result = save_finished(library.directory, lesson, preview)
        target = Path(result['path'])
        assert target.parent == source.parent and target != source
        assert 'Voice VI-EN' in target.name and not result['fallback']
        with ZipFile(target) as archive:
            assert sum(name.endswith('.wav') for name in archive.namelist()) == 2
        assert source.read_bytes() == source_bytes and library.get(lesson['id']) == lesson
        assert wavs == {p.name: p.read_bytes() for p in (library.directory/'audio').glob('*.wav')}
        repeated = save_finished(library.directory, lesson, preview)
        assert repeated['reused'] and repeated['path'] == result['path']
    finally:
        library.close()


def test_teacher_edit_of_autosaved_file_is_kept_and_a_new_name_is_used(tmp_path):
    library, lesson, _, preview = prepared(tmp_path)
    try:
        first = Path(save_finished(library.directory, lesson, preview)['path'])
        first.write_bytes(b'teacher edited this file')
        second = Path(save_finished(library.directory, lesson, preview)['path'])
        assert first != second and second.is_file()
        assert first.read_bytes() == b'teacher edited this file'
    finally:
        library.close()


def test_old_pause_policy_is_reexported_without_regenerating_or_overwriting_audio(tmp_path, monkeypatch):
    library, lesson, source, preview = prepared(tmp_path)
    wavs = {p.name: p.read_bytes() for p in (library.directory/'audio').glob('*.wav')}
    try:
        with monkeypatch.context() as patch:
            patch.setattr('app.completed_export.PARAGRAPH_GAP_MS', 450)
            old = save_finished(library.directory, lesson, preview)
        previous = Path(old['path']).read_bytes()
        fresh = save_finished(library.directory, lesson, preview)
        assert fresh['path'] != old['path'] and not fresh['reused']
        assert fresh['join_gap_ms'] == 1100 and Path(old['path']).read_bytes() == previous
        assert wavs == {p.name: p.read_bytes() for p in (library.directory/'audio').glob('*.wav')}
        assert save_finished(library.directory, lesson, preview)['reused']
    finally:
        library.close()


def test_new_audio_with_same_text_keys_invalidates_autosave_reuse(tmp_path):
    library, lesson, _, preview = prepared(tmp_path)
    try:
        first = save_finished(library.directory, lesson, preview)
        wav = next((library.directory/'audio').glob('*.wav'))
        data = bytearray(wav.read_bytes())
        data[-2:] = b'\1\0'
        wav.write_bytes(data)
        second = save_finished(library.directory, lesson, preview)
        assert not second['reused'] and first['path'] != second['path']
        assert first['audio_sha256'] != second['audio_sha256']
    finally:
        library.close()


def test_denied_source_folder_falls_back_to_managed_exports_and_download_guard_stays_in_force(tmp_path, monkeypatch):
    library, lesson, source, preview = prepared(tmp_path)
    original = save_presentation

    def permission_checked(*args, **kwargs):
        if Path(args[3]).parent == source.parent:
            raise PermissionError('Fixture source folder is read only')
        return original(*args, **kwargs)

    monkeypatch.setattr('app.completed_export.save_presentation', permission_checked)
    try:
        result = save_finished(library.directory, lesson, preview)
        assert result['fallback'] and Path(result['path']).parent == library.directory/'exports'
        assert Path(result['path']).is_file()
        with pytest.raises(ValueError, match='ngoài dữ liệu'):
            save_presentation(lesson, preview, library.directory, library.directory/'exports/manual.pptx')
    finally:
        library.close()


def test_incomplete_edited_or_deleted_product_is_not_exported(tmp_path):
    library, lesson, _, preview = prepared(tmp_path)
    try:
        stale = copy.deepcopy(lesson)
        stale['revision'] -= 1
        with pytest.raises(ValueError, match='thay đổi'):
            save_finished(library.directory, stale, preview)
        next((library.directory/'audio').glob('*.wav')).unlink()
        with pytest.raises(ValueError, match='chưa đủ'):
            save_finished(library.directory, lesson, preview)
        library.trash_lesson(lesson['id'])
        with pytest.raises(ValueError):
            save_finished(library.directory, lesson, preview)
        assert not (library.directory/'exports').exists()
    finally:
        library.close()


def test_exclusive_publish_cannot_replace_a_file_created_after_name_selection(tmp_path):
    library, lesson, _, preview = prepared(tmp_path)
    target = tmp_path/'chosen.pptx'
    target.write_bytes(b'existing teacher file')
    try:
        with pytest.raises(FileExistsError):
            save_presentation(lesson, preview, library.directory, target, overwrite=False)
        assert target.read_bytes() == b'existing teacher file'
        assert not list(tmp_path.glob('.biliclass-*.pptx'))
    finally:
        library.close()
