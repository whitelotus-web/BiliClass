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
