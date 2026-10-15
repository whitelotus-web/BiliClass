"""Bundled, engine-versioned samples for instant first playback in Settings."""

import hashlib
import json
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
        path = SAMPLE_ROOT / (key + '.wav')
        if (manifest['engine'] == speech.VIENEU_VERSION and manifest['text'] == text and digest
                and hashlib.sha256(path.read_bytes()).hexdigest() == digest and speech.valid_audio(path)):
            return path
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def preview(text, voice, rate, directory):
    if voice not in {v['id'] for v in speech.VIENEU_VOICES} or type(rate) is not int or not -3 <= rate <= 3:
        raise ValueError('Chọn giọng và tốc độ hợp lệ để nghe thử.')
    source = bundled_sample(text, voice)
    if source is None:
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
