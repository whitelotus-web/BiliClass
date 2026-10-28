"""Verify updater handoff happens after the real desktop closes its library."""

import json
import logging
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtCore import QTimer

from app import desktop
from app.ui import Bridge


def main():
    report = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/update-handoff')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-handoff-') as temporary:
        state = {}

        class UpdateBridge(Bridge):
            def __init__(self, library):
                super().__init__(library)
                state['library'] = library
                self._update_package = Path(temporary) / 'verified-package'

                def begin():
                    if self.googleSettings.loading:
                        QTimer.singleShot(25, begin)
                        return
                    self.applyDownloadedUpdate()
                    assert self._update_applying
                    assert not state.get('launched'), 'Installer must wait for desktop cleanup'

                QTimer.singleShot(100, begin)

        def install(package, process_id):
            assert process_id == os.getpid()
            assert package == Path(temporary) / 'verified-package'
            try:
                state['library'].db.execute('SELECT 1')
            except sqlite3.ProgrammingError:
                state['launched'] = True
            else:
                raise AssertionError('Library was still open at installer handoff')

        args = SimpleNamespace(smoke=True, seed_demo=False, size='1366x850', page='word',
                               screenshot=str(report / 'timeout.png'), lesson_id=None)
        with patch.dict(os.environ, BILICLASS_DATA=temporary), patch.object(desktop, 'Bridge', UpdateBridge), \
                patch('app.updater.launch_install', install):
            assert desktop.run(args) == 0
        assert state.get('launched'), 'Desktop did not hand off the verified update'
        result = dict(status='passed', installer_after_library_close=True, old_process_not_forced=True)
        (report / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)
        logging.shutdown()


if __name__ == '__main__':
    main()
