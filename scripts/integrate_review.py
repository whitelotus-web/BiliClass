"""One-time, reproducible integration of the user's additional reference."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path, old, new):
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    if old in text:
        file.write_text(text.replace(old, new), encoding="utf-8")


def append(path, marker, text):
    file = ROOT / path
    source = file.read_text(encoding="utf-8")
    if marker not in source:
        file.write_text(source.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


replace(
    "docs/PRODUCT_SPEC.md",
    "khối mặc định 10/11/12.",
    "cấp học và khối cấu hình tự do; ưu tiên THPT nhưng không khóa engine ở lớp 10–12.",
)
replace(
    "docs/PRODUCT_SPEC.md",
    "PPTX và văn bản; nhiều bộ bài THPT đại diện | Thêm DOCX, PDF, ảnh và OCR local",
    "PPTX, DOCX, PDF có text và văn bản; nhiều bài đại diện | Thêm ảnh/PDF scan OCR và trường hợp nhập nâng cao",
)
append(
    "docs/PRODUCT_SPEC.md",
    "## 10. Bổ sung",
    """
## 10. Bổ sung theo tài liệu góp ý mới

Pipeline: Import → Parse → Concept Model → Bilingual Engine → Lesson Intelligence → Teacher Review → Lesson Pack → Readiness Check. Lesson Intelligence chứa explanation VI/EN, easy EN, examples, teacher prompts, questions, VI Rescue, vocabulary, quiz/misconceptions và audio scripts/cache refs; nội dung có nguồn và trạng thái duyệt.

Trạng thái bài: DRAFT → REVIEW_REQUIRED → READY_TO_TEACH. Tiến độ chuẩn bị/audio quản lý riêng. Readiness kiểm tra nguồn, nội dung chưa duyệt, thiếu giải thích, voice/cache; quiz/network chỉ kiểm tra nếu giáo viên chọn quiz. Giáo viên có thể tiếp tục với warning có ghi nhận; override không tự biến nội dung thành đã duyệt và không bỏ kiểm tra file hỏng.

Glossary có UI thêm/sửa/xóa/khóa theo teacher + subject; CSV để mở rộng. ResponseProvider chuẩn hóa nguồn phản hồi; BiliCard là extension sau V1. Khi không có mạng vẫn dạy song ngữ, nhưng không thu đáp án điện thoại qua QR nếu thiếu LAN.

Tài liệu góp ý đề xuất V1 THCS–THPT, khác với yêu cầu trực tiếp ưu tiên THPT trước đó. Đã hỏi làm rõ; tạm giữ ưu tiên THPT và không hard-code cấp học/khối/môn.
""",
)
replace(
    "docs/ARCHITECTURE.md",
    "Import → Normalize → Review extraction → Segment → Protect terminology/symbols → Translate → Review bilingual → Prepare → Teach",
    "Import → Parse/Normalize → Concept Model → Bilingual Engine → Lesson Intelligence → Teacher Review → Lesson Pack → Readiness Check → Teach",
)
append(
    "docs/ARCHITECTURE.md",
    "## 10. Điều chỉnh sau",
    """
## 10. Điều chỉnh sau góp ý và thử M0

ResponseProvider chuẩn hóa participant/question/round/answer/submission/timestamp/source. Analytics độc lập transport; WebQuizProvider trước, BiliCard/camera sau V1. M0 có contract chạy được trong biliclass_m0/contracts.py.

Concept có đầy đủ trường Lesson Intelligence. Grade/education_level/subject cấu hình bằng dữ liệu; memory ít nhất teacher + subject. Trạng thái bài DRAFT/REVIEW_REQUIRED/READY_TO_TEACH tách khỏi job/cache. Readiness có warning và override ghi nhận.

Benchmark đầu tiên dùng Argos Translate 1.9/CTranslate2 INT8; chưa khóa model sản phẩm. Native loaders có lỗi đường dẫn tiếng Việt nên nạp SentencePiece và model bằng bytes do Python đọc. M0 dùng PyInstaller onedir để kiểm chứng đóng gói; Nuitka để xem xét sau. Qt Controls dùng Basic style cho UI tùy biến.

M2 nhập PPTX, DOCX, PDF text và TXT; M7 thêm OCR ảnh/PDF scan, edge cases và xuất deck. Chưa nhận kết quả local là nghiệm thu điện thoại/projector/laptop 8 GB.
""",
)
replace("docs/DATA_SCHEMA.md", "grade 10/11/12", "education_level/grade cấu hình tự do")
replace(
    "docs/DATA_SCHEMA.md",
    "`draft → needs_review → approved → preparing → prepared`",
    "Trạng thái bài: `DRAFT → REVIEW_REQUIRED → READY_TO_TEACH`. Tiến độ job chuẩn bị: `idle → preparing → prepared/failed`, tách riêng quyền duyệt nội dung.",
)
append(
    "docs/DATA_SCHEMA.md",
    "## 8. Trường bổ sung",
    """
## 8. Trường bổ sung từ góp ý

Concept bắt buộc hỗ trợ: explanation_vi, explanation_en, easy_en, examples, teacher_prompts, questions, vi_rescue, vocabulary, quiz_refs, misconceptions, audio_scripts, audio_cache_refs. Các trường có thể rỗng nhưng phải thể hiện thiếu nội dung trong readiness và assistant.

Memory key ít nhất gồm teacher_id + subject_id + source/target language + source text. Readiness lưu warning và override của giáo viên theo revision; override không đổi review state của item.
""",
)
replace("docs/BUILD_PLAN.md", "PPTX/text đa môn", "PPTX/DOCX/PDF text/TXT đa môn")
replace("docs/BUILD_PLAN.md", "DOCX/PDF/ảnh/OCR, kiểm chứng", "Ảnh/PDF scan OCR, edge cases, kiểm chứng")
replace("docs/TASKS.md", "PPTX/text importer", "PPTX/DOCX/PDF text/TXT importer")
replace("docs/TASKS.md", "DOCX/PDF/image/OCR, reviewer", "Image/PDF scan OCR và edge cases, reviewer")
append(
    "docs/DESIGN_SPEC.md",
    "## 10. Bổ sung",
    """
## 10. Bổ sung luồng duyệt và glossary

Glossary Management trong Cài đặt: môn/giáo viên, thuật ngữ VI/EN, thêm/sửa/xóa/khóa, nhập/xuất CSV sau. Builder có trạng thái DRAFT/REVIEW_REQUIRED/READY_TO_TEACH và nút duyệt rõ ràng. Readiness hiển thị nguồn, phần chưa duyệt, explanation, voice/cache; quiz và mạng chỉ khi được chọn. Warning cho phép tiếp tục có ghi nhận. Cấp học/khối là trường cấu hình, không chỉ dropdown 10–12.
""",
)
append(
    "refs/README.md",
    "review-input.txt",
    """
Tài liệu góp ý mới: `inputs/review-input.txt`, từ `C:/Users/Admin/.codex/attachments/bcf0e4f3-7594-499c-95b7-aab9c4698b30/Pasted text.txt`. Xem `docs/REVIEW_INTEGRATION.md` để phân biệt phần đã áp dụng và điểm phạm vi khác yêu cầu trực tiếp trước đó.
""",
)
print("Review integrated into project documents.")
