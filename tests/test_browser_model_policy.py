import pytest

from app import browser_capabilities as models
from app import gemini_automation as gemini
from app.browser_automation import BrowserProblem
from app.browser_model_policy import prepare_models
from app.browser_reasoning import level


@pytest.mark.parametrize("service,model,reasoning", [("chatgpt","Thinking","Suy luận trên web: High"),
                                                  ("chatgpt","Mặc định của web","Đã bật suy luận trên web"),
                                                  ("gemini","Gemini 3.1 Pro","Suy luận trên web: Extended")])
def test_confirmed_highest_controls_saved(service, model, reasoning, monkeypatch):
    monkeypatch.setattr(models, 'select_best_model', lambda _:model)
    monkeypatch.setattr(models, 'select_reasoning', lambda _:reasoning)
    monkeypatch.setattr(gemini, 'select_model', lambda _:model)
    monkeypatch.setattr('app.browser_reasoning.select_effort', lambda *a,**kw:reasoning)
    policy = prepare_models(None,service)
    assert policy['highest_model_verified'] and policy['reasoning_verified'] and policy['model'] == model


@pytest.mark.parametrize("service", ['chatgpt','gemini'])
def test_unconfirmed_fast_default_blocks_submission(service, monkeypatch):
    monkeypatch.setattr(models,'select_best_model',lambda _:'Fast')
    monkeypatch.setattr(models,'select_reasoning',lambda _:'Theo tùy chọn web đang có')
    monkeypatch.setattr(gemini,'select_model',lambda _:'Fast')
    monkeypatch.setattr('app.browser_reasoning.select_effort',lambda *a,**kw:'Theo tùy chọn web đang có')
    with pytest.raises(BrowserProblem) as exc:
        prepare_models(None,service)
    assert exc.value.code=='model'


def test_vietnamese_complex_reasoning_ranks_above_high_and_below_extra_high():
    assert level('Rất cao')[0] > level('Suy luận phức tạp')[0] > level('Cao')[0] > level('Think')[0]
