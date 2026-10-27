"""Word-only checkpoints and library, separate from PowerPoint lesson records."""

import copy
import json
import os
import re
import shutil
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .google_translation import _atomic
from .word_document import (
    Package,
    digest,
    display_translation,
    font_name,
    keyword_annotations,
    validate_translation,
)


def root(directory):
    folder = Path(directory) / 'word_documents'
    if folder.is_symlink() or folder.is_junction():
        raise ValueError('Kho Word phải là thư mục lưu trực tiếp.')
    folder.mkdir(parents=True, exist_ok=True)
    return folder.resolve()


def folder_for(directory, identity):
    if not isinstance(identity, str) or not re.fullmatch('[a-f0-9]{32}', identity):
        raise ValueError('Mã tài liệu Word chưa hợp lệ.')
    folder = root(directory) / identity
    if folder.is_symlink() or folder.is_junction() or folder.resolve().parent != root(directory):
        raise ValueError('Tài liệu không thuộc kho Word này.')
    return folder


@contextmanager
def locked(folder):
    with (Path(folder) / 'word.lock').open('a+b') as stream:
        try:
            if os.name == 'nt':
                import msvcrt

                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ValueError('Tài liệu Word đang được xử lý trong cửa sổ khác.') from None
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def write(folder, job):
    job['updated_at'] = datetime.now(timezone.utc).isoformat()
    _atomic(Path(folder) / 'job.json', json.dumps(job, ensure_ascii=False).encode('utf-8'))
    summary = {key: job.get(key, '') for key in ('id', 'title', 'phase', 'created_at', 'updated_at', 'subject', 'grade',
               'output_sha256', 'export_sha256', 'source_sha256', 'deleted_at', 'purged_at')}
    summary.update(catalog_version=2, selected_count=len(job.get('regions', [])),
                   preview_text=' '.join(row.get('vi', '') for row in job.get('regions', [])[:2])[:450])
    try:
        _atomic(Path(folder) / 'summary.json', json.dumps(summary, ensure_ascii=False).encode('utf-8'))
    except OSError:
        pass  # The full checkpoint remains authoritative if a summary write fails.


def read(directory, identity):
    folder = folder_for(directory, identity)
    path = folder / 'job.json'
    if path.stat().st_size > 24 * 1024**2:
        raise ValueError('Bản ghi Word vượt giới hạn.')
    job = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(job, dict) or job.get('id') != identity or not isinstance(job.get('regions'), list):
        raise ValueError('Bản ghi Word không hợp lệ.')
    source = folder / 'source.docx'
    if source.is_symlink() or digest(source) != job.get('source_sha256'):
        raise ValueError('Bản nguồn Word trong kho đã thay đổi; chọn lại tài liệu.')
    return job


def verify_original(job):
    original = Path(job['source_original'])
    if original.is_file() and digest(original) != job['source_sha256']:
        raise ValueError('File Word gốc đã được sửa sau khi tải. Chọn lại file để dùng nội dung mới.')


def catalog(directory, trash=False):
    result = []
    for folder in sorted(root(directory).iterdir())[:5000]:
        if not folder.is_dir() or not re.fullmatch('[a-f0-9]{32}', folder.name):
            continue
        try:
            # Catalog does not hash/open every document; opening one verifies it.
            full = folder / 'job.json'
            brief = folder / 'summary.json'
            path = brief if brief.is_file() and brief.stat().st_mtime_ns >= full.stat().st_mtime_ns else full
            if folder.is_symlink() or folder.is_junction() or path.stat().st_size > 24 * 1024**2:
                continue
            job = json.loads(path.read_text(encoding='utf-8'))
            if path == brief and isinstance(job, dict) and job.get('catalog_version') != 2:
                job = json.loads(full.read_text(encoding='utf-8'))
            if not isinstance(job, dict) or job.get('id') != folder.name or job.get('purged_at') or bool(job.get('deleted_at')) != trash:
                continue
            row = {key: job.get(key, '') for key in ('id', 'title', 'phase', 'created_at', 'updated_at', 'subject', 'grade',
                   'output_sha256', 'export_sha256', 'source_sha256', 'deleted_at')}
            row.update(selected_count=job.get('selected_count', len(job.get('regions', []))),
                       preview_text=job.get('preview_text', ' '.join(part.get('vi', '') for part in job.get('regions', [])[:2])[:450]))
            result.append(row)
        except (OSError, ValueError, TypeError):
            continue
    return sorted(result, key=lambda row: row['updated_at'], reverse=True)


def public(directory, job, *, paragraphs=True):
    result = copy.deepcopy(job)
    result['source_title'] = Path(job['source_original']).stem
    grade = str(job.get('grade', ''))
    result['education_level'] = 'Tiểu học' if grade in {'1', '2', '3', '4', '5'} else 'THCS' if grade in {'6', '7', '8', '9'} else 'THPT'
    result['regions'] = [{**region, 'display_en': display_translation(region)} for region in result['regions']]
    if paragraphs:
        result['paragraphs'] = Package(folder_for(directory, job['id']) / 'source.docx').rows
    result['selected_count'] = len(result['regions'])
    result['can_export'] = bool(result['regions']) and all(region.get('en', '').strip() for region in result['regions'])
    result['has_previous'] = (folder_for(directory, job['id']) / 'previous.docx').is_file()
    result.pop('translation_config', None)
    return result


def create(directory, source, *, preferences=None):
    from .storage_space import MIB, require_space

    source = Path(source).resolve()
    package = Package(source)
    if not package.rows:
        raise ValueError('Tệp chưa có văn bản chỉnh sửa được. Chữ trong ảnh không phải vùng chọn Word.')
    signature = digest(source)
    for row in catalog(directory):
        if signature in {row.get('source_sha256'), row.get('output_sha256'), row.get('export_sha256')}:
            return read(directory, row['id'])
    preferences = preferences or {}
    options = options_for({**formatting_defaults(directory), **preferences.get('options', {})})
    subject = str(preferences.get('subject', 'Toán')).strip()[:120] or 'Toán'
    grade = str(preferences.get('grade', '11')).strip()[:80]
    require_space(directory, source.stat().st_size * 3 + 32 * MIB)
    identity = uuid4().hex
    folder = folder_for(directory, identity)
    folder.mkdir()
    shutil.copyfile(source, folder / 'source.docx')
    if digest(folder / 'source.docx') != signature:
        raise ValueError('Nguồn Word thay đổi trong lúc tải; chọn lại tệp.')
    job = dict(id=identity, title=title_for(preferences.get('title', ''), source.stem), source_original=str(source), source_sha256=signature,
               created_at=datetime.now(timezone.utc).isoformat(),
               regions=[], options=options,
               phase='select', message='Bôi đen và thêm vùng, hoặc tích chọn câu/đoạn cần dịch.', subject=subject, grade=grade)
    write(folder, job)
    return job


def selections(directory, identity, rows, *, whole_document=None):
    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        package = Package(folder / 'source.docx')
        if whole_document is None and job.get('whole_document'):
            raise ValueError('Bỏ tích Dịch toàn bộ trước khi chọn riêng nội dung.')
        if whole_document is True:
            if not job.get('whole_document'):
                job['manual_selection'] = [{key: row[key] for key in ('paragraph', 'start', 'end')} for row in job['regions']]
            rows = [dict(paragraph=row['id'], start=0, end=len(row['text'])) for row in package.rows if row['editable']]
        elif whole_document is False:
            rows = job.pop('manual_selection', rows)
        if whole_document is not None:
            job['whole_document'] = whole_document
        selected = package.selection(rows)
        old = {row['id']: row for row in job['regions']}
        job['regions'] = [{**row, **{key: value for key, value in old.get(row['id'], {}).items()
                                  if key in {'en', 'annotations'}}} for row in selected]
        job.update(phase='select', message='Đã chọn ' + str(len(selected)) + ' vùng cần chuyển đổi.')
        write(folder, job)
        return job


def title_for(value, fallback):
    return ' '.join(str(value).split())[:200] or fallback


def options_for(value):
    from .word_document import HIGHLIGHTS, MODES, font_size, valid_color

    result = dict(mode=value.get('mode', 'below'), color=value.get('color', 'original'), highlight=value.get('highlight', 'none'),
                  italic=value.get('italic', True), bold=value.get('bold', False),
                  underline=value.get('underline', False), strike=value.get('strike', False), script=value.get('script', 'normal'),
                  font_size=font_size(value.get('font_size', 0)),
                  font=font_name(value.get('font', '')), density=value.get('density', 'normal'))
    if (result['mode'] not in MODES or not valid_color(result['color'])
            or not isinstance(result['highlight'], str) or result['highlight'] != 'none' and result['highlight'] not in HIGHLIGHTS
            or any(type(result[key]) is not bool for key in ('italic', 'bold', 'underline', 'strike'))
            or result['script'] not in {'normal', 'subscript', 'superscript'} or result['density'] not in {'few', 'normal', 'deep'}):
        raise ValueError('Cấu hình trình bày Word chưa hợp lệ.')
    return result


def formatting_defaults(directory, value=None):
    path = root(directory) / 'formatting.json'
    saving = value is not None
    if value is None:
        try:
            if path.stat().st_size > 8192:
                raise ValueError('Cấu hình quá lớn.')
            value = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                raise ValueError('Cấu hình chưa hợp lệ.')
            result = options_for(value)
        except (OSError, ValueError, TypeError):
            result = options_for({})
    else:
        result = options_for(value)
    result = {key: result[key] for key in ('color', 'highlight', 'italic', 'bold', 'underline', 'strike', 'script', 'font', 'font_size')}
    if saving:
        _atomic(path, json.dumps(result, ensure_ascii=False).encode('utf-8'))
    return result


def reading_theme(directory, value=None):
    """Local reading preference; deliberately separate from export formatting."""
    path = root(directory) / 'reading.json'
    if value is None:
        try:
            if path.stat().st_size > 1024:
                return 'light'
            value = json.loads(path.read_text(encoding='utf-8'))['theme']
        except (OSError, ValueError, TypeError, KeyError):
            return 'light'
        return value if value in ('light', 'dark') else 'light'
    if value not in ('light', 'dark'):
        raise ValueError('Chọn nền văn bản sáng hoặc tối.')
    _atomic(path, json.dumps(dict(theme=value)).encode('utf-8'))
    return value


def translate(directory, identity, options, subject, grade, cancel, progress, *, translator=None, title=None):
    from .google_translation import Translator
    from .library import Library
    from .translation_knowledge import prepare
    from .translation_provider import build_translator, require_credentials, snapshot
    from .translation_terms import TermPolicy

    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        verify_original(job)
        if not job['regions']:
            raise ValueError('Chọn ít nhất một vùng văn bản trước khi chuyển đổi.')
        subject, grade = str(subject).strip()[:120], str(grade).strip()[:80]
        if not subject:
            raise ValueError('Chọn môn học để dịch đúng ngữ cảnh.')
        selected_options = options_for(options)
        old_density = job['options'].get('density', 'normal')
        changed = job['subject'] != subject or job['grade'] != grade or (job['options'].get('mode') == 'keywords') != (selected_options['mode'] == 'keywords')
        if changed:
            for region in job['regions']:
                region.pop('en', None)
                region.pop('annotations', None)
            job.pop('translation_config', None)
        job.update(options=selected_options, subject=subject, grade=grade, phase='working', message='Đang chuẩn bị nội dung đã chọn.')
        if title is not None:
            job['title'] = title_for(title, Path(job['source_original']).stem)
        if 'translation_config' not in job:
            route = snapshot(directory, include_fallback=True)
            if selected_options['mode'] != 'keywords' and translator is None:
                require_credentials(directory, route['translation_provider'], route)
            job['translation_config'] = {**route,
                'subject': subject, 'grade': grade, 'title': job['title'], 'source_sha256': job['source_sha256']}
        config = job['translation_config']
        config['title'] = job['title']
        write(folder, job)
        try:
            pending = [region for region in job['regions'] if not region.get('en')]
            if job['options']['mode'] == 'keywords':
                pending = job['regions']
            if cancel.is_set():
                raise InterruptedError()
            progress(dict(message='Đang đối chiếu thuật ngữ theo môn.', percent=5))
            plan = prepare(directory, folder, config, [dict(text=region['wire']) for region in pending], cancel)
            with closing(Library.read_only(directory)) as library:
                terms = library.glossary()
            if job['options']['mode'] == 'keywords':
                policy = TermPolicy(subject, terms, references=plan['terms'])
                for region in pending:
                    if changed or old_density != job['options']['density'] or 'annotations' not in region:
                        region['annotations'] = keyword_annotations(region, policy.terms, job['options']['density'])
                    region['en'] = region['vi']
                job['notices'] = ['Chưa tìm được từ khóa đủ căn cứ ở một số vùng; phần nguồn được giữ nguyên.'] if any(not row['annotations'] for row in pending) else []
            elif pending:
                if translator is None:
                    translator = build_translator(directory, {**config, 'translation_work_folder': str(folder)}, 500_000, Translator)
                translator.configure_terms(subject, terms)
                translator.configure_knowledge(plan)
                if hasattr(translator, 'on_service_notice'):
                    translator.on_service_notice = lambda message: progress(dict(message=message))
                output = translator.translate([region['wire'] for region in pending], cancel,
                    lambda done, total: progress(dict(percent=min(95, 5 + round(90 * done / max(1, total))), message='Đang dịch các vùng đã chọn.')))
                for region, english in zip(pending, output, strict=True):
                    validate_translation(region, english)
                    region['en'] = english
                job['notices'] = getattr(translator, 'notices', [])
                job['services'] = getattr(translator, 'used_services', [config.get('translation_provider', 'google')])
            job.update(phase='review', message='Bản dịch đã sẵn sàng. Xem, chỉnh nếu cần rồi bấm Lưu Word song ngữ.')
        except InterruptedError:
            job.update(phase='paused', message='Đã dừng. Phần đã dịch được giữ để tiếp tục.')
        except Exception as exc:
            job.update(phase='paused', message=str(exc), error_code=getattr(exc, 'code', 'word_conversion'))
        write(folder, job)
        return job


def convert(directory, identity, options, subject, grade, cancel, progress, **kwargs):
    job = translate(directory, identity, options, subject, grade, cancel, progress, **kwargs)
    if job['phase'] != 'review':
        return job
    progress(dict(percent=98, message='Đã dịch xong; đang tự động lưu Word.'))
    try:
        return export(directory, identity, cancel)
    except Exception as exc:
        job.update(phase='paused' if isinstance(exc, InterruptedError) else 'review',
                   message='Đã dịch xong nhưng chưa lưu được Word. ' + str(exc) + ' Bấm Lưu Word song ngữ để thử lại.')
        try:
            folder = folder_for(directory, identity)
            with locked(folder):
                write(folder, job)
        except (OSError, ValueError):
            pass  # The completed translation checkpoint already exists for retry.
        return job


def edit(directory, identity, region_id, display):
    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        region = next((row for row in job['regions'] if row['id'] == region_id), None)
        if region is None or job['options']['mode'] == 'keywords':
            raise ValueError('Chọn đúng bản dịch cần sửa.')
        value = str(display)
        for index, lock in enumerate(region['locks']):
            value = value.replace('〔' + lock['text'] + '〕', f'⟦BLC{index}⟧', 1)
        validate_translation(region, value)
        region['en'] = value
        job.update(phase='review', message='Đã lưu chỉnh sửa bản dịch; có thể xuất Word.')
        write(folder, job)
        return job


def edit_keyword(directory, identity, region_id, index, value):
    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        region = next((row for row in job['regions'] if row['id'] == region_id), None)
        if region is None or not 0 <= index < len(region.get('annotations', [])):
            raise ValueError('Từ khóa không còn trong vùng đã chọn.')
        value = str(value).strip()
        if len(value) > 160 or any(char in value for char in '\r\n\t'):
            raise ValueError('Thuật ngữ tiếng Anh cần ngắn gọn, trên một dòng.')
        if value:
            region['annotations'][index]['en'] = value
        else:
            region['annotations'].pop(index)
        job.update(phase='review', message='Đã cập nhật từ khóa.')
        write(folder, job)
        return job


def add_keyword(directory, identity, region_id, vietnamese, english):
    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        region = next((row for row in job['regions'] if row['id'] == region_id), None)
        vi, en = str(vietnamese).strip(), str(english).strip()
        if (region is None or job['options']['mode'] != 'keywords' or not vi or not en
                or max(len(vi), len(en)) > 160 or any(char in vi + en for char in '\r\n\t')):
            raise ValueError('Điền từ tiếng Việt có trong vùng đã chọn và thuật ngữ tiếng Anh ngắn gọn.')
        candidates = keyword_annotations(region, {vi: en}, 'few')
        existing = region.get('annotations', [])
        if not candidates or len(existing) >= 20:
            raise ValueError('Chưa tìm được từ này trong vùng chọn, hoặc vùng đã có 20 từ khóa.')
        annotation = candidates[0]
        if any(row['start'] < annotation['end'] and annotation['start'] < row['end'] for row in existing):
            raise ValueError('Từ khóa đã có hoặc chồng với một từ khóa khác; sửa từ khóa đang có.')
        region['annotations'] = sorted([*existing, annotation], key=lambda row: row['start'])
        region['en'] = region['vi']
        job.update(phase='review', message='Đã thêm từ khóa cho vùng chọn này.')
        write(folder, job)
        return job


def replace_output(source, target, cancel):
    for attempt in range(5):
        if cancel.is_set():
            raise InterruptedError('Đã dừng trước khi lưu; bản trước được giữ.')
        try:
            source.replace(target)
            return
        except OSError as exc:
            if getattr(exc, 'winerror', None) not in {5, 32, 33} or attempt == 4:
                raise
            if cancel.wait(.05 * (attempt + 1)):
                raise InterruptedError('Đã dừng trước khi lưu; bản trước được giữ.') from None


def export(directory, identity, cancel):
    from .storage_space import MIB, require_space

    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        verify_original(job)
        if not job['regions'] or any(not row.get('en') for row in job['regions']):
            raise ValueError('Chưa dịch đủ các vùng đã chọn; tiếp tục chuyển đổi trước khi lưu.')
        if cancel.is_set():
            raise InterruptedError('Đã dừng trước khi lưu Word.')
        require_space(directory, (folder / 'source.docx').stat().st_size * 3 + 16 * MIB)
        # Always rebuild from the frozen original, never append to a prior bilingual output.
        candidate, target = folder / 'candidate.docx', folder / 'result.docx'
        Package(folder / 'source.docx').save(candidate, job['regions'], job['options'])
        Package(candidate)  # Verify that the result remains an editable Word document.
        signature = digest(candidate)
        if cancel.is_set():
            candidate.unlink(missing_ok=True)
            raise InterruptedError('Đã dừng trước khi lưu; bản trước được giữ.')
        if target.exists() and digest(target) != signature:
            shutil.copyfile(target, folder / 'previous.docx')
            if job.get('published'):
                _atomic(folder / 'previous.json', json.dumps(job['published'], ensure_ascii=False).encode('utf-8'))
        replace_output(candidate, target, cancel)
        job.update(output_sha256=signature, phase='completed', message='Đã lưu Word song ngữ vào thư viện.')
        job['published'] = {key: copy.deepcopy(job.get(key)) for key in ('title', 'regions', 'options', 'subject', 'grade', 'output_sha256')}
        original = Path(job['source_original'])
        previous_export = Path(job.get('export_path', ''))
        job['export_path'] = str(target)
        if original.is_file() and digest(original) == job['source_sha256']:
            export_stem = original.stem + ' (Song ngu VI-EN)'
            destination = original.with_name(export_stem + '.docx')
            prior = job.get('export_sha256')
            if (previous_export.is_file() and previous_export.parent == original.parent
                    and previous_export.suffix.lower() == '.docx'
                    and previous_export.stem.startswith(export_stem)
                    and digest(previous_export) in {prior, signature}):
                destination = previous_export
            if destination.exists() and digest(destination) not in {prior, signature}:
                for number in range(2, 1000):
                    candidate_path = destination.with_name(destination.stem + '_' + str(number) + '.docx')
                    if not candidate_path.exists():
                        destination = candidate_path
                        break
                else:
                    destination = target
            try:
                pending = destination.with_name(destination.name + '.' + uuid4().hex + '.pending')
                shutil.copyfile(target, pending)
                pending.replace(destination)
                job.update(export_path=str(destination), export_sha256=signature,
                           message='Đã lưu Word song ngữ cạnh file gốc và trong thư viện Word.')
            except OSError:
                job['message'] = 'Đã lưu trong thư viện Word. Chưa ghi được cạnh file gốc; mở thư mục để lấy bài.'
            finally:
                try:
                    pending.unlink(missing_ok=True)
                except OSError:
                    pass
        write(folder, job)
        return job


def restore_previous(directory, identity):
    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        previous = folder / 'previous.docx'
        if not previous.is_file():
            raise ValueError('Chưa có bản xuất trước để khôi phục.')
        Package(previous)
        prior_state = json.loads((folder / 'previous.json').read_text(encoding='utf-8')) if (folder / 'previous.json').is_file() else {}
        if prior_state and prior_state.get('output_sha256') != digest(previous):
            raise ValueError('Bản xuất trước không còn khớp dữ liệu khôi phục.')
        target = folder / 'result.docx'
        temporary = folder / 'undo.pending'
        shutil.copyfile(previous, temporary)
        if target.exists():
            shutil.copyfile(target, previous)
            if job.get('published'):
                _atomic(folder / 'previous.json', json.dumps(job['published'], ensure_ascii=False).encode('utf-8'))
        temporary.replace(target)
        if prior_state:
            job.update(prior_state)
            job['published'] = copy.deepcopy(prior_state)
        job.update(output_sha256=digest(target), export_path=str(target), phase='completed',
                   message='Đã khôi phục bản xuất trước trong thư viện; tệp ngoài thư viện được giữ nguyên.')
        write(folder, job)
        return job


def trash(directory, identity, deleted):
    folder = folder_for(directory, identity)
    with locked(folder):
        job = read(directory, identity)
        job['deleted_at'] = datetime.now(timezone.utc).isoformat() if deleted else ''
        write(folder, job)
        return job
