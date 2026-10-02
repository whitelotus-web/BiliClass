"""Portable WAVs tied to exact text, language, voice and speed."""
import hashlib
import io
import json
import wave
from pathlib import Path

from .speech import audio_key, valid_audio


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def available_audio(directory, text, language, voice="", rate=0):
    root = Path(directory) / "audio"
    exact = root / (audio_key(text, voice, rate) + ".wav")
    if valid_audio(exact):
        return exact
    for metadata in root.glob("*.json"):
        try:
            record = json.loads(metadata.read_text(encoding="utf-8"))
            if record["text_sha256"] != text_hash(text) or record["language"] != language:
                continue
            if voice and (record["voice"] != voice or record["rate"] != rate):
                continue
            wav = root / record["file"]
            if wav.name != record["file"] or not valid_audio(wav):
                continue
            if hashlib.sha256(wav.read_bytes()).hexdigest() == record["sha256"]:
                return wav
        except (ValueError, OSError, KeyError, TypeError):
            continue
    return None


def collect_audio(library, lesson):
    from .speech import list_voices
    try:
        voices = list_voices()
    except Exception:
        voices = []
    records, files = [], {}
    for segment in lesson["segments"]:
        if not segment.get("approved"):
            continue
        for language in ("vi", "en"):
            voice = library.setting("voice_" + language, "")
            if not voice:
                voice = next((v["id"] for v in voices if v["language"] == language), "")
            rate = library.setting("voice_rate", 0)
            path = available_audio(library.directory, segment[language], language, voice, rate)
            if path is None:
                continue
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            filename = digest + ".wav"
            records.append({"segment_id": segment["id"], "language": language,
                            "text_sha256": text_hash(segment[language]), "voice": voice, "rate": rate,
                            "sha256": digest, "file": filename})
            files["audio/" + filename] = data
    return records, files


def validate_audio(records, segments, payloads):
    if not isinstance(records, list) or len(records) > 20000:
        raise ValueError("Danh sách âm thanh không hợp lệ.")
    validated = []
    by_id = {s["id"]: s for s in segments}
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("Thông tin âm thanh không hợp lệ.")
        language = item.get("language")
        segment = by_id.get(item.get("segment_id"))
        filename = item.get("file", "")
        if language not in ("vi", "en") or not segment or not isinstance(filename, str):
            raise ValueError("Âm thanh không thuộc nội dung bài.")
        data = payloads.get("audio/" + filename)
        if data is None or len(data) > 25 * 1024**2:
            raise ValueError("Âm thanh bị thiếu hoặc quá lớn.")
        digest = hashlib.sha256(data).hexdigest()
        if filename != digest + ".wav" or item.get("sha256") != digest or item.get("text_sha256") != text_hash(segment[language]):
            raise ValueError("Âm thanh không khớp nội dung hoặc checksum.")
        if not isinstance(item.get("voice"), str) or len(item["voice"]) > 1000 or type(item.get("rate")) is not int or not -3 <= item["rate"] <= 3:
            raise ValueError("Giọng/tốc độ âm thanh không hợp lệ.")
        try:
            with wave.open(io.BytesIO(data), "rb") as wav:
                if wav.getnframes() <= 0 or wav.getnchannels() not in (1, 2) or not 8000 <= wav.getframerate() <= 96000:
                    raise ValueError("WAV không hợp lệ.")
                if len(wav.readframes(wav.getnframes())) != wav.getnframes() * wav.getnchannels() * wav.getsampwidth():
                    raise ValueError("WAV bị cắt ngắn.")
        except (wave.Error, EOFError) as exc:
            raise ValueError("WAV không hợp lệ.") from exc
        validated.append((item, data))
    return validated
