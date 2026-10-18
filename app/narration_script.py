"""Local narration overrides; slide text and its integrity signature stay intact."""

import copy
import re

from .input_analysis import language_of, split_existing_pair


def segments(lesson):
    from .picture_narration import without_image_suffix
    from .powerpoint import slide_for_locator

    saved = lesson.get('narration_script', {})
    saved = saved if isinstance(saved, dict) else {}
    result = []
    for row in lesson.get('segments', []):
        override = saved.get(row['id'], {})
        override = override if isinstance(override, dict) else {}
        text = {lang: override[lang] if isinstance(override.get(lang), str) else row.get(lang, '')
                for lang in ('vi', 'en')}
        if not override.get('manual'):
            captions = lesson.get('narration_image_text', {}).get(str(slide_for_locator(row['locator'])), [])
            text = {lang: without_image_suffix(value, captions, lang) for lang, value in text.items()}
        silent = row['id'] in lesson.get('narration_silent', [])
        result.append({**row, **{lang: '' if silent else text[lang] for lang in ('vi', 'en')},
                       'original_vi': text['vi'], 'original_en': text['en'], 'silent': silent,
                       'classification': classification(text['vi'], text['en'], manual=bool(override.get('manual')),
                                                        silent=silent)})
    return result


def classification(vi, en, *, manual=False, silent=False):
    if silent:
        return dict(confidence=1.0, reason='Giáo viên chọn slide không cần lời đọc', needs_review=False)
    if manual:
        return dict(confidence=1.0, reason='Lời đọc do giáo viên chỉnh', needs_review=False)
    if re.search(r'(?im)^\s*(?:VI|EN|Tiếng Việt|Tiếng Anh|Vietnamese|English)\s*[:：]', vi + '\n' + en):
        return dict(confidence=1.0, reason='Có nhãn ngôn ngữ rõ ràng', needs_review=False)
    evidence = [language_of(text) == lang for text, lang in ((vi, 'vi'), (en, 'en')) if text.strip()]
    if evidence and all(evidence):
        return dict(confidence=.9, reason='Nhận diện theo nội dung ngôn ngữ', needs_review=False)
    return dict(confidence=.4, reason='Chưa chắc ngôn ngữ; cần kiểm tra từ ngắn, công thức hoặc chữ trong ảnh',
                needs_review=True)


def classified(vi, en):
    """Use explicit language boundaries first; never manufacture translations."""
    pair = split_existing_pair(vi) if vi.strip() else None
    if pair and (not en.strip() or en.strip() == pair['en']):
        return pair['vi'], pair['en']
    pair = split_existing_pair(en) if en.strip() else None
    if pair and (not vi.strip() or vi.strip() == pair['vi']):
        return pair['vi'], pair['en']
    if vi.strip() and not en.strip():
        from .slide_speech import english_text

        parts = {'vi': [], 'en': []}
        for line in vi.splitlines():
            lang = language_of(line)
            if lang not in parts:
                lang = 'en' if english_text(line) else 'vi'
            parts[lang].append(line)
        if parts['en']:
            return '\n'.join(parts['vi']).strip(), '\n'.join(parts['en']).strip()
    return vi, en


def refresh_speech(lesson, *, edited=()):
    """Preserve native build timing unless a teacher explicitly changes that page."""
    from .powerpoint import slide_for_locator
    from .voice_import import script_speech

    edited = set(edited) | {slide_for_locator(row['locator']) for row in lesson.get('segments', [])
                            if lesson.get('narration_script', {}).get(row['id'], {}).get('manual')}

    generated = script_speech(lesson)
    if lesson.get('voice_only'):
        lesson['slide_speech'] = generated
        return
    original = lesson.setdefault('source_slide_speech', copy.deepcopy(lesson.get('slide_speech', {})))
    speech = copy.deepcopy(original) if original else generated
    pages = {row['slide']: row for row in generated['slides']}
    for page in speech.get('slides', []):
        native = page.get('englishSpeechSegments', [])
        replacement = pages.get(page['slide'])
        if replacement and (page['slide'] in edited or not any(s.get('status') == 'ready' for s in native)):
            page['englishSpeechSegments'] = replacement['englishSpeechSegments']
    lesson['slide_speech'] = speech


def prepare(library, lesson, *, new=False):
    """Repair once; new records are normalized before their first database write."""
    from .picture_narration import prepare as prepare_images

    image_changed = prepare_images(lesson, library)
    if lesson.get('narration_classification_version') == 1:
        if image_changed and not new:
            library._write(lesson)
        return lesson
    changed = 0
    for row in segments(lesson):
        if lesson.get('narration_script', {}).get(row['id'], {}).get('manual'):
            continue
        vi, en = classified(row['vi'], row['en'])
        if (vi, en) == (row['vi'], row['en']):
            continue
        if lesson.get('voice_only'):
            original = next(s for s in lesson['segments'] if s['id'] == row['id'])
            original.update(vi=vi, en=en, approved=False)
        else:
            lesson.setdefault('narration_script', {})[row['id']] = {'vi': vi, 'en': en}
        changed += 1
    lesson['narration_classification_version'] = 1
    if changed:
        from .chatgpt_handoff import text_signature
        from .library import now

        lesson.update(revision=lesson['revision'] + (0 if new else 1), updated_at=now(), narration_script_version=2)
        refresh_speech(lesson)
        if lesson.get('external_deck'):
            lesson['external_deck'].update(text_signature=text_signature(lesson), reviewed_revision=0)
        lesson.pop('prepared', None)
    if not new:
        library._write(lesson)
    return lesson
