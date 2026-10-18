from app.download_names import presentation_suffix, suggestion


def test_export_names_describe_the_actual_language_and_selected_voice(tmp_path):
    lesson = {'title': 'Bài 1. Hệ điều hành', 'conversion_format': 'parallel_columns'}
    assert suggestion(tmp_path, lesson['title'], presentation_suffix(lesson), 'pptx').name == 'Bài 1. Hệ điều hành (Song ngữ Việt–Anh).pptx'
    lesson['conversion_format'] = 'english_only'
    assert presentation_suffix(lesson) == 'Tiếng Anh'
    lesson['narration'] = {'mode': 'both', 'voice': 'vieneu:Mai Anh', 'rate': 0}
    assert presentation_suffix(lesson, True) == 'Có giọng Việt–Anh · Mai Anh · 100%'
    lesson['voice_only'] = True
    assert presentation_suffix(lesson) == 'Nguyên bản · Không giọng'
