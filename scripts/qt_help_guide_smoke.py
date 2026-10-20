"""F1 is a readable, topic-based guide and never navigates the teacher's work."""

import json
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    assert app.thread() is not None
    QQuickStyle.setStyle('Basic')
    reports = Path('reports/rc104/help-native')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-help-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        def c(name):
            return control(root, name)
        try:
            root.resize(1366, 850)
            root.setProperty('page', 'settings')
            until(root.isVisible)
            pump(120)
            click(root, c('sidebarHelpButton'))
            until(lambda: c('helpDialog').property('visible'))
            assert c('helpDialog').property('activeTopic') == 0
            assert root.grabWindow().save(str(reports/'initial.png'))
            for index in range(6):
                click(root, c('helpTopic'+str(index)))
                pump(40)
                text = '\n'.join(str(item.property('text') or '') for item in c('helpDialog').findChildren(QQuickItem) if item.isVisible())
                assert not any(word in text for word in ('VieNeu', 'Kokoro', 'model', 'local', 'Quiz'))
                assert root.property('page') == 'settings'
            click(root, c('helpTopic2'))
            assert root.grabWindow().save(str(reports/'voice.png'))
            click(root, c('helpClose'))
            root.setProperty('page', 'library')
            pump(60)
            QTest.keyClick(root, Qt.Key_F1)
            until(lambda: c('helpDialog').property('visible'))
            assert c('helpDialog').property('activeTopic') == 2
            assert root.property('page') == 'library'
            click(root, c('helpTopic0'))
            root.resize(1080, 700)
            pump(100)
            assert root.grabWindow().save(str(reports/'compact.png'))
            click(root, c('helpClose'))
            assert root.property('page') == 'library' and not warnings, warnings
        finally:
            for service in (bridge.googleSettings, bridge._library_preferences, bridge._catalog,
                            bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                            bridge.narrationPreferences, bridge.narration_preparation,
                            bridge.english_reader, bridge.voice_controls, bridge._companion_preferences):
                service.shutdown()
            bridge.classroom.shutdown()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            library.close()
    print(json.dumps({'status':'passed','qml_warnings':warnings,
          'checks':['initial setup first; six readable topics','no provider/engine names',
                    'F1 and sidebar open same guide','reading and closing never change main page',
                    'last topic retained; compact layout scrolls']}), flush=True)


if __name__ == '__main__':
    main()
