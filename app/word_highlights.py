"""Transient source-selection marks; never change source text or DOCX styling."""

from bisect import bisect_right

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


class SourceHighlights(QSyntaxHighlighter):
    def __init__(self, document):
        self.ranges, self.ends = [], []
        self.mark = QTextCharFormat()
        self.mark.setBackground(QColor('#dbeafe'))
        super().__init__(document)

    def set_ranges(self, ranges):
        merged = []
        for start, end in sorted(ranges):
            if start >= end:
                continue
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
            else:
                merged.append((start, end))
        if merged == self.ranges:
            return
        affected = set()
        document = self.document()
        for start, end in [*self.ranges, *merged]:
            block = document.findBlock(start)
            while block.isValid() and block.position() < end:
                affected.add(block.position())
                block = block.next()
        self.ranges, self.ends = merged, [end for _, end in merged]
        for position in sorted(affected):
            self.rehighlightBlock(document.findBlock(position))

    def highlightBlock(self, _text):
        block = self.currentBlock()
        start, end = block.position(), block.position() + block.length() - 1
        for left, right in self.ranges[bisect_right(self.ends, start):]:
            if left >= end:
                break
            self.setFormat(max(start, left) - start, min(end, right) - max(start, left), self.mark)
