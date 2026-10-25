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
    parser.add_argument('--startup-splash', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument(
        "--self-test", metavar="REPORT_JSON", help="Test the local pipeline with disposable data"
    )
    parser.add_argument("--seed-demo", action="store_true", help="Create an example only in an empty library")
    parser.add_argument(
        "--check-picture-ocr", nargs=2, metavar=("INPUT_PPTX", "REPORT_JSON"), help=argparse.SUPPRESS
    )
    parser.add_argument('--check-native-preview', nargs=2, metavar=('INPUT_PPTX', 'REPORT_JSON'), help=argparse.SUPPRESS)
    parser.add_argument('--check-voice-ui', metavar='REPORT_JSON', help=argparse.SUPPRESS)
    parser.add_argument('--check-narration-ui', metavar='REPORT_JSON', help=argparse.SUPPRESS)
    parser.add_argument('--check-universal-templates', metavar='REPORT_JSON', help=argparse.SUPPRESS)
    parser.add_argument('--register-shortcut', metavar='BILICLASS_LNK', help=argparse.SUPPRESS)
    parser.add_argument("--screenshot")
    parser.add_argument("--lesson-id", help="Open a saved lesson in the guarded desktop entry point")
    parser.add_argument('--office-task', help=argparse.SUPPRESS)
    parser.add_argument("--size", default="1366x850")
    parser.add_argument(
        "--page",
        choices=[
            "home",
            "library",
            "voice",
            "new",
            "word",
            "word-library",
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
    if args.startup_splash:
        from .startup_splash import run

        return run()
    if args.register_shortcut:
        from .windows_identity import register_shortcut

        register_shortcut(args.register_shortcut)
        return 0
    if args.office_task:
        from .office_tasks import worker_main

        return worker_main(args.office_task)
    if args.check_universal_templates:
        from .universal_templates import diagnose

        return diagnose(args.check_universal_templates)
    if args.check_voice_ui:
        from .voice_diagnostics import run

        return run(args.check_voice_ui)
    if args.check_narration_ui:
        from .narration_diagnostics import run

        return run(args.check_narration_ui)
    if args.check_native_preview:
        import hashlib
        import json
        import traceback
        from pathlib import Path

        from .paths import user_data
        from .powerpoint_review import render_preview_pages

        source, report = args.check_native_preview
        try:
            digest = hashlib.sha256(Path(source).read_bytes()).hexdigest()
            folder, _ = render_preview_pages(source, [1], user_data(), digest)
            result = {'image': str(folder / 'slide-1.png'), 'sha256': digest}
        except Exception as exc:
            result = {'error': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        Path(report).parent.mkdir(parents=True, exist_ok=True)
        Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        return 1 if 'error' in result else 0
    if args.check_picture_ocr:
        import json
        from pathlib import Path
        from threading import Event

        from .paths import user_data
        from .picture_ocr import extract_pictures

        source, report = args.check_picture_ocr
        try:
            result = extract_pictures(source, user_data(), Event())
        except Exception as exc:
            result = {"error": type(exc).__name__, "message": str(exc)}
        Path(report).parent.mkdir(parents=True, exist_ok=True)
        Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return 1 if "error" in result else 0
    if args.self_test:
        from .diagnostics import run

        return run(args.self_test)
    from .startup_splash import start

    args.startup_screen = start(enabled=not args.smoke)
    try:
        from .ui import run

        return run(args)
    finally:
        args.startup_screen.close()


if __name__ == "__main__":
    raise SystemExit(main())
