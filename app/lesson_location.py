"""Find an existing lesson file without exporting, synthesizing or changing it."""

import json
import os
from contextlib import closing
from pathlib import Path

from .lesson_narration import records, variant_id
from .library import Library


def presentation_location(directory, identity):
    with closing(Library.read_only(directory)) as library:
        lesson = library.get(identity)
        preferred = variant_id(lesson.get('narration')) or 'no_voice'
        allowed = {'no_voice', *records(lesson)}
        candidates = []
        for row in library.db.execute('SELECT value FROM settings WHERE key LIKE ?',
                                      ('completed_export:' + identity + ':%',)):
            try:
                saved = json.loads(row[0])
                if (not isinstance(saved, dict) or saved.get('lesson_id') != identity
                        or saved.get('record_id') not in allowed or not isinstance(saved.get('path'), str)):
                    continue
                path = Path(saved['path'])
                if not path.is_absolute() or path.suffix.lower() != '.pptx' or not path.is_file():
                    continue
                revision = saved.get('revision', 0)
                if type(revision) is not int or revision > lesson['revision']:
                    continue
                candidates.append(((saved['record_id'] == preferred, revision, path.stat().st_mtime_ns), path))
            except (ValueError, OSError, TypeError):
                continue
        if candidates:
            # Browsing must also find a teacher's manually edited saved file;
            # it does not approve that file or replace the library's content.
            return max(candidates, key=lambda item: item[0])[1].resolve()
        filename = (lesson.get('source') or {}).get('file', '')
        if (isinstance(filename, str) and filename and Path(filename).name == filename
                and ':' not in filename and Path(filename).suffix.lower() == '.pptx'):
            folder = (Path(directory) / 'sources').resolve()
            path = (folder / filename).resolve()
            if path.is_relative_to(folder) and path.is_file():
                return path
    raise ValueError('Không tìm thấy file bài giảng. File có thể đã được chuyển hoặc xóa khỏi vị trí lưu.')


def select_in_explorer(path):
    """Select the exact Unicode path through the Windows shell, without command text."""
    if os.name != 'nt':
        return False
    import pythoncom
    from win32com.shell import shell

    pythoncom.CoInitialize()
    try:
        identity = shell.SHParseDisplayName(str(path), 0)[0]
        shell.SHOpenFolderAndSelectItems(identity, [], 0)
        return True
    except (OSError, pythoncom.com_error):
        return False
    finally:
        pythoncom.CoUninitialize()
