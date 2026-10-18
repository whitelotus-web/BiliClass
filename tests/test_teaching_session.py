import copy
import wave
from types import SimpleNamespace

import pytest
from pptx import Presentation
from PySide6.QtCore import QObject, Signal

from app import speech
from app.lesson_narration import make_plan, variant_id
from app.library import Library
from app.teaching_session import TeachingSession, prepare_teaching
from app.voice_import import import_presentation, save_script


def prepared_lesson(tmp_path, mode='both'):
    from app.chatgpt_handoff import external_preview

    path = tmp_path / 'Independent.pptx'
    deck = Presentation()
    for _ in range(3):
        deck.slides.add_slide(deck.slide_layouts[6])
    deck.save(path)
    directory = tmp_path / 'library'
    lesson, preview = import_presentation(directory, path)
    library = Library(directory)
    for index, (vi, en) in enumerate([('Xin chào.', 'Hello.'), ('', ''), ('Tạm biệt.', '')]):
        lesson = save_script(library, lesson['id'], lesson['segments'][index]['id'], lesson['revision'], vi, en)
    plan, _ = make_plan(lesson, mode, {'voice': 'vieneu:Mai Anh', 'rate': 0}, playback='both_controls')
    for keys in plan['keys'].values():
        for key in keys:
            target = directory / 'audio' / (key + '.wav')
            target.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(target), 'wb') as audio:
                audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                audio.writeframes(b'\0\0' * 24000)
    plan.update(lesson_id=lesson['id'], revision=lesson['revision'], complete=plan['total'], running=False)
    lesson = library.update_narration(lesson['id'], plan)
    lesson = library.select_narration_variant(lesson['id'], variant_id(plan))
    library.close()
    return lesson, external_preview(lesson, directory), directory, path


def test_ready_voice_opens_powerpoint_without_approving_or_blocking_on_layout_warning(tmp_path, monkeypatch):
    import time

    from PySide6.QtCore import QCoreApplication

    from app.ui import Bridge

    app = QCoreApplication.instance() or QCoreApplication([])
    lesson, preview, directory, source = prepared_lesson(tmp_path)
    lesson['voice_only'] = False
    lesson['slide_quality'] = {'counts': {'FAIL': 1, 'CHECK': 2}, 'slides': []}
    library = Library(directory)
    library._write(lesson)
    original, opened = source.read_bytes(), []
    bridge = Bridge(library)
    bridge._lesson, bridge._quick_result = lesson, preview
    monkeypatch.setattr(bridge, '_activate_teaching', opened.append)
    monkeypatch.setattr(speech, 'synthesize', lambda *a, **k: pytest.fail('Opening must reuse existing WAVs'))
    try:
        bridge.openNarratedPowerPoint(variant_id(lesson['narration']))
        deadline = time.monotonic() + 8
        while bridge.busy and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        assert not bridge.busy and len(opened) == 1, bridge.message
        assert set(opened[0]['media'][1]) == {'vi', 'en', 'both'}
        saved = library.get(lesson['id'])
        assert saved['revision'] == lesson['revision']
        assert not any(row['approved'] for row in saved['segments'])
        assert saved['slide_quality']['counts']['FAIL'] == 1
        assert source.read_bytes() == original
    finally:
        for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                       bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader):
            worker.shutdown()
        library.close()


def test_completed_preview_uses_the_saved_voice_without_synthesis(tmp_path, monkeypatch):
    from PySide6.QtCore import QCoreApplication

    from app.ui import Bridge

    app = QCoreApplication.instance() or QCoreApplication([])
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    library = Library(directory)
    bridge = Bridge(library)
    bridge._lesson, bridge._quick_result = lesson, preview
    calls = []
    monkeypatch.setattr(bridge.english_reader, 'start', lambda *a, **k: calls.append((a, k)))
    try:
        bridge.narrationWorkspace.listenCreated(1, 'en', variant_id(lesson['narration']))
        assert calls == [((['Hello.'], lesson['narration']['voice'], 0), {'cache_only': True})]
        bridge.narrationWorkspace.listenCreated(2, 'en', variant_id(lesson['narration']))
        assert len(calls) == 1 and 'không có lời' in bridge.message
        lesson['segments'][0]['en'] = 'Changed since generation.'
        bridge.narrationWorkspace.listenCreated(1, 'en', variant_id(lesson['narration']))
        assert len(calls) == 1 and bridge.error
        app.processEvents()
    finally:
        for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                       bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader):
            worker.shutdown()
        library.close()


class FakeBridge(QObject):
    changed = Signal()
    speechStateChanged = Signal()

    def __init__(self, directory):
        super().__init__()
        self.library = SimpleNamespace(directory=directory)
        self._powerpoint_state = {'active': True, 'slide': 1}
        self.calls = []
        self.powerpoint_worker = SimpleNamespace(navigate=lambda *args: self.calls.append(args))
        self.english_reader = SimpleNamespace(start=lambda *args, **kwargs: self.calls.append((args, kwargs)))

    def stopSpeech(self):
        self.calls.append('stop')

    def inform(self, *args, **kwargs):
        self.calls.append(('message', args))


def test_bound_snapshot_follows_slide_not_browsed_lesson(tmp_path, monkeypatch):
    lesson, preview, directory, source = prepared_lesson(tmp_path)
    original = source.read_bytes()
    monkeypatch.setattr(speech, 'synthesize', lambda *_: (_ for _ in ()).throw(AssertionError('No synthesis')))
    prepared = prepare_teaching(lesson, preview, directory)
    bridge = FakeBridge(directory)
    session = TeachingSession(bridge)
    session.bind(prepared)
    assert session.audio == {'vi': True, 'en': True, 'both': True}
    bridge._lesson = {'id': 'another-lesson', 'segments': []}
    lesson['segments'][0]['vi'] = 'Changed after binding'
    assert session.texts('vi') == ['Xin chào.']
    assert session.state['lesson_id'] == prepared['lesson']['id']
    bridge._powerpoint_state['slide'] = 2
    assert session.audio == {'vi': False, 'en': False, 'both': False}
    bridge._powerpoint_state['slide'] = 3
    assert session.audio == {'vi': True, 'en': False, 'both': False}
    assert source.read_bytes() == original
    import zipfile

    with zipfile.ZipFile(prepared['path']) as archive:
        assert any(name.startswith('ppt/media/') and name.endswith('.wav') for name in archive.namelist())


def test_cached_fallback_waits_for_powerpoint_stop_and_rejects_late_slide(tmp_path, monkeypatch):
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    from app import presentation_audio

    monkeypatch.setattr(presentation_audio, 'embed_audio', lambda *_: (_ for _ in ()).throw(ValueError('No room')))
    prepared = prepare_teaching(lesson, preview, directory)
    assert prepared['warning'] and not any(prepared['media'].values())
    bridge = FakeBridge(directory)
    session = TeachingSession(bridge)
    session.bind(prepared)
    session.read('vi')
    token = session.token
    assert bridge.calls[-1] == ('stop_media', token)
    bridge._powerpoint_state['slide'] = 2
    session.event({'event': 'media_stopped', 'token': token})
    assert not any(isinstance(call, tuple) and isinstance(call[-1], dict) for call in bridge.calls)
    bridge._powerpoint_state['slide'] = 1
    session.read('vi')
    session.event({'event': 'media_stopped', 'token': session.token})
    assert bridge.calls[-1][1] == {'cache_only': True}
    session.read('vi')
    token = session.token
    session.stop()
    calls = len(bridge.calls)
    session.event({'event': 'media_stopped', 'token': token})
    assert len(bridge.calls) == calls, 'A stop must invalidate a queued read acknowledgement'
    changed = copy.deepcopy(prepared)
    changed['sha256'] = 'changed'
    session.bind(changed)
    session.read('vi')
    assert bridge.calls[-1][0] == 'message'


def test_explicit_no_voice_and_independent_embedded_powerpoint_are_teachable(tmp_path):
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    with_voice = prepare_teaching(lesson, preview, directory)
    lesson['narration'] = {'version': 2, 'mode': 'none'}
    without = prepare_teaching(lesson, preview, directory)
    assert without['path'] == preview['path'] and not any(without['media'].values())
    imported, preview = import_presentation(directory, with_voice['path'])
    assert imported['narration']['mode'] == 'none'
    independent = prepare_teaching(imported, preview, directory)
    bridge = FakeBridge(directory)
    session = TeachingSession(bridge)
    session.bind(independent)
    assert session.audio == {'vi': True, 'en': True, 'both': True}


def test_key_and_mouse_toggle_pause_resume_switch_and_missing_language(tmp_path):
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    bridge = FakeBridge(directory)
    session = TeachingSession(bridge)
    session.bind(prepare_teaching(lesson, preview, directory))
    bridge._powerpoint_state['slide_id'] = 256
    session.event({'event': 'read_requested', 'slide_id': 256, 'language': 'en'})
    assert bridge.calls[-1] == ('play_media', 'en')
    session.event({'event': 'media_started', 'language': 'en'})
    session.toggleRead('en')
    assert bridge.calls[-1] == ('pause_media',)
    session.event({'event': 'media_paused'})
    session.toggleRead('en')
    assert bridge.calls[-1] == ('resume_media',)
    session.event({'event': 'media_resumed'})
    session.toggleRead('vi')
    assert bridge.calls[-1] == ('play_media', 'vi')
    assert session.language == 'vi'
    before = list(bridge.calls)
    session.event({'event': 'read_requested', 'slide_id': 999, 'language': 'en'})
    assert bridge.calls == before, 'Drop key-downs belonging to a previous slide'
    bridge._powerpoint_state['slide'] = 3
    session.toggleRead('en')
    assert bridge.calls[-1][0] == 'message'
    assert not any(call == ('play_media', 'en') for call in bridge.calls[len(before):])


def test_repeated_press_while_native_player_prepares_queues_pause_without_restarting(tmp_path):
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    bridge = FakeBridge(directory)
    session = TeachingSession(bridge)
    session.bind(prepare_teaching(lesson, preview, directory))
    session.toggleRead('en')
    assert session.native_state == 'preparing'
    before = list(bridge.calls)
    session.toggleRead('en')
    assert bridge.calls == before
    session.event({'event': 'media_started', 'language': 'en'})
    assert bridge.calls[-1] == ('pause_media',)
    assert bridge.calls.count(('play_media', 'en')) == 1


def test_build_aware_reading_bypasses_whole_slide_media_and_only_uses_visible_cached_words(tmp_path):
    import time

    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    prepared = prepare_teaching(lesson, preview, directory)
    page = prepared['speech']['slides'][0]
    for row in page['englishSpeechSegments']:
        row['visibility'] = {'kind': 'click', 'show_after': 1, 'hide_after': None, 'settle_seconds': 0}
    bridge = FakeBridge(directory)
    bridge._powerpoint_state.update(click_index=0, build_started=time.monotonic() - 2)
    session = TeachingSession(bridge)
    session.bind(prepared)
    assert session.audio['en'], 'Whole-slide playback includes the saved script behind builds'
    session.setReadingScope('visible')
    assert not session.audio['en']
    bridge._powerpoint_state['click_index'] = 1
    assert session.audio['en']
    session.read('en')
    assert bridge.calls[-1] == ('stop_media', session.token), 'Wait for native stop before cached playback'
    session.event({'event': 'media_stopped', 'token': session.token})
    assert bridge.calls[-1][1] == {'cache_only': True}
