"""Add reviewed language versions to a copy of a PowerPoint's native package.

Unchanged package parts pass through byte-for-byte. Text remains editable; slide
masters, media, drawings and timing XML are not flattened into screenshots.
"""

import copy
import json
import posixpath
import re
import tempfile
import textwrap
import zipfile
from pathlib import Path

from lxml import etree

from .presentation_policy import presentation_content

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
      "ct": "http://schemas.openxmlformats.org/package/2006/content-types"}


def text_blocks(presentation):
    """Use exactly the same ordered source units for import and native export."""
    def leaves(shapes):
        for shape in shapes:
            if hasattr(shape, "shapes"):
                yield from leaves(shape.shapes)
            else:
                yield shape

    blocks = []
    for index, slide in enumerate(presentation.slides, 1):
        units = []
        for shape in sorted(leaves(slide.shapes), key=lambda value: (value.top, value.left)):
            if shape.has_text_frame:
                text = shape.text.strip()
            elif shape.has_table:
                text = "\n".join(" | ".join(cell.text for cell in row.cells) for row in shape.table.rows).strip()
                if not text.strip(" |\n"):
                    text = ""
            else:
                continue
            if text:
                units.append({"text": text, "shape": shape, "slide": index})
        for part, unit in enumerate(units, 1):
            unit["locator"] = f"Slide {index}" if len(units) == 1 else f"Slide {index} · ý {part}"
            blocks.append(unit)
    return blocks


def is_source_style(lesson):
    return lesson.get("presentation_style", "template") == "source"


def _xml(data):
    return etree.fromstring(data, etree.XMLParser(resolve_entities=False, no_network=True))


def _bytes(tree):
    return etree.tostring(tree, encoding="UTF-8", xml_declaration=True, standalone=True)


def _size(frame, shape):
    sizes = [value for p in frame.paragraphs for value in
             [p.font.size, *(run.font.size for run in p.runs)] if value]
    if sizes:
        return max(sizes) / 12700
    if shape.is_placeholder:
        for collection in (shape.part.slide.slide_layout.placeholders, shape.part.slide.slide_master.placeholders):
            for placeholder in collection:
                if placeholder.placeholder_format.type == shape.placeholder_format.type and placeholder.has_text_frame:
                    values = [p.font.size for p in placeholder.text_frame.paragraphs if p.font.size]
                    if values:
                        return max(values) / 12700
        if int(shape.placeholder_format.type) in (1, 3):
            return 32
    return 18


def _replace_text(body, text, size):
    """Keep paragraph/run appearance, replacing only the reviewed language text."""
    original = list(body.findall("a:p", NS))
    for paragraph in original:
        body.remove(paragraph)
    for index, line in enumerate(text.replace("\v", "\n").split("\n")):
        template = original[min(index, len(original) - 1)] if original else etree.Element(f"{{{NS['a']}}}p")
        paragraph = copy.deepcopy(template)
        style = paragraph.find("a:r/a:rPr", NS)
        if style is None:
            style = paragraph.find("a:pPr/a:defRPr", NS)
        style = copy.deepcopy(style) if style is not None else etree.Element(f"{{{NS['a']}}}rPr")
        style.tag = f"{{{NS['a']}}}rPr"
        style.set("sz", str(round(size * 100)))
        # A translated run must not acquire a hyperlink from an unrelated word.
        for link in list(style):
            if etree.QName(link).localname in {"hlinkClick", "hlinkMouseOver"}:
                style.remove(link)
        for child in list(paragraph):
            if etree.QName(child).localname != "pPr":
                paragraph.remove(child)
        ppr = paragraph.find("a:pPr", NS)
        if ppr is None:
            ppr = etree.SubElement(paragraph, f"{{{NS['a']}}}pPr")
        # Fix an explicit line height for the measured translated text.
        for position, tag in enumerate(("lnSpc", "spcBef", "spcAft")):
            previous = ppr.find("a:" + tag, NS)
            if previous is not None:
                ppr.remove(previous)
            spacing = etree.Element(f"{{{NS['a']}}}{tag}")
            etree.SubElement(spacing, f"{{{NS['a']}}}" + ("spcPct" if tag == "lnSpc" else "spcPts"),
                             val="115000" if tag == "lnSpc" else "0")
            ppr.insert(position, spacing)
        run = etree.SubElement(paragraph, f"{{{NS['a']}}}r")
        run.append(style)
        etree.SubElement(run, f"{{{NS['a']}}}t").text = line
        body.append(paragraph)
    bodypr = body.find("a:bodyPr", NS)
    if bodypr is not None:
        bodypr.set("wrap", "square")
        for child in list(bodypr):
            if etree.QName(child).localname in {"normAutofit", "spAutoFit", "noAutofit"}:
                bodypr.remove(child)
        warp = bodypr.find("a:prstTxWarp", NS)
        bodypr.insert(bodypr.index(warp) + 1 if warp is not None else 0, etree.Element(f"{{{NS['a']}}}noAutofit"))


def _fit(text, frame, shape, width, height, locator):
    width = (width - frame.margin_left - frame.margin_right) / 12700
    height = (height - frame.margin_top - frame.margin_bottom) / 12700
    original_size = _size(frame, shape)
    minimum = min(original_size, 18)
    for size in range(int(original_size), int(minimum) - 1, -1):
        columns = max(1, int(width / (size * .6)))
        lines = sum(max(1, len(textwrap.wrap(line, columns))) for line in text.replace("\v", "\n").splitlines())
        if width > size and lines * size * 1.2 <= height:
            return size
    raise ValueError(f"{locator}: bản dịch quá dài cho ô chữ gốc. Rút gọn bản dịch và duyệt lại, hoặc chọn bố cục của BiliClass.")


def _apply(tree, unit, text):
    shape = unit["shape"]
    nodes = etree.XPath(".//p:cNvPr[@id=$id]/..", namespaces=NS)(tree, id=str(shape.shape_id))
    if len(nodes) != 1:
        raise ValueError("Không xác định được đối tượng chữ trong PowerPoint gốc.")
    node = nodes[0].getparent()
    if shape.has_table:
        rows = text.splitlines()
        if len(rows) != len(shape.table.rows):
            raise ValueError(unit["locator"] + ": giữ số dòng và dấu | phân cột của bảng khi dịch.")
        cells = node.findall(".//a:tbl/a:tr", NS)
        for row_index, (row, translated) in enumerate(zip(shape.table.rows, rows, strict=True)):
            values = [value.strip() for value in translated.split("|")]
            if len(values) != len(row.cells):
                raise ValueError(unit["locator"] + ": giữ dấu | phân cột của bảng khi dịch.")
            for column, (cell, value) in enumerate(zip(row.cells, values, strict=True)):
                if cell.text.strip() == value:
                    continue
                body = cells[row_index].findall("a:tc", NS)[column].find("a:txBody", NS)
                size = _fit(value, cell.text_frame, shape, shape.table.columns[column].width, row.height, unit["locator"])
                _replace_text(body, value, size)
    else:
        if shape.text.strip() == text.strip():
            return
        size = _fit(text, shape.text_frame, shape, shape.width, shape.height, unit["locator"])
        _replace_text(node.find("p:txBody", NS), text, size)


def _part_relative(owner, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(owner), target)) if not target.startswith("/") else target[1:]


def _rels_path(part):
    return posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")


def _clone_owned_part(part, index, entries, types, cloned):
    """PowerPoint requires each duplicated chart to own its chart/workbook parts."""
    if part in cloned:
        return cloned[part]
    path = Path(part)
    new_part = str(path.with_name(f"{path.stem}-biliclass-{index}{path.suffix}")).replace("\\", "/")
    if new_part in entries:
        raise ValueError("Tệp nguồn đã chứa đối tượng BiliClass. Hãy nhập PowerPoint gốc.")
    cloned[part] = new_part
    entries[new_part] = entries[part]
    for override in list(types):
        if override.get("PartName") == "/" + part:
            etree.SubElement(types, f"{{{NS['ct']}}}Override", PartName="/" + new_part,
                             ContentType=override.get("ContentType"))
            break
    relation_path = _rels_path(part)
    if relation_path in entries:
        relationships = _xml(entries[relation_path])
        for relation in relationships:
            if relation.get("TargetMode") == "External":
                continue
            # Media/theme parts can be shared. Mutable chart dependencies must
            # be copied too, including the embedded workbook and chart styles.
            if relation.get("Type", "").rsplit("/", 1)[-1] in {"image", "theme"}:
                continue
            dependency = _part_relative(part, relation.get("Target"))
            copied = _clone_owned_part(dependency, index, entries, types, cloned)
            relation.set("Target", posixpath.relpath(copied, posixpath.dirname(new_part)))
        entries[_rels_path(new_part)] = _bytes(relationships)
    return new_part


def _append_slide(part, tree, token, entries, types, relations, slide_list, sid, slide_id):
    new_part = f"ppt/slides/biliclass-en-{token}.xml"
    if new_part in entries:
        raise ValueError("Tệp nguồn đã chứa slide BiliClass. Hãy nhập bản gốc của thầy cô.")
    entries[new_part] = _bytes(tree)
    etree.SubElement(types, f"{{{NS['ct']}}}Override", PartName="/" + new_part,
                     ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml")
    source_rels = _rels_path(part)
    if source_rels in entries:
        copied_rels, cloned = _xml(entries[source_rels]), {}
        for relation in copied_rels:
            if relation.get("TargetMode") == "External":
                continue
            if relation.get("Type", "").rsplit("/", 1)[-1] in {
                    "chart", "chartUserShapes", "oleObject", "package", "comments", "tags",
                    "diagramData", "diagramLayout", "diagramQuickStyle", "diagramColors"}:
                owned = _part_relative(part, relation.get("Target"))
                copied = _clone_owned_part(owned, token, entries, types, cloned)
                relation.set("Target", posixpath.relpath(copied, posixpath.dirname(new_part)))
            if relation.get("Type", "").endswith("/notesSlide"):
                old_note = _part_relative(part, relation.get("Target"))
                new_note = f"ppt/notesSlides/biliclass-en-{token}.xml"
                entries[new_note] = entries[old_note]
                note_rels = _rels_path(old_note)
                if note_rels in entries:
                    copied_notes = _xml(entries[note_rels])
                    for back_link in copied_notes:
                        if back_link.get("Type", "").endswith("/slide"):
                            back_link.set("Target", "../slides/" + posixpath.basename(new_part))
                    entries[_rels_path(new_note)] = _bytes(copied_notes)
                relation.set("Target", "../notesSlides/" + posixpath.basename(new_note))
                etree.SubElement(types, f"{{{NS['ct']}}}Override", PartName="/" + new_note,
                                 ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml")
        entries[_rels_path(new_part)] = _bytes(copied_rels)
    rid = "biliEnglish" + str(token)
    if any(item.get("Id") == rid for item in relations):
        raise ValueError("Mã liên kết slide trùng với bản đã chuyển đổi; nhập lại PowerPoint gốc.")
    etree.SubElement(relations, f"{{{NS['rel']}}}Relationship", Id=rid,
                     Type=NS["r"] + "/slide", Target="slides/" + posixpath.basename(new_part))
    added = copy.deepcopy(sid)
    added.set("id", str(slide_id))
    added.set(f"{{{NS['r']}}}id", rid)
    slide_list.insert(slide_list.index(sid) + 1, added)
    return added


def export_source_deck(lesson, directory, destination, terms=()):
    """Return output path and slide→source mapping for a reviewed native deck."""
    from pptx import Presentation

    from .powerpoint import verified_presentation

    source = verified_presentation(lesson, directory)
    target = Path(destination).with_suffix(".pptx").resolve()
    if source.resolve() == target:
        raise ValueError("Chọn đường dẫn mới để giữ nguyên tệp nguồn.")
    mode = lesson.get("conversion_mode", "paired")
    if mode not in {"preserve", "level", "paired"}:
        raise ValueError("Cách chuyển đổi PowerPoint không hợp lệ.")
    if mode != "preserve" and (not lesson.get("segments") or any(not s.get("approved") for s in lesson["segments"])):
        raise ValueError("Duyệt toàn bộ cặp Việt/Anh trước khi xuất PowerPoint.")
    deck = Presentation(source)
    units = text_blocks(deck)
    if mode == "preserve":
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".pptx", delete=False) as pending:
            pending_path = Path(pending.name)
        try:
            pending_path.write_bytes(source.read_bytes())
            pending_path.replace(target)
        finally:
            pending_path.unlink(missing_ok=True)
        return {"path": str(target), "slide_map": list(range(1, len(deck.slides) + 1)),
                "report": [{"mode": "preserve", "message": "Giữ nguyên PowerPoint; trợ giảng chỉ dùng nội dung đã duyệt."}]}
    groups = {}
    image_segments = []
    for segment in lesson["segments"]:
        if segment.get("source_image_only"):
            image_segments.append(segment)
            continue
        locator = re.sub(r"(?: · phần \d+)+$", "", segment["locator"])
        groups.setdefault(locator, []).append(segment)
    if set(groups) != {unit["locator"] for unit in units}:
        raise ValueError("Các đoạn không còn khớp đối tượng PowerPoint gốc. Nhập lại tệp, hoặc chọn bố cục của BiliClass.")
    by_slide = {}
    for unit in units:
        segments = groups[unit["locator"]]
        if any(s.get("source_text", "").strip() != unit["text"] for s in segments):
            raise ValueError(unit["locator"] + ": đoạn nguồn không khớp; nhập lại tệp trước khi giữ thiết kế gốc.")
        joined = {**segments[0], "source_language": segments[0].get("source_language", lesson.get("source_language", "vi")),
                  "vi": "\n".join(s["vi"] for s in segments), "en": "\n".join(s["en"] for s in segments),
                  "support": [item for s in segments for item in s.get("support", [])] if len(segments) == 1 else []}
        layout = lesson.get("layout", "line_pair")
        if mode == "paired" and layout == "level_auto":
            layout = "line_pair"
        content = presentation_content(joined, lesson.get("level", 2), layout, terms=terms)
        content["segment"] = joined
        by_slide.setdefault(unit["slide"], []).append((unit, content))
    for segment in image_segments:
        match = re.fullmatch(r"Slide (\d+) · hình nguồn", segment["locator"])
        index = int(match[1]) if match else 0
        if (not 1 <= index <= len(deck.slides) or any(u["slide"] == index for u in units)
                or segment.get("source_ref") != f"{lesson['source']['sha256']}/{deck.slides[index - 1].part.partname}/image"):
            raise ValueError("Nội dung ảnh không còn khớp slide nguồn.")
        unit = {"slide": index, "locator": segment["locator"], "text": segment["source_text"], "image_only": True}
        content = presentation_content(segment, lesson.get("level", 2), lesson.get("layout", "line_pair"), terms=terms)
        content["segment"] = segment
        by_slide.setdefault(index, []).append((unit, content))
    with zipfile.ZipFile(source) as archive:
        entries = {item.filename: archive.read(item) for item in archive.infolist()}
    presentation = _xml(entries["ppt/presentation.xml"])
    relations = _xml(entries["ppt/_rels/presentation.xml.rels"])
    types = _xml(entries["[Content_Types].xml"])
    slide_list = presentation.find("p:sldIdLst", NS)
    originals = list(slide_list)
    highest_id = max(int(item.get("id")) for item in originals)
    slide_map, report = [], []
    for index, (slide, sid) in enumerate(zip(deck.slides, originals, strict=True), 1):
        part = str(slide.part.partname)[1:]
        items = by_slide.get(index, [])
        if not items:
            slide_map.append(index)  # Image-only slides remain in their original positions.
            continue
        base, english = copy.deepcopy(slide._element), copy.deepcopy(slide._element)
        if (mode == "level" and lesson.get("level", 2) < 4) or any(u.get("image_only") for u, _c in items):
            from .source_support import apply_support

            base, extra_slides, action, warnings = apply_support(slide, deck, items, lesson.get("level", 2), terms, NS)
            if action == "added":
                entries[part] = _bytes(base)
            # Otherwise the native source slide bytes remain untouched.
            report.append({"slide": index, "action": action, "warnings": warnings})
            slide_map.append(index)
            previous = sid
            for number, extra in enumerate(extra_slides, 1):
                highest_id += 1
                token = str(index) if number == 1 else f"{index}-{number}"
                previous = _append_slide(part, extra, token, entries, types, relations, slide_list, previous, highest_id)
                slide_map.append(index)
            continue
        if mode == "level":
            # L4 prioritizes English. A separate VI box already paired with an
            # English box is left empty on the exported copy to avoid duplication.
            for unit, content in items:
                segment = content["segment"]
                value = "" if segment.get("paired_locator") and segment.get("source_language") == "vi" else content["en"]
                if not value:
                    node = etree.XPath(".//p:cNvPr[@id=$id]/..", namespaces=NS)(base, id=str(unit["shape"].shape_id))[0].getparent()
                    for body in node.findall(".//a:txBody", NS) + node.findall("p:txBody", NS):
                        _replace_text(body, "", 18)
                else:
                    _apply(base, unit, value)
            entries[part] = _bytes(base)
            slide_map.append(index)
            report.append({"slide": index, "action": "english", "warnings": ["VI Rescue được giữ trong dự án BiliClass."]})
            continue
        show_vi, show_en = items[0][1]["show_vi"], items[0][1]["show_en"]
        for unit, content in items:
            _apply(base, unit, content["vi"] if show_vi else content["en"])
            if show_vi and show_en:
                _apply(english, unit, content["en"])
        entries[part] = _bytes(base)
        slide_map.append(index)
        if not (show_vi and show_en) or all(content["vi"] == content["en"] for _, content in items):
            continue
        highest_id += 1
        _append_slide(part, english, index, entries, types, relations, slide_list, sid, highest_id)
        slide_map.append(index)
    entries["ppt/presentation.xml"] = _bytes(presentation)
    entries["ppt/_rels/presentation.xml.rels"] = _bytes(relations)
    entries["[Content_Types].xml"] = _bytes(types)
    if "docProps/app.xml" in entries:
        properties = _xml(entries["docProps/app.xml"])
        count = properties.find("{*}Slides")
        if count is not None:
            count.text = str(len(slide_map))
            entries["docProps/app.xml"] = _bytes(properties)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".pptx", delete=False) as pending:
        pending_path = Path(pending.name)
    try:
        with zipfile.ZipFile(pending_path, "w", zipfile.ZIP_DEFLATED) as output:
            for name, data in entries.items():
                output.writestr(name, data)
        pending_path.replace(target)
    finally:
        pending_path.unlink(missing_ok=True)
    return {"path": str(target), "slide_map": slide_map, "report": report}


def prepare_source_deck(lesson, directory, terms=()):
    """Keep generated presentations in the teacher's temporary data directory."""
    import hashlib

    from .powerpoint import verified_presentation

    verified_presentation(lesson, directory)

    signature = hashlib.sha256(json.dumps({"engine": "source-layout-v3", "lesson": lesson, "terms": terms}, sort_keys=True,
                                        ensure_ascii=False).encode("utf-8")).hexdigest()[:24]
    path = Path(directory) / "temp/bilingual-powerpoint" / (signature + ".pptx")
    manifest = path.with_suffix(".json")
    if path.is_file() and manifest.is_file():
        try:
            cached = json.loads(manifest.read_text(encoding="utf-8"))
            if (cached.get("sha256") == hashlib.sha256(path.read_bytes()).hexdigest()
                    and isinstance(cached.get("slide_map"), list)
                    and all(type(item) is int and item > 0 for item in cached["slide_map"])):
                return {"path": str(path), "slide_map": cached["slide_map"], "report": cached.get("report", [])}
        except (OSError, ValueError):
            pass
    result = export_source_deck(lesson, directory, path, terms)
    manifest.write_text(json.dumps({"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                   "slide_map": result["slide_map"], "report": result["report"]}), encoding="utf-8")
    return result
