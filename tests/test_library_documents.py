import json
import zipfile
from contextlib import closing
from pathlib import Path
from threading import Event

import pytest
from docx import Document

from app import library_actions, word_jobs
from app.library import Library
from app.library_documents import change, word_id, word_rows
from app.library_download import export
from app.library_view import query
from app.word_document import Package


@pytest.fixture
def mixed(tmp_path):
    directory = tmp_path / 'data'
    with closing(Library(directory)) as library:
        slide = library.create('Động năng', 'Vật lý', 'THPT', '11', [('Slide 1', 'Vật có vận tốc 12 m/s.')])
        library.edit_segment(slide['id'], slide['segments'][0]['id'], 'Vật có vận tốc 12 m/s.', 'The object has a velocity of 12 m/s.', True)
    source = tmp_path / 'Bài học Word.docx'
    document = Document()
    document.add_paragraph('Vận tốc 12 m/s.')
    document.save(source)
    job = word_jobs.create(directory, source)
    package = Package(source)
    region = package.selection([dict(paragraph='p0', start=0, end=len(package.rows[0]['text']))])[0]
    word_jobs.selections(directory, job['id'], [region])
    word_jobs.edit(directory, job['id'], region['id'], 'Velocity 12 m/s.')
    word = word_jobs.export(directory, job['id'], Event())
    return directory, slide, word, source


def test_all_and_word_groups_share_catalog_but_word_never_enters_voice_groups(mixed):
    directory, slide, job, _ = mixed
    with closing(Library.read_only(directory)) as library:
        rows = library.list_lessons() + word_rows(directory)
    result = query(rows)
    assert result['total'] == 2 and result['groups']['word'] == 1
    assert result['groups']['none'] == 1 and result['groups']['ready'] == 0
    assert query(rows, group='none')['ids'] == [slide['id']]
    assert query(rows, group='word')['ids'] == ['word:' + job['id']]
    assert query(rows, text='WORD', grade='THPT|11')['ids'] == ['word:' + job['id']]
    assert query(rows, text='PowerPoint')['ids'] == [slide['id']]
    assert not query(rows, group='word', voice='none')['rows']
    assert word_rows(directory)[0]['selected_count'] == 1


def test_old_word_summary_is_enriched_without_rewriting_the_record(mixed):
    directory, _, job, _ = mixed
    folder = word_jobs.folder_for(directory, job['id'])
    original = (folder / 'job.json').read_bytes()
    (folder / 'summary.json').write_text(json.dumps({key: job[key] for key in ('id', 'title', 'phase', 'updated_at')}))
    row = word_rows(directory)[0]
    assert row['grade'] == '11' and row['preview_text'] == 'Vận tốc 12 m/s.'
    assert (folder / 'job.json').read_bytes() == original


def test_mixed_download_keeps_native_formats_and_source_files(mixed, tmp_path):
    directory, slide, job, source = mixed
    before = source.read_bytes()
    target = tmp_path / 'Các bài.zip'
    result = export(directory, [slide['id'], 'word:' + job['id']], target, with_voice=False)
    with zipfile.ZipFile(target) as archive:
        assert sum(name.endswith('.pptx') for name in archive.namelist()) == 1
        word_name = next(name for name in archive.namelist() if name.endswith('.docx'))
        assert archive.read(word_name) == Path(job['export_path']).read_bytes()
    assert result['count'] == 2 and source.read_bytes() == before
    standalone = tmp_path / 'Bản tải.docx'
    export(directory, ['word:' + job['id']], standalone)
    assert standalone.read_bytes() == Path(job['export_path']).read_bytes()
    with pytest.raises(ValueError):
        export(directory, ['word:' + job['id']], standalone.with_suffix('.pptx'))


def test_word_download_rejects_unpublished_or_modified_result_and_keeps_destination(mixed, tmp_path):
    directory, _, job, _ = mixed
    target = tmp_path / 'existing.docx'
    target.write_bytes(b'keep previous')
    folder = word_jobs.folder_for(directory, job['id'])
    (folder / 'result.docx').write_bytes(b'changed result')
    with pytest.raises(ValueError, match='thay đổi'):
        export(directory, ['word:' + job['id']], target)
    assert target.read_bytes() == b'keep previous'


def test_mixed_trash_undo_and_stale_receipt_keep_both_types_consistent(mixed):
    directory, slide, job, source = mixed
    ids = [slide['id'], 'word:' + job['id']]
    receipt = change(directory, 'trash', ids, library_actions.change, with_receipt=True)
    assert set(receipt) == set(ids) and not word_rows(directory)
    assert len(word_rows(directory, trash=True)) == 1
    bad = {**receipt, ids[1]: 'old deletion'}
    with pytest.raises(ValueError, match='thay đổi'):
        change(directory, 'restore', ids, library_actions.change, expected_deleted=bad)
    assert not word_rows(directory)
    assert change(directory, 'restore', ids, library_actions.change, expected_deleted=receipt) == 2
    with closing(Library.read_only(directory)) as library:
        assert library.get(slide['id'])['title'] == slide['title']
    assert source.is_file() and len(word_rows(directory)) == 1


def test_failed_powerpoint_transaction_rolls_word_trash_back(mixed):
    directory, _, job, _ = mixed
    with pytest.raises(ValueError):
        change(directory, 'trash', ['missing', 'word:' + job['id']], library_actions.change, with_receipt=True)
    assert not word_jobs.read(directory, job['id']).get('deleted_at')
    assert len(word_rows(directory)) == 1


def test_mixed_purge_only_removes_word_managed_folder_after_trash(mixed):
    directory, slide, job, source = mixed
    ids = [slide['id'], 'word:' + job['id']]
    with pytest.raises(ValueError, match='thùng rác'):
        change(directory, 'purge', ids, library_actions.change)
    change(directory, 'trash', ids, library_actions.change)
    assert change(directory, 'purge', ids, library_actions.change) == 2
    assert not word_jobs.folder_for(directory, job['id']).exists()
    assert source.is_file() and Path(job['export_path']).is_file()
    assert not word_rows(directory, trash=True)
    with pytest.raises(ValueError):
        word_id('word:../../elsewhere')
