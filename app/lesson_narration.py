"""Explicit, local narration plans; opening a lesson never starts synthesis."""

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from . import speech
from .browser_audio import narration_tasks

MODES = {"en": ("en",), "vi": ("vi",), "both": ("vi", "en")}
LABELS = {"en": "Tiếng Anh", "vi": "Tiếng Việt", "both": "Việt + Anh"}


def variant_id(record):
    if (not isinstance(record, dict) or not isinstance(record.get('mode'), str) or record.get('mode') not in MODES
            or not isinstance(record.get('signature'), str) or not isinstance(record.get('voice'), str)
            or type(record.get('rate')) is not int or not -3 <= record['rate'] <= 3
            or record.get('playback', 'separate') not in ('separate', 'both_controls')):
        return ''
    value = {key: record.get(key) for key in ('signature', 'mode', 'voice', 'rate')}
    value['playback'] = record.get('playback', 'separate')
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def records(lesson):
    """Include the old single recording without rewriting the personal library."""
    saved = lesson.get('narration_variants', {})
    result = {variant_id(row): row for row in saved.values() if isinstance(row, dict) and variant_id(row)} if isinstance(saved, dict) else {}
    active = lesson.get('narration')
    identity = variant_id(active)
    if identity:
        result[identity] = active
    return result


def variant_title(record):
    voice = next((v['name'] for v in speech.VIENEU_VOICES if v['id'] == record.get('voice')), record.get('voice', ''))
    mode = 'Việt–Anh · loa riêng và chung' if record.get('mode') == 'both' and record.get('playback') == 'both_controls' else LABELS.get(record.get('mode'), '')
    if record.get('mode') == 'both' and record.get('playback', 'separate') == 'separate':
        mode = 'Việt + Anh · hai loa'
    rate = record.get('rate', 0)
    speed = round(speech._SPEEDS[rate + 3] * 100) if type(rate) is int and -3 <= rate <= 3 else 100
    return f'{mode} · {voice} · {speed}%'


def variant_statuses(lesson, directory, fallback_voices=None, *, cancel=None):
    context = {}
    return [{**audio_status({**lesson, 'narration': record}, directory, fallback_voices, cancel=cancel, _context=context),
             'id': identity, 'title': variant_title(record)}
            for identity, record in records(lesson).items()]


def library_audio_status(lesson, directory, fallback_voices=None, *, cancel=None):
    variants = variant_statuses(lesson, directory, fallback_voices, cancel=cancel)
    active = next((row for row in variants if row['id'] == variant_id(lesson.get('narration'))), None)
    if active is None:
        active = audio_status(lesson, directory, fallback_voices, cancel=cancel)
    ready = [v for v in variants if v['ready']]
    if ready:
        modes = {v['mode'] for v in ready}
        labels = [label for mode, label in (('en', 'Anh'), ('vi', 'Việt'), ('both', 'Song ngữ')) if mode in modes]
        active = {**active, 'label': 'Đã có giọng đọc: ' + ' · '.join(labels), 'ready': True}
    elif not variants and active.get('status') == 'none':
        active = {**active, 'label': 'Chưa có giọng đọc'}
    return {**active, 'variants': variants}


def creation_choices(lesson, voice, rate, verified=(), live=None):
    """Describe the three exact products using published audio checks, no I/O."""
    if not lesson or voice not in {v['id'] for v in speech.VIENEU_VOICES} or type(rate) is not int or not -3 <= rate <= 3:
        return {}
    saved = records(lesson)
    checked = {row['id']: row for row in verified if row.get('id')}
    if live and live.get('id'):
        checked[live['id']] = live
    result = {}
    context = {}
    for mode in MODES:
        plan, _ = make_plan(lesson, mode, {'voice': voice, 'rate': rate},
                            playback='both_controls' if mode == 'both' else 'separate', _context=context)
        identity = variant_id(plan)
        stored, state = saved.get(identity), checked.get(identity)
        if not plan['total']:
            phase = 'empty'
        elif not stored:
            phase = 'new'
        elif stored.get('keys') != plan['keys']:
            phase = 'stale'
        elif state is None or state.get('status') in {'checking', 'unknown'}:
            phase = 'checking'
        elif state.get('status') == 'running':
            phase = 'running'
        elif state.get('ready'):
            phase = 'ready'
        else:
            phase = 'partial'
        labels = {'empty': 'Chưa có lời đọc', 'new': 'Chưa tạo', 'stale': 'Cần cập nhật', 'checking': 'Đang kiểm tra',
                  'running': 'Đang tạo', 'ready': 'Đã tạo', 'partial': 'Cần tạo tiếp'}
        result[mode] = {'id': identity, 'phase': phase, 'label': labels[phase],
                        'ready': phase == 'ready', 'canCreate': phase in {'new', 'partial', 'stale'},
                        'title': variant_title(plan), 'total': plan['total']}
    return result


def inspection_for(lesson):
    return {"profile": {"units": [{"vi": s["vi"], "en": s["en"]} for s in lesson["segments"]]},
            "slide_speech": lesson.get("slide_speech", {})}


def signature(lesson):
    value = {"source": (lesson.get("source") or {}).get("sha256", ""),
             "units": [{"vi": s["vi"], "en": s["en"]} for s in lesson["segments"]],
             "speech": lesson.get("slide_speech", {})}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _plan_signature(lesson, context):
    if 'signature' not in context:
        context['signature'] = signature(lesson)
    return context['signature']


def make_plan(lesson, mode, voices, *, playback='separate', _context=None):
    if mode not in MODES:
        raise ValueError("Chọn tiếng Anh, tiếng Việt hoặc Việt + Anh.")
    selected = {**voices, **{lang: voices.get("voice", "") if lang in MODES[mode] else ""
                            for lang in ("vi", "en")}}
    keys = {}
    skipped = 0
    context = {} if _context is None else _context
    tasks_by_language = context.setdefault('plans', {})
    for lang in MODES[mode]:
        identity = lang, selected.get(lang, ''), selected['rate']
        if identity not in tasks_by_language:
            tasks, omitted, _ = narration_tasks(inspection_for(lesson), {**selected, **{other: ""
                                                      for other in ("vi", "en") if other != lang}})
            tasks_by_language[identity] = ([speech.audio_key(text, voice, selected["rate"])
                                          for text, voice in tasks], omitted)
        language_keys, omitted = tasks_by_language[identity]
        keys[lang] = list(language_keys)
        skipped += omitted
    if playback not in {'separate', 'both_controls'}:
        raise ValueError('Kiểu phát giọng không hợp lệ.')
    return {"version": 2, "mode": mode, "signature": _plan_signature(lesson, context), 'playback': playback,
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


def audio_status(lesson, directory, fallback_voices=None, *, cancel=None, _context=None):
    # Scope reuse to this single inspection, never across edits/file changes.
    context = {} if _context is None else _context
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
        record, _ = make_plan(lesson, "both", voices, _context=context)
    empty = {"status": "none", "mode": "none", "label": "Chỉ bài giảng song ngữ", "ready": False}
    if not isinstance(record, dict):
        return empty
    mode = record.get("mode", "none")
    if not isinstance(mode, str) or mode not in MODES:
        return empty
    if record.get("signature") != _plan_signature(lesson, context):
        return {**empty, "status": "stale", "mode": mode, "label": "Giọng đọc cần cập nhật"}
    if (not isinstance(record.get("voice"), str) or type(record.get("rate")) is not int
            or not -3 <= record["rate"] <= 3):
        return empty
    keys = record.get("keys", {})
    if not isinstance(keys, dict) or any(not isinstance(keys.get(lang, []), list) for lang in MODES[mode]):
        return empty
    expected, _ = make_plan(lesson, mode, {"voice": record["voice"], "rate": record["rate"]}, _context=context)
    if keys != expected["keys"]:
        return {**empty, "status": "stale", "mode": mode, "label": "Giọng đọc cần cập nhật"}
    all_keys = set(k for lang in MODES[mode] for k in keys.get(lang, []) if isinstance(k, str))
    valid = {}
    checked = context.setdefault('audio', {})
    for key in all_keys:
        if cancel is not None and cancel.is_set():
            raise InterruptedError('Đã dừng kiểm tra giọng đọc.')
        if key not in checked:
            checked[key] = valid_key(directory, key)
        valid[key] = checked[key]
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
            'id': variant_id(record), 'title': variant_title(record), 'playback': record.get('playback', 'separate'),
            "languages": list(MODES[mode]), "ready_languages": ready_languages,
            "label": "Có giọng " + LABELS[mode] if ready else "Giọng đọc chưa đủ" if complete else "Chưa tạo xong giọng đọc"}
