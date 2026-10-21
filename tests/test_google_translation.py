from contextlib import closing
from threading import Event

import pytest

from app.google_translation import KeyStore, TranslationProblem, Translator, chunks, protected_html, unprotect

KEY1, KEY2 = 'AIza' + 'a' * 35, 'AIza' + 'b' * 35


def test_key_auto_names_stay_stable_and_custom_names_do_not_change_usage(tmp_path):
    store = KeyStore(tmp_path)
    store.add(KEY1 + '\nTên dự án | ' + KEY2)
    rows = store.public()
    assert [row['name'] for row in rows] == ['Key 1','Key 2 (Tên dự án)']
    store.reserve(6, 100)
    store.rename(rows[0]['id'], 'Gmail cá nhân')
    assert store.public()[0]['name'] == 'Key 1 (Gmail cá nhân)'
    assert store.public()[0]['used'] == 6 and store.public()[0]['project'] == 'mặc định'
    store.remove(rows[0]['id'])
    assert store.public()[0]['name'] == 'Key 2 (Tên dự án)'
    store.add('AIza'+'c'*35)
    assert store.public()[1]['name'] == 'Key 3'
    store.add(KEY1)
    assert store.public()[2]['name'] == 'Key 1 (Gmail cá nhân)' and store.public()[2]['used'] == 6


def test_keys_encrypted_masked_and_readding_does_not_reset_budget(tmp_path):
    store = KeyStore(tmp_path)
    store.add('Project A | ' + KEY1 + '\nProject A | ' + KEY2)
    assert KEY1.encode() not in store.path.read_bytes()
    assert KEY1 not in str(store.public())
    first = store.reserve(50, 50)
    store.remove(first['id'])
    store.add('Project A | ' + KEY1)
    assert [row['used'] for row in store.public()] == [0, 50]
    assert store.reserve(50, 50)['key'] == KEY2
    with pytest.raises(TranslationProblem, match='giới hạn'):
        store.reserve(1, 50)


def test_ordered_distinct_projects_advance_at_local_budget(tmp_path):
    store = KeyStore(tmp_path)
    store.add('A | ' + KEY1 + '\nB | ' + KEY2)
    assert store.reserve(10, 10)['key'] == KEY1
    assert store.reserve(10, 10)['key'] == KEY2
    with pytest.raises(TranslationProblem):
        store.reserve(1, 10)


def test_unlabelled_keys_have_independent_budgets_and_keep_stable_project_metadata(tmp_path):
    store = KeyStore(tmp_path)
    store.add(KEY1 + '\n' + KEY2)
    store.reserve(8, 8)
    assert store.reserve(8, 8)['key'] == KEY2
    with pytest.raises(TranslationProblem):
        store.reserve(1, 8)
    with pytest.raises(TranslationProblem):
        store.add('Other | ' + KEY1)


@pytest.mark.parametrize('four_column_ledger', [False, True])
def test_legacy_group_history_is_retained_without_inventing_a_per_key_split(tmp_path, four_column_ledger):
    store = KeyStore(tmp_path)
    store.add(KEY1 + '\n' + KEY2)
    month = store.month()
    with closing(store.connect()) as db, db:
        db.execute('INSERT INTO usage VALUES(?,?,?)', (month, 'mặc định', 104853))
        db.execute('DROP TABLE usage_per_key')  # Simulate the actual pre-RC69 database.
        if four_column_ledger:
            db.execute('CREATE TABLE usage_per_key(month TEXT,key_id TEXT,project TEXT,'
                       'characters INTEGER NOT NULL,PRIMARY KEY(month,key_id))')
    store = KeyStore(tmp_path)
    assert [row['used'] for row in store.public()] == [0, 0]
    assert all(row['legacyUsed'] == 104853 for row in store.public())
    assert all(row['carryover'] == 104853 for row in store.public())
    second = store.public()[1]['id']
    store.reserve(20, 500000, only_key=second)
    store.rename(second, 'Mail thứ hai')
    store.remove(second)
    store.add(KEY2)
    rows = store.public()
    assert [row['used'] for row in rows] == [0, 20]
    assert all(row['legacyUsed'] == 104853 for row in rows)
    assert rows[1]['name'] == 'Key 2 (Mail thứ hai)'
    with closing(store.connect()) as db:
        assert db.execute('SELECT characters FROM usage WHERE month=?', (month,)).fetchone()[0] == 104873
    with pytest.raises(TranslationProblem):
        store.reserve(500000, 500000, only_key=second)
    fresh = 'AIza' + 'c' * 35
    store.add(fresh)
    assert store.public()[-1]['carryover'] == 0, 'A genuinely new key must get its full budget'


def test_rotation_skips_a_key_before_next_batch_would_cross_500000_and_month_rolls_over(tmp_path, monkeypatch):
    monkeypatch.setattr(KeyStore, 'month', staticmethod(lambda: '2026-10'))
    store = KeyStore(tmp_path)
    store.add(KEY1 + '\n' + KEY2)
    assert store.reserve(499999, 500000)['key'] == KEY1
    assert store.reserve(2, 500000)['key'] == KEY2
    assert store.reserve(1, 500000)['key'] == KEY1
    assert store.reserve(499998, 500000)['key'] == KEY2
    with pytest.raises(TranslationProblem):
        store.reserve(1, 500000)
    assert [row['used'] for row in store.public()] == [500000, 500000]
    monkeypatch.setattr(KeyStore, 'month', staticmethod(lambda: '2026-11'))
    assert [row['used'] for row in store.public()] == [0, 0]
    assert store.reserve(5, 500000)['key'] == KEY1
    with closing(store.connect()) as db:
        assert db.execute("SELECT SUM(characters) FROM usage_per_key WHERE month='2026-10'").fetchone()[0] == 1000000


@pytest.mark.parametrize('key_count', [1, 2])
def test_concurrent_reservations_never_overspend(tmp_path, key_count):
    from concurrent.futures import ThreadPoolExecutor
    store = KeyStore(tmp_path)
    store.add('\n'.join((KEY1, KEY2)[:key_count]))
    def reserve():
        try:
            store.reserve(7, 20)
            return True
        except TranslationProblem:
            return False
    with ThreadPoolExecutor(8) as pool:
        assert sum(pool.map(lambda _: reserve(), range(8))) == 2 * key_count
    assert all(row['used'] == 14 for row in store.public())


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


def test_numeric_repair_retries_only_failed_chunks_and_keeps_exact_values(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    calls=[]
    def transport(rows,*_):
        calls.append(rows)
        if len(calls)==1:
            return [rows[0].replace('Độ dài','Length'),rows[1].replace('Tọa độ','Coordinates')+' 999']
        assert len(rows)==1 and '>1,2<' not in rows[0], 'Retry must hide the exposed value'
        return [rows[0].replace('Tọa độ','Coordinates')]
    translator=Translator(tmp_path,transport=transport)
    texts=['Độ dài 12 m','Tọa độ (1,2; -3)']
    assert translator.translate(texts,Event()) == ['Length 12 m','Coordinates (1,2; -3)']
    assert len(calls)==2
    assert translator.store.public()[0]['used'] == sum(len(row) for batch in calls for row in batch)
    assert translator.translate(texts,Event()) == ['Length 12 m','Coordinates (1,2; -3)']
    assert len(calls)==2, 'Good values and repaired values must both resume from cache'


def test_invalid_numeric_repair_stops_after_one_attempt_and_never_caches(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    calls=[]
    def transport(rows,*_):
        calls.append(rows)
        return [row+' 999' for row in rows]
    translator=Translator(tmp_path,transport=transport)
    with pytest.raises(TranslationProblem,match='số liệu'):
        translator.translate(['Giá trị 12'],Event())
    assert len(calls)==2
    with closing(translator.store.connect()) as db:
        assert db.execute('select count(*) from cache').fetchone()[0]==0


def test_cancel_before_numeric_repair_never_sends_the_retry(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    cancel=Event(); calls=[]
    def transport(rows,*_):
        calls.append(rows); cancel.set()
        return [row+' 999' for row in rows]
    with pytest.raises(InterruptedError):
        Translator(tmp_path,transport=transport).translate(['Giá trị 12'],cancel)
    assert len(calls)==1


def test_circled_number_labels_from_geometry_deck_never_reach_google(tmp_path):
    translator=Translator(tmp_path,transport=lambda *_:pytest.fail('A numeric label needs no API key or translation'))
    labels=['❶','❷','❸','①','⑳','㊿','⑴','⓿','½','Ⅲ']
    assert translator.translate(labels,Event())==labels


def test_inline_unicode_numbers_restore_exact_glyphs_and_skip_old_bad_cache(tmp_path):
    import hashlib
    KeyStore(tmp_path).add(KEY1)
    calls=[]
    def transport(rows,*_):
        calls.extend(rows)
        return [row.replace('Hoạt động','Activity').replace('>❸<','>4<').replace('>½<','>9<') for row in rows]
    translator=Translator(tmp_path,transport=transport)
    text='Hoạt động ❸, phần ½'
    legacy=hashlib.sha256(('google-nmt-context-v3|vi|en|'+text).encode()).hexdigest()
    translator.store.cache(legacy,'Activity four, part nine')
    assert translator.translate([text],Event())==['Activity ❸, phần ½']
    assert len(calls)==1


def test_source_html_escaped_and_long_content_not_truncated():
    text = '<script>Tiếng Việt</script>\nGiá trị 12 + $x^2$ + ⟦BLC0⟧'
    encoded, locks = protected_html(text)
    assert '<script>' not in encoded
    assert unprotect(encoded, locks) == text
    long = ('Một câu tiếng Việt. ' * 200) + '⟦BLC123⟧'
    parts = chunks(long)
    assert ''.join(parts) == long and all(len(part) <= 1010 for part in parts)


def test_translation_context_exposes_locked_terms_values_and_complete_units():
    text = 'Vận tốc là 1 cm/s và gia tốc là 1,57 cm/s2, với $x=2$.'
    payload, locks = protected_html(text, {'vận tốc': 'velocity', 'gia tốc': 'acceleration'})
    assert '>velocity</span>' in payload and '>1,57 cm/s2</span>' in payload
    assert 'x=2' not in payload, 'Native math stays opaque and exact'
    assert unprotect(payload, locks) == 'velocity là 1 cm/s và acceleration là 1,57 cm/s2, với $x=2$.'
    assert unprotect(payload.replace('>1,57 cm/s2<', '>wrong value<'), locks).count('1,57 cm/s2') == 1
    with pytest.raises(TranslationProblem):
        unprotect(payload.replace('id="BCLLOCK0END"', ''), locks)
    with pytest.raises(TranslationProblem):
        unprotect(payload + payload, locks)
    units, locked = protected_html('Đơn vị (cm/s2), (m/s²) và cm².')
    assert '>cm/s2</span>' in units and '>m/s²</span>' in units and '>cm²</span>' in units
    assert unprotect(units, locked) == 'Đơn vị (cm/s2), (m/s²) và cm².'
    powers, locked = protected_html('Hệ số ω² và chú thích¹.')
    assert '>²</span>' in powers and '>¹</span>' in powers
    assert unprotect(powers, locked) == 'Hệ số ω² và chú thích¹.'


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
