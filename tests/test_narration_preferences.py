from app.library import Library
from app.narration_preferences import read_mode, store_mode


def test_first_use_is_english_and_later_launch_uses_last_deliberate_choice(tmp_path):
    library = Library(tmp_path)
    try:
        assert read_mode(library) == 'en'
        for mode in ('vi', 'en', 'both'):
            store_mode(tmp_path, mode)
            assert read_mode(library) == mode
        library.set_setting('narration_last_mode', 'unknown')
        assert read_mode(library) == 'en'
    finally:
        library.close()


def test_single_language_uses_actual_footer_edge_and_deck_union_reserves_slots():
    from app.speaker_layout import fixed_slots

    assert fixed_slots((960, 540), mini=True, languages=('en',))['en'][:2] == (898, 508)
    deck_slots = fixed_slots((960, 540), mini=True, languages=('vi', 'en', 'both'))
    assert deck_slots['both'][0] + 50 == 948
    assert deck_slots['en'][0] == 848
    assert fixed_slots((960, 540), 'bottom_left', mini=True)['vi'][0] == 12
    centered = fixed_slots((960, 540), 'bottom_center', mini=True)
    assert centered['vi'][0] == 405


def test_last_choice_survives_reopening_the_library(tmp_path):
    library = Library(tmp_path)
    library.close()
    store_mode(tmp_path, 'vi')
    reopened = Library(tmp_path)
    try:
        assert read_mode(reopened) == 'vi'
    finally:
        reopened.close()


def test_positions_default_right_and_persist_without_changing_voice_or_revision(tmp_path):
    from app.lesson_narration import signature
    from app.narration_preferences import store_choices, store_lesson_position
    from app.speaker_layout import default_position, fixed_slots

    library = Library(tmp_path)
    try:
        lesson = library.create('Position fixture', 'Tin học', 'THPT', '10', [('Slide 1', 'Xin chào.')])
        before = signature(lesson)
        assert default_position(tmp_path) == 'bottom_right'
        for selected in ('top_left', 'top_center', 'top_right', 'bottom_left', 'bottom_center', 'bottom_right'):
            store_choices(tmp_path, {'narration_speaker_position': selected})
            saved = store_lesson_position(tmp_path, lesson['id'], selected)
            assert saved['revision'] == lesson['revision'] and signature(saved) == before
            assert saved['speaker_position'] == selected and default_position(tmp_path) == selected
            slots = fixed_slots((960, 540), selected, mini=True)
            assert len({p[1] for p in slots.values()}) == 1
            assert slots['vi'][0] < slots['en'][0] < slots['both'][0]
            assert 0 <= slots['vi'][0] and slots['both'][0] + 50 <= 960
            assert all(p[1] == (12 if selected.startswith('top_') else 508) for p in slots.values())
    finally:
        library.close()


def test_speaker_moves_immediately_and_coalesces_saves_without_busy_or_stale_lesson(monkeypatch, tmp_path):
    import threading
    import time
    from PySide6.QtCore import QCoreApplication, QObject, Signal
    from app.narration_preferences import NarrationPreferences, store_choices
    from app.narration_workspace import NarrationWorkspace

    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    first = library.create('First', 'Vật lý', 'THPT', '11', [('Slide 1', 'Dao động.')])
    second = library.create('Second', 'Vật lý', 'THPT', '11', [('Slide 1', 'Cộng hưởng.')])

    class Editor(QObject):
        selectionChanged = Signal()
        narrationChanged = Signal()
        changed = Signal()
        powerpointStateChanged = Signal()
        busy = narrationBusy = False
        teachingTransitioning = False
        powerpointState = {}
        powerpoint_worker = None
        class Classroom(QObject):
            changed = Signal()
            running = False
        classroom = Classroom()
        def launch(self, *_):
            raise AssertionError('Position must not start a global job')

    bridge = Editor()
    bridge._lesson = first
    bridge.narrationPreferences = NarrationPreferences(library)
    workspace = NarrationWorkspace(bridge)
    entered, release = threading.Event(), threading.Event()
    writes = []

    def delayed(directory, choices, positions=None):
        writes.append(dict(positions or {}))
        if len(writes) == 1:
            entered.set()
            assert release.wait(5)
        return store_choices(directory, choices, positions)

    monkeypatch.setattr('app.narration_preferences.store_choices', delayed)

    def wait(predicate):
        deadline = time.monotonic() + 5
        while not predicate():
            assert time.monotonic() < deadline
            app.processEvents()
            time.sleep(.002)

    try:
        started = time.monotonic()
        workspace.setSpeakerPosition('bottom_left')
        assert workspace.speakerPosition == 'bottom_left' and time.monotonic() - started < .1
        wait(entered.is_set)
        for position in ('bottom_right', 'bottom_center', 'bottom_left', 'bottom_center'):
            workspace.setSpeakerPosition(position)
        bridge._lesson = second
        workspace.setSpeakerPosition('bottom_left')
        # A delayed preference save must not restore an old title or voice blob.
        edited = library.get(first['id'])
        edited.update(title='Edited while saving', revision=edited['revision'] + 1)
        library._write(edited)
        release.set()
        wait(lambda: bridge.narrationPreferences.worker is None)
        assert len(writes) == 2 and not bridge.busy
        assert bridge._lesson['id'] == second['id'] and workspace.speakerPosition == 'bottom_left'
        saved = library.get(first['id'])
        assert saved['title'] == edited['title'] and saved['revision'] == edited['revision']
        assert saved['speaker_position'] == 'bottom_center'
        assert library.get(second['id'])['speaker_position'] == 'bottom_left'
    finally:
        release.set()
        bridge.narrationPreferences.shutdown()
        library.close()
