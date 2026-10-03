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
    parser.add_argument("--screenshot")
    parser.add_argument("--size", default="1366x850")
    parser.add_argument(
        "--page", choices=["home", "library", "new", "result", "editor", "glossary", "knowledge", "settings", "browser-ai", "classroom", "reports"], default="home"
    )
    args = parser.parse_args()
    if args.self_test:
        from .diagnostics import run

        return run(args.self_test)
    from .ui import run

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
