import pytest

from app.translation_health import summarize


@pytest.mark.parametrize('used,level', [(79,'normal'), (80,'warning'), (94,'warning'), (95,'critical'), (100,'exhausted'), (120,'exhausted')])
def test_thresholds_and_remaining_are_local_estimates(used, level):
    health = summarize([{'project':'a','used':used}], 100)
    group = health['groups'][0]
    assert group['level'] == level
    assert group['remaining'] == max(0, 100-used)
    assert health['available'] == (used < 100)


def test_default_keys_share_history_without_double_counting_or_claimed_cloud_balance():
    health = summarize([{'project':'mặc định','used':66174}, {'project':'mặc định','used':66174}], 500000)
    assert health['used'] == 66174 and health['remaining'] == 433826
    assert len(health['groups']) == 1 and health['unverified']
    assert 'cloudRemaining' not in health


def test_ordered_fallback_has_another_group_after_exhaustion_and_blocked_keys():
    health = summarize([{'project':'a','used':100}, {'project':'b','used':4,'blocked':'api_key'},
                        {'project':'b','used':4}, {'project':'c','used':0,'blocked':'api_quota'}],100)
    assert health['remaining'] == 96 and health['available'] and health['warning']
