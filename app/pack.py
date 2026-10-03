"""Versioned draft pack; integrity and conservative resource limits."""

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4


def export_pack(library, lesson_id, destination):
    lesson = library.get(lesson_id)
    destination = Path(destination)
    if destination.suffix.lower() != ".biliclass":
        destination = destination.with_suffix(".biliclass")
    from .portable_audio import collect_audio
    records, audio_files = collect_audio(library, lesson)
    lesson["portable_audio"] = records
    # Keep a portable reference, never install another teacher's glossary or
    # voice/mascot preferences into the receiving machine automatically.
    terms = {item["vi"].casefold(): item for item in lesson.get("project_terms", [])}
    terms.update({item["vi"].casefold(): {key: item[key] for key in ("vi", "en", "subject", "locked")}
                  for item in library.glossary(lesson["subject"])})
    lesson["project_terms"] = list(terms.values())
    lesson["project_preferences"] = {key: library.setting(key, default) for key, default in
                                     (("voice_en", ""), ("voice_vi", ""), ("voice_rate", 0),
                                      ("mascot", "Milo"), ("mascot_options", {}))}
    entries = {"lesson.json": json.dumps(lesson, ensure_ascii=False).encode("utf-8")}
    entries.update(audio_files)
    from .lesson_templates import source_image
    for segment in lesson["segments"]:
        if segment.get("source_image"):
            image = source_image(lesson, library.directory, segment)
            # source_image is only used for visual blocks; validate every stored asset.
            if image is None:
                image = library.directory / "assets" / segment["source_image"]
            if (Path(segment["source_image"]).name != segment["source_image"] or not segment["source_image"].startswith("ai-")
                    or image.is_symlink() or image.resolve().parent != (library.directory / "assets").resolve()):
                raise ValueError("Ảnh nguồn không hợp lệ.")
            payload = image.read_bytes()
            if hashlib.sha256(payload).hexdigest() != segment.get("source_image_sha256"):
                raise ValueError("Ảnh nguồn đã thay đổi; chưa thể xuất gói.")
            entries["assets/" + image.name] = payload
    source = lesson.get("source")
    if source:
        source_path = library.directory / "sources" / source["file"]
        payload = source_path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != source["sha256"]:
            raise ValueError("Bản nguồn lưu trên máy đã thay đổi; chưa thể xuất gói.")
        entries["source/" + source["file"]] = payload
    manifest = {
        "schema_version": 4 if any(name.startswith("assets/") for name in entries) else 3,
        "kind": "biliclass-draft",
        "lesson_id": lesson_id,
        "files": {
            name: {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
            for name, data in entries.items()
        },
    }
    entries["manifest.json"] = json.dumps(manifest).encode("utf-8")
    if len(entries) > 1000 or sum(map(len, entries.values())) > 200 * 1024**2:
        raise ValueError("Gói bài vượt giới hạn 1.000 tệp hoặc 200 MB giải nén; chia nhỏ bài hoặc xuất ít âm thanh hơn.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as temporary:
        temp_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        if temp_path.stat().st_size > 100 * 1024**2:
            raise ValueError("Gói bài vượt 100 MB nén; chia nhỏ bài trước khi xuất.")
        temp_path.replace(destination)
    finally:
        temp_path.unlink(missing_ok=True)
    return destination


def import_pack(library, path):
    if Path(path).stat().st_size > 100 * 1024**2:
        raise ValueError("Gói bài vượt giới hạn 100 MB.")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(entries) > 1000 or len(set(names)) != len(names):
            raise ValueError("Gói bài có quá nhiều entry hoặc entry trùng nhau.")
        if sum(entry.file_size for entry in entries) > 200 * 1024**2:
            raise ValueError("Gói giải nén quá lớn.")
        for entry in entries:
            part = PurePosixPath(entry.filename)
            if part.is_absolute() or ".." in part.parts or ":" in entry.filename or "\\" in entry.filename:
                raise ValueError("Đường dẫn trong gói không an toàn.")
            if ((entry.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError("Không chấp nhận liên kết trong gói.")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("schema_version") not in (1, 2, 3, 4) or manifest.get("kind") != "biliclass-draft":
            raise ValueError("Phiên bản Lesson Pack chưa được hỗ trợ.")
        if set(names) != set(manifest["files"]) | {"manifest.json"}:
            raise ValueError("Danh sách nội dung gói không khớp manifest.")
        payloads = {}
        for name, record in manifest["files"].items():
            data = archive.read(name)
            if len(data) != record["size"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise ValueError("Checksum gói không khớp; tệp có thể đã hỏng.")
            payloads[name] = data
    lesson = json.loads(payloads["lesson.json"])
    lesson.setdefault("source_language", "vi")
    if lesson["source_language"] not in ("vi", "en"):
        raise ValueError("Ngôn ngữ nguồn không hợp lệ.")
    for key in ("title", "subject", "education_level", "grade"):
        if not isinstance(lesson.get(key), str) or len(lesson[key]) > 1000:
            raise ValueError("Thông tin bài học không hợp lệ.")
    if not lesson["title"].strip() or not lesson["subject"].strip():
        raise ValueError("Tên bài học hoặc môn học trống.")
    terms = lesson.get("project_terms", [])
    if not isinstance(terms, list) or len(terms) > 10000 or any(
        not isinstance(item, dict) or any(not isinstance(item.get(key), str) or not item[key].strip()
                                         or len(item[key]) > 1000 for key in ("vi", "en", "subject"))
        for item in terms
    ):
        raise ValueError("Thuật ngữ tham khảo của gói bài không hợp lệ.")
    preferences = lesson.get("project_preferences", {})
    if not isinstance(preferences, dict) or len(json.dumps(preferences)) > 20000:
        raise ValueError("Cấu hình tham khảo của gói bài không hợp lệ.")
    segments = lesson.get("segments")
    if not isinstance(segments, list) or not 1 <= len(segments) <= 10000:
        raise ValueError("Danh sách đoạn không hợp lệ.")
    from .content import validate_question, validate_support
    from .portable_audio import validate_audio
    audio = validate_audio(lesson.get("portable_audio", []), segments, payloads)
    id_map, image_assets = {}, {}
    for segment in segments:
        if not isinstance(segment, dict) or not all(
            isinstance(segment.get(key), str) for key in ("vi", "en", "locator")
        ):
            raise ValueError("Nội dung đoạn không hợp lệ.")
        source_language = segment.get("source_language", lesson["source_language"])
        if source_language not in {"vi", "en"}:
            raise ValueError("Ngôn ngữ của vùng nguồn không hợp lệ.")
        if (
            not segment[source_language].strip()
            or len(segment["vi"]) + len(segment["en"]) > 100_000
        ):
            raise ValueError("Đoạn trống hoặc quá dài.")
        old_id = segment.get("id")
        if not isinstance(old_id, str) or old_id in id_map:
            raise ValueError("Mã đoạn không hợp lệ hoặc trùng lặp.")
        segment["id"] = id_map[old_id] = str(uuid4())
        support = segment.get("support", [])
        if not isinstance(support, list) or len(support) > 100:
            raise ValueError("Nội dung trợ giảng không hợp lệ.")
        segment["support"] = [validate_support(item, reset_review=True) for item in support]
        if segment.get("ai_provider") == "chatgpt_plan":
            ref, issues = segment.get("source_ref"), segment.get("ai_issues", [])
            if (not isinstance(ref, str) or len(ref) > 1000 or not ref
                    or not isinstance(issues, list) or len(issues) > 20
                    or any(not isinstance(issue, str) or len(issue) > 5000 for issue in issues)):
                raise ValueError("Tham chiếu AI của gói không hợp lệ.")
            for original, checked in zip(support, segment["support"], strict=True):
                if original.get("provider") == "chatgpt_plan":
                    basis = original.get("basis_sha256", "")
                    if (original.get("source_refs") != [ref] or not isinstance(basis, str)
                            or len(basis) != 64 or any(c not in "0123456789abcdef" for c in basis)):
                        raise ValueError("Tham chiếu hỗ trợ AI không hợp lệ.")
                    checked.update(provider="chatgpt_plan", source_refs=[ref], basis_sha256=basis)
        image_name = segment.get("source_image")
        if image_name:
            if (not isinstance(image_name, str) or Path(image_name).name != image_name or not image_name.startswith("ai-")
                    or Path(image_name).suffix != ".png"):
                raise ValueError("Tên ảnh nguồn không hợp lệ.")
            image_data = payloads.get("assets/" + image_name)
            if image_data is None or hashlib.sha256(image_data).hexdigest() != segment.get("source_image_sha256"):
                raise ValueError("Ảnh nguồn không khớp gói bài.")
            import io

            from PIL import Image
            with Image.open(io.BytesIO(image_data)) as image:
                image.verify()
            image_assets[image_name] = image_data
        segment["approved"] = False  # imported content must be reviewed by this teacher
        segment["locked"] = bool(segment.get("locked", False))
        from .lesson_templates import block_type
        segment["kind"] = block_type(segment.get("kind", "unknown"))["id"]
        segment.setdefault("source_text", segment[source_language])
        if segment.get("source_language", lesson["source_language"]) not in {"vi", "en"}:
            raise ValueError("Ngôn ngữ của vùng nguồn không hợp lệ.")
        if not isinstance(segment.get("paired_locator", ""), str):
            raise ValueError("Liên kết vùng song ngữ không hợp lệ.")
        if not isinstance(segment["source_text"], str) or len(segment["source_text"]) > 100_000:
            raise ValueError("Bản trích xuất nguồn không hợp lệ.")
    questions = lesson.get("questions", [])
    if not isinstance(questions, list) or len(questions) > 200:
        raise ValueError("Danh sách câu hỏi không hợp lệ.")
    lesson["questions"] = [validate_question(q, reset_review=True) for q in questions]
    for question in lesson["questions"]:
        if question["concept_id"] not in id_map:
            raise ValueError("Câu hỏi không liên kết nội dung bài.")
        question["concept_id"] = id_map[question["concept_id"]]
    lesson.pop("portable_audio", None)
    lesson.pop("prepared", None)  # receiving teacher must review and prepare this revision
    source = lesson.get("source")
    if source:
        if not isinstance(source, dict):
            raise ValueError("Thông tin nguồn không hợp lệ.")
        filename = source.get("file", "")
        if Path(filename).name != filename or not filename or ":" in filename:
            raise ValueError("Tên nguồn không hợp lệ.")
        data = payloads.get("source/" + filename)
        if data is None or hashlib.sha256(data).hexdigest() != source.get("sha256"):
            raise ValueError("Nguồn bài học không khớp.")
        if (
            Path(filename).suffix not in (".txt", ".docx", ".pptx", ".pdf", ".png", ".jpg", ".jpeg")
            or filename != hashlib.sha256(data).hexdigest() + Path(filename).suffix
        ):
            raise ValueError("Tên tệp nguồn phải khớp checksum.")
        target = library.directory / "sources" / filename
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(data)
    from .library import now

    lesson.update(id=str(uuid4()), revision=1, updated_at=now())
    if lesson.get("external_deck"):
        from .chatgpt_handoff import text_signature

        external = lesson["external_deck"]
        if (not isinstance(external, dict) or not source or not source["file"].endswith(".pptx")
                or external.get("sha256") != source["sha256"]
                or type(external.get("total")) is not int or not 1 <= external["total"] <= 1000
                or external.get("text_signature") != text_signature(lesson)):
            raise ValueError("PowerPoint từ ChatGPT trong gói không hợp lệ.")
        external["reviewed_revision"] = 0
        external.pop("reviewed_at", None)
    lesson["level"] = (
        lesson.get("level", 2) if type(lesson.get("level")) is int and 0 <= lesson["level"] <= 5 else 2
    )
    if lesson.get("layout") not in ("keyword_overlay", "line_pair", "split_view", "english_rescue", "level_auto"):
        lesson["layout"] = "line_pair"
    if lesson.get("teaching_preset") not in ("standard", "visual", "practice"):
        lesson["teaching_preset"] = "standard"
    if lesson.get("presentation_style") not in {"source", "template"}:
        lesson["presentation_style"] = "template"
    if lesson["presentation_style"] == "source" and not (lesson.get("source") or {}).get("file", "").lower().endswith(".pptx"):
        raise ValueError("Chế độ giữ thiết kế gốc cần nguồn PowerPoint.")
    if lesson.get("conversion_mode", "paired") not in {"level", "preserve", "paired"}:
        raise ValueError("Cách chuyển đổi PowerPoint không hợp lệ.")
    for record, data in audio:
        folder = library.directory / "audio"
        folder.mkdir(exist_ok=True)
        (folder / record["file"]).write_bytes(data)
        record = {**record, "segment_id": id_map[record["segment_id"]]}
        (folder / (record["sha256"] + ".json")).write_text(json.dumps(record), encoding="utf-8")
    for name, data in image_assets.items():
        folder = library.directory / "assets"
        folder.mkdir(exist_ok=True)
        target = folder / name
        if target.is_symlink():
            raise ValueError("Không ghi ảnh qua liên kết.")
        target.write_bytes(data)
    library._write(lesson, new=True)
    return lesson
