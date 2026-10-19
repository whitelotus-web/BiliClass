"""An attached Office worker must block preview only while actually presenting."""

from types import SimpleNamespace

import pytest

from app.ui import Bridge


@pytest.mark.parametrize('state,busy,expected', [
    ({}, False, True),
    ({'opened': True, 'active': False, 'starting': False}, False, True),
    ({'active': True}, False, False),
    ({'starting': True}, False, False),
    ({}, True, False),
])
def test_preview_with_attached_worker_respects_actual_presentation_state(state, busy, expected):
    calls = []
    result = {'total': 3, 'slide': 1}
    bridge = SimpleNamespace(
        _busy=busy, _powerpoint_state=state, powerpoint_worker=object(),
        quickResult=result, _quick_result=result, _lesson={'id': 'fixture'},
        stopSpeech=lambda: calls.append('stop'),
        quickResultChanged=SimpleNamespace(emit=lambda: calls.append('changed')),
        slidePreview=SimpleNamespace(start=lambda *args: calls.append(args)),
    )
    Bridge.previewConvertedSlide(bridge, 2)
    assert bool(calls) is expected
    if expected:
        assert result['slide'] == 2
        assert calls[-1] == ({'id': 'fixture'}, {'total': 3, 'slide': 1}, 2)


def test_open_navigation_does_not_wait_for_preparation_worker():
    calls = []
    lesson = {'id': 'fixture', 'external_deck': {'total': 2}}
    bridge = SimpleNamespace(
        _busy=False, narrationBusy=False,
        library=SimpleNamespace(get=lambda _: lesson),
        _show_lesson=lambda *args, **kwargs: calls.append(('show', args, kwargs)),
        launch=lambda *args: calls.append(('worker',)),
        inform=lambda *args: calls.append(('error',)),
    )
    Bridge.openLesson(bridge, 'fixture')
    assert [row[0] for row in calls] == ['show', 'worker']
    assert calls[0][2] == {'auto_repair': False, 'load_preview': False}
