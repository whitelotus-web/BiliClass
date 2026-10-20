"""Bounded, verified local completion of older converted presentations."""

from pathlib import Path

VERSION = 4


def complete_existing(library, lesson, cancel=None):
    from .google_conversion import original_source
    from .library import RevisionConflict
    from .powerpoint import verified_presentation
    from .slide_repair import repair_and_inspect

    quality = lesson.get('slide_quality', {})
    if lesson.get('voice_only') or not lesson.get('external_deck'):
        return lesson
    stamp = lesson['source']['sha256']
    if quality.get('completion_version') == VERSION and quality.get('completion_sha256') == stamp:
        return lesson
    if not quality.get('counts', {}).get('FAIL'):
        # Earlier checks could approve an oversized box while its text escaped
        # a painted panel. Audit only native converted decks with paired frames.
        if not any(row.get('pairs') for row in lesson['external_deck'].get('layout_plan', [])):
            return lesson
        from pptx import Presentation

        from .framed_text import escapes

        path = verified_presentation(lesson, library.directory)
        deck = Presentation(path)
        if not any(escapes(slide, deck.slide_width, deck.slide_height) for slide in deck.slides):
            return lesson
    else:
        path = verified_presentation(lesson, library.directory)
    if cancel and cancel.is_set():
        raise InterruptedError('Đã dừng hoàn thiện bài giảng.')
    result = repair_and_inspect(path, library.directory, source=original_source(library.directory, lesson),
                                mode=lesson.get('conversion_format', ''), cancel=cancel,
                                layout_plan=lesson.get('external_deck', {}).get('layout_plan'))
    if cancel and cancel.is_set():
        raise InterruptedError('Đã dừng hoàn thiện. Bản trước được giữ nguyên.')
    inspection = result['inspection']
    inspected = inspection['slide_quality']
    inspected.update(completion_version=VERSION, completion_sha256=inspection['slide_speech']['sha256'])
    # A concurrent edit/rename/trash must never be overwritten by a slow Office check.
    library.db.execute('BEGIN IMMEDIATE')
    try:
        current = library.get(lesson['id'])
        if current != lesson:
            raise RevisionConflict('Bài vừa thay đổi. Bấm mở hoặc tải lại để dùng bản mới nhất.')
        if Path(result['path']).resolve() != path.resolve():
            stored = library.store_source(Path(result['path']))
            updated = library.replace_external_presentation(lesson['id'], lesson['revision'], stored, inspection,
                                                             retain_audio=True)
        else:
            updated = library.update_slide_inspection(lesson['id'], inspection)
        return updated
    except BaseException:
        library.db.rollback()
        raise


def _retain_unchanged_audio(before, after):
    """Layout can change the source hash; only identical spoken tasks retain WAVs."""
    from collections import Counter

    from .lesson_narration import MODES, make_plan, records, signature, variant_id
    from .narration_script import segments
    from .slide_speech import speech_chunks

    old_signature = signature(before)
    active = variant_id(before.get('narration'))
    before_words, after_words = segments(before), segments(after)
    saved = {}
    for identity, record in records(before).items():
        updated = dict(record)
        same_words = all([speech_chunks(row[lang]) for row in before_words] == [speech_chunks(row[lang]) for row in after_words]
                         for lang in MODES[record['mode']])
        if record.get('signature') == old_signature and same_words:
            plan, _ = make_plan(after, record['mode'], record, playback=record.get('playback', 'separate'))
            # Geometry can change native reading order. Reorder existing WAV
            # references only when every utterance/key and multiplicity match.
            if (set(record.get('keys', {})) == set(plan['keys']) and all(
                    Counter(record['keys'][lang]) == Counter(plan['keys'][lang]) for lang in plan['keys'])):
                updated.update(signature=plan['signature'], revision=after['revision'], keys=plan['keys'])
        saved[variant_id(updated)] = updated
        if identity == active:
            after['narration'] = updated
    if saved:
        after['narration_variants'] = saved


def prepare_library_teaching(directory, identity, profile=None, cancel=None, *, narration=None):
    from .lesson_narration import audio_status, records
    from .teaching_session import prepare_teaching
    from .voice_import import prepare_library_lesson

    # Only a stored layout failure needs the bounded completion pass. Its
    # version/hash stamp prevents repeating an unsuccessful pass on each open.
    lesson, preview = prepare_library_lesson(directory, identity, profile, complete=True, cancel=cancel)
    if narration is not None:
        def choice(record):
            return record.get('mode'), record.get('voice'), record.get('rate'), record.get('playback', 'separate')

        lesson['narration'] = next((record for record in records(lesson).values()
                                    if choice(record) == choice(narration)), narration)
        if not audio_status(lesson, directory).get('ready'):
            raise ValueError('Lời đọc của bài đã thay đổi. Tạo tiếp giọng đã chọn trước khi mở bản có giọng.')
    # Keep the chosen ready voice; otherwise use a saved ready variant. Opening
    # never starts synthesis and an unfinished voice never blocks the deck itself.
    if narration is None:
        from .final_narration import select_final

        lesson = select_final(lesson, directory, cancel)
    prepared = prepare_teaching(lesson, preview, directory)
    return prepared
