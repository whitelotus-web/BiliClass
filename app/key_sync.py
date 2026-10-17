"""Explicit key transfer through an authenticated, private GitHub repository.

No application password, plaintext local export, public release asset or log.
Git Credential Manager supplies the existing GitHub login on each machine.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from contextlib import closing

from .google_translation import _LOCK, DEFAULT_BUDGET, _digest

REPOSITORY = 'whitelotus-web/BiliClass-Private-Config'
CONFIG_PATH = '/contents/google-translation-keys.json'
MAX_BYTES = 100_000


class GitHub:
    def __init__(self):
        executable = shutil.which('git')
        if not executable:
            raise ValueError('Cần Git for Windows và tài khoản GitHub có quyền vào kho cấu hình riêng tư. Không cần mật khẩu BiliClass.')
        try:
            result = subprocess.run(
                [executable, 'credential', 'fill'],
                input='protocol=https\nhost=github.com\nusername=whitelotus-web\n\n',
                capture_output=True, text=True, timeout=15, check=True,
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'},
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
            fields = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
            self._token = fields['password']
            if not self._token:
                raise ValueError()
        except (subprocess.SubprocessError, KeyError, ValueError, OSError):
            raise ValueError('Đăng nhập GitHub bằng Git Credential Manager trên máy này trước khi đồng bộ key.') from None

    def request(self, method, path, payload=None, *, missing=False):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        data = json.dumps(payload).encode('utf-8') if payload is not None else None
        outgoing = urllib.request.Request(
            'https://api.github.com/repos/' + REPOSITORY + path, data=data, method=method,
            headers={'Authorization': 'Bearer ' + self._token, 'User-Agent': 'BiliClass-Key-Sync',
                     'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.build_opener(NoRedirect).open(outgoing, timeout=25) as response:
                raw = response.read(MAX_BYTES * 2 + 1)
            if len(raw) > MAX_BYTES * 2:
                raise ValueError('Cấu hình GitHub vượt kích thước cho phép.')
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and missing:
                return None
            message = ('Cấu hình đã đổi trên máy khác. Nhận key từ GitHub rồi thử lại.' if exc.code in {409, 422}
                       else 'Chưa truy cập được kho cấu hình riêng tư. Kiểm tra đăng nhập và quyền GitHub.')
            raise ValueError(message) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ValueError('Chưa kết nối được GitHub. Key đang lưu tại máy vẫn giữ nguyên.') from None


def _require(condition):
    if not condition:
        raise ValueError()


def validate(data):
    try:
        _require(isinstance(data, dict) and data.get('format') == 'BiliClass Google keys v1')
        rows, usage, budget = data['keys'], data['usage'], data['budget']
        _require(isinstance(rows, list) and 1 <= len(rows) <= 50)
        _require(isinstance(budget, int) and not isinstance(budget, bool) and 1 <= budget <= DEFAULT_BUDGET)
        projects, identities = set(), set()
        for row in rows:
            _require(isinstance(row, dict) and set(row) == {'project', 'key'})
            _require(isinstance(row['project'], str) and 1 <= len(row['project']) <= 100)
            _require(not any(c in row['project'] for c in '|\r\n'))
            _require(row['project'] == row['project'].strip().casefold())
            _require(isinstance(row['key'], str) and re.fullmatch(r'[A-Za-z0-9_-]{30,200}', row['key']))
            _require(row['key'] not in identities)
            projects.add(row['project'])
            identities.add(row['key'])
        _require(isinstance(usage, list) and len(usage) <= 6000)
        for row in usage:
            _require(isinstance(row, list) and len(row) == 3)
            _require(isinstance(row[0], str) and re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', row[0]))
            _require(isinstance(row[1], str) and row[1] in projects)
            _require(isinstance(row[2], int) and not isinstance(row[2], bool) and 0 <= row[2] <= 2**63-1)
        key_usage = data.get('key_usage', [])
        _require(isinstance(key_usage, list) and len(key_usage) <= 6000)
        for row in key_usage:
            _require(isinstance(row, list) and len(row) == 4)
            _require(isinstance(row[0], str) and re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])', row[0]))
            _require(isinstance(row[1], str) and re.fullmatch('[0-9a-f]{64}', row[1]))
            _require(isinstance(row[2], str) and row[2] in projects)
            _require(isinstance(row[3], int) and not isinstance(row[3], bool) and 0 <= row[3] <= 2**63-1)
        # Historical entries may belong to removed keys; a current key must
        # retain its original project metadata when importing accounting.
        by_id = {_digest(row['key']): row['project'] for row in rows}
        _require(all(key_id not in by_id or by_id[key_id] == project for _, key_id, project, _ in key_usage))
        return data
    except (AssertionError, KeyError, TypeError, ValueError):
        raise ValueError('Tệp cấu hình key không đúng định dạng; chưa thay đổi key tại máy.') from None


def snapshot(store, budget):
    with _LOCK, closing(store.connect()) as db:
        keys = [{'project': r['project'], 'key': r['key']} for r in store.keys()]
        projects = {r['project'] for r in keys}
        usage = [list(r) for r in db.execute('SELECT month,project,characters FROM usage') if r[1] in projects]
        key_usage = [list(r) for r in db.execute('SELECT month,key_id,project,characters FROM usage_per_key') if r[2] in projects]
        return validate({'format': 'BiliClass Google keys v1', 'keys': keys, 'usage': usage,
                         'key_usage': key_usage, 'budget': budget})


def merge(first, second):
    validate(first)
    validate(second)
    rows = {r['key']: r for r in first['keys']}
    for row in second['keys']:
        if row['key'] in rows and rows[row['key']]['project'] != row['project']:
            raise ValueError('Cùng key đang thuộc hai tên nhóm khác nhau. Giữ cùng tên nhóm trên hai máy trước khi đồng bộ.')
        rows[row['key']] = row
    usage = {}
    for month, project, count in first['usage'] + second['usage']:
        usage[month, project] = max(usage.get((month, project), 0), count)
    key_usage = {}
    for month, key_id, project, count in first.get('key_usage', []) + second.get('key_usage', []):
        identity = month, key_id
        previous = key_usage.get(identity)
        if previous and previous[0] != project:
            raise ValueError('Lịch sử key đang thuộc hai tên nhóm khác nhau; chưa thay đổi dữ liệu.')
        key_usage[identity] = project, max(previous[1] if previous else 0, count)
    totals = {}
    for (month, _), (project, count) in key_usage.items():
        totals[month, project] = totals.get((month, project), 0) + count
    for identity, total in totals.items():
        usage[identity] = max(usage.get(identity, 0), total)
    return validate({'format': first['format'], 'keys': list(rows.values()),
                     'usage': [[*key, count] for key, count in usage.items()],
                     'key_usage': [[*key, *value] for key, value in key_usage.items()],
                     'budget': min(first['budget'], second['budget'])})


def remote(client):
    info = client.request('GET', '')
    if info.get('private') is not True or info.get('full_name', '').casefold() != REPOSITORY.casefold():
        raise ValueError('Chỉ đồng bộ key với đúng kho GitHub riêng tư. Đã chặn gửi/nhận key ở kho công khai.')
    entry = client.request('GET', CONFIG_PATH, missing=True)
    if entry is None:
        return None, None
    try:
        _require(entry['type'] == 'file' and entry['encoding'] == 'base64' and entry['size'] <= MAX_BYTES)
        content = base64.b64decode(''.join(entry['content'].split()), validate=True)
        _require(len(content) <= MAX_BYTES and re.fullmatch('[0-9a-f]{40,64}', entry['sha']))
        return validate(json.loads(content)), entry['sha']
    except (KeyError, AssertionError, ValueError, TypeError):
        raise ValueError('Không đọc được tệp key trong kho riêng tư; chưa thay đổi key tại máy.') from None


def upload(store, budget, client=None):
    local = snapshot(store, budget)
    client = client or GitHub()
    previous, sha = remote(client)
    combined = merge(local, previous) if previous else local
    content = json.dumps(combined, ensure_ascii=False).encode('utf-8')
    if len(content) > MAX_BYTES:
        raise ValueError('Cấu hình key vượt kích thước cho phép.')
    payload = {'message': 'Update private BiliClass translation configuration',
               'content': base64.b64encode(content).decode('ascii')}
    if sha:
        payload['sha'] = sha
    client.request('PUT', CONFIG_PATH, payload)
    return len(combined['keys'])


def download(store, budget, client=None):
    data, _ = remote(client or GitHub())
    if data is None:
        raise ValueError('Kho riêng tư chưa có key để nhận.')
    with _LOCK:
        if store.keys():
            data = merge(snapshot(store, budget), data)
        # Account conservatively before storing credentials. Repeated imports
        # cannot reset/inflate local counters; future machines remain separate.
        with closing(store.connect()) as db, db:
            db.executemany('INSERT INTO usage VALUES(?,?,?) ON CONFLICT(month,project) '
                           'DO UPDATE SET characters=MAX(characters,excluded.characters)', data['usage'])
            db.executemany('INSERT INTO usage_per_key VALUES(?,?,?,?) ON CONFLICT(month,key_id) '
                           'DO UPDATE SET characters=MAX(characters,excluded.characters)', data.get('key_usage', []))
        store.add('\n'.join(r['project'] + ' | ' + r['key'] for r in data['keys']))
    return {'count': len(data['keys']), 'budget': min(budget, data['budget'])}
