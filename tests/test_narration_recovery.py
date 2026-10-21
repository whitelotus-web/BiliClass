from copy import deepcopy

import pytest

from app.lesson_narration import automatic_repair_choice, make_plan
from app.narration_text import clean_artifacts
from app.slide_speech import speech_chunks, speech_problem


def item():
    lesson = {'id': 'one', 'revision': 1, 'segments': [
        {'id': 'a', 'locator': 'Slide 1', 'vi': 'Năng lượng được bảo toàn.', 'en': ''},
        {'id': 'b', 'locator': 'Slide 2', 'vi': 'Con lắc đếm thời gian. 19lt568', 'en': ''},
        {'id': 'c', 'locator': 'Slide 3', 'vi': 'Gemini Notebook 19lt568', 'en': ''}]}
    plan, _ = make_plan(lesson, 'vi', {'voice': 'vieneu:Mai Anh', 'rate': 0})
    # Simulate the old finished plan, before the stamped sentence was recovered.
    plan['keys']['vi'] = plan['keys']['vi'][:1]
    plan.update(total=1, complete=1, skipped=2, failed=0, cancelled=False)
    lesson['narration'] = plan
    return lesson


def test_missing_audio_of_finished_voice_recovers_only_after_verified_status():
    from app.lesson_narration import variant_id

    lesson = item()
    lesson['segments'] = lesson['segments'][:1]
    plan, _ = make_plan(lesson, 'vi', {'voice': 'vieneu:Mai Anh', 'rate': 0})
    plan.update(complete=plan['total'], failed=0, cancelled=False)
    lesson['narration'] = plan
    status = dict(id=variant_id(plan), status='partial', total=plan['total'])
    expected = {'mode': 'vi', 'voice': 'vieneu:Mai Anh', 'rate': 0}
    assert automatic_repair_choice(lesson, status) == expected
    assert automatic_repair_choice(lesson) is None
    assert automatic_repair_choice(lesson, {**status, 'id': 'another-recording'}) is None
    assert automatic_repair_choice(lesson, {**status, 'status': 'ready'}) is None
    plan['cancelled'] = True
    assert automatic_repair_choice(lesson, status) is None


def test_known_stamps_preserve_valid_sentences_and_unaffected_cache_text():
    text = 'Năng lượng.\r\nĐộng năng.'
    assert clean_artifacts(text) == text
    assert speech_chunks('Con lắc đếm thời gian. 19lt568') == ['Con lắc đếm thời gian.']
    assert speech_problem('Con lắc đếm thời gian. 19wx568') == ''
    assert speech_chunks('Gemini Notebook 19lt568') == []
    assert clean_artifacts('Gemini Notebook') == 'Gemini Notebook'
    assert speech_problem('Mã chưa rõ 33abc222') == 'suspicious_code'


def test_repair_only_finishes_known_stamped_plan_without_editing_content():
    lesson = item()
    before = deepcopy(lesson)
    assert automatic_repair_choice(lesson) == {'mode': 'vi', 'voice': 'vieneu:Mai Anh', 'rate': 0}
    assert lesson == before
    new, _ = make_plan(lesson, 'vi', lesson['narration'])
    assert new['total'] == 2 and new['skipped'] == 0
    assert set(before['narration']['keys']['vi']) < set(new['keys']['vi'])


@pytest.mark.parametrize('changes', [
    {'failed': 1}, {'cancelled': True}, {'complete': 0}, {'skipped': 0},
    {'keys': []}, {'keys': {'vi': [{}]}}, {'total': '1'}, {'signature': 'stale'}])
def test_unfinished_unknown_or_corrupt_records_are_not_silently_completed(changes):
    lesson = item()
    lesson['narration'].update(changes)
    assert automatic_repair_choice(lesson) is None


def test_non_dict_record_does_not_crash_recovery():
    lesson = item()
    lesson['narration'] = ['bad record']
    assert automatic_repair_choice(lesson) is None
