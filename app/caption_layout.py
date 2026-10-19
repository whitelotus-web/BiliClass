"""Reserve a shared readable caption band below a row of native pictures."""

from .source_deck import NS


def reserve_band(tree, width, height, slide):
    from .native_layout import text_height
    from .slide_speech import objects

    width, height = width / 12700, height / 12700
    items = {row['shape_id']: row for row in objects(slide)}
    captions, pictures = [], []
    for shape in tree.iter():
        if shape.tag not in {'{' + NS['p'] + '}sp', '{' + NS['p'] + '}pic'}:
            continue
        identity = shape.find('p:nvSpPr/p:cNvPr', NS)
        transform = shape.find('p:spPr/a:xfrm', NS)
        picture = identity is None
        if picture:
            identity = shape.find('p:nvPicPr/p:cNvPr', NS)
        if identity is None or transform is None or transform.get('rot', '0') != '0':
            continue
        off, ext = transform.find('a:off', NS), transform.find('a:ext', NS)
        if off is None or ext is None:
            continue
        item = items.get(int(identity.get('id')))
        if not item or item['hidden']:
            continue
        if any(any(group.get(key, '0') not in ('0', 'false') for key in ('rot', 'flipH', 'flipV'))
               for parent in shape.iterancestors() if parent.tag == '{' + NS['p'] + '}grpSp'
               for group in parent.findall('p:grpSpPr/a:xfrm', NS)):
            continue
        x, y, w, h = [item[key] / 12700 for key in ('x', 'y', 'w', 'h')]
        if min(w, h) <= 0:
            continue
        if picture:
            pictures.append((shape, int(identity.get('id')), off, ext, x, y, w, h))
        elif identity.get('name', '').startswith('BCL_') and y >= height*.75 and h <= height*.23:
            body = shape.find('p:txBody', NS)
            if body is None or body.xpath('.//*[local-name()="oMath"]'):
                continue
            needed = 4
            length = 0
            for paragraph in body.findall('a:p', NS):
                text = ''.join(node.text or '' for node in paragraph.findall('.//a:t', NS)).strip()
                length += len(text)
                sizes = [int(node.get('sz')) / 100 for node in paragraph.findall('.//a:rPr', NS) if node.get('sz')]
                needed += text_height(text, max(1, w-6), max(sizes, default=18))
            if length > 25:
                captions.append((shape, int(identity.get('id')), off, ext, x, y, w, h, needed))
    if len(captions) < 2 or max(row[5] for row in captions)-min(row[5] for row in captions) > 18:
        return []
    needed = max(row[8] for row in captions) + 6
    if needed > height*.32 or needed <= min(row[7] for row in captions) + 3:
        return []
    top = height-10-needed
    mains = [row for row in pictures if row[7] >= height*.25 and row[6] >= width*.25
             and row[5] >= height*.3 and row[5]+row[7] > top]
    if len(mains) < 2:
        return []
    # Motion coordinates and click triggers are never moved automatically.
    moved_ids = {str(row[1]) for row in pictures if any(
        main[4] <= row[4]+row[6]/2 <= main[4]+main[6]
        and main[5] <= row[5]+row[7]/2 <= main[5]+main[7] for main in mains)}
    if any(node.get('spid') in moved_ids for node in tree.findall('.//p:animMotion//p:spTgt', NS)) or any(
            node.get('spid') in moved_ids for node in tree.findall('.//p:cond/p:tgtEl/p:spTgt', NS)):
        return []
    factors = []
    assignments = {}
    for row in pictures:
        owners = [main for main in mains if main[4] <= row[4]+row[6]/2 <= main[4]+main[6]
                  and main[5] <= row[5]+row[7]/2 <= main[5]+main[7]]
        if owners:
            assignments[row[1]] = min(owners, key=lambda main: main[6]*main[7])
    for main in mains:
        bottom = max(row[5]+row[7] for row in pictures if assignments.get(row[1]) == main)
        factors.append((top-8-main[5]) / (bottom-main[5]))
    factor = min(factors)
    if not .45 <= factor < .99:
        return []
    # No unrelated text may be displaced by the new caption band.
    caption_ids = {row[1] for row in captions}
    for item in items.values():
        if (item['shape_id'] not in caption_ids and not item['hidden'] and item['text'].strip()
                and (item['y'] + item['h']) / 12700 > top):
            return []
    def place(row, nx, ny, nw, nh):
        _, _, off, ext, x, y, w, h, *_ = row
        sx, sy = int(ext.get('cx')) / w, int(ext.get('cy')) / h
        off.set('x', str(round(int(off.get('x')) + (nx-x)*sx)))
        off.set('y', str(round(int(off.get('y')) + (ny-y)*sy)))
        ext.set('cx', str(round(nw*sx)))
        ext.set('cy', str(round(nh*sy)))
    changes = []
    for row in pictures:
        owner = assignments.get(row[1])
        if owner is None:
            continue
        _, identity, off, ext, x, y, w, h = row
        center = owner[4]+owner[6]/2
        place(row, center+(x-center)*factor, owner[5]+(y-owner[5])*factor, w*factor, h*factor)
        changes.append({'shape_id': identity, 'operation': 'reserve_caption_band'})
    for row in captions:
        _, identity, off, ext, x, y, w, h, _ = row
        place(row, x, top, w, needed)
        changes.append({'shape_id': identity, 'operation': 'align_caption_band'})
    # A translated row can meet a full-width source definition above it. Use
    # the existing lower edge, so neither the artwork nor the title is covered.
    for shape in tree.iter('{' + NS['p'] + '}sp'):
        identity = shape.find('p:nvSpPr/p:cNvPr', NS)
        if identity is None or not identity.get('name', '').startswith('BCL_BODY'):
            continue
        transforms = [*shape.findall('p:spPr/a:xfrm', NS),
                      *(group for parent in shape.iterancestors() if parent.tag == '{' + NS['p'] + '}grpSp'
                        for group in parent.findall('p:grpSpPr/a:xfrm', NS))]
        if any(any(node.get(key, '0') not in ('0', 'false') for key in ('rot', 'flipH', 'flipV')) for node in transforms):
            continue
        item = items.get(int(identity.get('id')))
        off, ext = shape.find('p:spPr/a:xfrm/a:off', NS), shape.find('p:spPr/a:xfrm/a:ext', NS)
        if not item or off is None or ext is None or item['shape_id'] in caption_ids:
            continue
        x, y, w, h = [item[key]/12700 for key in ('x', 'y', 'w', 'h')]
        blockers = [other for other in items.values() if other['shape_id'] != item['shape_id']
                    and other['text'].strip() and not other['hidden'] and other['y']/12700 < y-10
                    and y+2 < (other['y']+other['h'])/12700 < y+h*.6
                    and min(x+w, (other['x']+other['w'])/12700)-max(x, other['x']/12700) > w*.5]
        if not blockers or shape.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'):
            continue
        ny = max((other['y']+other['h'])/12700 for other in blockers)+6
        if y+h-ny < 36:
            continue
        place((shape, item['shape_id'], off, ext, x, y, w, h), x, ny, w, y+h-ny)
        changes.append({'shape_id': item['shape_id'], 'operation': 'separate_text_rows'})
    return changes
