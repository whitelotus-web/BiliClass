import json
import zipfile

import pytest

from app import storage
from app.library import Library


@pytest.fixture
def data(tmp_path):
    root = tmp_path / 'data'
    library = Library(root)
    lesson = library.create('Backup test', 'Physics', 'THPT', '10', [('Slide 1', 'Năng lượng')])
    library.close()
    (root / 'audio').mkdir()
    (root / 'audio/sample.wav').write_bytes(b'bounded audio fixture' * 100000)
    return root, lesson


def test_streamed_backup_round_trip_and_staging_uses_destination_drive(data, tmp_path, monkeypatch):
    root, lesson = data
    actual_temp = storage.tempfile.TemporaryDirectory
    staging_parents = []

    def capture_temp(*args, **kwargs):
        staging_parents.append(kwargs.get('dir'))
        return actual_temp(*args, **kwargs)

    monkeypatch.setattr(storage.tempfile, 'TemporaryDirectory', capture_temp)
    archive = storage.backup_library(root, tmp_path / 'exports/test.bcbackup')
    destination = tmp_path / 'restored'
    storage.restore_backup(archive, destination)
    assert staging_parents == [archive.parent, destination.parent]
    assert (destination / 'audio/sample.wav').read_bytes() == (root / 'audio/sample.wav').read_bytes()
    library = Library(destination)
    try:
        assert library.get(lesson['id']) == lesson
    finally:
        library.close()


@pytest.mark.parametrize('limit', ['MAX_BACKUP_BYTES', 'MAX_RESTORE_BYTES', 'MAX_BACKUP_FILES', 'MAX_FILE_BYTES'])
def test_oversized_backup_never_replaces_previous_good_archive(data, tmp_path, monkeypatch, limit):
    root, _ = data
    archive = storage.backup_library(root, tmp_path / 'good.bcbackup')
    before = archive.read_bytes()
    monkeypatch.setattr(storage, limit, 1)
    with pytest.raises(ValueError, match='giới hạn'):
        storage.backup_library(root, archive)
    assert archive.read_bytes() == before
    assert not list(tmp_path.glob('*.tmp'))
    assert not list(tmp_path.glob('biliclass-backup-*'))


def test_corrupt_restore_does_not_publish_partial_library(data, tmp_path):
    root, _ = data
    archive = storage.backup_library(root, tmp_path / 'good.bcbackup')
    corrupt = tmp_path / 'corrupt.bcbackup'
    with zipfile.ZipFile(archive) as original, zipfile.ZipFile(corrupt, 'w') as changed:
        for entry in original.infolist():
            content = original.read(entry)
            if entry.filename == 'manifest.json':
                value = json.loads(content)
                value['files']['audio/sample.wav'] = '0' * 64
                content = json.dumps(value).encode()
            changed.writestr(entry, content)
    destination = tmp_path / 'restored'
    destination.mkdir()
    with pytest.raises(ValueError, match='Checksum'):
        storage.restore_backup(corrupt, destination)
    assert list(destination.iterdir()) == []
    assert not list(tmp_path.glob('biliclass-restore-*'))


def test_restore_rejects_oversized_entry_before_publishing(data, tmp_path, monkeypatch):
    root, _ = data
    archive = storage.backup_library(root, tmp_path / 'good.bcbackup')
    monkeypatch.setattr(storage, 'MAX_FILE_BYTES', 100)
    destination = tmp_path / 'restored'
    with pytest.raises(ValueError, match='giới hạn'):
        storage.restore_backup(archive, destination)
    assert not destination.exists()
