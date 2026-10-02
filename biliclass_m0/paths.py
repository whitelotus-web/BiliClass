"""Local resources and experiment outputs; never use the current directory implicitly."""

import os
import sys
from pathlib import Path

RESOURCES = Path(__file__).resolve().parent
ROOT = RESOURCES.parent


def data_root() -> Path:
    configured = os.environ.get("BILICLASS_M0_DATA")
    if configured:
        return Path(configured).expanduser().resolve()
    if getattr(sys, "frozen", False):
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "BiliClass" / "M0"
    return ROOT / ".runtime"


def output_root() -> Path:
    path = data_root() / "reports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def model_root() -> Path:
    path = data_root() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path
