"""A teaching binding is independent of the lesson currently being browsed."""

import copy
import hashlib
import time
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Property, QObject, Signal, Slot

from . import speech
from .powerpoint import slide_segment_indexes
from .slide_speech import speech_chunks, visible_segments


def prepare_teaching(lesson, preview, directory):
    """Verify the selected product once, without synthesis or source edits."""
    from pptx import Presentation

    from .lesson_narration import MODES, audio_status
    from .quick_conversion import verify_preview
    from .slide_speech import deck_speech

    lesson, preview = copy.deepcopy(lesson), dict(preview)
    path = verify_preview(lesson, preview, directory)
    data = lesson.get('slide_speech', {})
    if not lesson.get('voice_only') and data.get('sha256') != preview['sha256']:
        data = deck_speech(path, Presentation(path), lesson.get('conversion_format', ''))
    warning = ''
    owned_path = ''
    if (lesson.get('narration') or {}).get('mode') in MODES:
        if not audio_status(lesson, directory).get('ready'):
            raise ValueError('Bản giọng chưa hoàn tất. Tạo tiếp hoặc chọn Không kèm giọng đọc.')
        from .presentation_audio import embed_audio

        target = Path(directory) / 'temp/teaching' / (uuid4().hex + '.pptx')
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            coverage = embed_audio(path, target, lesson, directory)
            path = target
            owned_path = str(target)
            if coverage.get('unplaced_pages'):
                warning = f"{len(coverage['unplaced_pages'])} slide chưa đủ chỗ đặt loa; Mascot dùng giọng đã lưu."
        except ValueError as exc:
            target.unlink(missing_ok=True)
            warning = str(exc) + ' Mascot vẫn dùng giọng đã lưu; bản gốc không thay đổi.'
    media = {}
    for index, slide in enumerate(Presentation(path).slides, 1):
        languages = [shape.name.rsplit(' ', 1)[-1].lower() for shape in slide.shapes
                     if shape.name.startswith('BiliClass audio ') and shape.element.xpath('.//a:audioFile')]
        media[index] = [lang for lang in languages if lang in {'vi', 'en', 'both'}]
    return {'lesson': lesson, 'preview': preview, 'path': str(path), 'speech': data,
            'media': media, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'owned_path': owned_path, 'warning': warning}


class TeachingSession(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.bound = {}
        self.response = {'untouched': True, 'text': ''}
        self.pending_read = None
        self.token = 0
        self.native_state = 'stopped'
        self.reading_scope = 'full_slide'
        bridge.changed.connect(self.changed)
        bridge.speechStateChanged.connect(self.changed)

    def bind(self, prepared):
        self.bound = copy.deepcopy(prepared)
        self.reading_scope = 'full_slide'
        self.reset_reading()

    @Slot(str)
    def setReadingScope(self, scope):
        if scope in {'full_slide', 'visible'} and scope != self.reading_scope:
            self.stop()
            self.reading_scope = scope
            self.changed.emit()

    def reset_reading(self):
        self.token += 1
        self.pending_read = None
        self.native_state = 'stopped'
        self.response = {'untouched': True, 'text': ''}
        self.changed.emit()

    def clear(self):
        owned = self.bound.get('owned_path')
        if owned:
            path = Path(owned).resolve()
            parent = (self.bridge.library.directory / 'temp/teaching').resolve()
            if path.parent == parent:
                try:
                    path.unlink(missing_ok=True)  # Only the exact session copy after Office has closed it.
                except OSError:
                    pass  # Office may still be releasing its handle; the personal source is never removed.
        self.bound = {}
        self.reset_reading()

    @Property('QVariantMap', notify=changed)
    def state(self):
        state = self.bridge._powerpoint_state
        lesson = self.bound.get('lesson', {})
        return {**state, 'bound': bool(lesson), 'lesson_id': lesson.get('id', ''),
                'title': lesson.get('title', ''), 'response': self.response,
                'warning': self.bound.get('warning', ''),
                'reading_scope': self.reading_scope,
                'can_choose_scope': bool(lesson.get('narration', {}).get('keys')),
                'voice': (lesson.get('narration') or {}).get('voice', '')}

    def texts(self, language):
        lesson = self.bound.get('lesson', {})
        state = self.bridge._powerpoint_state
        preview = self.bound.get('preview', {})
        number = state.get('slide', 0)
        indexes = slide_segment_indexes(lesson, number, preview.get('slide_map', []), preview.get('segment_map', []))
        from .narration_script import segments as narration_segments

        spoken = narration_segments(lesson)
        units = [spoken[i] for i in indexes]
        page = next((row for row in self.bound.get('speech', {}).get('slides', []) if row['slide'] == number), {})
        visible = ([row for row in page.get('englishSpeechSegments', []) if row['status'] == 'ready']
                   if self.reading_scope == 'full_slide' else visible_segments(page, state.get('click_index'),
                   time.monotonic() - state.get('build_started', time.monotonic())))
        english = [part for row in visible
                   for part in speech_chunks(row['english_text'])]
        if language == 'en':
            return english
        vietnamese = [part for unit in units if self.reading_scope == 'full_slide' or lesson.get('voice_only') or lesson.get('narration_script') or
                      (speech_chunks(unit.get('en', '')) and set(speech_chunks(unit['en'])) <= set(english))
                      for part in speech_chunks(unit.get('vi', ''))]
        if language == 'vi':
            return vietnamese
        if self.reading_scope == 'full_slide':
            return vietnamese + english
        paired, used = [], set()
        for unit in units:
            partner = speech_chunks(unit.get('en', ''))
            if partner and set(partner) <= set(english):
                paired.extend(speech_chunks(unit.get('vi', '')))
                paired.extend(partner)
                used.update(partner)
            elif (lesson.get('voice_only') or lesson.get('narration_script')) and not partner:
                paired.extend(speech_chunks(unit.get('vi', '')))
        return paired + [part for part in english if part not in used]

    @Property('QVariantMap', notify=changed)
    def audio(self):
        from .lesson_narration import valid_key

        state = self.bridge._powerpoint_state
        if not self.bound or not state.get('active'):
            return {'vi': False, 'en': False, 'both': False}
        embedded = self.bound.get('media', {}).get(state.get('slide'), []) if self.reading_scope == 'full_slide' else []
        record = self.bound['lesson'].get('narration') or {}
        def available(language):
            if language in embedded:
                return True
            texts = self.texts(language)
            keys = record.get('keys', {}).get(language, [])
            wanted = [speech.audio_key(text, record.get('voice', ''), record.get('rate', 0)) for text in texts]
            return bool(texts) and all(key in keys and valid_key(self.bridge.library.directory, key) for key in wanted)
        vi, en = available('vi'), available('en')
        return {'vi': vi, 'en': en, 'both': 'both' in embedded or (vi and en and record.get('mode') == 'both')}

    @Property('QVariantMap', notify=changed)
    def reader(self):
        if self.native_state != 'stopped':
            return {'state': self.native_state, 'message': 'PowerPoint · ' + ('Tạm dừng' if self.native_state == 'paused' else 'Đang đọc')}
        return self.bridge.englishReaderState

    def event(self, state):
        event = state['event']
        if event == 'media_stopped' and self.pending_read:
            token, number, texts, voice, rate = self.pending_read
            self.pending_read = None
            if token == state.get('token') == self.token and number == self.bridge._powerpoint_state.get('slide'):
                self.bridge.english_reader.start(texts, voice, rate, cache_only=True)
        elif event == 'media_started':
            self.token += 1
            self.pending_read = None
            self.bridge.stopSpeech()
            self.native_state = 'reading'
        elif event in {'media_paused', 'media_resumed', 'media_finished'}:
            self.native_state = {'media_paused': 'paused', 'media_resumed': 'reading', 'media_finished': 'stopped'}[event]
        elif event == 'media_error':
            self.native_state = 'stopped'
            self.bridge.inform(state['message'], True, refresh=False)
        self.changed.emit()

    @Slot(str)
    def read(self, language):
        if language not in {'vi', 'en', 'both'} or not self.audio.get(language):
            return
        path = Path(self.bound['path'])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != self.bound['sha256']:
            self.bridge.inform('PowerPoint đã thay đổi. Chọn lại bài để gắn đúng lời đọc.', True, refresh=False)
            return
        self.bridge.stopSpeech()
        self.reset_reading()
        self.bridge._companion_language = language
        worker = self.bridge.powerpoint_worker
        if self.reading_scope == 'full_slide' and language in self.bound.get('media', {}).get(self.bridge._powerpoint_state.get('slide'), []):
            worker.navigate('play_media', language)
        else:
            record = self.bound['lesson'].get('narration') or {}
            self.token += 1
            self.pending_read = (self.token, self.bridge._powerpoint_state['slide'], self.texts(language),
                                 record['voice'], record['rate'])
            worker.navigate('stop_media', self.token)

    @Slot()
    def stop(self):
        self.reset_reading()
        self.bridge.stopSpeech()
        if self.bridge.powerpoint_worker:
            self.bridge.powerpoint_worker.navigate('stop_media')

    @Slot()
    def pauseResume(self):
        if self.native_state != 'stopped' and self.bridge.powerpoint_worker:
            self.bridge.powerpoint_worker.navigate('resume_media' if self.native_state == 'paused' else 'pause_media')
        elif self.bridge.english_reader.state == 'paused':
            self.bridge.resumeEnglish()
        else:
            self.bridge.pauseEnglish()

    @Slot(str, str)
    def ask(self, action, language):
        from .content import assistant_response

        if not self.bridge._powerpoint_state.get('active') or not self.bound:
            return
        preview, lesson = self.bound['preview'], self.bound['lesson']
        indexes = slide_segment_indexes(lesson, self.bridge._powerpoint_state['slide'],
                                        preview.get('slide_map', []), preview.get('segment_map', []))
        if indexes:
            self.response = assistant_response(lesson['segments'][indexes[0]], action, language, lesson.get('level', 2))
            self.changed.emit()
