"""Exercise teacher subject defaults and persisted class selection in real Qt."""

import json
import logging
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    out = Path('reports/rc69/defaults')
    out.mkdir(parents=True, exist_ok=True)
    warnings, checks = [], []
    with tempfile.TemporaryDirectory(prefix='bcl-conversion-defaults-', ignore_cleanup_errors=True) as temp:
        for phase in ('first', 'reopened'):
            library = Library(Path(temp) / 'data')
            bridge = Bridge(library)
            engine = QQmlApplicationEngine()
            engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
            engine.rootContext().setContextProperty('bridge', bridge)
            engine.load(RESOURCE_ROOT / 'qml/Main.qml')
            assert engine.rootObjects(), warnings
            window = engine.rootObjects()[0]
            window.resize(1366, 850)
            def c(name):
                return control(window, name)

            def choose(name, index):
                item = c(name)
                item.setProperty('currentIndex', index)
                assert QMetaObject.invokeMethod(item, 'activated', Qt.DirectConnection, Q_ARG(int, index))
                pump(80)

            try:
                pump(200)
                if phase == 'reopened':
                    assert bridge.defaultTeachingSubject == 'STEM – dự án, thực hành'
                    assert c('lessonSubject').property('currentText') == 'Khác'
                    assert c('creationCustomSubject').property('text') == bridge.defaultTeachingSubject
                    assert c('creationEducation').property('currentText') == 'THCS'
                    assert c('creationGrade').property('currentText') == '8'
                    assert c('settingsSubjects').property('currentText') == 'Khác'
                    assert c('settingsCustomSubject').property('text') == bridge.defaultTeachingSubject
                    checks.append('Subject and THCS/8 restored after closing and reopening library and QML')
                    continue

                assert c('lessonSubject').property('currentIndex') == -1
                assert c('creationEducation').property('currentText') == 'THPT'
                assert c('creationGrade').property('currentText') == '10'
                assert library.setting('conversion_class_selection', None) is None
                window.setProperty('page', 'settings')
                choose('settingsSubjects', bridge.conversionSubjects.index('Tin học'))
                assert not bridge.settings['subjects'], 'An unsaved choice must not change the profile'
                click(window, c('saveProfile'))
                assert bridge.defaultTeachingSubject == 'Tin học'
                assert c('lessonSubject').property('currentText') == 'Tin học'
                window.grabWindow().save(str(out / 'general-subject.png'))
                checks.append('Settings dropdown shares conversion subjects; default changes only after Save')

                window.setProperty('page', 'new')
                choose('lessonSubject', bridge.conversionSubjects.index('Vật lý'))
                choose('creationGrade', 1)
                assert bridge.conversionClassSelection == {'education': 'THPT', 'grade': '11'}
                window.setProperty('page', 'settings')
                full_name = 'Hoạt động trải nghiệm, hướng nghiệp'
                choose('settingsSubjects', bridge.conversionSubjects.index(full_name))
                click(window, c('saveProfile'))
                assert bridge.settings['subjects'] == [full_name], 'Do not split a curriculum subject at its comma'
                window.setProperty('page', 'new')
                assert c('lessonSubject').property('currentText') == 'Vật lý'
                assert c('creationGrade').property('currentText') == '11'
                bridge.navigate.emit('voice')
                pump(100)
                assert c('lessonSubject').property('currentText') == full_name
                assert c('creationGrade').property('currentText') == '11'
                checks.append('Per-lesson subject survives navigation/profile changes; new draft uses saved subject')

                window.setProperty('page', 'new')
                for index, education, grade in ((2, 'Tiểu học', '4'), (0, 'THPT', '12'), (1, 'THCS', '8')):
                    choose('creationEducation', index)
                    grades = bridge.educationGrades(education)
                    assert c('creationGrade').property('currentText') == grades[0]
                    choose('creationGrade', grades.index(grade))
                    assert bridge.conversionClassSelection == {'education': education, 'grade': grade}
                bridge.rememberConversionClass('THCS', '12')
                assert bridge.conversionClassSelection == {'education': 'THCS', 'grade': '8'}
                checks.append('All three education levels reset to a valid grade and persist the latest pair')

                window.setProperty('page', 'settings')
                choose('settingsSubjects', bridge.conversionSubjects.index('Khác'))
                c('settingsCustomSubject').setProperty('text', '')
                assert not c('saveProfile').isEnabled()
                c('settingsCustomSubject').setProperty('text', 'STEM – dự án, thực hành')
                click(window, c('saveProfile'))
                assert bridge.settings['subjects'] == ['STEM – dự án, thực hành']
                assert c('creationCustomSubject').property('text') == bridge.defaultTeachingSubject
                checks.append('Custom subjects, including commas, remain intact; empty custom subject cannot be saved')
            finally:
                window.hide()
                for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                               bridge.english_reader, bridge.narration_preparation, bridge.classroom, bridge.voice_controls):
                    worker.shutdown()
                engine.deleteLater()
                QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
                app.processEvents()
                library.close()
                logging.shutdown()
        assert not warnings, warnings
        result = {'status': 'passed', 'checks': checks, 'qml_warnings': warnings}
        (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
