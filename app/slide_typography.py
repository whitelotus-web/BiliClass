"""Keep scientific quantities together without rewriting words, runs or equations."""

import re

from lxml import etree

from .source_deck import NS

NUMBER = r'[+−-]?(?:\d+(?:[.,]\d+)*|[.,]\d+)(?:[eE][+−-]?\d+)?'
UNIT = r'(?:mmHg|kg|mg|µg|μg|km|cm|mm|µm|μm|nm|ms|µs|μs|ns|min|kHz|MHz|GHz|Hz|mN|kN|MPa|kPa|Pa|kJ|MJ|MW|kW|mV|kV|mA|kΩ|Ω|mol|mmol|mL|ml|°C|°F|rad|[mgshNJWVALK%°])'
POWER = r'(?:[²³]|\^[+−-]?\d+)?'
QUANTITY = re.compile(r'(?<![\w.])' + NUMBER + r'(?P<gap>[ \t\v\u00a0\u202f]*)' + UNIT + POWER
                      + r'(?:[ \t]*(?:/|·)[ \t]*' + UNIT + POWER + r')?(?![\w])')


def protect_paragraph(paragraph):
    """Join number/unit spaces across ordinary runs; leave OMML/fields intact."""
    changed = False
    groups, current = [], []
    for child in paragraph:
        tag = etree.QName(child).localname
        if tag == 'r':
            for text in child.findall('a:t', NS):
                current.extend((text, index, char) for index, char in enumerate(text.text or ''))
        elif tag == 'br':
            current.append((child, 0, '\v'))
        elif tag not in {'pPr', 'endParaRPr'}:
            groups.append(current)
            current = []  # Never join through an equation, field or foreign object.
    groups.append(current)
    protected = False
    edits = {}
    for group in groups:
        text = ''.join(item[2] for item in group)
        for match in QUANTITY.finditer(text):
            protected = True
            start, end = match.span('gap')
            for offset in range(start, end):
                node, index, _ = group[offset]
                edits.setdefault(node, {})[index] = '\u00a0' if offset == start else ''
    for node, replacements in edits.items():
        if etree.QName(node).localname == 'br':
            run = etree.Element('{' + NS['a'] + '}r')
            for child in list(node):
                run.append(child)
            etree.SubElement(run, '{' + NS['a'] + '}t').text = replacements[0]
            node.getparent().replace(node, run)
            changed = True
        else:
            before = node.text or ''
            node.text = ''.join(replacements.get(index, char) for index, char in enumerate(before))
            changed |= node.text != before
    if protected:
        props = paragraph.find('a:pPr', NS)
        if props is None:
            props = etree.Element('{' + NS['a'] + '}pPr')
            paragraph.insert(0, props)
        changed |= props.get('latinLnBrk') != '0'
        props.set('latinLnBrk', '0')
    return changed


def protect_tree(tree):
    return sum(protect_paragraph(paragraph) for paragraph in tree.findall('.//a:p', NS))
