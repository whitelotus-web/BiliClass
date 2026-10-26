import pytest

from app.word_selection import TextSelection, complete_word_ranges, review_groups


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


@pytest.mark.parametrize('text,fragment,expected', [
    ('Nguyễn Văn An', 'Ng', 'Nguyễn'),
    ('😀 Nguyễn Văn An', 'uyễ', 'Nguyễn'),
    ('Nguye\u0302\u0303n Văn An', 'ye\u0302', 'Nguye\u0302\u0303n'),
    ('Bộ ESP32 đang hoạt động.', 'SP3', 'ESP32'),
    ('Đây là câu một. Đây là câu hai.', 'câu mộ', 'câu một'),
    ('Giữ nguyên câu sau.', 'Giữ nguyên', 'Giữ nguyên'),
])
def test_clipped_words_are_completed_without_extending_sentences(text, fragment, expected):
    rows = [paragraph('p0', text)]
    selected = dict(paragraph='p0', start=text.index(fragment), end=text.index(fragment) + len(fragment))
    before = selected.copy()
    region = complete_word_ranges(rows, [selected])[0]
    assert text[region['start']:region['end']] == expected
    assert selected == before and rows[0]['text'] == text


def test_completion_keeps_utf16_offsets_after_emoji():
    text = '😀 Nguyễn Văn An'
    selection = TextSelection([paragraph('p0', text)])
    regions, _ = selection.ranges(utf16(text[:2]), utf16(text[:4]))
    full = complete_word_ranges([paragraph('p0', text)], regions)
    assert full == [dict(paragraph='p0', start=2, end=8)]


def test_review_groups_merge_adjacent_paragraphs_and_extend_in_source_order():
    paragraphs = [paragraph('p' + str(index), f'Đoạn {index + 1}') for index in range(7)]

    def region(index):
        text = paragraphs[index]['text']
        return dict(id=f'p{index}:0:{len(text)}', paragraph=f'p{index}', start=0, end=len(text), vi=text)

    first = review_groups(paragraphs, [region(index) for index in range(5)])
    assert len(first) == 1 and first[0]['vi'] == '\n'.join(row['text'] for row in paragraphs[:5])
    extended = review_groups(paragraphs, [region(index) for index in range(7)])
    assert len(extended) == 1 and len(extended[0]['members']) == 7
    disjoint = review_groups(paragraphs, [region(index) for index in (0, 2, 3, 4)])
    assert len(disjoint) == 2 and [row['paragraph'] for row in disjoint[1]['members']] == ['p2', 'p3', 'p4']
