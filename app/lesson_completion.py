"""Bounded, verified local completion of older converted presentations."""

from pathlib import Path

VERSION = 1


def complete_existing(library, lesson, cancel=None):
    from .google_conversion import original_source
    from .library import RevisionConflict
    from .powerpoint import verified_presentation
    from .slide_repair import repair_and_inspect

    quality = lesson.get('slide_quality', {})
    if (lesson.get('voice_only') or not lesson.get('external_deck')
            or not quality.get('counts', {}).get('FAIL')):
        return lesson
    path = verified_presentation(lesson, library.directory)
    stamp = lesson['source']['sha256']
    if quality.get('completion_version') == VERSION and quality.get('completion_sha256') == stamp:
        return lesson
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
    from .lesson_narration import MODES, make_plan, records, signature, variant_id
    from .narration_script import segments

    old_signature = signature(before)
    active = variant_id(before.get('narration'))
    before_words, after_words = segments(before), segments(after)
    saved = {}
    for identity, record in records(before).items():
        updated = dict(record)
        same_words = all([row[lang] for row in before_words] == [row[lang] for row in after_words]
                         for lang in MODES[record['mode']])
        if record.get('signature') == old_signature and same_words:
            plan, _ = make_plan(after, record['mode'], record, playback=record.get('playback', 'separate'))
            if record.get('keys') == plan['keys']:
                updated.update(signature=plan['signature'], revision=after['revision'])
        saved[variant_id(updated)] = updated
        if identity == active:
            after['narration'] = updated
    if saved:
        after['narration_variants'] = saved


def layout_notice(lesson):
    count = lesson.get('slide_quality', {}).get('counts', {}).get('FAIL', 0)
    if count and not lesson.get('voice_only'):
        return f'Đã thử tự căn chỉnh; còn {count} slide cần xem lại bố cục trong PowerPoint. Bản gốc được giữ nguyên.'
    return ''


def prepare_library_teaching(directory, identity, profile=None, cancel=None, *, narration=None):
    from .lesson_narration import audio_status, records
    from .teaching_session import prepare_teaching
    from .voice_import import prepare_library_lesson

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
    if narration is None and not audio_status(lesson, directory).get('ready'):
        lesson['narration'] = next((record for record in records(lesson).values()
                                    if audio_status({**lesson, 'narration': record}, directory).get('ready')),
                                   {'version': 2, 'mode': 'none'})
    prepared = prepare_teaching(lesson, preview, directory)
    prepared['warning'] = ' '.join(filter(None, (layout_notice(lesson), prepared.get('warning'))))
    return prepared
