"""Map the continuous Word reading view back to immutable paragraph ranges."""

import unicodedata

from .word_document import utf16_position


def complete_word_ranges(paragraphs, ranges):
    """Extend clipped edge words without selecting extra sentences or rows."""
    text_by_id = {row['id']: row['text'] for row in paragraphs}

    def word_character(char):
        return char.isalnum() or char == '_' or unicodedata.category(char).startswith('M')

    result = []
    for region in ranges:
        text = text_by_id[region['paragraph']]
        start, end = region['start'], region['end']
        while 0 < start < len(text) and word_character(text[start]) and word_character(text[start - 1]):
            start -= 1
        while 0 < end < len(text) and word_character(text[end - 1]) and word_character(text[end]):
            end += 1
        result.append({**region, 'start': start, 'end': end})
    return result


def review_groups(paragraphs, regions):
    """Group adjacent display ranges while keeping the saved DOCX edits separate."""
    rows = {row['id']: (index, row['text']) for index, row in enumerate(paragraphs)}
    groups, previous = [], None
    for index, region in enumerate(regions):
        order, source = rows[region['paragraph']]
        adjacent = previous and (
            previous['paragraph'] == region['paragraph'] and previous['end'] == region['start']
            or rows[previous['paragraph']][0] + 1 == order
            and previous['end'] == len(rows[previous['paragraph']][1]) and region['start'] == 0)
        member = {**region, 'review_index': index}
        if not adjacent:
            groups.append(dict(id=region['id'], members=[], vi=''))
        group = groups[-1]
        separator = '\n' if previous and previous['paragraph'] != region['paragraph'] else ''
        group['vi'] += (separator if group['members'] else '') + region['vi']
        group['members'].append(member)
        previous = region
    return groups


class TextSelection:
    def __init__(self, paragraphs):
        parts, self.spans, position = [], [], 0
        for row in paragraphs:
            original = row['text']
            text, boundaries = original, None
            if '\r' in original:
                chars, boundaries, index = [], [0], 0
                while index < len(original):
                    char = original[index]
                    index += 1
                    if char == '\r':
                        if index < len(original) and original[index] == '\n':
                            index += 1
                        char = '\n'
                    chars.append(char)
                    boundaries.append(index)
                text = ''.join(chars)
            if parts:
                parts.append('\n\n')
                position += 2
            self.spans.append((position, position + len(text), row, boundaries))
            parts.append(text)
            position += len(text)
        self.text = ''.join(parts)

    def ranges(self, start, end):
        start, end = utf16_position(self.text, start), utf16_position(self.text, end)
        if start >= end:
            raise ValueError('Bôi đen phần văn bản cần dịch trước.')
        selected, skipped = [], 0
        for left, right, row, boundaries in self.spans:
            begin, finish = max(left, start), min(right, end)
            if begin >= finish or not self.text[begin:finish].strip():
                continue
            if not row['editable']:
                skipped += 1
                continue
            begin, finish = begin - left, finish - left
            selected.append(dict(paragraph=row['id'],
                start=boundaries[begin] if boundaries is not None else begin,
                end=boundaries[finish] if boundaries is not None else finish))
        if not selected:
            raise ValueError('Vùng bôi đen chưa có phần chữ dịch được. Chọn lại phần văn bản; hình, công thức và đoạn đang khóa được giữ nguyên.')
        return selected, skipped
