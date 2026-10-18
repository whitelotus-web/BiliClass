"""Embed existing, verified narration without asking a model or rewriting artwork."""

import hashlib
import io
import wave
import zipfile
from pathlib import Path

from lxml import etree

from .layout_regions import empty_region
from .lesson_narration import MODES, audio_status, valid_key
from .narration_script import segments as narration_segments
from .paths import RESOURCE_ROOT
from .powerpoint import slide_for_locator
from .source_deck import NS, _bytes, _rels_path, _xml, source_slide_parts


def slide_audio(lesson, directory, *, scope='full_slide'):
    from . import speech
    from .slide_speech import speech_chunks

    if scope not in {'full_slide', 'visible'}:
        raise ValueError('Chọn phạm vi lời đọc hợp lệ.')
    status = audio_status(lesson, directory)
    if not status["ready"]:
        raise ValueError("Tạo đủ giọng đọc đã chọn trước khi tải PowerPoint kèm giọng.")
    record = lesson["narration"]
    pages = {}
    for page in lesson.get("slide_speech", {}).get("slides", []):
        segments = page["englishSpeechSegments"]
        safe = [
            s for s in segments if s["status"] == "ready" and (
                scope == 'full_slide' or s.get("visibility", {}).get("kind") == "always")
        ]
        languages = {}
        if "en" in MODES[record["mode"]]:
            languages["en"] = [part for s in safe for part in speech_chunks(s["english_text"])]
        # The explicit whole-slide button reads the saved script on demand.
        # The optional build-aware route excludes words hidden behind clicks.
        if "vi" in MODES[record["mode"]] and (scope == 'full_slide' or not any(
            s.get("visibility", {}).get("kind") != "always" for s in segments if s["english_text"]
        )):
            languages["vi"] = [
                part
                for unit in narration_segments(lesson)
                if slide_for_locator(unit.get("locator", "")) == page["slide"]
                for part in speech_chunks(unit["vi"])
            ]
        for language, texts in languages.items():
            keys = [speech.audio_key(text, record["voice"], record["rate"]) for text in texts]
            if not keys:
                continue
            if any(key not in record["keys"][language] or not valid_key(directory, key) for key in keys):
                raise ValueError("Giọng đọc không khớp bài đang xem. Tạo lại giọng trước khi tải.")
            pages.setdefault(page["slide"], {})[language] = keys
        if record.get('playback') == 'both_controls' and set(pages.get(page['slide'], {})) == {'vi', 'en'}:
            pages[page['slide']]['both'] = paired_keys(lesson, page['slide'], pages[page['slide']], record)
    if not pages:
        raise ValueError(
            "Chưa có lời đọc tĩnh phù hợp để nhúng; phần theo hiệu ứng vẫn dùng trong BiliClass."
        )
    return pages


def paired_keys(lesson, number, languages, record):
    """Pair verified unit chunks, then retain any remaining visible text."""
    from . import speech
    from .slide_speech import speech_chunks

    allowed = {lang: set(keys) for lang, keys in languages.items()}
    used = {'vi': set(), 'en': set()}
    result = []
    for unit in narration_segments(lesson):
        if slide_for_locator(unit.get('locator', '')) != number:
            continue
        pair = {lang: [speech.audio_key(text, record['voice'], record['rate']) for text in speech_chunks(unit[lang])]
                for lang in ('vi', 'en')}
        if all(pair[lang] and set(pair[lang]) <= allowed[lang] for lang in ('vi', 'en')):
            for lang in ('vi', 'en'):
                result.extend(pair[lang])
                used[lang].update(pair[lang])
    for lang in ('vi', 'en'):
        result.extend(key for key in languages[lang] if key not in used[lang])
    return result


def static_vietnamese(slide, lesson, number):
    from .slide_speech import animation_rules, normalized, objects

    rules = animation_rules(slide)
    visible = normalized(' '.join(item['text'] for item in objects(slide)
                        if not item['hidden'] and not any(str(parent) in rules for parent in item['ancestors'])))
    texts = [normalized(unit['vi']) for unit in narration_segments(lesson)
             if slide_for_locator(unit.get('locator', '')) == number and unit['vi'].strip()]
    return bool(texts) and all(text in visible for text in texts)


def joined_wav(directory, keys):
    buffer = io.BytesIO()
    parameters = None
    total = 0
    with wave.open(buffer, "wb") as output:
        for key in keys:
            with wave.open(str(Path(directory) / "audio" / (key + ".wav")), "rb") as source:
                current = (source.getnchannels(), source.getsampwidth(), source.getframerate())
                if parameters is None:
                    parameters = current
                    output.setparams((*parameters, 0, "NONE", "not compressed"))
                if current != parameters or source.getcomptype() != "NONE":
                    raise ValueError("Các đoạn voice khác định dạng. Tạo lại giọng đọc của bài.")
                output.writeframes(source.readframes(source.getnframes()))
                silence = int(current[2] * 0.18)
                output.writeframes(b"\x00" * (silence * current[0] * current[1]))
                total += source.getnframes() + silence
    return buffer.getvalue(), round(total / parameters[2] * 1000)


def control_slots(languages, bounds, occupied, clear):
    """Try rows, columns and separate safe gaps before rejecting a crowded page."""
    languages = list(languages)
    for cell_w, cell_h, columns in ((62, 42, len(languages)), (62, 42, 1), (40, 48, len(languages))):
        width = cell_w * columns
        height = cell_h * ((len(languages) + columns - 1) // columns)
        slot = empty_region((bounds[0] - width - 12, bounds[1] - height - 12, width, height),
                            (width, height), bounds, occupied, clear=clear)
        if slot is not None:
            return {lang: (slot[0] + index % columns * cell_w,
                           slot[1] + index // columns * cell_h, cell_w == 40)
                    for index, lang in enumerate(languages)}
    for width, height in ((62, 42), (40, 48)):
        used, result = list(occupied), {}
        for lang in languages:
            slot = empty_region((bounds[0] - width - 12, bounds[1] - height - 12, width, height),
                                (width, height), bounds, used, clear=clear)
            if slot is None:
                break
            used.append(slot)
            result[lang] = slot[0], slot[1], width == 40
        if len(result) == len(languages):
            return result
    # A narrow header/margin can still hold labelled native audio controls.
    # Keep the same collision rules; do not shrink or cover the source content.
    used, result = list(occupied), {}
    for lang in languages:
        slot = empty_region((bounds[0] - 52, 6, 40, 20), (40, 20), bounds, used, clear=clear)
        if slot is None:
            break
        used.append(slot)
        result[lang] = slot[0], slot[1], 'mini'
    if len(result) == len(languages):
        return result
    return None


def coverage_message(report):
    message = f"Đã nhúng {report.get('speakers', 0)} nút loa trên {report.get('slides', 0)} slide. Bấm F5 rồi bấm loa để nghe."
    if report.get('unplaced_pages'):
        pages = ', '.join(str(n) for n in report['unplaced_pages'])
        message += f' Slide {pages} không đủ chỗ đặt loa; nghe giọng đã lưu bằng Mascot trong BiliClass.'
    if report.get('restricted_pages'):
        message += ' Phần lời phụ thuộc hiệu ứng hoặc chưa xác định khả năng hiển thị chỉ phát trong BiliClass.'
    if report.get('missing_pages'):
        message += f" {len(report['missing_pages'])} slide chưa có lời đọc cho ngôn ngữ đã chọn."
    if report.get('scope') == 'full_slide':
        message += ' Loa đọc toàn bộ lời đã lưu của slide, kể cả phần xuất hiện sau; không tự phát theo hiệu ứng.'
    return message


def _node(parent, prefix, tag, **attributes):
    return etree.SubElement(parent, f"{{{NS[prefix]}}}{tag}", **{k: str(v) for k, v in attributes.items()})


def media_shape(identity, language, box, audio_relation, media_relation, icon_relation):
    picture = etree.Element(f"{{{NS['p']}}}pic")
    nonvisual = _node(picture, "p", "nvPicPr")
    props = _node(
        nonvisual,
        "p",
        "cNvPr",
        id=identity,
        name="BiliClass audio " + language.upper(),
        descr="Play " + language.upper(),
        hidden="0",
    )
    link = _node(props, "a", "hlinkClick", action="ppaction://media",
                 tooltip="Bấm để đọc toàn bộ lời đã lưu của slide · " + language.upper())
    link.set(f"{{{NS['r']}}}id", "")
    _node(_node(nonvisual, "p", "cNvPicPr"), "a", "picLocks", noChangeAspect="1")
    application = _node(nonvisual, "p", "nvPr")
    audio = _node(application, "a", "audioFile")
    audio.set(f"{{{NS['r']}}}link", audio_relation)
    extension = _node(
        _node(application, "p", "extLst"), "p", "ext", uri="{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}"
    )
    media = etree.SubElement(
        extension,
        "{http://schemas.microsoft.com/office/powerpoint/2010/main}media",
        nsmap={"p14": "http://schemas.microsoft.com/office/powerpoint/2010/main"},
    )
    media.set(f"{{{NS['r']}}}embed", media_relation)
    fill = _node(picture, "p", "blipFill")
    _node(fill, "a", "blip").set(f"{{{NS['r']}}}embed", icon_relation)
    _node(_node(fill, "a", "stretch"), "a", "fillRect")
    geometry = _node(picture, "p", "spPr")
    transform = _node(geometry, "a", "xfrm")
    _node(transform, "a", "off", x=round(box[0] * 12700), y=round(box[1] * 12700))
    _node(transform, "a", "ext", cx=round(box[2] * 12700), cy=round(box[3] * 12700))
    _node(_node(geometry, "a", "prstGeom", prst="rect"), "a", "avLst")
    return picture


def add_playback(tree, identity, duration):
    timing = tree.find("p:timing", NS)
    if timing is None:
        timing = etree.Element(f"{{{NS['p']}}}timing")
        following = tree.find("p:extLst", NS)
        if following is None:
            tree.append(timing)
        else:
            following.addprevious(timing)
    clocks = [int(v) for v in timing.xpath(".//p:cTn/@id", namespaces=NS)]
    next_id = max(clocks + [0])

    def clock(parent, **attributes):
        nonlocal next_id
        next_id += 1
        return _node(parent, "p", "cTn", id=next_id, **attributes)

    root = timing.find('p:tnLst/p:par/p:cTn[@nodeType="tmRoot"]', NS)
    if root is None:
        nodes = timing.find("p:tnLst", NS)
        if nodes is None:
            nodes = etree.Element(f"{{{NS['p']}}}tnLst")
            timing.insert(0, nodes)
        root = clock(_node(nodes, "p", "par"), dur="indefinite", restart="never", nodeType="tmRoot")
    children = root.find("p:childTnLst", NS)
    if children is None:
        children = _node(root, "p", "childTnLst")
    sequence = _node(children, "p", "seq", concurrent="1", nextAc="seek")
    sequence_clock = clock(
        sequence, restart="whenNotActive", fill="hold", evtFilter="cancelBubble", nodeType="interactiveSeq"
    )
    condition = _node(_node(sequence_clock, "p", "stCondLst"), "p", "cond", evt="onClick", delay="0")
    _node(_node(condition, "p", "tgtEl"), "p", "spTgt", spid=identity)
    _node(_node(sequence_clock, "p", "endSync", evt="end", delay="0"), "p", "rtn", val="all")
    container = _node(sequence_clock, "p", "childTnLst")
    for attributes in (
        {"fill": "hold"},
        {"fill": "hold"},
        {
            "presetID": "1",
            "presetClass": "mediacall",
            "presetSubtype": "0",
            "fill": "hold",
            "nodeType": "clickEffect",
        },
    ):
        parent = clock(_node(container, "p", "par"), **attributes)
        _node(_node(parent, "p", "stCondLst"), "p", "cond", delay="0")
        container = _node(parent, "p", "childTnLst")
    command = _node(container, "p", "cmd", type="call", cmd="playFrom(0.0)")
    behavior = _node(command, "p", "cBhvr")
    clock(behavior, dur=duration, fill="hold")
    _node(_node(behavior, "p", "tgtEl"), "p", "spTgt", spid=identity)
    condition = _node(_node(sequence, "p", "nextCondLst"), "p", "cond", evt="onClick", delay="0")
    _node(_node(condition, "p", "tgtEl"), "p", "spTgt", spid=identity)
    media = _node(_node(children, "p", "audio"), "p", "cMediaNode", vol="80000")
    media_clock = clock(media, fill="hold", display="0")
    _node(_node(media_clock, "p", "stCondLst"), "p", "cond", delay="indefinite")
    condition = _node(_node(media_clock, "p", "endCondLst"), "p", "cond", evt="onStopAudio", delay="0")
    _node(_node(condition, "p", "tgtEl"), "p", "sldTgt")
    _node(_node(media, "p", "tgtEl"), "p", "spTgt", spid=identity)


def embed_audio(source, destination, lesson, directory, *, scope='full_slide'):
    from PIL import Image
    from pptx import Presentation

    from .picture_translation import background, text_shape
    from .slide_speech import objects

    pages = slide_audio(lesson, directory, scope=scope)
    deck = Presentation(source)
    parts = source_slide_parts(source)
    with zipfile.ZipFile(source) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    original_parts = set(entries)
    types = _xml(entries["[Content_Types].xml"])
    for extension, kind in [("wav", "audio/wav"), ("png", "image/png")]:
        if not any(n.get("Extension") == extension for n in types):
            etree.SubElement(types, f"{{{NS['ct']}}}Default", Extension=extension, ContentType=kind)
    icon = (RESOURCE_ROOT / "assets/navigation/voice-active.png").read_bytes()
    icon_name = "ppt/media/biliclass-" + hashlib.sha256(icon).hexdigest() + ".png"
    entries[icon_name] = icon
    count, embedded_pages, unplaced_pages = 0, [], []
    missing_pages = sorted(set(range(1, len(parts) + 1)) - set(pages))
    restricted_pages = list(missing_pages) if scope == 'visible' else []
    for number, languages in pages.items():
        if not 1 <= number <= len(parts):
            raise ValueError("Số trang giọng đọc không khớp PowerPoint.")
        part = parts[number - 1]
        tree = _xml(entries[part])
        if scope == 'visible' and tree.find("p:timing", NS) is not None and not static_vietnamese(deck.slides[number - 1], lesson, number):
            languages = {lang: keys for lang, keys in languages.items() if lang not in {"vi", "both"}}
        if not languages:
            restricted_pages.append(number)
            continue  # Vietnamese notes may include answers hidden in native builds.
        if set(languages) != set(pages[number]) or set(languages) - {'both'} != set(MODES[lesson['narration']['mode']]):
            restricted_pages.append(number)
        shape_tree = tree.find("p:cSld/p:spTree", NS)
        relationships = _xml(entries[_rels_path(part)])

        def relation(kind, target):
            identity = "rIdBiliClass" + str(len(relationships) + 1)
            while any(r.get("Id") == identity for r in relationships):
                identity += "x"
            etree.SubElement(
                relationships, f"{{{NS['rel']}}}Relationship", Id=identity, Type=kind, Target=target
            )
            return identity

        occupied = []
        backdrops = []
        for item in objects(deck.slides[number - 1]):
            box = tuple(item[k] / 12700 for k in ("x", "y", "w", "h"))
            if not item["hidden"] and (item['source_type'] != 'image' or
                    box[2] * box[3] < deck.slide_width * deck.slide_height / 12700**2 * 0.6):
                occupied.append(box)
            elif item["source_type"] == "image" and not item["hidden"]:
                try:
                    image = Image.open(io.BytesIO(item["shape"].image.blob)).convert("RGB")
                    backdrops.append((image, box))
                except (OSError, ValueError):
                    occupied.append(box)
        slots = control_slots(languages, (deck.slide_width / 12700, deck.slide_height / 12700), occupied,
                              lambda candidate: all(background(image, box, candidate) for image, box in backdrops))
        for image, _ in backdrops:
            image.close()
        if slots is None:
            unplaced_pages.append(number)
            continue
        embedded_pages.append(number)
        identity = max(int(v) for v in tree.xpath(".//p:cNvPr/@id", namespaces=NS))
        for language, keys in languages.items():
            audio, duration = joined_wav(directory, keys)
            audio_name = "ppt/media/biliclass-" + hashlib.sha256(audio).hexdigest() + ".wav"
            entries[audio_name] = audio
            audio_id = relation(NS["r"] + "/audio", "../media/" + Path(audio_name).name)
            media_id = relation(
                "http://schemas.microsoft.com/office/2007/relationships/media",
                "../media/" + Path(audio_name).name,
            )
            icon_id = relation(NS["r"] + "/image", "../media/" + Path(icon_name).name)
            identity += 1
            left, top, compact = slots[language]
            mini = compact == 'mini'
            box = (left + (6 if compact is True else 0), top, 20 if mini else 28, 20 if mini else 28)
            shape_tree.append(media_shape(identity, language, box, audio_id, media_id, icon_id))
            add_playback(tree, identity, duration)
            identity += 1
            label = text_shape(
                identity,
                {'vi': 'VI', 'en': 'EN', 'both': 'VI+EN'}[language],
                (left + 20, top, 20, 20) if mini else (left, top + 29, 40, 16) if compact else (box[0] + 29, box[1] + 5, 33, 24),
                8 if mini else 9 if language == 'both' else 12,
                english=False,
            )
            label.find("p:nvSpPr/p:cNvPr", NS).set("name", "BCL_DECORATION audio label")
            shape_tree.append(label)
            count += 1
        entries[part] = _bytes(tree)
        entries[_rels_path(part)] = _bytes(relationships)
    if not count:
        raise ValueError(
            "Không đủ chỗ đặt loa hoặc lời đọc phụ thuộc hiệu ứng. Nghe trong BiliClass hoặc tải bản không giọng."
        )
    entries["[Content_Types].xml"] = _bytes(types)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    # Every original resource remains in the output byte-for-byte.
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination) as exported:
        for name in original_parts:
            if name.startswith(("ppt/media/", "ppt/charts/", "ppt/embeddings/")) and original.read(
                name
            ) != exported.read(name):
                raise ValueError("Tài nguyên nguồn không khớp sau khi nhúng voice.")
    return {"speakers": count, "slides": len(embedded_pages), "embedded_pages": embedded_pages, "scope": scope,
            "unplaced_pages": unplaced_pages, "restricted_pages": sorted(set(restricted_pages)),
            "missing_pages": missing_pages if scope == 'full_slide' else []}
