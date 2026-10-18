"""Explain technical checks separately from the teacher's content confirmation."""

from .readiness import preparation_current


def summarize(lesson):
    segments = lesson.get('segments', [])
    counts = lesson.get('slide_quality', {}).get('counts', {})
    failures = 0 if lesson.get('voice_only') else max(0, int(counts.get('FAIL', 0)))
    if lesson.get('voice_only'):
        segments = [s for s in segments if s.get('vi', '').strip() or s.get('en', '').strip()]
    missing = sum(not ((s.get('vi', '').strip() or s.get('en', '').strip()) if lesson.get('voice_only')
                       else (s.get('vi', '').strip() and s.get('en', '').strip())) for s in segments)
    pending = sum(not s.get('approved') for s in segments)
    result = {'failures': failures, 'missing': missing, 'pending': pending,
              'canInspect': bool(lesson.get('external_deck') and not lesson.get('voice_only')),
              'canRepair': bool(lesson.get('external_deck') and failures and not lesson.get('voice_only')),
              'canConfirm': bool(segments) and not missing and not failures}
    if failures:
        result.update(kind='repair', label='Cần xem lại bố cục',
                      detail=f'{failures} slide có cảnh báo bố cục. Tool tự thử căn chỉnh khi chuyển đổi, mở hoặc tải; có thể xem chi tiết và đối chiếu trong PowerPoint.',
                      action='Xem chi tiết bố cục')
    elif not segments or missing:
        result.update(kind='incomplete', label='Chưa có lời đọc' if lesson.get('voice_only') else 'Chưa dịch đủ',
                      detail='Bổ sung lời đọc trong Tạo giọng đọc bài giảng → Kiểm tra lời đọc.' if lesson.get('voice_only') else 'Bài còn thiếu nội dung Việt–Anh. Mở phần chỉnh sửa để bổ sung hoặc tiếp tục chuyển đổi.',
                      action='Xem nội dung còn thiếu')
    elif pending:
        result.update(kind='confirm', label='Đã lưu bài',
                      detail='Bài đã lưu, có thể mở PowerPoint cùng Mascot. Duyệt nội dung khi muốn dùng câu hỏi và lớp học.',
                      action='Xem và duyệt nội dung')
    elif preparation_current(lesson):
        result.update(kind='ready', label='Sẵn sàng dạy',
                      detail='Nội dung đã xác nhận và bản hiện tại đã chốt để dạy.', action='Xem bản đã chốt')
    else:
        result.update(kind='reviewed', label='Đã duyệt nội dung',
                      detail='Nội dung Việt–Anh đã duyệt. Chọn Dùng để dạy để kiểm tra và chốt bản hiện tại.',
                      action='Chuẩn bị dạy')
    return result
