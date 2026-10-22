import hashlib
import re
from threading import Event

import pytest

from app.chemical_notation import formula_spans, only_notation, signature
from app.google_translation import KeyStore, Translator, protected_html, unprotect
from app.translation_terms import TermPolicy


@pytest.mark.parametrize('text', ['CO2', 'HCN', 'Al4C3', 'C12H22O11', 'HCOONa', 'NaCl', 'Na+',
    'CH3COOH', 'Ca(OH)2', 'C-H', 'C=O', 'CH=O', 'C 6 H 12 O 6', 'CO⟦BLC0⟧', 'CN⟦BLC1⟧', 'Al⟦BLC3⟧C⟦BLC4⟧'])
def test_complete_formulas_include_native_subscripts_and_element_case(text):
    assert [m.group() for m in formula_spans(text)] == [text]
    assert only_notation('A. '+text)


def test_ordinary_words_are_not_mistaken_for_chemical_formulas():
    assert not formula_spans('Alcohol and Amine, molecular formula, CHINH PHỤC, Section 2')
    assert not only_notation('Chọn HCN và CH4')
    assert not formula_spans('⟦BLC0⟧'), 'Do not match letters inside a native token'


def test_google_cannot_translate_or_drop_atoms_inside_native_formula_locks():
    source='carbon dioxide (CO⟦BLC0⟧), cyanide (CN⟦BLC1⟧), Al⟦BLC2⟧C⟦BLC3⟧; HCN'
    payload,locks=protected_html(source,chemistry=True)
    changed=payload.replace('CO⟦BLC0⟧','2').replace('HCN','Rectangle').replace('CN⟦BLC1⟧','-')
    assert unprotect(changed,locks) == source
    assert len(locks) == 4, 'Lock each complete formula, not just its numbers'
    assert 'CO⟦BLC0⟧' not in payload and 'HCN' not in payload
    payload,locks=protected_html('carbon dioxide (CO⟦BLC0⟧)',chemistry=True)
    assert payload.startswith('carbon dioxide (<span') and payload.endswith('</span>)')
    assert unprotect(payload,locks) == 'carbon dioxide (CO⟦BLC0⟧)'


def test_invented_compounds_are_rejected_before_caching(tmp_path):
    KeyStore(tmp_path).add('AIza'+'x'*35)
    translator=Translator(tmp_path,transport=lambda rows,*_:[row+' and C₄⁻' for row in rows])
    translator.configure_terms('Hóa học',[])
    from app.google_translation import TranslationProblem
    with pytest.raises(TranslationProblem,match='công thức hóa học'):
        translator.translate(['Chất có công thức CO2'],Event())
    assert signature('III. FORMULAS IN ORGANIC COMPOUNDS: CO₂') == signature('CO2')
    assert signature("LET'S CONQUER C⟦BLC0⟧ CUP!!") == signature('C⟦BLC0⟧')
    assert signature('(CO); (CO⟦BLC0⟧), (CN⟦BLC1⟧)') == signature('( CO ); ( CO⟦BLC0⟧ ), ( CN⟦BLC1⟧ )')


def test_formula_lock_does_not_match_prefixes_inside_words():
    payload,locks=protected_html('CO; COMPOUNDS',chemistry=True)
    assert locks == ['CO'] and payload.endswith('COMPOUNDS')


@pytest.mark.parametrize('unit', ['cm-1', 'cm -1', 'cm⁻¹', 'cm^{-1}', 'cm⟦BLC1⟧'])
def test_inverse_centimeter_units_are_immutable_including_native_exponent_tokens(unit):
    payload, locks = protected_html('Số sóng 3337 '+unit, chemistry=True)
    assert any(value.endswith(unit) for value in locks), locks
    # A translation engine changing the span contents must not remove cm or duplicate its exponent.
    changed = re.sub(r'(?<=>)(?:3337[^<]*|cm[^<]*)(?=</span>)', 'wrong', payload)
    assert unprotect(changed, locks) == 'Số sóng 3337 '+unit


def test_chemistry_nouns_keep_sentence_grammar_and_english_class_names():
    policy=TermPolicy('Hoá học')
    assert not policy.matches('công thức phân tử và nhóm chức trong phân tử')
    assert policy.exact('Nhóm chức') == 'functional group'
    assert policy.exact('liên kết cộng hoá trị') == 'covalent bond'
    assert policy.matches('Liên kết hóa học chủ yếu là liên kết cộng hoá trị') == {'cộng hóa trị':'covalent'}
    assert policy.exact('Alcohol') == 'Alcohol'
    assert policy.exact('Iron') == 'Iron'
    assert policy.exact('Sulfuric acid') == 'Sulfuric acid'
    assert policy.exact('Axit sunfuric') == 'sulfuric acid'
    assert policy.exact('Nhôm') == 'aluminium'
    assert not policy.matches('giá trị của đồng tiền'), 'Short legacy names remain exact-only'
    teacher=TermPolicy('Hóa học',[dict(vi='phân tử',en='custom molecule',locked=True)])
    assert teacher.matches('trong phân tử') == {'phân tử':'custom molecule'}


def test_standalone_chemical_labels_and_options_require_no_api(tmp_path):
    translator=Translator(tmp_path,transport=lambda *_:pytest.fail('No API needed for a formula or English name'))
    translator.configure_terms('Hóa học',[])
    assert translator.translate(['Alcohol','A. HCN','C6H12O6, C12H22O11, C2H2'],Event()) == [
        'Alcohol','A. HCN','C6H12O6, C12H22O11, C2H2']


def test_only_chemistry_replaces_legacy_formula_translation_cache(tmp_path):
    source='Chất HCN và CO⟦BLC0⟧'
    legacy=hashlib.sha256(('google-nmt-context-v3|vi|en|'+source).encode()).hexdigest()
    calls=[]
    KeyStore(tmp_path).add('AIza'+'x'*35)
    translator=Translator(tmp_path,transport=lambda rows,*_:calls.extend(rows) or [r.replace('Chất','Substance').replace(' và ',' and ') for r in rows])
    translator.store.cache(legacy,'Bad Rectangle and 2')
    translator.configure_terms('Hóa học',[])
    assert translator.translate([source],Event()) == ['Substance HCN and CO⟦BLC0⟧']
    assert len(calls)==1
    assert translator.translate([source],Event()) == ['Substance HCN and CO⟦BLC0⟧'] and len(calls)==1
    translator.configure_terms('Toán',[])
    assert translator.translate([source],Event()) == ['Bad Rectangle and 2'] and len(calls)==1
