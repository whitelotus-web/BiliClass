"""Recompile every app module while reusing a hash-verified dependency runtime."""
import importlib.util
import json
import os
import sys
from pathlib import Path

from PyInstaller.archive.readers import CArchiveReader
from PyInstaller.config import CONF

config = json.loads(Path(os.environ['BILICLASS_BUILD_CONFIG']).read_text(encoding='utf-8'))
root = Path(config['root'])
sys.path.insert(0, str(root))
from scripts.windows_version_info import version_info
import tomllib
release_version = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
archive = CArchiveReader(config['baseline_exe'])
reader = archive.open_embedded_archive('PYZ.pyz')
pure, codes = [], {}
for name, item in reader.toc.items():
    if name == 'app' or name.startswith('app.'):
        continue
    kind = item[0]
    filename = ('-' if kind == 3 else str(Path('baseline') / name.replace('.', '/') /
                '__init__.py') if kind == 1 else str(Path('baseline') / (name.replace('.', '/') + '.py')))
    pure.append((name, filename, 'PYMODULE'))
    if kind != 3:
        codes[name] = reader.extract(name)
for path in sorted((root / 'app').glob('*.py')):
    name = 'app' if path.stem == '__init__' else 'app.' + path.stem
    pure.append((name, str(path), 'PYMODULE'))
    codes[name] = compile(path.read_bytes(), str(path), 'exec')
if config.get('english_runtime'):
    # Explicit addition to the verified baseline: the pinned local English
    # dependency is included as source plus its own native runtime folder.
    source = Path(config['english_runtime'])
    for path in sorted(source.rglob('*.py')):
        relative = path.relative_to(source).with_suffix('')
        parts = relative.parts[:-1] if relative.name == '__init__' else relative.parts
        name = '.'.join(('sherpa_onnx', *parts))
        pure.append((name, str(path), 'PYMODULE'))
        codes[name] = compile(path.read_bytes(), str(path), 'exec')
    pure.append(('sherpa_onnx.lib', '-', 'PYMODULE'))
hooks = []
hook_folder = Path(config['work']) / 'runtime-hooks'
hook_folder.mkdir(parents=True, exist_ok=True)
for name, item in archive.toc.items():
    if name.startswith('pyi_rth_'):
        path = hook_folder / (name + '.pyc')
        path.write_bytes(importlib.util.MAGIC_NUMBER + bytes(12) + archive.extract(name))
        hooks.append((name, str(path), 'PYSOURCE'))
hooks.append(('app_entry', str(root / 'scripts/app_entry.py'), 'PYSOURCE'))
CONF.setdefault('code_cache', {})[id(pure)] = codes
pyz = PYZ(pure)
exe = EXE(pyz, hooks, [], exclude_binaries=True, name='BiliClass',
          icon=str(root / 'app/assets/brand/biliclass.ico'), console=False, upx=False,
          version=version_info(release_version),
          disable_windowed_traceback=False)
