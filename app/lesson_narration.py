"""Explicit, local narration plans; opening a lesson never starts synthesis."""

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from . import speech
from .browser_audio import narration_tasks

MODES = {"en": ("en",), "vi": ("vi",), "both": ("vi", "en")}
LABELS = {"en": "Tiếng Anh", "vi": "Tiếng Việt", "both": "Việt + Anh"}


def inspection_for(lesson):
    return {"profile": {"units": [{"vi": s["vi"], "en": s["en"]} for s in lesson["segments"]]},
            "slide_speech": lesson.get("slide_speech", {})}


def signature(lesson):
    value = {"source": (lesson.get("source") or {}).get("sha256", ""),
             "units": [{"vi": s["vi"], "en": s["en"]} for s in lesson["segments"]],
             "speech": lesson.get("slide_speech", {})}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def make_plan(lesson, mode, voices):
    if mode not in MODES:
        raise ValueError("Chọn tiếng Anh, tiếng Việt hoặc Việt + Anh.")
    selected = {**voices, **{lang: voices.get("voice", "") if lang in MODES[mode] else ""
                            for lang in ("vi", "en")}}
    keys = {}
    skipped = 0
    for lang in MODES[mode]:
        tasks, omitted, _ = narration_tasks(inspection_for(lesson), {**selected, **{other: ""
                                                  for other in ("vi", "en") if other != lang}})
        keys[lang] = [speech.audio_key(text, voice, selected["rate"]) for text, voice in tasks]
        skipped += omitted
    return {"version": 2, "mode": mode, "signature": signature(lesson),
            "voice": selected.get("voice", ""), "rate": selected["rate"], "keys": keys,
            "total": len(set(key for items in keys.values() for key in items)), "skipped": skipped}, selected


@lru_cache(maxsize=4096)
def _valid(path, size, modified):
    return speech.valid_audio(Path(path))


def valid_key(directory, key):
    # Imported manifests are data, never arbitrary paths.
    if not isinstance(key, str) or len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
        return False
    path = Path(directory) / "audio" / (key + ".wav")
    try:
        stat = path.stat()
        # The validated key cannot contain a path component. Resolving the
        # same absolute WAV path repeatedly also walks Windows reparse points.
        return _valid(str(path.absolute()), stat.st_size, stat.st_mtime_ns)
    except OSError:
        return False


def audio_status(lesson, directory, fallback_voices=None, *, cancel=None):
    record = lesson.get("narration")
    legacy = record is None
    if legacy:
        voices = dict(fallback_voices or {})
        request_id = lesson.get("external_deck", {}).get("request_id", "")
        folder = Path(directory) / "chatgpt" / request_id
        if folder.resolve().parent == (Path(directory) / "chatgpt").resolve():
            try:
                old = json.loads((folder / "narration-progress.json").read_text(encoding="utf-8"))
                if old.get("lesson_id") == lesson["id"] and old.get("voice"):
                    voices.update(voice=old["voice"], rate=old.get("rate", 0))
            except (OSError, ValueError, KeyError):
                pass
        if not voices.get("voice"):
            return {"status": "none", "mode": "none", "label": "Chỉ bài giảng song ngữ", "ready": False}
        record, _ = make_plan(lesson, "both", voices)
    empty = {"status": "none", "mode": "none", "label": "Chỉ bài giảng song ngữ", "ready": False}
    if not isinstance(record, dict):
        return empty
    mode = record.get("mode", "none")
    if not isinstance(mode, str) or mode not in MODES:
        return empty
    if record.get("signature") != signature(lesson):
        return {**empty, "status": "stale", "mode": mode, "label": "Giọng đọc cần cập nhật"}
    if (not isinstance(record.get("voice"), str) or type(record.get("rate")) is not int
            or not -3 <= record["rate"] <= 3):
        return empty
    keys = record.get("keys", {})
    if not isinstance(keys, dict) or any(not isinstance(keys.get(lang, []), list) for lang in MODES[mode]):
        return empty
    expected, _ = make_plan(lesson, mode, {"voice": record["voice"], "rate": record["rate"]})
    if keys != expected["keys"]:
        return {**empty, "status": "stale", "mode": mode, "label": "Giọng đọc cần cập nhật"}
    all_keys = set(k for lang in MODES[mode] for k in keys.get(lang, []) if isinstance(k, str))
    valid = {}
    for key in all_keys:
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Đã dừng kiểm tra giọng đọc.')
        valid[key] = valid_key(directory, key)
    counts = {lang: sum(valid.get(k, False) for k in keys.get(lang, [])) for lang in MODES[mode]}
    complete = sum(valid.values())
    ready_languages = [lang for lang in MODES[mode] if keys.get(lang) and counts[lang] == len(keys[lang])]
    if legacy:
        if not complete:
            return empty
        if ready_languages:
            mode = "both" if len(ready_languages) == 2 else ready_languages[0]
            all_keys = set(k for lang in MODES[mode] for k in keys.get(lang, []) if isinstance(k, str))
            complete = sum(valid.get(k, False) for k in all_keys)
    ready = bool(all_keys) and all(lang in ready_languages for lang in MODES[mode]) and not record.get("skipped")
    status = "ready" if ready else "partial" if complete else "pending"
    return {"status": status, "mode": mode, "ready": ready, "complete": complete, "total": len(all_keys),
            "voice": record.get("voice", ""), "rate": record.get("rate", 0), "skipped": record.get("skipped", 0),
            "languages": list(MODES[mode]), "ready_languages": ready_languages,
            "label": "Có giọng " + LABELS[mode] if ready else "Giọng đọc chưa đủ" if complete else "Chưa tạo xong giọng đọc"}
