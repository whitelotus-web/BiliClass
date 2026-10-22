from app.picture_prose import draft_line, paragraphs


def test_draft_reader_requires_agreement_on_counts_and_rejects_formulas():
    row = dict(text='Trạm ở trong góc 45° so với mặt đất.', alternate='Trạm ở trong góc 45? so với mặt đất.',
               confidence=.98, probability=.90, verified=False)
    assert draft_line(row) == 'Trạm ở trong góc 45° so với mặt đất.'
    assert draft_line({**row, 'alternate': 'Trạm ở trong góc 46? so với mặt đất.'}) is None
    assert draft_line({**row, 'alternate': 'Một nhận định khác về chuyển động.'}) is None
    assert draft_line({**row, 'probability': .6}) is None
    assert draft_line({**row, 'text': 'Vận tốc là v = 45 mét trên giây.'}) is None


def test_aligned_prose_is_joined_without_diagram_labels_or_uncertain_lines():
    rows = [dict(text='Một đoạn văn dài giải thích đường đi của trạm vũ trụ trong hình.',
                 confidence=.99, verified=True, points=[[.01, y], [.68, y], [.68, y+.04], [.01, y+.04]])
            for y in (.05, .11, .17, .23)]
    rows.append(dict(text='400 km', confidence=.99, verified=True,
                     points=[[.8, .2], [.95, .2], [.95, .24], [.8, .24]]))
    occurrence = dict(slide=2, shape_id=4, box=[20, 30, 1800, 500])
    blocks = paragraphs(rows, occurrence, 'fixture.png')
    assert len(blocks) == 1 and blocks[0]['draft']
    assert blocks[0]['line_indices'] == [0, 1, 2, 3]
    assert '400' not in blocks[0]['text']
    assert blocks[0]['region'][0] == 38
    rows[1]['verified'] = False
    assert not paragraphs(rows, occurrence, 'fixture.png')


def test_long_line_reader_splits_at_word_gap_instead_of_dropping_the_middle():
    from PIL import Image, ImageDraw

    from app.vietnamese_ocr import VietnameseReader

    image = Image.new('RGB', (1000, 40), 'white')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 10, 460, 30), fill='black')
    draw.rectangle((490, 10, 999, 30), fill='black')
    reader = object.__new__(VietnameseReader)
    widths = []

    def read(crop):
        widths.append(crop.width)
        return ('phần đầu' if len(widths) == 1 else 'phần cuối', .9)

    reader.read = read
    assert reader.read_line(image) == ('phần đầu phần cuối', .9)
    assert len(widths) == 2 and sum(widths) == 1000 and min(widths) > 400
