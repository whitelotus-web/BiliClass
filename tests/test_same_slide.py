"""Same-slide delivery, visible coverage and native build synchronization."""

import hashlib
import zipfile

import pytest
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt

from app.chatgpt_handoff import inspect_returned_deck
from app.native_bilingual import assemble, extract
from app.source_deck import NS, source_slide_parts


def fixture(path, *, animated=False):
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    title = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12), Inches(1))
    title.text = "Cơ năng"
    body = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(7), Inches(4))
    body.text = (
        "Năng lượng của vật được bảo toàn khi không có lực ma sát.\nVận tốc của vật tăng khi thế năng giảm."
    )
    for shape in (title, body):
        for p in shape.text_frame.paragraphs:
            p.font.name = "Arial"
            p.font.size = Pt(28)
    picture = path.with_suffix(".png")
    Image.new("RGB", (200, 200), "#46A3CF").save(picture)
    slide.shapes.add_picture(str(picture), Inches(8), Inches(2), width=Inches(4))
    if animated:
        timing = etree.SubElement(slide._element, f"{{{NS['p']}}}timing")
        sequence = etree.SubElement(timing, f"{{{NS['p']}}}tnLst")
        parent = etree.SubElement(sequence, f"{{{NS['p']}}}par")
        clock = etree.SubElement(parent, f"{{{NS['p']}}}cTn", id="1", nodeType="clickEffect")
        children = etree.SubElement(clock, f"{{{NS['p']}}}childTnLst")
        behavior = etree.SubElement(children, f"{{{NS['p']}}}animEffect", transition="in", filter="fade")
        common = etree.SubElement(behavior, f"{{{NS['p']}}}cBhvr")
        etree.SubElement(common, f"{{{NS['p']}}}cTn", id="2", dur="500")
        target = etree.SubElement(
            etree.SubElement(common, f"{{{NS['p']}}}tgtEl"), f"{{{NS['p']}}}spTgt", spid=str(body.shape_id)
        )
        text = etree.SubElement(target, f"{{{NS['p']}}}txEl")
        etree.SubElement(text, f"{{{NS['p']}}}pRg", st="1", end="1")
        builds = etree.SubElement(timing, f"{{{NS['p']}}}bldLst")
        etree.SubElement(builds, f"{{{NS['p']}}}bldP", spid=str(body.shape_id), grpId="0")
    deck.save(path)
    return path


def translations(manifest):
    values = [
        "Mechanical energy",
        "The energy of the object is conserved in the absence of friction.",
        "The velocity increases when the potential energy decreases.",
    ]
    return {unit["id"]: {"en": values[i]} for i, unit in enumerate(manifest["units"])}


@pytest.mark.parametrize("mode", ["parallel_columns", "sentence_pairs"])
def test_both_languages_visible_on_each_source_page_and_resources_preserved(tmp_path, mode):
    source = fixture(tmp_path / "original.pptx")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = extract(source, mode, same_slide=True)
    assert manifest["version"] == 4 and not manifest["paired_slides"]
    output = assemble(source, tmp_path / "output.pptx", manifest, translations(manifest), mode)
    deck = Presentation(output)
    assert len(deck.slides) == 1
    text = "\n".join(s.text for s in deck.slides[0].shapes if s.has_text_frame)
    assert "Năng lượng" in text and "The energy" in text and "The velocity" in text
    assert deck.slides[0].shapes[0].text == "Cơ năng\nMechanical energy"
    assert len(manifest["layout_plan"][0]["pairs"]) == 3
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    with zipfile.ZipFile(source) as before, zipfile.ZipFile(output) as after:
        for name in before.namelist():
            if name.startswith(("ppt/media/", "ppt/theme/", "ppt/slideLayouts/", "ppt/slideMasters/")):
                assert before.read(name) == after.read(name)
    report = inspect_returned_deck(output, source, mode, layout_plan=manifest["layout_plan"])
    assert not any(
        i["code"] in {"translation_pair_missing", "english_body_missing", "parallel_columns_missing"}
        for row in report["slide_quality"]["slides"]
        for i in row["issues"]
    )
    paragraph = deck.slides[0].shapes[0].text_frame.paragraphs[1]
    assert paragraph.runs[0].font.italic
    assert paragraph.runs[0].font.name == "Arial"
    vi = deck.slides[0].shapes[0].text_frame.paragraphs[0]
    assert paragraph.runs[0].font.size < (vi.runs[0].font.size or vi.font.size)


def test_notes_and_declared_pairs_cannot_hide_deleted_english(tmp_path):
    source = fixture(tmp_path / "source.pptx")
    manifest = extract(source, "parallel_columns", same_slide=True)
    output = assemble(source, tmp_path / "output.pptx", manifest, translations(manifest), "parallel_columns")
    deck = Presentation(output)
    pair = manifest["layout_plan"][0]["pairs"][1]
    next(s for s in deck.slides[0].shapes if s.shape_id == pair["en_shape"]).text = ""
    deck.save(output)
    report = inspect_returned_deck(output, source, "parallel_columns", layout_plan=manifest["layout_plan"])
    assert any(
        i["code"] == "translation_pair_missing" and i["severity"] == "FAIL"
        for row in report["slide_quality"]["slides"]
        for i in row["issues"]
    )


def test_transparent_english_is_not_visible_coverage(tmp_path):
    from app.same_slide import visible_pairs

    source = fixture(tmp_path / "source.pptx")
    manifest = extract(source, "parallel_columns", same_slide=True)
    output = assemble(source, tmp_path / "result.pptx", manifest, translations(manifest), "parallel_columns")
    with zipfile.ZipFile(output) as archive:
        tree = etree.fromstring(archive.read(source_slide_parts(output)[0]))
    pairs = manifest["layout_plan"][0]["pairs"]
    pair = pairs[1]
    node = tree.xpath(".//p:sp[p:nvSpPr/p:cNvPr[@id=$id]]", namespaces=NS, id=str(pair["en_shape"]))[0]
    for props in node.findall(".//a:rPr", NS):
        fill = etree.SubElement(props, f"{{{NS['a']}}}solidFill")
        color = etree.SubElement(fill, f"{{{NS['a']}}}srgbClr", val="000000")
        etree.SubElement(color, f"{{{NS['a']}}}alpha", val="0")
    assert not visible_pairs(tree, pairs)


def test_numeric_options_remain_single_native_objects(tmp_path):
    source = fixture(tmp_path / "source.pptx")
    deck = Presentation(source)
    option = deck.slides[0].shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(2), Inches(0.5))
    option.text = "A. 2,5 m/s²"
    deck.save(source)
    manifest = extract(source, "parallel_columns", same_slide=True)
    unit = next(u for u in manifest["units"] if u["shape_id"] == option.shape_id)
    assert unit["language"] == "neutral"
    values = {u["id"]: {"en": "Mechanical energy" if u["title"] else u["text"]} for u in manifest["units"]}
    output = assemble(source, tmp_path / "result.pptx", manifest, values, "parallel_columns")
    assert (
        sum(s.text.count("A. 2,5 m/s²") for s in Presentation(output).slides[0].shapes if s.has_text_frame)
        == 1
    )


def test_formula_variable_and_protected_xml_are_language_neutral(tmp_path):
    source = fixture(tmp_path / "source.pptx")
    deck = Presentation(source)
    paragraph = deck.slides[0].shapes[1].text_frame.add_paragraph()
    paragraph.add_run().text = "a"
    math = "http://schemas.openxmlformats.org/officeDocument/2006/math"
    formula = etree.SubElement(paragraph._p, f"{{{math}}}oMath")
    run = etree.SubElement(formula, f"{{{math}}}r")
    etree.SubElement(run, f"{{{math}}}t").text = "=±ω²A"
    deck.save(source)
    manifest = extract(source, "sentence_pairs", same_slide=True)
    unit = next(u for u in manifest["units"] if u["paragraph"] == 2)
    assert unit["text"] == "a⟦BLC0⟧" and unit["language"] == "neutral"


@pytest.mark.parametrize("mode", ["parallel_columns", "sentence_pairs"])
def test_answer_english_shares_source_click_and_paragraph_build(tmp_path, mode):
    source = fixture(tmp_path / "source.pptx", animated=True)
    manifest = extract(source, mode, same_slide=True)
    output = assemble(source, tmp_path / "output.pptx", manifest, translations(manifest), mode)
    with zipfile.ZipFile(output) as archive:
        tree = etree.fromstring(archive.read(source_slide_parts(output)[0]))
    timing = tree.find("p:timing", NS)
    ids = timing.xpath(".//p:cTn/@id", namespaces=NS)
    assert len(set(ids)) == len(ids)
    pair = manifest["layout_plan"][0]["pairs"][2]
    targets = timing.findall(".//p:spTgt", NS)
    if mode == "parallel_columns":
        assert {int(n.get("spid")) for n in targets} == {pair["vi_shape"], pair["en_shape"]}
        effects = timing.findall(".//p:animEffect", NS)
        assert len(effects) == 2 and effects[0].getparent() is effects[1].getparent()
        assert len(timing.findall(".//p:bldP", NS)) == 2
    else:
        region = targets[0].find("p:txEl/p:pRg", NS)
        assert region.attrib == {"st": "2", "end": "3"}


def test_long_math_or_single_body_is_not_misclassified_as_title(tmp_path):
    source = fixture(tmp_path / "source.pptx")
    deck = Presentation(source)
    body = deck.slides[0].shapes[1]
    body.top = Inches(0.1)
    body.text = "Nhập hàm số và kiểm tra vận tốc của vật. " * 12
    body.text_frame.paragraphs[0].font.size = Pt(32)
    deck.save(source)
    manifest = extract(source, "parallel_columns", same_slide=True)
    assert not next(u for u in manifest["units"] if u["shape_id"] == body.shape_id)["title"]


def test_table_cells_keep_both_languages(tmp_path):
    source = fixture(tmp_path / "source.pptx")
    deck = Presentation(source)
    table = deck.slides[0].shapes.add_table(1, 1, Inches(0.5), Inches(6.4), Inches(10), Inches(0.7)).table
    table.cell(0, 0).text = "Năng lượng được bảo toàn."
    deck.save(source)
    manifest = extract(source, "parallel_columns", same_slide=True)
    values = {u["id"]: {"en": "The energy is conserved."} for u in manifest["units"]}
    output = assemble(source, tmp_path / "result.pptx", manifest, values, "parallel_columns")
    cell = next(s.table.cell(0, 0) for s in Presentation(output).slides[0].shapes if s.has_table)
    assert cell.text == "Năng lượng được bảo toàn.\nThe energy is conserved."


@pytest.mark.parametrize("mode", ["parallel_columns", "sentence_pairs"])
def test_dense_frames_continue_with_whole_bilingual_pairs(tmp_path, mode):
    source = fixture(tmp_path / "source.pptx", animated=True)
    deck = Presentation(source)
    body = deck.slides[0].shapes[1]
    body.height = Inches(1.4)
    body.text = "\n".join("Năng lượng của vật được bảo toàn khi không có lực ma sát." for _ in range(8))
    for p in body.text_frame.paragraphs:
        p.font.size = Pt(26)
    deck.save(source)
    manifest = extract(source, mode, same_slide=True)
    values = {
        u["id"]: {
            "en": "Mechanical energy"
            if u["title"]
            else "The energy of the object is conserved in the absence of friction."
        }
        for u in manifest["units"]
    }
    output = assemble(source, tmp_path / "result.pptx", manifest, values, mode)
    plan = manifest["layout_plan"]
    assert len(plan) > 1
    assert all(row["role"] == "bilingual" and row["source_slide"] == 1 for row in plan)
    assert [row["continuation"] for row in plan[1:]] == list(range(2, len(plan) + 1))
    body_units = [p["unit"] for row in plan for p in row["pairs"] if not p["title"]]
    assert len(body_units) == 8 and len(set(body_units)) == 8
    for slide in Presentation(output).slides:
        text = "\n".join(s.text for s in slide.shapes if s.has_text_frame)
        assert "Năng lượng" in text and "The energy" in text
    report = inspect_returned_deck(output, source, mode, layout_plan=plan)
    assert not any(
        i["code"] in {"translation_pair_missing", "slide_count"}
        for row in report["slide_quality"]["slides"]
        for i in row["issues"]
    )
