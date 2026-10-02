"""Build a portable .biliknowledge release asset from a JSON source pack."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from app.knowledge import validate_pack


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    pack = validate_pack(json.loads(args.source.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ("manifest", "sources", "entries"):
            data = json.dumps(pack[name], ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
            archive.writestr(name + ".json", data)
    print(f"Created {args.output} · {len(pack['sources'])} sources · {len(pack['entries'])} entries")


if __name__ == "__main__":
    main()
