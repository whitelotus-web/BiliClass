"""Durable, sequential whole-document Word batches; single-file jobs stay separate."""

import copy
import json
import math
import os
import re
from pathlib import Path
from time import monotonic
from uuid import uuid4

from PySide6.QtCore import QUrl

from . import word_jobs as jobs
from .batch_jobs import GLOBAL_ERRORS, queue_lock
from .google_translation import _atomic

MAX_FILES = 100
STATUSES = {'waiting', 'running', 'done', 'failed'}
PHASES = {'draft', 'running', 'paused', 'finished', 'dismissed'}


def selection(urls):
    if not 2 <= len(urls) <= MAX_FILES:
        raise ValueError('Chọn từ 2 đến 100 file Word .docx cho một lượt chuyển đổi toàn bộ.')
    rows, seen = [], set()
    for value in urls:
        url = QUrl(str(value))
        if not url.isLocalFile():
            raise ValueError('Chọn các file Word trên máy tính.')
        path = Path(url.toLocalFile()).resolve()
        if path.suffix.lower() != '.docx' or not path.is_file():
            raise ValueError('Chọn file Word .docx có trên máy: ' + path.name)
        key = os.path.normcase(str(path))
        if key in seen:
            continue
        seen.add(key)
        rows.append(dict(id=uuid4().hex, url=QUrl.fromLocalFile(str(path)).toString(), name=path.name,
                         status='waiting', percent=0, message='Chờ chuyển đổi toàn bộ', elapsed_seconds=0))
    if len(rows) < 2:
        raise ValueError('Danh sách chỉ có một file khác nhau. Chọn file đó ở chế độ một bài.')
    return dict(id=uuid4().hex, kind='word', phase='draft', revision=0, rows=rows, options={},
                elapsed_seconds=0, message='')


def journal(directory, identity):
    if not isinstance(identity, str) or not re.fullmatch('[a-f0-9]{32}', identity):
        raise ValueError('Mã hàng đợi Word chưa hợp lệ.')
    folder = jobs.root(directory) / 'batches'
    if folder.is_symlink() or folder.is_junction():
        raise ValueError('Hàng đợi Word phải được lưu trực tiếp trong kho dữ liệu.')
    folder.mkdir(exist_ok=True)
    path = folder / (identity + '.json')
    if path.is_symlink():
        raise ValueError('Bản ghi hàng đợi Word không hợp lệ.')
    return path


def load(directory, identity):
    path = journal(directory, identity)
    if path.stat().st_size > 2_000_000:
        raise ValueError('Bản ghi hàng đợi Word quá lớn.')
    data = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(data, dict) or data.get('id') != identity or data.get('kind') != 'word'
            or data.get('phase') not in PHASES or type(data.get('revision')) is not int
            or data['revision'] < 0 or not isinstance(data.get('options'), dict)
            or not isinstance(data.get('rows'), list) or not 1 <= len(data['rows']) <= MAX_FILES):
        raise ValueError('Bản ghi hàng đợi Word chưa hợp lệ.')
    seen = set()
    def valid_seconds(value):
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 10**10
    if not valid_seconds(data.get('elapsed_seconds', 0)):
        raise ValueError('Thời gian hàng đợi Word không hợp lệ.')
    for row in data['rows']:
        if (not isinstance(row, dict) or not isinstance(row.get('id'), str)
                or not re.fullmatch('[a-f0-9]{32}', row['id']) or row['id'] in seen
                or row.get('status') not in STATUSES or not isinstance(row.get('name'), str)
                or not isinstance(row.get('url'), str) or not QUrl(row['url']).isLocalFile()
                or not valid_seconds(row.get('elapsed_seconds', 0))
                or row.get('word_id') and not re.fullmatch('[a-f0-9]{32}', str(row['word_id']))):
            raise ValueError('Một file trong hàng đợi Word không còn hợp lệ.')
        seen.add(row['id'])
    return data


def persist(directory, data):
    revision = data['revision'] + 1
    _atomic(journal(directory, data['id']), json.dumps({**data, 'revision': revision}, ensure_ascii=False).encode('utf-8'))
    data['revision'] = revision


def check_revision(directory, data):
    if data.get('revision') and load(directory, data['id'])['revision'] != data['revision']:
        raise ValueError('Hàng đợi Word đã đổi ở cửa sổ khác. Mở lại tool để lấy trạng thái mới.')


def discard(directory, data):
    if data:
        with queue_lock(directory):
            check_revision(directory, data)
            data = copy.deepcopy(data)
            data['phase'] = 'dismissed'
            persist(directory, data)


def run(directory, original, cancel, progress, *, retry=False):
    data = copy.deepcopy(original)
    with queue_lock(directory):
        check_revision(directory, data)
        if data['phase'] == 'dismissed':
            raise ValueError('Danh sách Word đã được bỏ; chọn các file để bắt đầu lượt mới.')
        settings = data['options']
        formatting = jobs.options_for(settings['formatting'])
        if retry:
            for row in data['rows']:
                if row['status'] == 'failed':
                    row.update(status='waiting', percent=0, message='Chờ thử lại')
        data.update(phase='running', message='')
        for row in data['rows']:
            if row['status'] == 'running':
                row['status'] = 'waiting'
        persist(directory, data)

        def notify():
            progress(copy.deepcopy(data))

        notify()
        for row in data['rows']:
            if row['status'] != 'waiting':
                continue
            if cancel.is_set():
                data.update(phase='paused', message='Đã dừng. Các bài hoàn tất được giữ; có thể tiếp tục.')
                break
            started = monotonic()
            data.update(current_row_id=row['id'], clock_monotonic=started)
            row.update(status='running', percent=0, message='Đang đọc Word và chọn toàn bộ phần chữ…')
            persist(directory, data)
            notify()

            def update(value):
                row.update({key: value[key] for key in ('percent', 'message') if key in value})
                notify()

            try:
                if row.get('word_id'):
                    job = jobs.read(directory, row['word_id'])
                    if (job.get('word_batch_id') != data['id']
                            or Path(job['source_original']).resolve() != Path(QUrl(row['url']).toLocalFile()).resolve()):
                        raise ValueError('Bài Word không còn khớp file trong hàng đợi; chọn lại file.')
                    if not job.get('whole_document') and job['regions']:
                        raise ValueError('Bài trong hàng đợi không còn ở chế độ Dịch toàn bộ; chọn lại file.')
                else:
                    # Equal bytes in different folders still need independent
                    # origins/outputs, and must not change an existing manual job.
                    job = jobs.create(directory, QUrl(row['url']).toLocalFile(), reuse=False,
                        preferences=dict(options=formatting, subject=settings['subject'], grade=settings['grade']))
                    job['word_batch_id'] = data['id']
                    with jobs.locked(jobs.folder_for(directory, job['id'])):
                        jobs.write(jobs.folder_for(directory, job['id']), job)
                    row['word_id'] = job['id']
                    persist(directory, data)
                if not job.get('whole_document'):
                    job = jobs.selections(directory, job['id'], [], whole_document=True)
                if not job['regions']:
                    raise ValueError('File chưa có phần chữ có thể chuyển đổi; hình/công thức được giữ nguyên.')
                if 'translation_config' not in job:
                    job['translation_config'] = {**settings['route'], 'subject': settings['subject'],
                        'grade': settings['grade'], 'title': job['title'], 'source_sha256': job['source_sha256']}
                    with jobs.locked(jobs.folder_for(directory, job['id'])):
                        jobs.write(jobs.folder_for(directory, job['id']), job)
                job = jobs.convert(directory, job['id'], formatting, settings['subject'], settings['grade'], cancel, update)
                if cancel.is_set() and job['phase'] != 'completed':
                    row.update(status='waiting', message='Đã dừng; phần đã làm được giữ để tiếp tục.')
                    data.update(phase='paused', message=row['message'])
                elif job['phase'] == 'completed':
                    row.update(status='done', percent=100, message=job['message'], output=job.get('export_path', ''))
                    row.pop('error_code', None)
                else:
                    row.update(status='failed', message=job['message'], error_code=job.get('error_code', 'word_conversion'))
                    if row['error_code'] in GLOBAL_ERRORS:
                        data.update(phase='paused', message='Dịch vụ hoặc ổ lưu trữ cần kiểm tra. ' + row['message'])
            except InterruptedError:
                row.update(status='waiting', message='Đã dừng; có thể tiếp tục.')
                data.update(phase='paused', message=row['message'])
            except Exception as exc:
                row.update(status='failed', message=str(exc), error_code=getattr(exc, 'code', 'word_file'))
                if row['error_code'] in GLOBAL_ERRORS:
                    data.update(phase='paused', message=row['message'])
            finally:
                elapsed = max(0, monotonic() - started)
                row['elapsed_seconds'] = row.get('elapsed_seconds', 0) + elapsed
                data['elapsed_seconds'] = data.get('elapsed_seconds', 0) + elapsed
                data.pop('clock_monotonic', None)
                persist(directory, data)
                notify()
            if data['phase'] == 'paused':
                break
        else:
            data.update(phase='finished', message='Đã kết thúc lượt chuyển đổi. Các bài đã tạo được giữ trong thư viện.')
        persist(directory, data)
        notify()
        return data
