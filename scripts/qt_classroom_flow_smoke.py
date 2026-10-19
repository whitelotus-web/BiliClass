"""Real Qt -> owned server -> student WebSocket -> durable report, disposable data."""
import asyncio
import json
import multiprocessing
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx
from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump, until
from websockets.asyncio.client import connect

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


async def answer(info, token, round_id):
    async with connect(f"ws://127.0.0.1:{info['port']}/student", proxy=None) as ws:
        await ws.send(json.dumps({'token': token}))
        initial = json.loads(await ws.recv())
        assert 'correct' not in initial['round']
        await ws.send(json.dumps({'round_id': round_id, 'answer': 'A', 'submission_id': 'one'}))
        while True:
            result = json.loads(await ws.recv())
            if result.get('type') == 'ack':
                return result

def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc58/classroom')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-classflow-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        lesson = library.create('Năng lượng quanh ta', 'Vật lý', 'THPT', '11', [('Slide 1', 'Năng lượng được bảo toàn.')])
        lesson = library.edit_segment(lesson['id'], lesson['segments'][0]['id'], 'Năng lượng được bảo toàn.', 'Energy is conserved.', True)
        for number in (1, 2):
            lesson = library.save_question(lesson['id'], {'kind': 'single', 'vi': f'Câu {number}: Năng lượng có được bảo toàn?',
                'en': f'Question {number}: Is energy conserved?', 'options': [{'vi': 'Có', 'en': 'Yes'}, {'vi': 'Không', 'en': 'No'}],
                'correct': 'A', 'concept_id': lesson['segments'][0]['id'], 'concept_label': 'Năng lượng', 'approved': True})
        lesson = library.mark_prepared(lesson['id'], lesson['revision'])
        bridge = Bridge(library)
        bridge.classroom.refreshInterfaces = lambda: None
        bridge.classroom._interfaces = [{'name': 'Chỉ thử trên máy · 127.0.0.1', 'host': '127.0.0.1'}]
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        def c(name): return control(window, name)
        try:
            bridge.selectLessonForClass(lesson['id'])
            window.setProperty('page', 'classroom')
            until(lambda: bridge.readiness['prepared_ready'])
            c('classTitle').setProperty('text', 'Vật lý 11A thử')
            pump(200)
            click(window, c('classroomQuizButton'))
            assert c('teachingDialog').property('visible') and c('teachingTabs').property('currentIndex') == 1
            assert window.property('page') == 'classroom'
            QMetaObject.invokeMethod(c('teachingDialog'), 'close', Qt.DirectConnection)
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                pump(150)
                assert window.grabWindow().save(str(report/f'prepare-{width}.png'))
            assert c('startClassButton').isEnabled()
            click(window, c('startClassButton'))
            until(lambda: bridge.classroom.running and bool(bridge.classroom.joinUrl) and not bridge.busy, timeout=40)
            assert '127.0.0.1' in bridge.classroom.message
            info = bridge.classroom.runtime.info
            with httpx.Client(trust_env=False) as client:
                student = client.post(f"http://127.0.0.1:{info['port']}/api/join", json={'join': info['join']}).json()
            question_ids = [q['id'] for q in bridge.classroom.state['questions']]
            c('classroomQuestionPicker').setProperty('currentIndex', 1)
            QMetaObject.invokeMethod(c('classroomQuestionPicker'), 'activated', Qt.DirectConnection, Q_ARG(int, 1))
            pump(1800)
            assert c('classroomQuestionPicker').property('currentIndex') == 1, 'Polling reset selected question'
            click(window, c('openQuestionButton'))
            until(lambda: (bridge.classroom.state.get('round') or {}).get('status') == 'open')
            assert bridge.classroom.state['round']['question_id'] == question_ids[1]
            round_id = bridge.classroom.state['round']['id']
            assert c('classroomCountdown').isVisible()
            ack = asyncio.run(answer(info, student['token'], round_id))
            assert ack['answer'] == 'A'
            until(lambda: (bridge.classroom.state.get('round') or {}).get('answered') == 1)
            assert not c('classroomReveal').isEnabled()
            click(window, c('classroomCloseQuestion'))
            until(lambda: bridge.classroom.state['round']['status'] == 'closed')
            click(window, c('classroomReveal'))
            until(lambda: bridge.classroom.state['round']['status'] == 'revealed')
            assert window.grabWindow().save(str(report/'live.png'))
            session_id = bridge.classroom.state['session_id']
            bridge.classroom.disconnect()
            until(lambda: not bridge.classroom.busy and bridge.classroom.runtime is None)
            bridge.classroom.openReport(session_id)
            assert bridge.classroom.selectedReport['rounds'][0]['percent'] == 100
            bridge.classroom.start('', 'anonymous', 50, '127.0.0.1', session_id)
            until(lambda: bridge.classroom.running and bool(bridge.classroom.joinUrl) and not bridge.busy, timeout=40)
            assert bridge.classroom.state['round']['answered'] == 1
            click(window, c('classroomEnd'))
            QMetaObject.invokeMethod(c('classroomEndDialog'), 'accept', Qt.DirectConnection)
            until(lambda: bridge.classroom.selectedReport.get('status') == 'ended')
            click(window, c('classroomReportsButton'))
            assert window.property('page') == 'reports' and c('navigationclassroom').property('selected')
            selected = bridge.classroom.selectedReport
            assert selected['participants_joined'] == selected['participants_responded'] == 1
            bridge.classroom.exportReport((report/'summary.csv').resolve().as_uri())
            bridge.classroom.exportResponses((report/'responses.csv').resolve().as_uri())
            assert (report/'summary.csv').is_file() and (report/'responses.csv').is_file()
            assert window.grabWindow().save(str(report/'results.png'))
            bridge.classroom.disconnect()
            until(lambda: not bridge.classroom.busy and bridge.classroom.runtime is None)
            # The failure must be visible and must release the failed runtime.
            bridge.classroom.start('Lớp thử lỗi mạng', 'anonymous', 10, '203.0.113.9', '')
            until(lambda: not bridge.busy)
            assert not bridge.classroom.running and bridge.classroom.runtime is None
            assert 'Chưa mở được lớp' in bridge.classroom.message
            window.setProperty('page', 'settings')
            c('settingsPage').setProperty('activeTab', 5)
            pump(100)
            click(window, c('toggleDataOptions'))
            click(window, c('settingsReferenceButton'))
            assert window.property('page') == 'reference'
            click(window, c('openCompanion'))
            c('companionWindow').setProperty('collapsed', False)
            pump(150)
            assert not c('companionExplain').isEnabled() and not c('companionNext').isEnabled()
            assert not bridge.teaching_session.state['bound']
            assert c('companionBoundLesson').property('text') == 'Chưa gắn với bài giảng'
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings, 'checks': [
                'prepared lesson -> live server QR', 'question selection retained across polling',
                'student WebSocket answer and hidden correct answer', 'close/reveal/countdown states',
                'disconnect/resume retains response', 'end auto-selects report and CSV exports',
                'start failure clears runtime and explains error', 'reference accessible from settings',
                'mascot teaching controls locked without presentation']}
            (report/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            bridge.classroom.shutdown()
            window.close()
            bridge.libraryThumbnails.shutdown()
            bridge.slidePreview.shutdown()
            bridge._catalog.shutdown()
            bridge.browserAI.shutdown()
            bridge.english_reader.shutdown()
            bridge.narration_preparation.shutdown()
            bridge.voice_controls.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
    return 0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())
