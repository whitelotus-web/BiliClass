import os
import sys
from pathlib import Path

RESOURCE_ROOT = Path(__file__).resolve().parent


def model_directory() -> Path:
    """Locate portable weights without importing any inference provider."""
    configured = os.environ.get("BILICLASS_MODEL_DIR")
    if configured:
        return Path(configured)
    portable = Path(sys.executable).parent / "models"
    if getattr(sys, "frozen", False) and portable.is_dir():
        return portable
    return user_data() / "models"


def user_data() -> Path:
    from .library_location import selected_directory

    configured = os.environ.get("BILICLASS_DATA")
    root = Path(configured) if configured else selected_directory()
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()
