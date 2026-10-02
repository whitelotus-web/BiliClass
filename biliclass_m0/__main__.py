import argparse
import importlib
import json
import sys
import traceback

from .reporting import save_report

PROBES = ("system", "tts", "powerpoint", "lan", "translation")


def execute_probe(name: str) -> dict:
    if name not in PROBES:
        raise ValueError("Unknown experiment")
    try:
        module = importlib.import_module(f"biliclass_m0.probes.{name}")
        result = module.run()
    except Exception as exc:
        result = {
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "diagnostic": traceback.format_exc(),
        }
    save_report(name, result)
    return result


def main():
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="BiliClass M0 feasibility workbench")
    parser.add_argument("--probe", choices=(*PROBES, "all"))
    parser.add_argument("--smoke", action="store_true", help="Capture the app window and exit")
    parser.add_argument("--screenshot")
    parser.add_argument("--size", default="1366x768")
    parser.add_argument("--tab", type=int, default=0)
    args = parser.parse_args()
    if args.probe:
        names = PROBES if args.probe == "all" else [args.probe]
        results = {name: execute_probe(name) for name in names}
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return int(any(result.get("status") == "failed" for result in results.values()))
    from .ui import run

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
