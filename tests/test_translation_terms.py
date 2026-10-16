from threading import Event

import pytest

from app.google_translation import KeyStore, TranslationProblem, Translator


def test_exact_teacher_term_and_classroom_heading_need_no_api(tmp_path):
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('Local wording must not call Google'))
    translator.configure_terms('Vật lý', [{'vi': 'động năng', 'en': 'Kinetic energy', 'locked': True}])
    assert translator.translate(['động năng', 'VẬN DỤNG'], Event()) == ['Kinetic energy', 'Application']
    assert not translator.store.public()


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


def test_unlocked_terms_do_not_override_google_and_word_boundaries_are_respected(tmp_path):
    from app.translation_terms import TermPolicy

    policy = TermPolicy('Vật lý', [{'vi': 'lực', 'en': 'force', 'locked': True},
                                  {'vi': 'động năng', 'en': 'bad draft', 'locked': False}])
    assert not policy.matches('lựcđẩy') and not policy.matches('động năng')
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
        translator.translate(['Xin chào', 'Sai 12'], Event())
    assert translator.translate(['Xin chào'], Event()) == ['Hello']
    assert len(calls) == 1
