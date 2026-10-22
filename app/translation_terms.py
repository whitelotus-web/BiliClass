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
    'định nghĩa': 'Definition', 'nội dung': 'Contents', 'lời giải': 'Solution',
    'bài giải': 'Solution', 'chú ý': 'Note', 'nhận xét': 'Observation',
}
# Whole headings only: sentence translations still keep their own grammar.
# Geometry assumptions are axioms/postulates, not "recognizational properties".
MATH_HEADINGS = {
    'khái niệm mở đầu': 'Introductory concepts',
    'các tính chất thừa nhận': 'Basic axioms',
    'cách xác định một mặt phẳng': 'Determining a plane',
    'hình chóp và hình tứ diện': 'Pyramids and tetrahedra',
    'các ví dụ minh họa': 'Illustrative examples',
    'bài tập': 'Exercises',
}
_NUMBERED = re.compile(r'^(phiếu học tập số|hoạt động|luyện tập|nhiệm vụ|vận dụng|ví dụ|hđ|bài|bai|chương|chuong|câu|cau|mục|muc)\s*(\d+(?:\.\d+)*|[IVXLCDM]+|⟦BLC\d+⟧)(?!\w)', re.I)
_LABELS = {'bài':'Lesson', 'bai':'Lesson', 'chương':'Chapter', 'chuong':'Chapter',
           'câu':'Question', 'cau':'Question', 'mục':'Section', 'muc':'Section',
           'hoạt động':'Activity', 'hđ':'Activity', 'luyện tập':'Practice',
           'nhiệm vụ':'Task', 'vận dụng':'Application', 'ví dụ':'Example', 'phiếu học tập số':'Worksheet'}


def numbered_heading(text):
    match = _NUMBERED.match(unicodedata.normalize('NFC', text).strip())
    return (match[0], _LABELS[match[1].casefold()] + ' ' + match[2]) if match else None


def normalized(value):
    return unicodedata.normalize('NFC', value).casefold().strip().replace('hoá', 'hóa')


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
        self.teacher_terms = teacher_terms
        self.identity_terms = {vi for vi,en in self.terms.items() if normalized(en) == vi and vi not in teacher_terms}
        self.ambiguous = [vi for vi, targets in candidates.items() if len(targets) > 1]
        for term in self.ambiguous:
            self.terms.pop(term, None)
        # Short polysemous words (e.g. công) are exact-only. A teacher can
        # explicitly lock an inline use; defaults protect multiword terms.
        # In chemistry, locking a singular noun inside a larger phrase prevents
        # Google from producing e.g. "molecular formula" or plural "atoms".
        # Keep noun definitions exact-only; teachers' explicit locks still win.
        inline_defaults = self.identity_terms | {'cộng hóa trị'} if self.subject == 'hoa hoc' else {
            vi for vi in self.terms if ' ' in vi}
        self.inline_terms = {vi:en for vi,en in self.terms.items() if vi in teacher_terms or vi in inline_defaults}
        variants = {variant for term in self.inline_terms for variant in (term, term.replace('hóa','hoá'))}
        self.pattern = re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(t) for t in sorted(variants, key=lambda t:(-len(t),t))) + r')(?!\w)', re.I) if variants else None

    def matches(self, text):
        matches = {normalized(m.group()): self.inline_terms[normalized(m.group())] for m in self.pattern.finditer(unicodedata.normalize('NFC', text))} if self.pattern else {}
        heading = numbered_heading(text)
        if heading and not any(normalized(heading[0]) in term for term in matches):
            matches[normalized(heading[0])] = heading[1]
        return matches

    def exact(self, text):
        key = normalized(text)
        if key in self.terms:
            return text.strip() if key in self.identity_terms else self.terms[key]
        if self.subject == 'toan' and key in MATH_HEADINGS:
            return MATH_HEADINGS[key]
        if key in HEADINGS:
            return HEADINGS[key]
        heading_key = key.rstrip(':.!? ').strip()
        if heading_key in self.terms or heading_key in HEADINGS:
            suffix = text.strip()[len(text.strip().rstrip(':.!? ')):].strip()
            return self.terms.get(heading_key, HEADINGS.get(heading_key)) + suffix
        if self.subject == 'toan':
            from .math_translation import exact

            value = exact(text)
            if value is not None and not any(term in key for term in self.teacher_terms):
                return value
        heading = numbered_heading(text)
        if heading:
            stripped = text.strip()
            tail = stripped[len(heading[0]):]
            if re.fullmatch(r'\s*[:.)]?\s*', tail):
                return heading[1] + tail.strip()
        return None

    def postprocess(self, text, translated):
        if self.subject == 'toan' and not any(term in normalized(text) for term in self.teacher_terms):
            from .math_translation import terminology

            return terminology(text, translated)
        return translated

    def fingerprint(self, matches):
        raw = json.dumps([self.subject, sorted(matches.items())], ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()
