import pytest

from app.slideshow_shortcuts import DEFAULTS, KeyPolicy, saved_bindings, validate


def test_defaults_migrate_invalid_settings_and_do_not_share_mutable_values():
    assert saved_bindings(None) == DEFAULTS
    settings = saved_bindings({'en': 'Space'})
    settings['en'] = 'A'
    assert DEFAULTS['en'] == 'Space'


@pytest.mark.parametrize('update', [
    {'en': 'Ctrl+A'}, {'both': 'A'}, {'both': 'Ctrl+Alt+A'}, {'vi': 'Space'},
    {'en': 'Left'}, {'vi': 'Up'}, {'en': 'Esc'}, {'vi': 'F5'},
    {'previous': 'A', 'next': 'A'}, {'volume_up': 'Space'}, {'next': 'Ctrl+D'},
    {'both': 'Alt+F4'}, {'both': 'Alt+Space'}, {'both': 'Win+Space'}, {'en': 32},
])
def test_validation_preserves_arity_navigation_and_system_keys(update):
    with pytest.raises(ValueError):
        validate(DEFAULTS | update)


def test_valid_reassignment_keeps_exact_modifiers():
    policy = KeyPolicy({'en': 'A', 'vi': 'F6', 'both': 'Shift+A'})
    assert policy.key(65, 0, True, True) == (True, 'en')
    assert policy.key(65, 0, False, True) == (True, None)
    assert policy.key(65, 4, True, True) == (True, 'both')
    assert policy.key(65, 4, False, True) == (True, None)
    assert policy.key(65, 5, True, True) == (False, None)


def test_repeat_release_modifiers_focus_and_unrelated_keys():
    policy = KeyPolicy()
    assert policy.key(32, 1, True, True) == (True, 'both')
    assert policy.key(32, 0, True, True) == (True, None), 'Modifier release must not start the other language'
    assert policy.key(32, 0, False, True) == (True, None)
    assert policy.key(32, 0, True, True) == (True, 'en')
    assert policy.key(32, 0, True, False) == (False, None)
    assert policy.key(32, 0, False, False) == (False, None)
    for key in (0x1B, 0x74, 65):
        assert policy.key(key, 0, True, True) == (False, None)


def test_press_elsewhere_is_not_suppressed_and_does_not_queue_read():
    policy = KeyPolicy()
    for key, mods in [(32, 0), (13, 0), (32, 1)]:
        assert policy.key(key, mods, True, False) == (False, None)
        assert policy.key(key, mods, False, False) == (False, None)


def test_volume_and_navigation_keys_are_scoped_and_do_not_repeat():
    policy = KeyPolicy()
    for key, action in [(0x26, 'volume_up'), (0x28, 'volume_down')]:
        assert policy.key(key, 0, True, True) == (True, action)
        assert policy.key(key, 0, True, True) == (True, None)
        assert policy.key(key, 0, False, True) == (True, None)
        assert policy.key(key, 0, True, False) == (False, None)
        assert policy.key(key, 1, True, True) == (False, None)
    for key, action in ((0x25, 'previous'), (0x27, 'next')):
        assert policy.key(key, 0, True, True) == (True, action)
        assert policy.key(key, 0, True, True) == (True, None)
        assert policy.key(key, 0, False, True) == (True, None)
        assert policy.key(key, 0, True, False) == (False, None)


def test_saved_three_reading_keys_migrate_without_losing_teacher_choices():
    chosen = {'en': 'A', 'vi': 'F6', 'both': 'Shift+A'}
    assert saved_bindings(chosen) == DEFAULTS | chosen


def test_wasd_replaces_arrows_and_keeps_function_keys_and_other_apps_free():
    policy = KeyPolicy(DEFAULTS | {'previous': 'A', 'next': 'D', 'volume_up': 'W', 'volume_down': 'S'})
    for name, action in [('A', 'previous'), ('D', 'next'), ('W', 'volume_up'), ('S', 'volume_down')]:
        assert policy.key(ord(name), 0, True, False) == (False, None)
        assert policy.key(ord(name), 0, True, True) == (True, action)
        assert policy.key(ord(name), 0, False, True) == (True, None)
    for key in (0x25, 0x26, 0x27, 0x28, 0x1B, 0x74):
        assert policy.key(key, 0, True, True) == (False, None)


def test_shortcut_storage_failure_keeps_previous_binding_and_live_worker():
    import sqlite3
    from types import SimpleNamespace

    from PySide6.QtCore import QCoreApplication, QObject

    from app.shortcut_settings import ShortcutSettings

    app = QCoreApplication.instance() or QCoreApplication([])
    calls = []
    bridge = QObject()
    def fail(*args):
        raise sqlite3.OperationalError('database is locked')
    bridge.library = SimpleNamespace(setting=lambda *a: dict(DEFAULTS), set_setting=fail)
    bridge.powerpoint_worker = SimpleNamespace(navigate=lambda *a: calls.append(a))
    settings = ShortcutSettings(bridge)
    assert not settings.save(DEFAULTS | {'en': 'A'})
    assert settings.bindings == DEFAULTS and settings.error and 'Chưa lưu' in settings.message
    assert not calls
    app.processEvents()
