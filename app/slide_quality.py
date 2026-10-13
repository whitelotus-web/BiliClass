"""Per-slide checks; render success is never a claim of semantic/visual completeness."""

import json
import re
from pathlib import Path

from .slide_speech import native_shapes, objects, speech_problem

MESSAGES = {
    "technical_text": "Có nhãn kỹ thuật hoặc ký tự bất thường; không đưa vào lời đọc.",
    "suspicious_code": "Có chuỗi nghi là mã rác; cần đối chiếu với nguồn.",
    "suspicious_character": "Có chữ thường lạc giữa tiêu đề; cần đối chiếu, không tự đọc.",
    "english_body_missing": "Thân bài Việt dài nhưng phần Anh chỉ ngắn như tiêu đề; cần bổ sung bản dịch từ nguồn.",
    "formula_needs_review": "Công thức/ký hiệu cần kiểm tra cách đọc theo ngữ cảnh.",
    "image_or_formula_needs_review": "Chữ/công thức trong ảnh chưa được xác minh; chưa chứng nhận đủ song ngữ/lời đọc.",
    "language_needs_review": "Có vùng chưa xác định chắc ngôn ngữ; không tự đọc như tiếng Anh.",
    "notes_mismatch": "Lời EN trong ghi chú khác nội dung tiếng Anh trích từ slide.",
    "animation_needs_review": "Hiệu ứng/trigger chưa xác định chắc phần đang hiển thị; bỏ qua phần đó khi đọc.",
    "speech_metadata_invalid": "Dữ liệu lời đọc có cấu trúc trong ghi chú không hợp lệ.",
    "speech_metadata_mismatch": "Dữ liệu lời đọc khai báo không khớp đối tượng trên slide.",
    "outside_slide": "Có chữ nằm ngoài khung slide.",
    "possible_overlap": "Hình ở phía trước có thể che chữ; cần kiểm tra ảnh render.",
    "text_overflow": "PowerPoint đo được chữ tràn khỏi hộp văn bản.",
    "small_text": "Có chữ nhỏ hơn 18 pt; kiểm tra độ dễ đọc khi chiếu.",
    "low_contrast": "Chữ có độ tương phản thấp với màu nền đặc của hộp chữ.",
    "quiz_mismatch": "Dấu tick trên phương án không khớp đáp án QUIZ trong ghi chú.",
    "render_unavailable": "Chưa render được bằng PowerPoint; không chứng nhận bố cục.",
    "visual_review": "Ảnh đã render; hình khoa học, tương phản và hiệu ứng vẫn cần đối chiếu.",
    "slide_count": "Số slide không khớp yêu cầu giữ PowerPoint đầu vào.",
    "vietnamese_remaining": "Chế độ English 100% còn chữ Việt trong đối tượng văn bản.",
}


def _intersection(a, b):
    return max(0, min(a[0]+a[2], b[0]+b[2])-max(a[0], b[0])) * max(0, min(a[1]+a[3], b[1]+b[3])-max(a[1], b[1]))


def contrast_ratio(first, second):
    def luminance(value):
        channels = [(value >> shift & 255)/255 for shift in (0, 8, 16)]
        linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels]
        return sum(c*w for c, w in zip(linear, (.2126, .7152, .0722), strict=True))
    a, b = sorted((luminance(first), luminance(second)))
    return (b+.05)/(a+.05)


def inspect_quality(deck, speech, mode="", source_total=None):
    from .slide_speech import VI_MARKS

    rows = []
    for index, slide in enumerate(deck.slides, 1):
        spoken = speech["slides"][index-1]
        issues = [{"code": code, "severity": "CHECK"} for code in spoken["issues"]]
        shapes = objects(slide)
        for item in shapes:
            if not item["text"]:
                continue
            box = (item["x"], item["y"], item["w"], item["h"])
            if (box[0] < -91440 or box[1] < -91440 or box[0]+box[2] > deck.slide_width+91440
                    or box[1]+box[3] > deck.slide_height+91440):
                issues.append({"code": "outside_slide", "severity": "FAIL", "shape_id": item["shape_id"]})
            problem = speech_problem(item["text"])
            if problem and problem != "formula_needs_review":
                issues.append({"code": problem, "severity": "FAIL", "shape_id": item["shape_id"]})
            if mode == "english_only" and any(c in VI_MARKS for c in item["text"].casefold()):
                issues.append({"code": "vietnamese_remaining", "severity": "CHECK", "shape_id": item["shape_id"]})
            if any(run.font.size and run.font.size.pt < 18 for run in item["runs"]):
                issues.append({"code": "small_text", "severity": "CHECK", "shape_id": item["shape_id"]})
            # Z-order matters; backgrounds behind text are never called occluders.
            positions = [s.shape_id for s in native_shapes(slide.shapes)]
            root_id = item["ancestors"][0]
            for later in shapes:
                if (later["source_type"] == "image" and later["ancestors"][0] in positions
                        and root_id in positions and positions.index(later["ancestors"][0]) > positions.index(root_id)
                        and _intersection(box, (later["x"], later["y"], later["w"], later["h"])) > box[2]*box[3]*.25):
                    issues.append({"code": "possible_overlap", "severity": "CHECK", "shape_id": item["shape_id"]})
                elif (later["text"] and later["shape_id"] != item["shape_id"]
                        and _intersection(box, (later["x"], later["y"], later["w"], later["h"])) > box[2]*box[3]*.65):
                    # A broad bounding box can contain intentionally aligned text,
                    # so overlap is a review hint, never an automatic deletion.
                    issues.append({"code": "possible_overlap", "severity": "CHECK", "shape_id": item["shape_id"]})
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        ticks = {m[1] for item in shapes for m in re.finditer(r"(?:[✓✔☑]\s*([A-D])[.)]|([A-D])[.)][^\n]*[✓✔☑])", item["text"])
                 if m[1]}
        ticks |= {m[1] for item in shapes for m in re.finditer(r"([A-D])[.)][^\n]*[✓✔☑]", item["text"])}
        for line in notes.splitlines():
            if line.strip().startswith("QUIZ:"):
                try:
                    question = json.loads(line.split(":", 1)[1])
                    if ticks and question.get("correct") not in ticks:
                        issues.append({"code": "quiz_mismatch", "severity": "FAIL"})
                except (ValueError, AttributeError):
                    pass
        if source_total is not None and source_total != len(deck.slides):
            issues.append({"code": "slide_count", "severity": "FAIL"})
        unique = {json.dumps(issue, sort_keys=True): issue for issue in issues}
        rows.append({"slide": index, "slide_id": slide.slide_id, "issues": list(unique.values()),
                     "rendered": False, "render_image": "", "status": "CHECK"})
    report = {"schema_version": 1, "sha256": speech["sha256"], "slides": rows,
              "scope": "native object/speech checks and Office text geometry; no automatic OCR or semantic/animation certification"}
    return update_status(report)


def update_status(report):
    for row in report["slides"]:
        for issue in row["issues"]:
            issue["message"] = MESSAGES.get(issue["code"], issue["code"])
        row["status"] = "FAIL" if any(i["severity"] == "FAIL" for i in row["issues"]) else "CHECK"
        # PASS only describes automated checks; visual/content approval belongs to the teacher.
        row["technical_status"] = "FAIL" if row["status"] == "FAIL" else "CHECK" if row["issues"] else "PASS"
    report["counts"] = {state: sum(row["status"] == state for row in report["slides"]) for state in ("PASS", "CHECK", "FAIL")}
    report["status"] = "FAIL" if report["counts"]["FAIL"] else "CHECK"
    return report


def quality_messages(report, limit=80):
    return [f"Slide {row['slide']} · {issue['severity']}: {MESSAGES.get(issue['code'], issue['code'])}"
            for row in report["slides"] for issue in row["issues"]][:limit]


def render_quality(path, directory, report, cancel=None, progress=None, *, reuse_directory=None):
    """Render every slide and measure actual text bounds using installed PowerPoint."""
    from .conversion_progress import emit_progress
    from .slide_render_cache import RENDER_CODES, RenderCache

    cache = RenderCache(path, directory, report, reuse_directory)
    folder = cache.folder
    remaining, complete, reused = [], 0, 0
    total = len(report["slides"])
    for row in report["slides"]:
        row["issues"] = [issue for issue in row["issues"] if issue["code"] not in RENDER_CODES]
        row.update(rendered=False, render_image="")
        if cancel and cancel.is_set():
            remaining.append(row)
        elif cache.reuse(row):
            complete += 1
            reused += 1
            emit_progress(progress, "quality", f"Dùng lại ảnh đã kiểm tra {complete}/{total} slide…", complete, total)
        else:
            remaining.append(row)
    office = deck = com = None
    existing = True
    try:
        if remaining and not (cancel and cancel.is_set()):
            import psutil
            import pythoncom
            import win32com.client

            existing = any((p.info["name"] or "").lower() == "powerpnt.exe" for p in psutil.process_iter(["name"]))
            pythoncom.CoInitialize()
            com = pythoncom
            office = win32com.client.DispatchEx("PowerPoint.Application")
            deck = office.Presentations.Open(str(Path(path).resolve()), ReadOnly=True, Untitled=False, WithWindow=False)
            height = round(1600*deck.PageSetup.SlideHeight/deck.PageSetup.SlideWidth)
        for row in remaining:
            if cancel and cancel.is_set():
                break
            emit_progress(progress, "quality", f"Kiểm tra ảnh và lời đọc slide {row['slide']}/{total}…", complete, total)
            image = cache.image(row["slide"])
            slide = deck.Slides(row["slide"])
            temporary = image.with_name(image.stem + "-pending.png")
            slide.Export(str(temporary.resolve()), "PNG", 1600, height)
            temporary.replace(image)
            row.update(rendered=True, render_image=image.relative_to(directory).as_posix())
            for shape in slide.Shapes:
                try:
                    if not shape.HasTextFrame or not shape.TextFrame2.HasText:
                        continue
                    text = shape.TextFrame2.TextRange
                    if text.BoundHeight > shape.Height + 3 or text.BoundWidth > shape.Width + 3:
                        row["issues"].append({"code": "text_overflow", "severity": "FAIL", "shape_id": shape.Id})
                    if shape.Fill.Visible and shape.Fill.Type == 1:
                        foreground, background = int(text.Font.Fill.ForeColor.RGB), int(shape.Fill.ForeColor.RGB)
                        if foreground < 0 or background < 0:
                            continue  # Mixed/theme-dependent colors are not a reliable measurement.
                        ratio = contrast_ratio(foreground, background)
                        threshold = 3 if float(text.Font.Size) >= 24 else 4.5
                        if ratio < threshold:
                            row["issues"].append({"code": "low_contrast", "severity": "CHECK", "shape_id": shape.Id})
                except Exception:
                    continue
            cache.save_row(row)
            complete += 1
            emit_progress(progress, "quality", f"Đã kiểm tra {complete}/{total} slide…", complete, total)
    except Exception:
        # Missing Office must not discard a returned deck or imply a successful visual check.
        pass
    finally:
        if deck is not None:
            try:
                deck.Close()
            except Exception:
                pass
        if office is not None and not existing:
            try:
                if office.Presentations.Count == 0:
                    office.Quit()
            except Exception:
                pass
        office = deck = None
        if com:
            com.CoUninitialize()
    for row in report["slides"]:
        row["issues"].append({"code": "visual_review" if row["rendered"] else "render_unavailable", "severity": "CHECK"})
    update_status(report)
    report["render_cache"] = {"reused": reused, "rendered": complete-reused, "total": total}
    cache.save()
    (folder / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
