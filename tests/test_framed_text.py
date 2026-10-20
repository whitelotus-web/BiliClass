from io import BytesIO

from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

from app.framed_text import _painted_image, constrain_generated, panels
from app.native_bilingual import assemble, extract
from app.slide_quality import inspect_quality
from app.slide_speech import deck_speech
from app.source_deck import NS


def panel_deck(path):
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    for n in range(3):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(.6), Inches(1+n*1.8), Inches(12), Inches(1.4))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string('FFE580')
        text = slide.shapes.add_textbox(Inches(1.8), Inches(1.25+n*1.8), Inches(10), Inches(.6))
        text.text = 'Mục tiêu học tập: Nhận biết dao động qua đồ thị li độ theo thời gian và giải thích nguyên nhân làm tiêu hao cơ năng của hệ.'
        text.text_frame.paragraphs[0].font.size = Pt(26)
    deck.save(path)


def test_transparent_shadow_is_not_part_of_usable_panel():
    image = Image.new('RGBA', (500, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 499, 119), fill=(0, 0, 0, 60))
    draw.rounded_rectangle((15, 12, 484, 94), radius=12, fill='#ffe580')
    stream = BytesIO()
    image.save(stream, format='PNG')
    left, top, right, bottom = _painted_image(stream.getvalue())
    assert .02 < left < .05 and .08 < top < .13
    assert .77 < bottom < .82 and .95 < right < .99
    draw.ellipse((0, 0, 499, 119), fill=(0, 0, 0, 0))
    stream = BytesIO()
    image.save(stream, format='PNG')
    assert _painted_image(stream.getvalue()) is None


def test_new_bilingual_columns_fit_inside_their_actual_panels(tmp_path):
    source, target = tmp_path/'source.pptx', tmp_path/'bilingual.pptx'
    panel_deck(source)
    manifest = extract(source, 'parallel_columns', same_slide=True)
    translations = {u['id']: {'en': 'Learning objective: Identify oscillations through displacement-time graphs and explain the reasons for the mechanical energy loss of the system.'} for u in manifest['units']}
    assemble(source, target, manifest, translations, 'parallel_columns')
    deck = Presentation(target)
    report = inspect_quality(deck, deck_speech(target, deck), 'parallel_columns', layout_plan=manifest['layout_plan'])
    assert not any(i['code'] == 'panel_text_escape' for row in report['slides'] for i in row['issues'])
    assert len(manifest['layout_plan'][0]['pairs']) == 3
    bands = panels(deck.slides[0], deck.slide_width, deck.slide_height)
    assert len(bands) == 3
    before = etree.tostring(deck.slides[0]._element)
    # A deliberately escaped old generated frame is caught even if PowerPoint
    # thinks the glyphs fit into its oversized text box.
    shape = next(s for s in deck.slides[0].shapes if s.name.startswith('BCL_BODY '))
    shape.height = Inches(2)
    report = inspect_quality(deck, deck_speech(target, deck), 'parallel_columns', layout_plan=manifest['layout_plan'])
    assert any(i['code'] == 'panel_text_escape' for row in report['slides'] for i in row['issues'])
    tree = etree.fromstring(etree.tostring(deck.slides[0]._element))
    original_words = tree.xpath('.//a:t/text()', namespaces=NS)
    changes = constrain_generated(tree, deck.slides[0], deck.slide_width, deck.slide_height)
    assert changes and tree.xpath('.//a:t/text()', namespaces=NS) == original_words
    assert etree.tostring(tree) == before, 'Repair returns the frame to its intended panel'


def test_panel_repair_does_not_move_motion_targets_or_original_frames(tmp_path):
    source, target = tmp_path/'source.pptx', tmp_path/'generated.pptx'
    panel_deck(source)
    manifest = extract(source, 'parallel_columns', same_slide=True)
    values = {u['id']: {'en': 'Learning objective: Identify energy loss of the system.'} for u in manifest['units']}
    assemble(source, target, manifest, values, 'parallel_columns')
    deck = Presentation(target)
    slide = deck.slides[0]
    moving = next(s for s in slide.shapes if s.name.startswith('BCL_BODY '))
    moving.height = Inches(2)
    tree = etree.fromstring(etree.tostring(slide._element))
    timing = etree.SubElement(tree, '{' + NS['p'] + '}timing')
    motion = etree.SubElement(timing, '{' + NS['p'] + '}animMotion')
    etree.SubElement(motion, '{' + NS['p'] + '}spTgt', spid=str(moving.shape_id))
    before = etree.tostring(tree)
    assert constrain_generated(tree, slide, deck.slide_width, deck.slide_height) == []
    assert etree.tostring(tree) == before
    original = Presentation(source)
    tree = etree.fromstring(etree.tostring(original.slides[0]._element))
    assert constrain_generated(tree, original.slides[0], original.slide_width, original.slide_height) == []
