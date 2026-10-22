"""Bound native Office work in a child process; checkpoint completed slides."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

from .library_location import write_record


class OfficeTaskError(RuntimeError):
    code = 'office'


def register_office(office):
    """Register only a fresh Office PID; an existing teacher presentation is excluded."""
    folder = os.environ.get('BILICLASS_OFFICE_TASK')
    if not folder:
        return
    try:
        import psutil
        import win32process

        pid = win32process.GetWindowThreadProcessId(int(office.HWND))[1]
        process = psutil.Process(pid)
        request = json.loads((Path(folder) / 'request.json').read_text(encoding='utf-8'))
        if pid not in request['existing_office'] and process.create_time() >= request['created_at'] - 1:
            write_record(Path(folder) / 'owned-office.json',
                         dict(pid=pid, created=process.create_time(), executable=process.exe()))
    except Exception:
        pass  # Uncertain ownership always means leave Office running.


def _stop_child(process, folder):
    forced = process.poll() is None
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    if not forced:
        return
    try:
        import psutil

        record = json.loads((folder / 'owned-office.json').read_text(encoding='utf-8'))
        office = psutil.Process(record['pid'])
        if (office.name().casefold() == 'powerpnt.exe' and office.create_time() == record['created']
                and office.exe() == record['executable']):
            office.terminate()
    except (OSError, ValueError, KeyError, psutil.Error):
        pass


def run_task(operation, directory, payload, cancel=None, progress=None, *, idle_timeout=90, timeout=900):
    import psutil

    if cancel and cancel.is_set():
        raise InterruptedError('Đã dừng tác vụ PowerPoint.')
    folder = Path(directory).resolve() / 'temp/native-jobs' / uuid4().hex
    folder.mkdir(parents=True)
    request = dict(operation=operation, payload=payload, created_at=time.time(),
                   existing_office=[p.pid for p in psutil.process_iter(['name'])
                                    if (p.info['name'] or '').casefold() == 'powerpnt.exe'])
    write_record(folder / 'request.json', request)
    command = [sys.executable] + ([] if getattr(sys, 'frozen', False) else ['-m', 'app'])
    command += ['--office-task', str(folder)]
    environment = dict(os.environ, BILICLASS_OFFICE_TASK=str(folder))
    started = updated = time.monotonic()
    signature = None
    with (folder / 'worker.log').open('wb') as log:
        child = subprocess.Popen(command, env=environment, stdout=log, stderr=log,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        try:
            while child.poll() is None:
                if cancel and cancel.is_set():
                    raise InterruptedError('Đã dừng PowerPoint; phần đã kiểm tra được giữ để tiếp tục.')
                heartbeat = folder / 'progress.json'
                try:
                    modified = heartbeat.stat().st_mtime_ns
                    if modified != signature:
                        value = json.loads(heartbeat.read_text(encoding='utf-8'))
                        signature, updated = modified, time.monotonic()
                        if progress:
                            from .conversion_progress import emit_progress

                            emit_progress(progress, 'quality', value['message'])
                except (OSError, ValueError, KeyError):
                    pass
                if time.monotonic() - updated > idle_timeout or time.monotonic() - started > timeout:
                    raise OfficeTaskError('PowerPoint không phản hồi trong thời hạn. Có thể thử lại phần chưa kiểm tra.')
                time.sleep(.1)
            result_path = folder / 'result.json'
            if not result_path.exists():
                raise OfficeTaskError('Tiến trình PowerPoint đã ngắt; phần kiểm tra hoàn tất vẫn được giữ.')
            result = json.loads(result_path.read_text(encoding='utf-8'))
            if result.get('error'):
                raise OfficeTaskError(result['error'])
            return result['value']
        except OfficeTaskError as exc:
            exc.folder = folder
            raise
        finally:
            _stop_child(child, folder)


def render_quality(path, directory, report, cancel=None, progress=None, *, reuse_directory=None):
    from .slide_quality import update_status

    payload = dict(path=str(Path(path).resolve()), directory=str(Path(directory).resolve()), report=report,
                   reuse_directory=str(Path(reuse_directory).resolve()) if reuse_directory else None)
    try:
        result = run_task('render', directory, payload, cancel, progress)
        report.clear()
        report.update(result)
    except OfficeTaskError as exc:
        # Per-slide render caches already contain completed measurements. A later
        # retry reuses those pages. No unchecked page becomes a verified pass.
        try:
            partial = json.loads((exc.folder / 'partial.json').read_text(encoding='utf-8'))
            if partial['sha256'] == report['sha256'] and len(partial['slides']) == len(report['slides']):
                report.clear()
                report.update(partial)
        except (OSError, ValueError, KeyError, AttributeError):
            pass
        report['native_error'] = str(exc)
        for row in report['slides']:
            if row.get('rendered'):
                continue
            row.update(rendered=False, render_image='')
            row['issues'] = [i for i in row['issues'] if i['code'] != 'visual_review']
            if not any(i['code'] == 'render_unavailable' for i in row['issues']):
                row['issues'].append(dict(code='render_unavailable', severity='CHECK'))
        update_status(report)
    return report


def native_progress(message):
    folder = os.environ.get('BILICLASS_OFFICE_TASK')
    if folder:
        write_record(Path(folder) / 'progress.json', dict(message=message))


def measure_overflows(path, pages, cancel=None):
    return run_task('measure', Path(path).parent, dict(path=str(Path(path).resolve()), pages=pages), cancel)


def fit_text(path, target, targets, cancel=None):
    return run_task('fit', Path(target).parent,
                    dict(path=str(Path(path).resolve()), target=str(Path(target).resolve()),
                         targets={str(k): list(v) for k, v in targets.items()}), cancel)


def worker_main(directory):
    folder = Path(directory).resolve(strict=True)
    request = json.loads((folder / 'request.json').read_text(encoding='utf-8'))
    payload = request['payload']
    def progress(message):
        write_record(folder / 'progress.json', dict(message=message))
        if request['operation'] == 'render':
            write_record(folder / 'partial.json', payload['report'])
    try:
        progress('Đang mở PowerPoint trong tiến trình kiểm tra…')
        if request['operation'] == 'render':
            from .slide_quality import render_quality as native_render

            value = native_render(payload['path'], payload['directory'], payload['report'],
                                  progress=progress, reuse_directory=payload.get('reuse_directory'))
        elif request['operation'] == 'measure':
            from .native_layout import _office_overflows

            value = _office_overflows(Path(payload['path']), payload['pages'], None)
        elif request['operation'] == 'fit':
            from .slide_repair import _office_fit

            _office_fit(Path(payload['path']), Path(payload['target']),
                        {int(k): {tuple(item) if isinstance(item, list) else item for item in v}
                         for k, v in payload['targets'].items()}, None)
            value = str(payload['target'])
        elif request['operation'] == 'preview':
            from .powerpoint_review import _render_preview_pages

            image_folder, index = _render_preview_pages(payload['path'], payload['pages'],
                                                       payload['directory'], payload['sha256'])
            value = [str(image_folder), index]
        else:
            raise ValueError('Tác vụ Office không được hỗ trợ.')
        write_record(folder / 'result.json', dict(value=value))
        return 0
    except Exception as exc:
        write_record(folder / 'result.json', dict(error=f'PowerPoint: {type(exc).__name__}: {exc}'))
        return 1
