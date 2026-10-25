"""Failure cases across real adapters; no network, personal data or credentials."""

import http.client
import io
import json
import shutil
import subprocess
import urllib.error
from contextlib import closing
from pathlib import Path
from threading import Barrier, Event

import pytest

from app import alternative_translation as api
from app import google_translation as google
from app.google_settings_tasks import read_state
from app.library import Library
from app.translation_provider import SELECTABLE

SECRET = 'fixture_secret_for_translation_123456'
URL = 'https://script.google.com/macros/s/' + 'A' * 40 + '/exec'
OPTIONS = {'languageapp': URL, 'gemini': api.DEFAULT_MODEL, 'deepl': 'developer'}


class Response:
    def __init__(self, payload):
        self.raw = json.dumps(payload).encode()

    def __enter__(self): return self
    def __exit__(self, *_): pass
    def read(self, limit): return self.raw[:limit]


def respond(monkeypatch, payload):
    monkeypatch.setattr(api.urllib.request, 'build_opener',
                        lambda *_: type('Opener', (), {'open': lambda *_a, **_k: Response(payload)})())


def translator_for(directory, provider, transport):
    if provider == 'google':
        google.KeyStore(directory).add('AIza' + 'a' * 35)
        return google.Translator(directory, transport=transport)
    api.AlternativeStore(directory, provider).configure(SECRET, OPTIONS[provider])
    return api.AlternativeTranslator(directory, provider, transport=transport)


@pytest.mark.parametrize('payload', [
    {'candidates': ['private malformed result']},
    {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [None]}}]},
    {'candidates': [{'finishReason': 'STOP', 'content': {'parts': ['private text']}}]},
    {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': '{"translations":[null]}'}]}}]},
])
def test_gemini_malformed_nested_json_has_safe_typed_error(monkeypatch, payload):
    respond(monkeypatch, payload)
    with pytest.raises(google.TranslationProblem) as caught:
        api.gemini_request(['source'], {'key': SECRET, 'option': api.DEFAULT_MODEL}, 'vi', 'en')
    assert caught.value.code == 'api_result'
    assert 'private' not in str(caught.value)


@pytest.mark.parametrize('error', [{'private': SECRET}, ['quota'], 123])
def test_languageapp_malformed_error_never_escapes_as_python_exception(monkeypatch, error):
    respond(monkeypatch, {'error': error})
    with pytest.raises(google.TranslationProblem) as caught:
        api.languageapp_request(['source'], {'key': SECRET, 'option': URL}, 'vi', 'en')
    assert caught.value.code == 'api_result' and SECRET not in str(caught.value)


@pytest.mark.parametrize('provider', SELECTABLE)
def test_failed_sibling_stops_retries_and_new_batches_but_retains_original_error(tmp_path, provider):
    entered = Barrier(2, timeout=5)
    failure_started = Event()
    calls = []

    def transport(rows, *_):
        calls.append(rows[0])
        if len(calls) <= 2:
            entered.wait()
        if rows[0].startswith('Mẩu alpha'):
            failure_started.set()
            raise google.TranslationProblem('api_request', 'Original terminal failure')
        assert failure_started.wait(5)
        raise google.TranslationProblem('api_network', 'Sibling transient failure')

    translator = translator_for(tmp_path, provider, transport)
    translator.max_items = 1
    with pytest.raises(google.TranslationProblem, match='Original terminal failure') as caught:
        translator.translate(['Mẩu alpha cần dịch.', 'Mẩu beta cần dịch.', 'Mẩu gamma cần dịch.'], Event())
    assert caught.value.code == 'api_request'
    assert len(calls) == 2, 'A failed lesson must not keep retrying a sibling or send the third group'


@pytest.mark.parametrize('provider', SELECTABLE)
def test_inflight_valid_sibling_is_cached_before_pause_and_reused(tmp_path, provider):
    entered = Barrier(2, timeout=5)
    calls = []

    def transport(rows, *_):
        calls.extend(rows)
        entered.wait()
        if rows[0].startswith('Mẩu alpha'):
            raise google.TranslationProblem('api_request', 'Pause')
        return ['A valid English sentence.']

    translator = translator_for(tmp_path, provider, transport)
    translator.max_items = 1
    with pytest.raises(google.TranslationProblem):
        translator.translate(['Mẩu alpha cần dịch.', 'Mẩu beta cần dịch.'], Event())
    translator.transport = lambda *_: pytest.fail('Valid in-flight work was not cached')
    assert translator.translate(['Mẩu beta cần dịch.'], Event()) == ['A valid English sentence.']
    assert len(calls) == 2


@pytest.mark.parametrize('provider,new_option', [
    ('gemini', 'gemini-3.1-flash-lite'), ('languageapp', URL.replace('AAAA', 'BBBB')),
])
def test_model_or_endpoint_change_after_translator_creation_cannot_mix_profiles(tmp_path, provider, new_option):
    translator = translator_for(tmp_path, provider, lambda *_: pytest.fail('Sent using a different profile'))
    translator.store.configure('', new_option)
    with pytest.raises(google.TranslationProblem) as caught:
        translator.translate(['Một câu cần được dịch.'], Event())
    assert caught.value.code == 'api_settings'
    assert translator.store.public()[0]['used'] == 0


@pytest.mark.parametrize('provider', SELECTABLE)
def test_long_server_cooldown_does_not_trigger_early_replays(tmp_path, monkeypatch, provider):
    calls = []
    streams = []

    class Opener:
        def open(self, request, **_):
            calls.append(request)
            stream = io.BytesIO(SECRET.encode())
            streams.append(stream)
            raise urllib.error.HTTPError(request.full_url, 429, SECRET, {'Retry-After': '60'}, stream)

    monkeypatch.setattr(google.urllib.request, 'build_opener', lambda *_: Opener())
    # Use the production adapter, not the fixture transport.
    translator = translator_for(tmp_path, provider, google.request if provider == 'google' else api.TRANSPORTS[provider])
    with pytest.raises(google.TranslationProblem) as caught:
        translator.translate(['Một câu cần được dịch.'], Event())
    assert caught.value.code == 'api_rate' and caught.value.retry_after == 60
    assert len(calls) == 1 and all(stream.closed for stream in streams)
    assert translator.store.public()[0]['used'] == 0
    assert SECRET not in str(caught.value)


@pytest.mark.parametrize('header,expected', [('0', 0), ('2', 2), ('bad', None), ('-3', None),
                                         ('9999999999', 86400), ('a' * 101, None)])
def test_retry_after_parser_is_bounded(header, expected):
    assert google._retry_after({'Retry-After': header}) == expected


def test_retry_after_accepts_http_date():
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime

    header = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=60), usegmt=True)
    assert 58 <= google._retry_after({'Retry-After': header}) <= 60


@pytest.mark.parametrize('provider', SELECTABLE)
def test_truncated_http_stream_is_classified_as_network_problem(monkeypatch, provider):
    class Opener:
        def open(self, *_a, **_k):
            raise http.client.IncompleteRead(b'private fragment', 100)

    monkeypatch.setattr(google.urllib.request, 'build_opener', lambda *_: Opener())
    with pytest.raises(google.TranslationProblem) as caught:
        if provider == 'google':
            google.request(['source'], SECRET, 'vi', 'en')
        else:
            api.TRANSPORTS[provider](['source'], {'key': SECRET, 'option': OPTIONS[provider]}, 'vi', 'en')
    assert caught.value.code == 'api_network'
    assert 'private' not in str(caught.value)


def test_google_truncated_error_body_keeps_status_error_and_closes_stream(monkeypatch):
    class BrokenBody(io.BytesIO):
        def read(self, *_):
            raise http.client.IncompleteRead(b'private source', 20)

    stream = BrokenBody()

    class Opener:
        def open(self, *_a, **_k):
            raise urllib.error.HTTPError(google.ENDPOINT, 403, SECRET, {}, stream)

    monkeypatch.setattr(google.urllib.request, 'build_opener', lambda *_: Opener())
    with pytest.raises(google.TranslationProblem) as caught:
        google.request(['source'], SECRET, 'vi', 'en')
    assert caught.value.code == 'api_key' and stream.closed
    assert 'private' not in str(caught.value) and SECRET not in str(caught.value)


@pytest.mark.parametrize('error', ['rate', 'quota', 'service'])
def test_languageapp_partial_prefix_is_kept_without_replay_or_refund(tmp_path, monkeypatch, error):
    calls = []

    def first(texts, credential, source, target):
        calls.append(list(texts))
        respond(monkeypatch, {'translations': ['A valid English sentence.'], 'error': error})
        return api.languageapp_request(texts, credential, source, target)

    translator = translator_for(tmp_path, 'languageapp', first)
    source = ['Mẩu alpha cần dịch.', 'Mẩu beta cần dịch.']
    with pytest.raises(google.TranslationProblem) as caught:
        translator.translate(source, Event())
    assert caught.value.code == {'rate': 'api_rate', 'quota': 'api_quota', 'service': 'api_network'}[error]
    assert len(calls) == 1 and translator.store.public()[0]['used'] == 2
    translator.store.recheck()
    translator.transport = lambda rows, *_: calls.append(rows) or ['Another English sentence.']
    assert translator.translate(source, Event()) == ['A valid English sentence.', 'Another English sentence.']
    assert len(calls[-1]) == 1 and calls[-1][0].startswith('Mẩu beta')
    assert translator.store.public()[0]['used'] == 3


def test_languageapp_partial_prefix_must_pass_same_number_guards(tmp_path, monkeypatch):
    respond(monkeypatch, {'translations': ['Incorrect value 999'], 'error': 'service'})
    translator = translator_for(tmp_path, 'languageapp', api.languageapp_request)
    with pytest.raises(google.TranslationProblem):
        translator.translate(['Giá trị 12', 'Mẩu beta cần dịch.'], Event())
    with translator.store.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM cache').fetchone()[0] == 0


@pytest.mark.parametrize('partial', [['one', 'two'], [None], 'not an array'])
def test_languageapp_refuses_malformed_partial_protocol(monkeypatch, partial):
    respond(monkeypatch, {'translations': partial, 'error': 'service'})
    with pytest.raises(google.TranslationProblem) as caught:
        api.languageapp_request(['one', 'two'], {'key': SECRET, 'option': URL}, 'vi', 'en')
    assert caught.value.code == 'api_result'


def test_gateway_partial_failure_and_invalid_request_are_structured():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node required to execute Apps Script fixture')
    script = (Path(api.__file__).parent / 'resources/languageapp.gs').read_text(encoding='utf-8')
    harness = r'''
const assert = require('node:assert/strict');
const values = {BILICLASS_ACCESS_CODE: 'fixture_secret_for_translation_123456'};
const PropertiesService = {getScriptProperties: () => ({getProperty: k => values[k], setProperty: (k,v) => {values[k] = v;}})};
const LockService = {getScriptLock: () => ({tryLock: () => true, releaseLock: () => {}})};
const ContentService = {MimeType: {JSON: 'json'}, createTextOutput: text => ({setMimeType: () => JSON.parse(text)})};
let calls = 0;
const LanguageApp = {translate: text => { calls++; if(calls === 2) throw new Error('rate limit private source'); return 'English ' + text; }};
function post(body) {return doPost({postData: {contents: JSON.stringify(body)}});}
for(const body of [null, [], 12, 'bad']) assert.deepEqual(post(body), {error: 'request'});
assert.equal(calls, 0);
assert.deepEqual(post({accessCode: values.BILICLASS_ACCESS_CODE, source: 'vi', target: 'en', texts: ['alpha', 'beta', 'gamma']}),
                 {error: 'rate', translations: ['English alpha']});
assert.equal(calls, 2);
assert.equal(JSON.parse(values.BILICLASS_USAGE).reduce((n,r) => n+r[1], 0), 3);
'''
    result = subprocess.run([node], input=script + '\n' + harness, text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('code', ['api_key', 'api_quota'])
def test_google_reports_actual_rejection_when_no_next_key_can_be_used(tmp_path, code):
    calls = []

    def transport(*_):
        calls.append(True)
        raise google.TranslationProblem(code, 'Actual credential or quota problem')

    translator = translator_for(tmp_path, 'google', transport)
    with pytest.raises(google.TranslationProblem) as caught:
        translator.translate(['Một câu cần dịch.'], Event())
    assert caught.value.code == code and len(calls) == 1


@pytest.mark.parametrize('provider', SELECTABLE[1:])
def test_bad_inactive_google_budget_does_not_disable_selected_service(tmp_path, provider):
    with closing(Library(tmp_path)) as library:
        library.set_setting('translation_provider', provider)
        library.set_setting('google_character_budget', 'damaged preference')
    api.AlternativeStore(tmp_path, provider).configure(SECRET, OPTIONS[provider])
    state = read_state(tmp_path)
    assert state['provider'] == provider and state['activeConfigured']
    assert not state['message'] and state['budget'] == google.DEFAULT_BUDGET


def test_languageapp_groups_emoji_using_gateway_utf16_limit(tmp_path):
    calls = []

    def transport(rows, *_):
        calls.append(rows)
        assert sum(len(row.encode('utf-16-le')) // 2 for row in rows) <= 4500
        return [row.replace('Nội dung', 'Content') for row in rows]

    translator = translator_for(tmp_path, 'languageapp', transport)
    source = ['Nội dung ' + char * 950 for char in '😀😃😄😁']
    assert translator.translate(source, Event()) == [text.replace('Nội dung', 'Content') for text in source]
    assert [len(rows) for rows in calls] == [2, 2]
