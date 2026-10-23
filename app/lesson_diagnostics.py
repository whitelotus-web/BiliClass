"""Explain verified slide checks and failed speech chunks without engine details."""

from .slide_quality import MESSAGES

INFORMATIONAL = {'visual_review', 'source_workspace', 'source_language_pair', 'source_motion_position'}
# These findings have an identifiable missing/invalid result. Bounding-box
# overlap, OCR coverage and animation uncertainty remain scope notes, not errors.
ACTIONABLE = {'source_review_note', 'english_body_missing', 'translation_pair_missing',
              'speech_metadata_invalid', 'speech_metadata_mismatch', 'quiz_mismatch',
              'vietnamese_remaining', 'render_unavailable', 'low_contrast'}
ACTIONS = {
    'source_review_note': 'Đối chiếu nhận xét với đề và hình gốc trước khi sử dụng bài.',
    'text_overflow': 'Tự căn lại khung chữ và đo lại bằng PowerPoint.',
    'panel_text_escape': 'Đưa cặp Việt–Anh vào trong dải nền rồi kiểm tra lại.',
    'possible_overlap': 'Đối chiếu vùng được nêu với hình slide; khung chữ có thể đang giao nhau.',
    'translation_pair_missing': 'Dựng lại cặp Việt–Anh từ bản dịch đã lưu.',
    'render_unavailable': 'Đóng hộp thoại đang chờ trong PowerPoint, rồi kiểm tra lại.',
    'image_or_formula_needs_review': 'Chữ trong ảnh hoặc công thức chưa được xác minh đủ; đối chiếu với bản gốc.',
    'animation_needs_review': 'Xem hiệu ứng khi trình chiếu; phần chưa xác định sẽ không tự đọc.',
    'notes_mismatch': 'Đối chiếu lời đọc với chữ đang có trên slide.',
}


def layout(lesson):
    report = lesson.get('slide_quality') or {}
    pages = []
    for row in report.get('slides', []):
        issues, seen = [], set()
        for issue in row.get('issues', []):
            code = issue.get('code', '')
            cell = issue.get('cell')
            identity = (code, issue.get('shape_id'), tuple(cell or ()))
            if code in INFORMATIONAL or identity in seen:
                continue
            seen.add(identity)
            excerpt = issue.get('excerpt', '')
            location = f'Ô bảng hàng {cell[0]+1}, cột {cell[1]+1}.' if isinstance(cell, list) and len(cell) == 2 else ''
            issues.append(dict(code=code, message=MESSAGES.get(code, 'Cần đối chiếu vùng nội dung này.'),
                               severity=issue.get('severity', 'CHECK'), excerpt=excerpt,
                               location=location,
                               action=ACTIONS.get(code, 'Xem slide và đối chiếu với bài gốc.')))
        if issues:
            pages.append(dict(slide=row['slide'], source_slide=row.get('source_slide', row['slide']),
                              failed=any(i['severity'] == 'FAIL' for i in issues), issues=issues))
    for page in pages:
        page['attention'] = any(issue['severity'] == 'FAIL' or issue['code'] in ACTIONABLE for issue in page['issues'])
    pages.sort(key=lambda row: (not row['attention'], not row['failed'], row['slide']))
    repairs = report.get('local_repairs', [])
    fixed = {row['slide'] for row in repairs if row.get('slide') and row.get('operation') not in
             {'keep_quantities_together', 'align_translation_case'}}
    failures = sum(row['failed'] for row in pages)
    attention = sum(row['attention'] for row in pages)
    rendered = sum(bool(row.get('rendered')) for row in report.get('slides', []))
    render_failed = bool(attention and not rendered and all(
        issue['code'] == 'render_unavailable' for page in pages for issue in page['issues']
        if issue['severity'] == 'FAIL' or issue['code'] in ACTIONABLE))
    review = (lesson.get('external_deck') or {}).get('content_review') or {}
    image_pages = sorted({n for n in review.get('image_pages', []) if type(n) is int and n > 0})
    image_note = (f"Chữ trong ảnh ở slide nguồn {', '.join(map(str, image_pages[:8]))}{'…' if len(image_pages) > 8 else ''} "
                  'chưa được xác minh đầy đủ; kết quả tự kiểm tra không chứng nhận phần này.'
                  if image_pages else review.get('message', ''))
    checked = (f"Đã đo bố cục {rendered}/{len(report.get('slides', []))} slide bằng PowerPoint. " if rendered
               else f"Đã kiểm tra cấu trúc {len(report.get('slides', []))} slide. " if report else '')
    return dict(pages=pages, total=len(report.get('slides', [])), repaired=len(fixed), failures=failures,
                remaining=attention, notices=sum(not row['attention'] for row in pages), has_report=bool(report),
                attention=attention, rendered=rendered,
                title='Bố cục cần xem lại' if failures else 'Chưa hoàn tất kiểm tra bằng PowerPoint'
                      if render_failed else 'Có phần chưa hoàn thiện' if attention else 'Đã kiểm tra tự động',
                image_note=image_note,
                scope_note='Kiểm tra cấu trúc và bố cục; chưa xác minh toàn bộ ý nghĩa, chữ trong ảnh và hiệu ứng.',
                summary=(f'Đã tự căn chỉnh {len(fixed)} slide. ' if fixed else '') + checked
                        + ('Chưa đo được bố cục bằng PowerPoint; bản đã xử lý được giữ để kiểm tra tiếp.' if render_failed
                           else f'Còn {failures} slide có lỗi bố cục chưa sửa được; bản đã xử lý được giữ lại.' if failures
                           else f'Còn {attention} slide có vấn đề cụ thể; xem trạng thái xử lý trong chi tiết.' if attention
                           else 'Chưa phát hiện lỗi cụ thể trong phạm vi kiểm tra. Giới hạn kiểm tra nằm trong chi tiết.'
                           if report else 'Chưa có kết quả kiểm tra slide.'))


def failed_speech(inspection, voices, tasks):
    """A shared utterance can belong to several slides; retain every exact match."""
    from .powerpoint import slide_for_locator
    from .slide_speech import speech_chunks

    def chunks(text):
        try:
            return speech_chunks(text)
        except ValueError:
            return []  # Diagnostics must not break a completed voice job.

    locations = {}
    for index, unit in enumerate(inspection.get('profile', {}).get('units', []), 1):
        number = slide_for_locator(unit.get('locator', '')) or index
        for language in ('vi', 'en'):
            for text in chunks(unit.get(language, '')):
                locations.setdefault((text, voices.get(language)), set()).add((number, language))
    for page in (inspection.get('slide_speech') or {}).get('slides', []):
        for segment in page.get('englishSpeechSegments', []):
            for text in chunks(segment.get('english_text', '')):
                locations.setdefault((text, voices.get('en')), set()).add((page['slide'], 'en'))
    rows = []
    for text, voice in tasks[:12]:
        matches = sorted(locations.get((text, voice), []))
        rows.append(dict(slides=sorted({number for number, _ in matches}),
                         languages=sorted({language for _, language in matches}), excerpt=text[:140]))
    return rows


def translation_context(error, units):
    """Map an exact failed chunk back to source slides; never guess from percent."""
    text = getattr(error, 'failed_text', '')
    if not text:
        return {}
    matches = [unit for unit in units if text.strip() in unit.get('text', '')]
    numbers = sorted({unit['slide'] for unit in matches})
    # Native translation protects quantities with internal tokens. Show the
    # source's actual wording rather than leaking those tokens to the teacher.
    excerpt = matches[0].get('raw', text) if matches else text
    return dict(source_slides=numbers, excerpt=excerpt.strip()[:140])
