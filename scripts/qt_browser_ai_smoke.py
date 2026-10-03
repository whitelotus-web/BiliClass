"""Compatibility entry point for the official ChatGPT plan Qt smoke."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("qt_chatgpt_plan_smoke.py")), run_name="__main__")
