"""Connect a development installation using a BiliClass-only system browser login."""

import argparse
from pathlib import Path

from app.chatgpt_auth import ChatGPTAuth, PlanAccounts
from app.chatgpt_plan import ChatGPTPlanProvider


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    accounts = PlanAccounts(args.data)
    auth = ChatGPTAuth(accounts)
    from app.chatgpt_auth import PlanError
    try:
        item = auth.authorize(progress=lambda message: print(message, flush=True))
    except PlanError as exc:
        print(str(exc), flush=True)
        return
    print("Đã kết nối." if item["ready"] else "Đã đăng nhập, chưa cấp quyền xử lý.", flush=True)
    if item["ready"]:
        models = ChatGPTPlanProvider(accounts).models(item["id"])
        print(f"Kết nối có {len(models)} model được phép xử lý.", flush=True)


if __name__ == "__main__":
    main()
