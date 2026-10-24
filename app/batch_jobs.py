"""One lesson at a time, with durable checkpoints and the existing conversion/voice engines."""

import copy
import hashlib
import json
import logging
import math
import os
import re
import traceback
from contextlib import closing, contextmanager
from pathlib import Path
from time import monotonic
from uuid import uuid4

from PySide6.QtCore import Qt, QUrl

from .library import Library

MAX_FILES = 100
GLOBAL_ERRORS = {'storage', 'api_settings', 'api_budget', 'api_key', 'api_rate', 'api_quota', 'api_network'}


def _log_failure(context, error):
    # The root console can be hidden in the desktop app. Keep a useful local
    # stack without copying exception text that may contain lesson content/key.
    logging.getLogger('biliclass').error('%s: %s\n%s', context, type(error).__name__,
                                       ''.join(traceback.format_tb(error.__traceback__)))


def selection(kind, urls):
    if kind not in {'convert', 'voice'} or not 1 <= len(urls) <= MAX_FILES:
        raise ValueError('Chọn từ 1 đến 100 file PowerPoint cho một lượt xử lý.')
    rows, seen = [], set()
    for value in urls:
        url = QUrl(str(value))
        if not url.isLocalFile():
            raise ValueError('Chọn file PowerPoint trên máy tính.')
        key = os.path.normcase(os.path.abspath(url.toLocalFile()))
        if key in seen:
            continue
        seen.add(key)
        rows.append({'id': uuid4().hex, 'url': url.toString(), 'name': Path(url.toLocalFile()).name,
                     'status': 'waiting', 'percent': 0, 'message': 'Chờ xử lý'})
    return {'id': uuid4().hex, 'kind': kind, 'phase': 'draft', 'rows': rows, 'revision': 0, 'options': {}}


def journal(directory, identity):
    if not isinstance(identity, str) or not re.fullmatch('[a-f0-9]{32}', identity):
        raise ValueError('Danh sách xử lý chưa hợp lệ.')
    return Path(directory)/'batch_jobs'/identity/'queue.json'


def library_selection(directory, identities):
    """Queue existing lesson identities without importing duplicate PPTX files."""
    from .lesson_narration import library_audio_status
    from .powerpoint import verified_presentation

    if not 1 <= len(identities) <= MAX_FILES or any(not isinstance(value, str) for value in identities):
        raise ValueError(f'Chọn từ 1 đến {MAX_FILES} bài trong thư viện.')
    rows, skipped = [], 0
    with closing(Library(directory)) as library:
        for identity in dict.fromkeys(identities):
            lesson = library.get(identity)
            if lesson.get('deleted_at'):
                raise ValueError('Danh sách có bài đã xóa. Chọn lại bài trong thư viện.')
            if library_audio_status(lesson, directory)['ready']:
                skipped += 1
                continue
            path = verified_presentation(lesson, directory)
            rows.append({'id': uuid4().hex, 'url': QUrl.fromLocalFile(str(path)).toString(),
                         'name': lesson['title'], 'lesson_id': identity, 'lesson_revision': lesson['revision'],
                         'library_lesson': True, 'status': 'waiting', 'percent': 0, 'message': 'Chờ xử lý'})
    if not rows:
        raise ValueError('Các bài đã chọn đều có giọng đọc hoàn tất. Chọn bài chưa có giọng để tạo hàng loạt.')
    return {'id': uuid4().hex, 'kind': 'voice', 'phase': 'draft', 'rows': rows,
            'revision': 0, 'options': {}, 'skipped_ready': skipped}


def load(directory, identity):
    path = journal(directory, identity)
    if path.stat().st_size > 2_000_000:
        raise ValueError('Danh sách xử lý vượt giới hạn.')
    state = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(state, dict) or state.get('id') != identity or state.get('kind') not in {'convert', 'voice'}
            or not isinstance(state.get('rows'), list) or not 1 <= len(state['rows']) <= MAX_FILES
            or type(state.get('revision')) is not int or state['revision'] < 0
            or state.get('phase') not in {'draft', 'running', 'paused', 'finished', 'dismissed'}
            or not isinstance(state.get('options'), dict)):
        raise ValueError('Chưa đọc được danh sách xử lý đã lưu.')
    identities = set()
    def valid_elapsed(value):
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 10**10
    if not valid_elapsed(state.get('elapsed_seconds', 0)):
        raise ValueError('Thời gian trong danh sách xử lý chưa hợp lệ.')
    for row in state['rows']:
        if (not isinstance(row, dict) or not isinstance(row.get('id'), str)
                or not re.fullmatch('[a-f0-9]{32}', row['id']) or row['id'] in identities
                or row.get('status') not in {'waiting', 'running', 'done', 'failed'}
                or not isinstance(row.get('name'), str) or not isinstance(row.get('url'), str)
                or not QUrl(row['url']).isLocalFile() or not valid_elapsed(row.get('elapsed_seconds', 0))):
            raise ValueError('Một mục trong hàng đợi đã lưu không còn hợp lệ.')
        identities.add(row['id'])
    return state


@contextmanager
def queue_lock(directory):
    folder = Path(directory)/'batch_jobs'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder/'active.lock').open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ValueError('Một cửa sổ BiliClass khác đang xử lý hàng đợi. Chờ lượt đó hoàn tất.') from None
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def persist(directory, state):
    path = journal(directory, state['id'])
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix('.'+uuid4().hex+'.pending')
    revision = state['revision'] + 1
    try:
        pending.write_text(json.dumps({**state, 'revision': revision}, ensure_ascii=False), encoding='utf-8')
        pending.replace(path)
        state['revision'] = revision
    finally:
        pending.unlink(missing_ok=True)


def dismiss(directory, state):
    with queue_lock(directory):
        if state.get('revision'):
            current = load(directory, state['id'])
            if current['revision'] != state['revision']:
                raise ValueError('Danh sách đã đổi ở cửa sổ khác. Mở lại ứng dụng để xem trạng thái mới.')
            current['phase'] = 'dismissed'
            persist(directory, current)


def verify_input_version(row, expected):
    """A missing original may resume from its managed copy; an edited original must be reselected."""
    from .document_limits import check_document_size

    path = Path(QUrl(row['url']).toLocalFile())
    try:
        if not path.is_file():
            return
        check_document_size(path)
        with path.open('rb') as stream:
            current = hashlib.file_digest(stream, 'sha256').hexdigest()
    except OSError:
        return
    if current != expected:
        raise ValueError('File đầu vào đã sửa từ lúc xử lý. Chọn lại file để dùng bản mới; phần đã làm vẫn được giữ.')


def bind_origin(directory, row, lesson):
    """A resumed row retains its own origin even if identical bytes were imported elsewhere."""
    path = Path(QUrl(row['url']).toLocalFile()).resolve()
    with closing(Library(directory)) as library:
        if not path.is_relative_to(library.directory.resolve()):
            from .export_origin import is_automatic_product

            if is_automatic_product(library, lesson, path):
                return
            library.set_setting('export_origin_lesson:' + lesson['id'],
                                {'folder': str(path.parent), 'name': path.name})


def convert_one(directory, row, options, cancel, update):
    from .chatgpt_handoff import validate_config
    from .completed_export import save_converted
    from .conversion_input import creation_config, local_document
    from .conversion_progress import ConversionProgress
    from .google_conversion import convert, prepare
    from .google_conversion import load as load_conversion

    if row.get('folder'):
        job = load_conversion(directory, row['folder'])
        verify_input_version(row, job['config']['source_sha256'])
        if row.get('lesson_id'):
            with closing(Library(directory)) as library:
                if library.get(row['lesson_id'])['revision'] != row['lesson_revision']:
                    raise ValueError('Bài giảng đã sửa. Chọn lại file để tạo lượt xử lý mới.')
    else:
        from .translation_provider import require_credentials

        # Legacy queues have no engine field and must keep their RC167 Google route.
        provider = options.get('translation_provider', 'google')
        require_credentials(directory, provider)
        path = local_document(row['url'])
        if path.suffix.lower() != '.pptx':
            raise ValueError('Hàng đợi nhận file PowerPoint .pptx, tối đa 200 MB mỗi file.')
        config = validate_config(creation_config(path.stem[:180], options['subject'], options['education'],
            options['grade'], options['format'], options['preset'], options['style'], options.get('notes', '')))
        config['template_bookends'] = options.get('bookends', False)
        config['translation_provider'] = provider
        config['translation_budget'] = options.get('translation_budget',
            options.get('budget', 500_000) if provider == 'google' else 2_000_000)
        job = prepare(directory, config, path)
        update({'folder': job['folder']}, True)
    progress = ConversionProgress(job['folder'], lambda value: update({
        'percent': value.get('percent', 0), 'message': value.get('message', 'Đang chuyển đổi…')}))
    try:
        lesson, preview = convert(directory, job, cancel, progress, budget=options.get('budget', 500_000))
    finally:
        progress.finish()
    update({'lesson_id': lesson['id'], 'lesson_revision': lesson['revision']}, True)
    if cancel.is_set():
        raise InterruptedError()
    update({'message': 'Đang lưu PowerPoint cạnh file gốc…', 'percent': 99})
    bind_origin(directory, row, lesson)
    exported = save_converted(directory, lesson, preview)
    return {'lesson_id': lesson['id'], 'output': exported['path'], 'fallback': exported['fallback']}


def narrate_one(directory, row, options, cancel, update):
    from .completed_export import save_finished
    from .conversion_input import local_document
    from .lesson_narration import make_plan, variant_id
    from .narration_preferences import store_lesson_position
    from .narration_preparation import NarrationJob, NarrationPreparation, prepare_request
    from .storage_space import require_space
    from .voice_import import import_presentation, prepare_library_lesson

    require_space(directory)
    if row.get('lesson_id'):
        if row.get('library_lesson'):
            with closing(Library(directory)) as library:
                if library.get(row['lesson_id'])['revision'] != row['lesson_revision']:
                    raise ValueError('Bài giảng đã sửa từ lúc vào hàng đợi. Chọn lại bài trong thư viện.')
        lesson, preview = prepare_library_lesson(directory, row['lesson_id'], cancel=cancel)
        verify_input_version(row, lesson['source']['sha256'])
        if row.get('library_lesson'):
            update({'lesson_revision': lesson['revision']}, True)
        if row.get('lesson_revision') != lesson['revision']:
            raise ValueError('Bài giảng đã sửa từ lúc vào hàng đợi. Chọn lại file để dùng nội dung mới.')
    else:
        path = local_document(row['url'])
        if path.suffix.lower() != '.pptx':
            raise ValueError('Chọn file PowerPoint .pptx để tạo giọng đọc.')
        lesson, preview = import_presentation(directory, path)
        update({'lesson_id': lesson['id'], 'lesson_revision': lesson['revision']}, True)
    if cancel.is_set():
        raise InterruptedError()
    store_lesson_position(directory, lesson['id'], options['position'])
    prepared = prepare_request(Path(directory), lesson['id'], lesson['revision'], options['mode'],
                               options['voice'], options['rate'], False, cancel)
    with closing(Library(directory)) as library:
        if prepared.get('already_created'):
            plan, _ = make_plan(lesson, options['mode'], options)
            lesson = library.select_narration_variant(lesson['id'], variant_id(plan))
        else:
            worker = NarrationJob(prepared['inspection'], prepared['selected'], Path(directory)/'audio', None)
            worker.cancel = cancel
            worker.progressed.connect(lambda value: update({
                'percent': int(95*value.get('complete', 0)/max(1, value.get('total', 0))),
                'message': f"Đang tạo giọng · {value.get('complete', 0)}/{value.get('total', 0)} đoạn"}),
                Qt.ConnectionType.DirectConnection)
            worker.run()  # Same proven engine, on this queue's existing worker; no second lesson starts.
            record = {**prepared['plan'], **worker.result, 'running': False}
            lesson = library.update_narration(lesson['id'], record)
            if record.get('cancelled'):
                raise InterruptedError()
            if record.get('failed') or record.get('complete') != record.get('total'):
                require_space(directory)
                raise ValueError(NarrationPreparation._completion_message(record))
    update({'message': 'Đang tự lưu PowerPoint có giọng…', 'percent': 99})
    bind_origin(directory, row, lesson)
    exported = save_finished(directory, lesson, preview)
    return {'lesson_id': lesson['id'], 'output': exported['path'], 'fallback': exported['fallback']}


def run(directory, original, cancel, notify, *, process=None, retry=False):
    """Stop preserves the current checkpoint; failures never silently discard the remaining files."""
    state = copy.deepcopy(original)
    started = current = None
    elapsed = state.get('elapsed_seconds', 0)
    row_started = row_elapsed = 0

    def clock():
        if started is not None:
            now = monotonic()
            state.update(elapsed_seconds=round(elapsed+now-started, 3), clock_monotonic=now)
            if current is not None:
                current['elapsed_seconds'] = round(row_elapsed+now-row_started, 3)

    try:
        with queue_lock(directory):
            if state['revision'] and load(directory, state['id'])['revision'] != state['revision']:
                raise ValueError('Danh sách đã đổi ở cửa sổ khác. Mở lại ứng dụng để tiếp tục đúng lượt.')
            if retry:
                for row in state['rows']:
                    if row['status'] == 'failed':
                        row.update(status='waiting', percent=0, message='Chờ thử lại')
            state['phase'] = 'running'
            state.pop('message', None)
            started = monotonic()
            clock()
            persist(directory, state)
            with closing(Library(directory)) as library:
                library.set_setting('last_batch_queue', state['id'])
            notify(copy.deepcopy(state))
            action = process or (convert_one if state['kind'] == 'convert' else narrate_one)
            for row in state['rows']:
                if cancel.is_set():
                    break
                if row['status'] not in {'waiting', 'running'}:
                    continue
                row.update(status='running', message='Đang chuẩn bị…')
                current = row
                row_started, row_elapsed = monotonic(), row.get('elapsed_seconds', 0)
                state['current_row_id'] = row['id']
                last_saved = monotonic()

                def update(values, checkpoint=False):
                    nonlocal last_saved
                    row.update(values)
                    clock()
                    if checkpoint or monotonic()-last_saved >= 1:
                        persist(directory, state)
                        last_saved = monotonic()
                    notify(copy.deepcopy(state))

                update({}, True)
                try:
                    result = action(directory, row, state['options'], cancel, update)
                    row.update(result, status='done', percent=100, message=(
                        'Đã hoàn tất · Đã lưu vào thư mục BiliClass' if result.get('fallback')
                        else 'Đã hoàn tất và lưu PowerPoint cạnh file gốc'))
                except InterruptedError:
                    row.update(status='waiting', message='Đã dừng; phần đã làm được giữ để tiếp tục')
                    state['phase'] = 'paused'
                    break
                except Exception as exc:
                    from .storage_space import FULL_DISK_MESSAGE, full_disk_error

                    _log_failure('Batch lesson ' + row['id'], exc)
                    full = full_disk_error(exc)
                    code = 'storage' if full else getattr(exc, 'code', 'unexpected')
                    message = FULL_DISK_MESSAGE if full else (str(exc) if isinstance(exc, (OSError, ValueError))
                        else 'Chưa hoàn tất bài này. Bấm Thử lại bài lỗi; phần đã làm được giữ lại.')
                    row.update(status='failed', message=message, error_code=code)
                    if code in GLOBAL_ERRORS:
                        row['status'] = 'waiting'
                        state.update(phase='paused', message=message)
                        break
                clock()
                persist(directory, state)
                notify(copy.deepcopy(state))
                current = None
            # A stop arriving after the last saved result has nothing left to
            # interrupt. Keep it complete instead of a paused queue with no work.
            all_done = all(row['status'] == 'done' for row in state['rows'])
            state['phase'] = 'finished' if all_done else (
                'paused' if cancel.is_set() or state['phase'] == 'paused' else 'finished')
            clock()
            persist(directory, state)
            notify(copy.deepcopy(state))
    except Exception as exc:
        from .storage_space import FULL_DISK_MESSAGE, full_disk_error

        _log_failure('Batch checkpoint', exc)
        state.update(phase='paused', message=FULL_DISK_MESSAGE if full_disk_error(exc) else str(exc))
        clock()
        for row in state['rows']:
            if row['status'] == 'running':
                row.update(status='waiting', message='Chưa hoàn tất; phần đã làm được giữ để tiếp tục')
    return state
