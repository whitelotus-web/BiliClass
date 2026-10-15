"""Translate text via Google; construct and inspect PowerPoint locally.

No browser imports or web submission. Source PowerPoints keep native resources;
Vietnamese and English share each page, including bilingual continuations.
"""

import hashlib
import json
import shutil
from contextlib import closing
from pathlib import Path
from uuid import uuid4

from .google_translation import TranslationProblem, Translator, chunks


def prepare(directory, config, source=None, text=''):
    from .document_limits import check_document_size

    config = {**config, 'provider': 'google_translate', 'request_id': uuid4().hex}
    folder = Path(directory) / 'google_jobs' / config['request_id']
    folder.mkdir(parents=True)
    if source:
        source = Path(source)
        check_document_size(source)
        target = folder / ('source' + source.suffix.lower())
        shutil.copyfile(source, target)
    else:
        if not text.strip() or len(text) > 1_000_000:
            raise ValueError('Nhập nội dung từ 1 đến 1.000.000 ký tự.')
        target = folder / 'source.txt'
        target.write_text(text, encoding='utf-8')
    config.update(source_file=target.name, source_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (folder / 'config.json').write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    from .library import Library
    with closing(Library(directory)) as library:
        library.set_setting('google_request_folder', str(folder))
    return {'folder': str(folder), 'config': config}


def load(directory, folder, *, verify_source=True):
    root = (Path(directory) / 'google_jobs').resolve()
    folder = Path(folder).resolve()
    if folder.parent != root or not folder.is_dir():
        raise ValueError('Bản ghi chuyển đổi không thuộc thư viện này.')
    config = json.loads((folder / 'config.json').read_text(encoding='utf-8'))
    name = config['source_file']
    if Path(name).name != name or (folder / name).resolve().parent != folder:
        raise ValueError('Đường dẫn nguồn không hợp lệ.')
    if verify_source and hashlib.sha256((folder / name).read_bytes()).hexdigest() != config['source_sha256']:
        raise ValueError('Nguồn chuyển đổi đã thay đổi; chọn lại tài liệu.')
    return {'folder': str(folder), 'config': config}


def original_source(directory, lesson):
    """Recover only this lesson's hash-verified original for later local checks."""
    import re

    external = lesson.get('external_deck', {})
    request = external.get('request_id', '')
    if (external.get('provider') != 'google_translate' or external.get('requested_style') != 'source'
            or not isinstance(request,str) or not re.fullmatch('[a-f0-9]{32}',request)):
        return None
    try:
        job = load(directory,Path(directory)/'google_jobs'/request)
        if job['config']['source_sha256'] != external.get('original_source_sha256'):
            return None
        source = Path(job['folder'])/job['config']['source_file']
        return source if source.suffix == '.pptx' else None
    except (OSError,ValueError,KeyError,TypeError):
        return None


def _template(path, config, pairs, cancel, source=None):
    """Known non-overlapping text regions; pagination keeps each pair intact."""
    import io

    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)

    def box(slide, text, x, y, width, height, size=22, italic=False, bold=False):
        import textwrap
        minimum = min(size, 18)
        for candidate in range(size, minimum - 1, -1):
            columns = max(1, int(width * 72 / (candidate * .65)))
            lines = sum(max(1, len(textwrap.wrap(line, columns))) for line in text.splitlines())
            if lines * candidate * 1.25 <= height * 72:
                size = candidate
                break
        else:
            raise TranslationProblem('api_layout', 'Một vùng chữ chưa vừa trang chiếu. Rút ngắn tên bài hoặc tách ngắn ý nguồn; bản dịch đã lưu để tiếp tục.')
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
        frame = shape.text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        for index, line in enumerate(text.splitlines()):
            p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            p.text = line
            p.font.name, p.font.size = 'Arial', Pt(size)
            p.font.italic, p.font.bold = italic, bold
            p.font.color.rgb = RGBColor.from_string('202D42')
            p.space_before = p.space_after = Pt(0)
            p.line_spacing = 1.15
            p.font._rPr.set('lang', 'en-US' if italic or mode == 'english_only' else 'vi-VN')
        return shape

    def page():
        if cancel.is_set():
            raise InterruptedError('Đã dừng dựng bài giảng.')
        return deck.slides.add_slide(deck.slide_layouts[6])

    mode = config['conversion_format']
    for locator, vi, en in pairs:
        slide = page()
        if mode != 'english_only':
            box(slide, config['title'], .55, .25, 12.2, .75, 26, bold=True)
        box(slide, config['english_title'], .55, .25 if mode == 'english_only' else 1.02,
            12.2, .7, 21, italic=True)
        if mode == 'parallel_columns':
            import textwrap
            left, right = vi.splitlines(), en.splitlines()
            if len(left) != len(right):
                left, right = [vi], [en]
            y = 1.95
            for vi_line, en_line in zip(left, right, strict=True):
                height = max(max(1, len(textwrap.wrap(vi_line, 29))) * 22,
                             max(1, len(textwrap.wrap(en_line, 32))) * 20) * 1.25 / 72
                if y + height > 6.75:
                    raise TranslationProblem('api_layout', 'Các cặp nội dung quá dài để căn hàng; tách ngắn ý nguồn.')
                box(slide, vi_line, .55, y, 5.9, height, 22)
                box(slide, en_line, 6.9, y, 5.9, height, 20, italic=True)
                y += height + .12
        elif mode == 'sentence_pairs':
            import textwrap
            left, right = vi.splitlines(), en.splitlines()
            if len(left) != len(right):
                left, right = [vi], [en]
            y = 1.95
            for vi_line, en_line in zip(left, right, strict=True):
                for text, size, italic in [(vi_line, 22, False), (en_line, 20, True)]:
                    columns = max(1, int(12.2 * 72 / (size * .65)))
                    height = max(1, len(textwrap.wrap(text, columns))) * size * 1.25 / 72
                    if y + height > 6.75:
                        raise TranslationProblem('api_layout', 'Các cặp nội dung quá dài; tách ngắn ý nguồn.')
                    box(slide, text, .55, y, 12.2, height, size, italic=italic)
                    y += height + .08
        else:
            box(slide, en, .55, 1.5, 12.2, 5.2, 23)
        box(slide, locator, .55, 7.02, 12.2, .25, 10)
        slide.notes_slide.notes_text_frame.text = 'BILICLASS_NOTES:\nVI: ' + vi + '\nEN: ' + en
    # Ordinary source pictures are retained on separate visual pages. No
    # picture is allowed to sit on top of a translated text region.
    if source and source.suffix.lower() == '.pptx':
        from .native_bilingual import leaves
        original = Presentation(source)
        for index, source_slide in enumerate(original.slides, 1):
            pictures = [s for s in leaves(source_slide.shapes) if int(s.shape_type) == 13]
            if not pictures:
                continue
            visual = page()
            scale = min(float(Inches(12.2)) / original.slide_width, float(Inches(5.65)) / original.slide_height)
            for picture in pictures:
                visual.shapes.add_picture(io.BytesIO(picture.image.blob),
                    int(Inches(.55) + picture.left * scale), int(Inches(.7) + picture.top * scale),
                    width=int(picture.width * scale), height=int(picture.height * scale))
            box(visual, f'Slide {index} · Hình gốc / Original visuals', .55, 7.02, 12.2, .25, 10)
            visual.notes_slide.notes_text_frame.text = 'CHECK: Hình từ nguồn; chữ trong ảnh chưa được dịch/xác minh. Hiệu ứng và đối tượng nhúng cần đối chiếu nguồn.'
    if not len(deck.slides):
        raise ValueError('Không tìm thấy nội dung để tạo PowerPoint.')
    pending = path.with_suffix('.pending.pptx')
    try:
        deck.save(pending)
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)


def convert(directory, job, cancel, progress, *, budget=500_000, translator=None):
    """OS-owned lock prevents duplicate work across two BiliClass windows."""
    job = load(directory, job['folder'])
    with (Path(job['folder']) / 'convert.lock').open('a+b') as lock:
        import os
        if lock.tell() == 0:
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise TranslationProblem('api_busy', 'Bài đang được xử lý trong một cửa sổ BiliClass khác.') from None
        try:
            return _convert(directory, job, cancel, progress, budget=budget, translator=translator)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, TranslationProblem):
                raise
            # Keep structural diagnostics private and never mistake a document
            # parser failure for an absent API credential or a network outage.
            import traceback
            code = 'source_document' if getattr(progress, 'state', {}).get('stage') == 'upload' else 'api_conversion'
            details = {'code': code, 'type': type(exc).__name__, 'frames': [
                {'module': Path(frame.filename).name, 'line': frame.lineno, 'function': frame.name}
                for frame in traceback.extract_tb(exc.__traceback__)]}
            (Path(job['folder']) / 'conversion-error.json').write_text(json.dumps(details), encoding='utf-8')
            message = ('Chưa đọc được một định dạng trong tài liệu nguồn. API key vẫn được giữ; cập nhật tool rồi tiếp tục bài.'
                       if code == 'source_document' else
                       'Chưa hoàn thiện được bản PowerPoint. Bản dịch đã lưu được giữ để tiếp tục; kiểm tra định dạng tài liệu.')
            raise TranslationProblem(code, message) from exc
        finally:
            lock.seek(0)
            if os.name == 'nt':
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _convert(directory, job, cancel, progress, *, budget=500_000, translator=None):
    from .chatgpt_handoff import inspect_returned_deck
    from .lesson_import import save_conversion
    from .library import Library
    from .native_bilingual import assemble, extract

    job = load(directory, job['folder'])
    folder, config = Path(job['folder']), dict(job['config'])
    if config['conversion_format'] == 'integrated_keywords':
        raise TranslationProblem('api_settings', 'Google Dịch hỗ trợ Hai cột, Từng câu và Tiếng Anh 100%. Chọn một trong ba kiểu này.')
    translator = translator or Translator(directory, budget)
    if cancel.is_set():
        raise InterruptedError('Đã dừng chuyển đổi.')
    completed = folder / 'saved.json'
    if completed.is_file():
        from .chatgpt_handoff import external_preview
        with closing(Library(directory)) as library:
            lesson = library.get(json.loads(completed.read_text())['lesson_id'])
            if lesson.get('deleted_at'):
                raise ValueError('Bài đã ở thùng rác; khôi phục trong thư viện để mở lại.')
            if library.setting('google_request_folder', '') == str(folder):
                library.set_setting('google_request_folder', '')
            return lesson, external_preview(lesson, directory)
    source = folder / config['source_file']
    progress.stage('upload', 'Đang đọc nội dung tài liệu.')
    manifest = extract(source, config['conversion_format'], preserve_design=True, same_slide=True) if source.suffix == '.pptx' and config['style'] == 'source' else None
    use_native = manifest is not None
    warnings = []
    target = folder / 'result.pptx'
    def notify(done,total):
        progress.stage('translate', 'Đang hoàn thiện nội dung song ngữ.', done, total)
    if use_native:
        units = manifest['units']
        pending = [u for u in units if u['language'] not in {'en', 'neutral'}]
        translated = translator.translate([u['text'] for u in pending], cancel, notify)
        values = {u['id']: {'en': u['text']} for u in units if u['language'] in {'en', 'neutral'}}
        values.update({u['id']: {'en': en} for u, en in zip(pending, translated, strict=True)})
        progress.stage('assemble', 'Đang sắp xếp nội dung bài giảng.')
        assemble(source, target, manifest, values, config['conversion_format'])
        from .native_layout import fit_preserved_frames
        fitting = fit_preserved_frames(target,manifest,cancel)
        (folder/'layout-fit.json').write_text(json.dumps(fitting),encoding='utf-8')
        if manifest.get('paired_slides'):
            warnings.append('Slide kín chữ/hình hoặc có hiệu ứng được giữ thành cặp trang Việt–Anh kế tiếp; số slide có thể tăng để giữ thiết kế gốc.')
        if any(row.get('continuation') for row in manifest.get('layout_plan',[])):
            warnings.append('Một số khung nhiều đoạn được chia thành trang tiếp nối; mỗi trang vẫn có cả Việt và Anh cùng hình gốc.')
        if manifest.get('visual_slides'):
            warnings.append('Hình, hiệu ứng, biểu đồ và đối tượng nhúng được giữ từ nguồn. Chữ nằm trong ảnh/biểu đồ chưa được dịch tự động; cần đối chiếu khi trình chiếu.')
    if not use_native:
        from .importers import extraction_warnings, parse_document
        from .input_analysis import language_of

        if manifest and manifest['visual_slides']:
            warnings.append('Nguồn có bố cục/đối tượng phức tạp: đã dùng mẫu mới, có thể đổi số slide. Hiệu ứng, biểu đồ và đối tượng nhúng chưa được bảo toàn; đối chiếu tệp gốc.')
        warnings.extend(extraction_warnings(source))
        if source.suffix == '.pptx':
            from pptx import Presentation

            from .source_deck import text_blocks
            blocks = [(u['locator'], u['text']) for u in text_blocks(Presentation(source))]
            if not blocks:
                raise TranslationProblem('api_result', 'PowerPoint chỉ có ảnh/đối tượng, chưa có văn bản dịch được. Dùng nguồn có chữ chỉnh sửa được; bản gốc được giữ.')
        else:
            blocks = parse_document(source, cancelled=cancel)
        # Short corresponding source units paginate without shrinking fonts
        # or truncating translations. Line boundaries are kept as data.
        units = [(locator, part) for locator, text in blocks for line in text.splitlines() if line.strip()
                 for part in chunks(line, maximum=200)]
        texts = [text for _, text in units]
        wanted = [index for index, text in enumerate(texts) if language_of(text) != 'en']
        english = list(texts)
        output = translator.translate([texts[i] for i in wanted] + [config['title']], cancel, notify)
        for index, value in zip(wanted, output[:-1], strict=True):
            english[index] = value
        config['english_title'] = output[-1]
        # Splitting a long translated pair independently would lose alignment.
        if any(len(en) > 650 for en in english):
            raise TranslationProblem('api_result', 'Một ý dịch quá dài để vừa mẫu; tách ngắn hơn nội dung nguồn rồi tiếp tục.')
        progress.stage('assemble', 'Đang dàn trang bài giảng song ngữ.')
        packed = []
        for (locator, vi), en in zip(units, english, strict=True):
            if (packed and packed[-1][0] == locator and len(packed[-1][1]) + len(vi) < 300
                    and len(packed[-1][2]) + len(en) < 400):
                old = packed.pop()
                packed.append((locator, old[1] + '\n' + vi, old[2] + '\n' + en))
            else:
                packed.append((locator, vi, en))
        _template(target, config, packed, cancel, source)
        config['style'] = 'template'
    if cancel.is_set():
        raise InterruptedError('Đã dừng; bản dịch đã được lưu.')
    progress.stage('quality', 'Đang kiểm tra nội dung và bố cục.')
    inspection = inspect_returned_deck(target, source if use_native else None,
                                      config['conversion_format'], config['style'],
                                      layout_plan=manifest.get('layout_plan') if use_native else None)
    inspection['review_notes'] = list(dict.fromkeys(inspection['review_notes'] + warnings))
    progress.stage('save', 'Đang lưu bài giảng song ngữ.')
    with closing(Library(directory)) as library:
        stored = library.store_source(target)
    lesson, preview = save_conversion(directory, config, stored, inspection, cancel)
    pending = completed.with_suffix('.tmp')
    pending.write_text(json.dumps({'lesson_id': lesson['id']}), encoding='utf-8')
    pending.replace(completed)
    with closing(Library(directory)) as library:
        if library.setting('google_request_folder', '') == str(folder):
            library.set_setting('google_request_folder', '')
    return lesson, preview
