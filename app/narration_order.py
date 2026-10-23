"""Visual narration order without changing native shape IDs or export locators."""

import re

POINT = 12700
CONTENTS = re.compile(r'^\s*(?:nội dung(?: chính)?|mục lục|contents?|outline)\s*[:：]?\s*$', re.I)
PREFIX = re.compile(r'^\s*(?:(?:bài|chương|lesson|chapter|unit)\s+)?\d+\s*[:：.\-]?\s*$', re.I)


def same_line(first, second):
    # Text frames with different font sizes rarely have identical top edges.
    tolerance = max(4 * POINT, min(24 * POINT, min(first.get('h', 0), second.get('h', 0)) * .3))
    return abs(first['y'] - second['y']) <= tolerance


def visual_order(items):
    """Read close rows left-to-right; a left contents label introduces its list."""
    items = list(items)
    empty = [item for item in items if not item.get('text', item.get('english_text', '')).strip()]
    items = [item for item in items if item.get('text', item.get('english_text', '')).strip()]
    rows, row = [], []
    for item in sorted(items, key=lambda item: item['y']):
        if row and not same_line(row[0], item):
            rows.append(sorted(row, key=lambda item: item['x']))
            row = []
        row.append(item)
    if row:
        rows.append(sorted(row, key=lambda item: item['x']))
    ordered = [item for row in rows for item in row]
    for label in list(ordered):
        if not CONTENTS.fullmatch(label.get('text', label.get('english_text', ''))):
            continue
        right = [item for item in ordered if item is not label and item['x'] >= label['x'] + label.get('w', 0)
                 and item.get('text', item.get('english_text', '')).strip()]
        anchors = [item for item in right if min(item['y'] + item.get('h', 0), label['y'] + label.get('h', 0))
                   > max(item['y'], label['y'])]
        # The list may consist of separate numbered boxes, or one tall textbox.
        # Match its column(s); an unrelated title at another x remains first.
        members = [item for item in right if item.get('kind') != 'title' and any(
            abs(item['x'] - anchor['x']) <= 24 * POINT for anchor in anchors)]
        if members:
            first = min(ordered.index(item) for item in members)
            if first < ordered.index(label):
                ordered.remove(label)
                ordered.insert(first, label)
    # Background artwork and empty formula-review markers must not establish
    # a row boundary between a lesson number and its adjacent title.
    return ordered + sorted(empty, key=lambda item: (item['y'], item['x']))
