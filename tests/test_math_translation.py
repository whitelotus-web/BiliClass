from threading import Event

import pytest

from app.google_translation import Translator
from app.translation_terms import MATH_HEADINGS, TermPolicy


@pytest.mark.parametrize('vi,en', MATH_HEADINGS.items())
def test_geometry_headings_are_subject_scoped_and_exact_only(vi, en):
    assert TermPolicy('Toán').exact(vi.upper()) == en
    assert TermPolicy('Hóa học').exact(vi) is None
    assert TermPolicy('Toán').exact('Ví dụ: ' + vi) is None


def test_heading_correction_replaces_bad_cache_without_an_api_request(tmp_path):
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('Exact headings need no API'))
    translator.configure_terms('Toán', [])
    assert translator.translate(['CÁC TÍNH CHẤT THỪA NHẬN'], Event()) == ['Basic axioms']
    teacher = TermPolicy('Toán', [{'vi': 'các tính chất thừa nhận', 'en': 'Postulates', 'locked': True}])
    assert teacher.exact('CÁC TÍNH CHẤT THỪA NHẬN') == 'Postulates'


def test_numbered_activity_and_geometry_wording_keep_every_source_token():
    math = TermPolicy('Toán')
    assert math.exact('Hoạt động ⟦BLC0⟧') == 'Activity ⟦BLC0⟧'
    assert math.exact('PHIẾU HỌC TẬP SỐ ⟦BLC0⟧') == 'Worksheet ⟦BLC0⟧'
    assert math.exact('Trả lời:') == 'Answer:'
    assert math.exact('ĐỊNH NGHĨA') == 'Definition'
    assert math.exact('Ta có ⟦BLC0⟧ vị trí tương đối giữa đường và mặt :') == 'There are ⟦BLC0⟧ possible relative positions of a line and a plane:'
    assert math.exact('- Qua ⟦BLC0⟧ điểm phân biệt không thẳng hàng.') == '- Through ⟦BLC0⟧ distinct, noncollinear points.'
    assert math.exact('+ Đường nằm trong mặt (vô số điểm chung)') == '+ The line lies in the plane (infinitely many common points)'
    assert math.exact('Vô số.') == 'Infinitely many.'
    assert math.exact('Mặt nước và thành bể giao nhau.') is None
    assert TermPolicy('Vật lý').exact('+ Đường nằm trong mặt (vô số điểm chung)') is None
    assert math.postprocess('Khối rubik có bốn mặt.', "A Rubik's Cube has four faces.") == "A Rubik's puzzle has four faces."
    assert math.postprocess('A nằm trên P.', 'A is above P.') == 'A lies on P.'
    assert math.postprocess('S ở phía trên P.', 'S is above P.') == 'S is above P.'
    assert math.postprocess('đã học ở lớp ⟦BLC0⟧', 'learned about in ⟦BLC0⟧ grade') == 'learned about in Grade ⟦BLC0⟧'
    teacher = TermPolicy('Toán', [{'vi': 'khối rubik', 'en': 'Rubik cube', 'locked': True}])
    assert teacher.postprocess('Khối rubik có bốn mặt.', 'Rubik cube') == 'Rubik cube'


def test_center_clause_preserves_both_identifiers_and_their_distinct_roles():
    from app.math_translation import exact

    assert exact('⟦BLC0⟧ với ⟦BLC1⟧ là tâm hình bình hành ⟦BLC2⟧.') == (
        '⟦BLC0⟧, where ⟦BLC1⟧ is the center of the parallelogram ⟦BLC2⟧.')
    assert exact('⟦BLC0⟧ với ⟦BLC1⟧ là tâm hình bình hành ⟦BLC2⟧⟦BLC3⟧').endswith('⟦BLC2⟧⟦BLC3⟧')
    assert exact('⟦BLC0⟧ với ⟦BLC1⟧ là trung điểm ⟦BLC2⟧') == '⟦BLC0⟧, where ⟦BLC1⟧ is the midpoint of ⟦BLC2⟧'
    assert exact('+ Một mặt đáy là tứ giác ABCD.') == '+ The base is the quadrilateral ABCD.'
