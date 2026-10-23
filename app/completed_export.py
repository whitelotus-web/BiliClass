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
from .narration_timing import reading_gap


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
        gap_ms = reading_gap(directory) if with_voice else 0
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
        current_key = 'completed_export:' + lesson['id'] + ':current:' + origin_key
        previous = library.setting(key, {})
        current = library.setting(current_key, {})
        if (not with_voice and isinstance(current, dict) and isinstance(current.get('record_id'), str)
                and current['record_id'] != 'no_voice'
                and current.get('source_sha256') == preview.get('sha256')
                and current.get('revision') == lesson['revision']
                and all(current.get(name) == value for name, value in origin.items())):
            try:
                path = Path(current['path'])
                if path.is_file() and digest(path) == current.get('sha256'):
                    return {**current, 'phase': 'saved', 'reused': True, 'kept_voiced_product': True}
            except (KeyError, TypeError, OSError):
                pass
        if (isinstance(previous, dict) and previous.get('source_sha256') == preview.get('sha256')
                and previous.get('revision') == lesson['revision'] and previous.get('audio_sha256') == audio_sha256
                and previous.get('join_gap_ms') == gap_ms
                and (not with_voice or previous.get('join_gap_version') == 2)
                and all(previous.get(key) == value for key, value in origin.items())):
            try:
                path = Path(previous['path'])
                if path.is_file() and digest(path) == previous.get('sha256'):
                    try:
                        library.set_setting(current_key, previous)
                    except (OSError, sqlite3.Error):
                        pass
                    return {**previous, 'phase': 'saved', 'reused': True}
            except (KeyError, TypeError, OSError):
                pass
        # One automatic product evolves from converted to voiced. Manual Save As
        # keeps its descriptive voice suffix and remains a separate user action.
        suffix = presentation_suffix(lesson, False)
        owned, kept = None, False
        if with_voice:
            candidates = [current, previous,
                          library.setting('completed_export:' + lesson['id'] + ':no_voice:' + origin_key, {})]
            for saved in candidates:
                if (not isinstance(saved, dict) or saved.get('lesson_id') != lesson['id']
                        or not all(saved.get(name) == value for name, value in origin.items())):
                    continue
                try:
                    path = Path(saved['path']).resolve()
                    if (path.suffix.lower() != '.pptx' or path.parent not in {folder.resolve(), fallback.resolve()}
                            or path == (folder / (title + '.pptx')).resolve()
                            or path == Path(preview['path']).resolve()):
                        continue
                    if path.is_file() and digest(path) == saved.get('sha256'):
                        owned = path, saved['sha256']
                        break
                    kept = kept or path.is_file()
                except (KeyError, TypeError, OSError):
                    continue
        failure = None
        for chosen in dict.fromkeys((folder, fallback)):
            try:
                if chosen == fallback:
                    fallback.mkdir(exist_ok=True)
                updated, report = False, {}
                if owned and owned[0].parent == chosen.resolve():
                    path = owned[0]
                    try:
                        save_presentation(lesson, preview, directory, path, with_voice=with_voice, report=report,
                                          expected_sha256=owned[1], managed_output=chosen == fallback, gap_ms=gap_ms)
                        updated = True
                    except (FileExistsError, PermissionError):
                        kept = True  # A teacher edit or an open presentation gets a separate new output.
                for _ in range(20):
                    if updated:
                        break
                    path = suggestion(chosen, title, suffix, 'pptx')
                    try:
                        report = {}
                        save_presentation(lesson, preview, directory, path, with_voice=with_voice, report=report,
                                          overwrite=False, managed_output=chosen == fallback, gap_ms=gap_ms)
                        break
                    except FileExistsError:
                        continue  # Another window won this exact filename; never replace it.
                else:
                    raise OSError('Chưa chọn được tên tệp mới để tự lưu.')
                value = {**origin, 'lesson_id': lesson['id'], 'record_id': identity, 'revision': lesson['revision'],
                         'source_sha256': preview['sha256'], 'path': str(path), 'sha256': digest(path),
                         'audio_sha256': audio_sha256, 'fallback': chosen == fallback, 'coverage': report,
                         'updated': updated, 'previous_kept': kept}
                value['join_gap_ms'] = gap_ms
                value['join_gap_version'] = 2
                try:
                    library.set_setting(key, value)
                    library.set_setting(current_key, value)
                except (OSError, sqlite3.Error):
                    pass  # The finished file is valid even if saving the shortcut fails.
                return {**value, 'phase': 'saved', 'reused': False}
            except OSError as exc:
                failure = exc
        raise OSError('Chưa ghi được bản PowerPoint tự lưu. Bài và giọng vẫn trong Thư viện; dùng Tải PowerPoint để chọn nơi khác.') from failure
