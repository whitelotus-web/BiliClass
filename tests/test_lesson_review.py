from copy import deepcopy

from app.lesson_review import summarize


def lesson():
    return {'id': 'one', 'revision': 1, 'segments': [{'vi': 'Một', 'en': 'One', 'approved': False}]}


def test_pending_confirmation_is_not_technical_failure_or_silent_approval():
    item = lesson()
    before = deepcopy(item)
    state = summarize(item)
    assert state['kind'] == 'confirm' and state['pending'] == 1
    assert state['canConfirm'] and not state['canRepair']
    assert item == before


def test_technical_failure_blocks_confirmation_even_for_previously_prepared_lesson():
    item = lesson()
    item.update(prepared={'revision': 1, 'source_sha256': ''},
                external_deck={'total': 2}, slide_quality={'counts': {'FAIL': 2}})
    state = summarize(item)
    assert state['label'] == '2 slide cần sửa'
    assert state['canRepair'] and not state['canConfirm']


def test_missing_translation_cannot_be_confirmed():
    item = lesson()
    item['segments'][0]['en'] = ''
    state = summarize(item)
    assert state['kind'] == 'incomplete' and not state['canConfirm']


def test_approved_text_and_current_preparation_have_different_states():
    item = lesson()
    item['segments'][0]['approved'] = True
    assert summarize(item)['kind'] == 'reviewed'
    item['prepared'] = {'revision': 1, 'source_sha256': ''}
    assert summarize(item)['kind'] == 'ready'
    item['revision'] = 2
    assert summarize(item)['kind'] == 'reviewed'
