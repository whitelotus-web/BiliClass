import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import output_root


def save_report(name: str, report: dict) -> Path:
    result = {"probe": name, "recorded_at": datetime.now(timezone.utc).isoformat(), **report}
    target = output_root() / f"{name}.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)
    return target


def load_reports() -> dict:
    result = {}
    for path in output_root().glob("*.json"):
        try:
            result[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return result
