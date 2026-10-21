"""Fast, read-only filtering of the catalog already published to Qt."""

import math
import unicodedata


def folded(text):
    text = unicodedata.normalize('NFD', str(text).casefold().replace('đ', 'd'))
    return ''.join(c for c in text if not unicodedata.combining(c))


def options(rows, kind):
    if kind == 'subject':
        values = sorted({row['subject'] for row in rows}, key=folded)
        return [{'id': '', 'label': 'Tất cả môn học'}] + [{'id': value, 'label': value} for value in values]
    values = {(row['education_level'], row['grade']) for row in rows}
    return [{'id': '', 'label': 'Tất cả khối lớp'}] + [
        {'id': level + '|' + grade, 'label': level + ' · Khối ' + grade}
        for level, grade in sorted(values, key=lambda pair: (pair[0], int(pair[1]) if pair[1].isdigit() else 999, pair[1]))]


def is_ready(row):
    return row['status'] == 'READY_TO_TEACH' and not row.get('quality_failures')


def voice_matches(row, voice):
    audio = row.get('narration', {})
    variants = audio.get('variants', [])
    if not variants and audio.get('mode') in {'en', 'vi', 'both'}:
        variants = [audio]  # Single recording from an older version.
    if voice in {'en', 'vi', 'both'}:
        languages = {language for variant in variants if variant.get('ready')
                     for language in (('vi', 'en') if variant.get('mode') == 'both' else (variant.get('mode'),))}
        return {'vi', 'en'} <= languages if voice == 'both' else voice in languages
    if voice == 'none':
        return not any(v.get('ready') for v in variants) and audio.get('status') != 'checking'
    if voice == 'partial':
        return any(not v.get('ready') for v in variants)
    return True


def query(rows, text='', subject='', grade='', state='', voice='', page=1, page_size=20):
    words = folded(text).split()
    selected = []
    for row in rows:
        haystack = folded(' '.join(str(row.get(k, '')) for k in ('title', 'subject', 'education_level', 'grade')))
        if (any(word not in haystack for word in words) or subject and row['subject'] != subject
                or grade and row['education_level'] + '|' + row['grade'] != grade
                or state == 'ready' and not is_ready(row)
                or state == 'review' and (is_ready(row) or row['status'] == 'DRAFT')
                or state == 'draft' and row['status'] != 'DRAFT'
                or not voice_matches(row, voice)):
            continue
        selected.append(row)
    pages = max(1, math.ceil(len(selected) / page_size))
    page = max(1, min(page, pages))
    start = (page - 1) * page_size
    return {'rows': selected[start:start + page_size], 'ids': [row['id'] for row in selected], 'total': len(selected), 'all': len(rows), 'page_size': page_size,
            'page': page, 'pages': pages, 'start': start + 1 if selected else 0,
            'end': min(start + page_size, len(selected))}
