from contextlib import closing
from threading import Event

import pytest

from app.google_translation import KeyStore, Translator, TranslationProblem, chunks, protected_html, unprotect

KEY1, KEY2 = 'AIza' + 'a' * 35, 'AIza' + 'b' * 35


def test_keys_encrypted_masked_and_readding_does_not_reset_budget(tmp_path):
    store = KeyStore(tmp_path)
    store.add('Project A | ' + KEY1 + '\nProject A | ' + KEY2)
    assert KEY1.encode() not in store.path.read_bytes()
    assert KEY1 not in str(store.public())
    first = store.reserve(50, 50)
    store.remove(first['id'])
    store.add('Project A | ' + KEY1)
    assert all(row['used'] == 50 for row in store.public())
    with pytest.raises(TranslationProblem, match='giới hạn'):
        store.reserve(1, 50)


def test_ordered_distinct_projects_advance_at_local_budget(tmp_path):
    store = KeyStore(tmp_path)
    store.add('A | ' + KEY1 + '\nB | ' + KEY2)
    assert store.reserve(10, 10)['key'] == KEY1
    assert store.reserve(10, 10)['key'] == KEY2
    with pytest.raises(TranslationProblem):
        store.reserve(1, 10)


def test_unlabelled_keys_share_budget_and_duplicate_key_cannot_change_group(tmp_path):
    store = KeyStore(tmp_path)
    store.add(KEY1 + '\n' + KEY2)
    store.reserve(8, 8)
    with pytest.raises(TranslationProblem):
        store.reserve(1, 8)
    with pytest.raises(TranslationProblem):
        store.add('Other | ' + KEY1)


def test_concurrent_reservations_never_overspend(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    store = KeyStore(tmp_path)
    store.add(KEY1)
    def reserve():
        try:
            store.reserve(7, 20)
            return True
        except TranslationProblem:
            return False
    with ThreadPoolExecutor(8) as pool:
        assert sum(pool.map(lambda _: reserve(), range(8))) == 2
    assert store.public()[0]['used'] == 14


def test_translation_dedup_cache_protection_and_resumption(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    calls = []
    def transport(texts, key, source, target):
        calls.append(texts)
        return [value.replace('Vận tốc', 'Velocity').replace('Khối lượng', 'Mass') for value in texts]
    translator = Translator(tmp_path, transport=transport)
    results = translator.translate(['Vận tốc 12 m/s', 'Vận tốc 12 m/s', 'Khối lượng 2 kg'], Event())
    assert results == ['Velocity 12 m/s', 'Velocity 12 m/s', 'Mass 2 kg']
    assert len(calls) == 1 and len(calls[0]) == 2
    used = translator.store.public()[0]['used']
    assert translator.translate(['Vận tốc 12 m/s'], Event()) == [results[0]]
    assert len(calls) == 1 and translator.store.public()[0]['used'] == used


def test_bad_key_moves_to_next_without_exposing_provider_details(tmp_path):
    store = KeyStore(tmp_path)
    store.add('A | ' + KEY1 + '\nB | ' + KEY2)
    called = []
    def transport(texts, key, source, target):
        called.append(key)
        if key == KEY1:
            raise TranslationProblem('api_key', 'Invalid key')
        return ['Hello']
    assert Translator(tmp_path, transport=transport).translate(['Xin chào'], Event()) == ['Hello']
    assert called == [KEY1, KEY2]
    assert store.public()[0]['blocked'] == 'api_key'
    assert store.public()[0]['used'] == 0


def test_unknown_network_result_not_refunded_or_moved_to_another_key(tmp_path):
    store = KeyStore(tmp_path)
    store.add('A | ' + KEY1 + '\nB | ' + KEY2)
    keys = []
    def transport(texts, key, source, target):
        keys.append(key)
        raise TranslationProblem('api_network', 'Network failed')
    # Budget for only one request: cannot replay an ambiguous send for free.
    translator = Translator(tmp_path, budget=len('Xin chào'), transport=transport)
    with pytest.raises(TranslationProblem):
        translator.translate(['Xin chào'], Event())
    assert store.public()[0]['used'] > 0
    assert keys == [KEY1]


def test_missing_number_token_is_rejected_and_not_cached(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    translator = Translator(tmp_path, transport=lambda *args: ['Velocity'])
    with pytest.raises(TranslationProblem, match='số liệu'):
        translator.translate(['Vận tốc 12'], Event())
    with closing(translator.store.connect()) as db:
        assert db.execute('SELECT COUNT(*) FROM cache').fetchone()[0] == 0


def test_source_html_escaped_and_long_content_not_truncated():
    text = '<script>Tiếng Việt</script>\nGiá trị 12 + $x^2$ + ⟦BLC0⟧'
    encoded, locks = protected_html(text)
    assert '<script>' not in encoded
    assert unprotect(encoded, locks) == text
    long = ('Một câu tiếng Việt. ' * 200) + '⟦BLC123⟧'
    parts = chunks(long)
    assert ''.join(parts) == long and all(len(part) <= 1010 for part in parts)


def test_cancel_before_network_and_no_keys_error(tmp_path):
    cancel = Event()
    cancel.set()
    translator = Translator(tmp_path, transport=lambda *args: pytest.fail('sent after cancel'))
    with pytest.raises(InterruptedError):
        translator.translate(['Xin chào'], cancel)
    with pytest.raises(TranslationProblem, match='API key'):
        translator.translate(['Xin chào'], Event())


def test_line_breaks_and_chunk_whitespace_survive_google_trimming(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    translator = Translator(tmp_path, transport=lambda texts, *args: [t.strip().replace('Xin chào', 'Hello') for t in texts])
    assert translator.translate(['  Xin chào\nXin chào\n'], Event()) == ['  Hello\nHello\n']


def test_http_request_uses_header_no_redirect_and_checks_result(monkeypatch):
    from app import google_translation as module
    seen = []
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, limit):
            assert limit == 1_000_001
            return b'{"data":{"translations":[{"translatedText":"Hello"}]}}'
    class Opener:
        def open(self, req, timeout):
            seen.append(req)
            assert timeout == 20 and req.full_url == module.ENDPOINT
            assert req.get_header('X-goog-api-key') == KEY1
            assert KEY1 not in req.full_url
            return Response()
    monkeypatch.setattr(module.urllib.request, 'build_opener', lambda handler: Opener())
    assert module.request(['Xin chào'], KEY1, 'vi', 'en') == ['Hello']
    assert len(seen) == 1


def test_http_error_does_not_echo_key_or_source(monkeypatch):
    import io
    import urllib.error
    from app import google_translation as module
    class Opener:
        def open(self, req, timeout):
            raise urllib.error.HTTPError(module.ENDPOINT, 400, 'bad ' + KEY1, {},
                io.BytesIO(b'{"error":{"errors":[{"reason":"keyInvalid"}]}}'))
    monkeypatch.setattr(module.urllib.request, 'build_opener', lambda *args: Opener())
    with pytest.raises(TranslationProblem) as caught:
        module.request(['Private source'], KEY1, 'vi', 'en')
    assert caught.value.code == 'api_key'
    assert KEY1 not in str(caught.value) and 'Private source' not in str(caught.value)
