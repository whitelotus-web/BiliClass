"""A smaller archive must still restore every original file independently."""

import json
import os
import zipfile
from pathlib import Path

import pytest

from app import storage
from app.library import Library


@pytest.fixture
def duplicate_library(tmp_path):
    root = tmp_path / 'data'
    library = Library(root)
    lesson = library.create('Giữ đủ tệp', 'Toán', 'THPT', '11', [('Mở đầu', 'Nội dung')])
    library.close()
    content = bytes(range(256)) * 8192
    names = ['sources/original.pptx', 'google_jobs/job/result.pptx', 'chatgpt/job/input.pptx']
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return root, lesson, names, content


def rewrite_archive(original, target, change):
    with zipfile.ZipFile(original) as source:
        contents = {entry.filename: source.read(entry) for entry in source.infolist()}
    manifest = json.loads(contents.pop('manifest.json'))
    change(manifest, contents)
    with zipfile.ZipFile(target, 'w') as archive:
        for name, value in contents.items():
            archive.writestr(name, value)
        archive.writestr('manifest.json', json.dumps(manifest))
    return target


def test_duplicate_contents_stored_once_restore_every_path_as_independent_files(duplicate_library, tmp_path):
    root, lesson, names, content = duplicate_library
    progress = []
    output = storage.backup_library(root, progress=lambda done, total: progress.append((done, total)))
    with zipfile.ZipFile(output) as archive:
        manifest = json.loads(archive.read('manifest.json'))
        assert manifest['version'] == 3
        assert manifest['aliases'] == {name: names[0] for name in names[1:]}
        assert set(archive.namelist()) == {'manifest.json', 'library.db', names[0]}
        assert archive.testzip() is None
    assert output.stat().st_size < len(content) + 100000
    assert progress[-1][0] == progress[-1][1]
    assert [done / total for done, total in progress] == sorted(done / total for done, total in progress)
    destination = storage.restore_backup(output, tmp_path / 'restored')
    assert all((destination / name).read_bytes() == content for name in names)
    library = Library(destination)
    try:
        assert library.get(lesson['id']) == lesson
    finally:
        library.close()
    (destination / names[1]).write_bytes(b'edited independently')
    assert (destination / names[0]).read_bytes() == content
    assert (destination / names[2]).read_bytes() == content
    assert all((root / name).read_bytes() == content for name in names)


def test_equal_size_different_contents_are_never_merged(duplicate_library):
    root, _, names, content = duplicate_library
    (root / names[1]).write_bytes(b'x' * len(content))
    (root / names[2]).write_bytes(b'y' * len(content))
    output = storage.backup_library(root)
    with zipfile.ZipFile(output) as archive:
        manifest = json.loads(archive.read('manifest.json'))
        assert manifest['version'] == 2 and 'aliases' not in manifest
        assert all(name in archive.namelist() for name in names)
        assert archive.read(names[1]) == b'x' * len(content)


def test_space_preflight_counts_unique_backup_bytes_but_all_restored_copies(duplicate_library, tmp_path, monkeypatch):
    root, _, names, content = duplicate_library
    checks = []
    monkeypatch.setattr(storage, '_check_space', lambda parent, required: checks.append((Path(parent), required)))
    output = storage.backup_library(root)
    with zipfile.ZipFile(output) as archive:
        unique = sum(entry.file_size for entry in archive.infolist() if entry.filename != 'manifest.json')
        expanded = unique + len(content) * (len(names) - 1) + archive.getinfo('manifest.json').file_size
    assert checks == [(output.parent, unique)]
    storage.restore_backup(output, tmp_path / 'restored')
    assert checks[-1] == (tmp_path, expanded)


def test_backup_fits_unique_budget_restore_still_requires_full_size(duplicate_library, tmp_path, monkeypatch):
    from app import storage_space

    root, _, _, content = duplicate_library
    free = len(content) + (root / 'library.db').stat().st_size + 128 * 1024**2 + 4096
    monkeypatch.setattr(storage_space.shutil, 'disk_usage', lambda _: type('Disk', (), {'free': free})())
    output = storage.backup_library(root)
    with pytest.raises(ValueError, match='trống'):
        storage.restore_backup(output, tmp_path / 'restored')
    assert not (tmp_path / 'restored').exists()


@pytest.mark.parametrize('case', ['missing', 'chain', 'cycle', 'self', 'non_string', 'not_mapping',
                                 'outside', 'case_collision', 'wrong_hash', 'extra_entry'])
def test_invalid_aliases_rejected_without_partial_restore(duplicate_library, tmp_path, case):
    root, _, names, _ = duplicate_library
    original = storage.backup_library(root)

    def change(manifest, contents):
        aliases = manifest['aliases']
        if case == 'missing':
            aliases[names[1]] = 'sources/missing.pptx'
        elif case == 'chain':
            aliases[names[2]] = names[1]
        elif case == 'cycle':
            aliases[names[1]], aliases[names[2]] = names[2], names[1]
        elif case == 'self':
            aliases[names[1]] = names[1]
        elif case == 'non_string':
            aliases[names[1]] = []
        elif case == 'not_mapping':
            manifest['aliases'] = []
        elif case in {'outside', 'case_collision'}:
            invalid = '../outside.pptx' if case == 'outside' else names[0].upper()
            manifest['files'][invalid] = manifest['files'].pop(names[1])
            aliases[invalid] = aliases.pop(names[1])
        elif case == 'wrong_hash':
            manifest['files'][names[1]] = '0' * 64
        elif case == 'extra_entry':
            contents[names[1]] = contents[names[0]]

    corrupt = rewrite_archive(original, tmp_path / 'bad.bcbackup', change)
    with pytest.raises(ValueError):
        storage.restore_backup(corrupt, tmp_path / 'restored')
    assert not (tmp_path / 'restored').exists()
    assert not list(tmp_path.glob('biliclass-restore-*'))


def test_unique_entry_corruption_also_invalidates_all_duplicate_paths(duplicate_library, tmp_path):
    root, _, names, _ = duplicate_library
    original = storage.backup_library(root)

    def change(manifest, contents):
        contents[names[0]] = b'changed'

    corrupt = rewrite_archive(original, tmp_path / 'bad.bcbackup', change)
    with pytest.raises(ValueError, match='Checksum'):
        storage.restore_backup(corrupt, tmp_path / 'restored')
    assert not (tmp_path / 'restored').exists()


@pytest.mark.parametrize('limit', ['MAX_RESTORE_BYTES', 'MAX_BACKUP_FILES'])
def test_restore_limits_include_aliases(duplicate_library, tmp_path, monkeypatch, limit):
    root, _, _, content = duplicate_library
    original = storage.backup_library(root)
    with zipfile.ZipFile(original) as archive:
        assert len(archive.namelist()) == 3
    monkeypatch.setattr(storage, limit, len(content) * 2 if limit == 'MAX_RESTORE_BYTES' else 4)
    with pytest.raises(ValueError):
        storage.restore_backup(original, tmp_path / 'restored')
    assert not (tmp_path / 'restored').exists()


@pytest.mark.parametrize('index', [0, 1])
def test_changed_original_or_alias_keeps_last_good_backup(duplicate_library, index):
    root, _, names, content = duplicate_library
    output = storage.backup_library(root)
    before = output.read_bytes()
    changed = False

    def progress(done, total):
        nonlocal changed
        if done * 2 == total and not changed:
            path = root / names[index]
            signature = path.stat()
            path.write_bytes(b'z' * len(content))
            os.utime(path, ns=(signature.st_atime_ns, signature.st_mtime_ns + 1000000000))
            changed = True

    with pytest.raises(ValueError, match='thay đổi'):
        storage.backup_library(root, output, progress=progress)
    assert output.read_bytes() == before
    assert not list(output.parent.glob('*.tmp'))
    assert not list(output.parent.glob('biliclass-backup-*'))
