"""Source selection and explicit per-slide narration controls for the voice workspace."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from .narration_script import segments as narration_segments


class NarrationWorkspace(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.index = 0
        self.identity = ''
        bridge.selectionChanged.connect(self._selection)

    def _selection(self):
        identity = self.bridge._lesson.get('id', '')
        if identity != self.identity:
            self.identity, self.index = identity, 0
        self.changed.emit()

    @Property('QVariantMap', notify=changed)
    def summary(self):
        lesson = self.bridge._lesson
        rows = narration_segments(lesson)
        counts = {lang: sum(bool(s.get(lang, '').strip()) for s in rows) for lang in ('vi', 'en')}
        return {'total': len(rows), **counts, 'editable': bool(lesson.get('external_deck')),
                'eligible': sum(not s.get('silent') for s in rows),
                'silent': sum(bool(s.get('silent')) for s in rows),
                'uncertain': sum(s['classification']['needs_review'] for s in rows),
                'empty': sum(not s.get('silent') and not s.get('vi', '').strip() and not s.get('en', '').strip() for s in rows),
                'name': (lesson.get('source') or {}).get('original_name', lesson.get('title', '')),
                'slides': [{'id': s['id'], 'label': s.get('locator', str(i + 1)) + (
                    ' · không đọc' if s.get('silent') else ' · chưa có lời đọc' if not s['vi'].strip() and not s['en'].strip() else '')}
                    for i, s in enumerate(rows)]}

    @Property('QVariantMap', notify=changed)
    def slide(self):
        rows = narration_segments(self.bridge._lesson)
        self.index = max(0, min(self.index, len(rows) - 1))
        return {**rows[self.index], 'vi': rows[self.index].get('original_vi', rows[self.index]['vi']),
                'en': rows[self.index].get('original_en', rows[self.index]['en']), 'index': self.index,
                'revision': self.bridge._lesson['revision']} if rows else {}

    def available(self):
        bridge = self.bridge
        if bridge.busy or bridge.narrationBusy or bridge.powerpoint_worker or bridge.classroom.running:
            bridge.inform('Dừng tạo giọng, trình chiếu hoặc tiết học trước khi đổi bài hay lời đọc.', True, refresh=False)
            return False
        return True

    @Slot(str)
    def selectLibrary(self, identity):
        if not self.available():
            return
        from .voice_import import prepare_library_lesson

        bridge = self.bridge
        directory, profile = bridge.library.directory, dict(bridge.settings)
        bridge.launch(lambda: prepare_library_lesson(directory, identity, profile),
                      lambda result: bridge._show_lesson(*result, auto_repair=False))

    @Slot(int)
    def selectSlide(self, index):
        self.index = index
        self.changed.emit()

    @Slot(str)
    def selectProblem(self, mode):
        wanted = ('vi', 'en') if mode == 'both' else (mode,)
        rows = narration_segments(self.bridge._lesson)
        self.index = next((i for i, row in enumerate(rows) if not row.get('silent') and
                           any(not row.get(lang, '').strip() for lang in wanted)), 0)
        self.changed.emit()

    @Slot(str, bool, int, result=bool)
    def setSilent(self, segment_id, silent, revision):
        if not self.available():
            return False
        from .chatgpt_handoff import external_preview
        from .voice_import import save_script

        bridge = self.bridge
        row = next((s for s in narration_segments(bridge._lesson) if s['id'] == segment_id), None)
        if row is None:
            return False
        try:
            lesson = save_script(bridge.library, bridge._lesson['id'], segment_id, revision,
                                 row['original_vi'], row['original_en'], silent=silent)
            bridge._show_lesson(lesson, external_preview(lesson, bridge.library.directory))
            return True
        except (ValueError, OSError) as exc:
            bridge.inform(str(exc), True, refresh=False)
            return False

    @Slot(str, str, str, int, result=bool)
    def save(self, segment_id, vi, en, revision):
        if not self.available():
            return False
        from .chatgpt_handoff import external_preview
        from .voice_import import save_script

        bridge = self.bridge
        try:
            bridge.stopSpeech()
            lesson = save_script(bridge.library, bridge._lesson['id'], segment_id, revision, vi, en)
            preview = external_preview(lesson, bridge.library.directory)
            bridge._show_lesson(lesson, preview)
            bridge.inform('Đã lưu lời đọc riêng. Slide gốc giữ nguyên; tạo lại bản giọng cho nội dung vừa sửa.')
            return True
        except (ValueError, OSError) as exc:
            bridge.inform(str(exc), True, refresh=False)
            return False

    @Slot(str, str, int)
    def preview(self, language, voice, rate):
        text = self.slide.get(language, '').strip()
        if text:
            self.bridge.previewMultilingualVoice(voice, rate, text[:250])
        else:
            self.bridge.inform('Slide này chưa có lời đọc cho ngôn ngữ đã chọn.', True, refresh=False)

    @Slot(str)
    def exportAudio(self, url):
        if not self.available():
            return
        from PySide6.QtCore import QUrl

        from .narration_audio_export import export_audio

        bridge = self.bridge
        lesson, directory = dict(bridge._lesson), bridge.library.directory
        bridge.rememberExportDirectory(url)
        bridge.launch(lambda: export_audio(lesson, directory, QUrl(url).toLocalFile()),
                      lambda path: bridge.inform('Đã lưu audio theo slide và lời đọc: ' + str(path)))
