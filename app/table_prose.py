"""Join manual line wraps in one table question, retaining its source paragraph map."""

import copy
import re

from .translation_batches import TOKEN


def join_wrapped(units):
    groups = {}
    for unit in units:
        if unit.get('table_cell'):
            groups.setdefault((unit['slide'], unit['shape_id'], unit['body']), []).append(unit)
    replacements, removed = {}, set()
    for group in groups.values():
        if (not 2 <= len(group) <= 8 or any(u['xml_locks'] or u['language'] == 'en' for u in group)
                or not re.search(r'[.!?]$', group[-1]['raw'])
                or any(re.search(r'[.!?;:]$', u['raw']) for u in group[:-1])
                or len(group[0]['raw']) < 18
                or any(b['paragraph'] != a['paragraph']+1 for a, b in zip(group, group[1:]))):
            continue
        merged = copy.deepcopy(group[0])
        pieces, values = [], []
        for unit in group:
            offset = len(values)
            pieces.append(TOKEN.sub(lambda m: f'⟦BLC{int(m.group()[4:-1])+offset}⟧', unit['text']))
            values.extend(unit['numbers'])
        merged.update(text=' '.join(pieces), raw=' '.join(u['raw'] for u in group), numbers=values,
                      merged_paragraphs=[u['paragraph'] for u in group])
        replacements[group[0]['id']] = merged
        removed.update(u['id'] for u in group[1:])
    return [replacements.get(u['id'], u) for u in units if u['id'] not in removed]
