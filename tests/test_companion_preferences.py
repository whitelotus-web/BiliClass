import sqlite3
import time
from threading import Event

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QTimer

from app.companion_preferences import CompanionPreferences
from app.library import Library


def pump_until(predicate, timeout=5):
    app = QCoreApplication.instance() or QCoreApplication([])
    end = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < end
        app.processEvents()
        time.sleep(.002)
    app.processEvents()


def test_drag_is_live_without_gui_database_writes_and_only_last_value_is_saved(tmp_path, monkeypatch):
    from app.narration_preferences import store_choices

    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    owner = QObject()
    preferences = CompanionPreferences(library, owner)
    writes = []
    monkeypatch.setattr('app.companion_preferences.store_choices',
                        lambda directory, values: writes.append(dict(values)) or store_choices(directory, values))
    # Held by a separate connection exactly as during a conversion/save.
    lock = sqlite3.connect(tmp_path / 'library.db')
    lock.execute('BEGIN IMMEDIATE')
    ticks = []
    timer = QTimer()
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(time.monotonic()))
    timer.start()
    try:
        start = time.monotonic()
        for value in range(100, 29, -1):
            preferences.select_opacity(value)
            app.processEvents()
        assert time.monotonic() - start < .5
        assert preferences.opacity == 30 and writes == []
        preferences.flush()
        pump_until(lambda: len(ticks) >= 10)
        assert preferences.worker is not None and preferences.opacity == 30
        lock.rollback()
        pump_until(lambda: preferences.worker is None and not preferences.pending)
        assert library.setting('companion_panel_opacity', None) == 30
        assert writes == [{'companion_panel_opacity': 30}]
        assert max(b - a for a, b in zip(ticks, ticks[1:])) < .2
    finally:
        lock.rollback()
        lock.close()
        timer.stop()
        preferences.shutdown()
        library.close()
        owner.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_new_drag_wins_over_in_flight_save_and_shutdown_flushes_final_choice(tmp_path, monkeypatch):
    from app.narration_preferences import store_choices

    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    preferences = CompanionPreferences(library)
    started, release = Event(), Event()
    calls = []

    def store(directory, values):
        calls.append(dict(values))
        if len(calls) == 1:
            started.set()
            assert release.wait(3)
        return store_choices(directory, values)

    monkeypatch.setattr('app.companion_preferences.store_choices', store)
    try:
        preferences.select_opacity(70)
        preferences.flush()
        pump_until(started.is_set)
        preferences.select_opacity(30)
        release.set()
        # Close before the 350ms debounce expires: the final choice still wins.
        preferences.shutdown()
        assert library.setting('companion_panel_opacity', None) == 30
        assert calls == [{'companion_panel_opacity': 70}, {'companion_panel_opacity': 30}]
        app.processEvents()
    finally:
        release.set()
        preferences.shutdown()
        library.close()


def test_failed_write_keeps_live_value_and_previous_saved_setting(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    library.set_setting('companion_panel_opacity', 80)
    preferences = CompanionPreferences(library)
    errors = []
    preferences.failed.connect(errors.append)

    def fail(*args):
        raise OSError('fixture disk failure')

    monkeypatch.setattr('app.companion_preferences.store_choices', fail)
    try:
        preferences.select_opacity(40)
        preferences.flush()
        pump_until(lambda: preferences.worker is None and preferences._attempts == 1)
        assert preferences.opacity == 40 and library.setting('companion_panel_opacity', None) == 80
        preferences.shutdown()
        assert errors and library.setting('companion_panel_opacity', None) == 80
        app.processEvents()
    finally:
        preferences.shutdown()
        library.close()


def test_reading_gap_changes_without_waiting_for_database_and_reopens_saved_choice(tmp_path, monkeypatch):
    from app.narration_preferences import store_choices
    from app.narration_timing import reading_gap

    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    preferences = CompanionPreferences(library)
    started, release = Event(), Event()

    def store(directory, values):
        started.set()
        assert release.wait(3)
        return store_choices(directory, values)

    monkeypatch.setattr('app.companion_preferences.store_choices', store)
    try:
        assert preferences.reading_gap == 400
        preferences.select_reading_gap(200)
        pump_until(started.is_set)
        assert preferences.reading_gap == reading_gap(tmp_path) == 200
        assert library.setting('paragraph_gap_ms', None) is None
        release.set()
        pump_until(lambda: preferences.worker is None and not preferences.pending)
        assert library.setting('paragraph_gap_ms', None) == 200
        preferences.shutdown()
        reopened = CompanionPreferences(library)
        assert reopened.reading_gap == 200
        reopened.shutdown()
        app.processEvents()
    finally:
        release.set()
        preferences.shutdown()
        library.close()
