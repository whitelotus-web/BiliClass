"""Disk/key work for Google settings. Run on a worker, publish masked rows only."""

import os
import sqlite3
from contextlib import closing

from .google_translation import DEFAULT_BUDGET, KeyStore
from .library import Library
from .translation_provider import PROVIDERS, snapshot


def read_state(directory, store=None, *, provider=None):
    selection = snapshot(directory, provider, include_profile=False)
    provider = selection['translation_provider']
    # A broken inactive provider must not disable the selected one.
    google_error = ''
    try:
        store = store if store is not None else KeyStore(directory)
        rows = store.public()
    except (ValueError, OSError, sqlite3.DatabaseError) as exc:
        if provider == 'google':
            raise
        rows, google_error = [], str(exc)
    with closing(Library.read_only(directory)) as library:
        budget = library.setting('google_character_budget', DEFAULT_BUDGET)
    if type(budget) is not int or not 1 <= budget <= DEFAULT_BUDGET:
        # snapshot already validates the active budget. A damaged inactive
        # Google preference must not prevent opening another service's controls.
        budget = DEFAULT_BUDGET
    rows = [{**row, 'budget': budget, 'remaining': max(0, budget-row['used']-row['carryover']),
             'percent': min(100, (row['used']+row['carryover'])*100/max(1, budget))} for row in rows]
    from .local_ocr import model_paths
    from .translation_health import summarize
    from .vietnamese_ocr import pack_directory

    result = dict(keys=rows, configured=bool(rows), budget=budget, month=KeyStore.month(),
                  message='', ocrReady=bool(model_paths() and pack_directory()),
                  health=summarize(rows, budget), powerpointInstalled=False)
    from .azure_translation import DEFAULT_BUDGET as AZURE_BUDGET
    from .azure_translation import AzureKeyStore

    azure = dict(configured=False, keys=[], region='global', resource='', budget=AZURE_BUDGET, message='')
    try:
        azure_store = AzureKeyStore(directory)
        azure_rows = azure_store.public()
        azure_budget = snapshot(directory, 'azure')['translation_budget']
        azure.update(azure_store.configuration(), configured=bool(azure_rows), budget=azure_budget,
                     keys=[{**row, 'remaining': max(0, azure_budget-row['used']-row['carryover'])}
                           for row in azure_rows])
    except (ValueError, OSError, sqlite3.DatabaseError) as exc:
        azure['message'] = str(exc)
    result.update(provider=provider, providerLabel=PROVIDERS[provider], azure=azure,
                  activeConfigured=bool(rows) if provider == 'google' else azure['configured'],
                  message=google_error if provider == 'google' else azure['message'])
    from .alternative_translation import LIMITS, AlternativeStore

    alternatives = {}
    for name, limit in LIMITS.items():
        state = dict(configured=False, keys=[], budget=limit, message='', option='')
        try:
            alternative = AlternativeStore(directory, name)
            masked = alternative.public()
            state.update(configured=bool(masked), option=alternative.configuration(),
                keys=[{**row, 'remaining': max(0, limit-row['used']-row['carryover'])} for row in masked])
        except (ValueError, OSError, sqlite3.DatabaseError) as exc:
            state['message'] = str(exc)
        alternatives[name] = state
    result['alternatives'] = alternatives
    if provider in alternatives:
        result.update(activeConfigured=alternatives[provider]['configured'], message=alternatives[provider]['message'])
    from pathlib import Path

    from .terminology_seed import statistics

    knowledge = {**statistics(), 'enabled': selection['translation_knowledge_version'] > 0,
                 'online': selection['translation_knowledge_online'], 'references': 0, 'lessons': 0, 'unresolved': 0, 'message': ''}
    if (Path(directory) / 'translation_knowledge/references.db').is_file():
        from .terminology_memory import Memory

        try:
            knowledge.update(Memory(directory).stats())
        except (OSError, ValueError, sqlite3.DatabaseError):
            knowledge['message'] = 'Chưa đọc được bộ nhớ tham khảo; kho thuật ngữ tích hợp vẫn dùng được.'
    result['knowledge'] = knowledge
    from .translation_failover import service_states

    result['services'] = service_states(directory)
    result['fallbackConfigured'] = any(row['configured'] for row in result['services'])
    result['serviceWarning'] = ' · '.join(row['label'] + ': ' + row['status'] for row in result['services'] if row['warning'])
    if os.name == 'nt':
        import winreg
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
        store = KeyStore(directory) if operation in {'save', 'rename', 'remove', 'recheck'} else None
        if operation == 'save':
            text, budget = values
            if text.strip():
                store.add(text)
            with closing(Library(directory)) as library:
                library.set_setting('google_character_budget', budget)
            from .translation_failover import forget

            forget(directory, 'google')
        elif operation == 'rename':
            store.rename(*values)
        elif operation == 'remove':
            store.remove(*values)
        elif operation == 'recheck':
            store.recheck()
            from .translation_failover import forget

            forget(directory, 'google')
        elif operation == 'provider':
            from .translation_provider import SELECTABLE, validate

            provider, = values
            validate(provider)
            if provider not in SELECTABLE:
                raise ValueError('Azure chỉ được giữ để tiếp tục bài cũ. Chọn dịch vụ khác cho bài mới.')
            # Validate and mask the destination before publishing the selection.
            # A read failure cannot leave Settings displaying a different engine.
            state = read_state(directory, provider=provider)
            with closing(Library(directory)) as library:
                library.set_setting('translation_provider', provider)
            return {'state': state, 'error': ''}
        elif operation in {'azure_save', 'azure_remove', 'azure_recheck'}:
            from .azure_translation import AzureKeyStore

            azure = AzureKeyStore(directory)
            if operation == 'azure_save':
                azure.configure(*values)
            elif operation == 'azure_remove':
                azure.clear()
            else:
                azure.recheck()
        elif operation in {'alternative_save', 'alternative_remove', 'alternative_recheck', 'alternative_check'}:
            from .alternative_translation import AlternativeStore

            alternative = AlternativeStore(directory, values[0])
            if operation == 'alternative_save':
                alternative.configure(*values[1:])
                from .translation_failover import forget

                forget(directory, values[0])
            elif operation == 'alternative_remove':
                alternative.clear()
            elif operation == 'alternative_check':
                from .alternative_translation import check_connection

                check_connection(directory, values[0])
            else:
                alternative.recheck()
                from .translation_failover import forget

                forget(directory, values[0])
        else:
            raise ValueError('Thao tác Google Dịch không hợp lệ.')
        state = read_state(directory, store)
        if operation == 'save' and values[0].strip() and not state['configured']:
            raise ValueError('Chưa đọc lại được key vừa lưu. Giữ nội dung nhập và thử lưu lại.')
        if operation == 'azure_save' and not state['azure']['configured']:
            raise ValueError('Chưa đọc lại được cấu hình Azure vừa lưu. Giữ nội dung nhập và thử lại.')
        if operation == 'alternative_save' and not state['alternatives'][values[0]]['configured']:
            raise ValueError('Chưa đọc lại được cấu hình vừa lưu. Giữ nội dung nhập và thử lại.')
        return {'state': state, 'error': ''}
    except Exception as exc:
        from .storage_space import FULL_DISK_MESSAGE, full_disk_error

        return {'state': None, 'error': FULL_DISK_MESSAGE if full_disk_error(exc) else str(exc)}
