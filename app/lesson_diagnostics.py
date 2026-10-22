"""Explain verified slide checks and failed speech chunks without engine details."""

from .slide_quality import MESSAGES

INFORMATIONAL = {'visual_review', 'source_workspace', 'source_language_pair', 'source_motion_position'}
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
            if code in INFORMATIONAL or code in seen:
                continue
            seen.add(code)
            excerpt = issue.get('excerpt', '')
            issues.append(dict(code=code, message=MESSAGES.get(code, 'Cần đối chiếu vùng nội dung này.'),
                               severity=issue.get('severity', 'CHECK'), excerpt=excerpt,
                               action=ACTIONS.get(code, 'Xem slide và đối chiếu với bài gốc.')))
        if issues:
            pages.append(dict(slide=row['slide'], source_slide=row.get('source_slide', row['slide']),
                              failed=any(i['severity'] == 'FAIL' for i in issues), issues=issues))
    pages.sort(key=lambda row: (not row['failed'], row['slide']))
    repairs = report.get('local_repairs', [])
    fixed = {row['slide'] for row in repairs if row.get('slide') and row.get('operation') != 'keep_quantities_together'}
    failures = sum(row['failed'] for row in pages)
    review = (lesson.get('external_deck') or {}).get('content_review') or {}
    image_pages = sorted({n for n in review.get('image_pages', []) if type(n) is int and n > 0})
    image_note = (f"Chữ trong ảnh ở slide nguồn {', '.join(map(str, image_pages[:8]))}{'…' if len(image_pages) > 8 else ''} "
                  'chưa được kiểm tra hết. Hãy đối chiếu chữ, bảng và công thức với bản gốc.'
                  if image_pages else review.get('message', ''))
    return dict(pages=pages, total=len(report.get('slides', [])), repaired=len(fixed), failures=failures,
                remaining=len(pages), has_report=bool(report),
                title='Cần sửa bố cục trước khi dạy' if failures else 'Cần xem lại trước khi dạy',
                image_note=image_note,
                summary=(f'Đã tự căn chỉnh {len(fixed)} slide. ' if fixed else '')
                        + (f'Có {len(pages)} slide cần xem lại' + (f', trong đó {failures} slide còn lỗi bố cục.' if failures else '.')
                           if pages else 'Chưa phát hiện lỗi trong các phép kiểm tra tự động.' if report else 'Chưa có kết quả kiểm tra slide.'))


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
