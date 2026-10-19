"""One no-I/O summary of independent saved, review, audio and teaching states."""

from .lesson_review import summarize
from .readiness import preparation_current


def summarize_state(lesson, audio=None):
    review = summarize(lesson)
    audio = audio or {}
    confirmed = bool(review['canConfirm'] and not review['pending'])
    complete, total = audio.get('complete', 0), audio.get('total', 0)
    return dict(saved=bool(lesson.get('id')), review=review, content_ready=confirmed,
                audio_ready=bool(audio.get('ready')), audio_complete=complete, audio_total=total,
                audio_label=(f'Giọng {complete}/{total} đoạn' if total else
                             'Đang kiểm tra giọng' if audio.get('status') == 'checking' else 'Chưa tạo giọng'),
                prepared=confirmed and preparation_current(lesson))
