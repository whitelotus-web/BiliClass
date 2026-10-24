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
    from .storage_space import MIB, require_space
    from .translation_provider import snapshot

    require_space(directory, (Path(source).stat().st_size * 4 if source else len(text.encode('utf-8')) * 4) + 128 * MIB)

    selection = snapshot(directory, config.get('translation_provider'))
    if config.get('translation_profile') and config['translation_profile'] != selection.get('translation_profile'):
        raise TranslationProblem('api_settings', 'URL/model dịch đã đổi so với hàng đợi. Khôi phục cấu hình cũ hoặc chọn lại file để bắt đầu lượt mới.')
    if 'translation_budget' in config:
        selection['translation_budget'] = config['translation_budget']
    config = {**config, **selection, 'provider': 'google_translate', 'request_id': uuid4().hex,
              'adaptive_bilingual':config.get('conversion_format')=='parallel_columns'}
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
    if config.get('style') == 'template':
        config['template_version'] = 2
        if config.get('custom_template'):
            from .pptx_template import stored_path, validate_roles
            metadata = config['custom_template']
            template = stored_path(directory, metadata)
            config['template_roles'] = validate_roles(metadata, metadata['roles'])
            shutil.copyfile(template, folder / 'template.pptx')
            config['template_sha256'] = hashlib.sha256((folder / 'template.pptx').read_bytes()).hexdigest()
            if config['template_sha256'] != metadata['sha256']:
                raise ValueError('Mẫu vừa thay đổi; chọn lại mẫu trước khi chuyển đổi.')
        else:
            from .universal_templates import asset, manifest
            template = asset(config.get('preset', 'standard'))
            shutil.copyfile(template, folder / 'template.pptx')
            config.update(template_version=3, template_layouts=manifest()['layouts'],
                          template_sha256=hashlib.sha256((folder / 'template.pptx').read_bytes()).hexdigest())
    config.update(source_file=target.name, source_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    if source:
        from .export_origin import remember_source
        from .library import Library

        with closing(Library(directory)) as library:
            remember_source(library, source, config['source_sha256'])
    (folder / 'config.json').write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    from .library import Library
    with closing(Library(directory)) as library:
        library.set_setting('google_request_folder', str(folder))
    return {'folder': str(folder), 'config': config}


class ConversionDiscarded(ValueError):
    pass


def load(directory, folder, *, verify_source=True, allow_discarded=False):
    root = (Path(directory) / 'google_jobs').resolve()
    folder = Path(folder).resolve()
    if folder.parent != root or not folder.is_dir():
        raise ValueError('Bản ghi chuyển đổi không thuộc thư viện này.')
    if not allow_discarded and (folder / 'conversion-discarded').exists():
        raise ConversionDiscarded('Bài đang tạo đã được hủy. Chọn tài liệu để tạo bài mới.')
    config = json.loads((folder / 'config.json').read_text(encoding='utf-8'))
    name = config['source_file']
    if Path(name).name != name or (folder / name).resolve().parent != folder:
        raise ValueError('Đường dẫn nguồn không hợp lệ.')
    if verify_source and hashlib.sha256((folder / name).read_bytes()).hexdigest() != config['source_sha256']:
        raise ValueError('Nguồn chuyển đổi đã thay đổi; chọn lại tài liệu.')
    if config.get('template_sha256') and hashlib.sha256((folder / 'template.pptx').read_bytes()).hexdigest() != config['template_sha256']:
        raise ValueError('Mẫu của lượt chuyển đổi đã thay đổi; tạo lượt mới.')
    return {'folder': str(folder), 'config': config}


def mark_discarded(directory, folder):
    """Durable stop marker, scoped to one validated Google job."""
    job = load(directory, folder, verify_source=False, allow_discarded=True)
    if job['config'].get('provider') != 'google_translate' or job['config'].get('request_id') != Path(job['folder']).name:
        raise ValueError('Bản ghi chuyển đổi không hợp lệ.')
    (Path(job['folder']) / 'conversion-discarded').touch()
    return job


def discard(directory, folder):
    """Remove only this run from active work; use recoverable library deletion.

    Source/audio objects are shared by hash and must never be unlinked here.
    Also catches the race where save committed just before the teacher canceled.
    """
    from .library import Library

    job = mark_discarded(directory, folder)
    request_id = job['config']['request_id']
    with closing(Library(directory)) as library:
        rows = [json.loads(row[0]) for row in library.db.execute('SELECT content FROM lessons')]
        identities = [row['id'] for row in rows if not row.get('deleted_at')
                      and row.get('external_deck', {}).get('provider') == 'google_translate'
                      and row['external_deck'].get('request_id') == request_id]
        if identities:
            library.trash_lessons(identities)
        if library.setting('google_request_folder', '') == job['folder']:
            library.set_setting('google_request_folder', '')
    return identities


def dismiss(directory, folder):
    """Forget an idle input selection without deleting saved lessons or caches."""
    from .library import Library

    job = load(directory, folder, verify_source=False, allow_discarded=True)
    if not (Path(job['folder']) / 'saved.json').is_file():
        mark_discarded(directory, folder)
    with closing(Library(directory)) as library:
        if library.setting('google_request_folder', '') == job['folder']:
            library.set_setting('google_request_folder', '')


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
    if config.get('template_version') == 3:
        from .universal_templates import asset, build
        template = Path(path).parent / 'template.pptx'
        if not config.get('template_sha256'):
            template = asset(config.get('preset', 'standard'))
        return build(path, template, config, pairs, cancel, source)
    if config.get('template_version') == 2:
        from .pptx_template import build
        from .template_builtin import create
        custom = config.get('custom_template')
        template = Path(path).parent / ('template.pptx' if custom else 'builtin-template.pptx')
        if not custom:
            create(template, config.get('preset', 'standard'))
        return build(path, template, config, pairs, cancel, source,
                     config.get('template_roles') if custom else {'cover': 1, 'intro': 0, 'content': 3, 'ending': 4})
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
                             max(1, len(textwrap.wrap(en_line, 32))) * 20) * 1.4 / 72
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
                    height = max(1, len(textwrap.wrap(text, columns))) * size * 1.4 / 72
                    if y + height > 6.75:
                        raise TranslationProblem('api_layout', 'Các cặp nội dung quá dài; tách ngắn ý nguồn.')
                    box(slide, text, .55, y, 12.2, height, size, italic=italic)
                    y += height + .08
        else:
            box(slide, en, .55, 1.5, 12.2, 5.2, 23)
        box(slide, f'Page {len(deck.slides)}' if mode=='english_only' else locator, .55, 7.02, 12.2, .25, 10).name='BCL_DECORATION locator'
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
            box(visual, f'Slide {index} · Original visuals' if mode=='english_only' else f'Slide {index} · Hình gốc / Original visuals', .55, 7.02, 12.2, .25, 10).name='BCL_DECORATION locator'
            visual.notes_slide.notes_text_frame.text = 'CHECK: Hình từ nguồn; chữ trong ảnh chưa được dịch/xác minh. Hiệu ứng và đối tượng nhúng cần đối chiếu nguồn.'
    if not len(deck.slides):
        raise ValueError('Không tìm thấy nội dung để tạo PowerPoint.')
    from .local_template_style import decorate

    decorate(deck, config)
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
            (Path(job['folder'])/'conversion-issue.json').unlink(missing_ok=True)
            return _convert(directory, job, cancel, progress, budget=budget, translator=translator)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            from .storage_space import StorageProblem

            if isinstance(exc, StorageProblem):
                raise
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
    from .library import Library
    from .native_bilingual import assemble, extract

    job = load(directory, job['folder'])
    folder, config = Path(job['folder']), dict(job['config'])
    if config['conversion_format'] == 'integrated_keywords':
        raise TranslationProblem('api_settings', 'Dịch vụ chuyển ngữ hỗ trợ Hai cột, Từng câu và Tiếng Anh 100%. Chọn một trong ba kiểu này.')
    if translator is None:
        from .translation_provider import build_translator

        translator = build_translator(directory, config, budget, Translator)
    if hasattr(translator, 'configure_terms'):
        with closing(Library(directory)) as library:
            translator.configure_terms(config.get('subject', ''), library.glossary())
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
    checkpoint = folder / 'publish-ready.json'
    if checkpoint.is_file():
        saved = json.loads(checkpoint.read_text(encoding='utf-8'))
        target = (Path(directory) / saved['artifact']).resolve()
        if (target.is_relative_to(Path(directory).resolve()) and target.is_file()
                and saved['source_sha256'] == config['source_sha256']
                and saved['job_config'] == job['config']
                and hashlib.sha256(target.read_bytes()).hexdigest() == saved['inspection']['slide_speech']['sha256']):
            return _publish_checked(directory, folder, saved['config'], target, saved['inspection'], cancel, progress)
    source = folder / config['source_file']
    progress.stage('upload', 'Đang đọc nội dung tài liệu.')
    manifest = extract(source, config['conversion_format'], preserve_design=True,
                       same_slide=config['conversion_format']!='english_only') if source.suffix == '.pptx' and config['style'] == 'source' else None
    use_native = manifest is not None
    warnings = []
    picture_data = {'rows': [], 'warnings': []}
    content_review = {}
    if source.suffix == '.pptx':
        from pptx import Presentation

        from .picture_ocr import extract_pictures
        from .universal_content import image_content_pages

        image_pages = image_content_pages(Presentation(source))

        progress.stage('upload', 'Đang đọc nội dung và hình minh họa.')
        try:
            picture_data = extract_pictures(source, directory, cancel,
                                           lambda message: progress.stage('upload', message),
                                           include_animated=config['style'] == 'template')
        except ValueError as exc:
            picture_data = {'rows': [], 'warnings': [str(exc)]}
        # A photograph without detected text is not an untranslated paragraph.
        # An unavailable OCR pass leaves coverage unknown rather than complete.
        text_pages = picture_data.get('text_pages', image_pages)
        needs_review = sorted(set(text_pages)
                              | {row['slide'] for row in picture_data['rows']})
        if needs_review:
            content_review = {
                'image_pages': needs_review, 'coverage': 'unverified',
                'message': (f"{len(needs_review)} slide cần đối chiếu chữ trong ảnh "
                            f"(slide nguồn: {', '.join(map(str, needs_review[:8]))}{'…' if len(needs_review) > 8 else ''}). "
                            "Tool tự nhận diện và dịch vùng chữ đọc rõ; chưa xác minh đủ chữ, bảng và công thức trong ảnh."),
            }
            warnings.append(content_review['message'])
        warnings.extend(picture_data['warnings'])
        (folder/'picture-ocr.json').write_text(json.dumps(picture_data,ensure_ascii=False),encoding='utf-8')
    target = folder / 'result.pptx'
    def notify(done,total):
        progress.stage('translate', 'Đang hoàn thiện nội dung song ngữ.', done, total)
    if use_native:
        units = manifest['units']
        manifest['note_slides'] = sorted({row['slide'] for row in picture_data['rows']})
        pending = [u for u in units if u['language'] not in {'en', 'neutral'}]
        try:
            if hasattr(translator, 'translate_native'):
                translated = translator.translate_native(pending, picture_data['rows'], cancel, notify)
            else:
                translated = translator.translate([u['text'] for u in pending] +
                                                 [row['text'] for row in picture_data['rows']], cancel, notify)
        except TranslationProblem as exc:
            from .lesson_diagnostics import translation_context

            context = translation_context(exc, pending + picture_data['rows'])
            if context:
                from .library_location import write_record

                write_record(folder/'conversion-issue.json', dict(stage='translate', code=exc.code, **context))
                slides = ', '.join(map(str, context['source_slides']))
                location = f'Slide nguồn {slides}' if slides else 'Một đoạn nội dung'
                raise TranslationProblem(exc.code, f'{location}: {exc} Vùng nội dung: “{context["excerpt"]}”') from exc
            raise
        values = {u['id']: {'en': u['text']} for u in units if u['language'] in {'en', 'neutral'}}
        values.update({u['id']: {'en': en} for u, en in zip(pending, translated[:len(pending)], strict=True)})
        progress.stage('assemble', 'Đang sắp xếp nội dung bài giảng.')
        assemble(source, target, manifest, values, config['conversion_format'])
        if picture_data['rows']:
            from .picture_translation import apply_picture_translations

            image_values = {row['id']: en for row,en in zip(picture_data['rows'],translated[len(pending):],strict=True)}
            image_result = apply_picture_translations(target,manifest,picture_data['rows'],image_values,
                                                      config['conversion_format'],cancel)
            warnings.extend(image_result['warnings'])
            (folder/'picture-layout.json').write_text(json.dumps(image_result,ensure_ascii=False),encoding='utf-8')
        from .native_layout import fit_preserved_frames
        fitting = fit_preserved_frames(target,manifest,cancel)
        (folder/'layout-fit.json').write_text(json.dumps(fitting),encoding='utf-8')
        if manifest.get('paired_slides'):
            warnings.append('Slide kín chữ/hình hoặc có hiệu ứng được giữ thành cặp trang Việt–Anh kế tiếp; số slide có thể tăng để giữ thiết kế gốc.')
        if any(row.get('continuation') for row in manifest.get('layout_plan',[])):
            warnings.append('Một số khung nhiều đoạn được chia thành trang tiếp nối; mỗi trang vẫn có cả Việt và Anh cùng hình gốc.')
        if manifest.get('visual_slides'):
            warnings.append('Hình, hiệu ứng, biểu đồ và đối tượng nhúng được giữ từ nguồn. OCR chỉ dịch chữ nhận rõ và đặt được an toàn; công thức, nhãn biểu đồ và vùng còn lại cần đối chiếu.')
        if manifest.get('font_fallbacks'):
            warnings.append('Font nhúng chưa có trên máy được thay bằng Arial cho cả Việt–Anh để tránh lỗi ký tự khi thêm bản dịch.')
    if not use_native:
        from .importers import extraction_warnings, parse_document
        from .input_analysis import language_of

        if manifest and manifest['visual_slides']:
            warnings.append('Nguồn có bố cục/đối tượng phức tạp: đã dùng mẫu mới, có thể đổi số slide. Hiệu ứng, biểu đồ và đối tượng nhúng chưa được bảo toàn; đối chiếu tệp gốc.')
        warnings.extend(extraction_warnings(source))
        if source.suffix == '.pptx':
            from pptx import Presentation

            from .source_deck import text_blocks
            if config.get('template_version') == 3:
                from .universal_templates import source_blocks
                blocks = source_blocks(Presentation(source))
            else:
                blocks = [(u['locator'], u['text']) for u in text_blocks(Presentation(source))]
            blocks.extend((f"Slide {row['slide']} · chữ trong ảnh",row['text']) for row in picture_data['rows'])
            if not blocks and config.get('template_version') != 3:
                raise TranslationProblem('api_result', 'PowerPoint chỉ có ảnh/đối tượng, chưa có văn bản dịch được. Dùng nguồn có chữ chỉnh sửa được; bản gốc được giữ.')
        else:
            blocks = parse_document(source, cancelled=cancel)
        # Short corresponding source units paginate without shrinking fonts
        # or truncating translations. Line boundaries are kept as data.
        units = [(locator, part) for locator, text in blocks for line in text.splitlines() if line.strip()
                 for part in chunks(line, maximum=320)]
        texts = [text for _, text in units]
        from .universal_templates import needs_translation
        wanted = [index for index, text in enumerate(texts) if language_of(text) != 'en'
                  and (config.get('template_version') != 3 or needs_translation(text))]
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
        warnings.append('Mẫu mới được dàn trang tại máy. Hiệu ứng và tương tác gốc không được tái dựng. Chữ trong ảnh, nhãn biểu đồ và đối tượng nhúng cần đối chiếu với tài liệu nguồn.')
    if cancel.is_set():
        raise InterruptedError('Đã dừng; bản dịch đã được lưu.')
    from .slide_repair import repair_and_inspect

    # Render once before publishing. Local repairs reuse unchanged slide PNGs;
    # no browser round-trip, retranslation, narration or unbounded retries.
    progress.stage('quality','Đang hoàn thiện bản trình chiếu.')
    # A template frame can require stacked pairs even in the automatic
    # bilingual option. Check visible coverage, without imposing two columns
    # on a narrow teacher-supplied frame; native overflow checks still apply.
    quality_mode = ('sentence_pairs' if not use_native and config.get('template_version') in {2,3}
                    and config['conversion_format'] == 'parallel_columns' else config['conversion_format'])
    checked=repair_and_inspect(target,directory,source=source if use_native else None,
                              mode=quality_mode,style=config['style'],cancel=cancel,
                              progress=progress.scope('quality'),
                              layout_plan=manifest.get('layout_plan') if use_native else None)
    target=Path(checked['path'])
    inspection=checked['inspection']
    if content_review:
        inspection['content_review'] = content_review
    from .lesson_completion import VERSION

    inspection['slide_quality'].update(completion_version=VERSION,
                                       completion_sha256=inspection['slide_speech']['sha256'])
    (folder/'automatic-layout-check.json').write_text(json.dumps({
        'changes':checked['changes'],'counts':inspection['slide_quality']['counts']}),encoding='utf-8')
    inspection['review_notes'] = list(dict.fromkeys(inspection['review_notes'] + warnings))
    ready = {'source_sha256': job['config']['source_sha256'], 'job_config': job['config'], 'config': config,
             'artifact': target.resolve().relative_to(Path(directory).resolve()).as_posix(), 'inspection': inspection}
    pending = (folder / 'publish-ready.json').with_suffix('.tmp')
    pending.write_text(json.dumps(ready, ensure_ascii=False), encoding='utf-8')
    pending.replace(folder / 'publish-ready.json')
    return _publish_checked(directory, folder, config, target, inspection, cancel, progress)


def _publish_checked(directory, folder, config, target, inspection, cancel, progress):
    from .lesson_import import save_conversion
    from .library import Library

    load(directory, folder, verify_source=False)
    if cancel.is_set():
        raise InterruptedError('Đã dừng chuyển đổi.')
    progress.stage('save', 'Đang lưu bài giảng song ngữ.')
    with closing(Library(directory)) as library:
        stored = library.store_source(target)
    lesson, preview = save_conversion(directory, config, stored, inspection, cancel)
    completed = folder / 'saved.json'
    pending = completed.with_suffix('.tmp')
    pending.write_text(json.dumps({'lesson_id': lesson['id']}), encoding='utf-8')
    pending.replace(completed)
    (folder / 'conversion-error.json').unlink(missing_ok=True)
    with closing(Library(directory)) as library:
        if library.setting('google_request_folder', '') == str(folder):
            library.set_setting('google_request_folder', '')
    return lesson, preview
