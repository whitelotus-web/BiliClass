"""Local stack evidence for intermittent GUI stalls; no user text or locals."""

import faulthandler
import os

from PySide6.QtCore import QTimer


class UiWatchdog:
    def __init__(self, app, directory):
        path = directory / 'logs' / ('ui-hang-' + str(os.getpid()) + '.log')
        path.parent.mkdir(parents=True, exist_ok=True)
        self.output = path.open('w', encoding='utf-8')
        self.timer = QTimer(app)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.beat)
        app.aboutToQuit.connect(self.stop)
        self.beat()
        self.timer.start()

    def beat(self):
        if not self.output.closed:
            # The native watchdog can dump even when Python holds the GIL.
            faulthandler.dump_traceback_later(5, file=self.output)

    def stop(self):
        self.timer.stop()
        faulthandler.cancel_dump_traceback_later()
        if not self.output.closed:
            self.output.close()
