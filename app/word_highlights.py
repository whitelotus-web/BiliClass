"""Transient source-selection marks; never change source text or DOCX styling."""

from bisect import bisect_right

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


class SourceHighlights(QSyntaxHighlighter):
    def __init__(self, document):
        self.ranges, self.ends = [], []
        self.dark = False
        self.mark = QTextCharFormat()
        self.mark.setBackground(QColor('#dbeafe'))
        super().__init__(document)

    def set_dark(self, dark):
        if dark == self.dark:
            return
        self.dark = dark
        self.mark.setBackground(QColor('#264b70' if dark else '#dbeafe'))
        self.rehighlight()

    @staticmethod
    def reading_ink(color):
        if color.lightnessF() >= .7:
            return color
        if color.hslSaturationF() < .15:
            return QColor('#e6edf7')
        return QColor.fromHslF(color.hslHueF(), color.hslSaturationF(), .78, color.alphaF())

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
        boundaries = [0, end - start]
        if self.dark:
            fragment = block.begin()
            while not fragment.atEnd():
                part = fragment.fragment()
                left, right = part.position() - start, part.position() - start + part.length()
                boundaries.extend((left, right))
                if not part.charFormat().isImageFormat():
                    ink = QTextCharFormat()
                    ink.setForeground(self.reading_ink(part.charFormat().foreground().color()))
                    self.setFormat(left, part.length(), ink)
                fragment += 1
        for left, right in self.ranges[bisect_right(self.ends, start):]:
            if left >= end:
                break
            begin, finish = max(start, left) - start, min(end, right) - start
            if not self.dark:
                self.setFormat(begin, finish - begin, self.mark)
                continue
            stops = sorted({begin, finish, *(point for point in boundaries if begin < point < finish)})
            for first, last in zip(stops, stops[1:]):
                mark = self.format(first)
                mark.setBackground(self.mark.background())
                self.setFormat(first, last - first, mark)
