"""Export a whitelist of operational facts, never raw logs or classroom content."""

import platform
import shutil
import sqlite3
from collections import Counter
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .storage import backup_state


def error_category(message):
    text = str(message).casefold()
    for category, words in (
        ('storage', ('disk', 'dung lượng', 'enospc', 'sqlite_full', 'space', 'giới hạn')),
        ('office', ('powerpoint', 'rpc', 'com_error')),
        ('quota', ('quota', '429', 'hạn mức')),
        ('network', ('network', 'timeout', 'connection', 'mạng')),
        ('voice', ('voice', 'vieneu', 'giọng', 'wav')),
        ('quality', ('overflow', 'bố cục', 'slide')),
    ):
        if any(word in text for word in words):
            return category
    return 'other'


def create_report(directory, output):
    root = Path(directory)
    backup = backup_state(root)
    report = dict(schema_version=1, app_version=__version__, created_at=datetime.now(UTC).isoformat(),
                  system=dict(os=platform.system(), release=platform.release(), machine=platform.machine(),
                              python=platform.python_version()),
                  free_bytes=shutil.disk_usage(root).free,
                  backup=dict(status=backup.get('status', 'unknown'),
                              last_success=backup.get('last_success', ''),
                              last_error_category=error_category(backup.get('last_error', ''))
                              if backup.get('last_error') else ''),
                  databases={}, log_levels={}, privacy='No names, text, paths, keys, tokens, answers or raw logs')
    for name, tables in (('library.db', ('lessons', 'lesson_revisions')),
                         ('classroom.db', ('sessions', 'participants', 'answers'))):
        if not (root / name).is_file():
            continue
        with closing(sqlite3.connect((root / name).resolve().as_uri() + '?mode=ro', uri=True)) as db:
            available = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            report['databases'][name] = dict(integrity=db.execute('PRAGMA quick_check').fetchone()[0] == 'ok',
                counts={table: db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                        for table in tables if table in available})
    levels = Counter()
    for path in (root / 'logs').glob('app.log*'):
        with path.open(encoding='utf-8', errors='replace') as stream:
            for line in stream:
                words = line.split(maxsplit=3)
                if len(words) >= 3 and words[2] in {'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'}:
                    levels[words[2]] += 1
    report['log_levels'] = dict(levels)
    from .library_location import write_record

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_record(output, report)
    return output
