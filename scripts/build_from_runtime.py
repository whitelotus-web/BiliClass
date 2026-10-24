"""Build/package against an explicitly selected, verified previous release folder.

Run with the project virtual environment. The optional --english-model flag adds the pinned, verified Kokoro runtime.
Other native dependency/model changes require scripts/build.ps1. All app code is rebuilt.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path, PurePosixPath


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_baseline(folder):
    manifest_path = folder / 'app-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    if manifest.get('product') != 'BiliClass' or not isinstance(manifest.get('files'), dict):
        raise ValueError('Select a complete previous BiliClass release folder with its manifest.')
    for index, (name, checksum) in enumerate(manifest['files'].items(), 1):
        relative = PurePosixPath(name)
        path = folder / 'BiliClass' / name
        if (relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name
                or not path.resolve().is_relative_to((folder / 'BiliClass').resolve())
                or digest(path) != checksum):
            raise ValueError('Baseline verification failed: ' + name)
        if index % 1000 == 0:
            print('Verified baseline runtime', index, flush=True)
    return manifest, digest(manifest_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--english-model', type=Path, help='Explicitly add the pinned Kokoro v1.0 CPU runtime/model')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output, baseline = args.output.resolve(), args.baseline.resolve(strict=True)
    if not output.is_relative_to(root) or output == root or output.exists():
        raise ValueError('Choose a new output folder within the project.')
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=root, text=True)
    if status.strip():
        raise ValueError('Commit verified source changes before building.')
    sys.path.insert(0, str(root))
    from app import __version__

    version = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    if version != __version__:
        raise ValueError('Application and package versions differ.')
    manifest, manifest_sha = verify_baseline(baseline)
    output.mkdir(parents=True)
    work = output / '.build-work'
    work.mkdir()
    config = dict(root=str(root), baseline_exe=str(baseline / 'BiliClass/BiliClass.exe'),
                  work=str(work))
    if args.english_model:
        import importlib.metadata
        import importlib.util

        if importlib.metadata.version('sherpa-onnx') != '1.13.8':
            raise ValueError('This milestone requires the tested sherpa-onnx 1.13.8 runtime.')
        config['english_runtime'] = str(Path(importlib.util.find_spec('sherpa_onnx').origin).parent)
    config_path = work / 'build-config.json'
    config_path.write_text(json.dumps(config), encoding='utf-8')
    environment = dict(os.environ, BILICLASS_BUILD_CONFIG=str(config_path))
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--workpath', str(work),
                    '--distpath', str(work / 'dist'), str(root / 'scripts/build_runtime.spec')],
                   cwd=root, env=environment, check=True)
    bundle = output / 'BiliClass'
    bundle.mkdir()
    for name in manifest['files']:
        if (name in {'BiliClass.exe', 'BUILD_INFO.json', 'OCR_BUILD_INFO.json'}
                or name.startswith(('_internal/app/qml/', '_internal/app/assets/', '_internal/app/student_web/', '_internal/app/resources/'))):
            continue
        source, target = baseline / 'BiliClass' / name, bundle / name
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)
    shutil.copy2(work / 'build_runtime/BiliClass.exe', bundle / 'BiliClass.exe')
    if os.name == 'nt':
        import win32api

        resource = '\\StringFileInfo\\042a04b0\\'
        if (win32api.GetFileVersionInfo(str(bundle / 'BiliClass.exe'), resource + 'ProductVersion') != version
                or win32api.GetFileVersionInfo(str(bundle / 'BiliClass.exe'), resource + 'ProductName') != 'BiliClass'
                or 'Nguyễn Diệu Linh' not in win32api.GetFileVersionInfo(
                    str(bundle / 'BiliClass.exe'), resource + 'LegalCopyright')):
            raise ValueError('Executable Windows Details resource does not match this release.')
    for folder in ('qml', 'assets', 'student_web', 'resources'):
        shutil.copytree(root / 'app' / folder, bundle / '_internal/app' / folder)
    added = {}
    if args.english_model:
        model = args.english_model.resolve(strict=True)
        expected = {'model.onnx': 'b40f62b166ac8164b0627ef48a0b358eda0985e272fb03ef5252e7206305da11',
                    'voices.bin': '1c5a5b983d3d50d8586d437a51f3faa2da7919ce76a013c081e65671a3447c29'}
        if any(digest(model/name) != checksum for name, checksum in expected.items()):
            raise ValueError('The English model does not match the verified Kokoro v1.0 artifacts.')
        runtime = Path(config['english_runtime'])
        for source, target in ((model, bundle/'models/kokoro-multi-lang-v1_0'),
                               (runtime, bundle/'_internal/sherpa_onnx')):
            for file in sorted(source.rglob('*')):
                if not file.is_file() or '__pycache__' in file.parts or file.suffix in {'.pyc', '.lib'}:
                    continue
                destination = target/file.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, destination)
                added[destination.relative_to(bundle).as_posix()] = digest(destination)
        for package in ('sherpa-onnx', 'sherpa-onnx-core'):
            distribution = importlib.metadata.distribution(package)
            target = bundle/'licenses'/(package+'-'+distribution.version)
            target.mkdir(parents=True, exist_ok=True)
            (target/'METADATA.txt').write_text(distribution.read_text('METADATA'), encoding='utf-8')
        shutil.copy2(root/'docs/THIRD_PARTY.md', bundle/'THIRD_PARTY.md')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    info = dict(product='BiliClass', version=version, source_commit=commit,
                exe_sha256=digest(bundle / 'BiliClass.exe'),
                runtime_baseline_version=manifest['version'], runtime_manifest_sha256=manifest_sha,
                build_mode='all app modules rebuilt; verified dependency/model runtime reused',
                added_english_runtime=added, python=sys.version, pyinstaller=subprocess.check_output(
                    [sys.executable, '-m', 'PyInstaller', '--version'], text=True).strip())
    (bundle / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
    if (baseline / 'BiliClass/OCR_BUILD_INFO.json').exists():
        ocr = json.loads((baseline / 'BiliClass/OCR_BUILD_INFO.json').read_text(encoding='utf-8-sig'))
        ocr['source_commit'] = commit
        (bundle / 'OCR_BUILD_INFO.json').write_text(json.dumps(ocr, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, str(root / 'scripts/package_release.py'), str(output)], cwd=root, check=True)
    packaged = json.loads((output / 'app-manifest.json').read_text(encoding='utf-8'))
    suffix = 'RC' + version.split('rc')[1] if 'rc' in version else version
    asset = output / f'BiliClass-{suffix}-Windows.zip'
    entries = ['app-manifest.json', 'Setup.cmd', 'Install-BiliClass.ps1', 'HUONG_DAN.md']
    entries += ['BiliClass/' + name for name in sorted(packaged['files'])]
    with zipfile.ZipFile(asset, 'w', zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for name in entries:
            archive.write(output / name, name)
    from app.updater import MAX_ARCHIVE, _safe_entries

    if asset.stat().st_size > MAX_ARCHIVE:
        raise ValueError('Package exceeds updater archive limit.')
    with zipfile.ZipFile(asset) as archive:
        _safe_entries(archive, version)
        for name, checksum in packaged['files'].items():
            with archive.open('BiliClass/' + name) as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != checksum:
                    raise ValueError('ZIP content verification failed: ' + name)
    checksum = digest(asset)
    asset.with_suffix('.zip.sha256').write_text(checksum + '  ' + asset.name + '\n', encoding='ascii')
    (output / 'build-result.json').write_text(json.dumps(dict(info, archive=str(asset), sha256=checksum,
        bytes=asset.stat().st_size, files=len(entries), zip_verified=True), indent=2), encoding='utf-8')
    print(json.dumps(dict(version=version, source_commit=commit, archive=str(asset), sha256=checksum)), flush=True)


if __name__ == '__main__':
    main()
