"""Reviewed teaching content; every item belongs to a source segment."""

from uuid import uuid4

KINDS = {"explanation", "easy_en", "example", "prompt", "question", "rescue", "vocabulary"}


def validate_support(value, reset_review=False):
    if not isinstance(value, dict) or value.get("kind") not in KINDS:
        raise ValueError("Loại nội dung trợ giảng không hợp lệ.")
    result = {"id": str(uuid4()), "kind": value["kind"], "provenance": "teacher_authored"}
    for language in ("vi", "en"):
        text = value.get(language, "")
        if not isinstance(text, str) or len(text) > 10000:
            raise ValueError("Nội dung trợ giảng tối đa 10.000 ký tự mỗi ngôn ngữ.")
        result[language] = text.strip()
    if not result["vi"] and not result["en"]:
        raise ValueError("Điền ít nhất một ngôn ngữ.")
    result["approved"] = bool(value.get("approved")) and not reset_review
    if result["approved"]:
        required = ("en",) if result["kind"] == "easy_en" else ("vi",) if result["kind"] == "rescue" else ("vi", "en")
        if any(not result[key] for key in required):
            raise ValueError("Bổ sung đủ nội dung Việt/Anh trước khi duyệt mục này.")
    return result


def validate_question(value, reset_review=False):
    if not isinstance(value, dict) or value.get("kind") not in {"single", "true_false", "poll"}:
        raise ValueError("Loại câu hỏi không hợp lệ.")
    result = {"id": str(uuid4()), "kind": value["kind"], "approved": bool(value.get("approved")) and not reset_review}
    for key in ("vi", "en", "concept_id", "concept_label", "rationale_vi", "rationale_en", "comparison_group"):
        text = value.get(key, "")
        if not isinstance(text, str) or len(text) > 5000:
            raise ValueError("Thông tin câu hỏi quá dài hoặc không hợp lệ.")
        result[key] = text.strip()
    if not result["concept_id"] or not result["vi"] or not result["en"]:
        raise ValueError("Câu hỏi cần liên kết đoạn và có đủ tiếng Việt/Anh.")
    options = value.get("options", [])
    if not isinstance(options, list) or not 2 <= len(options) <= 6:
        raise ValueError("Câu hỏi cần từ 2 đến 6 lựa chọn.")
    if result["kind"] == "true_false" and len(options) != 2:
        raise ValueError("Câu đúng/sai cần đúng 2 lựa chọn.")
    result["options"] = []
    for index, item in enumerate(options):
        if not isinstance(item, dict):
            raise ValueError("Lựa chọn không hợp lệ.")
        option = {"id": chr(65 + index)}
        for key in ("vi", "en", "misconception"):
            text = item.get(key, "")
            if not isinstance(text, str) or len(text) > 1500:
                raise ValueError("Lựa chọn quá dài.")
            option[key] = text.strip()
        if not option["vi"] or not option["en"]:
            raise ValueError("Mỗi lựa chọn cần có đủ Việt/Anh.")
        result["options"].append(option)
    correct = value.get("correct")
    if result["kind"] == "poll":
        result["correct"] = None
    elif correct not in {o["id"] for o in result["options"]}:
        raise ValueError("Chọn đáp án đúng trước khi lưu câu hỏi.")
    else:
        result["correct"] = correct
    return result


def assistant_response(segment, action, language, level=2):
    if not segment.get("approved"):
        return {"available": False, "text": "Đoạn này cần được duyệt trước khi dùng trợ giảng."}
    kind = "easy_en" if action == "explanation" and language == "en" and level == 2 else action
    items = [item for item in segment.get("support", []) if item.get("approved") and item["kind"] == kind]
    if not items and kind == "easy_en":
        items = [item for item in segment.get("support", []) if item.get("approved") and item["kind"] == action]
    texts = [item[language] for item in items if item.get(language)]
    if action == "rescue" and not texts:
        texts = [segment["vi"]] if segment.get("vi") else []
    return {"available": bool(texts), "text": "\n\n".join(texts) if texts else "Nội dung này chưa được chuẩn bị và duyệt cho đoạn đang dạy.",
            "source": segment.get("locator", ""), "language": language, "action": action}
