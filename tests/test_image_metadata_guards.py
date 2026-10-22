"""Reject oversized headers without decoding their declared image allocation."""

import hashlib
import struct
import sys
import zlib
from io import BytesIO

from PIL import Image

from app.framed_text import _painted_image
from app.library_thumbnails import cover_image
from app.logo_display import round_mask_safe


def oversized_header():
    output = BytesIO()
    Image.new('RGB', (1, 1)).save(output, 'PNG')
    data = bytearray(output.getvalue())
    data[16:24] = struct.pack('>II', 100000, 100000)
    data[29:33] = struct.pack('>I', zlib.crc32(data[12:29]))
    return bytes(data)


def test_oversized_embedded_image_is_not_treated_as_a_text_panel():
    limit = Image.MAX_IMAGE_PIXELS
    assert _painted_image(oversized_header()) is None
    assert Image.MAX_IMAGE_PIXELS == limit


def test_oversized_logo_header_keeps_safe_default_mask_without_crashing(tmp_path):
    path = tmp_path/'oversized.png'
    path.write_bytes(oversized_header())
    assert not round_mask_safe(path)
    assert path.read_bytes() == oversized_header()


def test_corrupt_oversized_cover_cache_is_regenerated_from_the_valid_slide(tmp_path):
    original = tmp_path/'slide.png'
    Image.new('RGB', (160, 90), 'navy').save(original)
    before = original.read_bytes()
    folder = tmp_path/'temp/library-covers'
    folder.mkdir(parents=True)
    cached = folder/(hashlib.sha256(before).hexdigest()+'.png')
    cached.write_bytes(oversized_header())
    assert cover_image(original, tmp_path) == str(cached)
    with Image.open(cached) as image:
        assert image.size == (640, 360)
        image.verify()
    assert original.read_bytes() == before


def test_panel_cache_does_not_keep_the_large_input_image_alive():
    output = BytesIO()
    Image.new('RGB', (100, 100), 'navy').save(output, 'PNG')
    blob = output.getvalue() + b'padding-after-image' * 100000
    references = sys.getrefcount(blob)
    assert _painted_image(blob) == (0, 0, 1, 1)
    assert _painted_image(blob) == (0, 0, 1, 1)
    assert sys.getrefcount(blob) == references
