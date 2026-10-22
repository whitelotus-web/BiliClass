from contextlib import closing
from threading import Event

import pytest

from app.google_translation import KeyStore, TranslationProblem, Translator, chunks, protected_html, unprotect

KEY1, KEY2 = 'AIza' + 'a' * 35, 'AIza' + 'b' * 35


def test_native_counts_are_visible_but_ids_and_context_caches_remain_distinct(tmp_path):
    import re

    translator = Translator(tmp_path)
    translator.store.add(KEY1)
    calls = []

    def translate(rows, *_):
        calls.extend(rows)
        results = []
        for row in rows:
            match = re.search(r'(<span[^>]+id="BCLLOCK0END">([13])</span>)', row)
            assert match, row
            results.append('There ' + ('is ' if match[2] == '1' else 'are ') + match[1]
                           + (' plane.' if match[2] == '1' else ' planes.'))
        return results

    translator.transport = translate
    units = [dict(text='Có ⟦BLC0⟧ mặt phẳng.', numbers=[count], xml_locks={}) for count in ('1', '3')]
    expected = ['There is ⟦BLC0⟧ plane.', 'There are ⟦BLC0⟧ planes.']
    assert translator.translate_native(units, [], Event()) == expected
    assert len(calls) == 2
    assert translator.translate_native(list(reversed(units)), [], Event()) == list(reversed(expected))
    assert len(calls) == 2, 'Cache identity must include the actual count'
    payload, locks = protected_html('⟦BLC0⟧', native_values={'⟦BLC0⟧': '3'})
    assert '>3</span>' in payload and unprotect(payload, locks) == '⟦BLC0⟧'
    opaque, locks = protected_html('⟦BLC0⟧', native_values={'⟦BLC0⟧': '3'}, opaque_values=True)
    assert '>3</span>' not in opaque and unprotect(opaque, locks) == '⟦BLC0⟧'


def test_native_variable_count_is_contextual_only_in_math_and_remains_locked(tmp_path):
    calls = []
    translator = Translator(tmp_path, transport=lambda rows, *_: calls.extend(rows) or rows)
    translator.store.add(KEY1)
    translator.configure_terms('Toán', [])
    unit = dict(text='Có ⟦BLC0⟧ tam giác.', numbers=['𝒏'], xml_locks={})
    assert translator.translate_native([unit], [], Event()) == [unit['text']]
    assert '>𝒏</span>' in calls[0]
    calls.clear()
    translator.configure_terms('Hóa học', [])
    translator.translate_native([unit], [], Event())
    assert '>𝒏</span>' not in calls[0]


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


def test_missing_number_token_without_fragment_repair_is_rejected_and_not_cached(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    translator = Translator(tmp_path, transport=lambda *args: ['Velocity'])
    with pytest.raises(TranslationProblem, match='số liệu'):
        translator.translate(['Vận tốc 12'], Event(), fragment_repair=False)
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


def test_invalid_numeric_repair_stops_after_bounded_fragment_attempt_and_never_caches(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    calls=[]
    def transport(rows,*_):
        calls.append(rows)
        return [row+' 999' for row in rows]
    translator=Translator(tmp_path,transport=transport)
    with pytest.raises(TranslationProblem,match='số liệu'):
        translator.translate(['Giá trị 12'],Event())
    assert len(calls)==4, 'Whole text and prose-only repair each have at most two attempts'
    with closing(translator.store.connect()) as db:
        assert db.execute('select count(*) from cache').fetchone()[0]==0


def test_cancel_before_numeric_repair_never_sends_the_retry(tmp_path):
    KeyStore(tmp_path).add(KEY1)
    cancel=Event()
    calls=[]
    def transport(rows,*_):
        calls.append(rows)
        cancel.set()
        return [row+' 999' for row in rows]
    with pytest.raises(InterruptedError):
        Translator(tmp_path,transport=transport).translate(['Giá trị 12'],cancel)
    assert len(calls)==1


@pytest.mark.parametrize('text', [
    'Sử dụng máy tính cầm tay, tìm số đo độ và radian của góc ⟦BLC0⟧ ,biết ⟦BLC1⟧',
    'Nếu ⟦BLC0⟧, tỉ số ⟦BLC1⟧ được gọi là tang của ⟦BLC2⟧,',
    'Độ dài 12 m và tọa độ (1,2; -3).',
])
def test_missing_html_locks_repaired_by_sending_prose_only_and_restoring_exact_tokens(tmp_path, text):
    import re
    from collections import Counter

    from app.translation_batches import NUMBERS

    store = KeyStore(tmp_path)
    store.add(KEY1)
    calls = []

    def transport(rows, *_):
        calls.append(rows)
        if any('<span' in row for row in rows):
            return [re.sub(r'BCLLOCK\d+END', 'lost', row) for row in rows]
        assert all('⟦BLC' not in row and not NUMBERS.findall(row) for row in rows)
        return [row.replace('Sử dụng máy tính cầm tay', 'Use a calculator')
                .replace('Nếu', 'If').replace('Độ dài', 'Length') for row in rows]

    translator = Translator(tmp_path, transport=transport)
    value = translator.translate([text], Event())[0]
    assert value != text and Counter(NUMBERS.findall(value)) == Counter(NUMBERS.findall(text))
    assert re.findall(r'⟦BLC\d+⟧', value) == re.findall(r'⟦BLC\d+⟧', text)
    assert len(calls) == 3 and all('<span' not in row for row in calls[-1])
    assert translator.translate([text], Event()) == [value] and len(calls) == 3
    assert store.public()[0]['used'] == sum(len(row) for batch in calls for row in batch)


def test_cancel_after_opaque_retry_prevents_fragment_requests(tmp_path):
    import re

    KeyStore(tmp_path).add(KEY1)
    cancel, calls = Event(), []

    def transport(rows, *_):
        calls.append(rows)
        if len(calls) == 2:
            cancel.set()
        return [re.sub(r'BCLLOCK\d+END', 'lost', row) for row in rows]

    with pytest.raises(InterruptedError):
        Translator(tmp_path, transport=transport).translate(['Nếu ⟦BLC0⟧ thì ⟦BLC1⟧'], cancel)
    assert len(calls) == 2


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
