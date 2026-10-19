"""A teaching binding is independent of the lesson currently being browsed."""

import copy
import hashlib
import shutil
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
    if not owned_path:
        # Office holds even a read-only deck open on Windows. Keep generated
        # previews/source files free for re-export and give each binding its
        # own presentation, including products without narration.
        target = Path(directory) / 'temp/teaching' / (uuid4().hex + '.pptx')
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(path, target)
        except OSError:
            target.unlink(missing_ok=True)
            raise
        path, owned_path = target, str(target)
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
        self.language = ''
        self.pause_on_start = False
        self.reading_scope = 'full_slide'
        self.volume = 80
        bridge.changed.connect(self.changed)
        bridge.speechStateChanged.connect(self.changed)

    def bind(self, prepared):
        self.bound = copy.deepcopy(prepared)
        self._verified_stamp = None
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
        self.language = ''
        self.pause_on_start = False
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
            return {'state': self.native_state, 'language': self.language, 'volume': self.volume,
                    'message': 'PowerPoint · ' + {'paused': 'Tạm dừng', 'preparing': 'Đang chuẩn bị', 'reading': 'Đang đọc'}[self.native_state]}
        return {**self.bridge.englishReaderState, 'language': self.language, 'volume': self.volume}

    def event(self, state):
        event = state['event']
        if event == 'media_rejected':
            if state.get('token') == self.token:
                self.reset_reading()
            return
        if event.startswith('media_'):
            if ('slide_id' in state and state['slide_id'] != self.bridge._powerpoint_state.get('slide_id')):
                return
            if state.get('token') is not None and state['token'] != self.token:
                return
        if event == 'read_requested':
            if state.get('slide_id') == self.bridge._powerpoint_state.get('slide_id') and self.bound:
                if state.get('language') in {'volume_up', 'volume_down'}:
                    self.setVolume(self.volume + (5 if state['language'] == 'volume_up' else -5))
                else:
                    self.toggleRead(state.get('language', ''))
        elif event == 'input_warning':
            self.bridge.inform(state['message'], True, refresh=False)
        elif event == 'media_stopped' and self.pending_read:
            token, number, slide_id, texts, voice, rate = self.pending_read
            self.pending_read = None
            self.native_state = 'stopped'
            if (token == state.get('token') == self.token and number == self.bridge._powerpoint_state.get('slide')
                    and slide_id == self.bridge._powerpoint_state.get('slide_id')):
                self.bridge.english_reader.start(texts, voice, rate, cache_only=True)
                if self.pause_on_start:
                    self.pause_on_start = False
                    self.bridge.pauseEnglish()
        elif event == 'media_started':
            self.pending_read = None
            self.bridge.stopSpeech()
            self.native_state = 'reading'
            self.language = state.get('language', self.language)
            if self.pause_on_start and self.bridge.powerpoint_worker:
                self.pause_on_start = False
                self.bridge.powerpoint_worker.navigate('pause_media', self._media_request())
        elif event in {'media_paused', 'media_resumed', 'media_finished'}:
            self.native_state = {'media_paused': 'paused', 'media_resumed': 'reading', 'media_finished': 'stopped'}[event]
        elif event == 'media_error':
            self.native_state = 'stopped'
            if state.get('operation') != 'play_media' or not self._read_cached(state.get('language', '')):
                self.pause_on_start = False
                self.bridge.inform(state['message'], True, refresh=False)
        self.changed.emit()

    def _media_request(self):
        return {'language': self.language, 'slide_id': self.bridge._powerpoint_state.get('slide_id'), 'token': self.token}

    def _read_cached(self, language):
        from .lesson_narration import valid_key

        record = self.bound.get('lesson', {}).get('narration') or {}
        texts = self.texts(language) if language in {'vi', 'en', 'both'} else []
        keys = record.get('keys', {}).get(language, [])
        if language == 'both' and record.get('mode') == 'both':
            keys = [key for lang in ('vi', 'en') for key in record.get('keys', {}).get(lang, [])]
        wanted = [speech.audio_key(text, record.get('voice', ''), record.get('rate', 0)) for text in texts]
        if not texts or not all(key in keys and valid_key(self.bridge.library.directory, key) for key in wanted):
            return False
        self.pending_read = (self.token, self.bridge._powerpoint_state['slide'],
                             self.bridge._powerpoint_state.get('slide_id'), texts, record['voice'], record['rate'])
        self.native_state = 'preparing'
        self.bridge.powerpoint_worker.navigate('stop_media', self._media_request())
        return True

    @Slot(str)
    def read(self, language):
        if language not in {'vi', 'en', 'both'} or not self.audio.get(language):
            return
        path = Path(self.bound['path'])
        stamp = self._file_stamp(path)
        try:
            verified = stamp is not None and (stamp == self._verified_stamp or
                       hashlib.sha256(path.read_bytes()).hexdigest() == self.bound['sha256'])
        except OSError:
            verified = False
        if not verified:
            self.bridge.inform('PowerPoint đã thay đổi. Chọn lại bài để gắn đúng lời đọc.', True, refresh=False)
            return
        self._verified_stamp = stamp
        self.bridge.stopSpeech()
        self.reset_reading()
        self.bridge._companion_language = language
        self.language = language
        if hasattr(getattr(self.bridge.english_reader, 'player', None), 'set_volume'):
            self.bridge.english_reader.player.set_volume(self.volume)
        worker = self.bridge.powerpoint_worker
        if self.reading_scope == 'full_slide' and language in self.bound.get('media', {}).get(self.bridge._powerpoint_state.get('slide'), []):
            self.native_state = 'preparing'
            worker.navigate('play_media', self._media_request())
        else:
            self._read_cached(language)
        self.changed.emit()

    @staticmethod
    def _file_stamp(path):
        try:
            info = path.stat()
            return info.st_size, info.st_mtime_ns, info.st_ctime_ns
        except OSError:
            return None

    @Slot(str)
    def toggleRead(self, language):
        if language not in {'vi', 'en', 'both'} or not self.bound or not self.bridge._powerpoint_state.get('active'):
            return
        if not self.audio.get(language):
            self.bridge.inform('Slide này chưa có giọng ' + {'vi': 'tiếng Việt', 'en': 'tiếng Anh', 'both': 'hai ngôn ngữ'}[language] + '. Chọn loa đang có giọng.', refresh=False)
            return
        state = self.native_state if self.native_state != 'stopped' else getattr(self.bridge.english_reader, 'state', 'stopped')
        if self.language == language and state == 'preparing':
            self.pause_on_start = not self.pause_on_start
        elif self.language == language and state in {'reading', 'paused'}:
            self.pauseResume()
        else:
            self.read(language)

    @Slot(int)
    def setVolume(self, volume):
        if not self.bound or not self.bridge._powerpoint_state.get('active'):
            return
        volume = max(0, min(100, volume))
        try:
            player = getattr(self.bridge.english_reader, 'player', None)
            if hasattr(player, 'set_volume'):
                player.set_volume(volume)
        except Exception:
            self.bridge.inform('Chưa đổi được âm lượng lời đọc. Kiểm tra loa của Windows.', True, refresh=False)
            return
        self.volume = volume
        if self.bridge.powerpoint_worker:
            self.bridge.powerpoint_worker.navigate('set_volume', volume)
        self.changed.emit()

    @Slot()
    def stop(self):
        self.reset_reading()
        self.bridge.stopSpeech()
        if self.bridge.powerpoint_worker:
            self.bridge.powerpoint_worker.navigate('stop_media')

    @Slot()
    def pauseResume(self):
        if self.native_state != 'stopped' and self.bridge.powerpoint_worker:
            self.bridge.powerpoint_worker.navigate('resume_media' if self.native_state == 'paused' else 'pause_media', self._media_request())
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
