"""Only explicit appearance choices persist; failures preserve the prior mode."""
from types import SimpleNamespace

import pytest

from app.appearance import saved_mode
from app.library import Library
from app.ui import Bridge


@pytest.mark.parametrize('value', [None, 'system', '', {'mode': 'dark'}, ['dark']])
def test_invalid_saved_mode_falls_back_to_light(tmp_path, value):
    library = Library(tmp_path)
    try:
        library.set_setting('application_theme', value)
        assert saved_mode(library) == 'light'
    finally:
        library.close()


def context(library):
    events, errors = [], []
    return SimpleNamespace(
        library=library, _application_theme=saved_mode(library),
        applicationThemeChanged=SimpleNamespace(emit=lambda: events.append('changed')),
        inform=lambda *args, **kwargs: errors.append((args, kwargs)),
    ), events, errors


def test_choice_persists_and_does_not_change_lesson_or_voice(tmp_path, monkeypatch):
    schemes = []
    monkeypatch.setattr('app.appearance.apply_color_scheme', schemes.append)
    library = Library(tmp_path)
    reopened = None
    try:
        lesson = library.create('Bài thử', 'Vật lý', 'THPT', '10', [('Năng lượng', 'Energy')])
        library.set_setting('voice_options', {'voice': 'pair:truc-ly', 'rate': 0})
        bridge, events, errors = context(library)
        assert bridge._application_theme == 'light'
        Bridge.setApplicationTheme(bridge, 'dark')
        assert bridge._application_theme == 'dark' and events == ['changed'] and not errors
        assert library.get(lesson['id']) == lesson
        assert library.setting('voice_options', {}) == {'voice': 'pair:truc-ly', 'rate': 0}
        reopened = Library(tmp_path)
        assert saved_mode(reopened) == 'dark'
        Bridge.setApplicationTheme(bridge, 'dark')
        assert events == ['changed'], 'Re-selecting a mode is a no-op'
        Bridge.setApplicationTheme(bridge, 'light')
        assert saved_mode(reopened) == 'light' and schemes == ['dark', 'light']
    finally:
        if reopened:
            reopened.close()
        library.close()


def test_failed_save_keeps_prior_mode(tmp_path, monkeypatch):
    library = Library(tmp_path)
    try:
        bridge, events, errors = context(library)
        def fail(*_):
            raise OSError('Fixture disk failure')
        monkeypatch.setattr(library, 'set_setting', fail)
        Bridge.setApplicationTheme(bridge, 'dark')
        assert bridge._application_theme == 'light' and not events and len(errors) == 1
    finally:
        library.close()


def test_invalid_choice_is_rejected(tmp_path):
    library = Library(tmp_path)
    try:
        bridge, events, errors = context(library)
        Bridge.setApplicationTheme(bridge, 'system')
        assert not events and len(errors) == 1
        assert library.setting('application_theme', None) is None
    finally:
        library.close()
