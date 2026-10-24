"""Optional Azure NMT transport; shared RC167 content guards, isolated secrets/cache.

One resource slot has one durable monthly ledger. Rotating Azure's two keys,
renaming or deleting/re-adding the configuration never grants another budget.
The local counter is conservative and is not Azure's account-wide quota.
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from contextlib import closing

from .google_translation import _LOCK, KeyStore, TranslationProblem, Translator, _atomic, _crypt, _digest

DEFAULT_BUDGET = 2_000_000
ENDPOINT = 'https://api.cognitive.microsofttranslator.com/translate'
RESOURCE_ID = _digest('azure-resource-slot-v1')


def validate_region(region):
    region = region.strip().lower() or 'global'
    if not re.fullmatch(r'[a-z][a-z0-9]{1,49}', region):
        raise TranslationProblem('api_settings', 'Region Azure phải là mã vùng, ví dụ southeastasia hoặc global; không nhập URL.')
    return region


class AzureKeyStore(KeyStore):
    def __init__(self, directory):
        super().__init__(directory, namespace='translation_azure')

    def keys(self):
        with _LOCK:
            if not self.path.exists():
                return []
            try:
                rows = json.loads(_crypt(self.path.read_bytes(), decrypt=True))
                if not isinstance(rows, list) or len(rows) > 1:
                    raise ValueError()
                for row in rows:
                    if (not isinstance(row, dict) or set(row) != {'id', 'project', 'key', 'region'}
                            or row['id'] != RESOURCE_ID or row['project'] != 'azure-resource'
                            or not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', row['key'])
                            or validate_region(row['region']) != row['region']):
                        raise ValueError()
                return rows
            except (ValueError, OSError, TypeError):
                raise TranslationProblem('api_settings', 'Chưa đọc được cấu hình Azure trên tài khoản Windows này. Nhập lại trong Cài đặt → Google Dịch.') from None

    def configure(self, key, region, name):
        key, name = key.strip(), name.strip()
        region = validate_region(region)
        if len(name) > 80 or any(ord(c) < 32 for c in name):
            raise TranslationProblem('api_settings', 'Tên tài nguyên Azure tối đa 80 ký tự, trên một dòng.')
        with _LOCK:
            if not key:
                old = self.keys()
                if not old:
                    raise TranslationProblem('api_settings', 'Nhập API key Azure trước khi lưu.')
                key = old[0]['key']
            if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', key):
                raise TranslationProblem('api_settings', 'API key Azure chưa đúng định dạng. Sao chép Key 1 hoặc Key 2 trong Keys and Endpoint.')
            rows = [dict(id=RESOURCE_ID, project='azure-resource', key=key, region=region)]
            _atomic(self.path, _crypt(json.dumps(rows).encode('utf-8')))
            self.public()
            with closing(self.connect()) as db, db:
                db.execute('UPDATE key_names SET name=? WHERE key_id=?', (name or 'Azure Translator', RESOURCE_ID))
                db.execute('DELETE FROM blocked WHERE key_id=?', (RESOURCE_ID,))

    def clear(self):
        with _LOCK:
            _atomic(self.path, _crypt(b'[]'))

    def reserve(self, count, budget, excluded=(), only_key=None):
        try:
            return super().reserve(count, budget, excluded, only_key)
        except TranslationProblem as exc:
            message = ('Thêm API key và Region Azure trong Cài đặt → Google Dịch.' if exc.code == 'api_settings' else
                       'Azure đã đạt giới hạn cục bộ hoặc key chưa dùng được. Kiểm tra tài nguyên và hạn mức Azure; phần đã dịch được giữ lại.')
            raise TranslationProblem(exc.code, message) from None

    def configuration(self):
        rows = self.keys()
        public = self.public()
        return dict(region=rows[0]['region'] if rows else 'global',
                    resource=public[0]['customName'] if public else '')


def request(texts, key, source, target, region):
    """Fixed commercial Azure endpoint; key/region in headers, no redirects."""
    region = validate_region(region)
    if source not in {'vi', 'en'} or target not in {'vi', 'en'}:
        raise TranslationProblem('api_settings', 'Chọn hướng dịch Việt–Anh hoặc Anh–Việt.')
    params = urllib.parse.urlencode({'api-version': '3.0', 'from': source, 'to': target,
                                    'textType': 'html', 'profanityAction': 'NoAction'})
    data = json.dumps([{'Text': '<div>' + text + '</div>'} for text in texts]).encode('utf-8')
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Ocp-Apim-Subscription-Key': key}
    if region != 'global':
        headers['Ocp-Apim-Subscription-Region'] = region
    outgoing = urllib.request.Request(ENDPOINT + '?' + params, data=data, method='POST', headers=headers)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    try:
        with urllib.request.build_opener(NoRedirect).open(outgoing, timeout=20) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError()
        rows = json.loads(raw)
        if not isinstance(rows, list) or len(rows) != len(texts):
            raise ValueError()
        values = []
        for row in rows:
            translations = row['translations']
            if len(translations) != 1 or translations[0]['to'] != target:
                raise ValueError()
            value = translations[0]['text']
            if not isinstance(value, str) or not value.strip():
                raise ValueError()
            values.append(value)
        return values
    except urllib.error.HTTPError as exc:
        status, detail = exc.code, ''
        try:
            detail = str(json.loads(exc.read(65536)).get('error', {}).get('code', ''))
        except (ValueError, TypeError, AttributeError):
            pass
        code = ('api_key' if status in {401, 403} else 'api_rate' if status == 429 else
                'api_network' if status >= 500 else 'api_request')
        if detail == '403001':
            code = 'api_quota'
        raise TranslationProblem(code, 'Azure chưa nhận được yêu cầu hợp lệ. Kiểm tra API key, Region và hạn mức trong Cài đặt → Google Dịch.') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise TranslationProblem('api_network', 'Kết nối Azure gián đoạn. Phần đã dịch được giữ lại để tiếp tục.') from None
    except (ValueError, KeyError, TypeError, IndexError):
        raise TranslationProblem('api_result', 'Azure trả kết quả chưa đủ hoặc chưa hợp lệ; phần đã xong được giữ lại.') from None


class AzureTranslator(Translator):
    cache_namespace = 'azure-nmt-context-v1'
    rotate_credentials = False

    def __init__(self, directory, budget=DEFAULT_BUDGET, transport=request):
        super().__init__(directory, budget, transport, store=AzureKeyStore(directory),
                         maximum_budget=DEFAULT_BUDGET)

    def _send(self, texts, credential, source, target):
        return self.transport(texts, credential['key'], source, target, credential['region'])

    def _request_cost(self, texts):
        return sum(len(text) + len('<div></div>') for text in texts)
