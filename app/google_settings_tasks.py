"""Disk/key work for Google settings. Run on a worker, publish masked rows only."""

import os
from contextlib import closing

from .google_translation import DEFAULT_BUDGET, KeyStore
from .library import Library


def read_state(directory, store=None):
    store = store if store is not None else KeyStore(directory)
    rows = store.public()
    with closing(Library.read_only(directory)) as library:
        budget = library.setting('google_character_budget', DEFAULT_BUDGET)
    rows = [{**row, 'budget': budget, 'remaining': max(0, budget-row['used']-row['carryover']),
             'percent': min(100, (row['used']+row['carryover'])*100/max(1, budget))} for row in rows]
    from .local_ocr import model_paths
    from .translation_health import summarize
    from .vietnamese_ocr import pack_directory

    result = dict(keys=rows, configured=bool(rows), budget=budget, month=KeyStore.month(),
                  message='', ocrReady=bool(model_paths() and pack_directory()),
                  health=summarize(rows, budget), powerpointInstalled=False)
    if os.name == 'nt':
        import winreg
        from pathlib import Path

        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\POWERPNT.EXE') as key:
                    if Path(winreg.QueryValue(key, None).strip('"')).is_file():
                        result['powerpointInstalled'] = True
            except OSError:
                pass
    return result


def change(directory, operation, values):
    """A failed readback is still a failed save; the UI must retain its input."""
    try:
        store = KeyStore(directory)
        if operation == 'save':
            text, budget = values
            if text.strip():
                store.add(text)
            with closing(Library(directory)) as library:
                library.set_setting('google_character_budget', budget)
        elif operation == 'rename':
            store.rename(*values)
        elif operation == 'remove':
            store.remove(*values)
        elif operation == 'recheck':
            store.recheck()
        else:
            raise ValueError('Thao tác Google Dịch không hợp lệ.')
        state = read_state(directory, store)
        if operation == 'save' and values[0].strip() and not state['configured']:
            raise ValueError('Chưa đọc lại được key vừa lưu. Giữ nội dung nhập và thử lưu lại.')
        return {'state': state, 'error': ''}
    except Exception as exc:
        from .storage_space import FULL_DISK_MESSAGE, full_disk_error

        return {'state': None, 'error': FULL_DISK_MESSAGE if full_disk_error(exc) else str(exc)}
