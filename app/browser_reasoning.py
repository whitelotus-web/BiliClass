"""Select and verify the strongest effort actually offered by composer controls."""

import re

LEVELS = (
    (6, "Extra high", r"extra\s*high|maximum|max|cao nhất|rất cao"),
    (5, "Extended", r"extended|mở rộng"),
    (4, "High", r"high|cao"),
    (3, "Standard", r"standard|medium|tiêu chuẩn|trung bình"),
    (2, "Think", r"think(?:ing)?|suy nghĩ|suy luận|tư duy"),
    (1, "Light", r"light|low|nhẹ|thấp"),
)


def label(item):
    return (item.inner_text(timeout=1000).strip() or item.get_attribute("aria-label") or "").strip()


def level(text):
    if re.search(r"upgrade|unlock|subscribe|nâng cấp|mở khóa|đăng ký", text, re.I):
        return 0, ""
    text = re.sub(r"^(?:selected|đã chọn|thinking time|thời gian suy nghĩ)\s*[:：]?\s*", "", text, flags=re.I)
    for rank, name, pattern in LEVELS:
        if re.match(r"^(?:" + pattern + r")(?:$|\n|\s*[:—–]|\s+(?:think|reason|more|longer|for)\b)", text, re.I):
            return rank, name
    return 0, ""


def selected(item):
    return item.evaluate("""el => {
        const yes = ['true', 'checked', 'selected', 'on', 'active'];
        return ['aria-pressed','aria-checked','aria-selected','data-state','data-selected']
            .some(k => yes.includes((el.getAttribute(k) || '').toLowerCase()))
            || Boolean(el.querySelector('[data-icon="check"], [aria-label="Selected"], [aria-label="Đã chọn"]'));
    }""")


def eligible(item):
    from .browser_automation import MESSAGE_ANCESTORS

    return (item.is_visible() and item.is_enabled() and item.get_attribute("aria-disabled") != "true"
            and item.get_attribute("data-disabled") not in {"true", ""}
            and not item.locator(MESSAGE_ANCESTORS).count())


def select_effort(page):
    from playwright.sync_api import Error

    from .browser_automation import COMPOSER, BrowserProblem, visible
    from .browser_capabilities import PICKER

    prompt = visible(page, COMPOSER)
    if not prompt:
        raise BrowserProblem("interface", "Chưa tìm được ô prompt để chọn suy luận. Chưa gửi bài.")
    scope = prompt.locator("xpath=ancestor::*[self::form or @data-type='unified-composer'][1]")
    if not scope.count():
        scope = prompt.locator("..")
    offered, verified, visited = False, "", set()

    def controls():
        return [b for b in scope.get_by_role("button").all()[:40] if eligible(b)]

    def readback(name, option=None):
        if option is not None and option.is_visible() and selected(option):
            return True
        for button in controls():
            if level(label(button))[1] == name and (name != "Think" or selected(button)):
                return True
        removal = scope.get_by_role("button", name=re.compile(r"(?:remove|disable|turn off|tắt|bỏ).*(?:think|suy nghĩ|suy luận|tư duy)", re.I))
        return name == "Think" and any(eligible(b) for b in removal.all())

    try:
        # At most three menus: enable Think, open its effort picker, then
        # verify the selected effort. Never inspect a lesson's action buttons.
        for _ in range(3):
            buttons = controls()
            ranked = sorted(((level(label(b))[0], i) for i, b in enumerate(buttons)), reverse=True)
            picker = None
            for rank, index in ranked:
                if not rank:
                    continue
                button = buttons[index]
                name = level(label(button))[1]
                if name != "Think":
                    offered, verified = True, name  # Effort picker displays its current selection.
                if name == "Think" and readback(name):
                    offered, verified = True, name
                    continue
                if label(button) not in visited:
                    picker = button
                    offered = True
                    break
            if picker is None:
                candidates = [b for b in buttons if re.match(r"^(?:Tools|Công cụ|Add files and more|Thêm ảnh và tệp|\+)$", label(b), re.I)]
                candidates += [b for b in page.locator(PICKER).all()[:4] if eligible(b)]
                picker = next((b for b in candidates if label(b) not in visited), None)
            if picker is None:
                break
            visited.add(label(picker))
            picker.click(timeout=2500)
            page.wait_for_timeout(150)
            options = []
            for panel in page.locator('[role="menu"], [role="listbox"]').all()[:10]:
                if not eligible(panel):
                    continue
                for item in panel.locator('[role="menuitem"], [role="menuitemradio"], [role="menuitemcheckbox"], [role="option"], button').all()[:50]:
                    if eligible(item):
                        rank, name = level(label(item))
                        if rank:
                            options.append((rank, name, item))
            if options:
                _, name, option = max(options, key=lambda row: row[0])
                offered = True
                if not selected(option):
                    option.click(timeout=2500)
                    page.wait_for_timeout(150)
                confirmed = readback(name, option)
                page.keyboard.press("Escape")
                if not confirmed:
                    # Menus that close after a click may only report selected
                    # state when reopened. Read that state before accepting it.
                    picker.click(timeout=2500)
                    page.wait_for_timeout(150)
                    confirmed = readback(name, option)
                    page.keyboard.press("Escape")
                if not confirmed:
                    raise BrowserProblem("model", "Web có lựa chọn suy luận nhưng chưa xác nhận được đã chọn. Chưa gửi bài; mở Chrome để kiểm tra.")
                verified = name
                if name != "Think":
                    break
            else:
                for button in controls():
                    if selected(button) and level(label(button))[1] == "Think":
                        offered, verified = True, "Think"
                        break
                page.keyboard.press("Escape")
    except Error as exc:
        if offered:
            raise BrowserProblem("model", "Chưa xác nhận được cấu hình suy luận trên web. Chưa gửi bài; thử lại khi Chrome sẵn sàng.") from exc
    finally:
        try:
            page.keyboard.press("Escape")
        except Error:
            pass
    if offered and not verified:
        raise BrowserProblem("model", "Chưa xác nhận được đã bật suy luận. Chưa gửi bài.")
    return ("Đã bật suy luận trên web" if verified == "Think" else
            f"Suy luận trên web: {verified}" if verified else "Theo tùy chọn web đang có")
