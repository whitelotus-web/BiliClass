"""Find text panels by their painted area, excluding transparent image shadows."""
from functools import lru_cache
from io import BytesIO

from PIL import Image, ImageStat

from .source_deck import NS


@lru_cache(maxsize=128)
def _painted_image(blob):
    try:
        with Image.open(BytesIO(blob)) as source:
            if source.width * source.height > 16_000_000:
                return None
            image = source.convert('RGBA')
            image.thumbnail((256, 256))
        mask = image.getchannel('A').point(lambda value: 255 if value >= 230 else 0)
        box = mask.getbbox()
        if box is None or ImageStat.Stat(mask.crop(box)).mean[0] < 225:
            return None  # An irregular illustration is not a text container.
        return tuple(value / size for value, size in zip(box, (image.width, image.height)*2, strict=True))
    except (OSError, ValueError, Image.DecompressionBombError):
        return None


def panels(slide, width, height):
    from .slide_speech import objects

    result = []
    for order, item in enumerate(objects(slide, include_empty=True)):
        shape = item['shape']
        if item['hidden'] or item['text'].strip() or shape.rotation:
            continue
        root = shape._element
        if root.tag != '{' + NS['p'] + '}sp':
            continue
        if any(any(node.get(key, '0') not in {'0', 'false'} for key in ('rot', 'flipH', 'flipV'))
               for parent in root.iterancestors() if parent.tag == '{' + NS['p'] + '}grpSp'
               for node in parent.findall('p:grpSpPr/a:xfrm', NS)):
            continue
        x, y, w, h = (item[key] for key in ('x', 'y', 'w', 'h'))
        if (w < width*.15 or h < height*.035 or w*h > width*height*.6
                or x < 0 or y < 0 or x+w > width*1.01 or y+h > height*1.01):
            continue
        properties = root.find('p:spPr', NS)
        painted_properties = properties
        if properties is not None and properties.find('a:grpFill', NS) is not None:
            # Many publisher decks put a panel's color on its parent group.
            # Follow only explicit group inheritance; no theme/color guessing.
            for parent in root.iterancestors():
                if parent.tag != '{' + NS['p'] + '}grpSp':
                    continue
                painted_properties = parent.find('p:grpSpPr', NS)
                if painted_properties is None or painted_properties.find('a:grpFill', NS) is None:
                    break
        fill = painted_properties.find('a:blipFill', NS) if painted_properties is not None else None
        if fill is not None:
            blip = fill.find('a:blip', NS)
            crop = fill.find('a:srcRect', NS)
            if (blip is None or fill.find('a:stretch', NS) is None
                    or crop is not None and any(int(value) for value in crop.attrib.values())):
                continue
            identity = blip.get('{' + NS['r'] + '}embed')
            try:
                painted = _painted_image(shape.part.related_part(identity).blob)
            except (KeyError, AttributeError):
                continue
            if painted is None:
                continue
            left, top, right, bottom = painted
            x, y, w, h = x+left*w, y+top*h, (right-left)*w, (bottom-top)*h
        else:
            geometry = root.find('p:spPr/a:prstGeom', NS)
            if (geometry is None or geometry.get('prst') not in {'rect', 'roundRect', 'round1Rect', 'round2SameRect'}
                    or painted_properties is None
                    or not any(painted_properties.find('a:' + kind, NS) is not None for kind in ('solidFill', 'gradFill'))):
                continue
        result.append({'shape_id': item['shape_id'], 'order': order,
                       'x': round(x), 'y': round(y), 'w': round(w), 'h': round(h)})
    return result


def owner(box, candidates):
    """Require the source text to belong to a single painted rectangular panel."""
    x, y, w, h = (box[key] for key in ('x', 'y', 'w', 'h'))
    matches = [p for p in candidates if p['shape_id'] != box['shape_id']
               and p['x'] <= x + w*.5 <= p['x']+p['w']
               and p['y'] <= y + h*.4 <= p['y']+p['h']
               and min(x+w, p['x']+p['w'])-max(x, p['x']) >= w*.85
               and p['w'] > w*1.04]
    return min(matches, key=lambda row: row['w']*row['h']) if matches else None


def artwork(slide, width, height, backgrounds):
    from .slide_speech import objects

    background_ids = {row['shape_id'] for row in backgrounds}
    return [row for row in objects(slide, include_empty=True) if not row['text'].strip()
            and not row['hidden'] and row['shape_id'] not in background_ids
            and 0 < row['w']*row['h'] < width*height*.6
            and row['x']+row['w'] > 0 and row['y']+row['h'] > 0]


def fit_box(box, panel):
    """Use the panel's real interior; align every VI/EN row to its same left edge."""
    inset = max(4*12700, min(panel['w'], panel['h'])*.045)
    left = max(box['x'], panel['x']+inset)
    # A large panel can contain a heading and several body rows. Empty area
    # above this row belongs to that content, not to the new translation.
    top = max(box['y'], panel['y']+inset)
    right = panel['x']+panel['w']-inset
    bottom = panel['y']+panel['h']-inset
    return {'x': round(left), 'y': round(top), 'w': round(max(127000, right-left)),
            'h': round(max(127000, bottom-top))}


def escapes(slide, width, height):
    from .slide_speech import objects

    backgrounds = panels(slide, width, height)
    result = {}
    protected = set(slide._element.xpath('.//p:animMotion//p:spTgt/@spid|.//p:cond/p:tgtEl/p:spTgt/@spid'))
    for item in objects(slide):
        if str(item['shape_id']) in protected:
            continue
        panel = owner(item, backgrounds) if item['name'].startswith('BCL_BODY ') else None
        if panel and (item['y'] < panel['y']-12700 or item['y']+item['h'] > panel['y']+panel['h']+12700
                      or item['x'] < panel['x']-12700 or item['x']+item['w'] > panel['x']+panel['w']+12700):
            result[item['shape_id']] = {'code': 'panel_text_escape', 'severity': 'FAIL',
                                        'shape_id': item['shape_id'], 'panel_id': panel['shape_id']}
    return list(result.values())


def constrain_generated(tree, slide, width, height):
    """Repair paired text geometry together, retaining every paragraph and trigger."""
    from .slide_speech import objects

    backgrounds = panels(slide, width, height)
    decorations = artwork(slide, width, height, backgrounds)
    items = {item['shape_id']: item for item in objects(slide)}
    changes = []
    for shape in tree.findall('.//p:sp', NS):
        identity = shape.find('p:nvSpPr/p:cNvPr', NS)
        transform = shape.find('p:spPr/a:xfrm', NS)
        if (identity is None or not identity.get('name', '').startswith('BCL_BODY ')
                or transform is None or transform.get('rot', '0') != '0'):
            continue
        key = int(identity.get('id'))
        item = items.get(key)
        panel = owner(item, backgrounds) if item else None
        if not panel:
            continue
        # Never alter a moving object or a shape whose position is a click target.
        if tree.xpath('.//p:animMotion//p:spTgt[@spid=$id]|.//p:cond/p:tgtEl/p:spTgt[@spid=$id]',
                      namespaces=NS, id=str(key)):
            continue
        off, ext = transform.find('a:off', NS), transform.find('a:ext', NS)
        if off is None or ext is None:
            continue
        inset = max(4*12700, min(panel['w'], panel['h'])*.045)
        # Keep already separated columns and their gap; only pull the pair into
        # its common vertical band and trim columns that cross the right edge.
        top, bottom = max(item['y'], panel['y']+inset), panel['y']+panel['h']-inset
        canvas_scale = max(.5, min(4, height / (540 * 12700)))
        for neighbor in items.values():
            overlap = min(item['x']+item['w'], neighbor['x']+neighbor['w']) - max(item['x'], neighbor['x'])
            if (neighbor['shape_id'] != key and neighbor['text'].strip() and not neighbor['hidden']
                    and overlap > min(item['w'], neighbor['w']) * .3
                    and neighbor['y'] > top + max(20*12700*canvas_scale, min(item['h']*.3, 60*12700*canvas_scale))):
                bottom = min(bottom, neighbor['y'] - 12700)
        right = min(item['x']+item['w'], panel['x']+panel['w']-inset)
        for decoration in decorations:
            if (item['x'] < decoration['x'] < right and min(bottom, decoration['y']+decoration['h'])
                    - max(top, decoration['y']) > min(bottom-top, decoration['h'])*.2):
                right = min(right, decoration['x']-6*12700)
        sx, sy = int(ext.get('cx'))/max(1, item['w']), int(ext.get('cy'))/max(1, item['h'])
        target = (int(off.get('x')), round(int(off.get('y'))+(top-item['y'])*sy),
                  round((right-item['x'])*sx), round((bottom-top)*sy))
        before = (int(off.get('x')), int(off.get('y')), int(ext.get('cx')), int(ext.get('cy')))
        if min(target[2:]) <= 0 or all(abs(a-b) <= 1270 for a, b in zip(before, target, strict=True)):
            continue
        off.set('x', str(target[0]))
        off.set('y', str(target[1]))
        ext.set('cx', str(target[2]))
        ext.set('cy', str(target[3]))
        changes.append({'shape_id': key, 'operation': 'fit_painted_panel', 'panel_id': panel['shape_id']})
    return changes
