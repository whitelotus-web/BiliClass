"""Atomic PowerPoint/ZIP export from immutable lesson snapshots, on a worker."""

import os
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

from .download_names import presentation_suffix, suggestion
from .lesson_files import save_presentation
from .lesson_narration import audio_status, variant_title
from .library import Library


def export(directory, identities, destination, with_voice=True, cancel=None):
    identities = list(dict.fromkeys(identities))
    if not identities or len(identities) > 10000:
        raise ValueError('Chọn bài giảng cần tải.')
    target = Path(destination).resolve()
    if target.suffix.lower() != ('.zip' if len(identities) > 1 else '.pptx'):
        raise ValueError('Chọn đúng định dạng PowerPoint cho một bài hoặc ZIP cho nhiều bài.')
    if target.is_relative_to(Path(directory).resolve()) or not target.parent.is_dir():
        raise ValueError('Chọn thư mục lưu ngoài dữ liệu BiliClass, ví dụ Downloads.')
    with closing(Library.read_only(directory)) as library:
        lessons = [library.get(identity) for identity in identities]
        terms = library.glossary()
    # Temporary workspace is owned by this export and stays inside the chosen
    # destination parent. Nothing in the teacher's source/library is removed.
    with tempfile.TemporaryDirectory(prefix='.biliclass-download-', dir=target.parent) as temporary:
        work = Path(temporary).resolve()
        if not work.is_relative_to(target.parent):
            raise ValueError('Không tạo được thư mục tải tạm.')
        notes, paths, voiced, warnings = [], [], 0, []
        for index, lesson in enumerate(lessons, 1):
            if cancel and cancel.is_set():
                raise InterruptedError('Đã dừng tải. Tệp đích cũ được giữ nguyên.')
            if lesson.get('external_deck'):
                from .chatgpt_handoff import external_preview
                preview = external_preview(lesson, directory)
            else:
                from .quick_conversion import build_preview
                preview = build_preview(lesson, directory, terms=[r for r in terms if r['subject'] == lesson['subject']])
            voice = bool(with_voice and audio_status(lesson, directory).get('ready'))
            label = variant_title(lesson['narration']) if voice else 'Không kèm giọng'
            path = suggestion(work, f'{index:03d} - ' + lesson['title'], presentation_suffix(lesson, voice), 'pptx')
            coverage = {}
            save_presentation(lesson, preview, directory, path, with_voice=voice, report=coverage)
            paths.append(path)
            voiced += int(voice)
            notes.append(path.name + '\n  Giọng: ' + label + '\n  Cần kiểm tra nội dung và bố cục trước khi dạy.\n')
            if voice:
                from .presentation_audio import coverage_message
                notes.append(coverage_message(coverage) + '\n')
                if coverage.get('unplaced_pages') or coverage.get('restricted_pages'):
                    warnings.append(coverage_message(coverage))
        if cancel and cancel.is_set():
            raise InterruptedError('Đã dừng tải. Tệp đích cũ được giữ nguyên.')
        if len(paths) == 1:
            pending = paths[0]
        else:
            pending = work / 'BiliClass.zip'
            with zipfile.ZipFile(pending, 'w', compression=zipfile.ZIP_STORED) as archive:
                for path in paths:
                    archive.write(path, path.name)
                archive.writestr('HUONG_DAN.txt', 'BiliClass - Các bài giảng đã chọn\n\n' + '\n'.join(notes))
        os.replace(pending, target)
    return {'path': str(target), 'count': len(lessons), 'voiced': voiced, 'warnings': warnings}
