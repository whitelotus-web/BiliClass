"""Bundled, engine-versioned samples for instant first playback in Settings."""

import hashlib
import json
import re
import wave
from pathlib import Path
from uuid import uuid4

from . import speech
from .paths import RESOURCE_ROOT

SAMPLE_TEXT = "Xin chào các em. Let's learn together."
SAMPLE_ROOT = RESOURCE_ROOT / 'assets' / 'voice-previews'


def bundled_sample(text, voice):
    if text != SAMPLE_TEXT:
        return None
    try:
        manifest = json.loads((SAMPLE_ROOT / 'manifest.json').read_text(encoding='utf-8'))
        key = speech.audio_key(text, voice, 0)
        digest = manifest['files'].get(key + '.wav')
        if voice in speech.PAIRS_BY_ID:
            key = pair_preview_key(text, voice, 0)
            digest = manifest.get('pair_files', {}).get(key+'.wav') if manifest.get('english_engine') == speech.ENGLISH_VERSION else None
        path = SAMPLE_ROOT / (key + '.wav')
        if (manifest['engine'] == speech.VIENEU_VERSION and manifest['text'] == text and digest
                and hashlib.sha256(path.read_bytes()).hexdigest() == digest and speech.valid_audio(path)):
            return path
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def preview(text, voice, rate, directory, *, cancel=None):
    if voice in speech.PAIRS_BY_ID:
        return pair_preview(text, voice, rate, directory, cancel=cancel)
    if voice not in {v['id'] for v in speech.VIENEU_VOICES} | set(speech.ENGLISH_VOICES) or type(rate) is not int or not -3 <= rate <= 3:
        raise ValueError('Chọn giọng và tốc độ hợp lệ để nghe thử.')
    source = bundled_sample(text, voice)
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Đã dừng nghe thử.')
    if source is None:
        if cancel is not None:
            return speech.synthesize_background(text, voice, rate, directory, cancel)
        return speech.synthesize(text, voice, rate, directory)
    if rate == 0:
        return {'path': str(source), 'cached': True}
    # Preset playback must not wait behind a long lesson inference. Speed
    # variants use a separate atomic temporary file and never load the model.
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / (speech.audio_key(text, voice, rate) + '.wav')
    if speech.valid_audio(destination):
        return {'path': str(destination), 'cached': True}
    temporary = root / (uuid4().hex + '.wav')
    try:
        speech._speed_variant(source, rate, temporary)
        if not speech.valid_audio(temporary):
            raise ValueError('Chưa chuẩn bị được câu nghe thử.')
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {'path': str(destination), 'cached': False}


def pair_preview(text, voice, rate, directory, *, cancel=None):
    from .input_analysis import language_of

    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    if type(rate) is not int or not -3 <= rate <= 3:
        raise ValueError('Chọn tốc độ hợp lệ để nghe thử.')
    key = pair_preview_key(text, voice, rate)
    target = root/(key+'.wav')
    if speech.valid_audio(target):
        return {'path': str(target), 'cached': True}
    source = bundled_sample(text, voice)
    if source:
        if rate == 0:
            return {'path': str(source), 'cached': True}
        temporary = root/(uuid4().hex+'.wav')
        try:
            speech._speed_variant(source, rate, temporary)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return {'path': str(target), 'cached': False}
    files = []
    for sentence in re.split(r'(?<=[.!?])\s+|\n+', text):
        if not sentence.strip():
            continue
        language = 'vi' if language_of(sentence) == 'vi' else 'en'
        files.append(preview(sentence, speech.voice_for(voice, language), rate, directory, cancel=cancel)['path'])
    if not files:
        raise ValueError('Nhập câu nghe thử tiếng Việt hoặc tiếng Anh.')
    pending = root/(uuid4().hex+'.wav')
    try:
        with wave.open(str(pending), 'wb') as output:
            output.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            for file in files:
                if cancel is not None and cancel.is_set():
                    raise InterruptedError('Đã dừng nghe thử.')
                with wave.open(file, 'rb') as source:
                    if (source.getnchannels(), source.getsampwidth(), source.getframerate()) != (1, 2, 48000):
                        raise ValueError('Câu nghe thử chưa đúng định dạng.')
                    output.writeframes(source.readframes(source.getnframes()))
                output.writeframes(bytes(48000//2))  # 250 ms between languages/sentences.
        pending.replace(target)
    finally:
        pending.unlink(missing_ok=True)
    return {'path': str(target), 'cached': False}


def pair_preview_key(text, voice, rate):
    return hashlib.sha256(json.dumps([text, voice, rate, speech.VIENEU_VERSION, speech.ENGLISH_VERSION]).encode()).hexdigest()
