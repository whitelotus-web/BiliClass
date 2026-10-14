"""Verified local fitting and bounded, durable corrections in the same chat."""

import hashlib
import json
import logging
import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

from .conversion_progress import emit_progress, scoped_progress
from .document_limits import MAX_POWERPOINT_BYTES
from .slide_repair import actionable_rows, failure_keys, repair_and_inspect

MAX_ROUNDS = 3


def source_media_preserved(source, candidate, style):
    if style != "source" or Path(source).suffix.lower() != ".pptx" or not zipfile.is_zipfile(source):
        return True
    def media(path):
        with zipfile.ZipFile(path) as archive:
            return {hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()
                    if name.startswith("ppt/media/") and not name.endswith("/")}
    return media(source) <= media(candidate)


def improved(before, after):
    old, new = failure_keys(before), failure_keys(after)
    critical = {"slide_count", "quiz_mismatch", "technical_text", "suspicious_code", "english_body_missing"}
    if {(n, code) for n, code, _ in new if code in critical} - {(n, code) for n, code, _ in old if code in critical}:
        return False
    def missing(q):
        return sum(i["code"] in {"english_body_missing", "translation_coverage"}
                   for r in q["slides"] for i in r["issues"])
    return (len(new), missing(after)) < (len(old), missing(before))


def refinement_prompt(config, report):
    from .conversion_formats import METHODS
    from .slide_quality import quality_messages

    method = METHODS.get(config.get("conversion_format"), "Giữ đủ cặp Việt–Anh trên slide theo cấu hình ban đầu.")
    heading = ("Tiêu đề chỉ bằng tiếng Anh, cùng font chủ đạo, dễ đọc và tương phản với nền. "
               if config.get("conversion_format") == "english_only" else
               "Mọi tiêu đề: Việt trên, Anh ngay dưới; cùng font, Anh nhỏ hơn khoảng 20–25%, in nghiêng, đen trên nền sáng. ")
    return ("SỬA BẢN SAO của PPTX mới nhất trong đúng cuộc trò chuyện này; dùng lại tệp và tài liệu nguồn "
            "đã có ở đây, không cần tải lại tệp. Xuất FILE bai-giang-song-ngu.pptx chỉnh sửa được và link tải.\n"
            "CHỈ DỊCH TIÊU ĐỀ HOẶC CHỈ THÊM EN VÀO NOTES LÀ CHƯA HOÀN THÀNH. "
            "Đối chiếu và dịch đầy đủ từng vùng thân bài, câu hỏi, phương án, hướng dẫn, chú thích và kết luận với nguồn; "
            "English phải hiển thị thật trên slide. Không bỏ ý/điều kiện, không đoán công thức hoặc đáp án.\n"
            "Đọc cả chữ trong ảnh kiến thức của nguồn; đặt bản dịch trong vùng text riêng, không phủ lên nhãn/hình "
            "và không chỉ thêm một tiêu đề Anh bên trên ảnh Việt. Chỗ không đọc chắc phải nêu rõ slide/vùng.\n"
            + method + "\n"
            + heading +
            "Dành riêng vùng tiêu đề. Hình không che chữ; dàn lại theo tỷ lệ, không cắt nhãn/trục/công thức. "
            "Giữ số/thứ tự slide và tài nguyên/hiệu ứng khi giữ PowerPoint gốc. Không ghép thân bài hai ngôn ngữ "
            "trong cùng hộp nếu chọn hai cột. Giữ đúng kiến thức, số liệu và ý đồ giáo viên.\n"
            "Sửa hộp chữ/giãn dòng/cỡ chữ trong mức dễ đọc; render và đọc lại từng slide, không chỉ kiểm tra file lưu được. "
            "Giữ Notes gốc, cập nhật VI:/EN: và SPEECH: từ chữ thực trên slide; không lộ đáp án ẩn, không đọc JSON/mã. "
            "CHECK chỉ cho phần thực sự chưa xác minh; ghi cụ thể, không dùng cảnh báo chung thay bản dịch.\n"
            + ("Lưu ý giáo viên: " + config["teacher_notes"] + "\n" if config.get("teacher_notes") else "")
            + "LỖI ĐƯỢC PHÁT HIỆN (chữ tràn và nội dung/bố cục):\n"
            + "\n".join(quality_messages(report, limit=70)))


def refine(page, folder, record, request, pending, cancel, progress, timeout):
    from .browser_services import backend_for
    web = backend_for({"service": request["config"].get("browser_service", "chatgpt")})

    folder, pending = Path(folder), Path(pending)
    config = request["config"]
    source = folder / config["source_file"]

    def checked(path, sink):
        return repair_and_inspect(path, folder, source=source, mode=config.get("conversion_format", ""),
                                  style=config["style"], cancel=cancel, progress=sink)

    emit_progress(progress, "quality", "Đang kiểm tra và hoàn thiện bố cục bài giảng…")
    result = checked(pending, progress)
    if Path(result["path"]) != pending:
        backup = folder / ("ban-nhap-truoc-sua-cuc-bo-" + uuid4().hex[:8] + ".pptx")
        pending.replace(backup)
        Path(result["path"]).replace(pending)
    quality = result["inspection"]["slide_quality"]
    (folder / "quality-before.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    # An uncertain send cannot be replaced with another correction prompt.
    if record.get("quality_stage") in {"preparing", "submitting"}:
        return
    while actionable_rows(quality) and record.get("quality_followups", 0) < MAX_ROUNDS:
        web.check_cancel(cancel)
        round_number = record.get("quality_followups", 0) + 1
        record.update(quality_followups=round_number, quality_stage="preparing")
        web.write_record(folder, record)
        prompt = refinement_prompt(config, {"slides": actionable_rows(quality)})
        files = ([folder / row["render_image"] for row in actionable_rows(quality)[:2] if row.get("render_image")]
                 if record.get("plan") in {"plus", "pro", "business", "enterprise", "edu", "go"} else [])
        emit_progress(progress, "refine", f"Đang hoàn thiện nội dung và bố cục, lượt {round_number}…")
        record["quality_stage"] = "submitting"
        web.write_record(folder, record)
        web.submit(page, folder, record, prompt, cancel, files=files, progress=progress)
        record["quality_stage"] = "waiting"
        web.write_record(folder, record)
        emit_progress(progress, "refine_wait", "Đang hoàn thiện bản bài giảng…")
        link = web.wait_result(page, folder, record, cancel, progress, timeout)
        download = web.receive_download(page, link, cancel, progress=progress)
        downloaded = download.path()
        if (Path(download.suggested_filename).suffix.casefold() != ".pptx" or not downloaded
                or Path(downloaded).stat().st_size > MAX_POWERPOINT_BYTES):
            raise web.BrowserProblem("download", "Chưa nhận được bản sửa hợp lệ; bài trước được giữ.")
        corrected = folder / f"ket-qua-sau-kiem-tra-{round_number}.pptx"
        download.save_as(str(corrected))
        after = checked(corrected, scoped_progress(progress, "refine_quality"))
        (folder / "quality-after.json").write_text(json.dumps(after["inspection"]["slide_quality"], ensure_ascii=False, indent=2), encoding="utf-8")
        web.check_cancel(cancel)
        record["quality_stage"] = "checked"
        if (not improved(quality, after["inspection"]["slide_quality"])
                or not source_media_preserved(source, Path(after["path"]), config["style"])):
            record["quality_stop_reason"] = "no_improvement"
            web.write_record(folder, record)
            break
        backup = folder / ("ban-nhap-truoc-sua.pptx" if round_number == 1 and not (folder / "ban-nhap-truoc-sua.pptx").exists()
                           else f"ban-nhap-truoc-sua-{round_number}-{uuid4().hex[:6]}.pptx")
        pending.replace(backup)
        Path(after["path"]).replace(pending)
        quality = after["inspection"]["slide_quality"]
        record["quality_stop_reason"] = "complete" if not actionable_rows(quality) else "improved"
        web.write_record(folder, record)
    if actionable_rows(quality) and record.get("quality_followups", 0) >= MAX_ROUNDS:
        record["quality_stop_reason"] = "round_limit"
        web.write_record(folder, record)


def repair_existing(account, root, original_folder, path, directory, lesson_id, revision, cancel, progress):
    """Repair a saved lesson without resending its original conversion request."""
    from .browser_services import backend_for
    web = backend_for(account)
    from .browser_accounts import profile_lock
    from .chatgpt_handoff import load_request

    directory, original_folder = Path(directory), Path(original_folder)
    request = load_request(original_folder)
    config = request["config"]
    result = repair_and_inspect(path, directory, source=original_folder / config["source_file"],
                               mode=config.get("conversion_format", ""), style=config["style"],
                               cancel=cancel, progress=progress)
    if not actionable_rows(result["inspection"]["slide_quality"]):
        return result
    from .browser_health import quota_blocked
    if not account.get("ready") or quota_blocked(account):
        result["message"] = "Đã kiểm tra bố cục. Đăng nhập lại tài khoản của bài này để tiếp tục hoàn thiện nội dung."
        return result
    parent_record = web.read_record(original_folder, account["id"])
    if not web.conversation_url(parent_record.get("url", "")):
        result["message"] = "Chưa có phiên sửa của bài này. Chuyển đổi lại từ tài liệu gốc để hoàn thiện nội dung."
        return result
    folder = directory / "temp" / "lesson-web-repair" / lesson_id / str(revision)
    folder.mkdir(parents=True, exist_ok=True)
    pending = folder / "best.pptx"
    journal = folder / "browser-job.json"
    if not journal.exists():
        shutil.copy2(original_folder / config["source_file"], folder / config["source_file"])
        shutil.copy2(result["path"], pending)
        record = {**parent_record, "state": "waiting", "quality_stage": "checked", "quality_followups": 0,
                  "followups": 0, "error": "", "lesson_id": ""}
        for key in ("send_sha256", "quality_stop_reason"):
            record.pop(key, None)
        web.write_record(folder, record)
    else:
        record = web.read_record(folder, account["id"])
    record["require_highest_model"] = config.get("require_highest_model", True)
    try:
        from playwright.sync_api import sync_playwright

        with profile_lock(root, account["id"]), sync_playwright() as playwright:
            context = web.open_context(playwright, account, background=True, cancel=cancel)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(10000)
                if record["state"] == "submitting":
                    if account.get("service", "chatgpt") == "gemini":
                        web.recover_submission(page, folder, record, cancel)
                    else:
                        from .browser_receipt import recover_submission
                        page = recover_submission(context, page, folder, record, request, cancel)
                else:
                    web.navigate(page, record["url"], cancel)
                    web.require_account(page, cancel)
                if record.get("quality_stage") not in {"submitting", "waiting"}:
                    from .browser_capabilities import select_best_model, select_reasoning

                    if account.get("service", "chatgpt") == "gemini":
                        record.update(model=web.select_model(page), reasoning="Theo quyền trên Gemini")
                    else:
                        record.update(model=select_best_model(page), reasoning=select_reasoning(page))
                    web.write_record(folder, record)
                if record.get("quality_stage") in {"submitting", "waiting"}:
                    link = web.wait_result(page, folder, record, cancel, progress, 900)
                    download = web.receive_download(page, link, cancel, progress=progress)
                    candidate = folder / "recovered.pptx"
                    if (Path(download.suggested_filename).suffix.casefold() != ".pptx" or not download.path()
                            or Path(download.path()).stat().st_size > MAX_POWERPOINT_BYTES):
                        raise web.BrowserProblem("download", "Bản sửa chưa hợp lệ; bài trước được giữ.")
                    download.save_as(str(candidate))
                    before = repair_and_inspect(pending, directory, source=folder / config["source_file"],
                                                mode=config.get("conversion_format", ""), style=config["style"], cancel=cancel)
                    after = repair_and_inspect(candidate, directory, source=folder / config["source_file"],
                                               mode=config.get("conversion_format", ""), style=config["style"], cancel=cancel)
                    if (improved(before["inspection"]["slide_quality"], after["inspection"]["slide_quality"])
                            and source_media_preserved(folder / config["source_file"], Path(after["path"]), config["style"])):
                        shutil.copy2(after["path"], pending)
                    else:
                        record["quality_stop_reason"] = "no_improvement"
                    record["quality_stage"] = "checked"
                    web.write_record(folder, record)
                if record.get("quality_stop_reason") != "no_improvement":
                    refine(page, folder, record, request, pending, cancel, progress, 900)
            finally:
                context.close()
        repaired = repair_and_inspect(pending, directory, source=folder / config["source_file"],
                                     mode=config.get("conversion_format", ""), style=config["style"], cancel=cancel)
        if improved(result["inspection"]["slide_quality"], repaired["inspection"]["slide_quality"]):
            result = repaired
        result["repair_folder"] = str(folder)
    except web.BrowserProblem as exc:
        record["error"] = exc.code
        web.write_record(folder, record)
        result["message"] = str(exc)
    except Exception:
        if cancel.is_set():
            raise ValueError("Đã dừng sửa bài giảng; bản trước vẫn được giữ.")
        logging.getLogger(__name__).exception("Saved lesson repair interrupted")
        record["error"] = "browser"
        web.write_record(folder, record)
        result["message"] = "Phiên xử lý tạm gián đoạn. Bài và tiến trình sửa đã được giữ để tiếp tục."
    return result
