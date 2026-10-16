"""Teacher-owned terminology and exact classroom headings for Google Basic."""

import hashlib
import json
import re
import unicodedata

HEADINGS = {
    'khởi động': 'Warm-up', 'mở đầu': 'Introduction',
    'nội dung bài học': 'Lesson outline', 'trả lời': 'Answer',
    'kết luận': 'Conclusion', 'vận dụng': 'Application',
    'phiếu học tập': 'Worksheet', 'hướng dẫn về nhà': 'Homework',
    'hướng dẫn vẽ đồ thị': 'Graphing instructions',
}


def normalized(value):
    return unicodedata.normalize('NFC', value).casefold().strip()


class TermPolicy:
    def __init__(self, subject='', rows=()):
        self.subject = normalized(subject)
        candidates = {}
        for row in rows:
            if row.get('locked') and row.get('vi', '').strip() and row.get('en', '').strip():
                candidates.setdefault(normalized(row['vi']), set()).add(row['en'].strip())
        self.terms = {vi: next(iter(targets)) for vi, targets in candidates.items() if len(targets) == 1}
        self.ambiguous = [vi for vi, targets in candidates.items() if len(targets) > 1]
        self.pattern = re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(t) for t in sorted(self.terms, key=len, reverse=True)) + r')(?!\w)', re.I) if self.terms else None

    def matches(self, text):
        return {normalized(m.group()): self.terms[normalized(m.group())] for m in self.pattern.finditer(unicodedata.normalize('NFC', text))} if self.pattern else {}

    def exact(self, text):
        key = normalized(text)
        if key in self.terms:
            return self.terms[key]
        return HEADINGS.get(key)

    def fingerprint(self, matches):
        raw = json.dumps([self.subject, sorted(matches.items())], ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()
