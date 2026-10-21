"""Keep imported narration sources separate from finished library products."""


def is_product(lesson):
    if not lesson.get('voice_only') or lesson.get('voice_published'):
        return True
    variants = lesson.get('narration_variants')
    records = [lesson.get('narration') or {}, *(variants.values() if isinstance(variants, dict) else [])]
    return any(type(record.get('total')) is int and record['total'] > 0
               and record.get('complete') == record['total'] and not record.get('failed')
               and not record.get('cancelled') for record in records if isinstance(record, dict))
