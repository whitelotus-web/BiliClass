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


def test_daily_backup_reuses_only_unchanged_owned_package_without_new_success_time(data, monkeypatch):
    root, _ = data
    output = storage.backup_library(root, daily=True)
    state = storage.backup_state(root)
    snapshot = storage._snapshot

    def unexpected_snapshot(*args):
        raise AssertionError('Unchanged daily backup must not reread the entire library')

    monkeypatch.setattr(storage, '_snapshot', unexpected_snapshot)
    assert storage.backup_library(root, daily=True) == output
    assert storage.backup_state(root) == state
    monkeypatch.setattr(storage, '_snapshot', snapshot)
    output.write_bytes(b'externally damaged archive')
    assert storage.backup_library(root, daily=True) == output
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert json.loads(archive.read('manifest.json'))['version'] == 2
    assert storage.backup_state(root)['last_bytes'] == output.stat().st_size


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


@pytest.mark.parametrize('legacy', [False, True])
def test_restore_on_another_drive_rebases_history_assets_and_nested_templates(data, tmp_path, legacy):
    root, lesson = data
    template = root / 'templates/custom/template.pptx'
    template.parent.mkdir(parents=True)
    template.write_bytes(b'template')
    library = Library(root)
    library.set_setting('template_path', str(template))
    library.close()
    archive = storage.backup_library(root, tmp_path / 'original.bcbackup')
    if legacy:
        converted = tmp_path / 'legacy.bcbackup'
        with zipfile.ZipFile(archive) as source, zipfile.ZipFile(converted, 'w') as target:
            for entry in source.infolist():
                content = source.read(entry)
                if entry.filename == 'manifest.json':
                    manifest = json.loads(content)
                    manifest['version'] = 1
                    manifest.pop('root')
                    content = json.dumps(manifest).encode()
                target.writestr(entry, content)
        archive = converted
    destination = storage.restore_backup(archive, tmp_path / 'another-drive/restored')
    library = Library(destination)
    try:
        assert library.setting('template_path', '') == str(destination / 'templates/custom/template.pptx')
        assert library.get(lesson['id']) == lesson
        assert (destination / 'templates/custom/template.pptx').read_bytes() == b'template'
    finally:
        library.close()


def test_failed_backup_preserves_last_success_and_reports_reason(data, tmp_path, monkeypatch):
    root, _ = data
    archive = storage.backup_library(root, tmp_path / 'good.bcbackup')
    before = storage.backup_state(root)
    monkeypatch.setattr(storage, 'MAX_BACKUP_BYTES', 1)
    with pytest.raises(ValueError):
        storage.backup_library(root, tmp_path / 'bad.bcbackup')
    after = storage.backup_state(root)
    assert after['status'] == 'failed' and 'giới hạn' in after['last_error']
    assert after['last_success'] == before['last_success']
    assert after['last_path'] == str(archive)
    assert not (tmp_path / 'bad.bcbackup').exists()


def test_restore_preflights_disk_space_and_keeps_destination_absent(data, tmp_path, monkeypatch):
    root, _ = data
    archive = storage.backup_library(root, tmp_path / 'good.bcbackup')
    from app import storage_space

    monkeypatch.setattr(storage_space.shutil, 'disk_usage', lambda _: type('Disk', (), {'free': 0})())
    with pytest.raises(ValueError, match='trống'):
        storage.restore_backup(archive, tmp_path / 'restored')
    assert not (tmp_path / 'restored').exists()


def test_backup_retention_uses_budget_but_always_keeps_latest(tmp_path):
    for day in range(10, 16):
        (tmp_path / f'BiliClass-202610{day}.bcbackup').write_bytes(b'x' * 100)
    manual = tmp_path / 'manual.bcbackup'
    manual.write_bytes(b'keep')
    storage.prune_backups(tmp_path, keep=14, budget=250)
    assert {p.name for p in tmp_path.iterdir()} == {
        'BiliClass-20261015.bcbackup', 'BiliClass-20261014.bcbackup', manual.name}
    storage.prune_backups(tmp_path, budget=1)
    assert (tmp_path / 'BiliClass-20261015.bcbackup').exists()
    assert manual.exists()


def test_checkpoint_and_template_round_trip_excludes_ephemeral_lock(data, tmp_path):
    root, _ = data
    job = root / 'google_jobs/test'
    job.mkdir(parents=True)
    (job / 'job.json').write_text(json.dumps({'artifact': str(job / 'result.pptx')}))
    (job / 'result.pptx').write_bytes(b'retained result')
    (job / 'active.lock').write_text('stale process')
    archive = storage.backup_library(root, tmp_path / 'jobs.bcbackup')
    destination = storage.restore_backup(archive, tmp_path / 'restored')
    assert json.loads((destination / 'google_jobs/test/job.json').read_text()) == {
        'artifact': str(destination / 'google_jobs/test/result.pptx')}
    assert not (destination / 'google_jobs/test/active.lock').exists()
