"""US English speakers using one offline, CPU-only Kokoro model."""

import os
import sys
import wave
from functools import lru_cache
from pathlib import Path

from .voice_pairs import ENGLISH_VOICES


def spoken_text(text):
    from .spoken_chemistry import english as chemistry
    from .spoken_labels import english as labels

    return chemistry(labels(text))


def model_root():
    configured = os.environ.get('BILICLASS_KOKORO_DIR')
    if configured:
        return Path(configured).resolve()
    base = Path(sys.executable).resolve().parent / 'models' if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1] / '.runtime/kokoro'
    return base / 'kokoro-multi-lang-v1_0'


def ready():
    root = model_root()
    return all((root/name).is_file() for name in ('model.onnx', 'voices.bin', 'tokens.txt')) and (root/'espeak-ng-data/lang/gmw/en-US').is_file()


@lru_cache(maxsize=1)
def engine(root, cache):
    import sherpa_onnx

    root = Path(root)
    if not ready():
        raise RuntimeError('Chưa có bộ giọng Anh–Mỹ ngoại tuyến. Cài bản BiliClass đầy đủ.')
    # An explicit en-us route uses eSpeak for the complete phrase; the large
    # lookup lexicon is unused on this route. Avoid parsing/copying it per helper.
    # eSpeak's C loader on Windows takes ANSI paths, including its data files.
    # Use existing 8.3 aliases without moving or copying the user's library.
    def native(path):
        if sys.platform == 'win32':
            import win32api

            return win32api.GetShortPathName(str(path))
        return str(path)
    config = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=native(root/'model.onnx'), voices=native(root/'voices.bin'), tokens=native(root/'tokens.txt'),
            data_dir=native(root/'espeak-ng-data'), lang='en-us'),
        num_threads=2, provider='cpu'), max_num_sentences=1)
    if not config.validate():
        raise RuntimeError('Bộ giọng Anh–Mỹ chưa đầy đủ. Cài lại gói giọng ngoại tuyến.')
    return sherpa_onnx.OfflineTts(config)


def render(text, voice, rate, temporary):
    import numpy as np
    from scipy.signal import resample_poly

    from .speech import _SPEEDS
    from .voice_speed import time_stretch_audio
    from .voice_threads import blas_budget

    player = engine(str(model_root()), str(Path(temporary).parent/'english-lexicon'))
    with blas_budget():
        audio = player.generate(text=spoken_text(text), sid=ENGLISH_VOICES[voice][1], speed=1.0)
    samples = np.asarray(audio.samples, dtype=np.float32)
    if samples.ndim != 1 or not samples.size or not np.isfinite(samples).all() or audio.sample_rate != 24000:
        raise RuntimeError('Chưa tạo được âm thanh tiếng Anh hợp lệ.')
    samples = resample_poly(samples, 2, 1).astype(np.float32)
    if rate:
        samples = time_stretch_audio(samples, _SPEEDS[rate+3])
    with wave.open(str(temporary), 'wb') as writer:
        writer.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        writer.writeframes((np.clip(samples, -1, 1)*32767).astype('<i2').tobytes())
