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
    readingThemeChanged = Signal()
    workspaceReset = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._state = dict(id='', phase='empty', regions=[], paragraphs=[], message='', selected_count=0, can_export=False, options={})
        self._library, self._drafts, self._keywords = [], {}, {}
        self._working, self._trash = False, False
        self._attention = ''
        self._formatting_defaults = jobs.formatting_defaults(bridge.library.directory)
        self._reading_theme = jobs.reading_theme(bridge.library.directory)
        self._reading_documents = {}
        from .word_selection import TextSelection

        self._text_selection, self._text_identity = TextSelection([]), ''
        self._preview = None
        self._preview_document = None
        self._preview_excerpts = {}
        self._font_families = None
        self._highlighter = self._highlight_document = self._highlight_wrapper = None
        self._highlight_identity = ''
        self._groups_cache = (None, None, [])
        self.progressed.connect(self._progress)
        from .word_batch_ui import WordBatch

        self._batch = WordBatch(self)

    @Property(QObject, constant=True)
    def batch(self):
        return self._batch

    @Property('QVariantMap', notify=changed)
    def state(self):
        attention = self._attention or self._state.get('preview_notice', '')
        if not attention and self._state.get('phase') == 'paused':
            attention = self._state.get('message', '')
        groups = self.reviewGroups
        # Keep paragraph/sentence data in the selection model rather than
        # copying the whole document into QML on every status change.
        return {**{key: value for key, value in self._state.items() if key != 'paragraphs'},
                'working': self._working, 'attention_message': attention, 'group_count': len(groups)}

    @Property('QVariantList', notify=changed)
    def reviewGroups(self):
        paragraphs, regions = self._state.get('paragraphs', []), self._state.get('regions', [])
        if self._groups_cache[0] is not paragraphs or self._groups_cache[1] is not regions:
            from .word_selection import review_groups

            self._groups_cache = (paragraphs, regions, review_groups(paragraphs, regions))
        return self._groups_cache[2]

    @Slot(str)
    def removeGroup(self, identity):
        group = next((row for row in self.reviewGroups if row['id'] == identity), None)
        if not group:
            return
        removed = {row['id'] for row in group['members']}
        rows = [{key: row[key] for key in ('paragraph', 'start', 'end')} for row in self._state['regions'] if row['id'] not in removed]
        current = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, current, rows), selection_only=True)

    @Slot(str, result=int)
    def rangePosition(self, identity):
        region = next((row for row in self._state['regions'] if row['id'] == identity), None)
        if not region or not self._highlight_document:
            return -1
        if self._preview:
            positions = self._preview.selected_positions(self._highlight_document, [region])
            return positions[0][0] if positions else -1
        from .word_preview import length, normalized

        for left, _, row, _ in self._text_selection.spans:
            if row['id'] == region['paragraph']:
                return length(self._text_selection.text[:left]) + length(normalized(row['text'][:region['start']]))
        return -1

    @Slot(str, result='QVariantMap')
    def rangeLocation(self, identity):
        group = next((row for row in self.reviewGroups if row['id'] == identity), None)
        if not group:
            return {}
        regions = group['members']
        positions = []
        if self._preview and self._highlight_document:
            positions = self._preview.selected_positions(self._highlight_document, regions)
        elif not self._preview:
            from .word_preview import length, normalized

            for left, _, row, _ in self._text_selection.spans:
                base = length(self._text_selection.text[:left])
                positions.extend((base + length(normalized(row['text'][:region['start']])),
                                  base + length(normalized(row['text'][:region['end']])))
                    for region in regions if region['paragraph'] == row['id'])
        return dict(paragraph=regions[0]['paragraph'], source_start=regions[0]['start'],
                    source_end=regions[0]['end'], start=min((left for left, _ in positions), default=-1),
                    end=max((right for _, right in positions), default=-1))

    def _show_error(self, message):
        self._state['message'] = self._attention = message
        self.changed.emit()

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
        if self._font_families is not None:
            return self._font_families
        from PySide6.QtGui import QFontDatabase

        families = [name for name in QFontDatabase.families() if not name.startswith('@') and not QFontDatabase.isPrivateFamily(name)]
        preferred = ['Times New Roman', 'Arial', 'Calibri', 'Aptos', 'Be Vietnam Pro']
        self._font_families = [name for name in preferred if name in families] + sorted(set(families) - set(preferred), key=str.casefold)
        return self._font_families

    @Slot(result='QStringList')
    def listFontFamilies(self):
        # A returned sequence is a copy in QML. A property-backed QStringList
        # rereads the Python getter for each indexOf/concat element access.
        return self.fontFamilies

    @Property('QVariantMap', notify=formattingDefaultsChanged)
    def formattingDefaults(self):
        return self._formatting_defaults

    @Property(str, notify=readingThemeChanged)
    def readingTheme(self):
        return self._reading_theme

    @Slot(str)
    def setReadingTheme(self, theme):
        if theme == self._reading_theme:
            return
        try:
            self._reading_theme = jobs.reading_theme(self.bridge.library.directory, theme)
        except (OSError, ValueError) as exc:
            self._show_error('Chưa lưu được nền đọc văn bản: ' + str(exc))
            return
        from shiboken6 import isValid

        if self._highlighter and isValid(self._highlighter):
            self._highlighter.set_dark(theme == 'dark')
        for _, _, highlighter in tuple(self._reading_documents.values()):
            if isValid(highlighter):
                highlighter.set_dark(theme == 'dark')
        self.readingThemeChanged.emit()

    @Slot(QObject)
    def bindReadingDocument(self, wrapper):
        if not wrapper:
            return
        from shiboken6 import isValid

        if not isValid(wrapper):
            return
        document = wrapper.textDocument()
        existing = self._reading_documents.get(wrapper)
        if existing and existing[1] == document:
            return
        if existing:
            if isValid(existing[2]):
                existing[2].setDocument(None)
                existing[2].deleteLater()
        else:
            wrapper.destroyed.connect(lambda *_: self._reading_documents.pop(wrapper, None))
        from .word_highlights import SourceHighlights

        highlighter = SourceHighlights(document)
        # Retain the Quick wrapper as well as the document, just as in the
        # continuous preview; release them when a virtualized row is destroyed.
        self._reading_documents[wrapper] = (wrapper, document, highlighter)
        highlighter.set_dark(self._reading_theme == 'dark')

    @Slot('QVariantMap')
    def rememberFormatting(self, options):
        if not self.available():
            return
        try:
            self._formatting_defaults = jobs.formatting_defaults(self.bridge.library.directory, options)
            self.formattingDefaultsChanged.emit()
        except (OSError, ValueError, TypeError) as exc:
            self._show_error('Chưa nhớ được định dạng cho bài mới: ' + str(exc))

    def available(self):
        return not (self.bridge.busy or self.bridge.narrationBusy or self.bridge.batchQueue.running or self._working)

    @Slot(object)
    def _progress(self, value):
        self._state.update(value)
        self.changed.emit()

    def _launch(self, action, *, clear_drafts=False, navigate=False, restore_configuration=False, selection_only=False):
        if not self.available():
            return
        self._working = True
        self._attention = ''
        self.changed.emit()
        directory = self.bridge.library.directory
        prior_text_identity = self._text_identity

        def work():
            try:
                job = action(directory)
                preview, preview_notice, package = None, '', None
                if job and job['id'] != prior_text_identity:
                    try:
                        from .word_document import Package
                        from .word_preview import Preview

                        package = Package(jobs.folder_for(directory, job['id']) / 'source.docx')
                        preview = Preview(package)
                    except Exception:
                        preview_notice = 'Chưa hiện được định dạng gốc; vẫn có thể chọn và dịch ở chế độ văn bản.'
                public = jobs.public(directory, job, paragraphs=not (selection_only and job['id'] == prior_text_identity), package=package) if job else None
                return dict(job=public, preview=preview,
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
                if 'paragraphs' not in result['job']:
                    result['job']['paragraphs'] = self._state.get('paragraphs', [])
                if result['job']['id'] == self._text_identity:
                    result['job']['preview_notice'] = self._state.get('preview_notice', '')
                self._state = result['job']
                self._attention = ''
                if self._text_identity != self._state['id']:
                    from .word_selection import TextSelection

                    self._text_selection = TextSelection(self._state['paragraphs'])
                    self._text_identity = self._state['id']
                    self._preview = result.get('preview')
                    self._preview_document = None
                    self._preview_excerpts = {}
                    self._state['preview_notice'] = result.get('preview_notice', '')
                    self.sourceTextChanged.emit()
                self._refresh_highlights()
                if clear_drafts:
                    self._drafts.clear()
                    self._keywords.clear()
                    self.draftsChanged.emit()
                if navigate:
                    self.bridge.navigate.emit('word')
            if result.get('error'):
                self._state['message'] = self._attention = result['error']
            self._library = result.get('library', self._library)
            self.libraryChanged.emit()
            self.changed.emit()
            if result.get('job') and restore_configuration:
                self.configurationRestored.emit()
            self.bridge.inform('', refresh=False)
            if not selection_only:
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
        if not self._can_change_input():
            return
        parsed = QUrl(url)
        if not parsed.isLocalFile():
            self._show_error('Chọn tệp Word trên máy tính.')
            return
        if not self._batch.clear():
            return
        self._launch(lambda directory: jobs.create(directory, parsed.toLocalFile(), preferences=preferences), clear_drafts=True, restore_configuration=True)

    @Slot(str)
    def loadRecord(self, identity):
        if not self._can_change_input():
            return
        if not self._batch.clear():
            return
        self._launch(lambda directory: jobs.read(directory, identity), clear_drafts=True, navigate=True, restore_configuration=True)

    def _can_change_input(self):
        if not self.available():
            return False
        if self.draftsPending:
            self._show_error('Có chỉnh sửa bản dịch chưa lưu. Bấm Lưu Word song ngữ trước khi đổi hoặc hủy bài đang chọn.')
            self.bridge.navigate.emit('word')
            return False
        return True

    @Slot()
    def dismissInput(self):
        if not self._can_change_input():
            return
        if self._batch.clear():
            self._dismiss_source()

    def _dismiss_source(self):
        from .word_selection import TextSelection

        self._state = dict(id='', phase='empty', regions=[], paragraphs=[], message='', selected_count=0, can_export=False, options={})
        self._attention = ''
        self._text_selection, self._text_identity = TextSelection([]), ''
        self._preview = self._preview_document = None
        self._preview_excerpts = {}
        self._detach_highlights()
        self.sourceTextChanged.emit()
        self.changed.emit()
        self.workspaceReset.emit()

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

    @Slot(bool)
    def setWholeDocument(self, enabled):
        if not self.available() or not self._state['id'] or enabled == bool(self._state.get('whole_document')):
            return
        if self.draftsPending:
            self._show_error('Có chỉnh sửa bản dịch chưa lưu. Bấm Lưu Word song ngữ trước khi đổi phạm vi dịch.')
            return
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, [], whole_document=enabled), selection_only=True)

    def _detach_highlights(self):
        from shiboken6 import isValid

        if self._highlighter and isValid(self._highlighter):
            self._highlighter.setDocument(None)
            self._highlighter.deleteLater()
        self._highlighter = self._highlight_document = self._highlight_wrapper = None
        self._highlight_identity = ''

    @Slot(QObject, str)
    def bindPreviewDocument(self, wrapper, identity):
        if not identity or identity != self._state['id'] or not wrapper:
            return
        document = wrapper.textDocument()
        if document == self._highlight_document and identity == self._highlight_identity:
            return
        self._detach_highlights()
        from .word_highlights import SourceHighlights

        self._highlight_wrapper, self._highlight_document, self._highlight_identity = wrapper, document, identity
        self._highlighter = SourceHighlights(document)
        self._highlighter.set_dark(self._reading_theme == 'dark')
        self._refresh_highlights()

    def _refresh_highlights(self):
        from shiboken6 import isValid

        if not self._highlighter or self._highlight_identity != self._state['id']:
            return
        if not isValid(self._highlighter) or not isValid(self._highlight_document):
            self._detach_highlights()
            return
        if self._preview:
            positions = self._preview.selected_positions(self._highlight_document, self._state['regions'])
        else:
            from .word_preview import length, normalized

            positions = []
            for left, _, row, _ in self._text_selection.spans:
                base = length(self._text_selection.text[:left])
                positions.extend((base + length(normalized(row['text'][:region['start']])),
                                  base + length(normalized(row['text'][:region['end']])))
                    for region in self._state['regions'] if region['paragraph'] == row['id'])
        self._highlighter.set_ranges(positions)

    def _visible_ranges(self, identity, wrapper, start, end):
        if not identity or identity != self._state['id'] or identity != self._text_identity:
            raise ValueError('Tài liệu đã đổi; bôi đen lại phần cần dịch.')
        if self._preview:
            selected, skipped = self._preview.ranges(wrapper.textDocument(), start, end)
        else:
            selected, skipped = self._text_selection.ranges(start, end)
        from .word_selection import complete_word_ranges

        return complete_word_ranges(self._state['paragraphs'], selected), skipped

    @Slot(str, QObject, int, int, result=str)
    def highlightAction(self, identity, wrapper, start, end):
        return self.highlightBounds(identity, wrapper, start, end).get('action', '')

    @Slot(str, QObject, int, int, result='QVariantMap')
    def highlightBounds(self, identity, wrapper, start, end):
        try:
            selected, _ = self._visible_ranges(identity, wrapper, start, end)
            covered = all(any(old['paragraph'] == row['paragraph'] and old['start'] <= row['start'] and old['end'] >= row['end']
                              for old in self._state['regions']) for row in selected)
            if self._preview:
                positions = self._preview.selected_positions(wrapper.textDocument(), selected)
            else:
                from .word_preview import length, normalized

                positions = []
                for left, _, row, _ in self._text_selection.spans:
                    base = length(self._text_selection.text[:left])
                    positions.extend((base + length(normalized(row['text'][:region['start']])),
                                      base + length(normalized(row['text'][:region['end']])))
                        for region in selected if region['paragraph'] == row['id'])
            return dict(action='remove' if covered else 'add', start=min(left for left, _ in positions), end=max(right for _, right in positions))
        except (ValueError, RuntimeError, AttributeError) as exc:
            self._show_error(str(exc))
            return {}

    @Slot(str, QObject, int, int, bool)
    def applyHighlight(self, identity, wrapper, start, end, remove):
        if not self.available():
            return
        try:
            selected, skipped = self._visible_ranges(identity, wrapper, start, end)
        except (ValueError, RuntimeError, AttributeError) as exc:
            self._show_error(str(exc))
            return
        if not remove:
            self._add_selected_ranges(identity, selected, skipped)
            return
        rows = self._ranges()
        for selection in selected:
            rows = self._subtract(rows, selection['paragraph'], selection['start'], selection['end'])
        self._launch(lambda directory: jobs.selections(directory, identity, rows), selection_only=True)

    @staticmethod
    def _subtract(rows, paragraph, start, end):
        updated = []
        for row in rows:
            if row['paragraph'] != paragraph or row['end'] <= start or row['start'] >= end:
                updated.append(row)
            else:
                if row['start'] < start:
                    updated.append({**row, 'end': start})
                if row['end'] > end:
                    updated.append({**row, 'start': end})
        return updated

    @Slot(str, int, int, bool)
    def toggle(self, paragraph, start, end, selected):
        rows = self._ranges()
        if selected:
            rows.append(dict(paragraph=paragraph, start=start, end=end))
        else:
            rows = self._subtract(rows, paragraph, start, end)
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, rows), selection_only=True)

    @Slot(str, int, int, int)
    def addRange(self, paragraph, base, start, end):
        try:
            text = next(row['text'] for row in self._state['paragraphs'] if row['id'] == paragraph)[base:]
            self.toggle(paragraph, base + utf16_position(text, start), base + utf16_position(text, end), True)
        except (ValueError, StopIteration) as exc:
            self._show_error(str(exc) or 'Chọn lại vùng văn bản.')

    @Slot(str, int, int)
    def addTextSelection(self, identity, start, end):
        if not self.available():
            return
        try:
            if not identity or identity != self._state['id'] or identity != self._text_identity:
                raise ValueError('Tài liệu đã đổi; bôi đen lại phần cần dịch.')
            selected, skipped = self._text_selection.ranges(start, end)
        except ValueError as exc:
            self._show_error(str(exc))
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
            self._show_error(str(exc))
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
            self._show_error(str(exc))
            return
        self._add_selected_ranges(identity, selected, skipped)

    def _add_selected_ranges(self, identity, selected, skipped):
        from .word_selection import complete_word_ranges

        selected = complete_word_ranges(self._state['paragraphs'], selected)
        rows = [*self._ranges(), *selected]

        def action(directory):
            job = jobs.selections(directory, identity, rows)
            if skipped:
                job['message'] += f' Giữ nguyên {skipped} đoạn chỉ có hình/công thức hoặc đang khóa; các đoạn đó chưa được chọn để dịch.'
            return job

        self._launch(action, selection_only=True)

    @Slot(str)
    def removeRange(self, identity):
        rows = [row for row in self._ranges() if f"{row['paragraph']}:{row['start']}:{row['end']}" != identity]
        current = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, current, rows), selection_only=True)

    @Slot()
    def clearSelection(self):
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, []), clear_drafts=True, selection_only=True)

    @Slot(str)
    def selectAll(self, scope):
        rows = [dict(paragraph=row['paragraph'], start=row['start'], end=row['end']) for row in self.items(scope) if row['editable']]
        identity = self._state['id']
        self._launch(lambda directory: jobs.selections(directory, identity, rows), selection_only=True)

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
            self._attention = self._state['message']
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
            self._show_error(str(exc))

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
