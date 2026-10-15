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


def heading_frame(shape, units, box, slide_height):
    if not shape.has_text_frame:
        return False
    text = " ".join(unit["raw"] for unit in units).strip()
    if not (4 <= len(text) <= 130 and len(units) <= 2 and box["h"] < slide_height * 0.25):
        return False
    if re.match(r"^(?:Câu|Bước|Question|Exercise)\s*\d", text, re.I) or re.search(r"[;=!?]", text):
        return False
    if shape._element.xpath('.//*[local-name()="oMath"]'):
        return False
    sizes = [unit["font_size"] for unit in units]
    properties = etree.XPath(".//a:r[a:t[normalize-space()]]/a:rPr", namespaces=NS)(shape._element)
    bold = sum(p.get("b") == "1" for p in properties)
    return min(sizes, default=0) >= 2200 and bool(properties) and bold >= len(properties) * 0.6
