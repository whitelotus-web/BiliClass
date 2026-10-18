from app.lesson_state import summarize_state


def test_audio_never_implies_content_review_or_teaching_preparation():
    lesson = dict(id='lesson', revision=2, segments=[dict(id='one', vi='Bài', en='Lesson', approved=False)])
    state = summarize_state(lesson, dict(ready=True, complete=2, total=2))
    assert state['saved'] and state['audio_ready']
    assert not state['content_ready'] and not state['prepared']
    lesson['segments'][0]['approved'] = True
    assert summarize_state(lesson)['content_ready']
    assert not summarize_state(lesson)['prepared']
    lesson['prepared'] = dict(revision=2, source_sha256='')
    assert summarize_state(lesson)['prepared']
    lesson['slide_quality'] = dict(counts=dict(FAIL=1))
    assert not summarize_state(lesson)['prepared']


def test_stale_audio_check_is_not_displayed_as_ready():
    state = summarize_state({}, {'status': 'checking'})
    assert not state['saved'] and not state['audio_ready']
    assert state['audio_label'] == 'Đang kiểm tra giọng'
