"""Design-only resources and age/subject guidance for the four-format workflow."""
import json
from functools import lru_cache

from .paths import RESOURCE_ROOT


@lru_cache(maxsize=1)
def reference_catalog():
    data = json.loads((RESOURCE_ROOT / "assets/templates/reference_library.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("content_policy") != "design_only":
        raise ValueError("Bộ mẫu thiết kế không hợp lệ.")
    return data["templates"]


def reference_asset(preset, *, role=None, conversion_format=None):
    item = reference_catalog().get(preset)
    if item is None:
        raise ValueError("Mẫu bài giảng không hợp lệ.")
    if conversion_format is not None:
        name = item["language_previews"].get(conversion_format)
    elif role is not None:
        name = next((layout["preview"] for layout in item["layouts"] if layout["id"] == role), None)
    else:
        name = item["pptx"]
    if not name:
        raise ValueError("Bố cục xem trước không hợp lệ.")
    root = RESOURCE_ROOT / "assets/templates"
    path = root / name
    if path.resolve().is_relative_to(root.resolve()) and path.is_file():
        return path
    raise ValueError("Thiếu tài nguyên mẫu BiliClass. Cập nhật lại ứng dụng.")


def audience_guidance(config):
    try:
        grade = int(config.get("grade", ""))
    except (TypeError, ValueError):
        grade = 0
    if 1 <= grade <= 2:
        age = "Tiểu học, lớp 1–2: chữ lớn khoảng 28–36 pt, một ý trong mỗi vùng; English dùng từ quen thuộc và câu rất ngắn."
    elif 3 <= grade <= 5:
        age = "Tiểu học, lớp 3–5: chữ khoảng 24–32 pt, hình nguồn rõ; English câu ngắn, tăng thuật ngữ vừa đủ theo nguồn."
    elif 6 <= grade <= 9:
        age = "THCS, lớp 6–9: chữ khoảng 22–30 pt, cân đối chữ/hình; English giải thích rõ, thuật ngữ đúng môn, tránh nâng cao ngoài nguồn."
    elif 10 <= grade <= 12:
        age = "THPT, lớp 10–12: chữ khoảng 20–28 pt, đồ thị/công thức dễ đọc; English chuẩn chuyên ngành theo nội dung nguồn."
    else:
        age = "Dùng đúng cấp/khối giáo viên cung cấp; nếu thiếu thì ghi CHECK, không mặc định THPT hoặc tự đoán độ tuổi."
    return """THÍCH ỨNG THEO CẤP HỌC VÀ KHỐI LỚP
- """ + age + """
- Khoảng chữ trên là mục tiêu cho mẫu mới, không phải giới hạn cứng. Tiêu đề lớn hơn, chú thích đủ rõ.
- Khi giữ PPTX gốc, ưu tiên font/định dạng gốc; chỉ chỉnh có kiểm soát khi bản dịch tràn.
- Điều chỉnh cách diễn đạt English và mật độ bố cục, giữ đủ kiến thức/câu Việt và kiểu chuyển đổi đã chọn.
- Không rút gọn, nâng cao kiến thức hoặc tự tách/thêm slide PPTX để đạt cỡ chữ. Không đủ chỗ thì ghi CHECK.
"""


SUBJECT_RULES = [
    (("toán",), "Giữ dấu phép toán, giả thiết, điều kiện, số mũ/chỉ số, bước chứng minh và lời giải; hình, kích thước, đơn vị và đáp án phải khớp nhau."),
    (("vật lí", "vật lý"), "Giữ đại lượng, vectơ, đơn vị, trục đồ thị, điều kiện áp dụng và ký hiệu; không suy diễn chuyển động/thí nghiệm từ hình thiếu dữ liệu."),
    (("hóa",), "Giữ công thức chất, hóa trị, chỉ số, hệ số phương trình, điện tích, điều kiện phản ứng và cảnh báo thí nghiệm trong nguồn."),
    (("sinh",), "Giữ tên loài, cấu trúc, cấp tổ chức và nhãn sơ đồ; không tự thêm quy trình hoặc cơ chế sinh học ngoài nguồn."),
    (("lịch sử", "địa lí", "địa lý"), "Giữ mốc thời gian, địa danh, tên riêng, trích dẫn, bản đồ, chú giải, tỷ lệ và số liệu; không tự sửa ranh giới hay bổ sung sự kiện."),
    (("ngữ văn", "tiếng việt", "tiếng dân tộc"), "Giữ nguyên ngữ liệu, tác giả, tác phẩm và dẫn chứng trong phần Việt; bản dịch phân biệt lời trích, lời giảng và bài tập. Không tự thêm phân tích ngoài nguồn."),
    (("ngoại ngữ", "tiếng anh"), "Phân biệt ngôn ngữ đang được học với ngôn ngữ lời hướng dẫn. Giữ ngữ liệu, phiên âm, ký hiệu, mẫu câu và yêu cầu bài tập; tránh dịch làm mất mục tiêu của bài."),
    (("tin học", "công nghệ", "stem"), "Giữ nguyên mã nguồn, cú pháp, tên biến, lệnh và dữ liệu; chỉ dịch lời giải thích/chú thích phù hợp. Bảo toàn sơ đồ và thứ tự thao tác."),
    (("âm nhạc", "mĩ thuật", "mỹ thuật", "nghệ thuật"), "Giữ bản nhạc, nhịp/phách, ký hiệu, màu sắc tác phẩm, tác giả và nhãn kỹ thuật; không thay hình tác phẩm bằng ảnh minh họa khác."),
    (("thể chất", "quốc phòng"), "Giữ trình tự động tác, quy tắc an toàn, khẩu lệnh và hình nguồn; không tự tạo hướng dẫn vận động hoặc thao tác còn thiếu."),
    (("đạo đức", "công dân", "pháp luật", "trải nghiệm", "địa phương"), "Giữ tình huống, nguồn trích dẫn, địa phương và yêu cầu hoạt động; không tự thêm quy định, phán xét hoặc đáp án ngoài tài liệu."),
    (("khoa học", "tự nhiên"), "Giữ hiện tượng, số liệu, điều kiện quan sát, quy trình và nhãn hình; bài tích hợp phải dùng thuật ngữ đúng từng lĩnh vực, không ép thành một môn khác."),
]


def subject_guidance(subject):
    key = str(subject).strip().casefold()
    rules = list(dict.fromkeys(rule for names, rule in SUBJECT_RULES if any(name in key for name in names)))
    return "QUY TẮC CHUYÊN MÔN CHO «" + str(subject) + "»\n- " + "\n- ".join(rules or [
        "Dùng thuật ngữ đúng ngữ cảnh tài liệu và môn giáo viên cung cấp; giữ ký hiệu, dữ kiện, dẫn chứng và yêu cầu nguồn. Không đủ căn cứ thì ghi CHECK."]) + "\n"


STYLE_RULES = {
    "standard": """PHONG CÁCH CLASSROOM – CHUẨN LỚP HỌC
- Phân cấp tiêu đề/kiến thức rõ, ít trang trí. Khái niệm hoặc ý trọng tâm trong vùng xanh nhạt, hình nguồn bên cạnh khi phù hợp.
- Trang tên bài thoáng; phần kiến thức giữ định nghĩa; hình/chú thích gần nhau; ví dụ tách đề, dữ kiện, các bước và kết luận theo nguồn.
- Giữ chỗ cho bảng, trích dẫn hoặc công thức khi tài liệu có; không ép bài Văn/Sử thành bài công thức.
""",
    "visual": """PHONG CÁCH VISUAL – TRỰC QUAN
- Ưu tiên hình/đồ thị/sơ đồ/bản đồ/tác phẩm nguồn, khoảng 45–65% vùng nội dung khi phù hợp; chú thích gần đúng bộ phận.
- Không che trục, chú giải, nhãn, số liệu; không bóp méo hoặc cắt mất chi tiết. Nhiều hình sắp theo thứ tự nguồn.
- Không có hình thì dùng chữ/bảng rõ ràng, không tự tạo sơ đồ, hình AI/Internet hoặc quan hệ mới để lấp chỗ.
""",
    "practice": """PHONG CÁCH PRACTICE – LUYỆN TẬP & TƯƠNG TÁC
- Câu hỏi/nhiệm vụ và dữ kiện là trọng tâm; lời giải/bước thực hiện chỉ dùng khi có trong nguồn.
- Phân biệt đề và đáp án. Giữ trình tự tiết lộ đáp án gốc; nếu chỉ có đề, không tự tạo lời giải hoặc hình làm lộ đáp án.
- Khái niệm vẫn là khái niệm, không biến tất cả slide thành trò chơi/câu hỏi. Hoạt động phù hợp môn và độ tuổi.
- Appear/Fade từng bước khi công cụ thực sự hỗ trợ; không gọi nút/trigger là tương tác nếu chưa có hành động thật.
""",
}


def design_guidance(preset):
    item = reference_catalog()[preset]
    colors = item["colors"]
    return f"""MẪU THIẾT KẾ TRUNG TÍNH – {item['id']}
- mau-biliclass.pptx chỉ chứa khung chỉnh sửa được; không phải nguồn kiến thức. Không chép nguyên bốn slide mẫu thành bài.
- Thay [LESSON_TITLE], [SUBJECT], [GRADE], [SOURCE_*] bằng dữ liệu tương ứng của giáo viên; bỏ vùng không dùng.
- Không để lại nhãn/placeholder, Speaker Notes, ví dụ, hình, công thức, đáp án hoặc tên môn của demo trong kết quả.
- Chỉ dùng tài liệu giáo viên làm nguồn nội dung. Thiếu dữ kiện không lấy từ mẫu hay từ môn/cấp khác, ghi CHECK.
- Nền {colors['background']}; tiêu đề {colors['heading']}; nhấn {colors['accent']}; chữ {colors['text']};
  vùng nhạt {colors['soft']}; đường phân cách {colors['border']}; font {item['font']}, 16:9 cho mẫu mới.
- Chọn vai trò từng slide theo nguồn: TITLE, CONCEPT, VISUAL, EXAMPLE, PRACTICE, SUMMARY.
  File mẫu có bốn bố cục (slide 1–4: tên bài, kiến thức, hình/chú thích, luyện tập); ví dụ/tổng kết dùng bố cục phù hợp.
- Khung mẫu không quyết định ngôn ngữ: sắp xếp lại chữ theo đúng kiểu đã chọn; không áp đặt hai cột cho kiểu khác.
- Giữ đủ số lượng/thứ tự slide PPTX. Word/PDF/ảnh chia slide theo trình tự nguồn. Không bắt buộc mọi bài có đủ các vai trò.
- Dựng lại theo mẫu có thể mất hiệu ứng/trigger nguồn; chỉ báo đã giữ khi đã kiểm chứng, nêu rõ phần không tái tạo được.
{STYLE_RULES[preset]}"""
