"""Recognize embedded pictures once in an isolated, bounded CPU worker."""

import hashlib
import io
import json
import multiprocessing
import queue
import time
from pathlib import Path

from PIL import Image

ENGINE = "rapidocr-3.9.2-latin-v5-vietocr-onnx-regions-4"


def _worker(files, events):
    from .local_ocr import engine
    from .vietnamese_ocr import VietnameseReader, pack_directory

    try:
        reader = engine("vi")
        verifier = VietnameseReader() if pack_directory() else None
        for key, path in files:
            with Image.open(path) as original:
                rgba=original.convert('RGBA')
                image=Image.new('RGB',rgba.size,'white')
                image.paste(rgba,mask=rgba.getchannel('A'))
                rgba.close()
            image.thumbnail((2400, 2400))
            try:
                result = reader(image)
                rows = []
                if result.boxes is not None:
                    for text, score, box in zip(result.txts, result.scores, result.boxes, strict=True):
                        checked, verified, alternate, probability = text, False, '', 0
                        from .input_analysis import language_of

                        if verifier is not None and language_of(text) == "vi":
                            left, top = box.min(axis=0)
                            right, bottom = box.max(axis=0)
                            crop = image.crop(
                                (
                                    max(0, int(left) - 3),
                                    max(0, int(top) - 3),
                                    min(image.width, int(right) + 4),
                                    min(image.height, int(bottom) + 4),
                                )
                            )
                            try:
                                alternate, probability = verifier.read_line(crop)
                            finally:
                                crop.close()
                            checked, verified = crosscheck(text, float(score), alternate, probability)
                        rows.append(
                            {
                                "text": checked,
                                "confidence": float(score),
                                "verified": verified,
                                "alternate": alternate,
                                "probability": probability,
                                "points": [[float(x) / image.width, float(y) / image.height] for x, y in box],
                            }
                        )
                events.put({"key": key, "rows": rows})
            finally:
                image.close()
    except Exception as exc:
        events.put({"error": type(exc).__name__})


def crosscheck(first, confidence, second, probability):
    import re
    import unicodedata

    def letters(text):
        text = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
        return re.sub(r"\s+", " ", "".join(c for c in text if not unicodedata.combining(c))).strip()

    agreed = confidence >= 0.92 and probability >= 0.88 and letters(first) == letters(second)
    return (second, True) if agreed else (first, False)


def recognize(files, cancel, notify=None, *, timeout=300):
    if not files:
        return {}
    context = multiprocessing.get_context("spawn")
    events = context.Queue()
    process = context.Process(target=_worker, args=(files, events), daemon=True)
    process.start()
    start = time.monotonic()
    rows = {}
    try:
        while len(rows) < len(files):
            if cancel.is_set():
                raise InterruptedError("Đã dừng nhận diện chữ trong ảnh.")
            if time.monotonic() - start > timeout:
                raise ValueError("Nhận diện ảnh quá thời gian; phần đã có được giữ để tiếp tục.")
            try:
                item = events.get(timeout=0.2)
            except queue.Empty:
                if not process.is_alive():
                    raise ValueError("Chưa nhận diện xong ảnh. Kiểm tra bộ OCR trong Cài đặt → Google Dịch.")
                continue
            if "error" in item:
                raise ValueError(
                    "Bộ nhận diện chữ trong ảnh chưa sẵn sàng. Chuẩn bị OCR trong Cài đặt → Google Dịch."
                )
            rows[item["key"]] = item["rows"]
            if notify:
                notify(item["key"], item["rows"])
        return rows
    finally:
        process.join(timeout=0.5)
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
        events.close()


def extract_pictures(source, directory, cancel, progress=None, *, recognizer=None, include_animated=False):
    from pptx import Presentation

    from .local_ocr import model_paths
    from .slide_speech import animation_rules, objects
    from .vietnamese_ocr import pack_directory

    deck = Presentation(source)
    occurrences = []
    pictures = {}
    warnings = []
    folder = Path(directory) / "temp/picture-ocr"
    folder.mkdir(parents=True, exist_ok=True)
    for number, slide in enumerate(deck.slides, 1):
        items = objects(slide)
        animated = set(slide._element.xpath(".//p:spTgt/@spid"))
        rules = animation_rules(slide)
        for item in items:
            if cancel.is_set():
                raise InterruptedError("Đã dừng đọc hình trong bài giảng.")
            if (
                item["source_type"] != "image"
                or item["hidden"]
                or item["w"] < 36 * 12700
                or item["h"] < 16 * 12700
            ):
                continue
            shape = item["shape"]
            # Bounding-box mapping is exact for unrotated, uncropped pictures.
            if shape.rotation or any(shape._element.xpath('.//a:xfrm[@flipH="1" or @flipV="1"]')):
                continue
            if any(
                parent.xpath('./p:grpSpPr/a:xfrm[@rot!="0" or @flipH="1" or @flipV="1"]')
                for parent in shape._element.iterancestors()
                if parent.tag.endswith("}grpSp")
            ):
                continue
            animation_sources = [key for key in item['ancestors'] if str(key) in animated]
            synchronized = (len(animation_sources) == 1
                            and rules.get(str(animation_sources[0]), {}).get('kind') == 'click')
            if not include_animated and animation_sources and not synchronized:
                continue  # Never reveal text hidden behind an unknown classroom trigger.
            crop_values=[getattr(shape,'crop_'+side,0) for side in ('left','top','right','bottom')]
            left,top,right,bottom=crop_values
            if min(crop_values)<0 or left+right>=1 or top+bottom>=1:
                continue
            blob = shape.image.blob
            digest = hashlib.sha256((ENGINE + str(bool(pack_directory()))+str(crop_values)).encode() + blob).hexdigest()
            if digest not in pictures:
                try:
                    with Image.open(io.BytesIO(blob)) as image:
                        if image.width * image.height > 30_000_000:
                            continue
                        path = folder / (digest + ".png")
                        if not path.is_file():
                            visible=image.crop((round(left*image.width),round(top*image.height),
                                                round((1-right)*image.width),round((1-bottom)*image.height)))
                            try:
                                visible.save(path, "PNG")
                            finally:
                                visible.close()
                except (OSError, ValueError):
                    warnings.append(f"Slide {number}: định dạng ảnh chưa hỗ trợ OCR.")
                    continue
                pictures[digest] = path
            occurrences.append(
                {
                    "slide": number,
                    "shape_id": item["shape_id"],
                    "key": digest,
                    "box": [item[k] / 12700 for k in ("x", "y", "w", "h")],
                    **({'animation_source': animation_sources[0]} if synchronized and not include_animated else {}),
                }
            )
    if not occurrences:
        return {"rows": [], "warnings": warnings, "images": 0, "text_pages": []}
    if recognizer is None and not model_paths():
        return {
            "rows": [],
            "images": len(pictures),
            "warnings": [
                "Chưa có bộ OCR Việt–Anh; chữ trong ảnh chưa được dịch. Chuẩn bị OCR trong Cài đặt → Google Dịch."
            ],
        }
    cached = {}
    missing = []
    for key, path in pictures.items():
        try:
            data = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
            if data["engine"] != ENGINE or data["key"] != key or not isinstance(data["rows"], list):
                raise ValueError("cache")
            cached[key] = data["rows"]
        except (OSError, ValueError, KeyError, TypeError):
            missing.append((key, str(path)))

    def checkpoint(key, rows):
        path = pictures[key].with_suffix(".json")
        pending = path.with_suffix(".tmp")
        pending.write_text(
            json.dumps({"engine": ENGINE, "key": key, "rows": rows}, ensure_ascii=False), encoding="utf-8"
        )
        pending.replace(path)
        if progress:
            progress("Đang đọc chữ trong hình minh họa.")

    if missing:
        cached.update((recognizer or recognize)(missing, cancel, checkpoint))
    rows = []
    import re

    from .input_analysis import language_of
    from .slide_semantics import roman_label

    for occurrence in occurrences:
        from .picture_prose import paragraphs, scientific_lines

        lines = scientific_lines(cached[occurrence["key"]])
        blocks = paragraphs(lines, occurrence, str(pictures[occurrence['key']]))
        rows.extend(blocks)
        included = {index for block in blocks for index in block['line_indices']}
        for index, line in enumerate(lines):
            if index in included:
                continue
            text = line["text"].strip()
            if language_of(text) != "vi" or roman_label(text) or len(text) < 4:
                continue
            if not line.get("verified") or line["confidence"] < 0.85 or re.search(r"[=∑√∫≤≥ωαβφ²³]", text):
                warnings.append(
                    f"Slide {occurrence['slide']}: chữ/công thức trong ảnh cần đối chiếu; chưa tự che."
                )
                continue
            points = line["points"]
            # Reject angled lines rather than cover neighbouring scientific labels.
            if abs((points[1][1] - points[0][1]) * occurrence['box'][3]) > max(
                    1, abs(points[1][0]-points[0][0]) * occurrence['box'][2] * .035):
                warnings.append(f"Slide {occurrence['slide']}: chữ nghiêng trong ảnh cần đối chiếu.")
                continue
            x, y, w, h = occurrence["box"]
            left, top = min(p[0] for p in points), min(p[1] for p in points)
            right, bottom = max(p[0] for p in points), max(p[1] for p in points)
            rows.append(
                {
                    **occurrence,
                    "id": f"ocr-{occurrence['slide']}-{occurrence['shape_id']}-{index}",
                    "text": text,
                    "confidence": line["confidence"],
                    "same_column": bool(line.get('scientific_join')),
                    "region": [x + left * w, y + top * h, (right - left) * w, (bottom - top) * h],
                    "image": str(pictures[occurrence["key"]]),
                }
            )
    text_pages = sorted({occurrence['slide'] for occurrence in occurrences
                         if any(sum(c.isalpha() for c in line['text']) >= 4
                                for line in cached[occurrence['key']])})
    return {"rows": rows, "images": len(pictures), "warnings": list(dict.fromkeys(warnings)),
            "text_pages": text_pages}
