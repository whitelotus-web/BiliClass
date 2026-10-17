"""Source selection and explicit per-slide narration controls for the voice workspace."""

from PySide6.QtCore import Property, QObject, Signal, Slot


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
        rows = lesson.get('segments', [])
        counts = {lang: sum(bool(s.get(lang, '').strip()) for s in rows) for lang in ('vi', 'en')}
        return {'total': len(rows), **counts, 'editable': bool(lesson.get('voice_only')),
                'empty': sum(not s.get('vi', '').strip() and not s.get('en', '').strip() for s in rows),
                'name': (lesson.get('source') or {}).get('original_name', lesson.get('title', '')),
                'slides': [{'id': s['id'], 'label': s.get('locator', str(i + 1)) + (
                    ' · chưa có lời đọc' if not s['vi'].strip() and not s['en'].strip() else '')}
                    for i, s in enumerate(rows)]}

    @Property('QVariantMap', notify=changed)
    def slide(self):
        rows = self.bridge._lesson.get('segments', [])
        self.index = max(0, min(self.index, len(rows) - 1))
        return {**rows[self.index], 'index': self.index,
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
