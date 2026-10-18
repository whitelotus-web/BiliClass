import pytest

from app.library import Library
from app.powerpoint import slide_for_locator, slide_segment_indexes, verified_presentation


def test_slide_locator_survives_split():
    assert slide_for_locator("Slide 12 · phần 2") == 12
    assert slide_for_locator("Trang 12") is None
    assert slide_for_locator("Slide 3") == 3


@pytest.mark.parametrize('playing,audible,paused,previous,event', [
    ({1}, set(), {1}, set(), 'media_paused'),
    ({1}, {1}, set(), {1}, 'media_resumed'),
    ({1}, set(), {1}, {1}, ''),
    ({1}, {1}, set(), set(), ''),
    ({2}, {2}, set(), {1}, ''),
    ({1}, set(), set(), set(), ''),
])
def test_native_slide_pause_and_resume_update_the_same_mascot_player(playing, audible, paused, previous, event):
    from app.powerpoint import _native_pause_event

    assert _native_pause_event(playing, audible, paused, previous) == event


def test_displayed_slide_resolves_all_source_sections_and_reordered_output():
    lesson = {"segments": [
        {"id": "a", "locator": "Slide 1 · ý 1"},
        {"id": "b", "locator": "Slide 1 · ý 2"},
        {"id": "c", "locator": "Slide 2"},
    ]}
    assert slide_segment_indexes(lesson, 1) == [0, 1]
    assert slide_segment_indexes(lesson, 1, [2, 1, 1]) == [2]
    assert slide_segment_indexes(lesson, 3, [2, 1, 1]) == [0, 1]
    assert slide_segment_indexes(lesson, 4, [2, 1, 1]) == []


def test_blank_external_slide_must_never_fall_back_to_another_slide():
    lesson = {"segments": [{"id": "a", "locator": "Slide 2"}]}
    assert slide_segment_indexes(lesson, 1, segment_map=["a", "", "a"]) == [0]
    assert slide_segment_indexes(lesson, 2, segment_map=["a", "", "a"]) == []
    assert slide_segment_indexes(lesson, 4, segment_map=["a", "", "a"]) == []
    assert slide_segment_indexes(lesson, 0) == []


def test_companion_rejects_changed_missing_or_non_pptx_source(tmp_path):
    library = Library(tmp_path / "library")
    path = tmp_path / "Thử.pptx"
    path.write_bytes(b"mock deck")
    source = library.store_source(path)
    saved = verified_presentation({"source": source}, library.directory)
    assert saved.read_bytes() == b"mock deck"
    saved.write_bytes(b"changed")
    with pytest.raises(ValueError, match="thay đổi"):
        verified_presentation({"source": source}, library.directory)
    with pytest.raises(ValueError, match="không có"):
        verified_presentation({"source": None}, library.directory)
    library.close()


def test_window_binding_requires_exact_filename_and_rejects_ambiguity(monkeypatch):
    import win32gui

    from app.powerpoint import presenter_handle, slideshow_handle

    windows = {1: ('screenClass', 'PowerPoint Slide Show - [Lesson extra.pptx]'),
               2: ('PodiumParent', 'Lesson extra.pptx - PowerPoint Presenter View')}
    monkeypatch.setattr(win32gui, 'EnumWindows', lambda collect, context: [collect(h, context) for h in windows])
    monkeypatch.setattr(win32gui, 'IsWindowVisible', lambda _: True)
    monkeypatch.setattr(win32gui, 'GetClassName', lambda h: windows[h][0])
    monkeypatch.setattr(win32gui, 'GetWindowText', lambda h: windows[h][1])
    path = 'Lesson.pptx'
    assert slideshow_handle(path) == presenter_handle(path) == 0
    windows[3] = ('screenClass', 'PowerPoint Slide Show - [Lesson.pptx [Read-Only]]')
    windows[4] = ('PodiumParent', 'Lesson.pptx [Read-Only] - PowerPoint Presenter View')
    assert slideshow_handle(path) == 3 and presenter_handle(path) == 4
    windows[5] = windows[3]
    assert slideshow_handle(path) == 0, 'Same-named decks must not bind arbitrarily'


@pytest.mark.parametrize('operation', ['play_media', 'pause_media', 'resume_media', 'stop_media'])
def test_delayed_media_commands_do_not_touch_players_of_a_different_slide(operation):
    from app.powerpoint import _control_media

    class Player:
        def __getattr__(self, name):
            pytest.fail('A stale request touched the new slide: ' + name)
    event, playing = _control_media(operation, {'slide_id': 256, 'token': 7, 'language': 'en'},
                                    257, {1: Player()}, {1: 'en'}, {1})
    assert event['event'] == 'media_rejected' and event['token'] == 7 and playing == {1}


@pytest.mark.parametrize('missing', [True, False])
def test_unavailable_native_player_reports_a_failure_instead_of_leaving_preparing(missing):
    from app.powerpoint import _control_media

    class Player:
        def Stop(self):
            pass

        def Play(self):
            raise RuntimeError('PowerPoint media unavailable')
    event, playing = _control_media('play_media', {'slide_id': 256, 'token': 8, 'language': 'en'},
                                    256, {} if missing else {1: Player()}, {1: 'en'}, set())
    assert event['event'] == 'media_error' and event['operation'] == 'play_media'
    assert event['slide_id'] == 256 and event['token'] == 8 and not playing


def test_failed_native_stop_does_not_acknowledge_permission_to_play_cached_audio():
    from app.powerpoint import _control_media

    class Player:
        def Stop(self):
            raise RuntimeError('Office disconnected during stop')
    event, playing = _control_media('stop_media', {'slide_id': 256, 'token': 9}, 256, {1: Player()}, {1: 'en'}, {1})
    assert event['event'] == 'media_error' and event['operation'] == 'stop_media' and playing == {1}
