import copy
import json
import time
from contextlib import closing
from threading import Event

import pytest

from app import alternative_translation as api
from app import terminology_memory
from app import translation_knowledge as context
from app.google_settings_tasks import read_state
from app.google_translation import KeyStore, Translator
from app.library import Library
from app.school_subjects import CURRICULUM_SUBJECTS
from app.terminology_lookup import lookup, valid_reference
from app.terminology_memory import MAX_DATABASE, Memory
from app.terminology_seed import SUBJECT_GROUPS, ensure_seed, seed_pack, statistics, terms_for
from app.translation_provider import snapshot
from app.translation_terms import TermPolicy


def config(**values):
    return dict(translation_knowledge_version=1, translation_knowledge_online=False,
                subject='Toán', grade='11', title='Bài thực hành', source_sha256='source', **values)


def plan(tmp_path, texts=('Đa thức', 'Biến cố'), *, subject='Toán', online=False, resolver=None, **values):
    folder = tmp_path / 'job'
    folder.mkdir(exist_ok=True)
    return context.prepare(tmp_path, folder, {**config(), 'subject': subject, 'translation_knowledge_online': online, **values},
                           [dict(text=text, slide=i+1) for i, text in enumerate(texts)], Event(), resolver=resolver)


def reference(term='đồng cấu nhóm', subject='Toán'):
    return dict(vi=term, en='group homomorphism', subject=subject, status='online_reference',
                source_id='Q123', source_url='https://www.wikidata.org/wiki/Q123')


def test_seed_all_subject_choices_compact_separate_and_idempotent(tmp_path):
    pack = seed_pack()
    assert set(CURRICULUM_SUBJECTS) <= set(SUBJECT_GROUPS)
    assert all(terms_for(subject) for subject in CURRICULUM_SUBJECTS)
    assert statistics()['concepts'] >= 1100
    assert len(json.dumps(pack, ensure_ascii=False).encode()) < 1_100_000
    assert not pack['manifest']['contains_full_text']
    assert all(entry['status'] == 'reference_only' for entry in pack['entries'])
    with closing(Library(tmp_path)) as library:
        library.save_term('Toán', 'đa thức', 'teacher polynomial', True)
        assert ensure_seed(library) and not ensure_seed(library)
        assert library.glossary('Toán')[0]['en'] == 'teacher polynomial'
        assert library.knowledge_stats()['entries'] == statistics()['entries']
        assert not library.knowledge_terms('Toán')  # Reference nouns never become global locks.


def test_seed_exact_only_teacher_priority_and_composite_subjects():
    policy = TermPolicy('Toán', references=terms_for('Toán'))
    assert policy.exact('đa thức') == 'polynomial'
    assert 'đa thức' not in policy.matches('Có hai đa thức khác nhau.')
    teacher = TermPolicy('Toán', [dict(subject='Toán', vi='đa thức', en='custom polynomial', locked=True)], terms_for('Toán'))
    assert teacher.exact('đa thức') == 'custom polynomial'
    assert teacher.matches('Đa thức cần tìm.')['đa thức'] == 'custom polynomial'
    assert {'nguyên tử', 'tế bào', 'gia tốc'} <= {row['vi'] for row in terms_for('Khoa học tự nhiên')}
    assert terms_for('Địa lí') == terms_for('Địa lý')
    assert not terms_for('Không phải môn')


def test_selected_subject_limits_and_weak_inference(tmp_path):
    value = plan(tmp_path, ('đa thức; xác suất; biến cố; tế bào',))
    assert {row['vi'] for row in value['terms']} >= {'đa thức', 'xác suất', 'biến cố'}
    assert 'tế bào' not in {row['vi'] for row in value['terms']}
    assert context.infer_subject('tế bào') == ''
    assert context.infer_subject('đa thức xác suất biến cố') == 'Toán'
    assert plan(tmp_path, ('đa thức xác suất biến cố',), subject='Khác')['inferred']
    assert context.prepare(tmp_path, tmp_path, {}, [], Event()) is None
    assert len(context._text_rows([{'text': 'x'*5000}]*2000)) == 36


def add_pair(library, vi, en, *, approved=True, subject='Toán', grade='11'):
    lesson = library.create('Đã đối chiếu', subject, 'THPT', grade, [('p1', vi)])
    return library.edit_segment(lesson['id'], lesson['segments'][0]['id'], vi, en, approved)


def test_memory_only_approved_current_same_subject_grade_case_numbers(tmp_path):
    vi = 'Cho một hình tứ diện.'
    with closing(Library(tmp_path)) as library:
        add_pair(library, vi, 'Consider a tetrahedron.')
        add_pair(library, 'Bản nháp chưa duyệt.', 'A draft.', approved=False)
        add_pair(library, 'Có 3 hình tam giác.', 'There are 4 triangles.')
        add_pair(library, 'Sai lớp sẽ bỏ qua.', 'Ignore this grade.', grade='12')
        add_pair(library, 'Sai môn sẽ bỏ qua.', 'Ignore this subject.', subject='Vật lý')
    texts = (vi, vi.upper(), 'Bản nháp chưa duyệt.', 'Có 3 hình tam giác.', 'Sai lớp sẽ bỏ qua.', 'Sai môn sẽ bỏ qua.')
    value = plan(tmp_path, texts)
    assert value['memory'] == {vi: 'Consider a tetrahedron.'}
    with closing(Library(tmp_path)) as library:
        add_pair(library, vi, 'A different approved rendering.')
    assert not plan(tmp_path, texts, source_sha256='new source')['memory']


def test_resume_freezes_reference_and_approved_sentence_but_corruption_rebuilds(tmp_path):
    with closing(Library(tmp_path)) as library:
        add_pair(library, 'Cho một hình tứ diện.', 'Consider a tetrahedron.')
    calls = []
    def resolve(term, subject, *_args, **_kwargs):
        calls.append(term)
        return reference(term, subject)
    value = plan(tmp_path, ('đồng cấu nhóm', 'Cho một hình tứ diện.'), online=True, resolver=resolve)
    assert len(calls) <= 3 and len(value['hints']) >= 1
    assert plan(tmp_path, ('đồng cấu nhóm', 'Cho một hình tứ diện.'), online=True,
                resolver=lambda *_a, **_k: pytest.fail('Resume must not refresh')) == value
    path = tmp_path / 'job/terminology-context.json'
    path.write_text('{broken', encoding='utf-8')
    rebuilt = plan(tmp_path, ('đồng cấu nhóm', 'Cho một hình tứ diện.'), online=True, resolver=resolve)
    assert rebuilt['fingerprint'] == value['fingerprint']
    rebuilt['terms'] = [dict(vi='unsafe', en='new', status='curated_reference')]
    rebuilt['fingerprint'] = context._digest({key: rebuilt[key] for key in context._FINGERPRINT_FIELDS})
    path.write_text(json.dumps(rebuilt), encoding='utf-8')
    assert plan(tmp_path, ('đồng cấu nhóm', 'Cho một hình tứ diện.'), online=True)['terms'] != rebuilt['terms']


@pytest.mark.parametrize('record', [None, {}, {'status': 'curated_reference', 'vi': 'x', 'en': 'y'},
                                  {**reference(), 'source_url': 'https://example.com/fake'}])
def test_unverified_resolver_never_enters_trusted_terms(tmp_path, record):
    value = plan(tmp_path, ('đồng cấu nhóm',), online=True, resolver=lambda *_a, **_k: record)
    assert not value['hints'] and not value['terms'] and value['unresolved']


def test_optional_network_or_cache_failure_does_not_block_translation(tmp_path):
    def unavailable(*_args, **_kwargs):
        raise TimeoutError('private lesson and URL must not be displayed')
    value = plan(tmp_path, ('đồng cấu nhóm',), online=True, resolver=unavailable)
    assert value['online_status'] == 'unavailable' and 'private' not in str(value)
    (tmp_path / 'translation_knowledge/references.db').write_bytes(b'not sqlite')
    assert plan(tmp_path, ('đồng cấu nhóm',), online=True, source_sha256='new')['online_status'] == 'unavailable'


def test_reference_store_ttl_subject_isolation_pruning_and_no_machine_drafts(tmp_path, monkeypatch):
    memory = Memory(tmp_path)
    with pytest.raises(ValueError):
        memory.remember('Toán', 'đồng cấu nhóm', {'status': 'approved', 'en': 'machine draft'})
    monkeypatch.setattr(terminology_memory, 'MAX_ROWS', 2)
    for i in range(3):
        memory.remember('Toán', 'term' + str(i), dict(vi='term'+str(i), en='', status='unresolved'))
    assert memory.get('Toán', 'term0') is None
    assert memory.get('Vật lý', 'term2') is None
    assert memory.stats()['unresolved'] == 2
    monkeypatch.setattr(terminology_memory.time, 'time', lambda: time.monotonic() + 10**11)
    assert memory.get('Toán', 'term2') is None
    assert memory.path.stat().st_size < MAX_DATABASE


def test_lookup_exact_vi_alias_subject_and_unique_sense_only():
    entity = dict(labels={'vi': {'value': 'đồng cấu nhóm'}, 'en': {'value': 'group homomorphism'}},
                  descriptions={'en': {'value': 'mathematical function between groups'}})
    def fetch(parameters, _deadline):
        assert 'đồng cấu nhóm' == parameters.get('search', 'đồng cấu nhóm')
        return {'search': [{'id': 'Q123'}]} if parameters['action'] == 'wbsearchentities' else {'entities': {'Q123': entity}}
    result = lookup('đồng cấu nhóm', 'Toán', Event(), fetch=fetch)
    assert valid_reference(result, 'đồng cấu nhóm', 'Toán')
    entity['descriptions']['en']['value'] = 'a type of sport'
    assert lookup('đồng cấu nhóm', 'Toán', Event(), fetch=fetch) is None
    entity['descriptions']['en']['value'] = 'mathematical function'
    entity['labels']['vi']['value'] = 'không khớp'
    assert lookup('đồng cấu nhóm', 'Toán', Event(), fetch=fetch) is None
    entity['aliases'] = {'vi': [{'value': 'đồng cấu nhóm'}]}
    assert lookup('đồng cấu nhóm', 'Toán', Event(), fetch=fetch)
    def ambiguous(parameters, _deadline):
        return ({'search': [{'id': 'Q123'}, {'id': 'Q456'}]} if parameters['action'] == 'wbsearchentities'
                else {'entities': {'Q123': entity, 'Q456': entity}})
    assert lookup('đồng cấu nhóm', 'Toán', Event(), fetch=ambiguous) is None


@pytest.mark.parametrize('term,subject', [('https://example.org', 'Toán'), ('đồng cấu nhóm', 'Khác'), ('bài 11', 'Toán')])
def test_lookup_no_arbitrary_queries_or_unrecognised_subject(term, subject):
    assert lookup(term, subject, Event(), fetch=lambda *_: pytest.fail('Unexpected request')) is None


@pytest.mark.parametrize('payload', [{'search': None}, {'search': []}, {'search': [{'id': 'Q123'}], 'entities': []}])
def test_lookup_malformed_service_returns_no_hint(payload):
    assert lookup('đồng cấu nhóm', 'Toán', Event(), fetch=lambda *_: payload) is None


def test_cancel_while_receiving_reference():
    cancel = Event()
    def fetch(parameters, _deadline):
        if parameters['action'] == 'wbsearchentities':
            return {'search': [{'id': 'Q123'}]}
        cancel.set()
        return {'entities': {}}
    with pytest.raises(InterruptedError):
        lookup('đồng cấu nhóm', 'Toán', cancel, fetch=fetch)


@pytest.mark.parametrize('provider', ['google', 'languageapp', 'gemini', 'deepl'])
def test_reference_context_shared_policy_and_cache_isolated_per_lesson(tmp_path, provider):
    from app.alternative_translation import DEFAULT_MODEL, AlternativeStore, AlternativeTranslator

    calls = []
    def send(texts, credential, *_):
        calls.append(credential)
        return [text.replace('Điều cần tìm.', 'Find the result.') for text in texts]
    if provider == 'google':
        KeyStore(tmp_path).add('AIza' + 'a'*35)
        translator = Translator(tmp_path, transport=send)
    else:
        option = ('https://script.google.com/macros/s/' + 'x'*30 + '/exec' if provider == 'languageapp' else
                  DEFAULT_MODEL if provider == 'gemini' else 'developer')
        AlternativeStore(tmp_path, provider).configure('a'*32, option)
        translator = AlternativeTranslator(tmp_path, provider, transport=send)
    value = plan(tmp_path)
    translator.configure_terms('Toán', [])
    translator.configure_knowledge(value)
    namespace = translator.cache_namespace
    expected_cost = (1 if provider == 'languageapp' else 10 + len(translator.lesson_context) if provider == 'gemini' else 10)
    assert translator._request_cost(['x'*10]) == expected_cost
    translator.configure_knowledge(value)
    assert translator.cache_namespace == namespace
    assert translator.translate(['Đa thức'], Event()) == ['Polynomial']
    assert not calls
    assert translator.translate(['Điều cần tìm.'], Event()) == ['Find the result.']
    assert len(calls) == 1
    if provider in ('gemini', 'deepl'):
        assert 'Toán' in calls[-1]['context']
    elif provider == 'languageapp':
        assert 'context' not in calls[-1]
    assert translator.translate(['Điều cần tìm.'], Event()) == ['Find the result.']
    assert len(calls) == 1
    another = plan(tmp_path, grade='12')
    translator.configure_knowledge(another)
    translator.translate(['Điều cần tìm.'], Event())
    assert len(calls) == 2 and translator.cache_namespace != namespace


def test_prompt_bounded_valid_data_and_teacher_terms_win(tmp_path):
    value = plan(tmp_path)
    expanded = copy.deepcopy(value)
    expanded['terms'] = [dict(vi='x'*110, en='y'*110)]*96
    assert len(context.prompt_context(expanded)) <= 5500
    assert json.loads(context.prompt_context(expanded))['subject'] == 'Toán'
    KeyStore(tmp_path).add('AIza' + 'a'*35)
    translator = Translator(tmp_path, transport=lambda *_: pytest.fail('No request needed'))
    translator.configure_terms('Toán', [dict(vi='đa thức', en='custom polynomial', subject='Toán', locked=True)])
    value['memory']['Cho một hình tứ diện.'] = 'Consider a tetrahedron.'
    translator.configure_knowledge(value)
    assert translator.translate(['đa thức', 'Cho một hình tứ diện.'], Event()) == ['custom polynomial', 'Consider a tetrahedron.']
    assert translator.reviewed_reused == {'Cho một hình tứ diện.'}
    report = context.review(value, [], [], memory_used=translator.reviewed_reused)
    assert report['reused'] == 1 and '1 câu đã duyệt được dùng lại' in report['summary']
    assert context.review(value, [], [])['reused'] == 0


def test_automatic_reference_for_new_work_ignores_old_switches_and_preserves_queued_policy(tmp_path):
    from app.conversion_input import creation_config
    from app.google_conversion import prepare

    with closing(Library(tmp_path)) as library:
        library.set_setting('translation_knowledge_enabled', False)
        library.set_setting('translation_knowledge_online', False)
    assert read_state(tmp_path)['knowledge']['enabled'] is True
    assert snapshot(tmp_path)['translation_knowledge_version'] == 1
    assert snapshot(tmp_path)['translation_knowledge_online'] is True
    settings = creation_config('Bài mới', 'Toán', 'THPT', '11', 'parallel_columns', 'standard', 'template')
    new = prepare(tmp_path, settings, text='đa thức')
    assert new['config']['translation_knowledge_version'] == 1 and new['config']['translation_knowledge_online'] is True
    pinned = dict(translation_knowledge_version=0, translation_knowledge_online=False)
    old = prepare(tmp_path, {**settings, **pinned}, text='đa thức')
    assert old['config']['translation_knowledge_version'] == 0 and old['config']['translation_knowledge_online'] is False


def test_gemini_and_deepl_send_context_as_supported_fields(monkeypatch):
    calls = []
    def request(url, payload, headers, provider, **_kwargs):
        calls.append(payload)
        return ({'translations': [{'text': 'Hello'}]} if provider == 'deepl' else
                {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': json.dumps({'translations': [{'index': 0, 'text': 'Hello'}]})}]}}]})
    monkeypatch.setattr(api, 'json_request', request)
    credential = dict(key='a'*32, option=api.DEFAULT_MODEL, context='Subject: Physics. Lesson: Energy.')
    api.gemini_request(['Xin chào'], credential, 'vi', 'en')
    assert credential['context'] in calls[-1]['contents'][0]['parts'][0]['text']
    api.deepl_request(['Xin chào'], credential, 'vi', 'en')
    assert calls[-1]['context'] == credential['context']


def test_diagnostics_hide_stale_reference_report():
    from app.lesson_diagnostics import layout

    lesson = dict(source={'sha256': 'current'}, external_deck={'terminology_review': dict(artifact_sha256='old', summary='Stale')})
    assert not layout(lesson)['terminology']
    lesson['external_deck']['terminology_review']['artifact_sha256'] = 'current'
    assert layout(lesson)['terminology']['summary'] == 'Stale'


def test_large_approved_scope_does_not_scan_every_lesson(tmp_path):
    with closing(Library(tmp_path)) as library:
        for _ in range(101):
            add_pair(library, 'Cho một hình tứ diện.', 'Consider a tetrahedron.')
    assert not plan(tmp_path, ('Cho một hình tứ diện.',))['memory']


def test_disabling_layer_does_not_leave_previous_context_on_reused_adapter(tmp_path):
    translator = Translator(tmp_path)
    translator.configure_knowledge(plan(tmp_path))
    assert '|lesson-reference-v1|' in translator.cache_namespace
    translator.configure_terms('Vật lý', [])
    assert translator.cache_namespace == 'google-nmt-context-v3'
    assert not translator.lesson_context and not translator.reviewed_memory
    assert translator.term_policy.exact('đa thức') is None


def test_art_reference_does_not_match_particle_or_article_description():
    from app.terminology_lookup import _domain_match

    assert not _domain_match('particle in an article', ('art',))
    assert _domain_match('a visual art form', ('art',))


def test_cancel_before_prepare_does_not_create_context(tmp_path):
    cancel = Event()
    cancel.set()
    with pytest.raises(InterruptedError):
        context.prepare(tmp_path, tmp_path, config(), [], cancel)
    assert not (tmp_path / 'terminology-context.json').exists()


def test_all_groups_expanded_and_all_subjects_have_reference_domains():
    from app.terminology_lookup import domain_markers
    from app.terminology_seed import GROUPS, vocabulary
    from app.terminology_seed_extra import EXTRA

    assert set(EXTRA) == set(GROUPS)
    for group, text in EXTRA.items():
        assert len([row for row in text.replace('\n', ';').split(';') if row.strip()]) >= 20
        assert len(vocabulary()[group]) > len([row for row in GROUPS[group][1].replace('\n', ';').split(';') if row.strip()])
    assert all(domain_markers(subject) for subject in SUBJECT_GROUPS)
    assert not domain_markers('Môn tùy biến chưa xác định')
    assert 'chem' in domain_markers('Khoa học tự nhiên')
    assert 'music' in domain_markers('Nghệ thuật')


@pytest.mark.parametrize('subject,vi,en', [
    ('Toán', 'phép tịnh tiến', 'translation'), ('Sinh học', 'dịch mã', 'translation'),
    ('Vật lý', 'hiệu suất', 'efficiency'), ('Hóa học', 'điện phân', 'electrolysis'),
    ('Tin học', 'xác thực', 'authentication'), ('Công nghệ', 'cảm biến', 'sensor'),
    ('Lịch sử', 'tư liệu gốc', 'primary source'), ('Địa lí', 'múi giờ', 'time zone'),
    ('Ngữ văn', 'độc thoại', 'monologue'), ('Tiếng Việt', 'từ đồng nghĩa', 'synonym'),
    ('Ngoại ngữ 2', 'danh động từ', 'gerund'), ('Tiếng dân tộc thiểu số', 'ngữ cảnh', 'context'),
    ('Âm nhạc', 'hợp âm ba', 'triad'), ('Mĩ thuật', 'phối cảnh một điểm tụ', 'one-point perspective'),
    ('Giáo dục công dân', 'đồng cảm', 'empathy'), ('Đạo đức', 'tự trọng', 'self-respect'),
    ('Giáo dục kinh tế và pháp luật', 'chi phí cơ hội', 'opportunity cost'),
    ('Giáo dục thể chất', 'phát cầu', 'badminton serve'),
    ('Hoạt động trải nghiệm', 'tư duy phản biện', 'critical thinking'),
    ('Hoạt động trải nghiệm, hướng nghiệp', 'đào tạo nghề', 'vocational training'),
    ('Nội dung giáo dục của địa phương', 'di sản tư liệu', 'documentary heritage'),
    ('Giáo dục quốc phòng và an ninh', 'phòng thủ dân sự', 'civil defense'),
    ('Khoa học tự nhiên', 'thẩm thấu', 'osmosis'), ('Tự nhiên và Xã hội', 'kính lúp', 'magnifying glass'),
    ('Tin học và Công nghệ', 'cầu chì', 'fuse'), ('Lịch sử và Địa lí', 'phong hóa', 'weathering'),
    ('Nghệ thuật', 'tranh màu nước', 'watercolor painting'),
])
def test_extended_reference_is_subject_scoped_and_heading_only(subject, vi, en):
    policy = TermPolicy(subject, references=terms_for(subject))
    assert policy.exact(vi) == en
    assert vi not in policy.matches('Tìm hiểu về ' + vi + ' trong bài học.')


def test_seed_upgrade_preserves_teacher_terms_and_lessons(tmp_path):
    old = seed_pack()
    old['manifest']['version'] = '2026.10.25.1'
    old['entries'] = old['entries'][:20]
    with closing(Library(tmp_path)) as library:
        library.install_knowledge_pack(old)
        library.save_term('Toán', 'cực trị', 'Teacher wording', True)
        lesson = add_pair(library, 'Cho một hình tứ diện.', 'Consider a tetrahedron.')
        assert ensure_seed(library)
        assert library.get(lesson['id']) == lesson
        assert library.glossary('Toán')[0]['en'] == 'Teacher wording'
        assert library.knowledge_stats()['entries'] == statistics()['entries']
        assert not ensure_seed(library)


def test_new_lessons_learn_past_cached_first_items_without_extra_calls(tmp_path):
    texts = ('đồng cấu nhóm', 'không gian vectơ', 'vành giao hoán', 'nhóm đối xứng',
             'ánh xạ tuyến tính', 'đại số tuyến tính', 'dạng song tuyến tính')
    calls = []
    def resolve(term, subject, *_a, **_k):
        calls.append(term)
        return reference(term, subject)
    first = plan(tmp_path, texts, online=True, resolver=resolve, source_sha256='lesson1')
    assert len(calls) == first['new_lookups'] == first['new_references'] == 3
    assert first['deferred'] and first['cached_references'] == 0
    second = plan(tmp_path, texts, online=True, resolver=resolve, source_sha256='lesson2')
    assert second['new_lookups'] == 3 and second['cached_references'] == 3
    assert len(second['hints']) == 6 and calls[:3] == list(texts[:3])
    assert len(calls) == len(set(calls))
    # Same job resumes with its frozen state, rather than spending new requests.
    assert plan(tmp_path, texts, online=True, resolver=lambda *_a, **_k: pytest.fail('Unexpected refresh'),
                source_sha256='lesson2') == second
    third = plan(tmp_path, texts, online=True, resolver=resolve, source_sha256='lesson3')
    assert third['new_lookups'] <= 3 and third['cached_references'] == 6
    assert len(third['hints']) >= 7 and len(calls) == len(set(calls))


def test_known_misses_do_not_spend_lookup_allowance_again(tmp_path):
    texts = ('đồng cấu nhóm', 'không gian vectơ', 'vành giao hoán', 'nhóm đối xứng')
    calls = []
    def resolve(term, *_a, **_k):
        calls.append(term)
        return None
    first = plan(tmp_path, texts, online=True, resolver=resolve, source_sha256='lesson1')
    second = plan(tmp_path, texts, online=True, resolver=resolve, source_sha256='lesson2')
    assert first['new_lookups'] == 3 and second['new_lookups'] == 1
    assert len(calls) == 4 and not second['deferred']
    assert not second['hints'] and len(second['unresolved']) == 4


def test_new_contextual_hints_are_not_crowded_out_by_seed_terms(tmp_path):
    value = plan(tmp_path, ('; '.join(row['vi'] for row in terms_for('Toán')),))
    value['hints'] = [reference()]
    assert len(value['terms']) >= 24
    assert json.loads(context.prompt_context(value))['reference_terms'][0]['vi'] == 'đồng cấu nhóm'


@pytest.mark.parametrize('provider', ['google', 'languageapp', 'gemini', 'deepl'])
@pytest.mark.parametrize('repair_succeeds', [True, False])
def test_automatic_language_repair_is_bounded_and_keeps_valid_chunks(tmp_path, provider, repair_succeeds):
    from app.alternative_translation import DEFAULT_MODEL, AlternativeStore, AlternativeTranslator
    from app.google_translation import TranslationProblem

    source = 'Nội dung của bài học được trình bày trong các ví dụ.'
    good_source = 'Đây là ví dụ.'
    calls = []
    def transport(texts, credential, *_a):
        calls.append((list(texts), credential))
        return [('This is an example.' if 'Đây' in text else
                 'The lesson content is presented through examples.' if len(calls) > 1 and repair_succeeds else
                 'Content của bài học được trình bày trong các ví dụ.') for text in texts]
    if provider == 'google':
        KeyStore(tmp_path).add('AIza' + 'a'*35)
        translator = Translator(tmp_path, transport=transport)
    else:
        option = ('https://script.google.com/macros/s/' + 'x'*30 + '/exec' if provider == 'languageapp' else
                  DEFAULT_MODEL if provider == 'gemini' else 'developer')
        AlternativeStore(tmp_path, provider).configure('a'*32, option)
        translator = AlternativeTranslator(tmp_path, provider, transport=transport)
    translator.configure_knowledge(plan(tmp_path, (source, good_source)))
    if repair_succeeds:
        assert translator.translate([source, good_source], Event()) == [
            'The lesson content is presented through examples.', 'This is an example.']
    else:
        with pytest.raises(TranslationProblem, match='tiếng Việt'):
            translator.translate([source, good_source], Event())
    assert [len(texts) for texts, _ in calls] == [2, 1]
    assert translator.translate([good_source], Event()) == ['This is an example.']
    assert len(calls) == 2
    if provider == 'gemini':
        assert calls[1][1]['repair'] is True


def test_language_guard_ignores_names_and_protected_vietnamese():
    from app.google_translation import _protected_text, protected_html
    from app.translation_quality import untranslated_prose

    assert untranslated_prose('Probability có điều kiện mô tả khả năng xảy ra của một biến cố.')
    assert not untranslated_prose('Nguyễn Văn An and Đà Nẵng are names in the source.')
    payload, _ = protected_html('The phrase được giữ nguyên trong bài remains unchanged.',
                                 {'được giữ nguyên trong bài': 'được giữ nguyên trong bài'})
    assert not untranslated_prose(_protected_text(payload))
    assert not untranslated_prose('Cells use RNA to synthesise proteins during translation.')


def test_biology_countable_nouns_keep_heading_but_allow_sentence_inflection():
    policy = TermPolicy('Sinh học')
    assert policy.exact('tế bào') == 'cell'
    assert 'tế bào' not in policy.matches('Tế bào sử dụng thông tin trên RNA.')
    teacher = TermPolicy('Sinh học', [dict(vi='tế bào', en='custom cell', subject='Sinh học', locked=True)])
    assert teacher.matches('Tế bào sử dụng RNA.')['tế bào'] == 'custom cell'


def test_specific_reference_phrase_does_not_freeze_generic_inner_noun():
    source = 'Xác suất có điều kiện mô tả khả năng xảy ra của một biến cố.'
    policy = TermPolicy('Toán', references=terms_for('Toán'))
    assert 'xác suất' not in policy.matches(source)
    assert policy.exact('Xác suất có điều kiện') == 'conditional probability'
    teacher = TermPolicy('Toán', [dict(vi='xác suất', en='teacher probability', subject='Toán', locked=True)], terms_for('Toán'))
    assert teacher.matches(source)['xác suất'] == 'teacher probability'
