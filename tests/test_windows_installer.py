"""The actual Windows installer against small disposable ZIPs, never user data."""

import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/Install-BiliClass.ps1'
VERSION = '1.0.0rc164'
pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Native Windows installer')


def make_package(folder, *, bad_hash=False, unsafe=None, missing=False, duplicate=False, version=VERSION):
    files = {'BiliClass.exe': b'fixture exe; not executed',
             '_internal/app/qml/Main.qml': 'Nội dung thử'.encode(),
             'models/vieneu-hf/config.json': b'{}'}
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    if bad_hash:
        hashes['BiliClass.exe'] = '0'*64
    if unsafe:
        hashes[unsafe] = hashlib.sha256(b'escape').hexdigest()
        files[unsafe] = b'escape'
    target = folder/'package.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('app-manifest.json', json.dumps(dict(product='BiliClass', version=version, files=hashes)))
        for name, data in files.items():
            if not (missing and name == 'BiliClass.exe'):
                archive.writestr('BiliClass/'+name, data)
        if duplicate:
            archive.writestr('BILICLASS/BILICLASS.EXE', b'duplicate case')
    return target, files


def invoke(target, package=None, *, version=VERSION, uninstall=False):
    powershell = Path(os.environ['WINDIR'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    args = [str(powershell), '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
            '-File', str(SCRIPT), '-InstallRoot', str(target), '-NoShortcuts']
    if uninstall:
        args += ['-Uninstall']
    else:
        args += ['-PackageZip', str(package), '-ExpectedVersion', version]
    return subprocess.run(args, capture_output=True, encoding='utf-8', errors='replace', timeout=40)


def test_direct_zip_install_and_uninstall_preserves_separate_library(tmp_path):
    package, files = make_package(tmp_path)
    target = tmp_path/'Ứng dụng riêng'
    data = tmp_path/'Thư viện riêng'
    data.mkdir()
    (data/'library.db').write_bytes(b'preserve teacher data')
    result = invoke(target, package)
    assert result.returncode == 0, result.stderr
    for name, payload in files.items():
        assert (target/VERSION/name).read_bytes() == payload
    marker = json.loads((target/'.biliclass-install.json').read_text(encoding='utf-8-sig'))
    assert marker == dict(product='BiliClass', root=str(target), version=VERSION)
    assert 'PROGRESS|100|' in result.stdout
    assert (target/'Uninstall-BiliClass.cmd').is_file()
    assert not list(target.glob('.staging-*'))
    assert invoke(target, package).returncode == 0, 'An identical verified version can repair its launch shortcuts'
    assert not list((target/VERSION).glob('.staging-*'))
    assert invoke(target, uninstall=True).returncode == 0
    assert not target.exists() and (data/'library.db').read_bytes() == b'preserve teacher data'


@pytest.mark.parametrize('old_version,new_version', [
    ('1.0.0rc167', '1.0.0rc169'), ('1.0.0rc155', '1.0.0rc171'),
    ('1.0.0rc155', '1.0.0rc172'), ('1.0.0rc171', '1.0.0rc172')])
def test_upgrade_keeps_old_program_and_teacher_data_key_settings(tmp_path, old_version, new_version):
    from contextlib import closing

    from app.google_translation import KeyStore
    from app.library import Library

    data = tmp_path / 'Thư viện giáo viên'
    with closing(Library(data)) as library:
        lesson = library.create('Bài giảng đã có', 'Toán', 'THPT', '11', [('Mở đầu', 'Nội dung giữ nguyên.')])
        library.set_setting('voice_options', dict(voice='pair:north-female', rate=-2))
        library.set_setting('teacher', 'Giáo viên thử nâng cấp')
    KeyStore(data).add('AIza' + 'a' * 35)
    (data / 'audio').mkdir(exist_ok=True)
    (data / 'audio/teacher.wav').write_bytes(b'teacher audio fixture')
    before = {path.relative_to(data): path.read_bytes() for path in data.rglob('*') if path.is_file()}
    application = tmp_path / 'BiliClass-App'
    for version in (old_version, new_version):
        folder = tmp_path / version
        folder.mkdir()
        package, _ = make_package(folder, version=version)
        result = invoke(application, package, version=version)
        assert result.returncode == 0, result.stderr
    assert (application / old_version / 'BiliClass.exe').is_file()
    assert (application / new_version / 'BiliClass.exe').is_file()
    marker = json.loads((application / '.biliclass-install.json').read_text(encoding='utf-8-sig'))
    assert marker['version'] == new_version
    assert before == {path.relative_to(data): path.read_bytes() for path in data.rglob('*') if path.is_file()}
    with closing(Library(data)) as library:
        assert library.get(lesson['id'])['title'] == 'Bài giảng đã có'
        assert library.setting('voice_options', {})['rate'] == -2


@pytest.mark.parametrize('options', [dict(bad_hash=True), dict(missing=True), dict(unsafe='../escape.txt'),
                                    dict(unsafe='C:/escape.txt'), dict(duplicate=True)])
def test_invalid_zip_cannot_publish_or_leave_partial_extraction(tmp_path, options):
    package, _ = make_package(tmp_path, **options)
    target = tmp_path/'application'
    result = invoke(target, package)
    assert result.returncode != 0
    assert not (target/'.biliclass-install.json').exists()
    assert not (target/VERSION).exists()
    assert not list(target.glob('.staging-*'))
    assert not (tmp_path/'escape.txt').exists()


def test_wrong_version_foreign_folder_and_library_are_preserved(tmp_path):
    package, _ = make_package(tmp_path)
    target = tmp_path/'foreign'
    target.mkdir()
    (target/'keep.txt').write_bytes(b'keep')
    assert invoke(target, package).returncode != 0
    assert (target/'keep.txt').read_bytes() == b'keep'
    data = tmp_path/'library'
    data.mkdir()
    (data/'library.db').write_bytes(b'keep db')
    assert invoke(data, package).returncode != 0
    assert (data/'library.db').read_bytes() == b'keep db'
    assert invoke(tmp_path/'wrong-version', package, version='1.0.0rc165').returncode != 0
    foreign_marker = tmp_path/'foreign-marker'
    foreign_marker.mkdir()
    (foreign_marker/'.biliclass-install.json').write_text(json.dumps(dict(product='Other', root=str(foreign_marker))))
    assert invoke(foreign_marker, package).returncode != 0


def compile_launcher(folder, package):
    metadata = dict(version=VERSION, payload=package.name, sha256=hashlib.sha256(package.read_bytes()).hexdigest())
    info = folder/'release.json'
    info.write_text(json.dumps(metadata), encoding='utf-8')
    executable = folder/'Setup.exe'
    csc = Path(os.environ['WINDIR'])/'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    subprocess.run([str(csc), '/nologo', '/target:winexe', '/codepage:65001',
                    '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll', '/reference:System.Web.Extensions.dll',
                    '/out:'+str(executable), '/resource:'+str(info)+',release.json',
                    '/resource:'+str(SCRIPT)+',Install-BiliClass.ps1', str(ROOT/'scripts/SetupLauncher.cs')],
                   check=True, capture_output=True, timeout=40)
    return executable


def native_failure(executable, target, temporary):
    environment = dict(os.environ, TEMP=str(temporary), TMP=str(temporary))
    result = subprocess.run([str(executable), '--install-test', str(target)], env=environment, timeout=40)
    assert result.returncode != 0
    return (temporary/'BiliClass-setup-error.txt').read_text(encoding='utf-8-sig')


def test_native_launcher_verifies_installs_and_rejects_changed_payload(tmp_path):
    package, files = make_package(tmp_path)
    executable = compile_launcher(tmp_path, package)
    assert subprocess.run([str(executable), '--verify'], timeout=40).returncode == 0
    screenshot = tmp_path/'setup.png'
    assert subprocess.run([str(executable), '--smoke', str(screenshot)], timeout=40).returncode == 0
    assert screenshot.stat().st_size > 1000
    target = tmp_path/'Bản cài từ EXE'
    assert subprocess.run([str(executable), '--install-test', str(target)], timeout=40).returncode == 0
    assert (target/VERSION/'BiliClass.exe').read_bytes() == files['BiliClass.exe']
    assert subprocess.run([str(executable), '--install-test', str(target)], timeout=40).returncode == 0
    (target/VERSION/'BiliClass.exe').write_bytes(b'changed application; preserve')
    error = native_failure(executable, target, tmp_path)
    assert 'tệp không khớp' in error and 'CLIXML' not in error
    assert invoke(target, uninstall=True).returncode == 0
    package.write_bytes(package.read_bytes()+b'changed')
    assert subprocess.run([str(executable), '--verify'], timeout=40).returncode != 0
    occupied = tmp_path/'Tài liệu khác'
    occupied.mkdir()
    original = occupied/'Bài giảng của tôi.pptx'
    original.write_bytes(b'teacher source; preserve')
    error = native_failure(executable, occupied, tmp_path)
    assert 'Thư mục này đã có dữ liệu' in error and 'thư mục mới' in error
    assert str(occupied) in error and 'CLIXML' not in error and 'schemas.microsoft.com' not in error
    assert 'Gói dữ liệu chưa đầy đủ' not in error, 'Check the destination before hashing the large ZIP'
    assert original.read_bytes() == b'teacher source; preserve'
    assert sorted(p.name for p in occupied.iterdir()) == [original.name]


def test_native_worker_error_preserves_vietnamese_without_xml_or_progress(tmp_path):
    package, _ = make_package(tmp_path, bad_hash=True)
    executable = compile_launcher(tmp_path, package)
    target = tmp_path/'Ứng dụng mới'
    error = native_failure(executable, target, tmp_path)
    assert 'Tệp trong bộ cài bị thiếu hoặc thay đổi' in error and 'BiliClass.exe' in error
    assert all(text not in error for text in ('CLIXML', 'schemas.microsoft.com', 'Preparing modules', 'BILICLASS_ERROR|'))
    assert not (target/VERSION).exists() and not (target/'.biliclass-install.json').exists()
    assert not list(target.glob('.staging-*'))
    assert SCRIPT.read_bytes().startswith(b'\xef\xbb\xbf'), 'Windows PowerShell 5.1 must read Vietnamese script messages as UTF-8'


def test_launcher_refresh_requires_clean_unchanged_application_source(tmp_path):
    from scripts.package_installer import verify_source

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=tmp_path, text=True).strip()

    git('init', '-q')
    git('config', 'user.email', 'fixture@example.invalid')
    git('config', 'user.name', 'Installer fixture')
    (tmp_path/'app').mkdir()
    (tmp_path/'app/__init__.py').write_text('version = 164\n')
    (tmp_path/'requirements-lock.txt').write_text('fixture == 1\n')
    git('add', '.')
    git('commit', '-qm', 'verified application')
    application = git('rev-parse', 'HEAD')
    (tmp_path/'SetupLauncher.cs').write_text('// setup-only change\n')
    git('add', '.')
    git('commit', '-qm', 'setup-only change')
    with pytest.raises(ValueError, match='current source commit'):
        verify_source(tmp_path, application)
    assert verify_source(tmp_path, application, reuse_application=True) == git('rev-parse', 'HEAD')
    (tmp_path/'requirements-lock.txt').write_text('fixture == 2\n')
    git('add', '.')
    git('commit', '-qm', 'different native dependency')
    with pytest.raises(ValueError, match='application/runtime source changed'):
        verify_source(tmp_path, application, reuse_application=True)
    (tmp_path/'uncommitted.txt').write_text('not verified')
    with pytest.raises(ValueError, match='Commit verified'):
        verify_source(tmp_path, application, reuse_application=True)
