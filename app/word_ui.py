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

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._state = dict(id='', phase='empty', regions=[], paragraphs=[], message='', selected_count=0, can_export=False, options={})
        self._library, self._drafts, self._keywords = [], {}, {}
        self._working, self._trash = False, False
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

        def work():
            try:
                job = action(directory)
                return dict(job=jobs.public(directory, job) if job else None,
                            library=jobs.catalog(directory, self._trash), error='')
            except Exception as exc:
                return dict(error=str(exc), job=None, library=jobs.catalog(directory, self._trash))

        def finished(result):
            self._working = False
            if result.get('job'):
                self._state = result['job']
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
        parsed = QUrl(url)
        if not parsed.isLocalFile():
            self._state['message'] = 'Chọn tệp Word trên máy tính.'
            self.changed.emit()
            return
        self._launch(lambda directory: jobs.create(directory, parsed.toLocalFile()), clear_drafts=True, restore_configuration=True)

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
                result.append(dict(paragraph=row['id'], start=part['start'], end=part['end'], text=part['text'],
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
    def preview(self, options, subject, grade):
        identity = self._state['id']
        drafts, keywords = copy.deepcopy(self._drafts), copy.deepcopy(self._keywords)

        def action(directory):
            self._apply_drafts(directory, identity, drafts, keywords)
            return jobs.translate(directory, identity, options, subject, grade, self.bridge.cancel_event, self.progressed.emit)

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
