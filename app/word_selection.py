"""Map the continuous Word reading view back to immutable paragraph ranges."""

from .word_document import utf16_position


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
