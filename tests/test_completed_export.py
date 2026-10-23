import copy
from pathlib import Path
from zipfile import ZipFile

import pytest
from test_presentation_audio import fixture

from app.chatgpt_handoff import external_preview
from app.completed_export import save_converted, save_finished
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
        assert 'Song ngữ VI-EN' in target.name and 'Voice' not in target.name and not result['fallback']
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


def test_old_pause_policy_is_reexported_without_regenerating_or_overwriting_audio(tmp_path):
    library, lesson, source, preview = prepared(tmp_path)
    wavs = {p.name: p.read_bytes() for p in (library.directory/'audio').glob('*.wav')}
    try:
        library.set_setting('paragraph_gap_ms', 1100)
        old = save_finished(library.directory, lesson, preview)
        library.set_setting('paragraph_gap_ms', 400)
        fresh = save_finished(library.directory, lesson, preview)
        assert fresh['path'] == old['path'] and not fresh['reused'] and fresh['updated']
        assert fresh['join_gap_ms'] == 400 and Path(old['path']).is_file()
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
        assert not second['reused'] and first['path'] == second['path'] and second['updated']
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


def test_conversion_then_voice_updates_one_owned_product_beside_unchanged_original(tmp_path):
    library, lesson, source, preview = prepared(tmp_path)
    original = source.read_bytes()
    try:
        converted = save_converted(library.directory, lesson, preview)
        target = Path(converted['path'])
        with ZipFile(target) as archive:
            assert not any(name.endswith('.wav') for name in archive.namelist())
        voiced = save_finished(library.directory, lesson, preview)
        assert voiced['path'] == converted['path'] and voiced['updated']
        assert len(list(source.parent.glob('*.pptx'))) == 2
        with ZipFile(target) as archive:
            assert sum(name.endswith('.wav') for name in archive.namelist()) == 2
        assert source.read_bytes() == original
        assert save_finished(library.directory, lesson, preview)['reused']
        retried_conversion = save_converted(library.directory, lesson, preview)
        assert retried_conversion['path'] == voiced['path'] and retried_conversion['kept_voiced_product']
        assert len(list(source.parent.glob('*.pptx'))) == 2
    finally:
        library.close()


@pytest.mark.parametrize('changed', ['edited', 'open'])
def test_converted_product_edited_or_open_in_powerpoint_gets_a_separate_voice_file(tmp_path, changed):
    library, lesson, source, preview = prepared(tmp_path)
    original = source.read_bytes()
    try:
        target = Path(save_converted(library.directory, lesson, preview)['path'])
        if changed == 'edited':
            target.write_bytes(b'teacher edit')
        else:
            target.with_name('~$' + target.name).write_bytes(b'Office owner file')
        before = target.read_bytes()
        voice = save_finished(library.directory, lesson, preview)
        assert Path(voice['path']) != target and not voice['updated'] and voice['previous_kept']
        assert target.read_bytes() == before and source.read_bytes() == original
    finally:
        library.close()


def test_teacher_edit_during_embedding_is_detected_before_replacing_the_product(tmp_path, monkeypatch):
    from app import presentation_audio

    library, lesson, _, preview = prepared(tmp_path)
    target = Path(save_converted(library.directory, lesson, preview)['path'])
    embed, changed = presentation_audio.embed_audio, False

    def edit_while_embedding(*args, **kwargs):
        nonlocal changed
        if not changed:
            target.write_bytes(b'edited while tool was generating voice')
            changed = True
        return embed(*args, **kwargs)

    monkeypatch.setattr(presentation_audio, 'embed_audio', edit_while_embedding)
    try:
        result = save_finished(library.directory, lesson, preview)
        assert result['path'] != str(target) and result['previous_kept']
        assert target.read_bytes() == b'edited while tool was generating voice'
        assert not list(target.parent.glob('.biliclass-*.pptx'))
    finally:
        library.close()


def test_failed_voice_embedding_keeps_converted_product_and_its_saved_shortcut(tmp_path, monkeypatch):
    library, lesson, _, preview = prepared(tmp_path)
    converted = save_converted(library.directory, lesson, preview)
    target = Path(converted['path'])
    before = target.read_bytes()

    def failed(*args, **kwargs):
        raise ValueError('Fixture embedding failed')

    monkeypatch.setattr('app.presentation_audio.embed_audio', failed)
    try:
        with pytest.raises(ValueError, match='embedding'):
            save_finished(library.directory, lesson, preview)
        assert target.read_bytes() == before
        assert save_converted(library.directory, lesson, preview)['path'] == converted['path']
        assert not list(target.parent.glob('.biliclass-*.pptx'))
    finally:
        library.close()


def test_importing_owned_converted_file_for_voice_keeps_original_origin_including_batch(tmp_path):
    from app.batch_jobs import bind_origin
    from app.export_origin import destination
    from app.voice_import import import_presentation

    library, lesson, source, preview = prepared(tmp_path)
    try:
        converted = save_converted(library.directory, lesson, preview)
        product = Path(converted['path'])
        reopened, _ = import_presentation(library.directory, product)
        assert reopened['id'] == lesson['id']
        assert destination(library, reopened, tmp_path) == (source.parent, source.stem)
        bind_origin(library.directory, {'url': product.as_uri()}, reopened)
        assert destination(library, reopened, tmp_path) == (source.parent, source.stem)
    finally:
        library.close()
