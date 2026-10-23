"""A teaching binding is independent of the lesson currently being browsed."""

import copy
import hashlib
import shutil
import time
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from . import speech
from .powerpoint import slide_for_locator, slide_segment_indexes
from .reading_progress import ReadingProgress
from .slide_speech import speech_chunks, visible_segments


def prepare_teaching(lesson, preview, directory):
    """Verify the selected product once, without synthesis or source edits."""
    from pptx import Presentation

    from .quick_conversion import verify_preview
    from .slide_speech import deck_speech

    lesson, preview = copy.deepcopy(lesson), dict(preview)
    path = verify_preview(lesson, preview, directory)
    data = lesson.get('slide_speech', {})
    if not lesson.get('voice_only') and data.get('sha256') != preview.get('sha256'):
        data = deck_speech(path, Presentation(path), lesson.get('conversion_format', ''))
    return _prepare_verified_teaching(lesson, preview, directory, path, data)


def prepare_original_teaching(lesson, directory):
    """Bind the verified original without borrowing a converted product's voice."""
    from pptx import Presentation

    from .powerpoint import verified_presentation
    from .slide_speech import deck_speech

    lesson = copy.deepcopy(lesson)
    path = verified_presentation(lesson, directory)
    data = deck_speech(path, Presentation(path))
    lesson.pop('narration', None)
    lesson.pop('narration_variants', None)
    lesson['slide_speech'] = data
    preview = dict(lesson_id=lesson['id'], revision=lesson['revision'], path=str(path),
                   sha256=data['sha256'], total=len(data['slides']), product='original')
    return _prepare_verified_teaching(lesson, preview, directory, path, data)


def _prepare_verified_teaching(lesson, preview, directory, path, data):
    from .lesson_narration import MODES, audio_status
    from .narration_timing import reading_gap
    from .slideshow_controls import speaker_languages

    gap_ms = reading_gap(directory)
    warning = ''
    owned_path = ''
    managed_key = None
    if (lesson.get('narration') or {}).get('mode') in MODES:
        if not audio_status(lesson, directory).get('ready'):
            raise ValueError('Bản giọng chưa hoàn tất. Tạo tiếp hoặc chọn Không kèm giọng đọc.')
        from . import teaching_cache
        from .presentation_audio import embed_audio

        target = Path(directory) / 'temp/teaching' / (uuid4().hex + '.pptx')
        target.parent.mkdir(parents=True, exist_ok=True)
        managed_key = teaching_cache.cache_key(lesson, preview['sha256'], directory, gap_ms=gap_ms)
        cached = teaching_cache.load(directory, managed_key)
        if cached:
            try:
                shutil.copyfile(cached['path'], target)
            except OSError:
                target.unlink(missing_ok=True)
                raise
            return dict(lesson=lesson, preview=preview, path=str(target), speech=data,
                        media=cached['media'], sha256=cached['sha256'], owned_path=str(target), warning=cached['warning'], gap_ms=gap_ms)
        try:
            coverage = embed_audio(path, target, lesson, directory, managed=True, gap_ms=gap_ms)
            path = target
            owned_path = str(target)
            if coverage.get('unplaced_pages'):
                warning = f"{len(coverage['unplaced_pages'])} slide chưa đủ chỗ đặt loa; Mascot dùng giọng đã lưu."
        except ValueError as exc:
            managed_key = None
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
    media = speaker_languages(path)
    with Path(path).open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    prepared = {'lesson': lesson, 'preview': preview, 'path': str(path), 'speech': data,
            'media': media, 'sha256': digest,
            'owned_path': owned_path, 'warning': warning, 'gap_ms': gap_ms}
    if managed_key:
        try:
            teaching_cache.store(directory, managed_key, prepared)
        except OSError:
            pass  # A valid current session does not depend on cache storage.
    return prepared


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
        self._progress = ReadingProgress()
        self._read_batch = []
        self._batch_language = ''
        self._batch_slide = None
        self._cache_generation = None
        from .system_volume import SystemVolume

        self.system_volume = SystemVolume(self)
        self.system_volume.changed.connect(self._sync_system_volume)
        self._player_volume = None
        self._build_key = None
        self._cache_badge = None
        self._deferred_read = None
        self._settled = QTimer(self)
        self._settled.setSingleShot(True)
        self._settled.timeout.connect(self._finish_build)
        getattr(bridge, 'powerpointStateChanged', bridge.changed).connect(self._watch_build)
        getattr(bridge, 'powerpointStateChanged', bridge.changed).connect(self.changed)
        bridge.speechStateChanged.connect(self.changed)
        bridge.speechStateChanged.connect(self._sync_cache_badge)
        if hasattr(bridge.english_reader, 'chunkFinished'):
            bridge.english_reader.chunkFinished.connect(self._cached_chunk_finished)

    @Slot(int)
    def _cached_chunk_finished(self, index):
        if self._cache_generation != getattr(self.bridge.english_reader, 'generation', None):
            return
        if 0 <= index < len(self._read_batch):
            self._progress.finish(self._batch_slide, self._batch_language, [self._read_batch[index]])

    def _sync_cache_badge(self):
        worker = self.bridge.powerpoint_worker
        if not worker or not self.bound or not self.bridge._powerpoint_state.get('active'):
            return
        reading = self.native_state == 'stopped' and self.bridge.englishReaderState.get('state') == 'reading'
        badge = (self.bridge._powerpoint_state.get('slide_id'), self.language if reading else '')
        if badge != self._cache_badge:
            self._cache_badge = badge
            worker.navigate('set_reading_badge', {'slide_id': badge[0], 'language': badge[1]})

    def bind(self, prepared):
        self.bound = copy.deepcopy(prepared)
        self._progress.reset()
        self._player_volume = None
        self._verified_stamp = None
        self._build_key = None
        self.reset_reading()
        self._watch_build()
        self.changed.emit()

    def _watch_build(self):
        state = self.bridge._powerpoint_state
        self._progress.enter(state.get('slide_id') if self.bound else None, state.get('slide'))
        self.system_volume.activate(bool(self.bound and state.get('active')))
        key = (state.get('slide_id'), state.get('click_index'), state.get('build_started'))
        if key != self._build_key:
            self._build_key = key
            self._deferred_read = None
            self._settled.stop()
            page = next((p for p in self.bound.get('speech', {}).get('slides', []) if p['slide'] == state.get('slide')), {})
            animated = any(row.get('visibility', {}).get('kind', 'always') not in {'always', 'hidden'}
                           for row in page.get('englishSpeechSegments', []))
            self.reading_scope = 'visible' if animated else 'full_slide'
            if self.bound and state.get('active') and self.reading_scope == 'visible':
                delay = max((r.get('visibility', {}).get('settle_seconds', 0)
                             for r in page.get('englishSpeechSegments', [])
                             if r.get('visibility', {}).get('show_after') == state.get('click_index')), default=0)
                remaining = delay - max(0, time.monotonic() - state.get('build_started', time.monotonic()))
                if remaining > 0:
                    self._settled.start(round(remaining*1000)+50)

    def _finish_build(self):
        intent, self._deferred_read = self._deferred_read, None
        if intent and intent[1] == self._build_key and self.bridge._powerpoint_state.get('active'):
            self.read(intent[0])
        self.changed.emit()

    def reset_reading(self):
        self._read_batch = []
        self._cache_generation = None
        self.token += 1
        self.pending_read = None
        self._deferred_read = None
        self.native_state = 'stopped'
        self.language = ''
        self.pause_on_start = False
        self.response = {'untouched': True, 'text': ''}
        self.changed.emit()

    def clear(self):
        self.system_volume.shutdown()
        self._progress.reset()
        self._settled.stop()
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
                'reading_mode': 'auto',
                'auto_completed': bool(self._progress.completed.get(self.language))
                                  and not self._selected_items(self.language),
                'settling': self._settled.isActive(),
                'voice': (lesson.get('narration') or {}).get('voice', '')}

    def _speech_items(self, language, *, settled_seconds=None):
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
                   time.monotonic() - state.get('build_started', time.monotonic()) if settled_seconds is None else settled_seconds))
        def chunks(kind, identity, text):
            return [((kind, identity, index), part) for index, part in enumerate(speech_chunks(text))]
        english_items = [part for row in visible for part in chunks('en', row['id'], row['english_text'])]
        english = [part[1] for part in english_items]
        if language == 'en':
            return english_items
        vietnamese = []
        for unit in units:
            parts = chunks('vi', unit['id'], unit.get('vi', ''))
            partner = speech_chunks(unit.get('en', ''))
            if self.reading_scope == 'full_slide':
                vietnamese.extend(parts)
            elif partner and len(partner) == len(parts):
                vietnamese.extend(part for part, en in zip(parts, partner, strict=True) if en in english)
            elif partner and set(partner) <= set(english):
                vietnamese.extend(parts)
        if language == 'vi':
            return vietnamese
        if self.reading_scope == 'full_slide':
            return vietnamese + english_items
        paired, used = [], set()
        for unit in units:
            partner = speech_chunks(unit.get('en', ''))
            if partner and set(partner) <= set(english):
                paired.extend(chunks('vi', unit['id'], unit.get('vi', '')))
                paired.extend(part for part in english_items if part[1] in partner)
                used.update(partner)
            elif (lesson.get('voice_only') or lesson.get('narration_script')) and not partner:
                paired.extend(chunks('vi', unit['id'], unit.get('vi', '')))
        return paired + [part for part in english_items if part[1] not in used]

    def _selected_items(self, language, *, replay=False):
        items = self._speech_items(language)
        if self._settled.isActive():
            return []  # Do not replay old text while a new entrance is settling.
        chosen = self._progress.choose(language, items, titles=self._titles(language))
        return chosen or (items if replay else [])

    def _titles(self, language):
        """Suppress only explicit headings actually read on the preceding page."""
        page = next((p for p in self.bound.get('speech', {}).get('slides', [])
                     if p['slide'] == self.bridge._powerpoint_state.get('slide')), {})
        titles = {part for row in page.get('englishSpeechSegments', []) if row.get('kind') == 'title'
                  for part in speech_chunks(row.get('english_text', ''))}
        if language == 'en':
            return titles
        if language == 'vi':
            from .narration_script import segments

            found = set()
            for unit in segments(self.bound.get('lesson', {})):
                if slide_for_locator(unit.get('locator', '')) != page.get('slide'):
                    continue
                vi, en = speech_chunks(unit.get('vi', '')), speech_chunks(unit.get('en', ''))
                if len(vi) == len(en):
                    found.update(v for v, e in zip(vi, en, strict=True) if e in titles)
            return found
        return set()

    def texts(self, language):
        return [item[1] for item in self._selected_items(language)]

    @Property('QVariantMap', notify=changed)
    def audio(self):
        from .lesson_narration import valid_key

        state = self.bridge._powerpoint_state
        if not self.bound or not state.get('active'):
            return {'vi': False, 'en': False, 'both': False}
        embedded = self.bound.get('media', {}).get(state.get('slide'), []) if self.reading_scope == 'full_slide' else []
        record = self.bound['lesson'].get('narration') or {}
        def available(language):
            if language in embedded and not record.get('keys'):
                return True
            keys = record.get('keys', {}).get(language, [])
            if not keys:
                return False
            # Availability describes this build's verified audio, even during
            # its entrance animation. A click is deferred until the words are
            # visible; it must not make the buttons blink off and on.
            items = self._speech_items(language, settled_seconds=float('inf'))
            texts = [item[1] for item in items]
            voice = speech.voice_for(record.get('voice', ''), language)
            wanted = [speech.audio_key(text, voice, record.get('rate', 0)) for text in texts]
            return bool(texts) and all(key in keys and valid_key(self.bridge.library.directory, key) for key in wanted)
        vi, en = available('vi'), available('en')
        return {'vi': vi, 'en': en, 'both': False}

    @Property('QVariantMap', notify=changed)
    def reader(self):
        if self.native_state != 'stopped':
            return {'state': self.native_state, 'language': self.language, 'volume': self.volume,
                    'message': 'PowerPoint · ' + {'paused': 'Tạm dừng', 'preparing': 'Đang chuẩn bị', 'reading': 'Đang đọc'}[self.native_state]}
        return {**self.bridge.englishReaderState, 'language': self.language, 'volume': self.volume}

    def office_event(self, state):
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
                # A mouse-hook click is consumed before Windows activates the
                # slide. Restore its focus before toggling the shared reader.
                getattr(self.bridge, 'focusTeachingPresentation', lambda: None)()
                if state.get('language') in {'volume_up', 'volume_down'}:
                    self.setVolume(self.volume + (5 if state['language'] == 'volume_up' else -5))
                elif state.get('language') in {'next', 'previous'}:
                    self.bridge.navigatePowerPoint(state['language'])
                else:
                    self.toggleRead(state.get('language', ''))
        elif event == 'input_warning':
            self.bridge.inform(state['message'], True, refresh=False)
        elif event == 'media_stopped' and self.pending_read:
            token, number, slide_id, texts, voice, rate = self.pending_read
            if state.get('token') != token:
                return  # An earlier untagged Stop must not discard a newer cached read.
            self.pending_read = None
            self.native_state = 'stopped'
            if (token == state.get('token') == self.token and number == self.bridge._powerpoint_state.get('slide')
                    and slide_id == self.bridge._powerpoint_state.get('slide_id')):
                self.bridge.english_reader.start(texts, voice, rate, cache_only=True)
                self._cache_generation = getattr(self.bridge.english_reader, 'generation', None)
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
            if event == 'media_finished' and self.native_state in {'reading', 'paused'} and self._cache_generation is None:
                self._progress.finish(self._batch_slide, self._batch_language, self._read_batch)
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
        items = (self._read_batch if self._batch_language == language
                 and self._batch_slide == self.bridge._powerpoint_state.get('slide_id')
                 else self._selected_items(language, replay=True)) if language in {'vi', 'en'} else []
        texts = [item[1] for item in items]
        keys = record.get('keys', {}).get(language, [])
        voice = speech.voice_for(record.get('voice', ''), language)
        wanted = [speech.audio_key(text, voice, record.get('rate', 0)) for text in texts]
        if not texts or not all(key in keys and valid_key(self.bridge.library.directory, key) for key in wanted):
            return False
        self._read_batch = items
        self._batch_language = language
        self._batch_slide = self.bridge._powerpoint_state.get('slide_id')
        self.pending_read = (self.token, self.bridge._powerpoint_state['slide'],
                             self.bridge._powerpoint_state.get('slide_id'), texts, voice, record['rate'])
        self.native_state = 'preparing'
        self.bridge.powerpoint_worker.navigate('stop_media', self._media_request())
        return True

    @Slot(str)
    def read(self, language):
        if language not in {'vi', 'en'} or not self.audio.get(language):
            return
        if self._settled.isActive() and self.reading_scope == 'visible':
            self._deferred_read = (language, self._build_key)
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
        self._read_batch = self._selected_items(language, replay=True)
        self._batch_language = language
        self._batch_slide = self.bridge._powerpoint_state.get('slide_id')
        if hasattr(getattr(self.bridge.english_reader, 'player', None), 'set_volume'):
            self.bridge.english_reader.player.set_volume(100 if self.system_volume.available else self.volume)
        worker = self.bridge.powerpoint_worker
        from .narration_timing import PARAGRAPH_GAP_MS

        timer = getattr(self.bridge.english_reader, 'gap', None)
        cadence_matches = self.bound.get('gap_ms', PARAGRAPH_GAP_MS) == (timer.interval() if timer else PARAGRAPH_GAP_MS)
        if (self.reading_scope == 'full_slide' and self._read_batch == self._speech_items(language)
                and (cadence_matches or not self.bound.get('lesson', {}).get('narration', {}).get('keys'))
                and language in self.bound.get('media', {}).get(self.bridge._powerpoint_state.get('slide'), [])):
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
        if language not in {'vi', 'en'} or not self.bound or not self.bridge._powerpoint_state.get('active'):
            return
        if self._deferred_read:
            # A second press cancels a queued start just as it pauses playback.
            self._deferred_read = None if self._deferred_read[0] == language else (language, self._build_key)
            return
        state = self.native_state if self.native_state != 'stopped' else getattr(self.bridge.english_reader, 'state', 'stopped')
        if self.language == language and state == 'preparing':
            self.pause_on_start = not self.pause_on_start
        elif self.language == language and state in {'reading', 'paused'}:
            self.pauseResume()
        elif not self.audio.get(language):
            self.bridge.inform('Slide này chưa có giọng ' + {'vi': 'tiếng Việt', 'en': 'tiếng Anh', 'both': 'hai ngôn ngữ'}[language] + '. Chọn loa đang có giọng.', refresh=False)
        else:
            self.read(language)

    @Slot(int)
    def setVolume(self, volume):
        if not self.bound or not self.bridge._powerpoint_state.get('active'):
            return
        volume = max(0, min(100, volume))
        if self.system_volume.available:
            self.system_volume.set_value(volume)
            return
        self._set_player_volume(volume)

    def _sync_system_volume(self):
        self.volume = self.system_volume.value
        # The device controls loudness. Keep both playback routes at unity so
        # master volume is not multiplied by a second software attenuation.
        self._set_player_volume(100 if self.system_volume.available else self.volume)

    def _set_player_volume(self, volume):
        try:
            player = getattr(self.bridge.english_reader, 'player', None)
            if hasattr(player, 'set_volume'):
                player.set_volume(volume)
        except Exception:
            self.bridge.inform('Chưa đổi được âm lượng lời đọc. Kiểm tra loa của Windows.', True, refresh=False)
            return
        if not self.system_volume.available:
            self.volume = volume
        if self.bridge.powerpoint_worker and volume != self._player_volume:
            self.bridge.powerpoint_worker.navigate('set_volume', volume)
        self._player_volume = volume
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
