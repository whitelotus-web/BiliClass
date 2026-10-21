from contextlib import closing

from app.chatgpt_handoff import inspect_returned_deck
from app.library import Library
from app.library_catalog import LibraryCatalog
from app.library_products import is_product
from app.voice_import import import_presentation


def test_source_drafts_stay_available_for_voice_without_appearing_as_products():
    rows = [{'id': 'converted', 'title': 'Bài song ngữ', 'library_product': True},
            {'id': 'source', 'title': 'Bài nguồn', 'library_product': False}]
    catalog = LibraryCatalog.__new__(LibraryCatalog)
    catalog._active, catalog._trash = rows, []
    assert [row['id'] for row in catalog.rows('title_asc')] == ['converted']
    assert {row['id'] for row in catalog.rows('title_asc', include_sources=True)} == {'source', 'converted'}


def test_published_source_remains_a_product_when_voice_is_later_missing():
    assert is_product({'voice_only': False})
    assert not is_product({'voice_only': True, 'narration': {'mode': 'none'}})
    assert not is_product({'voice_only': True, 'narration': {'complete': 175, 'total': 180, 'failed': 5}})
    record = {'complete': 180, 'total': 180, 'failed': 0}
    assert is_product({'voice_only': True, 'narration': record})
    assert is_product({'voice_only': True, 'voice_published': True,
                       'narration': {'complete': 175, 'total': 180}})


def test_importing_the_converted_powerpoint_reuses_its_existing_product(tmp_path):
    from test_narration_workspace import source

    path = source(tmp_path/'lecture.pptx', 'Cơ năng', 'VI: Cơ năng\nEN: Mechanical energy')
    directory = tmp_path/'data'
    draft, _ = import_presentation(directory, path)
    with closing(Library(directory)) as library:
        converted = library.create_external_lesson(
            {'title': 'Bài đã chuyển đổi', 'subject': 'Vật lý', 'education_level': 'THPT', 'grade': '11',
             'conversion_format': 'parallel_columns', 'style': 'source', 'level': 4,
             'layout': 'split_view', 'mode': 'preserve', 'preset': 'standard'},
            library.store_source(path), inspect_returned_deck(path))
        assert converted['id'] != draft['id']
    reopened, _ = import_presentation(directory, path)
    assert reopened['id'] == converted['id'] and not reopened.get('voice_only')
    with closing(Library(directory)) as library:
        assert len(library.list_lessons(verify_audio=False)) == 2
