"""Grow generated captions into free space before reducing their type size."""

from itertools import product

from lxml import etree

from .source_deck import NS


def grow(shape, slide, width, height, *, translated=False):
    from .framed_text import owner, panels
    from .native_layout import text_height
    from .slide_speech import objects

    identity = shape.find('p:nvSpPr/p:cNvPr', NS)
    transform = shape.find('p:spPr/a:xfrm', NS)
    body = shape.find('p:txBody', NS)
    if (identity is None or not (translated or identity.get('name', '').startswith('BCL_')) or body is None
            or transform is None or transform.get('rot', '0') != '0'):
        return False
    if etree.XPath('.//p:animMotion//p:spTgt[@spid=$id]|.//p:cond/p:tgtEl/p:spTgt[@spid=$id]',
                   namespaces=NS)(slide._element, id=identity.get('id')):
        return False
    for parent in shape.iterancestors():
        if parent.tag == '{' + NS['p'] + '}grpSp':
            group = parent.find('p:grpSpPr/a:xfrm', NS)
            if group is not None and any(group.get(key, '0') != '0' for key in ('rot', 'flipH', 'flipV')):
                return False
    offset, extent = transform.find('a:off', NS), transform.find('a:ext', NS)
    props = body.find('a:bodyPr', NS)
    if offset is None or extent is None or props is None or props.get('vert', 'horz') != 'horz':
        return False
    local_x, local_y, local_w, local_h = [int(node.get(key)) / 12700 for node, key in
                   [(offset, 'x'), (offset, 'y'), (extent, 'cx'), (extent, 'cy')]]
    page_width, page_height = width, height
    width, height = width / 12700, height / 12700
    items = objects(slide)
    target_index = next((i for i, row in enumerate(items) if row['shape_id'] == int(identity.get('id'))), None)
    if target_index is None:
        return False
    target = items[target_index]
    if owner(target, panels(slide, page_width, page_height)):
        return False  # Empty space outside a decorative band is not usable room.
    x, y, w, h = [target[key] / 12700 for key in ('x', 'y', 'w', 'h')]
    if min(x, y) < 0 or min(w, h) <= 0 or x+w > width or y+h > height:
        return False
    obstacles = {}
    for index, item in enumerate(items):
        if item['shape_id'] == int(identity.get('id')) or item['hidden']:
            continue
        bx, by, bw, bh = [item[key] / 12700 for key in ('x', 'y', 'w', 'h')]
        if min(bw, bh) <= 0 or bx+bw <= 0 or by+bh <= 0 or bx >= width or by >= height:
            continue
        intersects = bx < x+w and bx+bw > x and by < y+h and by+bh > y
        if (index < target_index and not item['text'].strip()
                and (intersects or bw*bh > width*height*.6)):
            continue  # Existing background, not a new occlusion.
        obstacles[item['shape_id']] = (bx, by, bw, bh)
    sizes = []
    for paragraph in body.findall('a:p', NS):
        text = ''.join(node.text or '' for node in paragraph.findall('.//a:t', NS)).strip()
        if text:
            values = [node.get('sz') for node in [*paragraph.findall('.//a:rPr', NS),
                                                 *paragraph.findall('a:pPr/a:defRPr', NS)] if node.get('sz')]
            sizes.append((text, max(map(int, values), default=1800) / 100))
    if not sizes:
        return False
    # Grow right/down first, retaining the original anchor and VI/EN alignment.
    # A small label can also gain room to its left; a long body never crosses
    # back over the neighboring Vietnamese column.
    lefts = {x}
    if sum(len(text) for text, _ in sizes) < 50:
        lefts.add(max(10, x - min(w*.5, 40)))
    rights = {x+w, min(width-10, x+w+max(w, 60))}
    tops = {y, max(10, y-min(h, 48))}
    bottoms = {y+h, min(height-8, y+h+max(h, 72))}
    for bx, by, bw, bh in obstacles.values():
        if bx > x+w:
            rights.add(min(width-10, bx-6))
        if by > y+h:
            bottoms.add(min(height-8, by-6))
    candidates = []
    for left, right, top, bottom in product(lefts, rights, tops, bottoms):
        if left > x or right < x+w or bottom < y+h:
            continue
        candidate = left, top, right-left, bottom-top
        if any(left < bx+bw-.1 and right > bx+.1 and top < by+bh-.1 and bottom > by+.1
               for bx, by, bw, bh in obstacles.values()):
            continue
        needed = sum(text_height(text, max(1, candidate[2]-6), size) for text, size in sizes) + 4
        fits = needed <= candidate[3]
        score = (not fits, max(0, needed-candidate[3]), candidate[2]*candidate[3], y-top, x-left)
        candidates.append((score, candidate))
    if not candidates:
        return False
    _, chosen = min(candidates)
    left, top, cw, ch = chosen
    if cw <= w+1 and ch <= h+1:
        return False
    offset.set('x', str(round((local_x+(left-x)*local_w/w)*12700)))
    offset.set('y', str(round((local_y+(top-y)*local_h/h)*12700)))
    extent.set('cx', str(round(cw*local_w/w*12700)))
    extent.set('cy', str(round(ch*local_h/h*12700)))
    return True
