"""Desktop Word workflow, using the existing cancellable job lifecycle."""

import copy

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from . import word_jobs as jobs
from .word_document import utf16_position


class WordDocuments(QObject):
    changed = Signal()
    libraryChanged = Signal()
    draftsChanged = Signal()
    progressed = Signal(object)
    configurationRestored = Signal()
    sourceTextChanged = Signal()
    formattingDefaultsChanged = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._state = dict(id='', phase='empty', regions=[], paragraphs=[], message='', selected_count=0, can_export=False, options={})
        self._library, self._drafts, self._keywords = [], {}, {}
        self._working, self._trash = False, False
        self._formatting_defaults = jobs.formatting_defaults(bridge.library.directory)
        from .word_selection import TextSelection

        self._text_selection, self._text_identity = TextSelection([]), ''
        self._preview = None
        self._preview_document = None
        self._preview_excerpts = {}
        self.progressed.connect(self._progress)

    @Property('QVariantMap', notify=changed)
    def state(self):
        return {**self._state, 'working': self._working}

    @Property('QVariantList', notify=libraryChanged)
    def library(self):
        return self._library

    @Property(bool, notify=draftsChanged)
    def draftsPending(self):
        return bool(self._drafts or self._keywords)

    @Property(str, notify=sourceTextChanged)
    def selectionText(self):
        return self._text_selection.text

    @Property(str, notify=sourceTextChanged)
    def previewHtml(self):
        return self._preview.html if self._preview else ''

    @Property(float, notify=sourceTextChanged)
    def previewPageWidth(self):
        return self._preview.width if self._preview else 794.0

    @Property('QVariantList', notify=sourceTextChanged)
    def previewMargins(self):
        return self._preview.margins if self._preview else [64, 64, 64, 64]

    @Property('QStringList', notify=sourceTextChanged)
    def sourceFonts(self):
        return self._preview.fonts if self._preview else []

    @Property(str, notify=changed)
    def sourceFontSize(self):
        return self._preview.selection_size(self._state.get('regions', [])) if self._preview else ''

    @Property('QStringList', constant=True)
    def fontFamilies(self):
        from PySide6.QtGui import QFontDatabase

        families = [name for name in QFontDatabase.families() if not name.startswith('@') and not QFontDatabase.isPrivateFamily(name)]
        preferred = ['Times New Roman', 'Arial', 'Calibri', 'Aptos', 'Be Vietnam Pro']
        return [name for name in preferred if name in families] + sorted(set(families) - set(preferred), key=str.casefold)

    @Property('QVariantMap', notify=formattingDefaultsChanged)
    def formattingDefaults(self):
        return self._formatting_defaults

    @Slot('QVariantMap')
    def rememberFormatting(self, options):
        if not self.available():
            return
        try:
            self._formatting_defaults = jobs.formatting_defaults(self.bridge.library.directory, options)
            self.formattingDefaultsChanged.emit()
        except (OSError, ValueError, TypeError) as exc:
            self._state['message'] = 'Chưa nhớ được định dạng cho bài mới: ' + str(exc)
            self.changed.emit()

    def available(self):
        return not (self.bridge.busy or self.bridge.narrationBusy or self.bridge.batchQueue.running or self._working)

    @Slot(object)
    def _progress(self, value):
        self._state.update(value)
        self.changed.emit()

    def _launch(self, action, *, clear_drafts=False, navigate=False, restore_configuration=False):
        if not self.available():
            return
        self._working = True
        self.changed.emit()
        directory = self.bridge.library.directory
        prior_text_identity = self._text_identity

        def work():
            try:
                job = action(directory)
                preview, preview_notice = None, ''
                if job and job['id'] != prior_text_identity:
                    try:
                        from .word_document import Package
                        from .word_preview import Preview

                        preview = Preview(Package(jobs.folder_for(directory, job['id']) / 'source.docx'))
                    except Exception:
                        preview_notice = 'Chưa hiện được định dạng gốc; vẫn có thể chọn và dịch ở chế độ văn bản.'
                return dict(job=jobs.public(directory, job) if job else None, preview=preview,
                            preview_notice=preview_notice, library=jobs.catalog(directory, self._trash), error='')
            except Exception as exc:
                return dict(error=str(exc), job=None, library=jobs.catalog(directory, self._trash))

        def finished(result):
            self._working = False
            defaults = jobs.formatting_defaults(directory)
            if defaults != self._formatting_defaults:
                self._formatting_defaults = defaults
                self.formattingDefaultsChanged.emit()
            if result.get('job'):
                self._state = result['job']
                if self._text_identity != self._state['id']:
                    from .word_selection import TextSelection

                    self._text_selection = TextSelection(self._state['paragraphs'])
                    self._text_identity = self._state['id']
                    self._preview = result.get('preview')
                    self._preview_document = None
                    self._preview_excerpts = {}
                    self._state['preview_notice'] = result.get('preview_notice', '')
                    self.sourceTextChanged.emit()
                if clear_drafts:
                    self._drafts.clear()
                    self._keywords.clear()
                    self.draftsChanged.emit()
                if navigate:
                    self.bridge.navigate.emit('word')
            if result.get('error'):
                self._state['message'] = result['error']
            self._library = result.get('library', self._library)
            self.libraryChanged.emit()
            self.changed.emit()
            if result.get('job') and restore_configuration:
                self.configurationRestored.emit()
            self.bridge.inform('', refresh=False)
            self.bridge.googleSettings.refresh()

        self.bridge.launch(work, finished, message='Đang xử lý tài liệu Word…')
        self.bridge.worker.word_task = True

    @Slot(str)
    def openFile(self, url):
        self._open_file(url)

    @Slot(str, 'QVariantMap')
    def openConfiguredFile(self, url, preferences):
        self._open_file(url, copy.deepcopy(preferences))

    def _open_file(self, url, preferences=None):
        parsed = QUrl(url)
        if not parsed.isLocalFile():
            self._state['message'] = 'Chọn tệp Word trên máy tính.'
            self.changed.emit()
            return
        self._launch(lambda directory: jobs.create(directory, parsed.toLocalFile(), preferences=preferences), clear_drafts=True, restore_configuration=True)

    @Slot(str)
    def loadRecord(self, identity):
        self._launch(lambda directory: jobs.read(directory, identity), clear_drafts=True, navigate=True, restore_configuration=True)

    @Slot(bool)
    def refreshLibrary(self, trash=False):
        self._trash = trash
        self._launch(lambda _: None)

    @Slot(str, result='QVariantList')
    def items(self, scope):
        result = []
        for row in self._state.get('paragraphs', []):
            regions = [part for part in self._state['regions'] if part['paragraph'] == row['id']]
            for part in row['sentences'] if scope == 'sentences' else [dict(start=0, end=len(row['text']), text=row['text'])]:
                key, html = (row['id'], part['start'], part['end']), ''
                if self._preview and row['id'] in self._preview.rows:
                    if key not in self._preview_excerpts:
                        self._preview_excerpts[key] = self._preview.excerpt(*key)
                    html = self._preview_excerpts[key].html
                result.append(dict(paragraph=row['id'], start=part['start'], end=part['end'], text=part['text'],
                    html=html,
                    location=row['location'], editable=row['editable'], reason=row['reason'],
                    selected=any(region['start'] <= part['start'] and part['end'] <= region['end'] for region in regions)))
        return result

    def _ranges(self):
        return [{key: row[key] for key in ('paragraph', 'start', 'end')} for row in self._state['regions']]

    @Slot(str, int, int, bool)
    def toggle(self, paragraph, start, end, selected):
        rows = self._ranges()
        if selected:
            rows.append(dict(paragraph=paragraph, start=start, end=end))
        else:
            updated = []
            for row in rows:
                if row['paragraph'] != paragraph or row['end'] <= start or row['start'] >= end:
                    updated.append(row)
                else:
                    if row['start'] < start:
                        updated.append({**row, 'end': start})
                    if row['end'] > end:
                        updated.append({**row, 'start': end})
            rows = updated
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, rows))

    @Slot(str, int, int, int)
    def addRange(self, paragraph, base, start, end):
        try:
            text = next(row['text'] for row in self._state['paragraphs'] if row['id'] == paragraph)[base:]
            self.toggle(paragraph, base + utf16_position(text, start), base + utf16_position(text, end), True)
        except (ValueError, StopIteration) as exc:
            self._state['message'] = str(exc) or 'Chọn lại vùng văn bản.'
            self.changed.emit()

    @Slot(str, int, int)
    def addTextSelection(self, identity, start, end):
        if not self.available():
            return
        try:
            if not identity or identity != self._state['id'] or identity != self._text_identity:
                raise ValueError('Tài liệu đã đổi; bôi đen lại phần cần dịch.')
            selected, skipped = self._text_selection.ranges(start, end)
        except ValueError as exc:
            self._state['message'] = str(exc)
            self.changed.emit()
            return

        self._add_selected_ranges(identity, selected, skipped)

    @Slot(str, str, int, int)
    def addPreviewSelection(self, identity, visible_text, start, end):
        if not self.available():
            return
        try:
            if not identity or identity != self._state['id'] or identity != self._text_identity or not self._preview:
                raise ValueError('Tài liệu đã đổi; bôi đen lại phần cần dịch.')
            from PySide6.QtGui import QTextDocument

            if self._preview_document is None:
                self._preview_document = QTextDocument()
                self._preview_document.setHtml(self._preview.html)
            from .word_preview import qt_text

            if qt_text(visible_text) != qt_text(self._preview_document.toRawText()):
                raise ValueError('Nội dung xem trước đã đổi; tải lại tài liệu rồi chọn lại vùng dịch.')
            selected, skipped = self._preview.ranges(self._preview_document, start, end)
        except (ValueError, AttributeError, RuntimeError) as exc:
            self._state['message'] = str(exc)
            self.changed.emit()
            return
        self._add_selected_ranges(identity, selected, skipped)

    @Slot(str, str, int, int, str, int, int)
    def addPreviewRange(self, identity, paragraph, base, limit, visible_text, start, end):
        if not self.available():
            return
        try:
            from PySide6.QtGui import QTextDocument

            preview = self._preview_excerpts.get((paragraph, base, limit))
            if identity != self._state['id'] or not preview:
                raise ValueError('Tài liệu đã đổi; chọn lại phần cần dịch.')
            document = QTextDocument()
            document.setHtml(preview.html)
            from .word_preview import qt_text

            if qt_text(visible_text) != qt_text(document.toRawText()):
                raise ValueError('Nội dung đã đổi; chọn lại phần văn bản.')
            selected, skipped = preview.ranges(document, start, end)
        except (ValueError, RuntimeError) as exc:
            self._state['message'] = str(exc)
            self.changed.emit()
            return
        self._add_selected_ranges(identity, selected, skipped)

    def _add_selected_ranges(self, identity, selected, skipped):
        rows = [*self._ranges(), *selected]

        def action(directory):
            job = jobs.selections(directory, identity, rows)
            if skipped:
                job['message'] += f' Giữ nguyên {skipped} đoạn chỉ có hình/công thức hoặc đang khóa; các đoạn đó chưa được chọn để dịch.'
            return job

        self._launch(action)

    @Slot(str)
    def removeRange(self, identity):
        rows = [row for row in self._ranges() if f"{row['paragraph']}:{row['start']}:{row['end']}" != identity]
        current = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, current, rows))

    @Slot()
    def clearSelection(self):
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, []), clear_drafts=True)

    @Slot(str)
    def selectAll(self, scope):
        rows = [dict(paragraph=row['paragraph'], start=row['start'], end=row['end']) for row in self.items(scope) if row['editable']]
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, rows))

    @Slot(str, str)
    def setDraft(self, identity, value):
        self._drafts[identity] = value
        self.draftsChanged.emit()

    @Slot(str, int, str)
    def setKeywordDraft(self, identity, index, value):
        self._keywords[(identity, index)] = value
        self.draftsChanged.emit()

    @Slot(str, str, str)
    def addKeyword(self, region_id, vietnamese, english):
        identity = self._state['id']
        drafts, keywords = copy.deepcopy(self._drafts), copy.deepcopy(self._keywords)

        def action(directory):
            self._apply_drafts(directory, identity, drafts, keywords)
            return jobs.add_keyword(directory, identity, region_id, vietnamese, english)

        self._launch(action, clear_drafts=True)

    def _apply_drafts(self, directory, identity, drafts, keywords):
        selected = {row['id'] for row in self._state['regions']}
        for region_id, value in drafts.items():
            if region_id in selected:
                jobs.edit(directory, identity, region_id, value)
        for (region_id, index), value in sorted(keywords.items(), key=lambda row: (row[0][0], -row[0][1])):
            if region_id in selected:
                jobs.edit_keyword(directory, identity, region_id, index, value)

    @Slot('QVariantMap', str, str)
    @Slot('QVariantMap', str, str, str)
    def preview(self, options, subject, grade, title=None):
        identity = self._state['id']
        drafts, keywords = copy.deepcopy(self._drafts), copy.deepcopy(self._keywords)

        def action(directory):
            self._apply_drafts(directory, identity, drafts, keywords)
            return jobs.convert(directory, identity, options, subject, grade, self.bridge.cancel_event, self.progressed.emit, title=title)

        self._launch(action, clear_drafts=True)

    @Slot()
    def save(self):
        identity = self._state['id']
        drafts, keywords = copy.deepcopy(self._drafts), copy.deepcopy(self._keywords)

        def action(directory):
            self._apply_drafts(directory, identity, drafts, keywords)
            return jobs.export(directory, identity, self.bridge.cancel_event)

        self._launch(action, clear_drafts=True)

    @Slot()
    def stop(self):
        if self._working:
            self.bridge.cancel_event.set()
            self._state['message'] = 'Đang dừng; chờ yêu cầu đang gửi kết thúc để giữ kết quả.'
            self.changed.emit()

    @Slot(str)
    def openOutput(self, identity):
        try:
            job = jobs.read(self.bridge.library.directory, identity)
            folder = jobs.folder_for(self.bridge.library.directory, identity)
            path = folder / 'result.docx'
            from .word_document import digest

            if not path.is_file() or digest(path) != job.get('output_sha256'):
                raise ValueError('Bản xuất đã thay đổi hoặc chưa có; mở bài và lưu lại Word.')
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        except (OSError, ValueError) as exc:
            self._state['message'] = str(exc)
            self.changed.emit()

    @Slot(str)
    def openFolder(self, identity):
        folder = jobs.folder_for(self.bridge.library.directory, identity)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    @Slot(str, bool)
    def trash(self, identity, deleted):
        self._launch(lambda directory: jobs.trash(directory, identity, deleted))

    @Slot()
    def restorePrevious(self):
        identity = self._state['id']
        self._launch(lambda directory: jobs.restore_previous(directory, identity), clear_drafts=True, restore_configuration=True)
