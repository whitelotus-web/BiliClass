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


def make_package(folder, *, bad_hash=False, unsafe=None, missing=False, duplicate=False):
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
        archive.writestr('app-manifest.json', json.dumps(dict(product='BiliClass', version=VERSION, files=hashes)))
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
    assert invoke(target, package).returncode != 0, 'Never nest another staging folder in an existing version'
    assert not list((target/VERSION).glob('.staging-*'))
    assert invoke(target, uninstall=True).returncode == 0
    assert not target.exists() and (data/'library.db').read_bytes() == b'preserve teacher data'


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


def test_native_launcher_verifies_installs_and_rejects_changed_payload(tmp_path):
    package, files = make_package(tmp_path)
    metadata = dict(version=VERSION, payload=package.name, sha256=hashlib.sha256(package.read_bytes()).hexdigest())
    info = tmp_path/'release.json'
    info.write_text(json.dumps(metadata), encoding='utf-8')
    executable = tmp_path/'Setup.exe'
    csc = Path(os.environ['WINDIR'])/'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    subprocess.run([str(csc), '/nologo', '/target:winexe', '/codepage:65001',
                    '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll', '/reference:System.Web.Extensions.dll',
                    '/out:'+str(executable), '/resource:'+str(info)+',release.json',
                    '/resource:'+str(SCRIPT)+',Install-BiliClass.ps1', str(ROOT/'scripts/SetupLauncher.cs')],
                   check=True, capture_output=True, timeout=40)
    assert subprocess.run([str(executable), '--verify'], timeout=40).returncode == 0
    screenshot = tmp_path/'setup.png'
    assert subprocess.run([str(executable), '--smoke', str(screenshot)], timeout=40).returncode == 0
    assert screenshot.stat().st_size > 1000
    target = tmp_path/'Bản cài từ EXE'
    assert subprocess.run([str(executable), '--install-test', str(target)], timeout=40).returncode == 0
    assert (target/VERSION/'BiliClass.exe').read_bytes() == files['BiliClass.exe']
    assert invoke(target, uninstall=True).returncode == 0
    package.write_bytes(package.read_bytes()+b'changed')
    assert subprocess.run([str(executable), '--verify'], timeout=40).returncode != 0
