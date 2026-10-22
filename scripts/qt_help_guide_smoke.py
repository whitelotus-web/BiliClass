"""F1 is a readable, topic-based guide and never navigates the teacher's work."""

import json
import os
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    assert app.thread() is not None
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT/'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    reports = Path(os.environ.get('BILICLASS_HELP_REPORT', 'reports/help-native'))
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
            assert '4 bước' in c('helpTopicHeading').property('text')
            for index in range(7):
                click(root, c('helpTopic'+str(index)))
                pump(40)
                text = '\n'.join(str(item.property('text') or '') for item in c('helpDialog').findChildren(QQuickItem) if item.isVisible())
                assert not any(word in text for word in ('VieNeu', 'Kokoro', 'model', 'local', 'Quiz'))
                assert root.property('page') == 'settings'
            guide = c('helpDialog')
            QTest.keyClick(root, Qt.Key_F, Qt.ControlModifier)
            assert c('helpSearch').hasActiveFocus()
            c('helpSearch').setProperty('text', 'am luong')
            pump(80)
            assert c('helpTopic3').isVisible() and c('helpTopic6').isVisible()
            assert not c('helpTopic1').isVisible()
            click(root, c('helpTopic3'))
            click(root, c('helpNext'))
            assert guide.property('activeTopic') == 6
            click(root, c('helpPrevious'))
            assert guide.property('activeTopic') == 3
            c('helpSearch').setProperty('text', 'zzzzkhongcotronghuongdan')
            pump(80)
            assert c('helpNoResults').isVisible() and not c('helpNext').isVisible()
            click(root, c('helpClearSearch'))
            assert not c('helpNoResults').isVisible()
            for theme in ('light', 'dark'):
                bridge.setApplicationTheme(theme)
                for width, height in ((1080,700),(1366,850)):
                    root.resize(width,height)
                    pump(100)
                    for topic in (0,3,6):
                        guide.setProperty('activeTopic',topic)
                        pump(80)
                        assert c('helpClose').mapToScene(QPointF()).y()+c('helpClose').height() <= root.height()
                        for item in guide.findChildren(QQuickItem):
                            if item.isVisible() and item.metaObject().indexOfProperty('contentWidth') >= 0 and item.width() > 0:
                                assert item.property('contentWidth') <= item.width()+1, (item.objectName(),item.property('text'))
                        assert root.grabWindow().save(str(reports/f'{theme}-{width}-topic-{topic}.png'))
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
    result = {'status':'passed','qml_warnings':warnings,
          'checks':['four-step quick start; seven readable topics','no provider/engine names',
                    'accent-insensitive search and no-results recovery; filtered next/previous',
                    'mouse and keyboard illustrations; light/dark 1080/1366',
                    'F1 and sidebar open same guide','reading and closing never change main page',
                    'last topic retained; compact layout scrolls']}
    (reports/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
