"""Read public web controls only; never infer entitlement from stored model names."""

import re

PICKER = ('[data-testid="model-switcher-dropdown-button"], [data-testid="model-picker-button"], '
          'button[aria-label="Choose model"], button[aria-label="Chọn mô hình"]')
PLANS = {"plus", "pro", "free", "go", "business", "enterprise", "edu"}


def plan_from_text(text):
    for line in text.splitlines():
        value = re.sub(r"^(your plan|plan|gói hiện tại|gói)\s*[:：]\s*", "", line.strip(), flags=re.I)
        value = re.sub(r"^ChatGPT\s+", "", value, flags=re.I).casefold()
        if value in PLANS:
            return value
    return "unknown"


def detect_plan(page, profile):
    """Exact plan labels only: 'Upgrade to Plus' must never mean a Plus account."""
    from playwright.sync_api import Error

    from .browser_automation import visible

    plan = "unknown"
    try:
        button = visible(page, profile)
        if not button:
            return plan
        plan = plan_from_text(button.inner_text())
        if plan != "unknown":
            return plan
        button.click(timeout=3000)
        page.wait_for_timeout(200)
        for menu in page.locator('[role="menu"], [data-testid="account-menu"]').all():
            if menu.is_visible():
                plan = plan_from_text(menu.inner_text())
                if plan != "unknown":
                    break
    except Error:
        return "unknown"
    finally:
        try:
            page.keyboard.press("Escape")
        except Error:
            pass
    return plan


def model_priority(label):
    """Quality preference; unknown options are left for the web's default.

    Current reference: https://learn.chatgpt.com/docs/model-selection
    Only enabled, visible options are eligible; this never grants model access.
    """
    text = label.casefold()
    if re.search(r"upgrade|unlock|subscribe|nâng cấp|mở khóa|đăng ký", text):
        return None
    version = re.search(r"gpt[ -]?(\d+)(?:\.(\d+))?", text)
    if "astra" in text:
        quality = 9
    elif re.search(r"\bsol\b", text):
        quality = 8
    elif re.search(r"\bpro\b", text):
        quality = 7
    elif re.search(r"\bthinking\b|suy nghĩ", text):
        quality = 6
    elif re.search(r"\bterra\b", text):
        quality = 5
    elif re.search(r"\bluna\b|\bmini\b|\binstant\b", text):
        quality = 3
    elif version:
        quality = 4
    else:
        return None
    return quality, int(version[1]) if version else 0, int(version[2] or 0) if version else 0


def select_best_model(page):
    from playwright.sync_api import Error

    from .browser_automation import visible

    picker = visible(page, PICKER)
    if not picker:
        return "Mặc định của web"
    current = picker.inner_text().strip() or "Mặc định của web"
    try:
        picker.click(timeout=3000)
        page.wait_for_timeout(250)
        options = []
        for panel in page.locator('[role="menu"], [role="listbox"], [role="dialog"]').all():
            if not panel.is_visible():
                continue
            for item in panel.locator('[role="menuitemradio"], [role="menuitem"], [role="radio"], [role="option"], button').all():
                if (not item.is_visible() or not item.is_enabled()
                        or item.get_attribute("aria-disabled") == "true" or item.get_attribute("data-disabled") == "true"):
                    continue
                label = item.inner_text().strip()
                rank = model_priority(label)
                if rank is not None:
                    options.append((rank, item, label.splitlines()[0]))
        if not options:
            return current
        _, choice, label = max(options, key=lambda option: option[0])
        choice.click(timeout=3000)
        page.wait_for_timeout(150)
        selected = picker.inner_text().strip()
        if (label.casefold() in selected.casefold() or choice.get_attribute("aria-checked") == "true"
                or choice.get_attribute("aria-selected") == "true"):
            return label
        return selected or current
    except Error:
        return current
    finally:
        try:
            page.keyboard.press("Escape")
        except Error:
            pass
