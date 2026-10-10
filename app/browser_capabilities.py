"""Read public web controls only; never infer entitlement from stored model names."""

import re

PICKER = ('[data-testid="model-switcher-dropdown-button"], [data-testid="model-picker-button"], '
          'button[aria-label="Choose model"], button[aria-label="Chọn mô hình"]')
PLANS = {"plus", "pro", "free", "go", "business", "enterprise", "edu"}


def plan_from_text(text):
    for line in text.splitlines():
        value = re.sub(r"^(current plan|your plan|plan|gói hiện tại|gói)\s*[:：]\s*", "", line.strip(), flags=re.I)
        value = re.sub(r"^ChatGPT\s+", "", value, flags=re.I).casefold()
        if value in PLANS:
            return value
    return "unknown"


def detect_account(page, profile, *, details=False):
    """Exact plan labels only: 'Upgrade to Plus' must never mean a Plus account."""
    from playwright.sync_api import Error

    from .browser_automation import visible

    info = {"plan": "unknown", "name": "", "email": ""}
    try:
        button = visible(page, profile)
        if not button:
            return info
        text = button.inner_text().strip()
        info["plan"] = plan_from_text(text)
        lines = text.splitlines()
        if lines and plan_from_text(lines[0]) == "unknown" and lines[0].casefold() not in {
            "open profile menu", "profile", "account", "chatgpt", "mở hồ sơ", "tài khoản",
        } and not re.search(r"upgrade|nâng cấp", lines[0], re.I):
            info["name"] = lines[0][:100]
        button.click(timeout=3000)
        page.wait_for_timeout(200)
        for menu in page.locator('[role="menu"], [data-testid="account-menu"]').all():
            if menu.is_visible():
                text += "\n" + menu.inner_text()
                plan = plan_from_text(text)
                if plan != "unknown":
                    info["plan"] = plan
        email = re.search(r"(?m)^\s*([^\s@]+@[^\s@]+\.[^\s@]+)\s*$", text)
        if email:
            info["email"] = email[1][:254]
        for node in page.locator('[data-testid="account-name"], [data-testid="profile-name"]').all():
            if node.is_visible() and node.inner_text().strip():
                info["name"] = node.inner_text().strip()[:100]
                break
        if details and info["plan"] == "unknown":
            settings = page.get_by_role("menuitem", name=re.compile(r"^(Settings|Cài đặt)$", re.I))
            if settings.count() and settings.first.is_visible():
                settings.first.click(timeout=3000)
                page.wait_for_timeout(300)
                for dialog in page.get_by_role("dialog").all():
                    if not dialog.is_visible():
                        continue
                    tabs = dialog.get_by_role("tab", name=re.compile(r"^(Account|Tài khoản)$", re.I))
                    if not tabs.count():
                        tabs = dialog.get_by_role("button", name=re.compile(r"^(Account|Tài khoản)$", re.I))
                    if tabs.count() and tabs.first.is_visible():
                        tabs.first.click(timeout=3000)
                        page.wait_for_timeout(200)
                    # Read the current-plan field, never pricing cards or an upsell.
                    for node in dialog.locator('[data-testid="current-plan"], [data-testid="account-plan"]').all():
                        if node.is_visible():
                            plan = plan_from_text(node.inner_text())
                            if plan != "unknown":
                                info["plan"] = plan
                    explicit = re.search(r"(?mi)^\s*(?:Current plan|Your plan|Gói hiện tại)\s*[:：]\s*(?:ChatGPT\s+)?(Free|Plus|Pro|Go|Business|Enterprise|Edu)\s*$", dialog.inner_text())
                    if explicit:
                        info["plan"] = explicit[1].casefold()
    except Error:
        pass
    finally:
        try:
            page.keyboard.press("Escape")
        except Error:
            pass
    return info


def detect_plan(page, profile):
    return detect_account(page, profile, details=True)["plan"]


def select_reasoning(page):
    from .browser_reasoning import select_effort

    return select_effort(page)


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
