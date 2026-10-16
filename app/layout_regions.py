"""Small geometry planner shared by captions and exported media controls."""


def intersection(a, b):
    return max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(
        0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    )


def empty_region(anchor, size, bounds, occupied, *, gap=6, clear=None):
    """Prefer nearby aligned slots, then a compact grid; never cover evidence."""
    x, y, w, h = anchor
    width, height = size
    page_width, page_height = bounds
    candidates = [(x, y + h + gap), (x + w + gap, y), (x, y - height - gap), (x - width - gap, y)]
    candidates += [
        (px, py)
        for py in range(round(gap), round(page_height - height - gap) + 1, 24)
        for px in range(round(gap), round(page_width - width - gap) + 1, 24)
    ]
    valid = []
    for index, (left, top) in enumerate(candidates):
        box = (left, top, width, height)
        if left < gap or top < gap or left + width > page_width - gap or top + height > page_height - gap:
            continue
        if any(intersection(box, other) > 0.5 for other in occupied):
            continue
        if clear is not None and not clear(box):
            continue
        if index < 4:
            return box
        distance = abs(left - x) + abs(top - y)
        valid.append((distance, box))
    return min(valid, key=lambda item: item[0])[1] if valid else None
