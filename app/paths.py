import os
from pathlib import Path

RESOURCE_ROOT = Path(__file__).resolve().parent


def user_data() -> Path:
    configured = os.environ.get("BILICLASS_DATA")
    root = Path(configured) if configured else Path(os.environ.get("LOCALAPPDATA", Path.home())) / "BiliClass"
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()
