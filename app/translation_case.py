"""Match source heading case without lowercasing names or native math locks."""

import re

_LOCKS = re.compile(r'⟦BLC\d+⟧|BCLLOCK\d+END|\$[^$]+\$|https?://\S+')
_LABEL = re.compile(r'^\s*(?:(?:\d+(?:\.\d+)*|[A-Za-z]|[IVXLCDM]+)[.)]\s+|[•●▪➤+–—-]\s*)')
_WORDS = re.compile(r'[^\W\d_]+', re.UNICODE)


def align_case(source, translated, *, chemistry=False):
    """Uppercase headings, or just the first prose letter, like Vietnamese.

    Never call capitalize/title: those also lowercase Newton, DNA, pH, etc.
    Lowercase source fragments retain the translator's natural word casing.
    """
    def spans(text):
        result = [(m.start(), m.end()) for m in _LOCKS.finditer(text)]
        label = _LABEL.match(text)
        if label:
            result.append(label.span())
        if chemistry:
            from .chemical_notation import formula_spans

            result.extend(m.span() for m in formula_spans(text))
        return result

    def words(text):
        protected = spans(text)
        return [m for m in _WORDS.finditer(text) if not any(a < m.end() and m.start() < b for a, b in protected)]

    original, target = words(source), words(translated)
    if not original or not target:
        return translated
    first = original[0].group()
    if not first[0].isupper():
        return translated
    uppercase = all(m.group().isupper() for m in original)
    if not uppercase and any(a < target[0].start() and _LOCKS.fullmatch(translated[a:b])
                             and not translated[a:b].startswith(('http://', 'https://'))
                             for a, b in spans(translated)):
        return translated  # An equation starts the sentence; its following verb stays lowercase.
    changes = []
    for word in target if uppercase else target[:1]:
        value = word.group()
        # Mixed-case names, scientific symbols and units are deliberate.
        if value[0].islower() and any(c.isupper() for c in value[1:]):
            continue
        replacement = value.upper() if uppercase else value[0].upper() + value[1:]
        if replacement != value:
            changes.append((word.start(), word.end(), replacement))
    for start, end, value in reversed(changes):
        translated = translated[:start] + value + translated[end:]
    return translated


def align_pairs(tree, pairs):
    """Repair only verified VI/EN pairs, preserving runs, math and shape IDs.

    The caller owns a copied layout plan. Stale paragraph hashes are never
    treated as permission to rewrite teacher edits at the same paragraph index.
    """
    from lxml import etree

    from .same_slide import NS, _shape, fingerprint

    def paragraph(pair, language):
        shape = _shape(tree, pair[language + '_shape'])
        if shape is None:
            return None
        bodies = shape.findall('p:txBody', NS) or shape.findall('.//a:tc/a:txBody', NS)
        body, index = pair['body'], pair[language + '_paragraph']
        if body >= len(bodies):
            return None
        paragraphs = bodies[body].findall('a:p', NS)
        if index >= len(paragraphs) or fingerprint(paragraphs[index]) != pair[language + '_hash']:
            return None
        return paragraphs[index]

    def editable_text(node):
        value, ranges = '', []
        for child in node:
            if child.tag == '{' + NS['a'] + '}r' and child.find('a:t', NS) is not None:
                text = child.find('a:t', NS)
                start = len(value)
                value += text.text or ''
                ranges.append((text, start, len(value)))
            elif etree.QName(child).localname == 'br':
                value += '\n'
            elif etree.QName(child).localname not in {'pPr', 'endParaRPr'}:
                value += f'⟦BLC{len(value)}⟧'  # Fields, native equations and non-text runs stay opaque.
        return value, ranges

    changes = []
    for pair in pairs:
        if pair.get('neutral'):
            continue
        vi, en = paragraph(pair, 'vi'), paragraph(pair, 'en')
        if vi is None or en is None or vi is en:
            continue
        source, _ = editable_text(vi)
        before, ranges = editable_text(en)
        after = align_case(source, before, chemistry=True)
        if after == before or len(after) != len(before):
            continue
        for node, start, end in ranges:
            node.text = after[start:end]
        pair['en_hash'] = fingerprint(en)
        changes.append({'shape_id': pair['en_shape'], 'operation': 'align_translation_case'})
    return changes
