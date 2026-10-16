import argparse
import os


def main():
    # BiliClass uses no third-party Pydantic plugins. Avoid scanning every
    # installed distribution before creating the desktop or classroom process.
    os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "__all__")
    from multiprocessing import freeze_support

    freeze_support()
    parser = argparse.ArgumentParser(description="BiliClass bilingual lesson workspace")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--self-test", metavar="REPORT_JSON", help="Test the local pipeline with disposable data"
    )
    parser.add_argument("--seed-demo", action="store_true", help="Create an example only in an empty library")
    parser.add_argument(
        "--check-picture-ocr", nargs=2, metavar=("INPUT_PPTX", "REPORT_JSON"), help=argparse.SUPPRESS
    )
    parser.add_argument("--screenshot")
    parser.add_argument("--lesson-id", help="Open a saved lesson in the guarded desktop entry point")
    parser.add_argument("--size", default="1366x850")
    parser.add_argument(
        "--page",
        choices=[
            "home",
            "library",
            "new",
            "result",
            "editor",
            "reference",
            "glossary",
            "knowledge",
            "settings",
            "browser-ai",
            "classroom",
            "reports",
        ],
        default="home",
    )
    args = parser.parse_args()
    if args.check_picture_ocr:
        import json
        from pathlib import Path
        from threading import Event

        from .paths import user_data
        from .picture_ocr import extract_pictures

        source, report = args.check_picture_ocr
        result = extract_pictures(source, user_data(), Event())
        Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0
    if args.self_test:
        from .diagnostics import run

        return run(args.self_test)
    from .ui import run

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
