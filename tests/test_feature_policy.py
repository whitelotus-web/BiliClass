import pytest

from app.feature_policy import experimental_teaching_enabled


@pytest.mark.parametrize('frozen,expected', [(False, True), (True, False)])
def test_development_keeps_features_and_packaged_release_hides_them(monkeypatch, frozen, expected):
    monkeypatch.delenv('BILICLASS_EXPERIMENTAL_TEACHING', raising=False)
    assert experimental_teaching_enabled(frozen=frozen) is expected


@pytest.mark.parametrize('value,expected', [('1', True), ('0', False), ('', False), ('true', False)])
@pytest.mark.parametrize('frozen', [False, True])
def test_explicit_developer_override_is_independent_of_library_data(monkeypatch, frozen, value, expected):
    monkeypatch.setenv('BILICLASS_EXPERIMENTAL_TEACHING', value)
    assert experimental_teaching_enabled(frozen=frozen) is expected
