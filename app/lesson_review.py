"""Explain technical checks separately from the teacher's content confirmation."""

from .readiness import preparation_current


def summarize(lesson):
    segments = lesson.get('segments', [])
    if lesson.get('external_deck'):
        # A blank/media-only page has no missing translation to supply.
        segments = [s for s in segments if s.get('vi', '').strip() or s.get('en', '').strip()]
    counts = lesson.get('slide_quality', {}).get('counts', {})
    failures = 0 if lesson.get('voice_only') else max(0, int(counts.get('FAIL', 0)))
    if lesson.get('voice_only'):
        segments = [s for s in segments if s.get('vi', '').strip() or s.get('en', '').strip()]
    missing = sum(not ((s.get('vi', '').strip() or s.get('en', '').strip()) if lesson.get('voice_only')
                       else (s.get('vi', '').strip() and s.get('en', '').strip())) for s in segments)
    pending = sum(not s.get('approved') for s in segments)
    image_review = lesson.get('external_deck', {}).get('content_review', {})
    unverified_images = image_review.get('coverage') == 'unverified'
    result = {'failures': failures, 'missing': missing, 'pending': pending,
              'canInspect': bool(lesson.get('external_deck') and not lesson.get('voice_only')),
              'canRepair': bool(lesson.get('external_deck') and failures and not lesson.get('voice_only')),
              'canConfirm': bool(segments) and not missing and not failures and not unverified_images}
    if failures:
        result.update(kind='repair', label='Đã lưu bài',
                      detail='BiliClass tự căn chỉnh và kiểm tra bố cục khi chuyển đổi, mở hoặc tải bài giảng.',
                      action='Xem bài giảng')
    elif not segments or missing or unverified_images:
        result.update(kind='incomplete', label='Chưa có lời đọc' if lesson.get('voice_only') else 'Chưa dịch đủ',
                      detail=image_review.get('message', 'Chưa xác minh đủ nội dung trong ảnh.') if unverified_images else 'Bổ sung lời đọc trong Tạo giọng đọc bài giảng → Kiểm tra lời đọc.' if lesson.get('voice_only') else 'Bài còn thiếu nội dung Việt–Anh. Mở phần chỉnh sửa để bổ sung hoặc tiếp tục chuyển đổi.',
                      action='Xem nội dung còn thiếu')
    elif pending:
        result.update(kind='confirm', label='Sẵn sàng trình chiếu' if lesson.get('external_deck') else 'Đã lưu bài',
                      detail='Có thể mở PowerPoint cùng Mascot. Xác nhận nội dung dành cho câu hỏi và lớp học; không bắt buộc để trình chiếu.',
                      action='Xem và duyệt nội dung')
    elif preparation_current(lesson):
        result.update(kind='ready', label='Sẵn sàng dạy',
                      detail='Nội dung đã xác nhận và bản hiện tại đã chốt để dạy.', action='Xem bản đã chốt')
    else:
        result.update(kind='reviewed', label='Đã duyệt nội dung',
                      detail='Nội dung Việt–Anh đã duyệt. Chọn Dùng để dạy để kiểm tra và chốt bản hiện tại.',
                      action='Chuẩn bị dạy')
    return result
