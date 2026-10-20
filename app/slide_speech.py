"""Speech grounded in native slide objects, with explicit uncertainty and visibility."""

import hashlib
import json
import math
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from lxml import etree

from .input_analysis import EN_WORDS, language_of

SCHEMA = 1
EXTRACTION_VERSION = 2
VI_MARKS = set("ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")
TERMS = set("velocity acceleration kinetic potential mechanical energy work power force momentum mass speed displacement amplitude frequency period equilibrium oscillation gravity gravitational spring elastic friction conservation joule watt definition conclusion evidence answer question activity exercise solution distance height horizontal vertical positive negative maximum minimum chapter lesson introduction summary objective objectives sequences arithmetic geometric progression cell photosynthesis noun verb water oxygen hydrogen carbon atom molecule electron proton neutron voltage current resistance derivative integral triangle rectangle square volume area history geography computer software hardware technology art music physical education language literature culture environment ecosystem temperature pressure density heat magnetic electric thermal chemical biology chemistry physics mathematics".split())
KINDS = {"title", "body", "caption", "question", "option", "keyword"}
LABEL_PREFIX = re.compile(r"^\s*(?:\d+|[IVX]+|[A-D])[.)/]\s+", re.I)


def neutral_fragment(text):
    return bool(text) and not re.search(r'[^\W\d_]', text, re.UNICODE)


# PowerPoint uses vertical tab for a normal soft line break (<a:br>).
TECHNICAL = re.compile(r"BILICLASS_NOTES|englishSpeechSegments|^\s*(?:CHECK|QUIZ|SPEECH)\s*:|https?://|\b19wx568\b|\b(?:CHAPTER|CHƯƠNG)\s+s\s*\d|\ufffd|[\x00-\x08\x0c\x0e-\x1f]", re.I)


@lru_cache(maxsize=32)
def _query(expression):
    return etree.XPath(expression, namespaces={"p": "http://schemas.openxmlformats.org/presentationml/2006/main"})


def xpath(node, expression):
    return _query(expression)(node)


def normalized(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def speech_problem(text):
    from .narration_text import clean_artifacts

    cleaned = clean_artifacts(text)
    if text.strip() and not cleaned.strip():
        return "technical_text"
    text = cleaned
    if TECHNICAL.search(text):
        return "technical_text"
    if re.search(r"(?<!\w)\d+[a-z]{2,}\d+(?!\w)", text, re.I):
        return "suspicious_code"
    if re.search(r"[A-ZĐ]\s+[b-df-hj-np-tv-z]\s+[A-ZĐ]", text):
        return "suspicious_character"
    if re.search(r"[=∫∑√^]|\\(?:frac|sqrt)|[α-ωΑ-Ω]", text):
        return "formula_needs_review"
    return ""


def english_text(text, *, tagged=False):
    """Language evidence, not all Latin characters and not narration from notes."""
    # A source identifier such as pendulum Đ can occur in otherwise ordinary
    # English, including untagged text returned by the web. Require actual
    # English evidence rather than treating every sentence containing Đ as VI.
    identifiers = re.sub(r'(?<!\w)Đ(?!\w)', 'D', text)
    if identifiers != text and (tagged or language_of(identifiers) == "en"):
        text = identifiers
    if any(c in VI_MARKS for c in text.casefold()):
        return False
    words = re.findall(r"[a-z]+", LABEL_PREFIX.sub("", text).casefold())
    if not words:
        return tagged and neutral_fragment(text)
    if language_of(text) == "vi":
        return False
    if tagged:
        return True
    return language_of(text) == "en" or bool(words) and all(w in TERMS | EN_WORDS for w in words)


def _transparent_run(node):
    return bool(etree.XPath('./a:rPr/a:solidFill/*/a:alpha[@val="0"]|./a:rPr/a:noFill',
                           namespaces={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'})(node))


def _visible_text(element, *, math=False):
    result = []
    for node in element.iter():
        name = etree.QName(node)
        if name.localname not in {'t','br'} or not math and name.namespace != 'http://schemas.openxmlformats.org/drawingml/2006/main':
            continue
        if any(etree.QName(parent).localname=='r' and _transparent_run(parent) for parent in node.iterancestors()):
            continue
        result.append('\v' if name.localname=='br' else node.text or '')
    return (' ' if math else '').join(result)


def objects(slide):
    """Keep group ancestry and stable native IDs, including table cells."""
    def compose(parent, local):
        a,b,c,d,e,f = parent
        g,h,i,j,k,offset_y = local
        return (a*g+c*h,b*g+d*h,a*i+c*j,b*i+d*j,a*k+c*offset_y+e,b*k+d*offset_y+f)

    def bounds(shape, transform):
        a,b,c,d,e,f = transform
        x,y,w,h = shape.left,shape.top,shape.width,shape.height
        angle = math.radians(shape.rotation)
        cosine,sine = math.cos(angle),math.sin(angle)
        points = []
        for px,py in ((x,y),(x+w,y),(x,y+h),(x+w,y+h)):
            rx,ry = px-x-w/2,py-y-h/2
            px,py = x+w/2+rx*cosine-ry*sine,y+h/2+rx*sine+ry*cosine
            points.append((a*px+c*py+e,b*px+d*py+f))
        left,top = min(p[0] for p in points),min(p[1] for p in points)
        return {'x':round(left),'y':round(top),
                'w':round(max(p[0] for p in points)-left),'h':round(max(p[1] for p in points)-top)}

    def group_transform(shape):
        nodes = shape._element.xpath('./p:grpSpPr/a:xfrm')
        if not nodes:
            return (1,0,0,1,0,0)
        node = nodes[0]
        children = {etree.QName(child).localname:child for child in node}
        offset,extent = children.get('chOff'),children.get('chExt')
        if offset is None or extent is None or not int(extent.get('cx','0')) or not int(extent.get('cy','0')):
            return (1,0,0,1,0,0)
        sx,sy = shape.width/int(extent.get('cx')),shape.height/int(extent.get('cy'))
        if node.get('flipH') in {'1','true'}:
            sx = -sx
        if node.get('flipV') in {'1','true'}:
            sy = -sy
        angle = math.radians(shape.rotation)
        cosine,sine = math.cos(angle),math.sin(angle)
        a,b,c,d = cosine*sx,sine*sx,-sine*sy,cosine*sy
        cx = int(offset.get('x'))+int(extent.get('cx'))/2
        cy = int(offset.get('y'))+int(extent.get('cy'))/2
        return (a,b,c,d,shape.left+shape.width/2-a*cx-c*cy,shape.top+shape.height/2-b*cx-d*cy)

    def walk(shapes, ancestors=(), inherited_hidden=False, transform=(1,0,0,1,0,0)):
        for shape in native_shapes(shapes):
            parents = (*ancestors, shape.shape_id)
            hidden = inherited_hidden or bool(shape._element.xpath('./*/p:cNvPr[@hidden="1" or @hidden="true"]'))
            if hasattr(shape, "shapes"):
                yield from walk(shape.shapes, parents, hidden, compose(transform,group_transform(shape)))
                continue
            base = {"shape_id": shape.shape_id, "ancestors": list(parents), "name": shape.name,
                    **bounds(shape, transform),
                    "shape": shape, "hidden": hidden}
            if shape.has_text_frame:
                if shape._element.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'):
                    formula_text = _visible_text(shape._element,math=True)
                    yield {**base, "paragraph": None, "cell": None, "text": formula_text, "runs": [], "source_type": "formula"}
                for index, paragraph in enumerate(shape.text_frame.paragraphs):
                    text = _visible_text(paragraph._p)
                    if text.strip():
                        yield {**base, "paragraph": index, "cell": None, "text": text,
                               "runs": [run for run in paragraph.runs if not _transparent_run(run._r)], "source_type": "shape"}
            elif shape.has_table:
                for row, cells in enumerate(shape.table.rows):
                    for column, cell in enumerate(cells.cells):
                        if cell.is_spanned:
                            continue
                        for index, paragraph in enumerate(cell.text_frame.paragraphs):
                            if paragraph.text.strip():
                                yield {**base, "paragraph": index, "cell": [row, column], "text": paragraph.text,
                                       "runs": list(paragraph.runs), "source_type": "table"}
            else:
                yield {**base, "paragraph": None, "cell": None, "text": "", "runs": [],
                       "source_type": "image" if shape.shape_type == 13 else "chart" if shape.has_chart else "object"}
    return list(walk(slide.shapes))


def native_shapes(shapes):
    """PowerPoint's modern math/text can live in mc:AlternateContent.

    python-pptx's regular iterator skips these shapes. Prefer Choice once;
    never also speak its fallback image/text copy.
    """
    def branches(element):
        if etree.QName(element).localname == "AlternateContent":
            choices = [n for n in element if etree.QName(n).localname == "Choice"]
            fallback = [n for n in element if etree.QName(n).localname == "Fallback"]
            selected = choices[:1] or fallback[:1]
            for selected_node in selected:
                for child in selected_node:
                    yield from branches(child)
        else:
            yield element
    for root in shapes._spTree:
        for element in branches(root):
            if etree.QName(element).localname in {"sp", "grpSp", "pic", "graphicFrame", "cxnSp"}:
                yield shapes._shape_factory(element)


def animation_rules(slide):
    """Resolve simple whole-object click/with-click entrance and exit.

    Paragraph builds, auto delays, triggers, motion and repeats remain uncertain.
    A click index does not prove an animation has finished: settle time is required.
    """
    rules = {node.get("spid"): {"kind": "unverified"}
             for node in slide._element.xpath(".//p:timing//p:spTgt")}
    clicks = 0
    unsafe = set()
    for sequence in slide._element.xpath('.//p:cTn[@nodeType="mainSeq"]'):
        for effect in xpath(sequence, './/p:cTn[@nodeType="clickEffect" or @nodeType="withEffect" or @nodeType="afterEffect"]'):
            if effect.get("nodeType") == "clickEffect":
                clicks += 1
            targets = xpath(effect, ".//p:spTgt")
            ids = {node.get("spid") for node in targets}
            delays = xpath(effect, './/p:cond[@delay != "0"]')
            duration = [float(n.get("dur")) / 1000 for n in xpath(effect, ".//p:cTn[@dur]")
                        if n.get("dur", "").isdigit()]
            if (clicks < 1 or effect.get("nodeType") not in {"clickEffect", "withEffect"} or not ids
                    or effect.get("presetClass") not in {"entr", "exit"} or delays
                    or any(xpath(node, "./p:txEl") for node in targets)
                    or xpath(effect, './/p:cTn[@repeatCount]')):
                unsafe.update(ids)
                continue
            # A bilingual conversion clones the original entrance behavior for
            # its translated textbox inside the SAME effect. Both targets have
            # the same click/visibility; multiple targets are not ambiguous.
            for shape_id in ids:
                previous = rules[shape_id]
                if effect.get("presetClass") == "entr" and previous["kind"] == "unverified":
                    rules[shape_id] = {"kind": "click", "show_after": clicks, "hide_after": None,
                                       "settle_seconds": max(duration or [0]) + .25}
                elif effect.get("presetClass") == "exit" and previous["kind"] == "click":
                    previous["hide_after"] = clicks
                else:
                    unsafe.add(shape_id)
    # Anything in an interactive sequence overrides main-sequence inference.
    for sequence in slide._element.xpath('.//p:cTn[@nodeType="interactiveSeq"]'):
        for target in xpath(sequence, ".//p:spTgt"):
            rules[target.get("spid")] = {"kind": "unverified"}
    for shape_id in unsafe:
        rules[shape_id] = {"kind": "unverified"}
    return rules


def _candidates(item, mode, metadata):
    text = item["text"]
    output = []
    tagged_shape = item["name"].startswith("BCL_EN")
    for line in text.splitlines():
        labelled = re.match(r"^\s*(?:EN|English)\s*[:：]\s*(.+)", line, re.I)
        if labelled and english_text(labelled[1], tagged=True):
            output.append(labelled[1].strip())
        elif english_text(line, tagged=tagged_shape):
            output.append(line.strip())
        elif "|" in line:
            output.extend(part.strip() for part in line.split("|") if english_text(part.strip()))
        elif mode == "integrated_keywords" or any(c in VI_MARKS for c in line.casefold()):
            output.extend(part for part in re.findall(r"\(([^()]+)\)", line) if english_text(part))
    # Language-tagged runs preserve embedded terms, but never trust a Vietnamese run tagged en.
    if not output and (mode == 'integrated_keywords' or not any(c in VI_MARKS for c in text.casefold())):
        tagged = []
        has_english = False
        mixed_vi = any(c in VI_MARKS for c in item["text"].casefold())
        for run in item["runs"]:
            props = run._r.find("{http://schemas.openxmlformats.org/drawingml/2006/main}rPr")
            if props is not None and props.get("lang", "").lower().startswith("en") and english_text(run.text, tagged=not mixed_vi):
                tagged.append(run.text)
                has_english = True
            elif not mixed_vi and neutral_fragment(run.text):
                # A separate number/punctuation run belongs to the same
                # English phrase, even when its font/language is inherited.
                tagged.append(run.text)
            elif tagged:
                if has_english:
                    output.append("".join(tagged).strip())
                tagged = []
                has_english = False
        if tagged and has_english:
            output.append("".join(tagged).strip())
    # AI may identify an inline term but must bind it to a real native substring.
    for segment in metadata:
        if (segment.get("shape_id") == item["shape_id"] and segment.get("paragraph", 0) == item["paragraph"]
                and segment.get("cell") == item["cell"]):
            value = segment.get("text", "")
            if (isinstance(value, str) and normalized(value) and normalized(value) in normalized(text)
                    and english_text(value, tagged=True) and value not in output):
                # Metadata covers a substring only; it never replaces the rest of an English paragraph.
                if not any(normalized(value) in normalized(existing) for existing in output):
                    output.append(value)
    return output


def _notes_metadata(notes):
    segments = []
    malformed = False
    for line in notes.splitlines():
        if re.match(r"^\s*SPEECH\s*:", line):
            try:
                value = json.loads(line.split(":", 1)[1])
                if value.get("version") != SCHEMA or not isinstance(value.get("segments"), list):
                    raise ValueError("Invalid speech schema")
                segments.extend(s for s in value["segments"] if isinstance(s, dict))
            except (ValueError, TypeError, AttributeError):
                malformed = True
    return segments[:1000], malformed


def inspect_slide(slide, number, mode="", notes_en="", bounds=None):
    from .picture_narration import image_text, without_image_suffix

    notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
    metadata, malformed = _notes_metadata(notes)
    items = objects(slide)
    captions = image_text(items, notes)
    notes_en = without_image_suffix(notes_en, captions, 'en')
    if bounds:
        animated = set(slide._element.xpath('.//p:spTgt/@spid'))
        width,height = bounds
        items = [item for item in items if animated.intersection(map(str,item['ancestors']))
                 or not (item['x']+item['w'] <= 0 or item['y']+item['h'] <= 0
                         or item['x'] >= width or item['y'] >= height)]
    animations = animation_rules(slide)
    shape_lengths={}
    for item in items:
        if item['source_type'] in {'shape','table'}:
            shape_lengths[item['shape_id']]=shape_lengths.get(item['shape_id'],0)+len(normalized(item['text']))
    segments, issues, seen = [], [], set()
    if malformed:
        issues.append("speech_metadata_invalid")
    for item in items:
        if (item['name'].startswith('BCL_DECORATION ') or item['name'] == 'BCL_EN image translation'
                or any(row['shape_id'] == item['shape_id'] and row.get('paragraph') == item['paragraph'] for row in captions)):
            continue  # Our page counter/branding is visible layout, not lecture speech.
        if item["source_type"] in {"image", "object", "chart", "formula"}:
            if item["source_type"] in {"image", "chart", "formula"} or item["shape"]._element.xpath('.//*[local-name()="m"]'):
                issues.append("image_or_formula_needs_review")
                source = {key: item[key] for key in ("shape_id", "paragraph", "cell", "source_type")}
                digest = hashlib.sha256(json.dumps([slide.slide_id, source, "review"], sort_keys=True).encode()).hexdigest()[:20]
                segments.append({"id": "en-"+digest, "slide_id": slide.slide_id, "slide": number,
                                 "english_text": "", "source": source, "kind": "caption", "order": 0,
                                 "status": "needs_review", "problem": "image_or_formula_needs_review",
                                 "visibility": {"kind": "unverified"}, "x": item["x"], "y": item["y"],
                                 "declared_order": None})
            continue
        values = _candidates(item, mode, metadata)
        if speech_problem(item["text"]):
            issues.append(speech_problem(item["text"]))
        if not values and item["text"].strip() and language_of(item["text"]) == "unknown":
            issues.append("language_needs_review")
        for offset, text in enumerate(values):
            key = (item["shape_id"], tuple(item["cell"] or ()), item["paragraph"], normalized(text))
            if key in seen:
                continue
            seen.add(key)
            kind = "option" if re.match(r"^[A-D][.)]\s", text) else "body"
            if re.match(r"^(?:Question|Exercise)\s*\d*\s*[:.)]", text, re.I):
                kind = "question"
            if (item["shape"].is_placeholder and item["shape"].placeholder_format.type in (1, 3)
                    and not item['name'].startswith('BCL_BODY ')
                    and shape_lengths.get(item['shape_id'],0)<=180
                    and (not bounds or item['h']<bounds[1]*.3)):
                kind = "title"
            if item["name"].startswith("BCL_EN_title"):
                kind = "title"
            declared_order = None
            for declaration in metadata:
                if (declaration.get("shape_id") == item["shape_id"]
                        and declaration.get("paragraph", 0) == item["paragraph"]
                        and declaration.get("cell") == item["cell"]
                        and normalized(str(declaration.get("text", ""))) == normalized(text)):
                    if declaration.get("kind") in KINDS and kind != "option":
                        kind = declaration["kind"]
                    if type(declaration.get("order")) is int and 0 <= declaration["order"] <= 1000:
                        declared_order = declaration["order"]
            source = {key: item[key] for key in ("shape_id", "paragraph", "cell", "source_type")}
            digest = hashlib.sha256(json.dumps([slide.slide_id, source, offset], sort_keys=True).encode()).hexdigest()[:20]
            visibility = {"kind": "always"}
            for ancestor in item["ancestors"]:
                if str(ancestor) in animations:
                    rule = animations[str(ancestor)]
                    visibility = rule if visibility["kind"] == "always" else {"kind": "unverified"}
            if item["hidden"]:
                visibility = {"kind": "hidden"}
            problem = speech_problem(text)
            segments.append({"id": "en-" + digest, "slide_id": slide.slide_id, "slide": number,
                             "english_text": text, "source": source, "kind": kind,
                             "status": "needs_review" if problem else "ready", "problem": problem,
                             "visibility": visibility, "x": item["x"], "y": item["y"], "order": 0,
                             "declared_order": declared_order})
    rank = {"title": 0, "body": 1, "caption": 2, "question": 3, "option": 4, "keyword": 1}
    segments.sort(key=lambda s: (rank[s["kind"]], s["english_text"][0] if s["kind"] == "option" else "",
                                 s["declared_order"] if s["declared_order"] is not None else s["y"],
                                 s["x"], s["source"]["paragraph"]))
    for index, segment in enumerate(segments):
        segment["order"] = index
    native_text = normalized(" ".join(s["english_text"] for s in segments))
    if notes_en and normalized(notes_en) != native_text:
        issues.append("notes_mismatch")
    vi_body = [i for i in items if len(i["text"]) > 120 and any(c in VI_MARKS for c in i["text"].casefold())]
    vi_body.extend(i for i in items if i["source_type"] == "formula" and any(c in VI_MARKS for c in i["text"].casefold()))
    if mode in {"parallel_columns", "sentence_pairs"} and vi_body and len(native_text) < 90:
        issues.append("english_body_missing")
    if any(s["english_text"] and s["visibility"]["kind"] == "unverified" for s in segments):
        issues.append("animation_needs_review")
    for declaration in metadata:
        if not any(s["source"]["shape_id"] == declaration.get("shape_id")
                   and normalized(s["english_text"]) == normalized(str(declaration.get("text", ""))) for s in segments):
            issues.append("speech_metadata_mismatch")
    return {"slide": number, "slide_id": slide.slide_id, "englishSpeechSegments": segments,
            "issues": sorted(set(issues)), "speech_status": "CHECK" if issues else "PASS",
            **({'imageText': captions} if captions else {})}


def deck_speech(path, deck, mode="", pairs=()):
    return {"schema_version": SCHEMA, "extraction_version": EXTRACTION_VERSION,
            "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            "slides": [inspect_slide(slide, i, mode, pairs[i - 1].get("en", "") if i <= len(pairs) else "",
                                     bounds=(deck.slide_width,deck.slide_height))
                       for i, slide in enumerate(deck.slides, 1)]}


def visible_segments(slide, click_index=None, settled_seconds=0):
    result = []
    for segment in slide.get("englishSpeechSegments", []):
        rule = segment["visibility"]
        if segment["status"] != "ready":
            continue
        if rule["kind"] == "always":
            result.append(segment)
        elif (rule["kind"] == "click" and type(click_index) is int
              and click_index >= rule["show_after"]
              and (rule["hide_after"] is None or click_index < rule["hide_after"])
              and settled_seconds >= rule["settle_seconds"]):
            result.append(segment)
    return result


def speech_chunks(text, limit=1500):
    """Keep paragraph breaks audible; split oversized paragraphs at sentences."""
    from .narration_text import clean_artifacts

    text = clean_artifacts(text)
    text = text.replace('\u00a0', ' ').replace('\u202f', ' ')
    paragraphs = [part.strip() for part in re.split(r'[\r\n\v]+', text) if part.strip()]
    if len(paragraphs) > 1:
        return [chunk for paragraph in paragraphs for chunk in speech_chunks(paragraph, limit)]
    chunks, current = [], ""
    for sentence in re.split(r"(?<=[.!?;])\s+|\n+", text.strip()):
        if len(sentence) > limit:
            words = sentence.split()
        else:
            words = [sentence]
        for word in words:
            if len(word) > limit:
                raise ValueError("Một cụm đọc quá dài; kiểm tra lại nội dung slide.")
            if current and len(current) + len(word) + 1 > limit:
                chunks.append(current)
                current = ""
            current = (current + " " + word).strip()
    if current:
        chunks.append(current)
    return chunks
