"""Expand circled numeric slide labels for speech without changing slide text."""

import re
import unicodedata

_DIGITS = ('không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín')


def _number(value):
    if value < 10:
        return _DIGITS[value]
    tens, units = divmod(value, 10)
    prefix = 'mười' if tens == 1 else _DIGITS[tens] + ' mươi'
    if not units:
        return prefix
    suffix = 'lăm' if units == 5 else 'mốt' if units == 1 and tens > 1 else _DIGITS[units]
    return prefix + ' ' + suffix


def vietnamese(text):
    replacements = {}
    for char in set(text):
        if 'CIRCLED' not in unicodedata.name(char, '') or unicodedata.category(char) != 'No':
            continue
        value = unicodedata.numeric(char, -1)
        if 0 <= value <= 50 and value == int(value):
            replacements[char] = _number(int(value))
    if not replacements:
        return text
    # A standalone marker needs a short spoken phrase; the engine can return
    # no samples for a glyph by itself. Reuse existing raw-text cache keys so
    # continuing an incomplete lesson retains every already-created WAV.
    if text.strip() in replacements:
        return 'Số ' + replacements[text.strip()] + '.'
    expanded = ''.join(' ' + replacements[char] + ' ' if char in replacements else char for char in text)
    return re.sub(r' +([.,:;!?])', r'\1', re.sub(r'[ \t]+', ' ', expanded)).strip()
