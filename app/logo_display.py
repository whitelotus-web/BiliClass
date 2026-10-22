"""Inspect display-only corner masking; never rewrite the school's artwork."""
from functools import lru_cache
from pathlib import Path

from PIL import Image


def round_mask_safe(path):
    path = Path(path)
    try:
        stat = path.stat()
        return _inspect(str(path), stat.st_size, stat.st_mtime_ns)
    except OSError:
        return False


@lru_cache(maxsize=16)
def _inspect(path, size, modified):
    try:
        with Image.open(path) as source:
            if (max(source.size) > 4096 or min(source.size) < 16
                    or abs(source.width/source.height-1) > .02):
                return False
            image = source.convert('RGBA').resize((128, 128), Image.Resampling.LANCZOS)
        ink = 0
        for y in range(128):
            for x in range(128):
                red, green, blue, alpha = image.getpixel((x, y))
                colored = alpha >= 16 and min(red, green, blue) < 240
                if colored:
                    ink += 1
                    # Leave a narrow allowance for the circle's antialiased rim.
                    if ((x+.5-64)/64)**2 + ((y+.5-64)/64)**2 > 1.04:
                        return False
        return ink > 8
    except (OSError, ValueError, Image.DecompressionBombError):
        return False
