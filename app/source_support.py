"""Add language support in clear slide space; crowded slides get support pages."""

import copy
import textwrap

from lxml import etree

from .level_conversion import support_for_level


def _panel(tree, rect, text, label, ns, size=22):
    def add(parent, prefix, tag, **attrs):
        return etree.SubElement(parent, f"{{{ns[prefix]}}}{tag}", **{key: str(value) for key, value in attrs.items()})

    ids = [int(value) for value in etree.XPath(".//p:cNvPr/@id", namespaces=ns)(tree)]
    owner = tree.find("p:cSld/p:spTree", ns)
    shape = add(owner, "p", "sp")
    nv = add(shape, "p", "nvSpPr")
    add(nv, "p", "cNvPr", id=max(ids, default=0) + 1, name="BiliClass language support")
    add(nv, "p", "cNvSpPr", txBox=1)
    add(nv, "p", "nvPr")
    properties = add(shape, "p", "spPr")
    transform = add(properties, "a", "xfrm")
    x, y, width, height = rect
    add(transform, "a", "off", x=int(x), y=int(y))
    add(transform, "a", "ext", cx=int(width), cy=int(height))
    add(add(properties, "a", "prstGeom", prst="rect"), "a", "avLst")
    add(add(properties, "a", "solidFill"), "a", "srgbClr", val="F5F8FF")
    add(add(add(properties, "a", "ln", w=12700), "a", "solidFill"), "a", "srgbClr", val="BCD0ED")
    body = add(shape, "p", "txBody")
    add(body, "a", "bodyPr", wrap="square", lIns=127000, rIns=127000, tIns=90000, bIns=90000)
    add(body, "a", "lstStyle")
    for index, line in enumerate((label + "\n" + text).splitlines()):
        paragraph = add(body, "a", "p")
        add(add(add(paragraph, "a", "pPr"), "a", "lnSpc"), "a", "spcPct", val=120000)
        run = add(paragraph, "a", "r")
        style = add(run, "a", "rPr", sz=size * 100, b=1 if index == 0 else 0)
        add(add(style, "a", "solidFill"), "a", "srgbClr", val="17365D")
        add(style, "a", "latin", typeface="Arial")
        add(run, "a", "t").text = line


def _height(text, width, size=22):
    columns = max(1, int((width / 12700 - 20) / (size * .6)))
    lines = sum(max(1, len(textwrap.wrap(line, columns))) for line in text.splitlines())
    return (lines * size * 1.2 + 20) * 12700


def _clear_region(slide, slide_width, slide_height, text):
    if slide._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}timing") is not None or any(s.rotation for s in slide.shapes):
        return None  # Animated/rotated objects may occupy space beyond their box.
    margin = min(slide_width, slide_height) * .025
    # Group bounding boxes intentionally count as occupied: never cover media,
    # diagrams or an object merely because its text could not be extracted.
    occupied = [(s.left - margin, s.top - margin, s.left + s.width + margin, s.top + s.height + margin)
                for s in slide.shapes]
    for width in (slide_width * .93, slide_width * .44):
        height = _height(text, width)
        if height > slide_height * .8:
            continue
        xs = {slide_width * .035, slide_width * .965 - width}
        ys = {slide_height * .94 - height, slide_height * .06}
        for left, top, right, bottom in occupied[:80]:
            xs.update((right, left - width))
            ys.update((bottom, top - height))
        for y in sorted(ys, reverse=True):
            for x in sorted(xs, reverse=True):
                if x < margin or y < margin or x + width > slide_width - margin or y + height > slide_height - margin:
                    continue
                if not any(x < right and x + width > left and y < bottom and y + height > top
                           for left, top, right, bottom in occupied):
                    return x, y, width, height
    return None


def apply_support(slide, deck, items, level, terms, ns):
    additions, warnings = [], []
    for unit, content in items:
        segment = content["segment"]
        support = support_for_level(segment, level, terms)
        if support["missing_vocabulary"]:
            warnings.append(unit["locator"] + ": chưa có thuật ngữ đã chuẩn bị cho L0/L1.")
        if support["missing_easy"]:
            warnings.append(unit["locator"] + ": L2 dùng câu đầu của bản Anh đã duyệt; chưa có câu Anh dễ riêng.")
        # Existing bilingual source gets only additional reviewed classroom
        # prompts/vocabulary, never another copy of its existing translation.
        if segment.get("existing_pair") or segment.get("paired_locator"):
            text = support["text"] if level < 2 else ""
        elif segment.get("source_language") == "en":
            text = segment["vi"]  # Supply the missing Vietnamese support.
        elif segment.get("vi", "").strip() == segment.get("en", "").strip():
            text = ""
        else:
            text = support["text"]
        if text:
            additions.append(text)
    text = "\n\n".join(dict.fromkeys(additions))
    base = copy.deepcopy(slide._element)
    if not text:
        return base, [], "existing", warnings
    label = "Language support / Hỗ trợ ngôn ngữ"
    region = _clear_region(slide, deck.slide_width, deck.slide_height, label + "\n" + text)
    if region:
        _panel(base, region, text, label, ns)
        return base, [], "added", warnings
    # Support pages keep the source theme/background; source object/animation
    # XML is left untouched on the original slide. No animation references to
    # removed objects may remain on the new page.
    width, height = deck.slide_width * .93, deck.slide_height * .8
    columns = max(1, int((width / 12700 - 20) / (22 * .6)))
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, columns) or [""])
    capacity = max(1, int((height / 12700 - 20) / (22 * 1.2)) - 2)
    pages = []
    for offset in range(0, len(lines), capacity):
        page = copy.deepcopy(slide._element)
        owner = page.find("p:cSld/p:spTree", ns)
        for child in list(owner):
            if etree.QName(child).localname not in {"nvGrpSpPr", "grpSpPr"}:
                owner.remove(child)
        for name in ("timing", "transition"):
            element = page.find("p:" + name, ns)
            if element is not None:
                page.remove(element)
        _panel(page, (deck.slide_width * .035, deck.slide_height * .1, width, height),
               "\n".join(lines[offset:offset + capacity]), label, ns)
        pages.append(page)
    return base, pages, "support_pages", warnings
