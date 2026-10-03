"""Pre-render extracted narration as draft audio; never approve or play it."""


def prepare_narration(inspection, voices, directory, cancel, progress):
    from . import speech

    tasks = [(unit[language], voices[language]) for unit in inspection["profile"]["units"]
             for language in ("vi", "en") if unit[language].strip() and voices.get(language)]
    complete, skipped, errors = 0, 0, []
    for index, (text, voice) in enumerate(tasks, 1):
        if cancel.is_set():
            break
        if len(text) > 5000:
            skipped += 1
            continue
        progress(f"Chuẩn bị giọng đọc {index}/{len(tasks)}…")
        try:
            speech.synthesize(text, voice, voices["rate"], directory)
            complete += 1
        except Exception:
            # One unavailable voice must not discard a completed PowerPoint.
            errors.append(voice)
    return {"complete": complete, "skipped": skipped, "failed": len(errors), "total": len(tasks)}
