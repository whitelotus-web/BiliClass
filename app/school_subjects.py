"""Conversion subjects from the general education curriculum; see docs/SCHOOL_SUBJECTS.md."""

from functools import cmp_to_key

from PySide6.QtCore import QCollator, QLocale

OTHER_SUBJECT = "Khác"

# Combined list for primary, lower and upper secondary, including optional
# subjects and teaching activities. Teachers can use the component arts subjects
# separately; Tiếng Anh is a convenient name for the foreign-language subject.
CURRICULUM_SUBJECTS = (
    "Âm nhạc", "Công nghệ", "Đạo đức", "Địa lí", "Giáo dục công dân",
    "Giáo dục kinh tế và pháp luật", "Giáo dục quốc phòng và an ninh", "Giáo dục thể chất",
    "Hóa học", "Hoạt động trải nghiệm", "Hoạt động trải nghiệm, hướng nghiệp",
    "Khoa học", "Khoa học tự nhiên", "Lịch sử", "Lịch sử và Địa lí", "Mĩ thuật",
    "Nghệ thuật", "Ngoại ngữ 1", "Ngoại ngữ 2", "Ngữ văn", "Nội dung giáo dục của địa phương",
    "Sinh học", "Tiếng dân tộc thiểu số", "Tiếng Việt", "Tin học", "Tin học và Công nghệ",
    "Toán", "Tự nhiên và Xã hội", "Vật lý",
)


def subject_options():
    """Use Vietnamese collation regardless of the computer's display language."""
    collator = QCollator(QLocale("vi_VN"))
    return sorted((*CURRICULUM_SUBJECTS, "Tiếng Anh"), key=cmp_to_key(collator.compare)) + [OTHER_SUBJECT]
