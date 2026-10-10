from PySide6.QtCore import QLocale

from app.school_subjects import subject_options


def test_subjects_use_vietnamese_alphabet_with_other_last_on_an_english_computer():
    previous = QLocale()
    try:
        QLocale.setDefault(QLocale("en_US"))
        options = subject_options()
        assert options == list(dict.fromkeys(options))
        assert options[0] == "Âm nhạc" and options[-1] == "Khác"
        # Unicode/English sorting puts Đ after V and orders Ngữ before Ngoại.
        for first, second in (("Công nghệ", "Đạo đức"), ("Đạo đức", "Địa lí"),
                              ("Địa lí", "Giáo dục công dân"), ("Ngoại ngữ 2", "Ngữ văn")):
            assert options.index(first) < options.index(second)
        assert subject_options() == options
    finally:
        QLocale.setDefault(previous)
