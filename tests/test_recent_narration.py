import pytest
from PySide6.QtCore import QCoreApplication
from test_teaching_session import prepared_lesson

from app import speech
from app.library import Library
from app.ui import Bridge


def test_completed_voice_link_survives_clearing_selection_and_opens_exact_variant(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    lesson, _, directory, original = prepared_lesson(tmp_path)
    source_bytes = original.read_bytes()
    library = Library(directory)
    bridge = Bridge(library)
    pages, requests = [], []
    bridge.navigate.connect(pages.append)
    bridge.narrationResultRequested.connect(lambda: requests.append(True))
    monkeypatch.setattr(speech, 'synthesize', lambda *_: pytest.fail('Reopening a result must not synthesize'))
    try:
        assert not bridge.recentNarrationResult
        bridge._lesson = lesson
        bridge.narration_preparation.state = dict(lesson['narration'])
        bridge._narration_updated()
        recent = dict(bridge.recentNarrationResult)
        assert recent['lesson_id'] == lesson['id'] and recent['variant_id']
        bridge._lesson = {}
        monkeypatch.setattr(bridge, 'launch', lambda action, callback, **_: callback(action()))
        bridge.openRecentNarrationResult()
        assert pages == ['voice'] and requests == [True]
        assert bridge.selectedNarrationVariant == recent['variant_id']
        assert bridge.lesson['id'] == lesson['id'] and original.read_bytes() == source_bytes
        # A subsequent cancelled attempt must retain the last successful result.
        bridge.narration_preparation.state = dict(running=False, cancelled=True, total=10, complete=2)
        bridge._narration_updated()
        assert bridge.recentNarrationResult == recent
        wav_key = lesson['narration']['keys']['vi'][0]
        (directory/'audio'/(wav_key+'.wav')).unlink()
        actions = []
        monkeypatch.setattr(bridge, 'launch', lambda action, callback, **_: actions.append(action))
        bridge.openRecentNarrationResult()
        with pytest.raises(ValueError, match='thiếu âm thanh|thay đổi'):
            actions[0]()
        assert pages == ['voice'] and requests == [True]
    finally:
        for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                       bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                       bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
            worker.shutdown()
        app.processEvents()
        library.close()
