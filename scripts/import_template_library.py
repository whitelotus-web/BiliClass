"""Import the supplied BiliClass design library without shipping lesson examples to AI.

Usage: project Python scripts/import_template_library.py path/to/library.zip
Native OOXML edits preserve the supplied themes, fonts and editable frames.
The original ZIP is never modified. Render the corrected mode demo with PowerPoint.
"""
import copy
import json
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/assets/templates"
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
STYLES = {"standard": "CLASSROOM", "visual": "VISUAL", "practice": "PRACTICE"}
ROLES = [("title", "Ten_bai"), ("concept", "Kien_thuc"), ("visual", "Hinh_chu_thich"), ("practice", "Luyen_tap")]
MODES = ["parallel_columns", "sentence_pairs", "integrated_keywords", "english_only"]
# Retain only the supplied structural frames, never the subject-specific diagram.
KEEP = {
    "standard": [set(range(2, 15)), set(range(2, 20)), set(range(2, 13)) | set(range(22, 27)), set(range(2, 18))],
    "visual": [set(range(2, 14)), set(range(2, 29)), set(range(2, 13)) | set(range(32, 41)), set(range(2, 18))],
    "practice": [set(range(2, 15)), set(range(2, 18)), set(range(2, 14)) | {30, 31, 32}, set(range(2, 19))],
}
TEXT = {
    "standard": [{13: "[SOURCE_SUBTITLE]"}, {15: "[SOURCE_CONTENT]", 16: "[SOURCE_EXPLANATION]", 18: "[SOURCE_KEY_IDEA]"},
                 {25: "[SOURCE_CAPTION]", 26: "[SOURCE_EXPLANATION]"}, {15: "[SOURCE_QUESTION]", 16: "[SOURCE_INSTRUCTIONS]"}],
    "visual": [{12: "[SOURCE_SUBTITLE]"}, {15: "[SOURCE_POINT_1]", 16: "[SOURCE_CAPTION_1]", 20: "[SOURCE_POINT_2]",
               21: "[SOURCE_CAPTION_2]", 25: "[SOURCE_POINT_3]", 26: "[SOURCE_CAPTION_3]", 28: "[SOURCE_SUMMARY]"},
               {34: "[SOURCE_CAPTION_1]", 37: "[SOURCE_CAPTION_2]", 40: "[SOURCE_CAPTION_3]"},
               {15: "[SOURCE_QUESTION]", 16: "[SOURCE_INSTRUCTIONS]"}],
    "practice": [{13: "[SOURCE_TASK]"}, {13: "[SOURCE_CONTENT]", 14: "[SOURCE_EXPLANATION]",
                 16: "[SOURCE_KEY_IDEA]", 17: "[SOURCE_CONDITIONS]"},
                 {31: "[SOURCE_CAPTION]", 32: "[SOURCE_EXPLANATION]"}, {15: "[SOURCE_QUESTION]",
                 16: "[SOURCE_INSTRUCTIONS]", 17: "[SOURCE_SOLUTION_IN_NOTES]"}],
}
IMAGE_FRAME = {"standard": [14, 19, 12, 17], "visual": [13, None, 12, 17], "practice": [14, None, 12, 18]}


def replace_text(shape, text):
    body = shape.find("p:txBody", NS)
    if body is None:
        return
    paragraphs = body.findall("a:p", NS)
    paragraph = copy.deepcopy(paragraphs[0]) if paragraphs else ET.Element("{" + NS["a"] + "}p")
    run = paragraph.find("a:r", NS)
    properties = copy.deepcopy(run.find("a:rPr", NS)) if run is not None and run.find("a:rPr", NS) is not None else None
    for item in list(paragraph):
        if item.tag != "{" + NS["a"] + "}pPr":
            paragraph.remove(item)
    if text:
        run = ET.SubElement(paragraph, "{" + NS["a"] + "}r")
        if properties is not None:
            # Long neutral markers must remain readable inside the original frame.
            if text.startswith("["):
                properties.set("sz", str(min(int(properties.get("sz", 2200)), 2200)))
            run.append(properties)
        ET.SubElement(run, "{" + NS["a"] + "}t").text = text
    for item in paragraphs:
        body.remove(item)
    body.append(paragraph)


def neutral_slide(raw, preset, number):
    root = ET.fromstring(raw)
    tree = root.find("p:cSld/p:spTree", NS)
    labels = {3: "BiliClass / [SUBJECT] / [GRADE]", 5: STYLES[preset],
              7: "DESIGN ONLY / Replace placeholders with the teacher's source", 8: str(number),
              9: ROLES[number - 1][0].upper(), 10: "[LESSON_TITLE]" if number == 1 else "[SOURCE_HEADING]",
              11: "[SOURCE_SUBTITLE]", **TEXT[preset][number - 1]}
    by_id = {}
    for shape in list(tree):
        if shape.tag in {"{" + NS["p"] + "}nvGrpSpPr", "{" + NS["p"] + "}grpSpPr"}:
            continue
        identity = shape.find(".//p:cNvPr", NS)
        if identity is None:
            continue
        key = int(identity.get("id"))
        if key not in KEEP[preset][number - 1]:
            tree.remove(shape)
            continue
        by_id[key] = shape
        identity.set("name", f"BiliClass frame {key}")
        identity.attrib.pop("descr", None)
        replace_text(shape, labels.get(key, ""))
    frame = IMAGE_FRAME[preset][number - 1]
    if frame in by_id:
        # Reuse the empty image region and an existing text style; no diagram/demo remains.
        shape = by_id[frame]
        body = shape.find("p:txBody", NS)
        reference = by_id[11].find("p:txBody", NS)
        if body is not None:
            shape.remove(body)
        shape.append(copy.deepcopy(reference))
        replace_text(shape, "[SOURCE_IMAGE]")
    for element in root.xpath("//p:timing | //p:transition", namespaces=NS):
        element.getparent().remove(element)
    return ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def import_library(path):
    preview = ASSETS / "reference-preview"
    preview.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "content_policy": "design_only", "templates": {}}
    with zipfile.ZipFile(path) as library:
        supplied = json.loads(library.read("BiliClass_ThuVienMau/ThongSo/biliclass_templates.json"))
        for preset, external in STYLES.items():
            item = supplied["templates"][external]
            raw = library.read("BiliClass_ThuVienMau/PowerPoint/BiliClass_" + external + ".pptx")
            target = ASSETS / (preset + "-classroom.pptx")
            with zipfile.ZipFile(__import__("io").BytesIO(raw)) as source, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as dest:
                for part in source.infolist():
                    if part.is_dir():
                        continue
                    data = source.read(part)
                    match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", part.filename)
                    if match:
                        data = neutral_slide(data, preset, int(match[1]))
                    elif part.filename.endswith(".xml") and ("notesSlides/notesSlide" in part.filename or "docProps/" in part.filename):
                        root = ET.fromstring(data)
                        for text in root.xpath("//*[local-name()='t' or local-name()='title' or local-name()='subject' or local-name()='description' or local-name()='creator' or local-name()='lastModifiedBy']"):
                            text.text = ""
                        data = ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                    dest.writestr(part.filename, data)
            layouts = []
            for number, (role, suffix) in enumerate(ROLES, 1):
                name = f"{preset}-{role}.png"
                (preview / name).write_bytes(library.read(f"BiliClass_ThuVienMau/Anh_Preview/{external}_{number:02}_{suffix}.png"))
                layouts.append({"id": role, "slide": number, "preview": "reference-preview/" + name})
            manifest["templates"][preset] = {"id": external, "pptx": target.name, "colors": item["colors"],
                "font": item["font"], "layouts": layouts,
                "language_previews": {mode: f"reference-preview/{preset}-{mode}.png" for mode in MODES}}
        # Correct demo subject labels before rendering language-mode previews.
        review = ROOT / ".runtime/template-review"
        review.mkdir(parents=True, exist_ok=True)
        raw = library.read("BiliClass_ThuVienMau/PowerPoint/BiliClass_4_Kieu_Ngon_Ngu.pptx")
        with zipfile.ZipFile(__import__("io").BytesIO(raw)) as source, zipfile.ZipFile(review / "language-demo-corrected.pptx", "w", zipfile.ZIP_DEFLATED) as dest:
            for part in source.infolist():
                data = source.read(part)
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", part.filename):
                    root = ET.fromstring(data)
                    for text in root.findall(".//a:t", NS):
                        if text.text and "BiliClass" in text.text:
                            text.text = text.text.replace("TOÁN", "VẬT LÍ").replace("KHOA HỌC", "VẬT LÍ").replace("MATHEMATICS", "PHYSICS").replace("SCIENCE", "PHYSICS")
                    data = ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                dest.writestr(part.filename, data)
    (ASSETS / "reference_library.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import_library(Path(sys.argv[1]))
