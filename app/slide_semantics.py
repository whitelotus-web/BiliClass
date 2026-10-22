"""Conservative structural labels and language-independent equation detection."""

import re

from lxml import etree

from .source_deck import NS


def roman_label(text):
    value = text.strip().rstrip(".)/:").strip()
    return bool(
        value and re.fullmatch(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})", value)
    )


def equation_only(paragraph):
    from .slide_speech import VI_MARKS

    native_math = bool(paragraph.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'))
    prose = "".join(
        node.text or ""
        for node in paragraph.findall(".//a:t", NS)
        if not any(
            etree.QName(parent).namespace == "http://schemas.openxmlformats.org/officeDocument/2006/math"
            for parent in node.iterancestors()
        )
    )
    # Do not classify a prose sentence containing a formula as a shared equation.
    prose = re.sub(r"\b(?:sin|cos|tan|cot|log|ln|exp|lim)\b", "", prose)
    if any(c in VI_MARKS for c in prose.casefold()) or re.search(r"[A-Za-z]{2,}", prose):
        return False
    if any(c.isalpha() and not ("a" <= c.casefold() <= "z" or "α" <= c.casefold() <= "ω") for c in prose):
        return False
    return native_math or bool(re.search(r"[=≤≥]", prose))


def quantity_only(text):
    """An isolated SI quantity has no second language to duplicate in a cell."""
    number = r'[+−-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)(?:[eE][+−-]?\d+)?'
    unit = r'(?:kg|mg|g|km|cm|mm|nm|m|ms|s|min|h|kHz|MHz|Hz|N|MPa|kPa|Pa|kJ|J|MW|kW|W|mV|V|mA|A|Ω|mol|K|°C|°F|rad|mL|ml|L|%)'
    power = r'(?:[²³]|\^[+−-]?\d+)?'
    return bool(re.fullmatch(number + r'\s*' + unit + power + r'(?:\s*/\s*' + unit + power + r')?', text.strip()))


def heading_frame(shape, units, box, slide_height):
    if not shape.has_text_frame:
        return False
    text = " ".join(unit["raw"] for unit in units).strip()
    if not (4 <= len(text) <= 130 and len(units) <= 2 and box["h"] < slide_height * 0.25):
        return False
    if re.match(r"^(?:Câu|Bước|Question|Exercise)\s*\d", text, re.I) or body_prose(text, len(units)) or '=' in text:
        return False
    if shape._element.xpath('.//*[local-name()="oMath"]'):
        return False
    sizes = [unit["font_size"] for unit in units]
    properties = etree.XPath(".//a:r[a:t[normalize-space()]]/a:rPr", namespaces=NS)(shape._element)
    bold = sum(p.get("b") == "1" for p in properties)
    return min(sizes, default=0) >= 2200 and bool(properties) and bold >= len(properties) * 0.6


def title_frame(shape, slide_width, slide_height):
    """Placeholder names are authoring hints; the actual content can be a body."""
    if not shape.has_text_frame:
        return False
    text = ' '.join(shape.text.split())
    paragraphs = [p for p in shape.text_frame.paragraphs if p.text.strip()]
    if (not text or body_prose(text, len(paragraphs))
            or shape.height >= slide_height * .3
            or re.search(r'(?:^|\s)[a-d][.)]\s', text, re.I)):
        return False
    placeholder = shape.is_placeholder and int(shape.placeholder_format.type) in {1, 3}
    top_band = 0 <= shape.top < slide_height * .18 and shape.width > slide_width * .22
    return placeholder or top_band


def body_prose(text, paragraph_count=1):
    return (len(text) >= 180 or paragraph_count > 2 or bool(re.search(r'[!?;]', text))
            or len(text) > 45 and bool(re.match(r'^(?:Cho|Hãy|Phải)\b', text, re.I)))
