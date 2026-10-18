import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('release_package', Path(__file__).parents[1]/'scripts/package_release.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def test_bundle_walk_includes_nested_models_and_hashes_real_contents(tmp_path):
    for name in ('BiliClass.exe', 'models/ocr-vi-en-v2/model.onnx', '_internal/app/qml/Main.qml'):
        target = tmp_path/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(name.encode())
    paths = list(package.bundle_files(tmp_path))
    assert {p.relative_to(tmp_path).as_posix() for p in paths} == {'BiliClass.exe', 'models/ocr-vi-en-v2/model.onnx', '_internal/app/qml/Main.qml'}
    assert len(package.file_sha256(paths[0])) == 64


def test_source_and_package_versions_match():
    import tomllib

    from app import __version__
    root = Path(__file__).parents[1]
    assert tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']['version'] == __version__


def test_native_ocr_package_models_are_not_mistaken_for_optional_downloads():
    assert package.distributable(Path('_internal/rapidocr/models/recognizer.onnx'))
    assert package.distributable(Path('models/ocr-vi-en-v2/recognizer.onnx'))
    assert package.distributable(Path('models/vieneu-hf/model.gguf'))
    assert not package.distributable(Path('models/unused-legacy-model/model.bin'))
