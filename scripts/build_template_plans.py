"""Emit the same template plans used by the app for editable sample decks."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.lesson_templates import catalog, example_plan


def main():
    destination = Path(sys.argv[1])
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = {preset["id"]: [example_plan(preset["id"], block["id"]) for block in catalog()["blocks"]]
              for preset in catalog()["presets"]}
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
