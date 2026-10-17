"""Explain technical checks separately from the teacher's content confirmation."""

from .readiness import preparation_current


def summarize(lesson):
    segments = lesson.get('segments', [])
    counts = lesson.get('slide_quality', {}).get('counts', {})
    failures = max(0, int(counts.get('FAIL', 0)))
    missing = sum(not ((s.get('vi', '').strip() or s.get('en', '').strip()) if lesson.get('voice_only')
                       else (s.get('vi', '').strip() and s.get('en', '').strip())) for s in segments)
    pending = sum(not s.get('approved') for s in segments)
    result = {'failures': failures, 'missing': missing, 'pending': pending,
              'canInspect': bool(lesson.get('external_deck')),
              'canRepair': bool(lesson.get('external_deck') and failures),
              'canConfirm': bool(segments) and not missing and not failures}
    if failures:
        result.update(kind='repair', label=f'{failures} slide cần sửa',
                      detail=f'Kiểm tra kỹ thuật phát hiện {failures} slide còn lỗi. Bấm Kiểm tra lại để cập nhật chi tiết, hoặc thử Tự sửa và kiểm tra.',
                      action='Xem lỗi và tự sửa')
    elif not segments or missing:
        result.update(kind='incomplete', label='Chưa dịch đủ',
                      detail='Bài còn thiếu nội dung Việt–Anh. Mở phần chỉnh sửa để bổ sung hoặc tiếp tục chuyển đổi.',
                      action='Xem nội dung còn thiếu')
    elif pending:
        result.update(kind='confirm', label='Chờ xác nhận',
                      detail=f'Còn {pending}/{len(segments)} phần chưa được thầy cô xác nhận. Xem lại bản dịch, thuật ngữ, số liệu và bố cục; không cần duyệt từng phần nếu đã kiểm tra cả bài.',
                      action='Xem và xác nhận')
    elif preparation_current(lesson):
        result.update(kind='ready', label='Sẵn sàng dạy',
                      detail='Nội dung đã xác nhận và bản hiện tại đã chốt để dạy.', action='Xem bản đã chốt')
    else:
        result.update(kind='reviewed', label='Đã duyệt nội dung',
                      detail='Nội dung Việt–Anh đã duyệt. Chọn Dùng để dạy để kiểm tra và chốt bản hiện tại.',
                      action='Chuẩn bị dạy')
    return result
