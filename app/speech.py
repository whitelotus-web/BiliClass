"""Offline English Kokoro, Vietnamese VieNeu, and Windows SAPI WAV cache."""

import ctypes
import hashlib
import json
import os
import sys
import wave
from functools import lru_cache
from pathlib import Path
from threading import Lock
from uuid import uuid4

KOKORO_MODEL = "kokoro-multi-lang-v1_0"
KOKORO_VERSION = "kokoro-v1_0-sherpa-1.13.8"
VIENEU_VERSION = "vieneu-v3-turbo-onnx-fp32-61b85e3-3.8.3"
VIENEU_VOICES = (
    {"id": "vieneu:Mai Anh", "name": "Mai Anh · Nữ Bắc", "detail": "Rõ ràng, nhẹ nhàng"},
    {"id": "vieneu:Thùy Dung", "name": "Thùy Dung · Nữ Nam", "detail": "Thân thiện, tự nhiên"},
    {"id": "vieneu:Hải Đăng", "name": "Hải Đăng · Nam Bắc", "detail": "Mạch lạc, truyền cảm"},
    {"id": "vieneu:Thái Sơn", "name": "Thái Sơn · Nam Nam", "detail": "Ấm áp, gần gũi"},
)
_VIENEU_BY_ID = {voice["id"]: voice for voice in VIENEU_VOICES}
KOKORO_VOICES = (
    {"id": "kokoro:af_heart", "name": "Emma · Mỹ · Nữ", "detail": "Rõ ràng, phù hợp giảng bài", "sid": 3},
    {"id": "kokoro:af_bella", "name": "Bella · Mỹ · Nữ", "detail": "Ấm áp, sinh động", "sid": 2},
    {"id": "kokoro:am_michael", "name": "Michael · Mỹ · Nam", "detail": "Trầm, mạch lạc", "sid": 16},
    {"id": "kokoro:bf_emma", "name": "Emma · Anh · Nữ", "detail": "Giọng Anh chuẩn", "sid": 21},
    {"id": "kokoro:bm_george", "name": "George · Anh · Nam", "detail": "Giọng Anh trầm", "sid": 26},
)
_VOICE_BY_ID = {voice["id"]: voice for voice in KOKORO_VOICES}
_ENGINE_LOCK = Lock()
# Keep adjustments modest: very slow inference can sound less natural.
_SPEEDS = (0.82, 0.88, 0.94, 1.0, 1.06, 1.12, 1.18)


def kokoro_root():
    configured = os.environ.get("BILICLASS_KOKORO_DIR")
    if configured:
        return Path(configured).resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "models" / KOKORO_MODEL
    return Path(__file__).resolve().parents[1] / ".runtime" / "kokoro" / KOKORO_MODEL


def kokoro_ready():
    root = kokoro_root()
    required = ("model.onnx", "voices.bin", "tokens.txt", "lexicon-us-en.txt", "espeak-ng-data/phontab")
    return all((root / name).is_file() for name in required)


def vieneu_root():
    configured = os.environ.get("BILICLASS_VIENEU_DIR")
    if configured:
        return Path(configured).resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "models" / "vieneu-hf"
    return Path(__file__).resolve().parents[1] / ".runtime" / "vieneu-hf"


def vieneu_ready():
    hub = vieneu_root() / "hub"
    model = hub / "models--pnnbao-ump--VieNeu-TTS-v3-Turbo" / "snapshots"
    codec = hub / "models--OpenMOSS-Team--MOSS-Audio-Tokenizer-Nano-ONNX" / "snapshots"
    graph_files = (
        "config.json", "tokenizer.json", "vieneu_prefill.onnx", "vieneu_decode_step.onnx",
        "vieneu_acoustic_cached.onnx", "vieneu_backbone_shared.data", "vieneu_v3_heads.npz",
    )
    codec_files = (
        "moss_audio_tokenizer_decode_full.onnx", "moss_audio_tokenizer_decode_shared.data",
        "moss_audio_tokenizer_decode_step.onnx", "moss_audio_tokenizer_encode.onnx",
        "moss_audio_tokenizer_encode.data",
    )
    return any(all((path / "onnx_update" / name).is_file() for name in graph_files)
               for path in model.glob("*")) and any(
        all((path / name).is_file() for name in codec_files) for path in codec.glob("*"))


def _windows_voices():
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    speaker = tokens = token = None
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        tokens = speaker.GetVoices()
        result = []
        for index in range(tokens.Count):
            token = tokens.Item(index)
            ids = [int(value, 16) & 0x3FF for value in token.GetAttribute("Language").split(";") if value]
            language = "en" if 9 in ids else "vi" if 42 in ids else "other"
            result.append({"id": token.Id, "name": token.GetDescription(), "language": language, "provider": "sapi"})
        return result
    finally:
        token = tokens = speaker = None
        pythoncom.CoUninitialize()


def list_voices():
    """Expose installed offline voices; retain SAPI as a Vietnamese fallback."""
    kokoro = [dict(voice, language="en", provider="kokoro") for voice in KOKORO_VOICES] if kokoro_ready() else []
    vieneu = [dict(voice, language="vi", provider="vieneu") for voice in VIENEU_VOICES] if vieneu_ready() else []
    try:
        windows = _windows_voices()
    except Exception:
        windows = []
    return kokoro + vieneu + [voice for voice in windows if voice["language"] == "vi" or not kokoro]


def audio_key(text, voice_id, rate):
    provider = KOKORO_VERSION if voice_id in _VOICE_BY_ID else VIENEU_VERSION if voice_id in _VIENEU_BY_ID else "sapi-v1"
    payload = json.dumps({"text": text, "voice": voice_id, "rate": rate, "provider": provider}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def valid_audio(path):
    try:
        with wave.open(str(path), "rb") as wav:
            return wav.getnframes() > 0 and wav.getframerate() > 0
    except (OSError, EOFError, wave.Error):
        return False


def _native_path(root):
    """sherpa's Windows C runtime requires an ASCII path for eSpeak data."""
    if os.name != "nt":
        return root
    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetShortPathNameW(str(root), buffer, len(buffer))
    if not length or length >= len(buffer) or not buffer.value.isascii():
        raise RuntimeError("Không mở được model Kokoro trong đường dẫn hiện tại. Hãy cài vào thư mục có đường dẫn ASCII.")
    return Path(buffer.value)


@lru_cache(maxsize=1)
def _kokoro_engine(root):
    import sherpa_onnx

    native = _native_path(root)
    config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=str(native / "model.onnx"),
                voices=str(native / "voices.bin"),
                tokens=str(native / "tokens.txt"),
                data_dir=str(native / "espeak-ng-data"),
                lexicon=str(native / "lexicon-us-en.txt"),
            ),
            num_threads=2,
            provider="cpu",
        ),
    )
    if not config.validate():
        raise RuntimeError("Bộ giọng Kokoro bị thiếu hoặc hỏng. Hãy cài lại bản BiliClass đầy đủ.")
    return sherpa_onnx.OfflineTts(config)


def _synthesize_kokoro(text, voice_id, rate, temporary):
    import numpy as np

    root = kokoro_root()
    if not kokoro_ready():
        raise RuntimeError("Chưa có model Kokoro ngoại tuyến. Hãy cài lại bản BiliClass đầy đủ.")
    with _ENGINE_LOCK:
        audio = _kokoro_engine(str(root)).generate(text, sid=_VOICE_BY_ID[voice_id]["sid"], speed=_SPEEDS[rate + 3])
    samples = np.asarray(audio.samples, dtype=np.float32)
    if samples.size == 0 or not 8000 <= audio.sample_rate <= 96000:
        raise RuntimeError("Kokoro không tạo được âm thanh cho đoạn này.")
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(temporary), "wb") as writer:
        writer.setparams((1, 2, audio.sample_rate, 0, "NONE", "not compressed"))
        writer.writeframes(pcm.tobytes())


@lru_cache(maxsize=1)
def _vieneu_engine(root):
    if not vieneu_ready():
        raise RuntimeError("Chưa có model VieNeu ngoại tuyến. Hãy cài bản BiliClass đầy đủ.")
    # The SDK reads HF_HOME at import time. The bundled cache is complete, and
    # offline mode prevents accidental lesson text or model requests over the network.
    os.environ["HF_HOME"] = root
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    from vieneu import Vieneu

    return Vieneu(backend="onnx", precision="fp32", threads=4)


def _synthesize_vieneu(text, voice_id, rate, temporary):
    import numpy as np

    with _ENGINE_LOCK:
        engine = _vieneu_engine(str(vieneu_root()))
        samples = np.asarray(engine.infer(text, voice=voice_id.split(":", 1)[1]), dtype=np.float32)
    if not samples.size:
        raise RuntimeError("VieNeu không tạo được âm thanh cho đoạn này.")
    if rate:
        import librosa

        samples = librosa.effects.time_stretch(samples, rate=_SPEEDS[rate + 3])
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(temporary), "wb") as writer:
        writer.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        writer.writeframes(pcm.tobytes())


def _synthesize_sapi(text, voice_id, rate, temporary):
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    speaker = tokens = selected = stream = None
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        tokens = speaker.GetVoices()
        selected = next((tokens.Item(i) for i in range(tokens.Count) if tokens.Item(i).Id == voice_id), None)
        if selected is None:
            raise ValueError("Giọng đã chọn không còn trên máy. Hãy chọn lại trong Cài đặt.")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        stream.Open(str(temporary), 3, False)
        try:
            speaker.Voice = selected
            speaker.Rate = rate
            speaker.AudioOutputStream = stream
            speaker.Speak(text, 16)  # SVSFIsNotXML: lesson text is never interpreted as speech markup.
        finally:
            stream.Close()
    finally:
        stream = selected = tokens = speaker = None
        pythoncom.CoUninitialize()


def synthesize(text, voice_id, rate, directory):
    if not text.strip() or len(text) > 5000:
        raise ValueError("Giọng đọc nhận từ 1 đến 5.000 ký tự mỗi đoạn.")
    if type(rate) is not int or not -3 <= rate <= 3:
        raise ValueError("Tốc độ giọng đọc không hợp lệ.")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / (audio_key(text, voice_id, rate) + ".wav")
    if valid_audio(destination):
        return {"path": str(destination), "cached": True}
    temporary = root / (str(uuid4()) + ".wav")
    try:
        if voice_id in _VOICE_BY_ID:
            _synthesize_kokoro(text, voice_id, rate, temporary)
        elif voice_id in _VIENEU_BY_ID:
            _synthesize_vieneu(text, voice_id, rate, temporary)
        else:
            _synthesize_sapi(text, voice_id, rate, temporary)
        if not valid_audio(temporary):
            raise ValueError("Giọng đọc không tạo được âm thanh hợp lệ.")
        temporary.replace(destination)
        return {"path": str(destination), "cached": False}
    finally:
        temporary.unlink(missing_ok=True)


def play(path):
    import winsound

    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)


def stop():
    import winsound

    winsound.PlaySound(None, 0)
