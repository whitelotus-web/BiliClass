"""Check the simplified menus and legacy lesson editor using disposable data."""

import json
import tempfile
from pathlib import Path

from PySide6.QtCore import QEventLoop, QObject, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def pump():
    loop = QEventLoop()
    QTimer.singleShot(180, loop.quit)
    loop.exec()


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    for font in (RESOURCE_ROOT / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Be Vietnam Pro", 10))
    messages, checks = [], []
    with tempfile.TemporaryDirectory(prefix="biliclass-simple-", ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        library.save_term("Toán", "cấp số cộng", "arithmetic progression", True)
        lesson = library.create("Bài cũ", "Toán", "THPT", "11", [("Ý 1", "Cấp số cộng.")])
        lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "Cấp số cộng.", "Arithmetic progression.", True)
        lesson.update(level=5, layout="english_rescue")
        library._write(lesson)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        engine.warnings.connect(lambda values: messages.extend(v.toString() for v in values))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
        assert engine.rootObjects(), messages
        window = engine.rootObjects()[0]

        def find(name):
            item = window.findChild(QObject, name)
            if item is None:
                queue = [window.contentItem()]
                while queue:
                    current = queue.pop()
                    if current.objectName() == name:
                        return current
                    queue.extend(current.childItems())
            return item

        def control(name):
            item = find(name)
            assert item is not None, name
            return item

        def click(name):
            item = control(name)
            point = item.mapToScene(item.boundingRect().center()).toPoint()
            from PySide6.QtCore import Qt

            QTest.mouseClick(window, Qt.LeftButton, pos=point)
            pump()

        pump()
        assert find("navigationreference")
        assert find("navigationglossary") is None
        assert find("navigationknowledge") is None
        click("navigationreference")
        assert window.property("page") == "reference"
        assert any(term["vi"] == "cấp số cộng" for term in bridge.terms)
        click("foundationDataTab")
        assert window.property("referenceTab") == 1 and bridge.knowledgeStats["entries"] > 0
        click("teacherDataTab")
        assert window.property("referenceTab") == 0
        window.setProperty("page", "knowledge")
        pump()
        assert window.property("page") == "reference" and window.property("referenceTab") == 1
        checks.append("one data menu, both reference tabs, teacher data preserved and old route retained")
        window.setProperty("page", "new")
        pump()
        assert control("creationFormat").property("count") == 4
        checks.append("new conversion has exactly four methods")
        bridge.openLesson(lesson["id"])
        window.setProperty("page", "editor")
        pump()
        assert library.get(lesson["id"])["level"] == 5
        assert window.findChild(QObject, "translateButton") is None
        assert window.findChild(QObject, "translateToViButton") is None
        assert window.findChild(QObject, "translateMissingButton") is None
        assert control("enEditor").property("text") == "Arithmetic progression."
        checks.append("legacy L5 lesson opens without local translators; editor retains teacher text")
        assert not messages, messages
        reports = Path("reports/app")
        reports.mkdir(parents=True, exist_ok=True)
        window.setProperty("page", "reference")
        pump()
        window.grabWindow().save(str(reports / "streamlined-data.png"))
        (reports / "streamlined-ui.json").write_text(json.dumps({"status": "passed", "checks": checks}, ensure_ascii=False, indent=2), encoding="utf-8")
        window.close()
        engine.deleteLater()
        pump()
        library.close()
        print(json.dumps({"status": "passed", "checks": checks}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
