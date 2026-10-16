"""Visible prose, editable inline math and decorative picture detection."""

import copy
import io
import re
import unicodedata
from functools import lru_cache

from lxml import etree

from .source_deck import NS


def local(node):
    return etree.QName(node).localname


@lru_cache(maxsize=32)
def _query(expression):
    return etree.XPath(expression, namespaces=NS)


def xpath(node, expression):
    return _query(expression)(node)


def math_text(node):
    """Readable cache/translation representation; native XML remains in the slide."""
    tag = local(node)
    children = {local(child): child for child in node}

    def part(name):
        child = children.get(name)
        return math_text(child) if child is not None else ''

    if tag == 't':
        return unicodedata.normalize('NFKC', node.text or '')
    if tag.endswith('Pr') or tag in {'ctrlPr', 'rPr'}:
        return ''
    if tag == 'f':
        return '(' + part('num') + ')/(' + part('den') + ')'
    if tag in {'sSup', 'sSub', 'sSubSup'}:
        result = part('e')
        if tag != 'sSup':
            result += '_(' + part('sub') + ')'
        if tag != 'sSub':
            sup = part('sup')
            result += {'2': '²', '3': '³'}.get(sup, '^(' + sup + ')')
        return result
    if tag == 'rad':
        return ('√' if not part('deg') else 'root[' + part('deg') + ']') + '(' + part('e') + ')'
    if tag == 'd':
        props = children.get('dPr')
        delimiters = {} if props is None else {local(c): c.get('{http://schemas.openxmlformats.org/officeDocument/2006/math}val') for c in props}
        return (delimiters.get('begChr', '(') or '') + part('e') + (delimiters.get('endChr', ')') or '')
    if tag in {'eqArr', 'm'}:
        return '; '.join(math_text(c) for c in node if not local(c).endswith('Pr'))
    if tag == 'br':
        return '\n'
    return ''.join(math_text(child) for child in node)


def visible_run(node):
    return not xpath(node, './a:rPr/a:solidFill/*/a:alpha[@val="0"]|./a:rPr/a:noFill')


def ordinary_text(paragraph):
    return ''.join(('\n' if local(c) == 'br' else ''.join(xpath(c, './/a:t/text()')))
                   for c in paragraph if local(c) in {'r', 'br', 'fld'} and visible_run(c))


def equation_only(paragraph):
    if not paragraph.xpath('.//*[local-name()="oMath"]'):
        return False
    plain = ordinary_text(paragraph)
    plain = re.sub(r'\b(?:cm|mm|km|m|s|rad|Hz|kg|N)\b', '', plain)
    return not re.search(r'[^\W\d_]', plain, re.UNICODE)


def paragraph_text(paragraph):
    pieces = []
    for child in paragraph:
        if local(child) in {'pPr', 'endParaRPr'} or not visible_run(child):
            continue
        if child.xpath('.//*[local-name()="oMath"]') or local(child) == 'oMath':
            pieces.append('$' + math_text(child) + '$')
        elif local(child) == 'br':
            pieces.append('\n')
        else:
            pieces.extend(xpath(child, './/a:t/text()'))
    return ''.join(pieces).strip()


def inline_math(deck):
    from .native_bilingual import leaves

    result = {}
    for slide in deck.slides:
        for shape in leaves(slide.shapes, modern=True):
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for child in paragraph._p:
                        if child.xpath('.//*[local-name()="oMath"]') or local(child) == 'oMath':
                            result.setdefault(math_text(child), copy.deepcopy(child))
    return result


def insert_inline_math(shape, equations, english):
    """Restore the original editable equation at the translated inline position."""
    for paragraph in shape.text_frame.paragraphs:
        for run in list(paragraph.runs):
            if '$' not in run.text:
                continue
            pieces = re.split(r'(\$[^$]+\$)', run.text)
            if not any(p.startswith('$') and p[1:-1] in equations for p in pieces):
                continue
            parent = run._r.getparent()
            index = parent.index(run._r)
            for piece in pieces:
                if not piece:
                    continue
                if piece.startswith('$') and piece[1:-1] in equations:
                    node = copy.deepcopy(equations[piece[1:-1]])
                    for props in xpath(node, './/a:rPr|.//a:defRPr'):
                        # Fractions need more vertical room than ordinary text.
                        # Keep editable math readable, with space above/below it.
                        size = max(18, (run.font.size.pt if run.font.size else 22) * .9)
                        props.set('sz', str(round(size*100)))
                        props.set('lang', 'en-US' if english else 'vi-VN')
                        for paint in list(props):
                            if local(paint) in {'solidFill', 'noFill'}:
                                props.remove(paint)
                        fill = etree.Element('{'+NS['a']+'}solidFill')
                        etree.SubElement(fill, '{'+NS['a']+'}srgbClr', val='173354')
                        props.insert(0, fill)
                else:
                    node = copy.deepcopy(run._r)
                    node.find('a:t', NS).text = piece
                parent.insert(index, node)
                index += 1
            parent.remove(run._r)


def source_objects(slide):
    """Unique native leaves in visual reading order, including group transforms."""
    from .slide_speech import objects

    located = {obj['shape']._element: obj for obj in objects(slide)}
    return sorted(located.values(), key=lambda obj: (obj['y'], obj['x']))


def source_blocks(deck):
    result = []
    for number, slide in enumerate(deck.slides, 1):
        seen = set()
        for index, obj in enumerate(source_objects(slide), 1):
            shape = obj['shape']
            if obj['hidden']:
                continue
            locator = f'Slide {number} · ý {index}'
            if shape.has_table:
                for row, cells in enumerate(shape.table.rows):
                    for col, cell in enumerate(cells.cells):
                        if not cell.is_spanned and cell.text.strip():
                            result.append((locator + f' · ô {row},{col}', cell.text.strip()))
            elif shape.has_text_frame:
                for part, paragraph in enumerate(shape.text_frame.paragraphs, 1):
                    if equation_only(paragraph._p):
                        continue  # The shared native equation is carried once.
                    text = paragraph_text(paragraph._p)
                    # Animation/reveal sources sometimes duplicate the same
                    # text in the same position. Retain separate repetitions
                    # elsewhere on the slide; remove only exact overlays.
                    identity = (text, *(round(obj[k]/12700) for k in ('x', 'y', 'w', 'h')), part)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    result.extend((locator + f' · đoạn {part} · dòng {line}', value.strip())
                                  for line, value in enumerate(text.splitlines(), 1) if value.strip())
    return result


def empty_picture(shape, inset=.1):
    """A blank label panel is decoration; never remove a picture with interior ink.

    Inspect the original bitmap, including alpha. Borders outside the central
    80% do not count as diagram content. Native charts are never passed here.
    """
    from PIL import Image, ImageStat

    try:
        with Image.open(io.BytesIO(shape.image.blob)) as original:
            image = original.convert('RGBA')
            width, height = image.size
            inner = image.crop((width*inset, height*inset, width*(1-inset), height*(1-inset)))
            if inner.getchannel('A').getextrema()[1] < 8:
                return True
            background = Image.new('RGB', inner.size, 'white')
            background.paste(inner, mask=inner.getchannel('A'))
            whole = Image.new('RGB', image.size, 'white')
            whole.paste(image, mask=image.getchannel('A'))
            return (max(ImageStat.Stat(background).stddev) < 2.5
                    and (max(ImageStat.Stat(whole).stddev) >= 2.5
                         or image.getchannel('A').getextrema()[0] < 8))
    except (OSError, ValueError):
        return False


def decorative_picture(obj, deck_size):
    width, height = deck_size
    if empty_picture(obj['shape']):
        return True
    # A full-slide bitmap behind editable source content is the old theme.
    # Its original is retained in the source file, rather than nested as a
    # miniature second slide inside the new theme.
    return (obj['w'] >= width*.92 and obj['h'] >= height*.9
            and abs(obj['x']) < width*.04 and abs(obj['y']) < height*.04
            and empty_picture(obj['shape'], inset=.3))
