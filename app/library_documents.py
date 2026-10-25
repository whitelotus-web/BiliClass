"""A shared catalog view; Word packages stay independent of PowerPoint records."""

import copy
import re
import shutil
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path

from . import word_jobs


def word_id(identity):
    if isinstance(identity, str) and re.fullmatch(r'word:[a-f0-9]{32}', identity):
        return identity[5:]
    if isinstance(identity, str) and identity.startswith('word:'):
        raise ValueError('Mã tài liệu Word chưa hợp lệ.')
    return ''


def word_rows(directory, *, trash=False):
    if not (Path(directory) / 'word_documents').exists():
        return []
    result = []
    for row in word_jobs.catalog(directory, trash):
        finished = row['phase'] == 'completed' and bool(row.get('output_sha256'))
        grade = str(row.get('grade', ''))
        number = int(grade) if grade.isdigit() else 0
        education = 'Tiểu học' if 1 <= number <= 5 else 'THCS' if 6 <= number <= 9 else 'THPT' if 10 <= number <= 12 else 'Khác'
        result.append({**row, 'id': 'word:' + row['id'], 'word_id': row['id'], 'document_type': 'word',
            'education_level': education, 'grade': grade, 'revision': 0, 'slides_count': 0, 'segments_count': row['selected_count'],
            'created_at': row.get('created_at') or row['updated_at'], 'created_at_estimated': not bool(row.get('created_at')),
            'status': 'READY_TO_TEACH' if finished else 'REVIEW_REQUIRED' if row['phase'] == 'review' else 'DRAFT',
            'quality_failures': 0, 'narration': {'status': 'not_applicable', 'ready': False},
            'word_label': 'Đã lưu song ngữ' if finished else 'Chờ xem và lưu' if row['phase'] == 'review' else 'Đang chuẩn bị · Có thể tiếp tục'})
    return result


def change(directory, operation, identities, legacy_change, *, with_receipt=False, expected_deleted=None):
    """Preflight Word entries and roll them back if the PowerPoint transaction fails."""
    identities = list(dict.fromkeys(identities))
    words = [(identity, word_id(identity)) for identity in identities if word_id(identity)]
    if not words:
        return legacy_change(directory, operation, identities, with_receipt=with_receipt, expected_deleted=expected_deleted)
    if operation not in {'trash', 'restore', 'purge'}:
        raise ValueError('Thao tác thư viện chưa hợp lệ.')
    slides = [identity for identity in identities if not word_id(identity)]
    if expected_deleted is not None and set(expected_deleted) != set(identities):
        raise ValueError('Lần xóa này đã thay đổi; chọn lại bài trong thùng rác.')
    originals, receipt = [], {}
    folders = []
    with ExitStack() as locks:
        for identity, native in sorted(words):
            folder = word_jobs.folder_for(directory, native)
            locks.enter_context(word_jobs.locked(folder))
            job = word_jobs.read(directory, native)
            if job.get('purged_at') or (operation != 'trash' and not job.get('deleted_at')):
                raise ValueError('Danh sách Word đã thay đổi; chỉ chọn bài còn trong thùng rác.')
            if expected_deleted is not None and expected_deleted[identity] != job.get('deleted_at'):
                raise ValueError('Lần xóa Word đã thay đổi; chọn lại bài trong thùng rác.')
            originals.append((folder, copy.deepcopy(job)))
            folders.append(folder)
        try:
            stamp = datetime.now(timezone.utc).isoformat()
            for identity, (_, original) in zip(sorted(identity for identity, _ in words), originals, strict=True):
                job = copy.deepcopy(original)
                job['deleted_at'] = stamp if operation == 'trash' else '' if operation == 'restore' else original['deleted_at']
                if operation == 'purge':
                    job['purged_at'] = stamp
                word_jobs.write(word_jobs.folder_for(directory, job['id']), job)
                receipt[identity] = stamp
            if slides:
                expected = {identity: expected_deleted[identity] for identity in slides} if expected_deleted is not None else None
                result = legacy_change(directory, operation, slides, with_receipt=with_receipt, expected_deleted=expected)
                if with_receipt:
                    receipt.update(result)
        except Exception:
            for folder, original in originals:
                word_jobs.write(folder, original)
            raise
    if operation == 'purge':
        for folder in folders:
            # The folder was resolved/validated by folder_for; external exports are never removed.
            if folder.parent != word_jobs.root(directory) or folder.is_symlink() or folder.is_junction():
                raise ValueError('Không dọn thư mục ngoài kho Word.')
            shutil.rmtree(folder)
    return receipt if with_receipt else len(identities)
