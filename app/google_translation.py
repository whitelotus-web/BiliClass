"""Google Translation Basic, bounded requests and machine-local credentials.

Keys are never returned to QML, logged, backed up or stored in the library DB.
Usage is a conservative local budget, NOT Google's billing/free-credit balance.
Keys without a project label share one budget. Keys for one project must share
the same label, including after key replacement.
"""

import ctypes
import hashlib
import html
import json
import os
import re
import sqlite3
import threading
import urllib.error
import urllib.request
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = 'https://translation.googleapis.com/language/translate/v2'
MAX_CHARS = 4500
MAX_ITEMS = 100
DEFAULT_BUDGET = 500_000
_LOCK = threading.RLock()


class TranslationProblem(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _atomic(path, data):
    pending = path.with_suffix('.tmp')
    pending.write_bytes(data)
    pending.replace(path)


def _crypt(data, decrypt=False):
    """Windows user-scoped DPAPI; fail closed on unsupported platforms."""
    if os.name != 'nt':
        raise TranslationProblem('api_settings', 'Lưu API key an toàn hiện hỗ trợ Windows.')

    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_char))]

    buffer = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    target = Blob()
    crypt = ctypes.WinDLL('crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    function = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    function.restype = wintypes.BOOL
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise TranslationProblem('api_settings', 'Không mở/lưu được API key trên tài khoản Windows này. Nhập lại key trong Cài đặt.')
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        kernel.LocalFree(ctypes.cast(target.data, ctypes.c_void_p))


class KeyStore:
    def __init__(self, directory):
        self.root = Path(directory) / 'translation_api'
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'keys.dpapi'
        with closing(self.connect()) as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS usage(month TEXT, project TEXT, characters INTEGER NOT NULL,
                    PRIMARY KEY(month,project));
                CREATE TABLE IF NOT EXISTS blocked(month TEXT, key_id TEXT, code TEXT,
                    PRIMARY KEY(month,key_id));
                CREATE TABLE IF NOT EXISTS cache(id TEXT PRIMARY KEY, value TEXT NOT NULL);
            ''')

    def connect(self):
        return sqlite3.connect(self.root / 'usage.db', timeout=10)

    def keys(self):
        with _LOCK:
            if not self.path.exists():
                return []
            try:
                rows = json.loads(_crypt(self.path.read_bytes(), decrypt=True))
                if not isinstance(rows, list) or any(not isinstance(r, dict) or
                        set(r) != {'id', 'project', 'key'} for r in rows):
                    raise ValueError()
                return rows
            except (ValueError, OSError) as exc:
                if isinstance(exc, TranslationProblem):
                    raise
                raise TranslationProblem('api_settings', 'Danh sách API key không đọc được; nhập lại trong Cài đặt.') from None

    def add(self, text):
        candidates = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if '|' in line:
                project, key = (part.strip() for part in line.split('|', 1))
            else:
                project, key = 'Mặc định', line
            if not project or len(project) > 100 or not re.fullmatch(r'[A-Za-z0-9_-]{30,200}', key):
                raise TranslationProblem('api_settings', 'Mỗi dòng nhập một key hoặc Tên dự án | key. Kiểm tra lại định dạng, không dán URL.')
            candidates.append({'id': _digest(key), 'project': project.casefold(), 'key': key})
        if not candidates or len(candidates) > 50:
            raise TranslationProblem('api_settings', 'Nhập từ 1 đến 50 API key, mỗi key một dòng.')
        with _LOCK:
            rows = self.keys()
            by_id = {r['id']: r for r in rows}
            for row in candidates:
                if row['id'] in by_id and by_id[row['id']]['project'] != row['project']:
                    raise TranslationProblem('api_settings', 'Key đã lưu thuộc nhóm dự án khác. Giữ đúng tên dự án để không đếm lại hạn mức.')
                by_id[row['id']] = row
            if len(by_id) > 50:
                raise TranslationProblem('api_settings', 'Tối đa 50 key đã lưu. Xóa key cũ trước khi thêm.')
            _atomic(self.path, _crypt(json.dumps(list(by_id.values())).encode('utf-8')))

    def remove(self, key_id):
        with _LOCK:
            rows = [r for r in self.keys() if r['id'] != key_id]
            _atomic(self.path, _crypt(json.dumps(rows).encode('utf-8')))
        # Never delete accounting when deleting/re-adding a credential.

    @staticmethod
    def month():
        return datetime.now(timezone.utc).strftime('%Y-%m')

    def public(self):
        with closing(self.connect()) as db:
            used = dict(db.execute('SELECT project,characters FROM usage WHERE month=?', (self.month(),)))
            blocked = dict(db.execute('SELECT key_id,code FROM blocked WHERE month=?', (self.month(),)))
        return [{'id': row['id'], 'project': row['project'], 'label': '•••• ' + row['key'][-4:],
                 'used': used.get(row['project'], 0), 'blocked': blocked.get(row['id'], '')}
                for row in self.keys()]

    def reserve(self, count, budget, excluded=(), only_key=None):
        """Atomic across workers/processes. Debit BEFORE send, including ambiguity."""
        with _LOCK, closing(self.connect()) as db:
            month = self.month()
            rows = self.keys()
            if not rows:
                raise TranslationProblem('api_settings', 'Thêm Google Cloud Translation API key trong Cài đặt → Google Dịch.')
            with db:
                db.execute('BEGIN IMMEDIATE')
                for row in rows:
                    if only_key is not None and row['id'] != only_key:
                        continue
                    if row['id'] in excluded or db.execute('SELECT 1 FROM blocked WHERE month=? AND key_id=?',
                                                         (month, row['id'])).fetchone():
                        continue
                    used = db.execute('SELECT characters FROM usage WHERE month=? AND project=?',
                                      (month, row['project'])).fetchone()
                    if (used[0] if used else 0) + count > budget:
                        continue
                    db.execute('INSERT INTO usage VALUES(?,?,?) ON CONFLICT(month,project) DO UPDATE SET characters=characters+excluded.characters',
                               (month, row['project'], count))
                    return {**row, 'month': month}
        raise TranslationProblem('api_budget', 'Các key đã hết giới hạn cục bộ hoặc chưa dùng được. Kiểm tra hạn mức/thanh toán trong Google Cloud; phần dịch xong đã lưu.')

    def reject(self, row, count, code):
        # A definitive rejected request is not translated; network/timeout
        # ambiguity is deliberately NOT refunded.
        with closing(self.connect()) as db, db:
            month = row.get('month', self.month())
            db.execute('UPDATE usage SET characters=MAX(0,characters-?) WHERE month=? AND project=?',
                       (count, month, row['project']))
            if code in {'api_key', 'api_quota'}:
                db.execute('INSERT OR REPLACE INTO blocked VALUES(?,?,?)', (month, row['id'], code))

    def recheck(self):
        with closing(self.connect()) as db, db:
            db.execute('DELETE FROM blocked')

    def cached(self, key):
        with closing(self.connect()) as db:
            row = db.execute('SELECT value FROM cache WHERE id=?', (key,)).fetchone()
        return row[0] if row else None

    def cache(self, key, value):
        self.cache_many([(key, value)])

    def cache_many(self, rows):
        with closing(self.connect()) as db, db:
            db.executemany('INSERT OR REPLACE INTO cache VALUES(?,?)', rows)


def request(texts, key, source, target):
    """Only fixed Google HTTPS endpoint, key in header, bounded response/time."""
    data = json.dumps({'q': texts, 'source': source, 'target': target,
                       'format': 'html', 'model': 'nmt'}).encode('utf-8')
    outgoing = urllib.request.Request(ENDPOINT, data=data, method='POST',
        headers={'Content-Type': 'application/json; charset=utf-8', 'X-Goog-Api-Key': key})
    try:
        # No redirect may forward credentials to another host.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        with urllib.request.build_opener(NoRedirect).open(outgoing, timeout=20) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise TranslationProblem('api_result', 'Kết quả dịch vượt giới hạn cho phép.')
        result = json.loads(raw)['data']['translations']
        if not isinstance(result, list) or len(result) != len(texts):
            raise ValueError()
        values = [row['translatedText'] for row in result]
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError()
        return values
    except urllib.error.HTTPError as exc:
        status = exc.code
        # Never expose provider error text: it can echo a key or source text.
        if status == 429:
            code = 'api_rate'
        elif status in {400, 401, 403}:
            code = 'api_key' if status != 400 else 'api_request'
            try:
                payload = json.loads(exc.read(65536))
                reasons = {r.get('reason') for r in payload.get('error', {}).get('errors', [])}
                if reasons & {'keyInvalid', 'accessNotConfigured', 'ipRefererBlocked'}:
                    code = 'api_key'
                if reasons & {'dailyLimitExceeded', 'userRateLimitExceeded', 'quotaExceeded'}:
                    code = 'api_quota'
                elif reasons & {'rateLimitExceeded'}:
                    code = 'api_rate'
            except (ValueError, TypeError, AttributeError):
                pass
        elif status >= 500:
            code = 'api_network'
        else:
            code = 'api_request'
        raise TranslationProblem(code, 'Google Dịch chưa nhận được yêu cầu hợp lệ. Kiểm tra key, bật Cloud Translation API, thanh toán và hạn mức của dự án.') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise TranslationProblem('api_network', 'Kết nối Google Dịch gián đoạn. Các phần đã dịch vẫn được lưu để tiếp tục.') from None
    except (ValueError, KeyError, TypeError):
        raise TranslationProblem('api_result', 'Google Dịch trả kết quả chưa hợp lệ; phần đã xong vẫn được lưu.') from None


def protected_html(text):
    # Protect arithmetic, LaTeX spans and native OOXML placeholder tokens.
    pattern = r'⟦BLC\d+⟧|\$[^$]+\$|[+−-]?\d+(?:[.,]\d+)*(?:\s*%)?'
    locks = []
    parts, last = [], 0
    for match in re.finditer(pattern, text):
        parts.append(html.escape(text[last:match.start()]))
        token = f'BCLLOCK{len(locks)}END'
        locks.append(match.group())
        parts.append('<span translate="no" class="notranslate">' + token + '</span>')
        last = match.end()
    parts.append(html.escape(text[last:]))
    return ''.join(parts), locks


def unprotect(value, locks):
    from html.parser import HTMLParser

    class Text(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []

        def handle_data(self, data):
            self.parts.append(data)

    parser = Text()
    parser.feed(value)
    text = ''.join(parser.parts)
    expected = [f'BCLLOCK{i}END' for i in range(len(locks))]
    if sorted(re.findall(r'BCLLOCK\d+END', text)) != sorted(expected):
        raise TranslationProblem('api_result', 'Bản dịch chưa giữ đủ số liệu/công thức; chưa áp dụng kết quả này.')
    for token, original in zip(expected, locks, strict=True):
        text = text.replace(token, original)
    if not text.strip() or any(ord(c) < 32 and c not in '\n\r\t' for c in text):
        raise TranslationProblem('api_result', 'Văn bản dịch chưa hợp lệ.')
    return text


def chunks(text, maximum=1000):
    """Keep exact separators and bound even a long unbroken source string."""
    result = []
    while len(text) > maximum:
        cut = max(text.rfind('\n', 0, maximum), text.rfind('. ', 0, maximum), text.rfind(' ', 0, maximum))
        cut = cut + 1 if cut > maximum // 2 else maximum
        # Never cut a native/math placeholder in half.
        for match in re.finditer(r'⟦BLC\d+⟧|\$[^$]+\$', text):
            if match.start() < cut < match.end():
                cut = match.start() or match.end()
                break
        result.append(text[:cut])
        text = text[cut:]
    if text:
        result.append(text)
    return result


class Translator:
    def __init__(self, directory, budget=DEFAULT_BUDGET, transport=request):
        self.store = KeyStore(directory)
        self.budget = int(budget)
        if not 1 <= self.budget <= DEFAULT_BUDGET:
            raise ValueError('Giới hạn cục bộ phải từ 1 đến 500.000 ký tự/dự án/tháng.')
        self.transport = transport

    def translate(self, texts, cancel, progress=None, *, source='vi', target='en'):
        """Two bounded workers; unique chunks cached as soon as they validate."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        split = [[part for line in text.splitlines(keepends=True) for part in chunks(line)] for text in texts]
        unique = list(dict.fromkeys(part for parts in split for part in parts))
        values, pending = {}, []
        for text in unique:
            if cancel.is_set():
                raise InterruptedError('Đã dừng dịch.')
            cache_id = _digest('google-nmt-v1|' + source + '|' + target + '|' + text)
            cached = self.store.cached(cache_id)
            if cached is not None:
                values[text] = cached
            elif not re.search(r'[^\W\d_]', text, re.UNICODE):
                values[text] = text
            else:
                payload, locks = protected_html(text)
                if len(payload) > MAX_CHARS:
                    raise TranslationProblem('api_request', 'Một công thức/vùng nội dung quá dài; chia nhỏ trước khi dịch.')
                pending.append((text, payload, locks, cache_id))
        groups, batch, size = [], [], 0
        for item in pending:
            if batch and (size + len(item[1]) > MAX_CHARS or len(batch) >= MAX_ITEMS):
                groups.append(batch)
                batch, size = [], 0
            batch.append(item)
            size += len(item[1])
        if batch:
            groups.append(batch)
        done, total = sum(len(t) for t in values), sum(len(t) for t in unique)
        if progress:
            progress(done, total)

        def run(group):
            count = sum(len(item[1]) for item in group)
            excluded = set()
            attempts = 0
            retry_key = None
            while True:
                if cancel.is_set():
                    raise InterruptedError('Đã dừng dịch.')
                row = self.store.reserve(count, self.budget, excluded, only_key=retry_key)
                try:
                    response = self.transport([item[1] for item in group], row['key'], source, target)
                except TranslationProblem as exc:
                    if exc.code not in {'api_network', 'api_result'}:
                        self.store.reject(row, count, exc.code)
                    if exc.code in {'api_key', 'api_quota'}:
                        excluded.add(row['id'])
                        retry_key = None
                        continue  # advance only on a definite credential/quota rejection
                    if exc.code in {'api_network', 'api_rate'} and attempts < 2:
                        retry_key = row['id']
                        attempts += 1
                        if cancel.wait(attempts):
                            raise InterruptedError('Đã dừng dịch.')
                        continue
                    raise
                if not isinstance(response, list) or len(response) != len(group):
                    raise TranslationProblem('api_result', 'Bản dịch chưa đủ nội dung yêu cầu.')
                translated = []
                for item, value in zip(group, response, strict=True):
                    result = unprotect(value, item[2])
                    whitespace = re.fullmatch(r'(\s*)(.*?)(\s*)', item[0], re.S)
                    result = whitespace[1] + result.strip() + whitespace[3]
                    from collections import Counter
                    from .translation_batches import NUMBERS
                    if Counter(NUMBERS.findall(result)) != Counter(NUMBERS.findall(item[0])):
                        raise TranslationProblem('api_result', 'Bản dịch làm thay đổi số liệu; chưa áp dụng kết quả này.')
                    translated.append((item, result))
                self.store.cache_many([(item[3], value) for item, value in translated])
                return [(item[0], value) for item, value in translated]

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix='google-translate') as executor:
            # Submit only two at a time, so a failure never queues the whole lesson.
            iterator = iter(groups)
            active = {executor.submit(run, group) for group in [next(iterator, None), next(iterator, None)] if group}
            while active:
                future = next(as_completed(active))
                active.remove(future)
                try:
                    for text, value in future.result():
                        values[text] = value
                        done += len(text)
                    if progress:
                        progress(done, total)
                    if cancel.is_set():
                        raise InterruptedError('Đã dừng dịch.')
                    group = next(iterator, None)
                    if group:
                        active.add(executor.submit(run, group))
                except BaseException:
                    for other in active:
                        other.cancel()
                    raise
        return [''.join(values[part] for part in parts) for parts in split]
