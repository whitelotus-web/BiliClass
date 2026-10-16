from app.library_view import options, query


def rows():
    base = {'education_level': 'THPT', 'grade': '11', 'status': 'REVIEW_REQUIRED', 'quality_failures': 0}
    return [
        {**base, 'id': 'physics', 'title': 'Dao động điều hòa', 'subject': 'Vật lý',
         'narration': {'variants': [{'mode': 'en', 'ready': True}, {'mode': 'both', 'ready': True}]}},
        {**base, 'id': 'it', 'title': 'Hệ điều hành', 'subject': 'Tin học', 'status': 'READY_TO_TEACH',
         'narration': {'status': 'none'}},
        {**base, 'id': 'unfinished', 'title': 'Cơ năng', 'subject': 'Vật lý', 'grade': '10',
         'narration': {'variants': [{'mode': 'vi', 'ready': False}]}},
        {**base, 'id': 'fail', 'title': 'Bài cần sửa bố cục', 'subject': 'Tin học',
         'status': 'READY_TO_TEACH', 'quality_failures': 1, 'narration': {'status': 'none'}}]


def test_unaccented_search_matches_words_in_any_order_and_combines_filters():
    result = query(rows(), 'HOA dao DONG', subject='Vật lý', grade='THPT|11', state='review', voice='both')
    assert [row['id'] for row in result['rows']] == ['physics']
    assert not query(rows(), 'dao dong', subject='Tin học')['rows']


def test_readiness_filter_never_calls_a_failed_layout_ready():
    assert [r['id'] for r in query(rows(), state='ready')['rows']] == ['it']
    assert 'fail' in [r['id'] for r in query(rows(), state='review')['rows']]


def test_voice_filter_distinguishes_ready_languages_partial_and_absent():
    assert [r['id'] for r in query(rows(), voice='en')['rows']] == ['physics']
    assert [r['id'] for r in query(rows(), voice='partial')['rows']] == ['unfinished']
    assert not query(rows(), voice='vi')['rows']
    assert [r['id'] for r in query(rows(), voice='none')['rows']] == ['it', 'fail']


def test_pagination_limits_created_rows_and_clamps_after_filtering():
    many = [{**rows()[1], 'id': str(i)} for i in range(43)]
    result = query(many, page=3)
    assert result['total'] == 43 and len(result['rows']) == 3
    assert (result['start'], result['end']) == (41, 43)
    result = query(many, text='not found', page=3)
    assert result['rows'] == [] and result['page'] == 1 and result['start'] == result['end'] == 0


def test_filter_options_are_unique_and_based_on_real_catalog():
    assert [r['label'] for r in options(rows(), 'subject')] == ['Tất cả môn học', 'Tin học', 'Vật lý']
    assert [r['id'] for r in options(rows(), 'grade')] == ['', 'THPT|10', 'THPT|11']
