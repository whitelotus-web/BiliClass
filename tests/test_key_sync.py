import base64
import copy
import json
from contextlib import closing

import pytest

from app.google_translation import KeyStore
from app.key_sync import CONFIG_PATH, REPOSITORY, download, remote, snapshot, upload

KEY = 'AIza' + 'a' * 35
OTHER = 'AIza' + 'b' * 35


class Client:
    def __init__(self, data=None, private=True):
        self.data, self.private, self.calls = data, private, []

    def request(self, method, path, payload=None, **kwargs):
        self.calls.append((method, path))
        if path == '':
            return {'private': self.private, 'full_name': REPOSITORY}
        assert path == CONFIG_PATH
        if method == 'GET':
            if self.data is None:
                return None
            raw = json.dumps(self.data).encode()
            return {'type': 'file', 'encoding': 'base64', 'size': len(raw), 'sha': 'f' * 40,
                    'content': base64.b64encode(raw).decode()}
        assert method == 'PUT'
        if self.data is not None:
            assert payload['sha'] == 'f' * 40, 'Existing file needs optimistic concurrency protection'
        self.data = json.loads(base64.b64decode(payload['content']))
        return {}


def test_private_upload_and_other_machine_import_encrypted_preserves_budget(tmp_path):
    source, target = KeyStore(tmp_path / 'one'), KeyStore(tmp_path / 'two')
    source.add('Project A | ' + KEY)
    source.reserve(345, 1000)
    client = Client()
    assert upload(source, 1000, client) == 1
    result = download(target, 500_000, client)
    assert result == {'count': 1, 'budget': 1000}
    assert target.keys() == source.keys()
    assert KEY.encode() not in target.path.read_bytes()
    assert target.public()[0]['used'] == 345
    download(target, 500_000, client)
    assert target.public()[0]['used'] == 345


@pytest.mark.parametrize('receive', [False, True])
def test_public_repo_blocked_before_any_key_read_or_write(tmp_path, receive):
    store = KeyStore(tmp_path)
    store.add(KEY)
    client = Client(private=False)
    with pytest.raises(ValueError, match='công khai'):
        (download if receive else upload)(store, 1000, client)
    assert client.calls == [('GET', '')]


def test_merge_additional_keys_without_resetting_existing_local_usage(tmp_path):
    source, target = KeyStore(tmp_path / 'one'), KeyStore(tmp_path / 'two')
    source.add('A | ' + KEY)
    source.reserve(30, 1000)
    client = Client(snapshot(source, 1000))
    target.add('A | ' + KEY + '\nB | ' + OTHER)
    target.reserve(70, 1000)
    assert upload(target, 2000, client) == 2
    assert client.data['budget'] == 1000
    download(source, 1000, client)
    assert len(source.keys()) == 2 and source.public()[0]['used'] == 70


def test_legacy_sync_keeps_shared_history_and_does_not_reset_existing_key_counter(tmp_path):
    target = KeyStore(tmp_path)
    target.add('A | ' + KEY)
    target.reserve(70, 500000)
    client = Client({'format': 'BiliClass Google keys v1', 'keys': [{'project': 'a', 'key': KEY}],
                     'usage': [[target.month(), 'a', 345]], 'budget': 500000})
    download(target, 500000, client)
    row = target.public()[0]
    assert row['used'] == 70 and row['legacyUsed'] == 275
    assert row['carryover'] == 275
    download(target, 500000, client)
    assert target.public()[0] == row


def test_import_rejects_malformed_per_key_accounting_without_changing_keys(tmp_path):
    store = KeyStore(tmp_path)
    store.add(KEY)
    data = snapshot(store, 500000)
    data['key_usage'] = [[store.month(), store.public()[0]['id'], 'mặc định', -1]]
    before = store.path.read_bytes()
    with pytest.raises(ValueError, match='chưa thay đổi'):
        download(store, 500000, Client(data))
    assert store.path.read_bytes() == before
    assert store.public()[0]['used'] == 0


def test_conflicting_project_and_invalid_remote_do_not_change_store(tmp_path):
    source, target = KeyStore(tmp_path / 'one'), KeyStore(tmp_path / 'two')
    source.add('A | ' + KEY)
    target.add('B | ' + KEY)
    before = target.path.read_bytes()
    client = Client(snapshot(source, 1000))
    with pytest.raises(ValueError, match='hai tên nhóm'):
        download(target, 1000, client)
    assert target.path.read_bytes() == before
    malformed = copy.deepcopy(client.data)
    malformed['usage'] = [['2026-10', 'a', -5]]
    with pytest.raises(ValueError, match='chưa thay đổi'):
        remote(Client(malformed))
    assert target.path.read_bytes() == before
    with closing(target.connect()) as db:
        assert db.execute('SELECT COUNT(*) FROM usage').fetchone()[0] == 0
