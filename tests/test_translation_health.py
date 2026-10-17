import pytest

from app.translation_health import summarize


@pytest.mark.parametrize('used,level', [(79,'normal'), (80,'warning'), (94,'warning'), (95,'critical'), (100,'exhausted'), (120,'exhausted')])
def test_thresholds_and_remaining_are_local_estimates(used, level):
    health = summarize([{'project':'a','used':used}], 100)
    group = health['groups'][0]
    assert group['level'] == level
    assert group['remaining'] == max(0, 100-used)
    assert health['available'] == (used < 100)


def test_legacy_shared_history_is_separate_from_independent_key_counters():
    health = summarize([{'project':'mặc định','used':0, 'legacyUsed':66174},
                        {'project':'mặc định','used':0, 'legacyUsed':66174}], 500000)
    assert health['used'] == 0 and health['remaining'] == 1000000
    assert health['legacyUsed'] == 66174
    assert len(health['groups']) == 2 and health['counterCount'] == 2
    assert 'cloudRemaining' not in health
    assert health['keyCount'] == 2 and health['groupCount'] == 1
    assert health['totalBudget'] == 1000000


def test_total_local_budget_counts_each_configured_key_independently():
    health = summarize([{'project': 'a', 'used': 20}, {'project': 'a', 'used': 20},
                        {'project': 'b', 'used': 30}], 500000)
    assert health['keyCount'] == 3 and health['groupCount'] == 2
    assert health['used'] == 70 and health['totalBudget'] == 1500000


def test_ordered_fallback_has_another_group_after_exhaustion_and_blocked_keys():
    health = summarize([{'project':'a','used':100}, {'project':'b','used':4,'blocked':'api_key'},
                        {'project':'b','used':4}, {'project':'c','used':0,'blocked':'api_quota'}],100)
    assert health['remaining'] == 96 and health['available'] and health['warning']
