from threading import Event

import pytest

from app.google_translation import KeyStore, TranslationProblem, Translator


@pytest.mark.parametrize('direction, english', [('chiều quay ngược chiều kim đồng hồ', 'counterclockwise'),
                                              ('chiều quay của kim đồng hồ', 'clockwise')])
def test_clock_question_keeps_fraction_and_rotation_direction(direction, english):
    from app.translation_terms import TermPolicy

    text = f'Phải quay kim phút mấy phần của một vòng tròn theo {direction} để nó chỉ đúng số ⟦BLC0⟧?'
    translated = TermPolicy('Toán').exact(text)
    assert translated == f'Through what fraction of a full turn must the minute hand rotate {english} to point to ⟦BLC0⟧?'
    assert TermPolicy('Toán').exact('Giải') == 'Solution'


def test_exact_teacher_term_and_classroom_heading_need_no_api(tmp_path):
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('Local wording must not call Google'))
    translator.configure_terms('Vật lý', [{'vi': 'động năng', 'en': 'Kinetic energy', 'locked': True}])
    assert translator.translate(['động năng', 'VẬN DỤNG'], Event()) == ['Kinetic energy', 'APPLICATION']
    assert not translator.store.public()


@pytest.mark.parametrize('source,target', [('Bài 4:', 'Lesson 4:'), ('BÀI 12', 'LESSON 12'),
    ('Bai 4.1', 'Lesson 4.1'), ('Bài ⟦BLC0⟧:', 'Lesson ⟦BLC0⟧:'), ('Chương II', 'Chapter II')])
def test_numbered_lesson_heading_is_local_and_never_becomes_song(tmp_path, source, target):
    translator = Translator(tmp_path, transport=lambda *_:pytest.fail('Heading should not call API'))
    assert translator.translate([source], Event()) == [target]


def test_subject_defaults_aliases_and_teacher_priority():
    from app.translation_terms import TermPolicy

    physics = TermPolicy('Vật lí')
    assert physics.exact('công') == 'work'
    assert physics.matches('Tính độ dịch chuyển và vận tốc.') == {'độ dịch chuyển':'displacement', 'vận tốc':'velocity'}
    assert not physics.matches('Người công nhân')
    assert not TermPolicy('Tin học').matches('Tính độ dịch chuyển và vận tốc.')
    assert TermPolicy('Địa lí').exact('mật độ dân số') == 'population density'
    teacher = TermPolicy('Vật lý', [{'subject':'Vật lí','vi':'vận tốc','en':'custom velocity','locked':True},
                                  {'subject':'Tin học','vi':'vận tốc','en':'wrong subject','locked':True}])
    assert teacher.exact('vận tốc') == 'custom velocity'
    assert not TermPolicy('Âm nhạc').matches('Bài hát 4')


def test_recent_physics_titles_and_pendulum_terms_are_local_and_teacher_overridable(tmp_path):
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('Known physics terms need no API'))
    translator.configure_terms('Vật lý', [])
    assert translator.translate(['Định luật I Newton', 'Định luật 1 Newton', 'con lắc lò xo',
                                 'dao động điều hoà'], Event()) == [
        "Newton's first law", "Newton's first law", 'spring–mass oscillator', 'simple harmonic motion']
    translator.configure_terms('Vật lý', [{'vi':'con lắc lò xo','en':'spring pendulum','locked':True}])
    assert translator.translate(['con lắc lò xo'], Event()) == ['spring pendulum']


def test_contextual_title_protects_heading_and_subject_terms_before_api(tmp_path):
    KeyStore(tmp_path).add('AIza' + 'x'*35)
    seen = []

    def transport(texts, *_):
        seen.extend(texts)
        return texts  # Protected words are restored without relying on API wording.

    translator = Translator(tmp_path, transport=transport)
    translator.configure_terms('Vật lý', [])
    assert translator.translate(['Bài 4: Độ dịch chuyển'], Event()) == ['Lesson 4: displacement']
    assert len(seen) == 1 and 'Bài' not in seen[0] and 'Độ dịch chuyển' not in seen[0]


def test_term_cache_isolated_by_subject_and_teacher_wording(tmp_path):
    KeyStore(tmp_path).add('AIza' + 'x'*35)
    calls = []

    def transport(texts, *_):
        calls.extend(texts)
        return [text.replace('Khái niệm', 'The concept') for text in texts]

    translator = Translator(tmp_path, transport=transport)
    for subject, target in [('Vật lý', 'force'), ('Ngữ văn', 'strength'), ('Ngữ văn', 'power')]:
        translator.configure_terms(subject, [{'vi': 'lực', 'en': target, 'locked': True}])
        result = translator.translate(['Khái niệm lực'], Event())
        assert result == ['The concept ' + target]
        assert translator.translate(['Khái niệm lực'], Event()) == result
    assert len(calls) == 3 and all('lực' not in value for value in calls)


def test_contextual_payload_does_not_reuse_opaque_term_cache(tmp_path):
    import hashlib

    from app.translation_terms import TermPolicy

    KeyStore(tmp_path).add('AIza' + 'x'*35)
    text = 'Vận tốc thay đổi.'
    policy = TermPolicy('Vật lý')
    old = 'google-nmt-terms-v1|' + policy.fingerprint(policy.matches(text))
    key = hashlib.sha256((old+'|vi|en|'+text).encode()).hexdigest()
    calls = []
    translator = Translator(tmp_path, transport=lambda rows,*_: calls.extend(rows) or [s.replace('thay đổi.', 'changes.') for s in rows])
    translator.store.cache_many([(key, 'Bad word order from old opaque payload')])
    translator.configure_terms('Vật lý', [])
    assert translator.translate([text], Event()) == ['Velocity changes.']
    assert len(calls) == 1 and '>velocity</span>' in calls[0]
    assert translator.store.cached(key) == 'Bad word order from old opaque payload'


def test_unlocked_terms_do_not_override_google_and_word_boundaries_are_respected(tmp_path):
    from app.translation_terms import TermPolicy

    policy = TermPolicy('Vật lý', [{'vi': 'lực', 'en': 'force', 'locked': True},
                                  {'vi': 'động năng', 'en': 'bad draft', 'locked': False}])
    assert not policy.matches('lựcđẩy')
    assert policy.matches('động năng') == {'động năng':'kinetic energy'}, 'An unlocked draft cannot replace the subject baseline'
    assert policy.matches('lực đẩy') == {'lực': 'force'}


def test_valid_items_are_cached_when_another_item_in_same_batch_is_rejected(tmp_path):
    KeyStore(tmp_path).add('AIza' + 'x'*35)
    calls = []

    def transport(texts, *_):
        calls.append(texts)
        return [text.replace('Xin chào', 'Hello').replace('BCLLOCK0END', 'broken') if 'Sai' in text
                else text.replace('Xin chào', 'Hello') for text in texts]

    translator = Translator(tmp_path, transport=transport)
    with pytest.raises(TranslationProblem):
        translator.translate(['Xin chào', 'Sai 12'], Event(), fragment_repair=False)
    assert translator.translate(['Xin chào'], Event()) == ['Hello']
    assert len(calls) == 2, 'Only the invalid chunk gets one bounded opaque-value repair'
    assert len(calls[1]) == 1 and 'Sai' in calls[1][0]


def test_math_instruction_keeps_the_solve_verb_before_cache_or_provider(tmp_path):
    import hashlib
    from threading import Event

    from app.google_translation import Translator

    translator = Translator(tmp_path, transport=lambda *_: (_ for _ in ()).throw(AssertionError('Exact instruction needs no API')))
    translator.configure_terms('Toán', [])
    text = 'Giải phương trình'
    stale = hashlib.sha256(('google-nmt-context-v3|vi|en|' + text).encode()).hexdigest()
    translator.store.cache(stale, 'equation')
    assert translator.translate([text, 'Giải hệ phương trình', 'Giải phương trình ⟦BLC0⟧.',
        'Sin thì sin cos cos sin', 'Cos thì cos cos sin sin nhớ trừ.'], Event()) == [
        'Solve the equation', 'Solve the system of equations', 'Solve the equation ⟦BLC0⟧.',
        'Sine: sine–cosine, cosine–sine', 'Cosine: cosine–cosine, sine–sine; remember to subtract.']
