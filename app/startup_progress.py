"""A visible, responsive progress window for one-time library verification."""

import time

from PySide6.QtCore import QCoreApplication, QEvent, QUrl
from PySide6.QtQml import QQmlApplicationEngine

from .paths import RESOURCE_ROOT


def run_with_progress(app, action, title):
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/StartupProgress.qml')))
    roots = engine.rootObjects()
    window = roots[0] if roots else None
    if window:
        window.setProperty('operation', title)
    app.processEvents()
    updated = 0
    def progress(done, total):
        nonlocal updated
        now = time.monotonic()
        if window and (done == total or now - updated >= .08):
            updated = now
            window.setProperty('completed', done)
            window.setProperty('total', total)
            app.processEvents()
    try:
        return action(progress)
    finally:
        if window:
            window.hide()
        engine.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
