"""Local-only export locations; paths never enter portable lesson content."""

import hashlib
import json
from pathlib import Path

from .download_names import presentation_title


def is_automatic_product(library, lesson, path, digest=None):
    """An unchanged automatic B keeps its link to A when imported for voice."""
    path = Path(path).resolve()
    for row in library.db.execute('SELECT value FROM settings WHERE key LIKE ?',
                                  ('completed_export:' + lesson['id'] + ':%',)):
        try:
            saved = json.loads(row[0])
            if (isinstance(saved, dict) and saved.get('lesson_id') == lesson['id']
                    and Path(saved['path']).resolve() == path):
                if digest is None:
                    with path.open('rb') as source:
                        digest = hashlib.file_digest(source, 'sha256').hexdigest()
                if digest == saved.get('sha256'):
                    return True
        except (ValueError, KeyError, TypeError, OSError):
            continue
    return False


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
