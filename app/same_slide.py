"""Local bilingual typography and source-aware geometry; no language-page pairs."""

import copy
import hashlib
import re

from lxml import etree

from .source_deck import NS

_NUMBER_BADGE = re.compile(r'^\s*(?:Câu|Question|Hoạt động|Activity|Ví dụ|Example|Luyện tập|Practice)\s*\d+\s*$', re.I)


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


def style_paragraph(paragraph, source_size, *, english=False, title=False, label=False, canvas_scale=1):
    """Keep font family, symbols, alpha and emphasis; scale math with the prose."""
    props = _paragraph_style(paragraph)
    tabs = props.find("a:tabLst", NS)
    if tabs is not None:
        props.remove(tabs)
    for node in paragraph.findall(".//a:t", NS):
        if node.text:
            node.text = node.text.replace("\t", " ")
    visible = bool(text_of(paragraph).strip())
    # A large slide canvas does not mean every small source label should grow
    # twofold. Preserve its hierarchy and use the readable floor in points.
    minimum = min(source_size / 100, 14 * min(1, canvas_scale)) if label else 18 * min(1, canvas_scale)
    size = min(max(source_size / 100, minimum), (32 if title else 18 if label else 24) * canvas_scale)
    target = size * .82 if english and label else max(minimum, size * (0.82 if english else 1))
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
    from .slide_semantics import body_prose, heading_frame
    from .slide_speech import normalized, objects

    deck = Presentation(source)
    canvas_scale = max(.5, min(4, deck.slide_height / (540 * 12700)))
    manifest['font_fallbacks'] = missing_embedded_fonts(source)
    units_by_slide = {}
    for unit in manifest["units"]:
        units_by_slide.setdefault(unit["slide"], {}).setdefault(unit["shape_id"], []).append(unit)
    suppressed = {}
    for index, slide in enumerate(deck.slides, 1):
        items = objects(slide)
        from .framed_text import fit_box, owner, panels

        backgrounds = panels(slide, deck.slide_width, deck.slide_height)
        raster_backdrop = any(
            item["source_type"] == "image"
            and item["w"] * item["h"] > deck.slide_width * deck.slide_height * 0.6
            for item in items
        )
        boxes = {item["shape_id"]: item for item in items}
        shapes = {shape.shape_id: shape for shape in leaves(slide.shapes, modern=True)}
        texts = {key: shape for key, shape in shapes.items() if shape.has_text_frame and shape.text.strip()}
        animated = set(slide._element.xpath(".//p:spTgt/@spid"))
        fixed_targets = set(slide._element.xpath('.//p:animMotion//p:spTgt/@spid|.//p:cond/p:tgtEl/p:spTgt/@spid'))
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
            if box is None and shape.has_table:
                # Ordinary text extraction omits a cell containing only native
                # Office Math. Its grid still owns the canvas scale and margins.
                box = dict(x=shape.left, y=shape.top, w=shape.width, h=shape.height)
            if box is None:
                continue
            if shape.has_table:
                # Each cell owns its font and grid. A table is neither a title
                # nor one huge text frame to expand around its foreground art.
                for unit in units:
                    row, column = divmod(unit['body'], len(shape.table.columns))
                    cell = shape.table.cell(row, column)
                    left = box['x'] + sum(c.width for c in list(shape.table.columns)[:column]) * box['w']/shape.width
                    top = box['y'] + sum(r.height for r in list(shape.table.rows)[:row]) * box['h']/shape.height
                    width = sum(c.width for c in list(shape.table.columns)[column:column+cell.span_width]) * box['w']/shape.width
                    height = sum(r.height for r in list(shape.table.rows)[row:row+cell.span_height]) * box['h']/shape.height
                    margins = {}
                    for other in items:
                        if other['shape_id'] == key or other.get('hidden'):
                            continue
                        ox, oy, ow, oh = (other[n] for n in ('x', 'y', 'w', 'h'))
                        overlap = min(top+height, oy+oh)-max(top, oy)
                        if (other['source_type'] == 'image' and overlap > min(height, oh)*.15
                                and left+width*.45 < ox < left+width
                                and ow*oh < deck.slide_width*deck.slide_height*.6):
                            margins['marR'] = max(margins.get('marR', 0), round((left+width-ox+12700)*shape.width/box['w']))
                        if (other['text'] and len(other['text']) < 30 and overlap > min(height, oh)*.15
                                and left-width*.1 < ox < left+width*.2 and ow < width*.3):
                            margins['marL'] = max(margins.get('marL', 0), round((ox+ow-left+6*12700)*shape.width/box['w']))
                        if (other['text'] and top+height*.5 < oy < top+height
                                and min(left+width, ox+ow)-max(left, ox) > width*.5):
                            margins['marB'] = max(margins.get('marB', 0), round((top+height-oy+12700)*shape.height/box['h']))
                    unit.update(title=False, canvas_scale=canvas_scale, inline_pair=True, cell_margins=margins,
                                cell_heading=row == 0 and len(unit['raw']) <= 50 and unit['raw'].isupper())
                continue
            x, y, w, h = (box[name] for name in ("x", "y", "w", "h"))
            length = sum(len(u["raw"]) for u in units)
            compact_caption = (max(u['font_size'] for u in units) <= 1400 * min(1, canvas_scale)
                               and length < 140 and len(units) <= 2 and h < deck.slide_height * .055)
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
            if body_prose(' '.join(u['raw'] for u in units), len(units)):
                title = False  # A question/instruction block needs body columns, not a stacked heading.
            if re.match(r"^\s*(?:Câu|Bước|Question)\s*\d", units[0]["raw"], re.I):
                title = False
            if compact_caption:
                title = False  # Small running headers keep their original band and hierarchy.
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
                badge = bool(_NUMBER_BADGE.fullmatch(other['text']))
                if (badge
                        and ox < x + w * .25 and ox + ow > x0 and ox + ow < right
                        and min(y+h, oy+oh)-max(y, oy) > min(h, oh)*.3):
                    # A centered stem's source box can sit behind its numbered
                    # badge. Two language columns need their own clear left edge.
                    x0 = max(x0, ox + ow + 6 * 12700)
                if (
                    length > 40
                    and not badge
                    and other["text"]
                    and len(other["text"]) < 35
                    and oy < y0 + h * 0.3
                    and oy + oh > y0
                    and oh < 80 * 12700
                    and horizontal > min(w, ow) * 0.5
                ):
                    y0 = max(y0, oy + oh + 6 * 12700)
                if (other['text'] and horizontal > min(w, ow) * 0.3
                        and oy > y0 + max(20 * 12700 * canvas_scale, min(h * .3, 60 * 12700 * canvas_scale))):
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
            panel = owner(box, backgrounds) if not title and str(key) not in fixed_targets else None
            if panel:
                interior = fit_box(box, panel)
                x0, y0 = max(x0, interior['x']), max(y0, interior['y'])
                width = max(254000, min(interior['x'] + interior['w'], right) - x0)
                height = max(127000, min(interior['y'] + interior['h'], bottom) - y0)
            # Translate world-coordinate adjustments back into a group's coordinates.
            sx, sy = shape.width / max(1, w), shape.height / max(1, h)
            geometry = {
                "x": round(shape.left + (x0 - x) * sx),
                "y": round(shape.top + (y0 - y) * sy),
                "w": round(width * sx),
                "h": round(height * sy),
            }
            label = compact_caption or length < 25 and not title and h < 55 * 12700 * canvas_scale
            if label:
                # Question numbers and solution badges own small frames. The
                # surrounding question band is not their shared text container.
                geometry = dict(x=shape.left, y=shape.top, w=shape.width, h=shape.height)
            for unit in units:
                unit.update(
                    title=title,
                    canvas_scale=canvas_scale,
                    same_slide_box=geometry,
                    suppressed=key in duplicates,
                    inline_pair=label or width < 200 * 12700
                    or bool(shape._element.xpath('.//*[local-name()="oMath"]'))
                    and width < deck.slide_width * 0.52
                    and height > deck.slide_height * 0.4,
                    label=label,
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
    from .translation_batches import restore

    if units[0].get('inline_pair') or any(unit['title'] for unit in units):
        return True
    geometry=units[0].get('same_slide_box')
    if not geometry:
        return False
    width,height=geometry['w']/12700,geometry['h']/12700
    canvas = units[0].get('canvas_scale', 1)
    def costs(scale):
        vi=en=stacked=0
        for unit in units:
            original=unit['raw']
            english=restore(translations[unit['id']]['en'],unit.get('numbers',[]))
            size=min(max(unit['font_size']/100,18*min(1,canvas)),24*canvas)*scale
            en_size=max(18*min(1,canvas), min(max(unit['font_size']/100,18*min(1,canvas)),24*canvas)*.82)*scale
            vi+=text_height(original,max(1,(width-12*canvas)/2),size)
            en+=text_height(english,max(1,(width-12*canvas)/2),en_size)
            stacked+=text_height(original,max(1,width-6*canvas),size)
            if unit['language']!='neutral':
                stacked+=text_height(english,max(1,width-6*canvas),en_size)
        return max(vi,en),stacked
    columns,stacked=costs(1)
    if stacked <= height*.95 and stacked < columns*.9:
        return True
    # Wide, shallow answer bands often need some fitting either way. Compare
    # the size retained by each arrangement instead of always forcing columns.
    fitted=[0.,0.]
    for step in range(20,3,-1):
        scale=step/20
        for index,cost in enumerate(costs(scale)):
            if not fitted[index] and cost <= height*.95:
                fitted[index]=scale
        if all(fitted):
            break
    return fitted[1] > fitted[0]*1.1


def fit(shape, fallback_size, *, title=False, label=False):
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
    # Decorative headers often have an oversized invisible textbox. Centering
    # a new VI/EN pair in it can push white text below its painted title band.
    props.set(
        "anchor",
        props.get('anchor', 't') if title else "t"
        if shape.find('p:nvSpPr/p:cNvPr', NS).get('name', '').startswith('BCL_BODY ')
        or sum(bool(text_of(p).strip()) for p in paragraphs) > 2
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
    # Running headers/footer captions already use small source type. Enlarging
    # them to the body floor makes two-language labels spill from painted bands.
    minimum = min(8, fallback_size / 100 * .65) if label else 18
    floor = min(1, minimum / min(sizes, default=24))
    scale = 1.0
    while scale > floor and needed(scale) > height:
        scale -= 0.025
    scale = max(floor, scale)
    # Office Math does not consistently honor DrawingML's fontScale. Apply
    # the same fitted size to its run properties, leaving symbols/structure
    # intact, rather than shrinking only the surrounding prose.
    if body.xpath('.//*[local-name()="oMath"]') and scale < 1:
        for node in body.xpath('.//a:rPr[@sz]|.//a:defRPr[@sz]|.//a:endParaRPr[@sz]', namespaces=NS):
            node.set('sz', str(max(100, round(int(node.get('sz')) * scale))))
        scale = 1.0
    for child in list(props):
        if etree.QName(child).localname in {"noAutofit", "normAutofit", "spAutoFit"}:
            props.remove(child)
    etree.SubElement(
        props,
        f"{{{NS['a']}}}normAutofit",
        fontScale=str(round(scale * 100000)),
        lnSpcReduction="10000",
    )


def fit_cells(shape, fallback_size):
    """Apply the same bounded fitter within each cell, retaining the native grid."""
    table = shape.find('.//a:tbl', NS)
    if table is None:
        return
    widths = [int(c.get('w')) for c in table.findall('a:tblGrid/a:gridCol', NS)]
    rows = table.findall('a:tr', NS)
    for row_index, row in enumerate(rows):
        for column, cell in enumerate(row.findall('a:tc', NS)):
            body = cell.find('a:txBody', NS)
            if body is None or cell.get('hMerge') == '1' or cell.get('vMerge') == '1':
                continue
            width = sum(widths[column:column+int(cell.get('gridSpan', '1'))])
            height = sum(int(r.get('h')) for r in rows[row_index:row_index+int(cell.get('rowSpan', '1'))])
            margins = cell.find('a:tcPr', NS)
            if margins is not None:
                width -= int(margins.get('marL', '91440')) + int(margins.get('marR', '91440'))
                height -= int(margins.get('marT', '45720')) + int(margins.get('marB', '45720'))
            wrapper = etree.Element(f'{{{NS["p"]}}}sp')
            nv = etree.SubElement(wrapper, f'{{{NS["p"]}}}nvSpPr')
            etree.SubElement(nv, f'{{{NS["p"]}}}cNvPr', name='BCL_BODY cell')
            props = etree.SubElement(wrapper, f'{{{NS["p"]}}}spPr')
            transform = etree.SubElement(props, f'{{{NS["a"]}}}xfrm')
            etree.SubElement(transform, f'{{{NS["a"]}}}ext', cx=str(width), cy=str(height))
            copied = copy.deepcopy(body)
            copied.tag = f'{{{NS["p"]}}}txBody'
            # Cell margins live on tcPr, not bodyPr.
            bp = copied.find('a:bodyPr', NS)
            if bp is not None:
                for margin in ('lIns', 'rIns', 'tIns', 'bIns'):
                    bp.set(margin, '0')
            wrapper.append(copied)
            fit(wrapper, fallback_size)
            # PowerPoint ignores normAutofit for some table cells. Materialize
            # the bounded scale in run properties, preserving relative sizes.
            bp = copied.find('a:bodyPr', NS)
            autofit = bp.find('a:normAutofit', NS)
            scale = int(autofit.get('fontScale', '100000')) / 100000
            for node in copied.xpath('.//a:rPr[@sz]|.//a:defRPr[@sz]|.//a:endParaRPr[@sz]', namespaces=NS):
                node.set('sz', str(max(100, round(int(node.get('sz')) * scale))))
            autofit.set('fontScale', '100000')
            copied.tag = f'{{{NS["a"]}}}txBody'
            cell.replace(body, copied)


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
