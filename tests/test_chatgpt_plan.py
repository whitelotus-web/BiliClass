import json
from threading import Event

import httpx
import pytest

from app.chatgpt_auth import PlanError
from app.chatgpt_plan import ChatGPTPlanProvider


class Auth:
    def access_token(self, _account):
        return "fixture-access"


def provider_for(events, status=200):
    requests = []
    def route(request):
        requests.append(request)
        if request.url.path.endswith("models"):
            return httpx.Response(200, json={"models": [{"slug": "visible", "visibility": "list", "display_name": "Allowed"},
                                                       {"slug": "hidden", "visibility": "hide"}]})
        if status != 200:
            return httpx.Response(status, json={"error": {"code": "subscription_sharing_usage_limit_exceeded", "message": "secret"}})
        return httpx.Response(200, text="".join("data: " + json.dumps(event) + "\n\n" for event in events),
                              headers={"Content-Type": "text/event-stream"})
    client = httpx.Client(transport=httpx.MockTransport(route))
    return ChatGPTPlanProvider(None, client, Auth()), requests


def generate(provider):
    return provider.generate("one", "visible", "Source rules", [{"type": "input_text", "text": "Synthetic"}],
                             {"type": "object", "additionalProperties": False, "properties": {}, "required": []}, Event())


def test_completed_stream_and_supported_payload_only():
    events = [{"type": "response.output_text.delta", "delta": '{"draft":true}'},
              {"type": "response.completed", "response": {"output": []}}]
    provider, requests = provider_for(events)
    assert provider.models("one")[0]["slug"] == "visible" and len(provider.models("one")) == 1
    assert generate(provider) == {"draft": True}
    body = json.loads(requests[-1].content)
    assert body["store"] is False and body["stream"] is True
    assert set(body) == {"model", "store", "stream", "instructions", "input", "text"}
    assert body["input"][0]["role"] == "user"


@pytest.mark.parametrize("events", [[], [{"type": "response.output_text.delta", "delta": '{"partial":true}'}],
                                  [{"type": "response.incomplete", "response": {}}],
                                  [{"type": "response.completed", "response": {"output": []}}]])
def test_no_partial_or_empty_results(events):
    provider, _ = provider_for(events)
    with pytest.raises(PlanError):
        generate(provider)


def test_midstream_quota_failure_is_not_success_or_token_leak():
    provider, _ = provider_for([{"type": "response.output_text.delta", "delta": '{"draft":true}'},
                               {"type": "error", "code": "subscription_sharing_usage_limit_exceeded", "message": "secret"}])
    with pytest.raises(PlanError) as failure:
        generate(provider)
    assert failure.value.status == 429 and "secret" not in str(failure.value)
    assert "hạn mức" in str(failure.value)


def test_http_rejection_and_cancel():
    provider, requests = provider_for([], status=429)
    with pytest.raises(PlanError) as failure:
        generate(provider)
    assert failure.value.status == 429
    cancelled = Event()
    cancelled.set()
    with pytest.raises(PlanError) as failure:
        provider.generate("one", "visible", "", [], {}, cancelled)
    assert failure.value.code == "cancelled" and len(requests) == 1
