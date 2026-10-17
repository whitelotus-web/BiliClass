"""Export the selected verified voice as per-slide WAVs without a model call."""

import json
import os
import tempfile
import zipfile
from pathlib import Path

from . import speech
from .lesson_narration import MODES, audio_status, valid_key
from .narration_script import segments as narration_segments
from .powerpoint import slide_for_locator
from .presentation_audio import joined_wav, paired_keys
from .slide_speech import speech_chunks


def export_audio(lesson, directory, destination):
    if not audio_status(lesson, directory).get('ready'):
        raise ValueError('Tạo đủ bản giọng đã chọn trước khi tải audio.')
    target = Path(destination).resolve()
    if target.suffix.lower() != '.zip' or target.is_relative_to(Path(directory).resolve()):
        raise ValueError('Chọn tệp .zip ở ngoài thư viện BiliClass.')
    if not target.parent.is_dir():
        raise ValueError('Thư mục lưu chưa tồn tại.')
    record = lesson['narration']
    pages = {}
    for index, unit in enumerate(narration_segments(lesson), 1):
        number = slide_for_locator(unit.get('locator', '')) or index
        if number and 'vi' in MODES[record['mode']]:
            pages.setdefault(number, {}).setdefault('vi', []).extend(speech_chunks(unit['vi']))
    speech_data = lesson.get('slide_speech')
    if speech_data:
        for page in speech_data['slides']:
            if 'en' in MODES[record['mode']]:
                pages.setdefault(page['slide'], {}).setdefault('en', []).extend(
                    part for segment in page['englishSpeechSegments'] if segment['status'] == 'ready'
                    for part in speech_chunks(segment['english_text']))
    elif 'en' in MODES[record['mode']]:
        for index, unit in enumerate(narration_segments(lesson), 1):
            number = slide_for_locator(unit.get('locator', '')) or index
            pages.setdefault(number, {}).setdefault('en', []).extend(speech_chunks(unit['en']))
    pending = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.biliclass-audio-', suffix='.zip', dir=target.parent, delete=False) as file:
            pending = Path(file.name)
        exported = []
        with zipfile.ZipFile(pending, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
            for number, languages in sorted(pages.items()):
                keys = {language: [speech.audio_key(text, record['voice'], record['rate']) for text in texts]
                        for language, texts in languages.items() if texts}
                for language, values in keys.items():
                    if any(key not in record['keys'].get(language, []) or not valid_key(directory, key) for key in values):
                        raise ValueError('Lời đọc đã đổi hoặc audio bị thiếu. Tạo lại bản giọng trước khi tải.')
                if record.get('playback') == 'both_controls' and set(keys) == {'vi', 'en'}:
                    keys['both'] = paired_keys(lesson, number, keys, record)
                for language, values in keys.items():
                    name = f'Slide-{number:03d}-{language}.wav'
                    audio, duration = joined_wav(directory, values)
                    archive.writestr(name, audio)
                    exported.append({'slide': number, 'language': language, 'file': name, 'duration_ms': duration})
            if not exported:
                raise ValueError('Chưa tìm thấy audio theo slide để tải.')
            archive.writestr('loi-doc.txt', '\n\n'.join(
                f"{unit['locator']}\nVI: {unit['vi']}\nEN: {unit['en']}" for unit in narration_segments(lesson)))
            archive.writestr('manifest.json', json.dumps({
                'version': 1, 'title': lesson['title'], 'mode': record['mode'],
                'voice': record['voice'], 'rate': record['rate'], 'files': exported,
                'playback': 'Phát thủ công theo slide; tệp audio không tự đồng bộ hiệu ứng PowerPoint.'},
                ensure_ascii=False, indent=2))
        os.replace(pending, target)
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)
    return target
