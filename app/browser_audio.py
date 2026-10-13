"""Pre-render extracted narration as draft audio; never approve or play it."""


def prepare_narration(inspection, voices, directory, cancel, progress):
    from . import speech
    from .conversion_progress import emit_progress
    from .slide_speech import speech_chunks

    data = inspection.get("slide_speech")
    if data:
        texts = [(unit["vi"], "vi") for unit in inspection["profile"]["units"] if unit["vi"].strip()]
        texts.extend((segment["english_text"], "en") for slide in data["slides"]
                     for segment in slide["englishSpeechSegments"] if segment["status"] == "ready")
    else:
        texts = [(unit[language], language) for unit in inspection["profile"]["units"]
                 for language in ("vi", "en") if unit[language].strip()]
    tasks, skipped = [], 0
    for text, language in texts:
        if not voices.get(language):
            continue
        try:
            tasks.extend((part, voices[language]) for part in speech_chunks(text))
        except ValueError:
            skipped += 1
    duplicates = len(tasks)
    tasks = list(dict.fromkeys(tasks))
    duplicates -= len(tasks)
    complete, cached, errors = 0, 0, []
    emit_progress(progress, "audio", f"Chuẩn bị {len(tasks)} đoạn giọng đọc khác nhau…", 0, len(tasks))
    for index, (text, voice) in enumerate(tasks, 1):
        if cancel.is_set():
            break
        if len(text) > 5000:
            skipped += 1
            continue
        emit_progress(progress, "audio", f"Chuẩn bị giọng đọc {index}/{len(tasks)}…", index-1, len(tasks))
        try:
            result = speech.synthesize(text, voice, voices["rate"], directory)
            cached += bool(result and result.get("cached"))
            complete += 1
        except Exception:
            # One unavailable voice must not discard a completed PowerPoint.
            errors.append(voice)
        emit_progress(progress, "audio", f"Đã xử lý {index}/{len(tasks)} đoạn giọng đọc…", index, len(tasks))
    return {"complete": complete, "cached": cached, "duplicates": duplicates,
            "skipped": skipped, "failed": len(errors), "total": len(tasks)+skipped}
