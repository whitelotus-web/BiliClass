"""Create a separate, editable bilingual PowerPoint from reviewed segments."""
import io
import tempfile
from pathlib import Path

from .lesson_templates import slide_pages, source_image
from .powerpoint import slide_for_locator


def export_deck(lesson, directory, destination, profile=None, terms=()):
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    from pptx.util import Inches, Pt
    target = Path(destination).with_suffix(".pptx").resolve()
    source = lesson.get("source")
    if source and target == (Path(directory) / "sources" / source["file"]).resolve():
        raise ValueError("Chọn đường dẫn mới để giữ nguyên tệp nguồn.")
    if not lesson.get("segments") or any(not s.get("approved") for s in lesson["segments"]):
        raise ValueError("Duyệt toàn bộ cặp Việt/Anh trước khi xuất PowerPoint.")
    from .source_deck import export_source_deck, is_source_style

    if is_source_style(lesson):
        return Path(export_source_deck(lesson, directory, target, terms)["path"])
    presentation = Presentation()
    presentation.slide_width, presentation.slide_height = Inches(13.333), Inches(7.5)
    source_deck = None
    if source and source.get("file", "").lower().endswith(".pptx"):
        from .powerpoint import verified_presentation
        source_deck = Presentation(verified_presentation(lesson, directory))

    def textbox(slide, text, x, y, w, h, size, color, bold=False, italic=False):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        frame = box.text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = Inches(.04)
        for i, line in enumerate(text.splitlines()):
            p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            p.text = line
            p.font.name, p.font.size, p.font.bold, p.font.italic = "Arial", Pt(size), bold, italic
            p.font.color.rgb = RGBColor.from_string(color)
        return box

    def pictures(shapes):
        for shape in shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                yield from pictures(shape.shapes)
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                yield shape

    def add_original_visual(source_slide):
        original = source_deck.slides[source_slide - 1]
        images = list(pictures(original.shapes))
        if not images:
            return
        visual = presentation.slides.add_slide(presentation.slide_layouts[6])
        visual.background.fill.solid()
        visual.background.fill.fore_color.rgb = RGBColor.from_string("F3F7FC")
        textbox(visual, lesson["title"][:100], .6, .35, 12, .65, 24, "112650", True)
        textbox(visual, f"Hình từ slide gốc {source_slide}", .65, 6.85, 12, .3, 12, "667997")
        for picture in images:
            # Keep relative positions without stretching or inventing captions.
            scale = min(11.6 / float(source_deck.slide_width), 5.55 / float(source_deck.slide_height))
            visual.shapes.add_picture(
                io.BytesIO(picture.image.blob),
                int(Inches(.85) + picture.left * scale),
                int(Inches(1.05) + picture.top * scale),
                width=int(picture.width * scale),
                height=int(picture.height * scale),
            )

    next_source_slide = 1
    preset = lesson.get("teaching_preset", "standard")
    if preset not in {"standard", "visual", "practice"}:
        raise ValueError("Kiểu dạy không hợp lệ.")
    for segment in lesson["segments"]:
        source_slide = slide_for_locator(segment.get("locator", "")) if source_deck else None
        if source_slide and source_slide <= len(source_deck.slides):
            while next_source_slide <= source_slide:
                add_original_visual(next_source_slide)
                next_source_slide += 1
        image_path = source_image(lesson, directory, segment)
        plans = slide_pages(lesson, segment, terms=terms, image=str(image_path) if image_path else "", profile=profile)
        for plan in plans:
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor.from_string(plan["background"].lstrip("#"))
            from pptx.enum.text import PP_ALIGN
            from pptx.util import Emu
            for item in plan["elements"]:
                box = slide.shapes.add_textbox(*(Emu(int(item[key] * 9525)) for key in ("x", "y", "width", "height")))
                frame = box.text_frame
                frame.word_wrap = True
                frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
                for index, line in enumerate(item["text"].splitlines()):
                    paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
                    paragraph.text = line
                    paragraph.font.name = plan["font"]
                    paragraph.font.size = Pt(item["size"] * .75)
                    paragraph.font.bold, paragraph.font.italic = item["bold"], item["italic"]
                    paragraph.font.color.rgb = RGBColor.from_string(item["color"].lstrip("#"))
                    paragraph.alignment = PP_ALIGN.CENTER if item["align"] == "center" else PP_ALIGN.LEFT
                    paragraph.space_before = paragraph.space_after = Pt(0)
                    paragraph.line_spacing = 1.15
            if image_path:
                from PIL import Image
                region = plan["image_box"]
                with Image.open(image_path) as image:
                    scale = min(region["width"] / image.width, region["height"] / image.height)
                    width, height = image.width * scale, image.height * scale
                slide.shapes.add_picture(str(image_path), Emu(int((region["x"] + (region["width"] - width) / 2) * 9525)),
                                         Emu(int((region["y"] + (region["height"] - height) / 2) * 9525)),
                                         width=Emu(int(width * 9525)), height=Emu(int(height * 9525)))
            logo_path = Path(directory) / "assets" / "school-logo.png"
            if profile and profile.get("show_profile", True) and logo_path.is_file():
                from PIL import Image
                with Image.open(logo_path) as logo:
                    ratio = logo.width / logo.height
                width, height = (.35, .35 / ratio) if ratio >= 1 else (.35 * ratio, .35)
                slide.shapes.add_picture(str(logo_path), Inches(12.55), Inches(.2), width=Inches(width), height=Inches(height))
            slide.notes_slide.notes_text_frame.text = ("BiliClass: nội dung đã duyệt. Đoạn: " + segment["id"] + "\n" + segment["locator"]
                                                      + "\nMẫu: " + preset + " / " + plan["kind"])
    if source_deck:
        while next_source_slide <= len(source_deck.slides):
            add_original_visual(next_source_slide)
            next_source_slide += 1
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".pptx", delete=False) as f:
        pending = Path(f.name)
    try:
        presentation.save(str(pending))
        pending.replace(target)
    finally:
        pending.unlink(missing_ok=True)
    return target
