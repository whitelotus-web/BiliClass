import json

import pytest

from app.translation_batches import (
    TranslationCache,
    batch_items,
    lock_numbers,
    parse_response,
    prompt,
    restore,
)


def item(text='Vận tốc của vật bằng 12 m/s.', key='s1p1'):
    protected,numbers = lock_numbers(text)
    return {'id':key,'slide':1,'text':protected,'numbers':numbers,'raw':text}


def config(mode='parallel_columns'):
    return {'title':'Cơ năng','subject':'Vật lý','education_level':'THPT','grade':'10',
            'conversion_format':mode,'teacher_notes':'Giữ số liệu và đơn vị.'}


def answer(row, batch='b1'):
    return json.dumps({'batch':batch,'items':[row]},ensure_ascii=False)


def test_round_trip_keeps_numbers_and_validates_complete_ids():
    source = item()
    result = parse_response(answer({'id':source['id'],'en':'The velocity is ⟦BLC0⟧ m/s.'}),[source],'b1','parallel_columns')
    assert restore(result[source['id']]['en'],source['numbers'])=='The velocity is 12 m/s.'
    assert 'Vật lý' in prompt(config(),[source],'b1')
    assert 'Giữ số liệu và đơn vị.' in prompt(config(),[source],'b1')


@pytest.mark.parametrize('row',[
    {'id':'other','en':'The velocity is ⟦BLC0⟧ m/s.'},
    {'id':'s1p1','en':'The velocity is 99 m/s.'},
    {'id':'s1p1','en':'The velocity is ⟦BLC0⟧ ⟦BLC0⟧ m/s.'},
    {'id':'s1p1','en':'The velocity is ⟦BLC2⟧ m/s.'},
    {'id':'s1p1','en':'The velocity is ⟦BLC0⟧ plus 99 m/s.'},
    {'id':'s1p1','en':''},
    {'id':'s1p1','en':'Valid ⟦BLC0⟧','approved':True},
])
def test_wrong_mapping_missing_tokens_and_invented_numbers_are_rejected(row):
    with pytest.raises(ValueError):
        parse_response(answer(row),[item()],'b1','parallel_columns')


def test_missing_duplicate_or_wrong_batch_does_not_count_as_done():
    row = {'id':'s1p1','en':'The velocity is ⟦BLC0⟧ m/s.'}
    for value in [{'batch':'wrong','items':[row]}, {'batch':'b1','items':[]}, {'batch':'b1','items':[row,row]}]:
        with pytest.raises(ValueError):
            parse_response(json.dumps(value),[item()],'b1','parallel_columns')


def test_keyword_response_requires_both_display_and_english_narration():
    source=item()
    with pytest.raises(ValueError):
        parse_response(answer({'id':source['id'],'en':'The velocity is ⟦BLC0⟧ m/s.'}),[source],'b1','integrated_keywords')
    result=parse_response(answer({'id':source['id'],'en':'The velocity is ⟦BLC0⟧ m/s.',
        'mixed':'Vận tốc (velocity) của vật bằng ⟦BLC0⟧ m/s.'}),[source],'b1','integrated_keywords')
    assert 'velocity' in result[source['id']]['mixed']


def test_long_body_cannot_be_replaced_by_a_title():
    source=item('Thầy cô yêu cầu dịch đầy đủ nội dung giải thích về sự chuyển hóa năng lượng của vật.')
    with pytest.raises(ValueError):
        parse_response(answer({'id':source['id'],'en':'Energy'}),[source],'b1','parallel_columns')


def test_cache_checks_scope_numbers_and_corruption(tmp_path):
    source=item()
    value={'en':'The velocity is ⟦BLC0⟧ m/s.'}
    cache=TranslationCache(tmp_path,config())
    cache.put(source,value)
    assert cache.get(source)==value
    assert cache.get(item('Vận tốc của vật bằng 20 m/s.')) is None
    assert TranslationCache(tmp_path,{**config(),'grade':'11'}).get(source) is None
    cache.path(source).write_text('{',encoding='utf-8')
    assert cache.get(source) is None


def test_batch_limits_do_not_drop_or_reorder_items():
    items=[item('Nội dung bài học.',f's1p{i}') for i in range(7)]
    batches=batch_items(items,maximum_items=3,maximum_chars=100)
    assert [len(batch) for batch in batches]==[3,3,1]
    assert [row['id'] for batch in batches for row in batch]==[row['id'] for row in items]


@pytest.mark.parametrize('heading', ['ChatGPT said:', 'ChatGPT đã nói:', 'ChatGPT nói:'])
def test_accessible_role_heading_is_not_part_of_json(heading):
    source = item()
    text = heading + '\n\n' + answer({'id':source['id'],'en':'The velocity is ⟦BLC0⟧ m/s.'})
    assert parse_response(text,[source],'b1','parallel_columns')[source['id']]['en'].endswith('m/s.')


def test_embedded_source_digits_are_protected_before_send():
    text, numbers = lock_numbers('Câu hỏi SGK tr25: H2O và A0, 12 m/s.')
    assert numbers == ['25', '2', '0', '12']
    assert text == 'Câu hỏi SGK tr⟦BLC0⟧: H⟦BLC1⟧O và A⟦BLC2⟧, ⟦BLC3⟧ m/s.'
    assert restore(text,numbers) == 'Câu hỏi SGK tr25: H2O và A0, 12 m/s.'


def test_old_checkpoint_page_reference_can_be_reformatted_but_not_changed_or_duplicated():
    source = {'id':'s52o6b0p0','slide':52,'text':'Câu hỏi (SGK – tr25): Tìm thêm ví dụ về dao động cưỡng bức',
              'numbers':[]}
    good = 'Question (Textbook – p. 25): Find additional examples of forced oscillations.'
    assert parse_response(answer({'id':source['id'],'en':good}),[source],'b1','parallel_columns')
    for bad in [good.replace('25','26'),good+' 25',good.replace('25',''),good+' 99']:
        with pytest.raises(ValueError):
            parse_response(answer({'id':source['id'],'en':bad}),[source],'b1','parallel_columns')


def test_arbitrary_prose_and_multiple_json_objects_remain_invalid():
    source=item()
    text=answer({'id':source['id'],'en':'The velocity is ⟦BLC0⟧ m/s.'})
    for invalid in ['Here is the answer: '+text,text+'\n'+text]:
        with pytest.raises(ValueError):parse_response(invalid,[source],'b1','parallel_columns')


def test_valid_pre_upgrade_translation_cache_stays_reusable(tmp_path):
    source={'id':'s52o6b0p0','slide':52,'text':'Câu hỏi SGK tr25: tìm thêm ví dụ về dao động cưỡng bức','numbers':[]}
    cache=TranslationCache(tmp_path,config())
    value={'en':'Question on textbook p. 25: find more examples of forced oscillations.'}
    cache.put(source,value)
    assert TranslationCache(tmp_path,config()).get(source)==value
