import copy
from threading import Event

import pytest
from test_lesson_completion import converted

from app.library import RevisionConflict
from app.voice_import import refresh_native_speech


def test_upgrade_is_once_only_and_keeps_manual_script_and_source(tmp_path, monkeypatch):
    library, lesson, path = converted(tmp_path)
    lesson['source_slide_speech'] = copy.deepcopy(lesson['slide_speech'])
    lesson['source_slide_speech'].pop('extraction_version', None)
    identity = lesson['segments'][0]['id']
    lesson['narration_script'] = {identity: {'vi': 'Lời riêng.', 'en': 'My own script 4.', 'manual': True}}
    library._write(lesson)
    original = path.read_bytes()
    updated = refresh_native_speech(library, lesson)
    assert updated['source_slide_speech']['extraction_version'] == 2
    assert updated['narration_script'][identity]['manual']
    assert updated['slide_speech']['slides'][0]['englishSpeechSegments'][0]['english_text'] == 'My own script 4.'
    assert updated['revision'] == lesson['revision'] and path.read_bytes() == original
    monkeypatch.setattr('pptx.Presentation', lambda *_: pytest.fail('Current extraction must be reused'))
    assert refresh_native_speech(library, updated) == updated
    library.close()


def test_cancelled_upgrade_does_not_publish_metadata(tmp_path):
    library, lesson, _ = converted(tmp_path)
    lesson['slide_speech'].pop('extraction_version', None)
    lesson.get('source_slide_speech', {}).pop('extraction_version', None)
    library._write(lesson)
    before = copy.deepcopy(lesson)
    cancel = Event()
    cancel.set()
    with pytest.raises(InterruptedError):
        refresh_native_speech(library, lesson, cancel)
    assert library.get(lesson['id']) == before
    library.close()


def test_upgrade_does_not_overwrite_concurrent_rename(tmp_path, monkeypatch):
    from app.slide_speech import deck_speech

    library, lesson, _ = converted(tmp_path)
    lesson['slide_speech'].pop('extraction_version', None)
    lesson.get('source_slide_speech', {}).pop('extraction_version', None)
    library._write(lesson)

    def inspect(*args):
        saved = library.get(lesson['id'])
        saved['title'] = 'Renamed during extraction'
        library._write(saved)
        return deck_speech(*args)

    monkeypatch.setattr('app.slide_speech.deck_speech', inspect)
    with pytest.raises(RevisionConflict):
        refresh_native_speech(library, lesson)
    assert library.get(lesson['id'])['title'] == 'Renamed during extraction'
    library.close()
