"""Unmodified teacher-supplied speaker PNGs, fitted with native picture crops."""
from .paths import RESOURCE_ROOT

CLIPS = {'vi': (171, 248, 976, 976), 'en': (143, 220, 1020, 1020)}


def artwork(language, *, paused=False):
    if language in CLIPS:
        name = ('pause-' if paused else 'speaker-') + language + '.png'
        x, y, width, height = CLIPS[language]
        crop = {edge: str(round(value / 1254 * 100000)) for edge, value in
                [('l', x), ('t', y), ('r', 1254 - x - width), ('b', 1254 - y - height)]}
        return (RESOURCE_ROOT / 'assets/slide-speakers' / name).read_bytes(), crop
    name = ('speaker-pause-' if paused else 'speaker-') + language + '.png'
    return (RESOURCE_ROOT / 'assets/actions' / name).read_bytes(), None
