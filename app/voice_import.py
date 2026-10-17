"""Import an existing PowerPoint for narration without translation or redesign."""

import json
from contextlib import closing
from pathlib import Path

from .chatgpt_handoff import external_preview, inspect_returned_deck
from .library import Library


def import_presentation(directory, path):
    path = Path(path)
    inspection = inspect_returned_deck(path)
    if not any(unit.get('vi', '').strip() or unit.get('en', '').strip() for unit in inspection['profile']['units']):
        raise ValueError('PowerPoint chưa có chữ để đọc. Bổ sung lời đọc trong slide hoặc ghi chú Việt/Anh rồi chọn lại.')
    with closing(Library(directory)) as library:
        source = library.store_source(path)
        # Reuse an earlier import of the exact file, including its voice variants.
        for row in library.db.execute('SELECT content FROM lessons'):
            lesson = json.loads(row[0])
            if lesson.get('voice_only') and (lesson.get('source') or {}).get('sha256') == source['sha256'] and not lesson.get('deleted_at'):
                return lesson, external_preview(lesson, directory)
        config = {'title': path.stem, 'subject': 'Bài giảng có sẵn', 'education_level': '', 'grade': '',
                  'level': 4, 'layout': 'split_view', 'style': 'source', 'preset': 'standard', 'mode': 'preserve'}
        lesson = library.create_external_lesson(config, source, inspection)
        lesson['voice_only'] = True
        lesson['external_deck']['provider'] = 'voice_import'
        library._write(lesson)
        return lesson, external_preview(lesson, directory)
