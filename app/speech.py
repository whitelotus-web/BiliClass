"""One offline VieNeu speaker for Vietnamese, English and mixed lesson text."""

import hashlib
import json
import os
import sys
import wave
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from threading import Condition, Lock, local
from uuid import uuid4
from weakref import WeakValueDictionary

from .voice_pairs import BY_ID as PAIRS_BY_ID
from .voice_pairs import ENGLISH_VERSION, ENGLISH_VOICES, PAIRS, selection_for, voice_for

VIENEU_VERSION = "vieneu-v3-turbo-onnx-fp32-61b85e3-3.8.3-multilingual-wsola1"
VIENEU_VOICES = (
    {"id": "vieneu:Mai Anh", "name": "Mai Anh · Nữ Bắc", "detail": "Rõ ràng, nhẹ nhàng"},
    {"id": "vieneu:Thùy Dung", "name": "Thùy Dung · Nữ Nam", "detail": "Thân thiện, tự nhiên"},
    {"id": "vieneu:Hải Đăng", "name": "Hải Đăng · Nam Bắc", "detail": "Mạch lạc, truyền cảm"},
    {"id": "vieneu:Thái Sơn", "name": "Thái Sơn · Nam Nam", "detail": "Ấm áp, gần gũi"},
    {"id": "vieneu:Ngọc Trân", "name": "Ngọc Trân · Nữ Trung", "detail": "Tự nhiên, nhẹ nhàng"},
    {"id": "vieneu:Quang Sơn", "name": "Quang Sơn · Nam Trung", "detail": "Tự nhiên, mạch lạc"},
)
_VIENEU_BY_ID = {voice["id"]: voice for voice in VIENEU_VOICES}
_ENGINE_TURN = Condition()
_ENGINE_BUSY = False
_FOREGROUND_WAITERS = 0
_SYNTHESIS_CONTEXT = local()
_ENGINE_LOAD_LOCK = Lock()
_SECOND_ENGINE_LOCK = Lock()
_AUDIO_LOCKS_LOCK = Lock()
_AUDIO_LOCKS = WeakValueDictionary()
_ISOLATED_SYNTHESIS = False
# Keep adjustments modest: very slow inference can sound less natural.
_SPEEDS = (0.82, 0.88, 0.94, 1.0, 1.06, 1.12, 1.18)


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


def list_voices():
    from .english_speech import ready

    return [dict(voice) for voice in PAIRS] if vieneu_ready() and ready() else []


def voice_settings(library, voices=None):
    """Resolve one speaker; migrate legacy preferences without changing stored lessons."""
    voices = list_voices() if voices is None else voices
    ids = [v["id"] for v in voices if v.get("provider") in {"vieneu", "local_pair"}]
    saved = library.setting("voice_options", None)
    if isinstance(saved, dict):
        selected, rate = saved.get("voice", ""), saved.get("rate", 0)
    else:
        selected, rate = library.setting("voice_vi", ""), library.setting("voice_rate", 0)
    selected = selection_for(selected) if any(identity in PAIRS_BY_ID for identity in ids) else selected
    voice = selected if selected in ids else ids[0] if ids else ""
    rate = rate if type(rate) is int and -3 <= rate <= 3 else 0
    # Language keys are routing aliases for existing narration/readiness consumers,
    # never independent saved voices or settings controls.
    return {"voice": voice, "vi": voice_for(voice, 'vi'), "en": voice_for(voice, 'en'), "rate": rate,
            "index": ids.index(voice) if voice else -1, "speed": _SPEEDS[rate + 3]}


def audio_key(text, voice_id, rate):
    # Preserve identity of old portable WAVs; their engines are no longer offered.
    provider = (ENGLISH_VERSION if voice_id in ENGLISH_VOICES else VIENEU_VERSION if voice_id in _VIENEU_BY_ID else
                "kokoro-v1_0-sherpa-1.13.8" if voice_id.startswith("kokoro:") else "sapi-v1")
    payload = json.dumps({"text": text, "voice": voice_id, "rate": rate, "provider": provider}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def valid_audio(path):
    try:
        with wave.open(str(path), "rb") as wav:
            return wav.getnframes() > 0 and wav.getframerate() > 0
    except (OSError, EOFError, wave.Error):
        return False


def _vieneu_engine(root):
    # lru_cache alone can initialize twice when two callers miss concurrently.
    with _ENGINE_LOAD_LOCK:
        return _cached_vieneu_engine(root)


@lru_cache(maxsize=1)
def _cached_vieneu_engine(root):
    if not vieneu_ready():
        raise RuntimeError("Chưa có model VieNeu ngoại tuyến. Hãy cài bản BiliClass đầy đủ.")
    # The SDK reads HF_HOME at import time. The bundled cache is complete, and
    # offline mode prevents accidental lesson text or model requests over the network.
    os.environ["HF_HOME"] = root
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    # Another speech dependency may have imported Hub before these environment
    # variables were set. Its cached constants would still allow HTTP metadata
    # requests, even though all model files are already installed locally.
    from huggingface_hub import constants

    constants.HF_HUB_OFFLINE = True
    constants.HF_HOME = root
    constants.HF_HUB_CACHE = str(Path(root) / "hub")
    constants.HUGGINGFACE_HUB_CACHE = constants.HF_HUB_CACHE
    from vieneu import Vieneu

    return Vieneu(backend="onnx", device="cpu", precision="fp32",
                  threads=getattr(_SYNTHESIS_CONTEXT, 'worker_threads', 4))


@lru_cache(maxsize=1)
def _secondary_vieneu_engine(root):
    _vieneu_engine(root)  # Complete offline initialization before the extra model.
    from vieneu import Vieneu
    return Vieneu(backend='onnx',device='cpu',precision='fp32',threads=2)


def narration_workers(tasks):
    """An extra model pays off only for a long uncached CPU narration job."""
    if os.environ.get('BILICLASS_NARRATION_WORKERS')=='1' or len(tasks)<48 or sum(len(t) for t,_ in tasks)<3000:
        return 1
    try:
        import psutil
        return 2 if (psutil.cpu_count(logical=False) or 1)>=6 and psutil.virtual_memory().available>=6*1024**3 else 1
    except Exception:
        return 1


def _synthesize_vieneu(text, voice_id, rate, temporary):
    if _ISOLATED_SYNTHESIS:
        from .speech_process import render

        return render(vieneu_root(), text, voice_id, rate, temporary,
                      secondary=getattr(_SYNTHESIS_CONTEXT, 'secondary', False))
    return _synthesize_vieneu_local(text, voice_id, rate, temporary)


def _synthesize_vieneu_local(text, voice_id, rate, temporary):
    if voice_id in ENGLISH_VOICES:
        from .english_speech import render

        return render(text, voice_id, rate, temporary)
    import numpy as np

    from .voice_threads import blas_budget

    factory=_secondary_vieneu_engine if getattr(_SYNTHESIS_CONTEXT,'secondary',False) else _vieneu_engine
    engine = factory(str(vieneu_root()))
    # ONNX already owns four CPU threads. The small NumPy projection heads
    # were starting another full BLAS pool for every token. One BLAS thread
    # measured faster without changing the model, precision or audio cache.
    # All inference callers share synthesis_turn(), including the reader.
    with blas_budget():
        samples = np.asarray(engine.infer(text, voice=voice_id.split(":", 1)[1]), dtype=np.float32)
    if not samples.size or samples.ndim != 1 or not np.isfinite(samples).all():
        raise RuntimeError("VieNeu không tạo được âm thanh cho đoạn này.")
    if rate:
        from .voice_speed import time_stretch_audio

        samples = time_stretch_audio(samples, rate=_SPEEDS[rate + 3])
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(temporary), "wb") as writer:
        writer.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        writer.writeframes(pcm.tobytes())


@contextmanager
def synthesis_turn():
    """One engine; requested playback takes the next turn before warmup."""
    global _ENGINE_BUSY, _FOREGROUND_WAITERS
    if getattr(_SYNTHESIS_CONTEXT,'secondary',False):
        with _SECOND_ENGINE_LOCK:
            yield
        return
    cancel = getattr(_SYNTHESIS_CONTEXT, "cancel", None)
    foreground = cancel is None
    with _ENGINE_TURN:
        if foreground:
            _FOREGROUND_WAITERS += 1
        try:
            while _ENGINE_BUSY or (not foreground and _FOREGROUND_WAITERS):
                if cancel is not None and cancel.is_set():
                    raise InterruptedError("Đã dừng chuẩn bị giọng đọc nền.")
                _ENGINE_TURN.wait(.1)
            if cancel is not None and cancel.is_set():
                raise InterruptedError("Đã dừng chuẩn bị giọng đọc nền.")
            _ENGINE_BUSY = True
        finally:
            if foreground:
                _FOREGROUND_WAITERS -= 1
    try:
        yield
    finally:
        with _ENGINE_TURN:
            _ENGINE_BUSY = False
            _ENGINE_TURN.notify_all()


def synthesize_background(text, voice_id, rate, directory, cancel):
    """A lower priority cache request, without a second model instance."""
    previous = getattr(_SYNTHESIS_CONTEXT, "cancel", None)
    _SYNTHESIS_CONTEXT.cancel = cancel
    try:
        return synthesize(text, voice_id, rate, directory)
    finally:
        _SYNTHESIS_CONTEXT.cancel = previous


def synthesize_secondary(text, voice_id, rate, directory, cancel):
    previous=getattr(_SYNTHESIS_CONTEXT,'secondary',False)
    _SYNTHESIS_CONTEXT.secondary=True
    try:
        return synthesize_background(text,voice_id,rate,directory,cancel)
    finally:
        _SYNTHESIS_CONTEXT.secondary=previous


@contextmanager
def _audio_turn(key):
    with _AUDIO_LOCKS_LOCK:
        lock=_AUDIO_LOCKS.get(key)
        if lock is None:
            lock=Lock()
            _AUDIO_LOCKS[key]=lock
    cancel=getattr(_SYNTHESIS_CONTEXT,'cancel',None)
    while not lock.acquire(timeout=.1):
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Đã dừng chờ đoạn giọng đọc.')
    try:
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Đã dừng chờ đoạn giọng đọc.')
        yield
    finally:
        lock.release()


def synthesize(text, voice_id, rate, directory):
    if not text.strip() or len(text) > 5000:
        raise ValueError("Giọng đọc nhận từ 1 đến 5.000 ký tự mỗi đoạn.")
    if type(rate) is not int or not -3 <= rate <= 3:
        raise ValueError("Tốc độ giọng đọc không hợp lệ.")
    if voice_id not in _VIENEU_BY_ID and voice_id not in ENGLISH_VOICES:
        raise ValueError("Chọn cặp giọng Việt–Mỹ trong Cài đặt → Giọng đọc (giọng Việt dùng VieNeu).")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / (audio_key(text, voice_id, rate) + ".wav")
    if valid_audio(destination):
        return {"path": str(destination), "cached": True}
    from .storage_space import MIB, require_space

    require_space(root, 64 * MIB)
    with _audio_turn(os.path.normcase(str(destination.absolute()))):
        # Another reader/warmup may have completed this exact chunk while we
        # waited. Reuse it instead of running inference twice.
        if valid_audio(destination):
            return {"path": str(destination), "cached": True}
        with synthesis_turn():
            return _synthesize_locked(text,voice_id,rate,root,destination)


def _synthesize_locked(text,voice_id,rate,root,destination):
    # Speed is post-processing, not a different utterance. Preserve the
    # existing public WAV keys/portable packs, but infer the neutral version
    # once and derive all other rates from it.
    original = root / (audio_key(text, voice_id, 0) + ".wav")
    temporary = root / (str(uuid4()) + ".wav")
    try:
        if not valid_audio(original):
            _synthesize_vieneu(text, voice_id, 0, temporary)
            if not valid_audio(temporary):
                raise ValueError("Giọng đọc không tạo được âm thanh hợp lệ.")
            temporary.replace(original)
        if not rate:
            return {"path": str(original), "cached": False}
        cancel = getattr(_SYNTHESIS_CONTEXT, "cancel", None)
        if cancel is not None and cancel.is_set():
            raise InterruptedError("Đã dừng tạo giọng; đoạn gốc đã được giữ.")
        _speed_variant(original, rate, temporary)
        if not valid_audio(temporary):
            raise ValueError("Giọng đọc không tạo được âm thanh hợp lệ.")
        temporary.replace(destination)
        return {"path": str(destination), "cached": False}
    finally:
        temporary.unlink(missing_ok=True)


def _speed_variant(original, rate, destination):
    """Derive a pitch-preserving rate variant without loading the TTS engine."""
    import numpy as np

    from .voice_speed import time_stretch_audio

    with wave.open(str(original), "rb") as reader:
        if (reader.getnchannels(), reader.getsampwidth(), reader.getframerate()) != (1, 2, 48000):
            raise ValueError("Âm thanh gốc chưa đúng định dạng VieNeu.")
        samples = np.frombuffer(reader.readframes(reader.getnframes()), dtype="<i2").astype(np.float32) / 32768
    adjusted = time_stretch_audio(samples, _SPEEDS[rate + 3])
    pcm = (np.clip(adjusted, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(destination), "wb") as writer:
        writer.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        writer.writeframes(pcm.tobytes())


def play(path):
    import winsound

    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)


def stop():
    import winsound

    winsound.PlaySound(None, 0)
