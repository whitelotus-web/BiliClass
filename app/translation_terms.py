"""Teacher-owned terminology and exact classroom headings for Google Basic."""

import hashlib
import json
import re
import unicodedata

from .subject_terms import TERMS, subject_key

HEADINGS = {
    'khởi động': 'Warm-up', 'mở đầu': 'Introduction',
    'nội dung bài học': 'Lesson outline', 'trả lời': 'Answer',
    'kết luận': 'Conclusion', 'vận dụng': 'Application',
    'phiếu học tập': 'Worksheet', 'hướng dẫn về nhà': 'Homework',
    'hướng dẫn vẽ đồ thị': 'Graphing instructions',
}
_NUMBERED = re.compile(r'^(bài|bai|chương|chuong|câu|cau|mục|muc)\s*(\d+(?:\.\d+)*|[IVXLCDM]+|⟦BLC\d+⟧)(?!\w)', re.I)
_LABELS = {'bài':'Lesson', 'bai':'Lesson', 'chương':'Chapter', 'chuong':'Chapter',
           'câu':'Question', 'cau':'Question', 'mục':'Section', 'muc':'Section'}


def numbered_heading(text):
    match = _NUMBERED.match(unicodedata.normalize('NFC', text).strip())
    return (match[0], _LABELS[match[1].casefold()] + ' ' + match[2]) if match else None


def normalized(value):
    return unicodedata.normalize('NFC', value).casefold().strip()


class TermPolicy:
    def __init__(self, subject='', rows=()):
        self.subject = subject_key(subject)
        candidates = {}
        for row in rows:
            if row.get('subject') and subject_key(row['subject']) != self.subject:
                continue
            if row.get('locked') and row.get('vi', '').strip() and row.get('en', '').strip():
                candidates.setdefault(normalized(row['vi']), set()).add(row['en'].strip())
        self.terms = dict(TERMS.get(self.subject, {}))
        teacher_terms = {vi: next(iter(targets)) for vi, targets in candidates.items() if len(targets) == 1}
        self.terms.update(teacher_terms)
        self.ambiguous = [vi for vi, targets in candidates.items() if len(targets) > 1]
        for term in self.ambiguous:
            self.terms.pop(term, None)
        # Short polysemous words (e.g. công) are exact-only. A teacher can
        # explicitly lock an inline use; defaults protect multiword terms.
        self.inline_terms = {vi:en for vi,en in self.terms.items() if ' ' in vi or vi in teacher_terms}
        self.pattern = re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(t) for t in sorted(self.inline_terms, key=len, reverse=True)) + r')(?!\w)', re.I) if self.inline_terms else None

    def matches(self, text):
        matches = {normalized(m.group()): self.inline_terms[normalized(m.group())] for m in self.pattern.finditer(unicodedata.normalize('NFC', text))} if self.pattern else {}
        heading = numbered_heading(text)
        if heading and not any(normalized(heading[0]) in term for term in matches):
            matches[normalized(heading[0])] = heading[1]
        return matches

    def exact(self, text):
        key = normalized(text)
        if key in self.terms:
            return self.terms[key]
        if key in HEADINGS:
            return HEADINGS[key]
        heading = numbered_heading(text)
        if heading:
            stripped = text.strip()
            tail = stripped[len(heading[0]):]
            if re.fullmatch(r'\s*[:.)]?\s*', tail):
                return heading[1] + tail.strip()
        return None

    def fingerprint(self, matches):
        raw = json.dumps([self.subject, sorted(matches.items())], ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()
