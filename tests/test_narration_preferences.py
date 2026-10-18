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


def test_last_choice_survives_reopening_the_library(tmp_path):
    library = Library(tmp_path)
    library.close()
    store_mode(tmp_path, 'vi')
    reopened = Library(tmp_path)
    try:
        assert read_mode(reopened) == 'vi'
    finally:
        reopened.close()
