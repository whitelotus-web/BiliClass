"""Read source-linked supports from lessons saved by the retired OAuth pipeline.

No credentials, networking or generation. Saved lessons remain teacher data.
"""

import hashlib
import json


def checked_ai_support(snapshot):
    for segment in snapshot.get("segments", []):
        if segment.get("ai_provider") != "chatgpt_plan":
            continue
        if any("SOURCE_MISSING" in issue for issue in segment.get("ai_issues", [])):
            raise ValueError(segment["locator"] + ": nguồn chưa đủ hoặc chưa đọc rõ. Sửa nội dung trước khi dùng để dạy.")
        basis = hashlib.sha256(json.dumps({"vi": segment["vi"], "en": segment["en"]},
                                          ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        for support in segment.get("support", []):
            if support.get("provider") == "chatgpt_plan":
                if support.get("source_refs") != [segment.get("source_ref")]:
                    raise ValueError("Nội dung trợ giảng không còn khớp nguồn.")
                if support.get("basis_sha256") == basis:
                    support["approved"] = True
    return snapshot
