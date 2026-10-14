from threading import Event

import pytest

from app import browser_automation, gemini_automation
from app.browser_accounts import BrowserAccounts
from app.browser_dispatch import convert_available
from app.browser_services import backend_for, conversation_url
from app.chatgpt_handoff import make_prompt


def test_services_and_explicit_account_choices_persist_without_moving_profiles(tmp_path):
    store = BrowserAccounts(tmp_path)
    chat = store.add("ChatGPT")
    store.observe(chat["id"], "plus")
    original = store.get(chat["id"])["profile"]
    store.choose_service("gemini")
    free = store.add("Gemini 1")
    paid = store.add("Gemini 2")
    store.observe(free["id"], "free")
    store.observe(paid["id"], "pro")
    assert store.preferred()["id"] == paid["id"]
    store.choose_account(free["id"])
    assert [x["id"] for x in store.candidates()] == [free["id"]]
    store.login_error(free["id"], "limit", "Hết lượt")
    assert not store.candidates()  # Explicit pin never silently uses a different account.
    store.choose_account("")
    assert store.preferred()["id"] == paid["id"]
    resumed = BrowserAccounts(tmp_path)
    assert resumed.data["service"] == "gemini" and resumed.get(chat["id"])["profile"] == original
    assert backend_for(resumed.get(paid["id"])) is gemini_automation
    resumed.choose_service("chatgpt")
    assert resumed.preferred()["id"] == chat["id"]
    assert backend_for(resumed.get(chat["id"])) is browser_automation
    with pytest.raises(ValueError):
        resumed.choose_account(free["id"])


def test_old_accounts_keep_chatgpt_session_and_old_jobs_keep_their_service(tmp_path):
    store = BrowserAccounts(tmp_path)
    chat = store.add("Old account")
    store.observe(chat["id"], "free")
    store.data["accounts"][0].pop("service")
    store.data.pop("service")
    store.data.pop("service_selection")
    store.save()
    restored = BrowserAccounts(tmp_path)
    assert restored.preferred()["id"] == chat["id"] and restored.get()["ready"]
    restored.choose_service("gemini")
    gem = restored.add("New")
    restored.observe(gem["id"], "pro")
    folder = tmp_path / "job"
    folder.mkdir()
    record = browser_automation.read_record(folder, chat["id"])
    record.update(state="waiting", url="https://chatgpt.com/c/old")
    browser_automation.write_record(folder, record)
    calls = []
    def converter(account, *args, **kwargs):
        calls.append(account["id"])
        return {"path":"old.pptx", "url":record["url"]}
    convert_available([restored.get(chat["id"])], restored.root, folder, Event(), lambda *_: None, converter=converter)
    assert calls == [chat["id"]]
    with pytest.raises(browser_automation.BrowserProblem):
        gemini_automation.read_record(folder, chat["id"])


@pytest.mark.parametrize("url", ["https://gemini.google.com.evil.invalid/app/1", "https://gemini.google.com/app/1?token=x",
                                "https://gemini.google.com/share/1", "http://gemini.google.com/app/1", "https://user@gemini.google.com/app/1"])
def test_gemini_conversation_boundaries(url):
    assert not conversation_url(url, "gemini")


def test_gemini_prompt_uses_same_bilingual_contract_with_correct_export_instructions():
    config = {"title":"Bài", "subject":"Toán", "grade":"10", "education_level":"THPT", "style":"source",
              "preset":"standard", "conversion_format":"parallel_columns", "provider":"browser_web"}
    chat = make_prompt(config, "input.pptx")
    gem = make_prompt({**config,"browser_service":"gemini"}, "input.pptx")
    assert "dịch đầy đủ từng câu" in gem and "Không thêm, bớt, tách, gộp slide" in gem
    assert "Google Slides" in gem and "Google Slides" not in chat
    assert "VI:" in gem and "EN:" in gem and "QUIZ:" in gem
    with pytest.raises(ValueError):
        make_prompt({**config,"browser_service":"foreign"}, "input.pptx")
