from PySide6.QtCore import QCoreApplication, QObject

from app.library import Library
from app.library_preferences import LibraryPreferences


def test_last_rapid_view_and_sort_choices_are_flushed_on_exit(tmp_path):
    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    owner = QObject()
    choices = LibraryPreferences(library, owner)
    for value in ('grid', 'list', 'grid'):
        choices.select('library_view', value)
    choices.select('lesson_order', 'updated_desc')
    choices.select('lesson_order', 'title_asc')
    assert choices.values == {'library_view': 'grid', 'lesson_order': 'title_asc'}
    choices.shutdown()
    assert library.setting('library_view', '') == 'grid'
    assert library.setting('lesson_order', '') == 'title_asc'
    choices._finished()  # A queued completion may arrive after shutdown removed its sender.
    app.processEvents()
    library.close()


def test_invalid_or_closed_changes_cannot_replace_the_saved_preference(tmp_path):
    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    owner = QObject()
    choices = LibraryPreferences(library, owner)
    choices.select('library_view', 'invalid')
    choices.select('unknown', 'grid')
    assert not choices.pending and choices.values['library_view'] == 'list'
    choices.shutdown()
    choices.select('library_view', 'grid')
    assert choices.values['library_view'] == 'list'
    app.processEvents()
    library.close()
