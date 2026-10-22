"""Recover a draft paragraph from two local readers; never certify raster math."""

import re
import unicodedata
from difflib import SequenceMatcher


def scientific_lines(lines):
    """Keep a verified split covalent-bond term together, within the same column."""
    result, used = [], set()
    for index, line in enumerate(lines):
        if index in used:
            continue
        text = line['text'].strip()
        if line.get('verified') and re.search(r'liên kết cộng$', text, re.I):
            points = line['points']
            left, bottom = min(p[0] for p in points), max(p[1] for p in points)
            height = bottom-min(p[1] for p in points)
            matches = []
            for other, following in enumerate(lines):
                if other <= index or other in used or not following.get('verified'):
                    continue
                if following['text'].strip().casefold() not in {'hoá trị', 'hóa trị'}:
                    continue
                corners = following['points']
                gap = min(p[1] for p in corners)-bottom
                aligned = (abs(min(p[0] for p in corners)-left) < .035
                           or abs((min(p[0] for p in corners)+max(p[0] for p in corners))
                                  -(left+max(p[0] for p in points))) < .07)
                if aligned and -.2*height <= gap <= 1.2*height:
                    matches.append((other, following))
            if len(matches) == 1:
                other, following = matches[0]
                corners = points+following['points']
                right, top = max(p[0] for p in corners), min(p[1] for p in corners)
                bottom = max(p[1] for p in corners)
                line = {**line, 'text': text+' '+following['text'].strip(),
                        'scientific_join': True,
                        'confidence': min(line['confidence'], following['confidence']),
                        'points': [[left, top], [right, top], [right, bottom], [left, bottom]]}
                used.add(other)
        result.append(line)
    return result


def draft_line(line):
    first, second = line['text'].strip(), line.get('alternate', '').strip()
    if re.search(r'[=∑√∫≤≥ωαβφ²³]', first + second):
        return None
    if line.get('verified'):
        return first
    if line.get('confidence', 0) < .92 or line.get('probability', 0) < .86:
        return None
    if re.findall(r'\d+', first) != re.findall(r'\d+', second):
        return None

    def letters(value):
        value = unicodedata.normalize('NFD', value.casefold().replace('đ', 'd').replace('δ', 'd'))
        return re.sub(r'[^a-z0-9]', '', ''.join(c for c in value if not unicodedata.combining(c)))

    if not second or SequenceMatcher(None, letters(first), letters(second)).ratio() < .925:
        return None
    # The Vietnamese reader can misread the degree glyph as a question mark.
    # Restore only a glyph independently present next to the same source number.
    for number in re.findall(r'(\d+)°', first):
        second = re.sub(r'(?<!\d)' + re.escape(number) + r'\?(?!\d)', number + '°', second)
    if re.findall(r'\d+°', first) != re.findall(r'\d+°', second):
        return None
    return second


def paragraphs(lines, occurrence, image):
    """Group only long aligned prose lines, keeping uncertain diagrams separate."""
    candidates = []
    for index, line in enumerate(lines):
        points = line['points']
        left, top = min(p[0] for p in points), min(p[1] for p in points)
        right, bottom = max(p[0] for p in points), max(p[1] for p in points)
        text = draft_line(line)
        if text and len(text) >= 20 and right-left >= .25 and abs(points[1][1]-points[0][1]) < .025:
            candidates.append(dict(index=index, text=text, left=left, top=top, right=right, bottom=bottom))
    groups = []
    for row in sorted(candidates, key=lambda r: (r['top'], r['left'])):
        if groups and abs(row['left']-groups[-1][0]['left']) < .035 and -.04 <= row['top']-groups[-1][-1]['bottom'] < .07:
            groups[-1].append(row)
        else:
            groups.append([row])
    blocks = []
    for group in groups:
        text = ' '.join(r['text'] for r in group)
        if len(group) < 4 or len(text) < 200:
            continue
        left, top = min(r['left'] for r in group), min(r['top'] for r in group)
        right, bottom = max(r['right'] for r in group), max(r['bottom'] for r in group)
        x, y, w, h = occurrence['box']
        blocks.append({**occurrence, 'id': f"ocr-prose-{occurrence['slide']}-{occurrence['shape_id']}-{group[0]['index']}",
            'text': text, 'confidence': min(lines[r['index']]['confidence'] for r in group),
            'region': [x+left*w, y+top*h, (right-left)*w, (bottom-top)*h],
            'image': image, 'draft': True, 'line_indices': [r['index'] for r in group]})
    return blocks
