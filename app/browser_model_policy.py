"""Confirm the strongest web controls before every authorized submission."""

import re


def prepare_models(page, service):
    from .browser_automation import BrowserProblem

    # Restored chats can show their composer before the web has hydrated the
    # model/Think controls. Retry the readback briefly, before any send intent.
    for attempt in range(3):
        try:
            return _prepare_models(page, service)
        except BrowserProblem as exc:
            if exc.code != 'model' or attempt == 2:
                raise
            page.wait_for_timeout(1000)


def _prepare_models(page, service):
    from .browser_automation import BrowserProblem
    from .browser_reasoning import select_effort

    if service == "gemini":
        from .gemini_automation import COMPOSER, MODEL_PICKER, select_model
        model = select_model(page)
        reasoning = select_effort(page, composer=COMPOSER, model_picker=MODEL_PICKER)
        intrinsic = bool(re.search(r"\bpro\b|deep\s*think|thinking|suy (?:nghĩ|luận)", model, re.I))
    else:
        from .browser_capabilities import select_best_model, select_reasoning
        model, reasoning = select_best_model(page), select_reasoning(page)
        intrinsic = bool(re.search(r"\bpro\b|thinking|suy (?:nghĩ|luận)", model, re.I))
    explicit = reasoning.startswith(("Đã bật suy luận", "Suy luận trên web:"))
    if not explicit and not intrinsic:
        raise BrowserProblem("model", "Chưa xác nhận được model/suy luận phù hợp trên web. Chưa gửi bài; mở tài khoản trong Browser AI để kiểm tra lựa chọn.")
    return {"model": model, "reasoning": reasoning if explicit else "Suy luận của model đã xác nhận: " + model,
            "highest_model_verified": True, "reasoning_verified": True}
