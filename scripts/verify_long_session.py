"""Exercise actual Qt navigation/catalog over a bounded, isolated long session.

Does not use teacher data, network, Office, playback or voice inference. Reports
sampling and workload explicitly; this is not a benchmark of the teaching PC.
"""

import argparse
import json
import logging
import tempfile
import time
from collections import deque
from pathlib import Path

import psutil
from PySide6.QtCore import QCoreApplication, QEvent, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.branding import configure_application
from app.library import Library
from app.library_location import write_record
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=3600)
    parser.add_argument('--output', type=Path, default=Path('reports/rc73/long-session.json'))
    args = parser.parse_args()
    if not 30 <= args.seconds <= 7200:
        parser.error('Use 30–7200 seconds.')
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    process = psutil.Process()
    with tempfile.TemporaryDirectory(prefix='biliclass-long-session-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        for index in range(120):
            library.create(f'Bài kiểm tra {index}', 'Liên môn', 'THPT', '11', [('Đoạn', 'Năng lượng được bảo toàn.')])
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings, samples, gaps = [], [], deque(maxlen=6000)
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.resize(1080, 700)
        started = last_tick = time.monotonic()
        navigations, ticks, longest = 0, 0, 0
        pages = ('home', 'new', 'voice', 'library', 'settings')

        def heartbeat():
            nonlocal last_tick, ticks, longest
            now = time.monotonic()
            gap = now - last_tick
            last_tick = now
            gaps.append(gap)
            longest = max(longest, gap)
            ticks += 1

        def navigate():
            nonlocal navigations
            window.setProperty('page', pages[navigations % len(pages)])
            navigations += 1
            if navigations % 20 == 0:
                bridge._catalog.refresh()

        def snapshot(final=False):
            elapsed = time.monotonic() - started
            ordered = sorted(gaps)
            sample = dict(seconds=round(elapsed, 2), rss_bytes=process.memory_info().rss,
                          handles=process.num_handles(), threads=process.num_threads())
            samples.append(sample)
            report = dict(status='failed' if warnings else 'passed' if final else 'running',
                          target_seconds=args.seconds, elapsed_seconds=round(elapsed, 2),
                          ticks=ticks, navigations=navigations, max_ui_gap_seconds=round(longest, 4),
                          recent_p95_gap_seconds=round(ordered[int((len(ordered)-1)*.95)], 4) if ordered else None,
                          samples=samples, qml_warnings=warnings,
                          scope='Actual Qt navigation and revision-aware catalog refresh calls, 120 synthetic lessons; '
                                'no network, teacher data, Office, voice inference or performance improvement claim.')
            write_record(args.output, report)
            print(json.dumps(sample), flush=True)
            if final:
                app.exit(1 if warnings else 0)

        beat, navigation, sample_timer = QTimer(), QTimer(), QTimer()
        beat.setInterval(20)
        beat.timeout.connect(heartbeat)
        navigation.setInterval(500)
        navigation.timeout.connect(navigate)
        sample_timer.setInterval(30000)
        sample_timer.timeout.connect(snapshot)
        for timer in (beat, navigation, sample_timer):
            timer.start()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        QTimer.singleShot(args.seconds * 1000, lambda: snapshot(True))
        result = app.exec()
        for timer in (beat, navigation, sample_timer):
            timer.stop()
        window.hide()
        for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                       bridge.english_reader, bridge.narration_preparation, bridge.classroom,
                       bridge.voice_controls, bridge.narrationPreferences):
            worker.shutdown()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        app.processEvents()
        library.close()
        logging.shutdown()
        return result


if __name__ == '__main__':
    raise SystemExit(main())
