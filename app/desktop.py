"""Desktop lifecycle, startup verification, background services and shutdown."""
import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QThread, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from . import speech
from .jobs import Job
from .library import Library
from .paths import RESOURCE_ROOT, user_data
from .ui import Bridge


def run(args):
    startup = getattr(args, 'startup_screen', None)
    speech._ISOLATED_SYNTHESIS = True
    from .branding import configure_application

    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle("Basic")
    for font in (RESOURCE_ROOT / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Be Vietnam Pro", 10))
    from .library_location import verify_transfer_start

    try:
        if startup:
            startup.stage('library')
        directory = user_data()
        marker = directory / 'library-transfer.json'
        if not args.smoke and marker.exists() and not json.loads(marker.read_text(encoding='utf-8')).get('activated'):
            from .startup_progress import run_with_progress

            run_with_progress(app, lambda progress: verify_transfer_start(directory, progress),
                              'Đang xác minh thư viện sau khi chuyển ổ')
        else:
            verify_transfer_start(directory)
    except Exception as exc:
        if startup:
            startup.close()
        if os.name == 'nt' and not args.smoke:
            import ctypes

            ctypes.windll.user32.MessageBoxW(None, str(exc), 'BiliClass · Nơi lưu thư viện', 0x10)
        return 1
    library = Library(directory)
    watchdog = None
    if not args.smoke:
        from .ui_watchdog import UiWatchdog

        watchdog = UiWatchdog(app, directory)
    if args.seed_demo and not library.list_lessons():
        lesson = library.create(
            "Thảo luận và lập luận",
            "Liên môn",
            "THPT",
            "10",
            [
                ("Hoạt động mở đầu", "Hãy thảo luận theo nhóm và trình bày ý kiến của em."),
                ("Gợi ý thảo luận", "Em có thể đưa ra một ví dụ để giải thích ý kiến này không?"),
                ("Tổng kết", "So sánh các cách giải thích và nêu lý do cho lựa chọn của em."),
            ],
        )
        library.edit_segment(
            lesson["id"],
            lesson["segments"][0]["id"],
            lesson["segments"][0]["vi"],
            "Discuss in groups and share your ideas.",
            True,
        )
        library.save_term("Liên môn", "lập luận", "reasoning")
    bridge = Bridge(library)
    if startup:
        startup.stage('interface')
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", bridge)
    warnings = []
    engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml" / "Main.qml")))
    if not engine.rootObjects():
        print("\n".join(warnings))
        if watchdog is not None:
            watchdog.stop()
        library.close()
        return 1
    window = engine.rootObjects()[0]
    if startup:
        startup_pending = True
        def startup_ready():
            nonlocal startup_pending
            if not startup_pending:
                return
            startup_pending = False
            window.frameSwapped.disconnect(startup_ready)
            startup.finish()
        window.frameSwapped.connect(startup_ready)
    if os.name == 'nt':
        from .windows_identity import configure_window

        try:
            configure_window(window)
        except OSError:
            bridge.logger.warning('Windows taskbar identity could not be registered')
    companion = window.findChild(QObject, 'companionWindow')

    def hide_windows():
        companion.setProperty('disposing', True)
        for view in app.topLevelWindows():
            view.hide()

    app.aboutToQuit.connect(hide_windows)
    if not args.smoke:
        QTimer.singleShot(0, lambda: bridge.showCompanion(companion))
    width, height = (int(n) for n in args.size.split("x"))
    window.resize(width, height)
    lesson_id = getattr(args, "lesson_id", None)
    if lesson_id:
        bridge.openLesson(lesson_id)
    elif args.page in {"editor", "result"} and library.list_lessons():
        bridge.openLesson(library.list_lessons()[0]["id"])
    window.setProperty("page", "result" if lesson_id and args.page == "home" else
                       "settings" if args.page == "browser-ai" else args.page)
    if args.page == "browser-ai":
        window.findChild(QObject, "settingsPage").setProperty("activeTab", 6)

    def capture():
        path = Path(args.screenshot or user_data() / "screenshot.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        saved = QQuickWindow.grabWindow(window).save(str(path))
        path.with_suffix(".json").write_text(
            json.dumps(
                {
                    "screenshot": str(path),
                    "saved": saved,
                    "warnings": warnings,
                    "size": [width, height],
                    "page": args.page,
                    "current_page": window.property('page'),
                    "experimental_teaching": bridge.experimentalTeaching,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        app.exit(0 if saved and not warnings else 1)

    if args.smoke:
        QTimer.singleShot(2000, capture)
    bridge._automatic_backup = backup_job = Job(lambda: bridge.storage.backup(daily=True), bridge)
    backup_job.completed.connect(bridge.storage.finish_backup)
    if not args.smoke:
        def start_backup():
            if bridge.busy or bridge.narrationBusy or bridge.powerpoint_worker or bridge.storage.state.get('running'):
                QTimer.singleShot(30_000, start_backup)
                return
            if not bridge.storage.moving:
                bridge.storage.begin_backup()
                backup_job.start(QThread.LowPriority)
        QTimer.singleShot(1000, start_backup)
        QTimer.singleShot(4000, lambda: bridge.checkForUpdates(True))
    from .library_location import cleanup_previous

    bridge._storage_cleanup = cleanup_job = Job(lambda: cleanup_previous(library.directory), bridge)
    cleanup_job.completed.connect(lambda count, error: bridge.inform(
        'Đã mở thư viện mới; một số tệp cũ chưa dọn được: ' + error, True) if error else None)
    if not args.smoke:
        QTimer.singleShot(1500, cleanup_job.start)
    result = app.exec()
    if watchdog is not None:
        watchdog.stop()
    if cleanup_job.isRunning():
        cleanup_job.wait()
    bridge.browserAI.shutdown()
    bridge.googleSettings.shutdown()
    bridge._library_preferences.shutdown()
    if backup_job.isRunning():
        backup_job.wait()
    if bridge.update_worker and bridge.update_worker.isRunning():
        bridge._update_cancel.set()
        bridge.update_worker.wait()
    bridge.classroom.shutdown()
    bridge.voice_controls.shutdown()
    if bridge.powerpoint_worker:
        bridge.stopPowerPoint()
        bridge.powerpoint_worker.wait()  # Helper supervisor has its own bounded shutdown.
    bridge.teaching_session.clear()
    if bridge.worker:
        bridge.worker.wait()  # closing is disabled while jobs run; also safe on OS shutdown
    bridge.english_reader.shutdown()
    bridge._catalog.shutdown()
    bridge.narration_preparation.shutdown()
    bridge._narration_preferences.shutdown()
    bridge._companion_preferences.shutdown()
    bridge.slidePreview.shutdown()
    bridge.libraryThumbnails.shutdown()
    bridge.inputDocuments.shutdown()
    speech.stop()
    from .speech_process import shutdown

    shutdown()
    # QML bindings may still read the library while their objects are destroyed.
    engine.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    bridge.library.close()
    del engine
    if bridge.storage.next_directory:
        from PySide6.QtCore import QProcess, QProcessEnvironment

        from .library_location import finalize_transfer, select_directory

        try:
            if bridge.storage.transfer_record:
                from .startup_progress import run_with_progress

                destination = run_with_progress(app, lambda progress: finalize_transfer(
                    bridge.storage.transfer_record, progress), 'Đang chốt dữ liệu và đổi đường dẫn thư viện')
            else:
                destination = Path(bridge.storage.next_directory)
            select_directory(destination)
            process = QProcess()
            environment = QProcessEnvironment.systemEnvironment()
            environment.insert('BILICLASS_DATA', str(destination))
            process.setProcessEnvironment(environment)
            process.setProgram(sys.executable)
            process.setArguments(([] if getattr(sys, 'frozen', False) else ['-m', 'app']) + ['--page', 'settings'])
            if not process.startDetached()[0]:
                raise ValueError('Chưa mở lại được ứng dụng. Mở BiliClass để tiếp tục với thư viện mới.')
        except Exception as exc:
            (library.directory / 'transfer-error.txt').write_text(str(exc), encoding='utf-8')
            return 1
    return result
