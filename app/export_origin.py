"""Local-only export locations; paths never enter portable lesson content."""

from pathlib import Path

from .download_names import presentation_title


def remember_source(library, path, digest):
    path = Path(path).resolve()
    if digest and path.is_file() and not path.is_relative_to(library.directory.resolve()):
        key = 'export_origin_source:' + digest
        origin = {'folder': str(path.parent), 'name': path.name}
        if library.setting(key, {}) != origin:
            library.set_setting(key, origin)


def bind_lesson(library, lesson, digest):
    origin = library.setting('export_origin_source:' + digest, {}) if digest else {}
    if (isinstance(origin, dict) and origin.get('folder')
            and library.setting('export_origin_lesson:' + lesson['id'], {}) != origin):
        library.set_setting('export_origin_lesson:' + lesson['id'], origin)


def destination(library, lesson, fallback):
    origin = library.setting('export_origin_lesson:' + lesson.get('id', ''), {})
    if not isinstance(origin, dict) or not origin.get('folder'):
        digest = ((lesson.get('external_deck') or {}).get('original_source_sha256')
                  or (lesson.get('source') or {}).get('sha256', ''))
        origin = library.setting('export_origin_source:' + digest, {}) if digest else {}
    title = presentation_title(lesson)
    if isinstance(origin, dict) and isinstance(origin.get('name'), str):
        title = Path(origin['name']).stem or title
    try:
        folder = Path(origin['folder'])
        if folder.is_absolute() and folder.is_dir() and not folder.resolve().is_relative_to(library.directory.resolve()):
            return folder, title
    except (KeyError, TypeError, OSError, ValueError):
        pass
    return Path(fallback), title
