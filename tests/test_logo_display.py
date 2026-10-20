from PIL import Image, ImageDraw

from app.logo_display import round_mask_safe


def test_round_mark_masks_only_clear_corners_and_preserves_source(tmp_path):
    path = tmp_path/'logo.png'
    image = Image.new('RGBA', (300, 300), 'white')
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 2, 297, 297), outline='#1377bc', width=10)
    draw.text((110, 140), 'School', fill='#1377bc')
    image.save(path)
    before = path.read_bytes()
    assert round_mask_safe(path)
    assert path.read_bytes() == before
    draw.rectangle((0, 0, 25, 25), fill='red')
    image.save(path)
    assert not round_mask_safe(path), 'Never crop a logo detail in the corner'


def test_wide_square_transparent_and_invalid_logos(tmp_path):
    path = tmp_path/'logo.png'
    for size, color in (((400, 120), 'blue'), ((200, 200), 'red')):
        Image.new('RGBA', size, color).save(path)
        assert not round_mask_safe(path)
    image = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(image).ellipse((20, 20, 180, 180), fill='blue')
    image.save(path)
    assert round_mask_safe(path)
    path.write_bytes(b'invalid image')
    assert not round_mask_safe(path)
    assert not round_mask_safe(tmp_path/'missing.png')
