import errno
import json
from contextlib import closing
from threading import Event

import pytest

from app import alternative_translation as api
from app.google_translation import KeyStore, TranslationProblem, Translator, network_problem
from app.library import Library
from app.translation_failover import health, record, service_states
from app.translation_provider import build_translator, snapshot

SECRET = 'fixture_translation_failover_123456'


def configured(directory):
    with closing(Library(directory)):
        pass
    KeyStore(directory).add('AIza' + 'a' * 35)
    api.AlternativeStore(directory, 'languageapp').configure(SECRET, 'https://script.google.com/macros/s/' + 'A' * 40 + '/exec')
    return {**snapshot(directory, include_fallback=True), 'translation_work_folder': str(directory)}


@pytest.mark.parametrize('code', ['api_key', 'api_quota', 'api_billing', 'api_model', 'api_deployment', 'api_rate', 'api_network'])
def test_switches_only_to_configured_provider_and_does_not_change_selection(tmp_path, monkeypatch, code):
    config = configured(tmp_path)
    calls = []

    def google(rows, *_):
        calls.append('google')
        raise TranslationProblem(code, 'Unavailable')

    def alternative(rows, *_):
        calls.append('languageapp')
        return [row.replace('Xin chào', 'Hello') for row in rows]

    monkeypatch.setitem(api.TRANSPORTS, 'languageapp', alternative)
    router = build_translator(tmp_path, config, 500_000, lambda directory, budget: Translator(directory, budget, google))
    assert router.translate(['Xin chào'], Event()) == ['Hello']
    assert calls == ['google', 'languageapp']
    assert router.notices and router.used_services == ['languageapp']
    assert snapshot(tmp_path)['translation_provider'] == 'google'
    assert [row['translation_provider'] for row in config['translation_fallback']] == ['google', 'languageapp']
    states = {row['provider']: row for row in service_states(tmp_path)}
    assert states['google']['warning'] and not states['gemini']['warning']
    assert states['languageapp']['status'] == 'Đã dịch/kết nối được'


def test_validated_primary_chunks_are_not_retranslated_and_survive_restart(tmp_path, monkeypatch):
    config = configured(tmp_path)
    calls = []

    def google(rows, *_):
        calls.extend(('google', text) for text in rows)
        return [rows[0].replace('Xin chào', 'Hello'), rows[1] + ' 999']

    # A service-level error after a valid chunk is returned through the gateway protocol.
    def partial(rows, *_):
        calls.extend(('primary', text) for text in rows)
        exc = TranslationProblem('api_network', 'Interrupted batch')
        exc.partial_translations = [rows[0].replace('Xin chào', 'Hello')]
        raise exc

    def alternative(rows, *_):
        calls.extend(('languageapp', text) for text in rows)
        assert all('Xin chào' not in row for row in rows)
        return [row.replace('Tạm biệt', 'Goodbye') for row in rows]

    monkeypatch.setitem(api.TRANSPORTS, 'languageapp', alternative)
    router = build_translator(tmp_path, config, 500_000, lambda directory, budget: Translator(directory, budget, partial))
    assert router.translate(['Xin chào', 'Tạm biệt'], Event()) == ['Hello', 'Goodbye']
    assert [provider for provider, _ in calls] == ['primary', 'primary', 'languageapp']
    router = build_translator(tmp_path, config, 500_000, lambda *_: pytest.fail('Restart repeated completed work'))
    assert router.translate(['Xin chào', 'Tạm biệt'], Event()) == ['Hello', 'Goodbye']


@pytest.mark.parametrize('code', ['api_result', 'api_request', 'api_layout'])
def test_content_failure_does_not_bypass_validation_by_switching(tmp_path, monkeypatch, code):
    config = configured(tmp_path)
    monkeypatch.setitem(api.TRANSPORTS, 'languageapp', lambda *_: pytest.fail('Switched after content failure'))

    def reject(*_):
        raise TranslationProblem(code, 'Content needs review')

    router = build_translator(tmp_path, config, 500_000, lambda directory, budget: Translator(directory, budget, reject))
    with pytest.raises(TranslationProblem) as caught:
        router.translate(['Xin chào'], Event())
    assert caught.value.code == code
    assert not health(tmp_path)


def test_cancel_and_offline_do_not_walk_through_all_providers(tmp_path, monkeypatch):
    config = configured(tmp_path)
    monkeypatch.setitem(api.TRANSPORTS, 'languageapp', lambda *_: pytest.fail('Sent after Stop/offline'))

    def offline(*_):
        raise network_problem('Network unavailable', OSError(errno.ENETUNREACH, 'unreachable'))

    router = build_translator(tmp_path, config, 500_000, lambda directory, budget: Translator(directory, budget, offline))
    cancel = Event()
    cancel.set()
    with pytest.raises(InterruptedError):
        router.translate(['Xin chào'], cancel)
    with pytest.raises(TranslationProblem) as caught:
        router.translate(['Xin chào'], Event())
    assert caught.value.offline


def test_health_unknown_is_not_success_and_changed_key_clears_old_warning(tmp_path):
    configured(tmp_path)
    assert service_states(tmp_path)[0]['status'] == 'Chưa kiểm tra kết nối'
    record(tmp_path, 'languageapp', TranslationProblem('api_key', 'Private failure'))
    assert service_states(tmp_path)[1]['warning']
    store = api.AlternativeStore(tmp_path, 'languageapp')
    store.configure(SECRET + '_changed', store.configuration())
    assert not service_states(tmp_path)[1]['warning']
    assert SECRET not in (tmp_path / 'translation-service-health.json').read_text()


def test_malformed_advisory_state_does_not_break_translation_settings(tmp_path):
    configured(tmp_path)
    (tmp_path / 'translation-service-health.json').write_text(json.dumps({'google': {'code': {'not': 'a string'}}}))
    assert health(tmp_path) == {}
