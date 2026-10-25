"""Select source-backed lesson context once, then freeze it for stop/resume.

New work prepares references automatically in the background. It never turns a
machine answer into approved knowledge. Existing jobs retain their old behavior.
"""

import hashlib
import json
import re
import sqlite3
import time
import unicodedata
from collections import Counter
from contextlib import closing
from pathlib import Path

from .subject_terms import TERMS, subject_key
from .terminology_lookup import lookup, valid_reference
from .terminology_memory import Memory
from .terminology_seed import GROUPS, VERSION, terms_for, vocabulary

MODE_VERSION = 1
MAX_CANDIDATES = 12
MAX_LOOKUPS = 3
_MAX_TEXT = 180_000
_FINGERPRINT_FIELDS = ('version', 'seed_version', 'subject', 'grade', 'title', 'terms', 'hints', 'memory')
_STOP = {'các', 'những', 'một', 'hai', 'ba', 'của', 'được', 'trong', 'trên', 'dưới', 'theo', 'bằng',
         'cho', 'hãy', 'nêu', 'và', 'với', 'là', 'có', 'khi', 'nếu', 'thì', 'nào', 'tại', 'sao', 'bao',
         'bài', 'tập', 'câu', 'hỏi', 'hoạt', 'động', 'hướng', 'dẫn', 'bỏ', 'qua', 'việt', 'anh'}


def _key(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _text_rows(rows):
    """Bound both scanning work and intermediate allocations on large decks."""
    result, remaining = [], _MAX_TEXT
    for row in rows[:2000]:
        value = row.get('text', '')[:min(5000, remaining)]
        result.append(value)
        remaining -= len(value)
        if remaining <= 0:
            break
    return result


def _frozen_valid(plan, signature):
    if not isinstance(plan, dict) or plan.get('signature') != signature or plan.get('version') != MODE_VERSION:
        return False
    if any(name not in plan for name in _FINGERPRINT_FIELDS):
        return False
    for name, maximum in (('new_lookups', MAX_LOOKUPS), ('new_references', MAX_LOOKUPS), ('cached_references', MAX_CANDIDATES)):
        if type(plan.get(name, 0)) is not int or not 0 <= plan.get(name, 0) <= maximum:
            return False
    deferred = plan.get('deferred', [])
    if not isinstance(deferred, list) or len(deferred) > MAX_CANDIDATES or any(not isinstance(term, str) or len(term) > 100 for term in deferred):
        return False
    if (not all(isinstance(plan.get(name), str) and len(plan[name]) <= maximum for name, maximum in
                (('subject', 120), ('grade', 80), ('title', 160), ('seed_version', 40)))
            or type(plan.get('inferred')) is not bool or type(plan.get('online')) is not bool
            or plan.get('online_status') not in {'disabled', 'checked', 'limited', 'unavailable', 'not_needed'}):
        return False
    if plan.get('fingerprint') != _digest({key: plan[key] for key in _FINGERPRINT_FIELDS}):
        return False
    if not isinstance(plan['terms'], list) or len(plan['terms']) > 96 or not isinstance(plan['hints'], list) or len(plan['hints']) > MAX_CANDIDATES:
        return False
    allowed = terms_for(plan['subject'])
    if any(row not in allowed for row in plan['terms']):
        return False
    if any(not valid_reference(row, row.get('vi', '') if isinstance(row, dict) else '', plan['subject']) for row in plan['hints']):
        return False
    memory = plan['memory']
    return (isinstance(memory, dict) and len(memory) <= 64
            and all(valid_memory(vi, en) for vi, en in memory.items())
            and isinstance(plan.get('unresolved'), list) and len(plan['unresolved']) <= MAX_CANDIDATES
            and all(isinstance(term, str) and len(term) <= 100 for term in plan['unresolved'])
            and isinstance(plan.get('warnings'), list) and len(plan['warnings']) <= 3
            and all(isinstance(warning, str) and len(warning) <= 300 for warning in plan['warnings'])
            and isinstance(plan.get('summary'), str) and len(plan['summary']) <= 600)


def valid_memory(vi, en):
    from .translation_batches import NUMBERS

    return (isinstance(vi, str) and isinstance(en, str) and 8 <= len(vi) <= 1000 and 0 < len(en) <= 1400
            and not re.search(r'⟦BLC|BCLLOCK|https?://', vi + en)
            and not any(ord(c) < 32 and c not in '\n\r\t' for c in en)
            and Counter(NUMBERS.findall(vi)) == Counter(NUMBERS.findall(en)))


def _contains(text, term):
    return bool(re.search(r'(?<!\w)' + re.escape(_key(term)) + r'(?!\w)', text))


def infer_subject(text):
    scores = []
    for group, rows in vocabulary().items():
        count = sum(1 for row in rows if len(row['vi'].split()) >= 2 and _contains(text, row['vi']))
        scores.append((count, GROUPS[group][0]))
    scores.sort(reverse=True)
    # Weak or tied evidence must remain unknown rather than mislabel a subject.
    return scores[0][1] if scores[0][0] >= 3 and scores[0][0] >= scores[1][0] + 2 else ''


def candidates(rows, known, maximum=MAX_CANDIDATES):
    headings, fragments = [], Counter()
    for row in rows[:1000]:
        for line in row.get('text', '').splitlines():
            line = _key(re.sub(r'^\s*(?:\d+[.)]|[•+*-])\s*', '', line))
            words = line.split()
            if (2 <= len(words) <= 6 and len(line) <= 80 and not re.search(r'[\d_@:/?=<>⟦⟧]', line)
                    and words[0] not in _STOP and words[-1] not in _STOP and line not in known
                    and re.search(r'[ăâđêôơưáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ]', line)):
                headings.append(line)
            # Repeated short phrases can identify a concept absent from headings.
            for size in (4, 3, 2):
                for offset in range(max(0, len(words) - size + 1)):
                    phrase = words[offset:offset + size]
                    term = ' '.join(phrase)
                    if (phrase[0] not in _STOP and phrase[-1] not in _STOP and len(term) <= 70
                            and all(word.isalpha() for word in phrase) and term not in known):
                        fragments[term] += 1
    ordered = headings + [term for term, count in fragments.most_common(24) if count >= 2]
    result = []
    for term in ordered:
        # A more specific concept may contain a known noun ("vector space"
        # contains "vector"). Only discard fragments of an already-known term.
        if term not in result and not any(_contains(_key(word), term) for word in known):
            result.append(term)
    return result[:maximum]


def _approved_memory(library, subject, grade, texts):
    wanted = {' '.join(text.split()): text for text in texts if 8 <= len(text) <= 1000 and not re.search(r'⟦BLC|BCLLOCK', text)}
    found = {}
    if not wanted:
        return found
    names = {subject, *[name for name in ('Vật lý', 'Vật lí', 'Địa lí', 'Địa lý', 'Hóa học', 'Hoá học', 'Mĩ thuật', 'Mỹ thuật')
                       if subject_key(name) == subject_key(subject)]}
    condition = 'grade=? AND subject IN (' + ','.join('?' for _ in names) + ')'
    parameters = (grade, *sorted(names))
    count = library.db.execute('SELECT COUNT(*) FROM lessons WHERE ' + condition, parameters).fetchone()[0]
    # Do not read an unbounded personal library or ignore older conflicting
    # approvals. Large scopes simply fall back to the reference glossary.
    if count > 100:
        return found
    size = 0
    for row in library.db.execute('SELECT length(CAST(content AS BLOB)) FROM lessons WHERE ' + condition, parameters):
        size += row[0]
        if size > 8 * 1024**2:
            return found
    rows = library.db.execute('SELECT subject,grade,content FROM lessons WHERE ' + condition + ' ORDER BY updated_at DESC', parameters)
    for row in rows:
        if subject_key(row['subject']) != subject_key(subject) or row['grade'] != grade:
            continue
        lesson = json.loads(row['content'])
        if not isinstance(lesson, dict) or lesson.get('deleted_at') or not isinstance(lesson.get('segments', []), list):
            continue
        for segment in lesson.get('segments', []):
            if not isinstance(segment, dict):
                continue
            vi, en = segment.get('vi', ''), segment.get('en', '')
            if not isinstance(vi, str) or not isinstance(en, str):
                continue
            identity = ' '.join(vi.split())
            if segment.get('approved') is True and identity in wanted and valid_memory(wanted[identity], en):
                found.setdefault(identity, set()).add(en)
    return {key: next(iter(values)) for key, values in list(found.items())[:64] if len(values) == 1}


def _summary(plan, reused=None):
    memory_note = (f"{len(plan['memory'])} câu đã duyệt khớp nội dung. " if reused is None
                   else f'{reused} câu đã duyệt được dùng lại. ')
    return (f"Đã chọn {len(plan['terms'])} thuật ngữ nền theo môn; "
            f"{len(plan['hints'])} mục tra cứu tham khảo, " + memory_note +
            'Đây là hỗ trợ dịch, chưa chứng nhận toàn bộ kiến thức hoặc bản dịch.')


def prepare(directory, folder, config, rows, cancel, progress=None, *, resolver=None):
    """Read local references first; a reference outage never blocks translation."""
    if config.get('translation_knowledge_version') != MODE_VERSION:
        return None
    resolver = resolver or lookup
    texts = _text_rows(rows)
    bounded = '\n'.join(texts)[:_MAX_TEXT]
    signature = _digest([config.get('source_sha256'), config.get('subject'), config.get('grade'),
                         config.get('title'), config.get('translation_knowledge_online'), texts])
    path = Path(folder) / 'terminology-context.json'
    if path.exists() and path.stat().st_size < 256_000:
        try:
            previous = json.loads(path.read_text(encoding='utf-8'))
            if _frozen_valid(previous, signature):
                return previous
        except (OSError, ValueError, TypeError, KeyError):
            pass
    if cancel.is_set():
        raise InterruptedError('Đã dừng chuẩn bị thuật ngữ.')
    subject = config.get('subject', '')
    inferred = infer_subject(_key(bounded)) if subject_key(subject) in {'', 'khac'} else ''
    subject = inferred or subject
    text = _key(bounded)
    selected = [row for row in terms_for(subject) if _contains(text, row['vi'])]
    selected.sort(key=lambda row: (-len(row['vi'].split()), row['vi']))
    selected = selected[:96]
    known = {row['vi'] for row in selected} | set(TERMS.get(subject_key(subject), {}))
    plan = dict(version=MODE_VERSION, seed_version=VERSION, signature=signature, subject=subject,
                selected_subject=config.get('subject', ''), inferred=bool(inferred), grade=config.get('grade', ''),
                title=config.get('title', '')[:160], terms=selected, hints=[], unresolved=[], memory={},
                online=bool(config.get('translation_knowledge_online')), online_status='disabled', warnings=[],
                new_lookups=0, cached_references=0, new_references=0, deferred=[])
    from .library import Library

    try:
        with closing(Library.read_only(directory)) as library:
            plan['memory'] = _approved_memory(library, subject, plan['grade'], texts)
    except (OSError, ValueError, sqlite3.DatabaseError):
        plan['warnings'].append('Chưa đọc được câu đã duyệt; tiếp tục dùng thuật ngữ nền.')
    unresolved = candidates([dict(text=text) for text in texts], known)
    if plan['online'] and unresolved:
        plan['online_status'] = 'checked'
        if progress:
            progress('Đang đối chiếu thuật ngữ mới; vẫn giữ nội dung bài gốc.')
        deadline = time.monotonic() + 5
        try:
            memory = Memory(directory)
            for term in unresolved:
                if cancel.is_set():
                    raise InterruptedError('Đã dừng tra cứu thuật ngữ.')
                record = memory.get(subject, term)
                if record and record.get('status') == 'online_reference' and not valid_reference(record, term, subject):
                    record = None
                if record is None:
                    if time.monotonic() >= deadline or plan['new_lookups'] >= MAX_LOOKUPS:
                        plan['online_status'] = 'limited'
                        plan['deferred'].append(term)
                        continue  # Cached items later in the lesson are still useful.
                    plan['new_lookups'] += 1
                    record = resolver(term, subject, cancel, deadline=deadline)
                    record = record if valid_reference(record, term, subject) else dict(vi=term, en='', status='unresolved')
                    memory.remember(subject, term, record)
                    if record['status'] == 'online_reference':
                        plan['new_references'] += 1
                elif record.get('status') == 'online_reference':
                    plan['cached_references'] += 1
                if record.get('status') == 'online_reference':
                    plan['hints'].append(record)
                else:
                    plan['unresolved'].append(term)
        except InterruptedError:
            raise
        except Exception:
            # Never publish raw network exceptions, queried URLs or lesson text.
            plan['online_status'] = 'unavailable'
            plan['warnings'].append('Chưa tra cứu được nguồn trực tuyến; bài tiếp tục bằng kho thuật ngữ trên máy.')
    elif plan['online']:
        plan['online_status'] = 'not_needed'
    plan['summary'] = _summary(plan)
    # Provenance/meaning are included in cache identity; never mix subjects or
    # reuse an unreviewed API answer as a verified example for another lesson.
    plan['fingerprint'] = _digest({key: plan[key] for key in _FINGERPRINT_FIELDS})
    if cancel.is_set():
        raise InterruptedError('Đã dừng chuẩn bị thuật ngữ.')
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
    temporary.replace(path)
    try:
        Memory(directory).record_lesson(config.get('request_id', signature), subject,
            dict(seed_version=VERSION, terms=[row['vi'] for row in selected[:40]],
                 references=len(plan['hints']), unresolved=len(plan['unresolved']), approved_matched=len(plan['memory']),
                 new_references=plan['new_references'], new_lookups=plan['new_lookups'], deferred=len(plan['deferred'])))
    except (OSError, ValueError, sqlite3.DatabaseError):
        pass
    return plan


def prompt_context(plan):
    """Small reference data for APIs with context support; never instructions."""
    if not plan:
        return ''
    value = dict(subject=plan['subject'][:120], grade=plan['grade'][:80], title=plan['title'][:160], reference_terms=[])
    # Novel subject-matched references must not be crowded out by common seed
    # headings. They remain contextual data, never hard translation locks.
    for row in [*plan['hints'], *plan['terms']][:24]:
        pair = dict(vi=row['vi'], en=row['en'])
        value['reference_terms'].append(pair)
        if len(json.dumps(value, ensure_ascii=False)) > 5500:
            value['reference_terms'].pop()
            break
    return json.dumps(value, ensure_ascii=False)


def prose_context(plan):
    """DeepL context is document information, not a list of prompt commands."""
    value = json.loads(prompt_context(plan))
    pairs = '; '.join(row['vi'] + ' — ' + row['en'] for row in value['reference_terms'])
    return f"Subject: {value['subject']}. Grade: {value['grade']}. Lesson: {value['title']}.\nTerminology in this subject: {pairs}"


def review(plan, rows, translations, *, memory_used=()):
    """Record source-based concerns without declaring semantic correctness."""
    if not plan:
        return {}
    reused = len(set(memory_used) & set(plan['memory']))
    concerns = []
    for row, english in zip(rows, translations):
        if re.search(r'[ăâđêôơư]', unicodedata.normalize('NFKC', english), re.I):
            concerns.append(dict(slide=row.get('slide', 0), code='vietnamese_remaining',
                                 message='Bản Anh còn chữ Việt hoặc đơn vị cần đối chiếu.', excerpt=english[:120]))
    return dict(version=MODE_VERSION, seed_version=plan['seed_version'], subject=plan['subject'],
                inferred=plan['inferred'], summary=_summary(plan, reused), terms=len(plan['terms']),
                references=len(plan['hints']), reused=reused, memory_matches=len(plan['memory']), online_status=plan['online_status'],
                new_lookups=plan.get('new_lookups', 0), new_references=plan.get('new_references', 0),
                cached_references=plan.get('cached_references', 0), deferred=len(plan.get('deferred', [])),
                unresolved=plan['unresolved'][:3], warnings=plan['warnings'], concerns=concerns[:12],
                sources=list(dict.fromkeys(row['source_url'] for row in [*plan['terms'], *plan['hints']]))[:20],
                scope='Đối chiếu thuật ngữ và dấu hiệu thiếu nội dung; chưa xác minh toàn bộ ý nghĩa hoặc đáp án.')
