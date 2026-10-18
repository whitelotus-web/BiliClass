import json

from app.library import Library
from app.storage import record_backup
from app.support_report import create_report, error_category


def test_support_report_uses_counts_and_categories_without_exporting_private_values(tmp_path):
    root = tmp_path / 'SecretTeacherName'
    library = Library(root)
    library.create('Private lesson title', 'Secret subject', 'THPT', '10', [('One', 'Private text')])
    library.set_setting('teacher', 'SecretTeacherName')
    library.set_setting('api_key', 'secret-api-key')
    library.close()
    (root / 'logs').mkdir()
    (root / 'logs/app.log').write_text('2026-10-18 12:00:00 ERROR Private text secret-token\n')
    record_backup(root, error='disk full at SecretTeacherName/Private text secret-api-key')
    output = create_report(root, tmp_path / 'report.json')
    text = output.read_text(encoding='utf-8')
    for secret in ('SecretTeacherName', 'Private text', 'Private lesson title', 'secret-api-key', 'secret-token'):
        assert secret not in text
    report = json.loads(text)
    assert report['databases']['library.db']['integrity']
    assert report['databases']['library.db']['counts']['lessons'] == 1
    assert report['backup']['last_error_category'] == 'storage'
    assert report['log_levels'] == {'ERROR': 1}
    assert error_category('PowerPoint RPC disconnected') == 'office'
