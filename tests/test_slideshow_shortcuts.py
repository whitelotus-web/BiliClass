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
    for key in (0x25, 0x27, 0x1B, 0x74, 65):
        assert policy.key(key, 0, True, True) == (False, None)


def test_press_elsewhere_is_not_suppressed_and_does_not_queue_read():
    policy = KeyPolicy()
    for key, mods in [(32, 0), (13, 0), (32, 1)]:
        assert policy.key(key, mods, True, False) == (False, None)
        assert policy.key(key, mods, False, False) == (False, None)


def test_volume_keys_are_scoped_and_reserved_without_stealing_horizontal_navigation():
    policy = KeyPolicy()
    for key, action in [(0x26, 'volume_up'), (0x28, 'volume_down')]:
        assert policy.key(key, 0, True, True) == (True, action)
        assert policy.key(key, 0, True, True) == (True, None)
        assert policy.key(key, 0, False, True) == (True, None)
        assert policy.key(key, 0, True, False) == (False, None)
        assert policy.key(key, 1, True, True) == (False, None)
    for key in (0x25, 0x27):
        assert policy.key(key, 0, True, True) == (False, None)
