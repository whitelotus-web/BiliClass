"""Automatically publish a finished narrated PPTX without overwriting teacher files."""

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .download_names import presentation_suffix, suggestion
from .export_origin import destination
from .lesson_files import save_presentation
from .lesson_narration import audio_status, records, variant_id
from .library import Library, RevisionConflict


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_finished(directory, selected, preview):
    """The narration is already complete; never synthesize or change the lesson."""
    return _save_product(directory, selected, preview, with_voice=True)


def save_converted(directory, selected, preview):
    return _save_product(directory, selected, preview, with_voice=False)


def _save_product(directory, selected, preview, *, with_voice):
    directory = Path(directory).resolve()
    identity = variant_id(selected.get('narration')) if with_voice else 'no_voice'
    if not identity:
        raise ValueError('Chưa có bản giọng hoàn tất để tự lưu PowerPoint.')
    with closing(Library(directory)) as library:
        lesson = library.get(selected['id'])
        if lesson['revision'] != selected['revision'] or lesson.get('source') != selected.get('source'):
            raise RevisionConflict('Bài giảng vừa thay đổi. Giọng đã tạo vẫn được giữ trong Thư viện.')
        if with_voice and identity not in records(lesson):
            raise RevisionConflict('Bản giọng vừa thay đổi. Mở bài để chọn bản hoàn tất cần lưu.')
        if with_voice:
            lesson['narration'] = records(lesson)[identity]
        if with_voice and not audio_status(lesson, directory).get('ready'):
            raise ValueError('Giọng đọc chưa đủ để tự lưu. Các đoạn đã tạo vẫn được giữ trong Thư viện.')
        keys = sorted({key for values in lesson['narration']['keys'].values() for key in values}) if with_voice else []
        audio_sha256 = hashlib.sha256(json.dumps([(key, digest(directory/'audio'/(key+'.wav')))
                                                 for key in keys]).encode()).hexdigest()
        fallback = directory / 'exports'
        folder, title = destination(library, lesson, fallback)
        origin = {'origin_folder': str(folder.resolve()), 'origin_name': title}
        origin_key = hashlib.sha256(json.dumps(origin, sort_keys=True).encode()).hexdigest()
        key = 'completed_export:' + lesson['id'] + ':' + identity + ':' + origin_key
        previous = library.setting(key, {})
        if (isinstance(previous, dict) and previous.get('source_sha256') == preview.get('sha256')
                and previous.get('revision') == lesson['revision'] and previous.get('audio_sha256') == audio_sha256
                and all(previous.get(key) == value for key, value in origin.items())):
            try:
                path = Path(previous['path'])
                if path.is_file() and digest(path) == previous.get('sha256'):
                    return {**previous, 'phase': 'saved', 'reused': True}
            except (KeyError, TypeError, OSError):
                pass
        suffix = presentation_suffix(lesson, with_voice)
        failure = None
        for chosen in dict.fromkeys((folder, fallback)):
            try:
                if chosen == fallback:
                    fallback.mkdir(exist_ok=True)
                for _ in range(20):
                    path = suggestion(chosen, title, suffix, 'pptx')
                    try:
                        report = {}
                        save_presentation(lesson, preview, directory, path, with_voice=with_voice, report=report,
                                          overwrite=False, managed_output=chosen == fallback)
                        break
                    except FileExistsError:
                        continue  # Another window won this exact filename; never replace it.
                else:
                    raise OSError('Chưa chọn được tên tệp mới để tự lưu.')
                value = {**origin, 'lesson_id': lesson['id'], 'record_id': identity, 'revision': lesson['revision'],
                         'source_sha256': preview['sha256'], 'path': str(path), 'sha256': digest(path),
                         'audio_sha256': audio_sha256, 'fallback': chosen == fallback, 'coverage': report}
                try:
                    library.set_setting(key, value)
                except (OSError, sqlite3.Error):
                    pass  # The finished file is valid even if saving the shortcut fails.
                return {**value, 'phase': 'saved', 'reused': False}
            except OSError as exc:
                failure = exc
        raise OSError('Chưa ghi được bản PowerPoint tự lưu. Bài và giọng vẫn trong Thư viện; dùng Tải PowerPoint để chọn nơi khác.') from failure
