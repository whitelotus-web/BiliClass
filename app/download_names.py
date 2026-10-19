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


def presentation_suffix(lesson, with_voice=False):
    """One product name for the workspace, library and files inside ZIPs."""
    if with_voice and (record := lesson.get('narration')):
        from . import speech

        language = {'en': 'Anh', 'vi': 'Việt', 'both': 'Việt–Anh'}.get(record.get('mode'), '')
        voice = next((v.get('name', '').split(' · ')[0] for v in (*speech.VIENEU_VOICES, *speech.PAIRS)
                      if v['id'] == record.get('voice')), record.get('voice', '').split(':')[-1])
        rate = record.get('rate', 0)
        speed = round(speech._SPEEDS[rate + 3] * 100) if type(rate) is int and -3 <= rate <= 3 else 100
        return f'Có giọng {language} · {voice} · {speed}%'
    if lesson.get('voice_only'):
        return 'Nguyên bản · Không giọng'
    return ('Tiếng Anh' if lesson.get('conversion_format') == 'english_only' else 'Song ngữ Việt–Anh')
