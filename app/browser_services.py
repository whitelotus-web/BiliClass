"""Provider boundaries for browser sessions; no web API keys or token access."""

import re
from urllib.parse import urlsplit

SERVICES = {"chatgpt": {"label": "ChatGPT", "home": "https://chatgpt.com/"},
            "gemini": {"label": "Gemini", "home": "https://gemini.google.com/app"}}


def service_spec(service):
    if not isinstance(service, str) or service not in SERVICES:
        raise ValueError("Chọn ChatGPT hoặc Gemini trong Browser AI.")
    return SERVICES[service]


def conversation_url(url, service=None):
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.query or parsed.fragment or parsed.username or parsed.password or parsed.port:
            return False
        chatgpt = parsed.hostname == "chatgpt.com" and bool(re.fullmatch(r"/c/[A-Za-z0-9_-]{1,200}", parsed.path))
        gemini = parsed.hostname == "gemini.google.com" and bool(re.fullmatch(r"/(?:u/\d+/)?app/[A-Za-z0-9_-]{1,200}", parsed.path))
        return chatgpt if service == "chatgpt" else gemini if service == "gemini" else (chatgpt or gemini) if service is None else False
    except ValueError:
        return False


def backend_for(account):
    service = account.get("service", "chatgpt")
    service_spec(service)
    if service == "gemini":
        from . import gemini_automation
        return gemini_automation
    from . import browser_automation
    return browser_automation
