"""Readable Windows file suggestions; native Save dialogs decide overwrites."""

import re
from pathlib import Path


def safe_name(text, limit=100):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(text))[:limit].strip(' .') or 'BiliClass'
    if re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', name, re.I):
        name = '_' + name
    return name


def suggestion(folder, title, suffix, extension):
    name = safe_name(title) + (' (' + safe_name(suffix, 80) + ')' if suffix else '')
    target = Path(folder) / (name + '.' + extension)
    index = 2
    while target.exists():
        target = Path(folder) / f'{name} ({index}).{extension}'
        index += 1
    return target


def presentation_title(lesson):
    title = str(lesson.get('title') or '').strip()
    return title or Path(lesson.get('source', {}).get('name') or '').stem or 'Bài giảng'


def presentation_suffix(lesson, with_voice=False):
    """Describe the actual conversion and audio languages, across all downloads."""
    base = ('Nguyên bản' if lesson.get('voice_only') else
            'Tiếng Anh' if lesson.get('conversion_format') == 'english_only' else 'Song ngu VI-EN')
    record = lesson.get('narration') or {}
    language = {'en': 'EN', 'vi': 'VI', 'both': 'VI-EN'}.get(record.get('mode'))
    return base + (f' - Voice {language}' if with_voice and language else '')
