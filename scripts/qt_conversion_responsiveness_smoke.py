"""Progress burst + a deliberately stalled WAV scan; no web or personal data."""
import json
import tempfile
import time
from pathlib import Path
from threading import Event, get_ident

from PySide6.QtCore import QCoreApplication, QEvent, QEventLoop, QObject, QPointF, QThread, Qt, QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QFont, QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app import library_catalog
from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def pump(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def until(test, timeout=10):
    end = time.monotonic() + timeout
    while not test():
        assert time.monotonic() < end, 'UI smoke timed out'
        pump(20)


app = QGuiApplication([])
configure_application(app)
QQuickStyle.setStyle('Basic')
for path in (RESOURCE_ROOT / 'assets').glob('*.ttf'):
    QFontDatabase.addApplicationFont(str(path))
app.setFont(QFont('Be Vietnam Pro', 10))
main_thread = get_ident()
entered, release = Event(), Event()
scans = []
original_status = library_catalog.audio_status


def blocked_status(lesson, directory, voices, *, cancel):
    assert get_ident() != main_thread, 'WAV scan blocked the GUI thread'
    scans.append(lesson['id'])
    entered.set()
    while not release.wait(.01):
        if cancel.is_set():
            raise InterruptedError()
    return {'status': 'none', 'mode': 'none', 'ready': False, 'label': 'Chỉ bài giảng song ngữ'}


library_catalog.audio_status = blocked_status
report = Path('reports/hang-rc37')
report.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='biliclass-responsive-', ignore_cleanup_errors=True) as directory:
    library = Library(Path(directory))
    for index in range(12):
        lesson = library.create(f'Bài {index}', 'Vật lý', 'THPT', '11', [('Năng lượng', 'Energy')])
        if index < 4:
            library.trash_lesson(lesson['id'])
    bridge = Bridge(library, translation_engine='browser_web')
    folder = Path(directory) / 'chatgpt' / 'fixture'
    folder.mkdir(parents=True)
    bridge._chatgpt_request = {'folder': str(folder), 'config': {'title': 'Kiểm tra giao diện phản hồi'}}
    bridge._browser_running = bridge._busy = True
    bridge._browser_state = {'running': True, 'phase': 'working', 'percent': 33, 'stage': 'translate',
                            'waiting': True, 'elapsedSeconds': 121, 'message': 'Đang biên soạn bài giảng song ngữ.'}
    engine = QQmlApplicationEngine()
    warnings = []
    engine.warnings.connect(lambda rows: warnings.extend(str(row) for row in rows))
    engine.rootContext().setContextProperty('bridge', bridge)
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
    assert engine.rootObjects(), warnings
    window = engine.rootObjects()[0]
    window.resize(1366, 850)
    window.setProperty('page', 'chatgpt')
    beats = []
    timer = QTimer()
    timer.setInterval(20)
    timer.timeout.connect(lambda: beats.append(time.monotonic()))
    timer.start()
    producer = None
    try:
        until(lambda: entered.is_set() and len(bridge.lessons) == 8)
        assert len(bridge.trashedLessons) == 4
        counts = {'progress': 0, 'broad': 0}
        bridge.browserStateChanged.connect(lambda: counts.__setitem__('progress', counts['progress'] + 1))
        bridge.changed.connect(lambda: counts.__setitem__('broad', counts['broad'] + 1))

        class ProgressBurst(QThread):
            def run(self):
                for index in range(200):
                    bridge.browserConversionProgress.emit({'percent': 33 + index % 3, 'stage': 'translate',
                        'waiting': True, 'elapsedSeconds': 121 + index // 100, 'message': 'Đang hoàn thiện nội dung song ngữ.'})
                    self.msleep(5)

        producer = ProgressBurst()
        producer.start()
        until(lambda: not producer.isRunning())
        pump(80)
        assert counts['progress'] == 200 and counts['broad'] == 0, counts
        burst_counts = dict(counts)
        assert len(scans) == 1, 'Progress must not queue another WAV scan'
        assert len(bridge.lessons) == 8 and len(bridge.trashedLessons) == 4
        gaps = [right-left for left, right in zip(beats, beats[1:])]
        assert len(beats) >= 15 and max(gaps, default=0) < .5, (len(beats), max(gaps, default=0))
        stop = window.findChild(QObject, 'browserConversionCancel')
        assert stop and stop.isVisible() and stop.isEnabled()
        point = stop.mapToScene(QPointF(stop.width()/2, stop.height()/2)).toPoint()
        started = time.monotonic()
        QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
        until(bridge.cancel_event.is_set)
        latency = time.monotonic()-started
        assert latency < .5 and not release.is_set(), latency
        assert (folder/'conversion-stopped').exists()
        assert window.grabWindow().save(str(report/'responsive.png'))
        release.set()
        until(lambda: bridge._catalog.worker is None)
        assert len(scans) == 8, 'Only active lessons may scan audio'
        assert not warnings, warnings
        result = {'status': 'passed', 'progress_events': burst_counts['progress'], 'broad_refreshes_during_progress': burst_counts['broad'],
                  'ui_ticks': len(beats), 'max_ui_gap_seconds': round(max(gaps), 4), 'stop_seconds': round(latency, 4),
                  'active_lessons': 8, 'trash_lessons': 4, 'wav_checks_on_ui': 0,
                  'scope': 'real Qt UI, deliberately stalled audio scan, synthetic progress, no web requests'}
        (report/'responsiveness.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False), flush=True)
    finally:
        release.set()
        if producer:
            producer.wait()
        bridge._catalog.shutdown()
        bridge._busy = bridge._browser_running = False
        timer.stop()
        window.close()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        app.processEvents()
        bridge.browserAI.shutdown()
        bridge.english_reader.shutdown()
        bridge.narration_preparation.shutdown()
        library.close()
        for handler in bridge.logger.handlers[:]:
            handler.close()
            bridge.logger.removeHandler(handler)
        library_catalog.audio_status = original_status
