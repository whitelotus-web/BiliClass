import pytest

from app.word_selection import TextSelection


def paragraph(identity, text, editable=True):
    return dict(id=identity, text=text, editable=editable)


def utf16(text):
    return len(text.encode('utf-16-le')) // 2


def test_continuous_selection_spans_disjoint_source_paragraphs_and_keeps_utf16_offsets():
    rows = [paragraph('p0', 'Bài học'), paragraph('p1', '😀 Vận tốc 12 m/s.'), paragraph('p2', 'Gia tốc 2 m/s².')]
    selection = TextSelection(rows)
    start = selection.text.index('Vận tốc')
    end = selection.text.index('Gia tốc') + len('Gia tốc')
    regions, skipped = selection.ranges(utf16(selection.text[:start]), utf16(selection.text[:end]))
    assert regions == [dict(paragraph='p1', start=2, end=len(rows[1]['text'])), dict(paragraph='p2', start=0, end=7)]
    assert skipped == 0
    assert rows[1]['text'][regions[0]['start']:] == 'Vận tốc 12 m/s.'


def test_qt_line_ending_normalization_maps_back_to_original_character_positions():
    original = 'Dòng một\r\nDòng hai\rDòng ba'
    selection = TextSelection([paragraph('p0', original)])
    assert selection.text == 'Dòng một\nDòng hai\nDòng ba'
    start = selection.text.index('Dòng hai')
    regions, _ = selection.ranges(start, len(selection.text))
    assert original[regions[0]['start']:regions[0]['end']] == 'Dòng hai\rDòng ba'


def test_locked_blocks_are_reported_and_never_submitted_as_translation_ranges():
    selection = TextSelection([paragraph('p0', 'Đoạn một'), paragraph('p1', '[Hình minh họa]', False), paragraph('p2', 'Đoạn hai')])
    regions, skipped = selection.ranges(0, utf16(selection.text))
    assert [row['paragraph'] for row in regions] == ['p0', 'p2'] and skipped == 1
    start = selection.text.index('[Hình')
    with pytest.raises(ValueError, match='chưa có phần chữ'):
        selection.ranges(start, start + len('[Hình minh họa]'))


@pytest.mark.parametrize('start,end', [(1, 2), (0, 999), (3, 2), (0, 0)])
def test_invalid_or_split_surrogate_selections_cannot_change_a_document(start, end):
    selection = TextSelection([paragraph('p0', '😀 Tiếng Việt')])
    with pytest.raises(ValueError):
        selection.ranges(start, end)


def test_paragraph_separators_are_not_new_translation_regions():
    selection = TextSelection([paragraph('p0', 'Một'), paragraph('p1', 'Hai')])
    with pytest.raises(ValueError, match='chưa có phần chữ'):
        selection.ranges(3, 5)
