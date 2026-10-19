"""Local bilingual typography and source-aware geometry; no language-page pairs."""

import copy
import hashlib
import re

from lxml import etree

from .source_deck import NS


def text_of(node):
    return "".join(node.xpath('.//*[local-name()="t"]/text()'))


def fingerprint(paragraph):
    from .slide_speech import _visible_text

    return hashlib.sha256(" ".join(_visible_text(paragraph, math=True).split()).encode("utf-8")).hexdigest()


def _paragraph_style(paragraph):
    props = paragraph.find("a:pPr", NS)
    if props is None:
        props = etree.Element(f"{{{NS['a']}}}pPr")
        paragraph.insert(0, props)
    for position, tag in enumerate(("lnSpc", "spcBef", "spcAft")):
        previous = props.find("a:" + tag, NS)
        if previous is not None:
            props.remove(previous)
        spacing = etree.Element(f"{{{NS['a']}}}{tag}")
        etree.SubElement(
            spacing,
            f"{{{NS['a']}}}" + ("spcPct" if tag == "lnSpc" else "spcPts"),
            val="108000" if tag == "lnSpc" else "0",
        )
        props.insert(position, spacing)
    return props


def style_paragraph(paragraph, source_size, *, english=False, title=False, label=False):
    """Keep font family, symbols, alpha and emphasis; scale math with the prose."""
    props = _paragraph_style(paragraph)
    tabs = props.find("a:tabLst", NS)
    if tabs is not None:
        props.remove(tabs)
    for node in paragraph.findall(".//a:t", NS):
        if node.text:
            node.text = node.text.replace("\t", " ")
    visible = bool(text_of(paragraph).strip())
    size = min(max(source_size / 100, 18), 32 if title else 18 if label else 24)
    target = max(18, size * (0.82 if english else 1))
    scale = target / max(1, source_size / 100)
    default = props.find("a:defRPr", NS)
    if default is None:
        default = etree.SubElement(props, f"{{{NS['a']}}}defRPr")
    default.set("sz", str(round(target * 100)) if visible else "100")
    if english:
        default.set("lang", "en-US")
        default.set("i", "1")
        if not title:
            default.set("b", "0")
    if not title and props.get("algn") in {"just", "dist", "thaiDist"}:
        props.set("algn", "l")
    for node in paragraph.xpath(".//a:rPr|.//a:endParaRPr", namespaces=NS):
        if node.xpath('./a:solidFill/*/a:alpha[@val="0"]', namespaces=NS):
            continue
        old = int(node.get("sz", str(source_size)))
        node.set("sz", str(max(100, round(old * scale))) if visible else "100")
        if english and node.getparent().tag in {f"{{{NS['a']}}}r", f"{{{NS['a']}}}br"}:
            node.set("lang", "en-US")
            node.set("i", "1")
            if not title:
                node.set("b", "0")
    # English follows the same family as the source; no separate Latin fallback.
    return paragraph


def prepare(source, manifest):
    from pptx import Presentation

    from .native_bilingual import leaves
    from .native_fonts import missing_embedded_fonts
    from .slide_semantics import heading_frame
    from .slide_speech import normalized, objects

    deck = Presentation(source)
    manifest['font_fallbacks'] = missing_embedded_fonts(source)
    units_by_slide = {}
    for unit in manifest["units"]:
        units_by_slide.setdefault(unit["slide"], {}).setdefault(unit["shape_id"], []).append(unit)
    suppressed = {}
    for index, slide in enumerate(deck.slides, 1):
        items = objects(slide)
        raster_backdrop = any(
            item["source_type"] == "image"
            and item["w"] * item["h"] > deck.slide_width * deck.slide_height * 0.6
            for item in items
        )
        boxes = {item["shape_id"]: item for item in items}
        shapes = {shape.shape_id: shape for shape in leaves(slide.shapes, modern=True)}
        texts = {key: shape for key, shape in shapes.items() if shape.has_text_frame and shape.text.strip()}
        animated = set(slide._element.xpath(".//p:spTgt/@spid"))
        # A duplicated workspace caption must not become a second visible answer.
        signatures = {}
        for key, shape in texts.items():
            signature = re.sub(r"\W", "", normalized(shape.text).casefold())
            if len(signature) > 70:
                signatures.setdefault(signature, []).append(key)
        duplicates = set()
        for keys in signatures.values():
            if len(keys) < 2:
                continue
            keep = max(keys, key=lambda key: boxes[key]["h"])
            for key in keys:
                if key != keep and str(key) not in animated and boxes[key]["h"] < boxes[keep]["h"] * 0.35:
                    duplicates.add(key)
        suppressed[index] = sorted(duplicates)
        groups = units_by_slide.get(index, {})
        for key, units in groups.items():
            shape = shapes[key]
            box = boxes.get(key)
            if box is None:
                continue
            x, y, w, h = (box[name] for name in ("x", "y", "w", "h"))
            length = sum(len(u["raw"]) for u in units)
            title = bool(
                units[0]["title"]
                and length < 180
                and h < deck.slide_height * 0.3
                or len(texts) <= 2
                and length < 100
                and h < deck.slide_height * 0.22
                and max(u["font_size"] for u in units) >= 2600
            )
            title = title or heading_frame(shape, units, box, deck.slide_height)
            if re.match(r"^\s*(?:Câu|Bước|Question)\s*\d", units[0]["raw"], re.I):
                title = False
            x0, y0 = max(127000, x), max(127000, y)
            right, bottom = min(deck.slide_width - 127000, x + w), deck.slide_height - 127000
            for other in items:
                if other["shape_id"] == key or other["shape_id"] in duplicates:
                    continue
                ox, oy, ow, oh = (other[name] for name in ("x", "y", "w", "h"))
                if other["source_type"] == "image" and ow * oh > deck.slide_width * deck.slide_height * 0.6:
                    continue
                if ox > x0 + w * 0.5 and oy < y + h and oy + oh > y + min(h, deck.slide_height * 0.1):
                    right = min(right, ox - 12700)
                horizontal = min(x + w, ox + ow) - max(x, ox)
                if (
                    length > 100
                    and other["text"]
                    and len(other["text"]) < 35
                    and oy < y0 + h * 0.3
                    and oy + oh > y0
                    and oh < 80 * 12700
                    and horizontal > min(w, ow) * 0.5
                ):
                    y0 = max(y0, oy + oh + 6 * 12700)
                if horizontal > min(w, ow) * 0.3 and oy >= y + h - 12700 and oy > y0 + 127000:
                    bottom = min(bottom, oy - 12700)
            fixed_caption = raster_backdrop and length < 130 and len(units) <= 2 and h < deck.slide_height * .25
            if fixed_caption:
                # Decorative bands may be painted into a full-slide bitmap. Growing
                # the text box would pass overflow QA yet escape its original band.
                desired = h
            elif title:
                # Reserve a readable two-line heading without growing across a figure.
                desired = max(h, min(84 * 12700, bottom - y0))
            elif length < 25 and h < 55 * 12700:
                desired = max(h, 40 * 12700)
            else:
                desired = max(h, min(bottom - y0, h * 1.8 + 36 * 12700))
            height = max(127000, min(desired, bottom - y0))
            width = max(254000, right - x0)
            # Translate world-coordinate adjustments back into a group's coordinates.
            sx, sy = shape.width / max(1, w), shape.height / max(1, h)
            geometry = {
                "x": round(shape.left + (x0 - x) * sx),
                "y": round(shape.top + (y0 - y) * sy),
                "w": round(width * sx),
                "h": round(height * sy),
            }
            for unit in units:
                unit.update(
                    title=title,
                    same_slide_box=geometry,
                    suppressed=key in duplicates,
                    inline_pair=width < 200 * 12700
                    or bool(shape._element.xpath('.//*[local-name()="oMath"]'))
                    and width < deck.slide_width * 0.52
                    and height > deck.slide_height * 0.4,
                    label=length < 25 and not title and h < 55 * 12700,
                    question=bool(re.match(r"^\s*(?:Câu|Question)\s*\d", units[0]["raw"], re.I)),
                )
    manifest["suppressed_duplicates"] = suppressed


def apply_geometry(shape, unit):
    transform = shape.find("p:spPr/a:xfrm", NS)
    if transform is None or int(transform.get("rot", "0")) % 21600000:
        return
    geometry = unit.get("same_slide_box")
    if not geometry:
        return
    off, ext = transform.find("a:off", NS), transform.find("a:ext", NS)
    if off is not None and ext is not None:
        off.set("x", str(geometry["x"]))
        off.set("y", str(geometry["y"]))
        ext.set("cx", str(geometry["w"]))
        ext.set("cy", str(geometry["h"]))


def prefer_inline(units, translations):
    """Compare actual translated line costs rather than a single width cutoff."""
    from .native_layout import text_height

    if units[0].get('inline_pair') or any(unit['title'] for unit in units):
        return True
    geometry=units[0].get('same_slide_box')
    if not geometry:
        return False
    width,height=geometry['w']/12700,geometry['h']/12700
    if width>=400:
        return False
    vi=en=stacked=0
    for unit in units:
        original,english=unit['raw'],translations[unit['id']]['en']
        vi+=text_height(original,max(1,(width-12)/2),18)
        en+=text_height(english,max(1,(width-12)/2),16)
        stacked+=text_height(original,max(1,width-6),18)
        if unit['language']!='neutral':
            stacked+=text_height(english,max(1,width-6),16)
    return stacked <= height*.95 and stacked < max(vi,en)*.9


def fit(shape, fallback_size):
    """Uniform type scaling keeps VI/EN hierarchy and native equation proportions."""
    from .native_layout import text_height

    body = shape.find("p:txBody", NS)
    extent = shape.find("p:spPr/a:xfrm/a:ext", NS)
    if body is None or extent is None:
        return
    props = body.find("a:bodyPr", NS)
    if props is None:
        return
    props.set("wrap", "square")
    paragraphs = body.findall("a:p", NS)
    props.set(
        "anchor",
        "t"
        if sum(bool(text_of(p).strip()) for p in paragraphs) > 2
        or sum(len(text_of(p)) for p in paragraphs) > 180
        else "ctr",
    )
    for name in ("lIns", "rIns"):
        props.set(name, str(min(int(props.get(name, "91440")), 38100)))
    for name in ("tIns", "bIns"):
        props.set(name, "12700")
    width = (
        int(extent.get("cx")) - int(props.get("lIns", "91440")) - int(props.get("rIns", "91440"))
    ) / 12700
    height = (
        int(extent.get("cy")) - int(props.get("tIns", "45720")) - int(props.get("bIns", "45720"))
    ) / 12700

    def needed(scale):
        total = 0
        for paragraph in paragraphs:
            text = text_of(paragraph).strip()
            if not text:
                total += 1
                continue
            default = paragraph.find("a:pPr/a:defRPr", NS)
            size = int(default.get("sz", str(fallback_size)) if default is not None else fallback_size) / 100
            fraction = bool(paragraph.xpath('.//*[local-name()="f" or local-name()="rad"]'))
            total += text_height(text, max(1, width), size * scale) * (1.3 if fraction else 1)
        return total

    nonempty = [p for p in paragraphs if text_of(p).strip()]
    sizes = [
        int(p.find("a:pPr/a:defRPr", NS).get("sz", str(fallback_size))) / 100
        for p in nonempty
        if p.find("a:pPr/a:defRPr", NS) is not None
    ]
    floor = min(1, 18 / min(sizes, default=24))
    scale = 1.0
    while scale > floor and needed(scale) > height:
        scale -= 0.025
    for child in list(props):
        if etree.QName(child).localname in {"noAutofit", "normAutofit", "spAutoFit"}:
            props.remove(child)
    etree.SubElement(
        props,
        f"{{{NS['a']}}}normAutofit",
        fontScale=str(round(max(floor, scale) * 100000)),
        lnSpcReduction="10000",
    )


def _shape(tree, shape_id):
    nodes = tree.xpath(
        ".//p:sp[p:nvSpPr/p:cNvPr[@id=$id]]|.//p:graphicFrame[p:nvGraphicFramePr/p:cNvPr[@id=$id]]",
        namespaces=NS,
        id=str(shape_id),
    )
    return next(
        (
            node
            for node in nodes
            if not any(etree.QName(p).localname == "Fallback" for p in node.iterancestors())
        ),
        None,
    )


def visible_pairs(tree, pairs):
    """Re-check visible paragraph XML, never accept notes as proof of coverage."""
    for pair in pairs:
        for language in ("vi", "en"):
            shape = _shape(tree, pair[language + "_shape"])
            if shape is None:
                return False
            bodies = shape.findall("p:txBody", NS) or shape.findall(".//a:tc/a:txBody", NS)
            if pair["body"] >= len(bodies):
                return False
            paragraphs = bodies[pair["body"]].findall("a:p", NS)
            index = pair[language + "_paragraph"]
            if index >= len(paragraphs) or fingerprint(paragraphs[index]) != pair[language + "_hash"]:
                return False
    return True


def paginate(tree, pairs):
    """Split whole VI/EN paragraph pairs; repeat the native artwork and heading.

    Paragraph slots are blanked, not removed, so native animation ranges retain
    their meaning. A single indivisible equation/paragraph is never cut in half.
    """
    from .native_layout import text_height

    groups = {}
    for pair in pairs:
        if not pair.get("title") and not pair.get("question"):
            groups.setdefault(pair["source_shape"], []).append(pair)
    schedules = {}
    for key, group in groups.items():
        if len(group) < 2:
            continue
        shape = _shape(tree, group[0]["vi_shape"])
        extent = shape.find("p:spPr/a:xfrm/a:ext", NS)
        if extent is None:  # Table cells remain paired inside their own grid.
            continue
        height = int(extent.get("cy")) / 12700 - 4
        costs = []
        for pair in group:
            costs_by_language = []
            for language in ("vi", "en"):
                box = _shape(tree, pair[language + "_shape"])
                body = box.find("p:txBody", NS)
                paragraph = body.findall("a:p", NS)[pair[language + "_paragraph"]]
                width = int(box.find("p:spPr/a:xfrm/a:ext", NS).get("cx")) / 12700 - 6
                default = paragraph.find("a:pPr/a:defRPr", NS)
                size = min(18, int(default.get("sz", "2400")) / 100)
                fraction = bool(paragraph.xpath('.//*[local-name()="f" or local-name()="rad"]'))
                costs_by_language.append(
                    text_height(text_of(paragraph), width, size) * (1.3 if fraction else 1)
                )
            costs.append(sum(costs_by_language) if pair["inline"] else max(costs_by_language))
        if sum(costs) <= height * 0.93:
            continue
        # Keep an oversized paragraph on its own continuation. Skipping the
        # whole group repeated all its paragraphs on continuations created for
        # another frame, leaving too much text even for the native fitter.
        blocks = []
        for pair, cost in zip(group, costs, strict=True):
            if pair.get("neutral") and blocks:
                blocks[-1][0].append(pair["unit"])
                blocks[-1][1] += cost
            else:
                blocks.append([[pair["unit"]], cost])
        chunks, current, used = [], [], 0
        for identifiers, cost in blocks:
            if current and used + cost > height * 0.9:
                chunks.append(current)
                current = []
                used = 0
            current.extend(identifiers)
            used += cost
        if current:
            chunks.append(current)
        schedules[key] = chunks
    if not schedules:
        return [(tree, pairs)]
    pages = []
    for page in range(max(map(len, schedules.values()))):
        result = copy.deepcopy(tree)
        selected = []
        for pair in pairs:
            chunks = schedules.get(pair["source_shape"])
            if chunks is None or page < len(chunks) and pair["unit"] in chunks[page]:
                selected.append(pair)
                continue
            for language in ("vi", "en"):
                shape = _shape(result, pair[language + "_shape"])
                body = shape.find("p:txBody", NS)
                paragraph = body.findall("a:p", NS)[pair[language + "_paragraph"]]
                for child in list(paragraph):
                    paragraph.remove(child)
                style_paragraph(paragraph, 100)
        for key in schedules:
            for shape_id in {pair[language + "_shape"] for pair in groups[key] for language in ("vi", "en")}:
                fit(_shape(result, shape_id), 2400)
        pages.append((result, selected))
    return pages


def synchronize(tree, columns, paragraph_maps):
    """Duplicate native behaviors into the same time container, never a later click."""
    timing = tree.find("p:timing", NS)
    if timing is None:
        return
    highest = max([int(n) for n in timing.xpath(".//p:cTn/@id", namespaces=NS) if n.isdigit()] + [0])
    cloned = set()
    for target in list(timing.findall(".//p:spTgt", NS)):
        key = int(target.get("spid", "0"))
        for paragraph_range in target.findall(".//p:pRg", NS):
            mapping = paragraph_maps.get(key, {})
            start, end = (
                int(paragraph_range.get("st", "0")),
                int(paragraph_range.get("end", paragraph_range.get("st", "0"))),
            )
            if start in mapping and end in mapping:
                paragraph_range.set("st", str(mapping[start][0]))
                paragraph_range.set("end", str(mapping[end][-1]))
        if key not in columns:
            continue
        owner = next(
            (parent.getparent() for parent in target.iterancestors() if parent.tag == f"{{{NS['p']}}}cBhvr"),
            None,
        )
        if owner is None or owner in cloned:
            continue
        cloned.add(owner)
        duplicate = copy.deepcopy(owner)
        for node in duplicate.findall(".//p:spTgt", NS):
            if int(node.get("spid", "0")) == key:
                node.set("spid", str(columns[key]))
        clocks = {}
        for node in duplicate.findall(".//p:cTn", NS):
            highest += 1
            clocks[node.get("id")] = str(highest)
            node.set("id", str(highest))
        for node in duplicate.findall(".//p:tn", NS):
            if node.get("val") in clocks:
                node.set("val", clocks[node.get("val")])
        owner.addnext(duplicate)
    for build in list(timing.findall(".//p:bldP", NS)):
        key = int(build.get("spid", "0"))
        if key in columns:
            duplicate = copy.deepcopy(build)
            duplicate.set("spid", str(columns[key]))
            build.addnext(duplicate)
