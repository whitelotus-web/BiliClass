"""Conservative local text fitting without moving pictures or source shapes.

These estimates select a native route, not a quality verdict. The resulting
PowerPoint still goes through the normal rendered overflow/coverage checks.
"""

import math
import textwrap

from lxml import etree

from .source_deck import NS, _size

MIN_FONT = 18.0


def text_height(text, width, size, expansion=1.0):
    columns = max(1, int(width / (size * .6 * expansion)))
    lines = sum(max(1, len(textwrap.wrap(line, columns))) for line in text.splitlines() or [''])
    return lines * size * 1.15


def can_fit(shape, mode, *, title_height=None, height=None):
    """A large original font alone is not a reason to upload the whole slide."""
    size = min(_size(shape.text_frame, shape), MIN_FONT)
    width = (shape.width-shape.text_frame.margin_left-shape.text_frame.margin_right)/12700
    height = ((title_height or height or shape.height)-shape.text_frame.margin_top-shape.text_frame.margin_bottom)/12700
    if width <= 0 or height <= 0:
        return False
    if title_height is not None:
        # Keep EN smaller than VI, but never force newly fitted text below 18pt.
        return (text_height(shape.text, width, size / .8)
                + text_height(shape.text, width, size, 1.35)) <= height
    if mode == 'parallel_columns':
        width *= .47
    estimate = text_height(shape.text, width, size, 1.35)
    if mode == 'sentence_pairs':
        estimate += text_height(shape.text, width, size)
    return estimate <= height


def fit_body(shape, fallback_size):
    """Fit actual translated text, retaining font family, emphasis and geometry.

Apply only to simple, unrotated native text shapes. Never shrink formulas or
superscript XML; those runs keep their original properties. Stop at a readable
floor even if the translation is unexpectedly long; validation reports that.
"""
    body = shape.find('p:txBody', NS)
    transform = shape.find('p:spPr/a:xfrm', NS)
    extent = shape.find('p:spPr/a:xfrm/a:ext', NS)
    if body is None or extent is None:
        return
    if transform is not None and int(transform.get('rot', '0')) % 21600000:
        return
    props = body.find('a:bodyPr', NS)
    if props is None or props.get('vert', 'horz') != 'horz':
        return
    width = (int(extent.get('cx'))-int(props.get('lIns', 91440))-int(props.get('rIns', 91440)))/12700
    height = (int(extent.get('cy'))-int(props.get('tIns', 45720))-int(props.get('bIns', 45720)))/12700
    paragraphs = body.findall('a:p', NS)
    if width <= 0 or height <= 0 or not paragraphs:
        return
    sizes = []
    for paragraph in paragraphs:
        values = [int(n) / 100 for n in paragraph.xpath('./a:r/a:rPr/@sz|./a:pPr/a:defRPr/@sz', namespaces=NS)]
        sizes.append(max(values, default=fallback_size / 100))

    def needed(scale):
        total = 0.0
        for paragraph, size in zip(paragraphs, sizes, strict=True):
            text = ''.join(('\n' if etree.QName(n).localname == 'br' else n.text or '')
                           for n in paragraph.iter() if etree.QName(n).localname in {'t', 'br'})
            fitted = max(min(MIN_FONT, size), size * scale)
            total += text_height(text, width, fitted)
            # Explicit paragraph spacing is scaled with the type. Fixed leading
            # is normalized only when this body actually needs fitting.
            for value in paragraph.xpath('./a:pPr/a:spcBef/a:spcPts/@val|./a:pPr/a:spcAft/a:spcPts/@val', namespaces=NS):
                total += int(value) / 100 * scale
        return total

    if needed(1) <= height:
        return
    scale = 1.0
    while scale > .1 and needed(scale) > height:
        scale -= .025
    for paragraph, size in zip(paragraphs, sizes, strict=True):
        ppr = paragraph.find('a:pPr', NS)
        if ppr is None:
            ppr = etree.Element(f'{{{NS["a"]}}}pPr')
            paragraph.insert(0, ppr)
        default = ppr.find('a:defRPr', NS)
        if default is None:
            default = etree.SubElement(ppr, f'{{{NS["a"]}}}defRPr')
        for node in [default, *paragraph.findall('a:r/a:rPr', NS), *paragraph.findall('a:endParaRPr', NS)]:
            if node.get('baseline', '0') != '0':
                continue
            old = int(node.get('sz', round(size*100)))
            node.set('sz', str(math.ceil(max(min(MIN_FONT*100, old), old*scale))))
        # Runs inheriting source theme size must inherit our new paragraph size.
        for child in ppr:
            tag = etree.QName(child).localname
            if tag == 'lnSpc':
                for node in list(child):
                    child.remove(node)
                etree.SubElement(child, f'{{{NS["a"]}}}spcPct', val='110000')
            elif tag in {'spcBef', 'spcAft'}:
                for node in child.findall('a:spcPts', NS):
                    node.set('val', str(round(int(node.get('val', '0'))*scale)))
