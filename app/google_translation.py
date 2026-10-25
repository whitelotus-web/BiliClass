"""Google Translation Basic, bounded requests and machine-local credentials.

Keys are never returned to QML, logged, backed up or stored in the library DB.
Usage is a conservative local budget, NOT Google's billing/free-credit balance.
Each key has its own local budget. The legacy project ledger is retained for
history; it cannot be split retrospectively into individual key usage.
"""

import ctypes
import errno
import hashlib
import html
import http.client
import json
import os
import re
import sqlite3
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from contextlib import closing
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ENDPOINT = 'https://translation.googleapis.com/language/translate/v2'
MAX_CHARS = 4500
MAX_ITEMS = 100
DEFAULT_BUDGET = 500_000
_LOCK = threading.RLock()
# A value and its unit form one protected expression. In particular, an
# exposed trailing s2 must not be translated as a word or lose its s.
_UNIT_BASE = r'(?-i:kHz|Hz|cm|mm|km|ms|rad|kg|mol|mL|eV|Pa|m|s|h|g|N|J|W|V|A|Ω|K|°C|L)'
_EXPONENT = r'(?:[²³23]|\^\s*(?:\{\s*[+−-]?\d+\s*\}|[+−-]?\d+)|[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+|[−-]\s*\d+|⟦BLC\d+⟧)'
_UNIT = _UNIT_BASE + r'(?:\s*' + _EXPONENT + ')?'
_NUMBER = r'[+−-]?\d+(?:[.,]\d+)*(?:\s*%)?'
_MEASUREMENT = _NUMBER + r'(?:\s*' + _UNIT + r'(?:/' + _UNIT + r')?(?!\w))?'
_UNIT_EXPRESSION = r'(?<!\w)(?:' + _UNIT + '/' + _UNIT + '|' + _UNIT_BASE + r'\s*' + _EXPONENT + r')(?!\w)'


class TranslationProblem(ValueError):
    def __init__(self, code, message, *, retry_after=None):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


def _retry_after(headers):
    """Read only the standard delay, never expose a provider's raw error body."""
    value = headers.get('Retry-After', '') if headers else ''
    if not isinstance(value, str) or len(value) > 100:
        return None
    try:
        if value.strip().isdigit():
            return min(int(value), 86400)
        date = parsedate_to_datetime(value)
        if date.tzinfo is not None:
            return min(86400, max(0, (date - datetime.now(timezone.utc)).total_seconds()))
    except (ValueError, TypeError, OverflowError):
        pass
    return None


def network_problem(message, error):
    problem = TranslationProblem('api_network', message)
    reason = getattr(error, 'reason', error)
    problem.offline = (getattr(reason, 'errno', None) in {errno.ENETDOWN, errno.ENETUNREACH}
                       or getattr(reason, 'winerror', None) in {10050, 10051})
    return problem


class _TranslationStop:
    """Join user cancellation with a failed sibling, including nested repairs."""

    def __init__(self, parent, failed):
        self.parent, self.failed = parent, failed

    def is_set(self):
        return self.parent.is_set() or self.failed.is_set()

    def wait(self, seconds):
        end = time.monotonic() + seconds
        while not self.is_set():
            remaining = end - time.monotonic()
            if remaining <= 0:
                return False
            self.failed.wait(min(.05, remaining))
        return True


def _digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def numeric_glyphs(text):
    """Circled/parenthesized/fractional numbers are numbers, not words to translate."""
    return ''.join(sorted({char for char in text if unicodedata.category(char) in {'No','Nl'}
        and char not in '⁰¹²³⁴⁵⁶⁷⁸⁹'}))


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
    def __init__(self, directory, *, namespace='translation_api'):
        self.root = Path(directory) / namespace
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'keys.dpapi'
        with _LOCK, closing(self.connect()) as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS usage(month TEXT, project TEXT, characters INTEGER NOT NULL,
                    PRIMARY KEY(month,project));
                CREATE TABLE IF NOT EXISTS blocked(month TEXT, key_id TEXT, code TEXT,
                    PRIMARY KEY(month,key_id));
                CREATE TABLE IF NOT EXISTS cache(id TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS key_names(key_id TEXT PRIMARY KEY,
                    number INTEGER UNIQUE NOT NULL, name TEXT NOT NULL DEFAULT '');
            ''')
            with db:
                db.execute('BEGIN IMMEDIATE')
                columns = {row[1] for row in db.execute('PRAGMA table_info(usage_per_key)')}
                if 'carryover' not in columns:
                    # The old ledger cannot identify which key spent a shared
                    # amount. Reserve it conservatively for existing keys only,
                    # so migration cannot grant another full budget this month.
                    rows = self.keys()
                    month = self.month()
                    if columns:
                        db.execute('ALTER TABLE usage_per_key ADD COLUMN carryover INTEGER NOT NULL DEFAULT 0')
                    else:
                        db.execute('CREATE TABLE usage_per_key(month TEXT,key_id TEXT,project TEXT,'
                                   'characters INTEGER NOT NULL,carryover INTEGER NOT NULL DEFAULT 0,'
                                   'PRIMARY KEY(month,key_id))')
                    used = dict(db.execute('SELECT project,characters FROM usage WHERE month=?', (month,)))
                    tracked = dict(db.execute('SELECT project,SUM(characters) FROM usage_per_key WHERE month=? GROUP BY project', (month,)))
                    for row in rows:
                        carry = max(0, used.get(row['project'], 0) - tracked.get(row['project'], 0))
                        if carry:
                            db.execute('INSERT INTO usage_per_key VALUES(?,?,?,?,?) ON CONFLICT(month,key_id) '
                                       'DO UPDATE SET carryover=MAX(carryover,excluded.carryover)',
                                       (month, row['id'], row['project'], 0, carry))

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
        display_names = {}
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
            if '|' in line:
                display_names[_digest(key)] = project
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
            if display_names:
                self.public()  # Allocate permanent numbers before optional names.
                with closing(self.connect()) as db, db:
                    db.executemany("UPDATE key_names SET name=? WHERE key_id=? AND name=''",
                                   [(name, key_id) for key_id, name in display_names.items()])

    def remove(self, key_id):
        with _LOCK:
            rows = [r for r in self.keys() if r['id'] != key_id]
            _atomic(self.path, _crypt(json.dumps(rows).encode('utf-8')))
        # Never delete accounting when deleting/re-adding a credential.

    @staticmethod
    def month():
        return datetime.now(timezone.utc).strftime('%Y-%m')

    def public(self):
        rows = self.keys()
        with closing(self.connect()) as db:
            with db:
                db.execute('BEGIN IMMEDIATE')
                for row in rows:
                    if not db.execute('SELECT 1 FROM key_names WHERE key_id=?', (row['id'],)).fetchone():
                        number = db.execute('SELECT COALESCE(MAX(number),0)+1 FROM key_names').fetchone()[0]
                        db.execute('INSERT INTO key_names(key_id,number) VALUES(?,?)', (row['id'], number))
            names = {row[0]: (row[1], row[2]) for row in db.execute('SELECT key_id,number,name FROM key_names')}
            used = dict(db.execute('SELECT project,characters FROM usage WHERE month=?', (self.month(),)))
            key_used = dict(db.execute('SELECT key_id,characters FROM usage_per_key WHERE month=?', (self.month(),)))
            carried = dict(db.execute('SELECT key_id,carryover FROM usage_per_key WHERE month=?', (self.month(),)))
            tracked = dict(db.execute('SELECT project,SUM(characters) FROM usage_per_key WHERE month=? GROUP BY project',
                                      (self.month(),)))
            blocked = dict(db.execute('SELECT key_id,code FROM blocked WHERE month=?', (self.month(),)))
        def display(row):
            number, name = names[row['id']]
            name = name or (row['project'] if row['project'] != 'mặc định' else '')
            return f'Key {number}' + (f' ({name})' if name else '')
        return [{'id': row['id'], 'project': row['project'], 'label': '•••• ' + row['key'][-4:],
                 'name': display(row), 'customName': names[row['id']][1],
                 'used': key_used.get(row['id'], 0),
                 'carryover': carried.get(row['id'], 0),
                 'legacyUsed': max(0, used.get(row['project'], 0) - tracked.get(row['project'], 0)),
                 'blocked': blocked.get(row['id'], '')}
                for row in rows]

    def rename(self, key_id, name):
        name = name.strip()
        if len(name) > 80 or any(ord(c) < 32 for c in name):
            raise ValueError('Tên key tối đa 80 ký tự, trên một dòng.')
        if not any(row['id'] == key_id for row in self.public()):
            raise ValueError('Key này không còn trong danh sách.')
        with closing(self.connect()) as db, db:
            db.execute('UPDATE key_names SET name=? WHERE key_id=?', (name, key_id))

    def reserve(self, count, budget, excluded=(), only_key=None):
        """Atomic across workers/processes. Debit BEFORE send, including ambiguity."""
        with _LOCK, closing(self.connect()) as db:
            month = self.month()
            rows = self.keys()
            if not rows:
                raise TranslationProblem('api_settings', 'Thêm Google Cloud Translation API key trong Cài đặt → Dịch thuật.')
            with db:
                db.execute('BEGIN IMMEDIATE')
                for row in rows:
                    if only_key is not None and row['id'] != only_key:
                        continue
                    if row['id'] in excluded or db.execute('SELECT 1 FROM blocked WHERE month=? AND key_id=?',
                                                         (month, row['id'])).fetchone():
                        continue
                    used = db.execute('SELECT characters+carryover FROM usage_per_key WHERE month=? AND key_id=?',
                                      (month, row['id'])).fetchone()
                    if (used[0] if used else 0) + count > budget:
                        continue
                    db.execute('INSERT INTO usage VALUES(?,?,?) ON CONFLICT(month,project) DO UPDATE SET characters=characters+excluded.characters',
                               (month, row['project'], count))
                    db.execute('INSERT INTO usage_per_key(month,key_id,project,characters) VALUES(?,?,?,?) ON CONFLICT(month,key_id) '
                               'DO UPDATE SET characters=characters+excluded.characters',
                               (month, row['id'], row['project'], count))
                    return {**row, 'month': month}
        raise TranslationProblem('api_budget', 'Các key đã hết giới hạn cục bộ hoặc chưa dùng được. Kiểm tra hạn mức/thanh toán trong Google Cloud; phần dịch xong đã lưu.')

    def reject(self, row, count, code):
        # A definitive rejected request is not translated; network/timeout
        # ambiguity is deliberately NOT refunded.
        with closing(self.connect()) as db, db:
            month = row.get('month', self.month())
            db.execute('UPDATE usage SET characters=MAX(0,characters-?) WHERE month=? AND project=?',
                       (count, month, row['project']))
            db.execute('UPDATE usage_per_key SET characters=MAX(0,characters-?) WHERE month=? AND key_id=?',
                       (count, month, row['id']))
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
        delay = _retry_after(exc.headers)
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
            except (ValueError, TypeError, AttributeError, OSError, http.client.HTTPException):
                pass
        elif status >= 500:
            code = 'api_network'
        else:
            code = 'api_request'
        exc.close()
        message = ('Google Dịch đang giới hạn tần suất. Chờ một lúc rồi tiếp tục; phần đã dịch được giữ lại.' if code == 'api_rate' else
                   'Google Dịch chưa nhận được yêu cầu hợp lệ. Kiểm tra key, bật Cloud Translation API, thanh toán và hạn mức của dự án.')
        raise TranslationProblem(code, message, retry_after=delay) from None
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
        raise network_problem('Kết nối Google Dịch gián đoạn. Các phần đã dịch vẫn được lưu để tiếp tục.', exc) from None
    except (ValueError, KeyError, TypeError):
        raise TranslationProblem('api_result', 'Google Dịch trả kết quả chưa hợp lệ; phần đã xong vẫn được lưu.') from None


def protected_html(text, terms=None, *, chemistry=False, opaque_values=False, native_values=None):
    # Protect arithmetic, LaTeX spans and native OOXML placeholder tokens.
    terms = terms or {}
    term_pattern = r'(?<!\w)(?:' + '|'.join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + r')(?!\w)' if terms else r'(?!)'
    pattern = (r'⟦BLC\d+⟧|\$[^$]+\$|' + term_pattern + '|' + _MEASUREMENT + '|'
               + _UNIT_EXPRESSION + r'|[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾]+')
    glyphs = numeric_glyphs(text)
    if glyphs:
        pattern += '|[' + re.escape(glyphs) + ']+'
    formula_pattern = ''
    formulas = set()
    if chemistry:
        from .chemical_notation import formula_spans

        # Escape the complete, case-sensitive span, including its native index
        # tokens. Protecting just "2" let Google remove "CO" from CO₂.
        formulas = {match.group()[1:-1] if match.group().startswith('(') and match.group().endswith(')')
                    else match.group() for match in formula_spans(text)}
        if formulas:
            formula_pattern = r'(?<![\w⟦])(?-i:' + '|'.join(re.escape(value) for value in sorted(formulas,key=lambda v:(-len(v),v))) + r')(?![\w⟧])|'
    pattern = formula_pattern + pattern
    locks = []
    parts, last = [], 0
    for match in re.finditer(pattern, text, re.I):
        parts.append(html.escape(text[last:match.start()]))
        token = f'BCLLOCK{len(locks)}END'
        from .translation_terms import normalized

        locks.append(match.group() if match.group() in formulas else terms.get(normalized(match.group()), match.group()))
        # Expose words/numbers to the model's sentence context. Opaque codes
        # make e.g. velocity look like a person's name and can move a question
        # number into the middle of the sentence. The HTML id still lets us
        # verify and restore every protected value exactly. Native math keeps
        # its opaque token because its XML representation is not prose.
        # Never expose chemical XML indices to the model: CO⟦BLC0⟧ prompted
        # invented atoms. A semantic replacement such as "chemical formula"
        # can swallow surrounding nouns; keep the opaque token instead.
        chemical = match.group() in formulas
        term = normalized(match.group()) in terms
        native_value = (native_values or {}).get(match.group())
        contextual = not chemical and ((native_value is not None and not opaque_values) or
            (term and not (opaque_values and re.search(r'\d', locks[-1]))) or
            (not opaque_values and not match.group().startswith(('⟦', '$'))))
        parts.append(('<span translate="no" class="notranslate" id="' + token + '">' +
                      html.escape(native_value if native_value is not None else locks[-1]) + '</span>') if contextual else
                     '<span translate="no" class="notranslate">' + token + '</span>')
        last = match.end()
    parts.append(html.escape(text[last:]))
    return ''.join(parts), locks


def _protected_text(value):
    from html.parser import HTMLParser

    class Text(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
            self.lock_depth = 0

        def handle_starttag(self, tag, attrs):
            if self.lock_depth:
                self.lock_depth += 1
                return
            token = dict(attrs).get('id', '')
            if tag == 'span' and re.fullmatch(r'BCLLOCK\d+END', token):
                self.parts.append(token)
                self.lock_depth = 1

        def handle_endtag(self, tag):
            if self.lock_depth:
                self.lock_depth -= 1

        def handle_data(self, data):
            if not self.lock_depth:
                self.parts.append(data)

    parser = Text()
    parser.feed(value)
    if parser.lock_depth:
        raise TranslationProblem('api_result', 'Vùng bảo vệ bản dịch chưa hợp lệ; chưa áp dụng kết quả này.')
    return ''.join(parser.parts)


def unprotect(value, locks):
    text = _protected_text(value)
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
    cache_namespace = 'google-nmt-context-v3'
    rotate_credentials = True
    max_items = MAX_ITEMS

    def __init__(self, directory, budget=DEFAULT_BUDGET, transport=request, *, store=None,
                 maximum_budget=DEFAULT_BUDGET):
        self.store = store if store is not None else KeyStore(directory)
        self.budget = int(budget)
        if not 1 <= self.budget <= maximum_budget:
            raise ValueError(f'Giới hạn cục bộ phải từ 1 đến {maximum_budget:,} ký tự/tháng.')
        self.transport = transport

    def _send(self, texts, credential, source, target):
        return self.transport(texts, credential['key'], source, target)

    def _send_repair(self, texts, credential, source, target):
        return self._send(texts, credential, source, target)

    def _request_cost(self, texts):
        return sum(map(len, texts))

    def _payload_size(self, text):
        return len(text)

    def _record_completed(self, rows):
        completed = getattr(self, 'completed_chunks', None)
        if completed is not None:
            completed.update(rows)

    def configure_terms(self, subject, rows, *, references=()):
        from .translation_terms import TermPolicy

        if hasattr(self, '_context_base_namespace'):
            self.cache_namespace = self._context_base_namespace
        self.lesson_context = self.lesson_context_deepl = ''
        self.reviewed_memory = {}
        self.reviewed_reused = set()
        self.reference_quality = False
        self._term_rows = list(rows)
        self.term_policy = TermPolicy(subject, self._term_rows, references)

    def configure_knowledge(self, plan):
        from .translation_knowledge import prompt_context, prose_context

        self.configure_terms(plan['subject'], getattr(self, '_term_rows', []), references=plan['terms'])
        self.lesson_context = prompt_context(plan)
        self.lesson_context_deepl = prose_context(plan)
        self.reviewed_memory = plan['memory']
        self.reference_quality = True
        self._context_base_namespace = getattr(self, '_context_base_namespace', self.cache_namespace)
        from .translation_quality import VERSION

        self.cache_namespace = self._context_base_namespace + '|lesson-reference-v1|' + VERSION + '|' + plan['fingerprint']

    def translate_native(self, units, images, cancel, progress=None):
        """Expose ordinary counts for grammar, retaining every immutable XML token."""
        from lxml import etree

        from .translation_batches import NUMBERS

        hints = []
        for unit in units:
            counts = {}
            for i, value in enumerate(unit['numbers']):
                variable_count = (getattr(getattr(self, 'term_policy', None), 'subject', '') == 'toan'
                    and re.fullmatch(r'[a-zA-Z]', unicodedata.normalize('NFKC', value))
                    and re.search(r'⟦BLC' + str(i) + r'⟧\s+(?:tam giác|điểm|cạnh|mặt|đường)\b', unit['text']))
                if not NUMBERS.fullmatch(value) and not variable_count:
                    continue
                xml = unit.get('xml_locks', {}).get(str(i))
                if xml:
                    try:
                        node = etree.fromstring(xml.encode('utf-8'))
                        if node.xpath('.//*[local-name()="alpha"][@val="0"]|.//*[local-name()="noFill"]'):
                            continue
                    except (ValueError, etree.XMLSyntaxError):
                        continue
                counts[f'⟦BLC{i}⟧'] = value
            hints.append(counts)
        return self.translate([u['text'] for u in units] + [row['text'] for row in images], cancel, progress,
                              native_values=hints + [{} for _ in images])

    def translate(self, texts, cancel, progress=None, *, source='vi', target='en', native_values=None,
                  fragment_repair=True):
        """Two bounded workers; unique chunks cached as soon as they validate."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        user_cancel = cancel
        failed, failures, failure_lock = threading.Event(), [], threading.Lock()
        cancel = _TranslationStop(cancel, failed)
        hints = native_values if native_values is not None else [{} for _ in texts]
        if len(hints) != len(texts):
            raise ValueError('Ngữ cảnh số liệu không khớp các đoạn dịch.')
        split = [[(part, tuple(sorted((key, value) for key, value in context.items() if key in part)))
                  for line in text.splitlines(keepends=True) for part in chunks(line)]
                 for text, context in zip(texts, hints, strict=True)]
        unique = list(dict.fromkeys(part for parts in split for part in parts))
        values, pending = {}, []
        from .translation_knowledge import valid_memory
        from .translation_terms import TermPolicy

        policy = getattr(self, 'term_policy', TermPolicy()) if source == 'vi' and target == 'en' else TermPolicy()
        for job in unique:
            text, context = job
            if cancel.is_set():
                raise InterruptedError('Đã dừng dịch.')
            exact = policy.exact(text)
            if exact is not None:
                whitespace = re.fullmatch(r'(\s*)(.*?)(\s*)', text, re.S)
                values[job] = whitespace[1] + policy.postprocess(text, exact) + whitespace[3]
                continue
            remembered = getattr(self, 'reviewed_memory', {}).get(' '.join(text.split())) if source == 'vi' and target == 'en' else None
            if remembered and valid_memory(text, remembered) and not any(term in text.casefold() for term in policy.teacher_terms):
                self.reviewed_reused.add(' '.join(text.split()))
                whitespace = re.fullmatch(r'(\s*)(.*?)(\s*)', text, re.S)
                values[job] = whitespace[1] + remembered + whitespace[3]
                continue
            chemistry = policy.subject == 'hoa hoc'
            if chemistry:
                from .chemical_notation import VERSION as notation_version
                from .chemical_notation import formula_spans, only_notation

                if only_notation(text):
                    values[job] = text
                    continue
            matches = policy.matches(text)
            namespace = self.cache_namespace + ('|' + policy.fingerprint(matches) if matches else '')
            if context:
                namespace += '|native-counts-v1|' + _digest(json.dumps(context, ensure_ascii=False))
            if chemistry and formula_spans(text):
                namespace += '|' + notation_version
            if numeric_glyphs(text):
                namespace += '|unicode-numeric-glyphs-v1'
            if re.search(_UNIT_EXPRESSION, text):
                namespace += '|unit-expressions-v2'
            cache_id = _digest(namespace + '|' + source + '|' + target + '|' + text)
            cached = self.store.cached(cache_id)
            if cached is not None:
                values[job] = policy.postprocess(text, cached)
            elif not any(unicodedata.category(char).startswith('L') for char in text):
                values[job] = text
            else:
                payload, locks = protected_html(text, matches, chemistry=chemistry, native_values=dict(context))
                if self._payload_size(payload) > MAX_CHARS:
                    raise TranslationProblem('api_request', 'Một công thức/vùng nội dung quá dài; chia nhỏ trước khi dịch.')
                pending.append((text, payload, locks, cache_id, job))
        groups, batch, size = [], [], 0
        for item in pending:
            if batch and (size + self._payload_size(item[1]) > MAX_CHARS or len(batch) >= self.max_items):
                groups.append(batch)
                batch, size = [], 0
            batch.append(item)
            size += self._payload_size(item[1])
        if batch:
            groups.append(batch)
        self._record_completed(values.items())
        done, total = sum(len(t[0]) for t in values), sum(len(t[0]) for t in unique)
        if progress:
            progress(done, total)

        def checked(item, result, *, prose=None):
            from collections import Counter

            from .translation_batches import NUMBERS
            from .translation_quality import untranslated_prose

            whitespace = re.fullmatch(r'(\s*)(.*?)(\s*)', item[0], re.S)
            result = whitespace[1] + result.strip() + whitespace[3]
            if Counter(NUMBERS.findall(result)) != Counter(NUMBERS.findall(item[0])):
                raise TranslationProblem('api_result', 'Bản dịch làm thay đổi số liệu; chưa áp dụng kết quả này.')
            if policy.subject == 'hoa hoc':
                from .chemical_notation import signature

                if signature(result) != signature(item[0]):
                    raise TranslationProblem('api_result', 'Bản dịch làm thay đổi công thức hóa học; chưa áp dụng kết quả này. Phần đã dịch đúng được giữ để tiếp tục.')
            if (source == 'vi' and target == 'en' and getattr(self, 'reference_quality', False)
                    and prose is not None and untranslated_prose(prose)):
                problem = TranslationProblem('api_result', 'Bản Anh còn đoạn tiếng Việt chưa được dịch đủ; phần đã đạt được giữ để tiếp tục.')
                problem.language_incomplete = True
                raise problem
            return policy.postprocess(item[0], result)

        def repair_fragments(invalid):
            """Last bounded attempt: send prose only, rebuild every lock locally."""
            repaired = []
            for item, error in invalid:
                payload, locks = protected_html(item[0], policy.matches(item[0]),
                    chemistry=policy.subject == 'hoa hoc', opaque_values=True)
                if not locks:
                    raise error
                pieces = re.split(r'(BCLLOCK\d+END)', _protected_text(payload))
                prose = [index for index in range(0, len(pieces), 2)
                         if any(unicodedata.category(char).startswith('L') for char in pieces[index])]
                try:
                    values = self.translate([pieces[index] for index in prose], cancel, source=source, target=target,
                                            fragment_repair=False)
                except TranslationProblem as exc:
                    exc.failed_text = item[0]  # Diagnostics refer to the original frame, not a common prose fragment.
                    raise
                for index, value in zip(prose, values, strict=True):
                    pieces[index] = value
                for index in range(1, len(pieces), 2):
                    pieces[index] = locks[int(pieces[index][7:-3])]
                try:
                    value = checked(item, ''.join(pieces))
                except TranslationProblem as exc:
                    exc.failed_text = item[0]
                    raise
                self.store.cache(item[3], value)
                self._record_completed([(item[4], value)])
                repaired.append((item[4], value))
            return repaired

        def run(group, *, repairing=False):
            count = self._request_cost([item[1] for item in group])
            excluded = set()
            attempts = 0
            retry_key = None
            last_rejection = None
            while True:
                if cancel.is_set():
                    raise InterruptedError('Đã dừng dịch.')
                try:
                    row = self.store.reserve(count, self.budget, excluded, only_key=retry_key)
                except TranslationProblem as exc:
                    if exc.code == 'api_budget' and last_rejection is not None:
                        raise last_rejection from None
                    raise
                try:
                    sender = self._send_repair if repairing else self._send
                    response = sender([item[1] for item in group], row, source, target)
                except TranslationProblem as exc:
                    # New LanguageApp gateways can return a successful prefix.
                    # Keep only validated chunks, then pause without replaying it.
                    partial = getattr(exc, 'partial_translations', [])
                    if partial:
                        accepted = []
                        for item, value in zip(group, partial):
                            try:
                                accepted.append((item[3], checked(item, unprotect(value, item[2]), prose=_protected_text(value))))
                            except TranslationProblem:
                                pass
                        self.store.cache_many(accepted)
                        self._record_completed([(item[4], value) for item in group for key, value in accepted if key == item[3]])
                        self.store.reject(row, 0, exc.code)  # Partial/ambiguous work remains charged.
                        raise
                    if exc.code not in {'api_network', 'api_result'}:
                        self.store.reject(row, count, exc.code)
                    if exc.code in {'api_key', 'api_quota'}:
                        if not self.rotate_credentials:
                            raise
                        last_rejection = exc
                        excluded.add(row['id'])
                        retry_key = None
                        continue  # advance only on a definite credential/quota rejection
                    if exc.code in {'api_network', 'api_rate'} and attempts < getattr(self, 'max_retries', 2):
                        delay = max(attempts + 1, exc.retry_after or 0)
                        if delay > 5:
                            raise  # Do not retry before the service's requested cooldown.
                        retry_key = row['id']
                        attempts += 1
                        if cancel.wait(delay):
                            raise InterruptedError('Đã dừng dịch.')
                        continue
                    raise
                if not isinstance(response, list) or len(response) != len(group):
                    raise TranslationProblem('api_result', 'Bản dịch chưa đủ nội dung yêu cầu.')
                translated, invalid = [], []
                for item, value in zip(group, response, strict=True):
                    try:
                        result = checked(item, unprotect(value, item[2]), prose=_protected_text(value))
                        translated.append((item, result))
                    except TranslationProblem as exc:
                        exc.failed_text = item[0]
                        invalid.append((item, exc))
                self.store.cache_many([(item[3], value) for item, value in translated])
                self._record_completed([(item[4], value) for item, value in translated])
                if invalid:
                    if repairing:
                        incomplete = next((error for _, error in invalid if getattr(error, 'language_incomplete', False)), None)
                        if incomplete:
                            raise incomplete  # No out-of-context fragments for missing prose.
                        if not fragment_repair:
                            raise invalid[0][1]
                        return [(item[4], value) for item, value in translated] + repair_fragments(invalid)
                    # One bounded repair of failed chunks only. Hide numeric
                    # values from the model as well as restoring them afterward;
                    # exposed numbers can be repeated outside their HTML locks.
                    # All calls still reserve budget; valid chunks stay cached.
                    repairs = []
                    for item, error in invalid:
                        payload, locks = protected_html(item[0], policy.matches(item[0]),
                            chemistry=policy.subject == 'hoa hoc', opaque_values=True)
                        if self._payload_size(payload) > MAX_CHARS:
                            raise error
                        repairs.append((item[0],payload,locks,item[3],item[4]))
                    repaired = []
                    batch, size = [], 0
                    for item in repairs:
                        if batch and (size + self._payload_size(item[1]) > MAX_CHARS or len(batch) >= self.max_items):
                            repaired.extend(run(batch,repairing=True))
                            batch, size = [], 0
                        batch.append(item)
                        size += self._payload_size(item[1])
                    if batch:
                        repaired.extend(run(batch,repairing=True))
                    return [(item[4], value) for item, value in translated] + repaired
                return [(item[4], value) for item, value in translated]

        def guarded_run(group):
            try:
                return run(group)
            except BaseException as exc:
                with failure_lock:
                    if not failures:
                        failures.append(exc)
                    failed.set()
                raise

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix='google-translate') as executor:
            # Submit only two at a time, so a failure never queues the whole lesson.
            iterator = iter(groups)
            active = {executor.submit(guarded_run, group) for group in [next(iterator, None), next(iterator, None)] if group}
            while active:
                future = next(as_completed(active))
                active.remove(future)
                try:
                    for job, value in future.result():
                        values[job] = value
                        done += len(job[0])
                    if progress:
                        progress(done, total)
                    if cancel.is_set():
                        raise InterruptedError('Đã dừng dịch.')
                    group = next(iterator, None)
                    if group:
                        active.add(executor.submit(guarded_run, group))
                except BaseException:
                    failed.set()
                    for other in active:
                        other.cancel()
                    if failures and not user_cancel.is_set():
                        raise failures[0]
                    raise
        return [''.join(values[part] for part in parts) for parts in split]
