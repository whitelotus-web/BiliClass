"""Stream official Responses using OAuth plan permission, never an API key."""

import json

import httpx

from .chatgpt_auth import RESOURCE, ChatGPTAuth, PlanError, response_error


class ChatGPTPlanProvider:
    def __init__(self, accounts, client=None, auth=None):
        self.accounts = accounts
        self.client = client or httpx.Client(timeout=httpx.Timeout(45, connect=10), follow_redirects=False)
        self.auth = auth or ChatGPTAuth(accounts, self.client)

    def models(self, account_id):
        token = self.auth.access_token(account_id)
        try:
            response = self.client.get(RESOURCE + "/models", headers={"Authorization": "Bearer " + token})
        except httpx.HTTPError:
            raise PlanError("Chưa lấy được danh sách model ChatGPT. Kiểm tra mạng; yêu cầu được giữ tại máy.") from None
        if response.status_code != 200:
            raise response_error(response)
        models = response.json().get("models", [])
        available = [{"slug": m["slug"], "display_name": m.get("display_name") or m["slug"],
                      "input_modalities": m.get("input_modalities", [])}
                     for m in models if isinstance(m, dict) and m.get("visibility") == "list"
                     and isinstance(m.get("slug"), str) and m["slug"]]
        if not available:
            raise PlanError("Tài khoản chưa có model được phép xử lý bài qua kết nối này.")
        return available

    def generate(self, account_id, model, instructions, content, schema, cancel, progress=lambda _: None):
        if cancel.is_set():
            raise PlanError("Đã dừng chuyển đổi.", "cancelled")
        token = self.auth.access_token(account_id)
        body = {"model": model, "store": False, "stream": True, "instructions": instructions,
                "input": [{"role": "user", "content": content}],
                "text": {"format": {"type": "json_schema", "name": "biliclass_lesson", "strict": True, "schema": schema}}}
        output, completed, terminal = [], None, False
        received = 0
        try:
            with self.client.stream("POST", RESOURCE + "/responses", json=body,
                                    headers={"Authorization": "Bearer " + token}) as response:
                if response.status_code != 200:
                    response.read()
                    raise response_error(response)
                data_lines = []
                for line in response.iter_lines():
                    if cancel.is_set():
                        raise PlanError("Đã dừng chuyển đổi. Có thể tiếp tục các phần chưa xong.", "cancelled")
                    if line.startswith("data:"):
                        data_lines.append(line[5:].lstrip())
                        received += len(line)
                        if received > 12_000_000:
                            raise PlanError("Kết quả ChatGPT quá lớn. Chia nhỏ bài trước khi tiếp tục.")
                    elif not line and data_lines:
                        raw, data_lines = "\n".join(data_lines), []
                        if raw == "[DONE]":
                            break
                        try:
                            event = json.loads(raw)
                        except ValueError:
                            raise PlanError("Luồng kết quả ChatGPT không hợp lệ; phần này chưa được áp dụng.") from None
                        kind = event.get("type")
                        if kind == "response.output_text.delta":
                            output.append(event.get("delta", ""))
                        elif kind in ("response.failed", "error"):
                            error = event.get("response", {}).get("error") or event.get("error") or {"code": event.get("code", "")}
                            error = error if isinstance(error, dict) else {}
                            # The mapper ignores free-form messages; never log output or tokens.
                            code = error.get("code", "")
                            status = 429 if "limit_exceeded" in code else 403 if "not_eligible" in code else 400 if "capability" in code else 503
                            synthetic = httpx.Response(status,
                                                       json={"error": error})
                            raise response_error(synthetic)
                        elif kind == "response.incomplete":
                            raise PlanError("ChatGPT chưa hoàn tất phần bài này. Kết quả một phần chưa được áp dụng.", "incomplete")
                        elif kind == "response.completed":
                            completed, terminal = event.get("response", {}), True
                            break
        except (httpx.HTTPError, OSError):
            raise PlanError("Mất kết nối khi xử lý bài. Phần đã hoàn tất được giữ; yêu cầu đang gửi cần xác nhận trước khi gửi lại.",
                            "stream_interrupted") from None
        if not terminal:
            raise PlanError("Luồng ChatGPT dừng trước khi hoàn tất. Không dùng kết quả một phần; xác nhận trước khi gửi lại.",
                            "stream_interrupted")
        text = "".join(c.get("text", "") for item in completed.get("output", []) if item.get("type") == "message"
                       for c in item.get("content", []) if c.get("type") == "output_text") or "".join(output)
        if not text.strip():
            raise PlanError("ChatGPT chưa trả nội dung bài có cấu trúc.")
        try:
            return json.loads(text)
        except ValueError:
            raise PlanError("ChatGPT trả dữ liệu không đúng JSON. Kết quả chưa được ghép vào bài.", "invalid_json") from None
