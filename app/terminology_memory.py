"""Small local reference memory; a machine draft never becomes a trusted term."""

import hashlib
import json
import sqlite3
import time
from pathlib import Path

from .subject_terms import subject_key

MAX_ROWS = 5000
MAX_DATABASE = 24 * 1024**2


class Memory:
    def __init__(self, directory):
        root = Path(directory) / 'translation_knowledge'
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / 'references.db'

    def connect(self):
        if self.path.exists() and self.path.stat().st_size > MAX_DATABASE:
            raise ValueError('Bộ nhớ tham chiếu đã đạt giới hạn; tiếp tục dùng kho tích hợp.')
        db = sqlite3.connect(self.path, timeout=2)
        try:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA busy_timeout=2000')
            db.execute('PRAGMA max_page_count=6144')
            db.execute('''CREATE TABLE IF NOT EXISTS references_seen (
                identity TEXT PRIMARY KEY, subject TEXT NOT NULL, term TEXT NOT NULL,
                record TEXT NOT NULL, last_seen REAL NOT NULL, sightings INTEGER NOT NULL DEFAULT 1)''')
            db.execute('''CREATE TABLE IF NOT EXISTS observations (
                identity TEXT PRIMARY KEY, subject TEXT NOT NULL, record TEXT NOT NULL, last_seen REAL NOT NULL)''')
        except Exception:
            db.close()
            raise
        return db

    @staticmethod
    def identity(subject, term):
        return hashlib.sha256((subject_key(subject) + '|' + ' '.join(term.casefold().split())).encode()).hexdigest()

    def get(self, subject, term):
        db = self.connect()
        try:
            row = db.execute('SELECT record,last_seen FROM references_seen WHERE identity=?',
                             (self.identity(subject, term),)).fetchone()
            if row:
                record = json.loads(row['record'])
                ttl = 86400 if isinstance(record, dict) and record.get('status') == 'unresolved' else 30 * 86400
                if time.time() - row['last_seen'] < ttl:
                    return record if isinstance(record, dict) else None
        finally:
            db.close()
        return None

    def remember(self, subject, term, record):
        # Only a reference result or a recorded miss may enter this store.
        if not isinstance(record, dict) or record.get('status') not in {'online_reference', 'unresolved'}:
            raise ValueError('Không lưu bản dịch máy thành thuật ngữ đã xác minh.')
        data = json.dumps(record, ensure_ascii=False)
        if len(data) > 2000 or len(term) > 100:
            return
        db = self.connect()
        try:
            with db:
                db.execute('''INSERT INTO references_seen VALUES(?,?,?,?,?,1)
                    ON CONFLICT(identity) DO UPDATE SET record=excluded.record,
                    last_seen=excluded.last_seen,sightings=references_seen.sightings+1''',
                    (self.identity(subject, term), subject_key(subject), term, data, time.time()))
                db.execute('DELETE FROM references_seen WHERE identity IN (SELECT identity FROM references_seen ORDER BY last_seen DESC LIMIT -1 OFFSET ?)', (MAX_ROWS,))
        finally:
            db.close()

    def record_lesson(self, identity, subject, record):
        # Summaries/IDs only: no copy of the PowerPoint, full lesson or API result.
        data = json.dumps(record, ensure_ascii=False)
        if len(data) > 4000:
            return
        db = self.connect()
        try:
            with db:
                db.execute('INSERT OR REPLACE INTO observations VALUES(?,?,?,?)',
                           (identity, subject_key(subject), data, time.time()))
                db.execute('DELETE FROM observations WHERE identity IN (SELECT identity FROM observations ORDER BY last_seen DESC LIMIT -1 OFFSET 500)')
        finally:
            db.close()

    def stats(self):
        db = self.connect()
        try:
            return dict(references=db.execute("SELECT COUNT(*) FROM references_seen WHERE json_extract(record,'$.status')='online_reference'").fetchone()[0],
                        unresolved=db.execute("SELECT COUNT(*) FROM references_seen WHERE json_extract(record,'$.status')='unresolved'").fetchone()[0],
                        lessons=db.execute('SELECT COUNT(*) FROM observations').fetchone()[0])
        finally:
            db.close()
