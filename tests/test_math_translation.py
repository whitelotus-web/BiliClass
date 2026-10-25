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
    assert translator.translate(['CÁC TÍNH CHẤT THỪA NHẬN'], Event()) == ['BASIC AXIOMS']
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


@pytest.mark.parametrize('source,target', [
    ('GÓC LƯỢNG GIÁC','TRIGONOMETRIC ANGLE'),
    ('ĐƯỜNG TRÒN LƯỢNG GIÁC','UNIT CIRCLE'),
    ('GIÁ TRỊ LƯỢNG GIÁC','TRIGONOMETRIC VALUE'),
    ('HỆ THỨC CHASLES',"CHASLES' RELATION"),
    ('GÓC BẸT','STRAIGHT ANGLE'),
    ('SỐ ĐO CỦA GÓC LƯỢNG GIÁC','MEASURE OF A TRIGONOMETRIC ANGLE'),
    ('HỆ THỨC CƠ BẢN GIỮA CÁC GIÁ TRỊ LƯỢNG GIÁC','FUNDAMENTAL TRIGONOMETRIC IDENTITIES')])
def test_trigonometry_headings_bypass_bad_cached_machine_translations(tmp_path, source, target):
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('Exact headings need no API'))
    translator.configure_terms('Toán', [])
    assert translator.translate([source], Event()) == [target]


def test_geometry_ray_is_not_a_pulse_and_teacher_override_wins():
    math = TermPolicy('Toán')
    assert math.postprocess('Với ba tia tùy ý', 'Given three arbitrary pulses') == 'Given three arbitrary rays'
    physics = TermPolicy('Vật lý')
    assert physics.postprocess('Tia xung', 'A pulse') == 'A pulse'
    teacher = TermPolicy('Toán', [{'vi':'góc lượng giác','en':'Directed angle','locked':True}])
    assert teacher.exact('GÓC LƯỢNG GIÁC') == 'Directed angle'


def test_angle_measure_prefix_is_an_immutable_math_label():
    from app.google_translation import protected_html, unprotect

    text='Do đó sđ⟦BLC0⟧ + sđ⟦BLC1⟧ = sđ⟦BLC2⟧.'
    policy=TermPolicy('Toán')
    payload, locks=protected_html(text, policy.matches(text))
    assert locks.count('sđ') == 3
    assert unprotect(payload.replace('Do đó','Therefore'),locks).count('sđ') == 3
    assert TermPolicy('Vật lý').matches(text) == {}


def test_mixed_native_angle_formula_keeps_operators_and_measure_prefix_without_api(tmp_path):
    translator=Translator(tmp_path,transport=lambda *_: pytest.fail('Equation connective needs no API'))
    translator.configure_terms('Toán',[])
    source='Do đó ⟦BLC0⟧+ sđ⟦BLC1⟧ = sđ⟦BLC2⟧+⟦BLC3⟧.'
    assert translator.translate([source],Event()) == ['Therefore, ⟦BLC0⟧+ sđ⟦BLC1⟧ = sđ⟦BLC2⟧+⟦BLC3⟧.']
    # The equality sign can itself be inside an immutable OMML token.
    native='Do đó ⟦BLC0⟧ sđ⟦BLC1⟧ ⟦BLC2⟧ sđ⟦BLC3⟧.'
    assert translator.translate([native],Event()) == ['Therefore, ⟦BLC0⟧ sđ⟦BLC1⟧ ⟦BLC2⟧ sđ⟦BLC3⟧.']
    assert TermPolicy('Toán').exact('Do đó ta có một góc bằng ⟦BLC0⟧.') is None


def test_full_turn_angle_is_not_circumference_in_radians():
    policy=TermPolicy('Toán')
    assert policy.exact('Mặt khác, đường tròn có số đo bằng ⟦BLC0⟧ nên ta có ⟦BLC1⟧=⟦BLC2⟧ rad.') == (
        'On the other hand, a full turn measures ⟦BLC0⟧, so ⟦BLC1⟧=⟦BLC2⟧ rad.')
    assert policy.exact('Do đường tròn có độ dài là ⟦BLC0⟧ nên nó có số đo ⟦BLC1⟧ rad.') == (
        'Since the circumference of the circle is ⟦BLC0⟧, a full turn measures ⟦BLC1⟧ rad.')
    assert policy.exact('Mặt khác, đường tròn có số đo bằng ⟦BLC0⟧ nên ta có thêm một câu khác.') is None
    assert policy.exact('Do đường tròn có độ dài là ⟦BLC0⟧ nên nó có số đo ⟦BLC1⟧.') == (
        'Since the circumference of the circle is ⟦BLC0⟧, a full turn measures ⟦BLC1⟧.')


def test_plural_glossary_keeps_singular_and_plural_in_the_same_sentence():
    from app.google_translation import protected_html, unprotect

    policy = TermPolicy('Toán')
    source = 'Cho một góc lượng giác, xác định số đo của ba góc lượng giác và các góc hình học.'
    matches = policy.matches(source)
    assert matches['góc lượng giác'] == 'trigonometric angle'
    assert matches['ba góc lượng giác'] == 'three trigonometric angles'
    assert matches['các góc hình học'] == 'geometric angles'
    html, locks = protected_html(source, matches)
    result = unprotect(html, locks)
    assert 'một trigonometric angle,' in result
    assert 'three trigonometric angles' in result
    assert 'geometric angles' in result
    assert 'ba trigonometric angle' not in result
    assert TermPolicy('Vật lý').matches('ba góc lượng giác') == {}
    teacher = TermPolicy('Toán', [{'vi': 'góc lượng giác', 'en': 'directed angle', 'locked': True}])
    assert teacher.matches('ba góc lượng giác') == {'góc lượng giác': 'directed angle'}


@pytest.mark.parametrize('source,target', [
    ('12 giờ 10 phút', '12 h 10 min'),
    ('⟦BLC0⟧ giờ ⟦BLC1⟧ phút', '⟦BLC0⟧ h ⟦BLC1⟧ min'),
    ('Một cung của đường tròn bán kính R và có số đo α  thì có độ là l=R.α',
     'An arc of a circle with radius R and measure α has length l=R.α'),
    ('Một cung của đường tròn bán kính ⟦BLC0⟧ và có số đo ⟦BLC1⟧ thì có độ dài là ⟦BLC2⟧.',
     'An arc of a circle with radius ⟦BLC0⟧ and measure ⟦BLC1⟧ has length ⟦BLC2⟧.'),
    ('Số đo của các góc lượng giác tia đầu ⟦BLC0⟧, tia cuối ⟦BLC1⟧ là',
     'The measures of trigonometric angles with initial ray ⟦BLC0⟧ and terminal ray ⟦BLC1⟧ are')])
def test_time_units_and_arc_length_are_not_lost_or_reinterpreted(tmp_path, source, target):
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('Exact clause needs no API'))
    translator.configure_terms('Toán', [])
    assert translator.translate([source], Event()) == [target]
    assert TermPolicy('Toán').exact('Một cung của đường tròn có độ là 30 độ.') is None
