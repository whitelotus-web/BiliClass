"""Five authored fixtures and 100 synthetic model probes, not teacher quality ratings."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.library import Library
from app.pack import export_pack, import_pack
from app.text_quality import review_warnings
from app.translation import translate_draft


def main():
    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("BILICLASS_MODEL_DIR", str(root / ".runtime/models"))
    fixtures = [
        ("Toán", "10", "So sánh hai biểu thức $x^2 + 2x = 3$ và $y = 2x$.", "Compare the expressions $x^2 + 2x = 3$ and $y = 2x$."),
        ("Hóa học", "11", "Ghi lại H₂O và CO2 trong bảng quan sát.", "Record H₂O and CO2 in the observation table."),
        ("Ngữ văn", "12", "Dùng bằng chứng để giải thích cách hiểu của em.", "Use evidence to explain your interpretation."),
        ("Lịch sử", "11", "So sánh thông tin trong hai nguồn tư liệu.", "Compare the information in two sources."),
        ("Dự án cộng đồng tự chọn", "10", "Lập kế hoạch và phân công nhiệm vụ cho nhóm.", "Make a plan and assign tasks to the group."),
    ]
    records, probes = [], []
    with tempfile.TemporaryDirectory(prefix="biliclass-subjects-") as temporary:
        library = Library(Path(temporary) / "library")
        try:
            for subject, grade, vi, en in fixtures:
                lesson = library.create("Bài kiểm chứng công cụ", subject, "THPT", grade, [("Hoạt động 1", vi)])
                lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], vi, en, True)
                path = export_pack(library, lesson["id"], Path(temporary) / f"{len(records)}.biliclass")
                copied = import_pack(library, path)
                assert copied["subject"] == subject and copied["segments"][0]["en"] == en
                assert not copied["segments"][0]["approved"]
                records.append({"subject": subject, "grade": grade, "roundtrip": True})
                for n in range(1, 11):
                    for language, text in (("vi", vi + f" Nhóm {n} có 20 học sinh."), ("en", en + f" Group {n} has 20 students.")):
                        start = time.perf_counter()
                        translated = translate_draft(text, language)
                        warnings = review_warnings(text, translated) if language == "vi" else review_warnings(translated, text)
                        probes.append({"subject": subject, "direction": language, "source": text, "draft": translated,
                                       "seconds": round(time.perf_counter()-start, 3), "number_symbol_warnings": warnings})
        finally:
            library.close()
    seconds = sorted(p["seconds"] for p in probes)
    result = {"status": "passed", "fixture_subjects": records, "model_calls": len(probes),
              "warning_cases": sum(bool(p["number_symbol_warnings"]) for p in probes), "p95_seconds": seconds[94],
              "scope": "Authored fixtures plus templated synthetic probes on this busy machine; no human evaluation of translation accuracy", "probes": probes}
    (root / "reports/app/multisubject.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("probes", "fixture_subjects")}))


if __name__ == "__main__":
    main()
