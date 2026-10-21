import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Window

ApplicationWindow {
    id: root
    palette: AppPalette {}
    Binding { target: AppTheme; property: "dark"; value: bridge.applicationTheme === "dark" }
    onVisibleChanged: if (visible) bridge.applyWindowAppearance(root)
    Connections { target: bridge; function onApplicationThemeChanged() { bridge.applyWindowAppearance(root) } }
    readonly property var appBridge: bridge
    readonly property var lessonData: bridge.lesson
    visible: false
    width: 1366; height: 850
    minimumWidth: 1080; minimumHeight: 700
    title: "BiliClass · " + bridge.appVersion + " · Trợ lý dạy học song ngữ" + (bridge.developmentMode ? " · Bản nguồn" : "")
    flags: Qt.Window | (Qt.platform.os === "windows" ? Qt.CustomizeWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.ExpandedClientAreaHint | Qt.NoTitleBarBackgroundHint : 0)
    background: Rectangle {
        color: root.color
        Rectangle {
            objectName: "applicationTitleBar"
            width: parent.width; height: root.SafeArea.margins.top
            color: AppTheme.surface; clip: true
            Image {
                x: 16; y: Math.round((parent.height - height) / 2); width: 16; height: 16
                source: "../assets/brand/biliclass.svg"; sourceSize.width: 64; sourceSize.height: 64
                Accessible.ignored: true
            }
            Text {
                id: captionText; objectName: "applicationCaptionText"
                x: 40; y: Math.round((parent.height - height) / 2)
                width: Math.min(implicitWidth, Math.max(0, parent.width - x - titleBadges.width - 175))
                text: root.title; color: AppTheme.ink; elide: Text.ElideRight
                font.family: bridge.windowCaptionFont.family
                font.pointSize: bridge.windowCaptionFont.pointSize
                font.weight: Font.Normal; renderType: Text.NativeRendering
            }
            Row {
                id: titleBadges
                objectName: "applicationTitleBadges"
                x: captionText.x + captionText.width + 16
                anchors.verticalCenter: parent.verticalCenter; spacing: 8
                Rectangle {
                    width: 82; height: 20; radius: 10; color: AppTheme.adapt("#eaf2ff")
                    Label { objectName: "applicationLanguageBadge"; anchors.centerIn: parent; text: "ANH ↔ VIỆT"; color: AppTheme.adapt("#0869f9"); font.pixelSize: 10; font.weight: Font.DemiBold }
                }
                Rectangle {
                    width: 84; height: 20; radius: 10; color: AppTheme.adapt("#eaf7f4")
                    Label { objectName: "applicationStorageBadge"; anchors.centerIn: parent; text: "Lưu trên máy"; color: AppTheme.adapt("#008f89"); font.pixelSize: 10; font.weight: Font.DemiBold }
                }
            }
        }
    }
    color: AppTheme.adapt("#f3f7fc")
    property string page: "home"
    function backFromLesson() {
        if (page !== "result" || bridge.busy || bridge.narrationBusy || root.Overlay.overlay.visible) return
        root.requestAction(function() { bridge.returnToLibrary() })
    }
    function editingText() {
        let item = root.activeFocusItem
        while (item) {
            if (item.visible && item.enabled && typeof item.cursorPosition === "number" && typeof item.text === "string") return true
            item = item.parent
        }
        return false
    }
    Shortcut {
        objectName: "lessonBackspaceShortcut"
        sequence: "Backspace"; context: Qt.WindowShortcut
        enabled: root.page === "result" && !root.editingText() && !root.Overlay.overlay.visible && !bridge.busy && !bridge.narrationBusy
        onActivated: root.backFromLesson()
    }
    MouseArea {
        objectName: "lessonMouseBack"; anchors.fill: parent; z: 1000
        // Reset MouseArea's implicit arrow so text controls and buttons below
        // keep their own pointer, including when this back-button layer is off.
        cursorShape: undefined
        acceptedButtons: Qt.BackButton; enabled: root.page === "result"
        onClicked: root.backFromLesson()
    }
    onPageChanged: {
        if (!bridge.experimentalTeaching && (page === "classroom" || page === "reports")) { page = "home"; return }
        if (page !== "library") root.endLibraryDrag()
        if (page === "voice") { Qt.callLater(root.ensureVoiceThumbnail); Qt.callLater(function() { bridge.completeLegacyNarration() }) }
        if (page === "result") Qt.callLater(function() { if (root.page === "result") backToLibraryAction.forceActiveFocus(Qt.OtherFocusReason) })
        if (page === "chatgpt" && bridge.browserState.phase === "completed") bridge.restoreConversionResult()
        if (page === "glossary" || page === "knowledge") {
            referenceTab = page === "knowledge" ? 1 : 0
            page = "reference"
        }
    }
    property color ink: AppTheme.adapt("#112650")
    property color muted: AppTheme.adapt("#667997")
    property color blue: AppTheme.adapt("#0869f9")
    property color line: AppTheme.adapt("#e0e8f3")
    property bool dirty: false
    property bool loadingFields: false
    property var pendingAction: null
    property bool voiceSourceExpanded: false
    readonly property bool compactCreation: height < 980
    readonly property bool tightCreation: height < 800
    readonly property bool compactVoice: page === "voice" && !!bridge.quickResult.path && height < 850
    property bool voicePreviewExpanded: false
    property bool creationPreviewExpanded: false
    function showCreationPreview() {
        creationPreviewExpanded = true
        Qt.callLater(function() { creationScroll.contentItem.contentY = Math.max(0, creationSlidePreview.y - 16) })
    }
    property bool voiceResultShown: false
    property bool voiceResultDismissed: true
    function openVoiceConfiguration() {
        voiceResultDismissed = true; voiceResultShown = false
        voiceConfigurationExpanded = true; narrationOptionsPinned = true
        voicePreviewExpanded = false
    }
    property string thumbnailRequested: ""
    function ensureVoiceThumbnail() {
        if (page !== "voice" || !bridge.quickResult.path || bridge.quickResult.image || bridge.busy || bridge.previewBusy) return
        const request = [root.lessonData.id, bridge.quickResult.path, bridge.quickResult.slide || 1].join("|")
        if (thumbnailRequested === request) return
        thumbnailRequested = request
        bridge.previewConvertedSlide(bridge.quickResult.slide || 1)
    }
    property bool narrationPreviewPending: false
    property bool voiceConfigurationExpanded: false
    readonly property bool narrationComplete: !!bridge.quickResult.path && !!narrationDraft.ready && !bridge.narrationBusy
    onNarrationCompleteChanged: if (narrationComplete) Qt.callLater(root.revealCompletedNarration)
    function revealCompletedNarration() {
        if (page !== "voice" || bridge.narrationBusy || !bridge.lessonNarration.ready || voiceResultDismissed) return
        narrationOptionsPinned = false
        narrationMode = bridge.lessonNarration.mode
        narrationVoice = bridge.lessonNarration.voice
        narrationRate = bridge.lessonNarration.rate || 0
        if (!voiceResultDismissed) voiceResultShown = true
        bridge.rememberNarrationResult()
        voicePreviewExpanded = true
        if (!bridge.quickResult.image && !bridge.previewBusy)
            bridge.previewConvertedSlide(bridge.quickResult.slide || 1)
    }
    function showNarrationPreview() {
        voicePreviewExpanded = true
        if (!bridge.quickResult.image && !bridge.previewBusy) bridge.previewConvertedSlide(bridge.quickResult.slide || 1)
        Qt.callLater(function() { resultScroll.contentItem.contentY = Math.max(0, lessonSlidePreview.y - 16) })
    }
    function showNarratedLessonInLibrary() {
        const identity = root.lessonData.id
        const title = root.lessonData.title
        bridge.stopSpeech()
        root.go("library")
        search.text = title
        subjectFilter.currentIndex = 0; gradeFilter.currentIndex = 0; stateFilter.currentIndex = 0; voiceFilter.currentIndex = 0
        root.libraryPage = 1
        Qt.callLater(function() {
            const index = root.libraryResult.ids.indexOf(identity)
            root.libraryPage = Math.floor(Math.max(0, index) / (root.libraryResult.page_size || 20)) + 1
            root.selectedLessons = [identity]
        })
    }
    property string selectedFile: ""
    property string selectedFileName: ""
    property string inputDocumentError: ""
    property string previousInputTitle: ""
    property bool pasteMode: false
    property bool creationPromptVisible: false
    property bool includeDownloadVoice: true
    property bool resultDetails: false
    property string libraryReviewTarget: ""
    property string narrationMode: bridge.narrationPreferences.mode
    property string narrationVoice: bridge.voiceSettings.voice || ""
    property int narrationRate: bridge.voiceSettings.rate || 0
    property bool narrationOptionsPinned: false
    readonly property var narrationDrafts: bridge.narrationCreationChoices(bridge.narrationVariants, root.narrationVoice, root.narrationRate)
    readonly property var narrationDraft: !root.narrationOptionsPinned && bridge.lessonNarration.ready && bridge.lessonNarration.mode === root.narrationMode ? bridge.lessonNarration : narrationDrafts[root.narrationMode] || ({})
    readonly property var narrationAvailable: bridge.narrationAvailableModes(bridge.narrationVariants)
    readonly property bool narrationAllCreated: !!narrationAvailable.both
    function chooseMissingNarration() {
        if (page !== "voice" || narrationOptionsPinned || !bridge.quickResult.path) return
        if (bridge.lessonNarration.ready && !voiceResultDismissed) return
        const languages = bridge.narrationInputLanguages
        const missing = ["en", "vi", "both"].filter(function(mode) {
            return !root.narrationAvailable[mode] && (mode === "both" ? languages.en && languages.vi : languages[mode])
        })
        if (missing.length && root.narrationAvailable[root.narrationMode]) root.narrationMode = missing[0]
    }
    onNarrationAvailableChanged: Qt.callLater(root.chooseMissingNarration)
    readonly property var narrationCoverage: bridge.narrationWorkspace.summary
    readonly property int narrationEligibleSlides: narrationCoverage.eligible === undefined ? narrationCoverage.total : narrationCoverage.eligible
    readonly property int narrationReadableSlides: narrationMode === "both" ? narrationEligibleSlides - narrationCoverage.empty : (narrationCoverage[narrationMode] || 0)
    readonly property int narrationSkippedSlides: narrationEligibleSlides - narrationReadableSlides
    readonly property int narrationPartialSlides: 2 * (narrationEligibleSlides - narrationCoverage.empty) - narrationCoverage.vi - narrationCoverage.en
    readonly property bool narrationPreviewActive: bridge.voiceUiState.phase === "preparing" || bridge.voiceUiState.phase === "playing"
    readonly property int lessonLayoutFailures: root.lessonData.voice_only ? 0 : ((((root.lessonData.slide_quality || {}).counts || {}).FAIL) || 0)
    readonly property bool taskRunning: bridge.busy || bridge.narrationBusy || !!bridge.browserState.running || bridge.inputDocuments.busy || !!bridge.updateState.downloading
    readonly property string idleActivity: bridge.teachingTransitioning ? "PowerPoint đang mở, đóng hoặc chuyển chế độ…"
        : bridge.powerpointState.active ? "PowerPoint đang trình chiếu"
        : narrationPreviewActive ? (bridge.voiceUiState.phase === "preparing" ? "Đang chuẩn bị câu nghe thử…" : "Đang nghe thử giọng đọc")
        : bridge.powerpointState.opened ? "Mascot đã gán bài · Chưa trình chiếu"
        : "BiliClass sẵn sàng"
    property bool jobObserved: false
    property bool inputObserved: false
    property var jobOrigin: ({page: "home", tab: 0})
    property var inputOrigin: ({page: "new", tab: 0})
    function rememberJobOrigin() {
        if (bridge.busy && !jobObserved) jobOrigin = {page: root.page, tab: settingsPanel.activeTab}
        jobObserved = bridge.busy
    }
    readonly property var activeTaskLocation: bridge.narrationBusy ? {page: "voice", tab: -1}
        : bridge.browserState.running ? {page: "chatgpt", tab: -1}
        : bridge.inputDocuments.busy ? inputOrigin : bridge.busy ? jobOrigin
        : bridge.updateState.downloading ? {page: "settings", tab: 1} : {page: "", tab: -1}
    readonly property bool taskElsewhere: taskRunning && !!activeTaskLocation.page &&
        (page !== activeTaskLocation.page || (page === "settings" && settingsPanel.activeTab !== activeTaskLocation.tab))
    function returnToTask() {
        if (!taskElsewhere) return
        const location = activeTaskLocation
        requestAction(function() {
            root.page = location.page
            if (location.page === "settings") settingsPanel.activeTab = location.tab
            if (location.page === "voice") Qt.callLater(function() {
                resultScroll.contentItem.contentY = Math.max(0, lessonNarrationPanel.y - 16)
            })
        })
    }
    property string lastReportedError: ""
    function showOperationError() {
        if (!bridge.error || !bridge.message) { lastReportedError = ""; operationError.close(); return }
        if (root.taskRunning) return
        if (lastReportedError === bridge.message) return
        lastReportedError = bridge.message
        operationError.notice = bridge.message
        operationError.open()
    }
    function chooseNarrationMode(mode) {
        if (page === "voice") narrationOptionsPinned = true
        narrationMode = mode
        bridge.narrationPreferences.select(mode)
        const choice = narrationDrafts[mode] || {}
        if (choice.ready && choice.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(choice.id)
    }
    function syncNarrationSelection() {
            if (root.page === "voice" && root.narrationOptionsPinned) {
                const available = bridge.narrationInputLanguages
                if ((available.en || available.vi) && ((root.narrationMode === "both" && !(available.en && available.vi)) || !available[root.narrationMode] && root.narrationMode !== "both")) root.narrationMode = available.en ? "en" : "vi"
                return
            }
            const record = root.lessonData.narration || {}
            const available = bridge.narrationInputLanguages
            const preferred = ["vi", "en", "both"].indexOf(record.mode) >= 0 ? record.mode : bridge.narrationPreferences.mode
            root.narrationMode = (available.en || available.vi) &&
                (preferred === "both" ? !(available.en && available.vi) : !available[preferred])
                ? available.en ? "en" : "vi" : preferred
            const voice = bridge.lessonNarration.voice || record.voice || bridge.voiceSettings.voice || ""
            root.narrationVoice = bridge.multilingualVoices.some(function(row) { return row.id === voice }) ? voice : bridge.voiceSettings.voice || ""
            root.narrationRate = record.voice ? record.rate : bridge.voiceSettings.rate
        }
    function prepareTeaching(identity) {
        if (bridge.busy || bridge.narrationBusy) return
        bridge.stopSpeech()
        if (identity !== undefined && identity !== bridge.selectedNarrationVariant) {
            bridge.selectNarrationVariant(identity)
            if (bridge.selectedNarrationVariant !== identity) return
        }
        if (bridge.selectedNarrationVariant && bridge.lessonNarration.ready)
            bridge.openNarratedPowerPoint(bridge.selectedNarrationVariant)
        else
            bridge.openTeachingLibraryLesson(root.lessonData.id)
    }
    property int libraryPage: 1
    readonly property bool libraryLarge: page === "library" && bridge.libraryView === "grid"
    onLibraryLargeChanged: coverRequests.restart()
    Timer { id: coverRequests; interval: 120; onTriggered: bridge.requestLibraryCovers(root.libraryLarge ? root.libraryResult.rows : []) }
    property var selectedLessons: []
    property string librarySelectionAnchor: ""
    property var libraryCardItems: ({})
    property string libraryDragStart: ""
    property var libraryDragBase: []
    property point libraryDragPointer: Qt.point(0, 0)
    property bool libraryDragActive: false
    property bool libraryDragSelecting: false
    readonly property string librarySelectionScope: [search.text, subjectFilter.currentValue, gradeFilter.currentValue, stateFilter.currentValue, voiceFilter.currentValue].join("|")
    readonly property bool libraryFiltersActive: !!(search.text.trim() || subjectFilter.currentValue || gradeFilter.currentValue || stateFilter.currentValue || voiceFilter.currentValue)
    onLibrarySelectionScopeChanged: { selectedLessons = []; librarySelectionAnchor = ""; endLibraryDrag() }
    onLibraryResultChanged: {
        coverRequests.restart()
        const kept = selectedLessons.filter(function(id) { return (libraryResult.ids || []).indexOf(id) >= 0 })
        if (kept.length !== selectedLessons.length) selectedLessons = kept
        if (libraryResult.ids.indexOf(librarySelectionAnchor) < 0) librarySelectionAnchor = ""
    }
    function libraryRange(first, last) {
        const ids = libraryResult.ids
        const a = ids.indexOf(first), b = ids.indexOf(last)
        return a < 0 || b < 0 ? [last] : ids.slice(Math.min(a, b), Math.max(a, b) + 1)
    }
    function addLibraryRange(base, first, last) {
        const list = base.slice()
        for (const id of libraryRange(first, last)) if (list.indexOf(id) < 0) list.push(id)
        selectedLessons = list
    }
    function selectLibraryLesson(identity, selected, modifiers) {
        if ((modifiers & Qt.ShiftModifier) && librarySelectionAnchor) {
            addLibraryRange(selectedLessons, librarySelectionAnchor, identity)
            return
        }
        const list = selectedLessons.filter(function(id) { return id !== identity })
        if (selected) list.push(identity)
        selectedLessons = list
        librarySelectionAnchor = identity
    }
    function beginLibraryDrag(identity, item, x, y) {
        libraryDragStart = identity
        libraryDragBase = selectedLessons.slice()
        libraryDragPointer = item.mapToItem(root.contentItem, x, y)
        libraryDragActive = false
        libraryDragSelecting = false
    }
    function moveLibraryDrag(item, x, y) {
        if (!libraryDragStart) return
        libraryDragPointer = item.mapToItem(root.contentItem, x, y)
        libraryDragActive = true
        updateLibraryDrag()
    }
    function updateLibraryDrag() {
        if (!libraryDragActive || page !== "library") return
        const point = libraryHomeScroll.mapFromItem(root.contentItem, libraryDragPointer.x, libraryDragPointer.y)
        if (point.x < 0 || point.x > libraryHomeScroll.width) return
        for (const row of libraryResult.rows) {
            const card = libraryCardItems[row.id]
            if (!card || !card.visible) continue
            const p = card.mapFromItem(root.contentItem, libraryDragPointer.x, libraryDragPointer.y)
            if (card.contains(p) && (row.id !== libraryDragStart || libraryDragSelecting)) {
                libraryDragSelecting = true
                addLibraryRange(libraryDragBase, libraryDragStart, row.id)
                librarySelectionAnchor = libraryDragStart
                return
            }
        }
    }
    function endLibraryDrag() { libraryDragActive = false; libraryDragStart = "" }
    Timer {
        interval: 30; repeat: true; running: root.libraryDragActive
        onTriggered: {
            const view = libraryHomeScroll.contentItem
            const p = libraryHomeScroll.mapFromItem(root.contentItem, root.libraryDragPointer.x, root.libraryDragPointer.y)
            if (p.x < 0 || p.x > libraryHomeScroll.width) return
            const step = p.y < 38 ? -14 : p.y > libraryHomeScroll.height - 38 ? 14 : 0
            if (step) view.contentY = Math.max(0, Math.min(Math.max(0, view.contentHeight - view.height), view.contentY + step))
            root.updateLibraryDrag()
        }
    }
    function downloadLibraryLessons(identities) {
        libraryDownloadDialog.identities = identities.slice()
        libraryDownloadDialog.open()
    }
    readonly property var libraryResult: bridge.queryLibrary(bridge.lessons, search.text,
        subjectFilter.currentValue || "", gradeFilter.currentValue || "", stateFilter.currentValue || "", voiceFilter.currentValue || "", root.libraryPage)
    function durationText(seconds) {
        const value = Math.max(0, Math.floor(seconds || 0))
        function two(n) { return n < 10 ? "0" + n : "" + n }
        return two(Math.floor(value / 3600)) + ":" + two(Math.floor(value / 60) % 60) + ":" + two(value % 60)
    }
    property int preferredCreationDesign: 0
    readonly property bool creationPowerPoint: selectedFileName.toLowerCase().endsWith(".pptx")
    readonly property bool creationCanKeepSource: creationPowerPoint || (!selectedFile && !pasteInput.text.trim())
    readonly property bool creationKeepSource: creationCanKeepSource && creationWorkflow.currentIndex === 0
    readonly property bool keepSourceDesign: root.lessonData.presentation_style === "source"
    onCreationCanKeepSourceChanged: Qt.callLater(function() { creationWorkflow.currentIndex = creationCanKeepSource ? preferredCreationDesign : 1 })
    property bool rescue: false
    property var presentationContent: bridge.presentationContent(rescue)
    onRescueChanged: { presentationContent = bridge.presentationContent(rescue); refreshTemplate() }
    property int referenceTab: 0
    property int termPage: 1
    property string knowledgeSearch: ""
    readonly property var knowledgeResults: root.page === "reference" && root.referenceTab === 1 && bridge.knowledgeStats.entries >= 0 ? bridge.searchKnowledge(knowledgeSearch, knowledgeSubject.text, knowledgeGrade.text) : []
    readonly property var filteredTerms: bridge.terms.filter(function(row) {
        const query = termSearch.text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d")
        const text = [row.subject, row.vi, row.en].join(" ").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d")
        return query.trim().split(/\s+/).every(function(word) { return text.indexOf(word) >= 0 })
            && (termSubjectFilter.currentIndex === 0 || row.subject === termSubjectFilter.currentText)
    })
    onFilteredTermsChanged: termPage = Math.min(termPage, Math.max(1, Math.ceil(filteredTerms.length / 20)))
    Timer { id: knowledgeSearchTimer; interval: 220; onTriggered: root.knowledgeSearch = knowledgeQuery.text }
    property string translationSource: "vi"
    property var teaching: bridge.teachingContext
    property var classroom: bridge.classroomContext
    property string profileLabel: [bridge.settings.teacher, bridge.settings.school].filter(function(value) { return !!value }).join("  ·  ")
    readonly property var conversionFormats: bridge.conversionFormats
    readonly property var selectedConversionFormat: conversionFormats[Math.min(Math.max(0, creationFormat.currentIndex), conversionFormats.length - 1)]
    readonly property string creationSubject: subjectInput.currentText === "Khác" ? customSubjectInput.text.trim() : subjectInput.currentText
    property bool creationSubjectOverridden: false
    function applyDefaultTeachingSubject() {
        const subject = bridge.conversionSubjectSelection
        const index = bridge.conversionSubjects.indexOf(subject)
        subjectInput.currentIndex = !subject ? -1 : index >= 0 ? index : bridge.conversionSubjects.indexOf("Khác")
        customSubjectInput.text = index < 0 ? subject : ""
    }
    Component.onCompleted: {
        applyDefaultTeachingSubject()
        // Show after QML construction returns to the event loop. A native
        // window shown halfway through cold loading cannot respond to input.
        Qt.callLater(function() { root.visible = true })
    }
    readonly property var creationPrompt: page === "new" ? bridge.conversionPromptPreview(
        titleInput.text, creationSubject, educationInput.currentText, gradeInput.currentText, pasteInput.text,
        selectedFile, selectedConversionFormat.id,
        ["standard", "visual", "practice"][creationPreset.currentIndex], creationKeepSource ? "source" : "template", teacherNotesInput.text) : ({prompt: "", ready: false})
    property var templatePages: bridge.templatePages(rescue)
    property int templatePageIndex: 0
    function refreshTemplate() { templatePages = bridge.templatePages(rescue); templatePageIndex = 0 }
    function acceptInputDocuments(urls) {
        creationPreviewExpanded = false
        if (urls.length === 1 && !String(urls[0]).toLowerCase().endsWith(".pptx")) {
            bridge.inputDocuments.clear()
            inputDocumentError = "Chỉ nhận tệp PowerPoint (.pptx), tối đa 200 MB."
            return false
        }
        if (selectedFileName) previousInputTitle = selectedFileName.replace(/\.[^.]+$/, "")
        selectedFile = ""
        selectedFileName = ""
        inputDocumentError = ""
        bridge.inputDocuments.select(urls)
        return true
    }
    Connections {
        target: bridge.inputDocuments
        function onSelected(selection, error) { root.applyInputSelection(selection, error) }
        function onChanged() {
            if (bridge.inputDocuments.busy && !root.inputObserved) root.inputOrigin = {page: root.page, tab: settingsPanel.activeTab}
            root.inputObserved = bridge.inputDocuments.busy
        }
    }
    function applyInputSelection(selection, error) {
        if (!selection.valid) { inputDocumentError = error; return }
        if (!selection.name.toLowerCase().endsWith(".pptx")) {
            inputDocumentError = "Chỉ nhận tệp PowerPoint (.pptx), tối đa 200 MB."
            return false
        }
        inputDocumentError = ""
        selectedFile = selection.url
        selectedFileName = selection.name
        pasteInput.text = ""
        pasteMode = false
        if (!titleInput.text.trim() || titleInput.text === previousInputTitle) titleInput.text = selection.name.replace(/\.[^.]+$/, "")
        titleInput.cursorPosition = 0
        previousInputTitle = selection.name.replace(/\.[^.]+$/, "")
        bridge.clearInputAssessment()
        return true
    }
    function removeInputDocument() {
        creationPreviewExpanded = false
        bridge.inputDocuments.clear()
        if (titleInput.text === (selectedFileName ? selectedFileName.replace(/\.[^.]+$/, "") : previousInputTitle)) titleInput.text = ""
        previousInputTitle = ""
        selectedFile = ""
        selectedFileName = ""
        inputDocumentError = ""
        bridge.clearInputAssessment()
    }
    function showConversionExample(index) {
        conversionExample.formatIndex = index
        conversionExample.open()
    }

    function statusLabel(value) {
        return value === "READY_TO_TEACH" ? "Đã duyệt nội dung" : value === "REVIEW_REQUIRED" ? "Chờ xác nhận" : "Bản nháp"
    }
    function loadFields() {
        autoSaveTimer.stop()
        loadingFields = true
        viEdit.text = bridge.segment.vi || ""
        enEdit.text = bridge.segment.en || ""
        lockedCheck.checked = bridge.segment.locked || false
        dirty = false
        loadingFields = false
    }
    function save(approve) {
        if (approve) {
            let warnings = bridge.inspectPair(viEdit.text, enEdit.text)
            if (warnings.length) { reviewWarning.details = warnings.join("\n\n"); reviewWarning.open(); return false }
        }
        return bridge.saveSegment(viEdit.text, enEdit.text, approve, lockedCheck.checked)
    }
    function requestAction(action) {
        if (dirty) { autoSaveTimer.stop(); pendingAction = action; unsaved.open() }
        else action()
    }
    function go(destination) { requestAction(function() {
        if (destination === "glossary" || destination === "knowledge") {
            referenceTab = destination === "knowledge" ? 1 : 0
            page = "reference"
        } else {
            if (destination === "voice") root.openVoiceConfiguration()
            page = destination
        }
    }) }
    function edited() {
        if (!loadingFields) { dirty = true; autoSaveTimer.restart() }
    }
    onClosing: function(close) {
        if (bridge.updateApplying) { close.accepted = true }
        else if (bridge.updateState.downloading) { close.accepted = false; updateBusyDialog.open() }
        else if (bridge.busy) { close.accepted = false; busyDialog.open() }
        else if (narrationScript.visible && narrationScript.dirty) { close.accepted = false; narrationScript.forceActiveFocus() }
        else if (dirty) { close.accepted = false; requestAction(function() { Qt.quit() }) }
        if (close.accepted) {
            companion.disposing = true
            companion.hide()
            Qt.quit()
        }
    }
    Connections {
        target: bridge
        function onBrowserStateChanged() { if (!bridge.browserState.running) cancelConversionDialog.close() }
        function onNarrationResultRequested() {
            const recent = bridge.recentNarrationResult
            root.narrationMode = recent.mode; root.narrationVoice = recent.voice; root.narrationRate = recent.rate
            root.narrationOptionsPinned = false; root.voiceResultDismissed = false
            root.voiceResultShown = true; root.voicePreviewExpanded = true
            Qt.callLater(root.revealCompletedNarration)
        }
        function onQuickResultChanged() { Qt.callLater(root.ensureVoiceThumbnail) }
        function onNarrationChanged() {
            if (root.page === "voice") Qt.callLater(function() { bridge.completeLegacyNarration() })
            const job = bridge.narrationPreparation
            if (bridge.lessonNarration.ready && !job.running && !root.voiceResultDismissed) Qt.callLater(root.revealCompletedNarration)
            if (job.lesson_id !== root.lessonData.id) return
            if (job.running) { root.narrationPreviewPending = true; root.voiceResultDismissed = false; root.voiceResultShown = false; return }
            if (!root.narrationPreviewPending || bridge.narrationBusy) return
            root.narrationPreviewPending = false
            if (root.page === "voice" && job.total > 0 && job.complete === job.total && !job.failed && !job.cancelled) {
                root.voicePreviewExpanded = true
                if (!bridge.quickResult.image && !bridge.previewBusy)
                    bridge.previewConvertedSlide(bridge.quickResult.slide || 1)
            }
        }
        function onNarrationAlreadyCreated(config) { existingNarration.selection = config; existingNarration.open() }
        function onUpdateAvailable() { updateDialog.open() }
        function onPowerpointSlideChanged(slide) { if (!root.dirty && !bridge.teachingSession.state.bound) bridge.followPowerPoint() }
        function onPowerpointStarted() {
            if (bridge.mascotSettings.visible || bridge.teachingSession.state.bound) {
                companion.collapsed = !bridge.teachingSession.state.bound
                bridge.showCompanion(companion, true)
            }
        }
        function onProjectClassroomRequested() { if (bridge.experimentalTeaching) { projector.quiz = true; bridge.showProjector(projector, bridge.screens.length > 1 ? 1 : 0) } }
        function onTeachingLessonReady() {
            root.showNormal(); root.raise(); root.requestActivate()
            root.requestAction(function() { root.prepareTeaching() })
        }
        function onNavigate(destination) {
            const showReview = destination === "result" && root.libraryReviewTarget === root.lessonData.id;
            const keepNarrationOptions = root.page === "voice" && root.narrationOptionsPinned;
            root.page = destination === "browser-settings" ? "settings" : destination;
            if (destination === "result" || destination === "voice") { root.voiceSourceExpanded = false; root.resultDetails = false; root.libraryReviewTarget = "" }
            if (destination === "voice") { root.voiceResultShown = false; root.voiceResultDismissed = true; root.narrationOptionsPinned = keepNarrationOptions; root.voiceConfigurationExpanded = true; root.includeDownloadVoice = true; root.syncNarrationSelection(); Qt.callLater(root.chooseMissingNarration) }
            if (destination === "browser-settings") settingsPanel.activeTab = 6;
            if (bridge.busy) root.jobOrigin = {page: root.page, tab: settingsPanel.activeTab};
            root.loadFields();
            if (destination === "result" || destination === "voice" || destination === "editor") { titleInput.text = ""; root.creationSubjectOverridden = false; root.applyDefaultTeachingSubject(); pasteInput.text = ""; teacherNotesInput.text = ""; root.inputDocumentError = ""; root.preferredCreationDesign = 0; root.selectedFile = ""; root.selectedFileName = "" }
            if (showReview) Qt.callLater(function() { lessonReviewHelp.open() });
        }
        function onSelectionChanged() { root.loadFields(); root.syncNarrationSelection() }
        function onVoiceSettingsChanged() {
            if (!(root.lessonData.narration || {}).voice) {
                root.narrationVoice = bridge.voiceSettings.voice || ""
                root.narrationRate = bridge.voiceSettings.rate || 0
            }
        }
        function onVoiceCatalogChanged() { if (root.page === "voice") Qt.callLater(function() { bridge.completeLegacyNarration() }) }
        function onTeacherProfileSaved() { if (!root.creationSubjectOverridden) root.applyDefaultTeachingSubject() }
        function onComparisonReady() { comparisonDialog.open() }
        function onChanged() { root.rememberJobOrigin(); root.presentationContent = bridge.presentationContent(root.rescue); root.refreshTemplate(); root.showOperationError(); Qt.callLater(root.ensureVoiceThumbnail) }
        function onStatusChanged() { root.showOperationError() }
        function onMemoryChoicesAvailable() { memoryDialog.open() }
        function onCloseMemoryChoicesRequested() { memoryDialog.close() }
        function onMascotPreferencesSaved(visible) {
            if (visible) {
                if (!companion.visible) companion.collapsed = true
                Qt.callLater(function() { bridge.showCompanion(companion) })
            } else companion.hide()
        }
    }
    Timer {
        id: autoSaveTimer; interval: 1800; repeat: false
        onTriggered: {
            if (root.dirty && !bridge.busy && bridge.autoSave(viEdit.text, enEdit.text, lockedCheck.checked)) root.dirty = false
        }
    }

    // Home provides the first-use steps; the complete guide remains available with F1.
    Shortcut { sequence: "F1"; onActivated: helpDialog.open() }
    component Heading: Label { color: root.ink; font.pixelSize: 27; font.weight: Font.Bold; wrapMode: Text.WordWrap }
    component Copy: Label { color: root.muted; font.pixelSize: 13; wrapMode: Text.WordWrap; lineHeight: 1.25; textFormat: Text.PlainText }
    component Caption: Label { color: root.ink; font.pixelSize: 13; font.weight: Font.DemiBold; textFormat: Text.PlainText }
    component MainAction: Button {
        id: action
        property bool danger: false
        property bool primary: false
        property bool attention: false
        property bool subtle: false
        property string iconName: ""
        property string symbol: ""
        implicitHeight: 43
        leftPadding: 17; rightPadding: 17
        font.pixelSize: 13; font.weight: Font.DemiBold
        contentItem: RowLayout {
            spacing: 7
            Item { Layout.fillWidth: true }
            ThemedImage { darkTint: action.attention ? "#172235" : action.primary ? AppTheme.accentText : action.danger ? AppTheme.danger : AppTheme.blue; visible: !!action.iconName; source: action.iconName ? "../assets/actions/" + action.iconName + ".png" : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 23; Layout.preferredHeight: 23; opacity: action.enabled ? 1 : .4 }
            Text { visible: !!action.symbol; text: action.symbol; font.pixelSize: 19; font.weight: Font.DemiBold; color: !action.enabled ? AppTheme.adapt("#96a6bc") : action.danger ? AppTheme.adapt("#b42318") : root.blue; Accessible.ignored: true; verticalAlignment: Text.AlignVCenter }
            Text { text: action.text; font: action.font; color: !action.enabled ? AppTheme.adapt("#96a6bc") : action.attention ? "#172235" : action.primary ? AppTheme.accentText : action.danger ? AppTheme.adapt("#b42318") : root.blue; verticalAlignment: Text.AlignVCenter }
            Item { Layout.fillWidth: true }
        }
        background: Rectangle {
            radius: 9
            color: !action.enabled ? AppTheme.adapt("#e8eef5") : action.attention ? (action.down ? "#e86509" : action.hovered ? "#ff923e" : "#ff7a18") : action.primary ? (action.down ? AppTheme.adapt("#0055d8") : action.hovered ? AppTheme.adapt("#147aff") : AppTheme.accent) : action.danger ? (action.down ? AppTheme.adapt("#fee4e2") : action.hovered ? AppTheme.adapt("#fff0ee") : AppTheme.adapt("#fffafa")) : action.hovered ? AppTheme.adapt("#e8f1ff") : (action.subtle ? "transparent" : AppTheme.surface)
            border.color: action.attention || action.primary || action.subtle ? "transparent" : action.danger ? AppTheme.adapt("#f0b4ae") : AppTheme.adapt("#cbdcf4")
            border.width: action.visualFocus ? 2 : 1
        }
    }
    component Field: TextField {
        implicitHeight: 43; selectByMouse: true
        color: root.ink; placeholderTextColor: AppTheme.adapt("#8a99b0"); font.pixelSize: 13
        leftPadding: 12; rightPadding: 12
        background: Rectangle { radius: 8; color: AppTheme.surface; border.color: parent.activeFocus ? root.blue : root.line }
    }
    component Choice: ComboBox {
        implicitHeight: 43; font.pixelSize: 13
        palette.buttonText: root.ink; palette.text: root.ink; palette.highlight: root.blue
        background: Rectangle { radius: 8; color: AppTheme.surface; border.color: parent.activeFocus ? root.blue : root.line }
    }
    component LibraryFilter: Choice {
        id: filter
        property string emptyLabel: ""
        implicitHeight: 32; font.pixelSize: 11; leftPadding: 8; rightPadding: 20
        displayText: currentIndex === 0 ? emptyLabel : currentText
        Accessible.name: emptyLabel
        ToolTip.visible: hovered
        ToolTip.text: currentText
        indicator: Text { text: "⌄"; color: root.muted; font.pixelSize: 17; x: filter.width - width - 7; y: (filter.height - height) / 2 - 2 }
        contentItem: Text { text: filter.displayText; font: filter.font; color: root.ink; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
        popup.width: Math.max(filter.width, 200)
    }
    component LibraryAction: Button {
        id: control
        property bool danger: false
        property bool subtle: false
        implicitHeight: 32; leftPadding: 8; rightPadding: 8; font.pixelSize: 11; font.weight: Font.DemiBold
        contentItem: Text { text: control.text; font: control.font; color: !control.enabled ? AppTheme.adapt("#96a6bc") : control.danger ? AppTheme.adapt("#b14828") : root.blue; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        background: Rectangle { radius: 6; color: !control.enabled ? AppTheme.adapt("#edf1f7") : control.checked || control.down ? AppTheme.adapt("#dfebfb") : control.hovered ? AppTheme.adapt("#eaf3ff") : control.subtle ? "transparent" : AppTheme.surface; border.color: control.checked || control.visualFocus ? root.blue : control.subtle ? "transparent" : AppTheme.adapt("#cbdcf4"); border.width: control.visualFocus ? 2 : 1 }
    }
    component LibraryRowAction: MainAction {
        implicitHeight: 34; leftPadding: 12; rightPadding: 12; font.pixelSize: 12
    }
    component LibraryDownloadButton: Button {
        id: downloadButton
        implicitWidth: 34; implicitHeight: 34; padding: 6
        Accessible.name: "Tải bài giảng"
        ToolTip.visible: hovered; ToolTip.delay: 400; ToolTip.text: "Tải bài giảng"
        contentItem: ThemedImage { darkTint: AppTheme.blue; source: "../assets/actions/download.png"; sourceSize.width: 48; sourceSize.height: 48; fillMode: Image.PreserveAspectFit; opacity: downloadButton.enabled ? 1 : .35; Accessible.ignored: true }
        background: Rectangle { radius: 6; color: !downloadButton.enabled ? AppTheme.disabledSurface : downloadButton.down ? AppTheme.selected : downloadButton.hovered ? AppTheme.hover : AppTheme.surface; border.color: downloadButton.visualFocus ? root.blue : root.line; border.width: downloadButton.visualFocus ? 2 : 1 }
    }
    component LibraryTrashButton: Button {
        id: trashButton
        implicitWidth: 34; implicitHeight: 34; padding: 7
        Accessible.name: "Xóa bài giảng"
        ToolTip.visible: hovered; ToolTip.delay: 400; ToolTip.text: "Xóa bài giảng"
        contentItem: ThemedImage { darkTint: AppTheme.danger; source: "../assets/actions/trash-red.svg"; sourceSize.width: 40; sourceSize.height: 40; fillMode: Image.PreserveAspectFit; opacity: trashButton.enabled ? 1 : .35; Accessible.ignored: true }
        background: Rectangle { radius: 6; color: !trashButton.enabled ? AppTheme.adapt("#edf1f7") : trashButton.down ? AppTheme.adapt("#fee4e2") : trashButton.hovered ? AppTheme.adapt("#fff0ee") : AppTheme.adapt("#fffafa"); border.color: trashButton.visualFocus ? AppTheme.adapt("#c63434") : "transparent" }
    }
    component LibraryCheck: CheckBox {
        id: control
        property string lessonIdentity: ""
        implicitHeight: 32; padding: 4; spacing: 5; font.pixelSize: 11
        indicator: Rectangle {
            implicitWidth: 16; implicitHeight: 16; x: control.leftPadding; y: Math.round((control.height - height) / 2)
            radius: 3; color: control.checkState === Qt.Unchecked ? AppTheme.surface : AppTheme.accent
            border.color: control.visualFocus || control.hovered || control.checkState !== Qt.Unchecked ? root.blue : AppTheme.adapt("#aebed2")
            border.width: control.visualFocus ? 2 : 1
            Text { anchors.centerIn: parent; text: control.checkState === Qt.PartiallyChecked ? "−" : "✓"; visible: control.checkState !== Qt.Unchecked; color: AppTheme.accentText; font.pixelSize: 12; font.bold: true }
        }
        MouseArea {
            anchors.fill: parent; enabled: !!control.lessonIdentity; preventStealing: true
            property point pressPoint
            property bool moved: false
            onPressed: function(mouse) {
                pressPoint = Qt.point(mouse.x, mouse.y); moved = false
                root.beginLibraryDrag(control.lessonIdentity, this, mouse.x, mouse.y)
            }
            onPositionChanged: function(mouse) {
                if (pressed && Math.hypot(mouse.x - pressPoint.x, mouse.y - pressPoint.y) > Qt.styleHints.startDragDistance) {
                    moved = true; root.moveLibraryDrag(this, mouse.x, mouse.y)
                }
            }
            onReleased: root.endLibraryDrag()
            onCanceled: root.endLibraryDrag()
            onClicked: function(mouse) { if (!moved) root.selectLibraryLesson(control.lessonIdentity, !control.checked, mouse.modifiers) }
        }
    }
    component Surface: Rectangle { color: AppTheme.surface; radius: 16; border.color: root.line }
    component LessonSurface: Surface {
        id: lessonSurface
        required property string lessonId
        property var selectionExclusions: []
        Component.onCompleted: root.libraryCardItems[lessonId] = lessonSurface
        Component.onDestruction: { if (root && root.libraryCardItems && root.libraryCardItems[lessonId] === lessonSurface) delete root.libraryCardItems[lessonId] }
        readonly property bool selectable: root.page === "library"
        readonly property bool selected: selectable && root.selectedLessons.indexOf(lessonId) >= 0
        border.color: selected ? AppTheme.adapt("#dce8f8") : root.line
        color: selected ? AppTheme.adapt("#f2f7ff") : selectionArea.containsMouse ? AppTheme.adapt("#fafcff") : AppTheme.surface
        MouseArea {
            id: selectionArea; objectName: "lessonSelectionArea_" + lessonSurface.lessonId
            anchors.fill: parent; enabled: lessonSurface.selectable
            hoverEnabled: true; cursorShape: Qt.PointingHandCursor; preventStealing: true
            property point pressPoint
            property bool moved: false
            onPressed: function(mouse) {
                for (const item of lessonSurface.selectionExclusions) {
                    if (item && item.visible && item.contains(item.mapFromItem(selectionArea, mouse.x, mouse.y))) {
                        mouse.accepted = false; return
                    }
                }
                pressPoint = Qt.point(mouse.x, mouse.y); moved = false
                root.beginLibraryDrag(lessonSurface.lessonId, selectionArea, mouse.x, mouse.y)
            }
            onPositionChanged: function(mouse) {
                if (pressed && Math.hypot(mouse.x - pressPoint.x, mouse.y - pressPoint.y) > Qt.styleHints.startDragDistance) {
                    moved = true; root.moveLibraryDrag(selectionArea, mouse.x, mouse.y)
                }
            }
            onReleased: root.endLibraryDrag()
            onCanceled: root.endLibraryDrag()
            onClicked: function(mouse) {
                if (moved) return
                // Disabled action buttons must not turn into card-selection targets.
                for (const item of lessonSurface.selectionExclusions) {
                    if (item && item.visible && item.contains(item.mapFromItem(selectionArea, mouse.x, mouse.y))) return
                }
                root.selectLibraryLesson(lessonSurface.lessonId, !lessonSurface.selected, mouse.modifiers)
            }
        }
    }
    component Pill: Rectangle {
        property string text: ""
        property color tone: root.blue
        implicitHeight: 28; implicitWidth: pillText.implicitWidth + 22; radius: 14
        color: Qt.rgba(tone.r, tone.g, tone.b, 0.08)
        Label { id: pillText; anchors.centerIn: parent; text: parent.text; color: parent.tone; font.pixelSize: 11; font.weight: Font.DemiBold }
    }
    component LessonStatus: Button {
        id: statusButton
        required property var lessonRow
        objectName: "lessonStatus_" + lessonRow.id
        text: statusBadge.text
        implicitWidth: 96; implicitHeight: 36; padding: 0
        enabled: !bridge.busy && !bridge.narrationBusy
        Accessible.name: statusBadge.description + ". Chọn hoặc tạo giọng đọc."
        ToolTip.visible: hovered; ToolTip.delay: 500
        ToolTip.text: statusBadge.description + "\nBấm để chọn hoặc tạo giọng đọc."
        contentItem: Item {
            implicitWidth: statusBadge.implicitWidth; implicitHeight: statusBadge.implicitHeight
            LibraryVoiceBadge { id: statusBadge; objectName: "lessonNarrationBadge_" + statusButton.lessonRow.id; anchors.centerIn: parent; audio: statusButton.lessonRow.narration || ({}); Accessible.ignored: true }
        }
        background: Rectangle { anchors.horizontalCenter: parent.horizontalCenter; width: Math.max(36, statusBadge.implicitWidth + 20); radius: 14; color: statusButton.hovered ? (AppTheme.dark ? Qt.lighter(statusBadge.fill, 1.1) : Qt.darker(statusBadge.fill, 1.04)) : statusBadge.fill; border.color: statusButton.visualFocus ? root.blue : statusBadge.outline; border.width: statusButton.visualFocus ? 2 : 1 }
        onClicked: bridge.openLessonNarration(lessonRow.id)
    }

    RowLayout {
        anchors.fill: parent; spacing: 0; enabled: !bridge.storageControls.moving
        Rectangle {
            Layout.preferredWidth: 216; Layout.fillHeight: true; color: AppTheme.surface
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: root.line }
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 20; spacing: 8
                RowLayout {
                    Layout.topMargin: 13; Layout.bottomMargin: 3; spacing: 9
                    Image { source: "book.svg"; sourceSize.width: 35; sourceSize.height: 35; Layout.preferredWidth: 35; Layout.preferredHeight: 35 }
                    Label { text: "Bili<span style='color:#ff7d2b'>Class</span>"; textFormat: Text.RichText; color: root.ink; font.pixelSize: 25; font.weight: Font.Bold }
                }
                Copy { objectName: "brandSlogan"; text: "CHUYỂN NGỮ THÔNG MINH\nNÂNG TẦM BÀI GIẢNG"; font.pixelSize: 9; font.letterSpacing: 0.6; Layout.bottomMargin: root.height < 800 ? 10 : 23 }
                ContentScrollView {
                    id: sidebarNavigation; objectName: "sidebarNavigation"; outerGutter: true; scrollBarGap: 2
                    Layout.fillWidth: true; Layout.fillHeight: true
                    contentWidth: availableWidth
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    ColumnLayout {
                        width: sidebarNavigation.availableWidth; spacing: 8
                        Repeater {
                            model: [{key:"home", label:"Trang chủ", icon:"home"}, {key:"new", label:"Chuyển đổi bài giảng", icon:"bilingual"}, {key:"voice", label:"Tạo giọng đọc bài giảng", icon:"narration"}, {key:"library", label:"Bài giảng", icon:"lessons"}, {key:"classroom", label:"Lớp học", icon:"classroom"}].filter(function(row) { return bridge.experimentalTeaching || row.key !== "classroom" })
                            delegate: NavigationItem {
                                required property var modelData
                                objectName: "navigation" + modelData.key
                                selected: root.page === modelData.key || (modelData.key === "library" && ["editor", "result"].indexOf(root.page) >= 0) || (modelData.key === "new" && root.page === "chatgpt") || (modelData.key === "classroom" && root.page === "reports")
                                text: modelData.label; iconName: modelData.icon
                                Layout.fillWidth: true
                                onClicked: root.go(modelData.key)
                            }
                        }
                    }
                }
                NavigationItem { objectName: "navigationsettings"; text: "Cài đặt"; iconName: "settings"; selected: ["settings", "reference"].indexOf(root.page) >= 0; Layout.fillWidth: true; onClicked: root.go("settings") }
                Button {
                    objectName: "openCompanion"
                    visible: bridge.mascotSettings.visible
                    Layout.fillWidth: true; implicitHeight: 58
                    Accessible.name: companion.visible ? "Ẩn trợ giảng nổi" : "Mở trợ giảng nổi"
                    onClicked: { if (companion.visible) companion.hide(); else bridge.showCompanion(companion) }
                    background: Rectangle { radius: 11; color: parent.hovered ? AppTheme.adapt("#e6f1ff") : AppTheme.adapt("#f4f8fe") }
                    contentItem: RowLayout {
                        spacing: 7
                        Mascot { character: bridge.settings.mascot; expression: bridge.mascotState; reducedMotion: bridge.mascotSettings.reduced_motion; accessories: false; Layout.preferredWidth: 42; Layout.preferredHeight: 48 }
                        Label { objectName: "toggleCompanionLabel"; text: companion.visible ? "Ẩn trợ giảng nổi" : "Mở trợ giảng nổi"; color: root.blue; font.pixelSize: 12; font.weight: Font.DemiBold; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                    }
                }
                Rectangle { Layout.fillWidth: true; height: 1; color: root.line; Layout.topMargin: 14; Layout.bottomMargin: 12 }
                RowLayout {
                    Layout.fillWidth: true; spacing: 10
                    Item {
                        Layout.preferredWidth: 40; Layout.preferredHeight: 40
                        SchoolLogo {
                            id: sidebarSchoolLogo; objectName: "sidebarSchoolLogo"
                            anchors.fill: parent; source: bridge.schoolLogoUrl; roundMask: bridge.schoolLogoRound
                            visible: status === Image.Ready
                            Accessible.name: "Logo trường"
                        }
                        Rectangle {
                            objectName: "sidebarProfileInitial"
                            anchors.centerIn: parent; width: 36; height: 36; radius: 18; color: AppTheme.adapt("#fff0df")
                            visible: sidebarSchoolLogo.status !== Image.Ready
                            Label { anchors.centerIn: parent; text: (bridge.settings.teacher || "G").charAt(0).toUpperCase(); color: AppTheme.adapt("#ab611f"); font.weight: Font.Bold }
                        }
                    }
                    ColumnLayout { Layout.fillWidth: true; spacing: 3
                        Label { objectName: "sidebarTeacherName"; text: bridge.settings.teacher; color: root.ink; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.Wrap; textFormat: Text.PlainText }
                        Copy { text: bridge.settings.school || "Giáo viên · Local"; font.pixelSize: 10; Layout.fillWidth: true; wrapMode: Text.Wrap; textFormat: Text.PlainText }
                    }
                }
                MainAction { objectName: "sidebarHelpButton"; text: "Hướng dẫn · F1"; implicitHeight: 32; subtle: true; Layout.alignment: Qt.AlignHCenter; onClicked: helpDialog.open() }
                Copy { objectName: "sidebarAppVersion"; text: (bridge.developmentMode ? "Bản nguồn · " : "Phiên bản · ") + bridge.appVersion; font.pixelSize: 9; Layout.topMargin: 6; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                Label {
                    objectName: "applicationCopyright"
                    text: "Copyright © 2026 Nguyễn Diệu Linh\nGiáo viên Tin học\nTrường THPT Vân\u00a0Cốc\nAll rights reserved."
                    color: root.muted; font.pixelSize: 9; textFormat: Text.PlainText
                    wrapMode: Text.WordWrap; Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter; Layout.topMargin: 3
                }
            }
        }
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 0
            Item {
                objectName: "mainPageArea"
                Layout.fillWidth: true; Layout.fillHeight: true
                Item {
                    id: libraryPinnedHeader; objectName: "libraryPinnedHeader"
                    anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right; anchors.margins: 30
                    height: libraryHeaderContent.implicitHeight; visible: root.page === "library"
                    ColumnLayout {
                        id: libraryHeaderContent; anchors.fill: parent; spacing: 12
                        ColumnLayout {
                            visible: root.page === "library"; Layout.fillWidth: true; spacing: 5
                            Heading { objectName: "libraryHomeHeading"; text: "Thư viện bài giảng"; font.pixelSize: 28; Layout.fillWidth: true }
                            RowLayout {
                                Layout.fillWidth: true; spacing: 12
                                Copy { objectName: "libraryDescription"; text: "Tìm đúng bài, chọn bản giọng và mở để dạy hoặc tải PowerPoint."; Layout.fillWidth: true }
                                MainAction { id: libraryManagementAction; objectName: "libraryManagementButton"; text: "Chia sẻ & quản lý"; subtle: true; implicitHeight: 28; onClicked: libraryManagementMenu.popup() }
                                Menu { id: libraryManagementMenu; parent: libraryManagementAction; x: parent.width - width; y: parent.height
                                    MenuItem { objectName: "importSharedLessonButton"; text: "Nhận gói bài từ giáo viên khác…"; onTriggered: packOpen.open() }
                                    MenuItem { text: "Thùng rác (" + bridge.trashedLessons.length + ")"; onTriggered: lessonTrashDialog.open() }
                                }
                            }
                        }
                        RowLayout { visible: root.page === "library"; Layout.fillWidth: true; spacing: 12
                            Field {
                                id: search; objectName: "librarySearch"; Layout.fillWidth: true
                                placeholderText: "Tìm tên bài, môn, khối… có thể gõ không dấu"
                                rightPadding: clearLibrarySearch.visible ? 44 : 12
                                onTextChanged: root.libraryPage = 1
                                LibraryAction {
                                    id: clearLibrarySearch; objectName: "libraryClearSearch"
                                    anchors.right: parent.right; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                    width: 32; height: 32; text: "×"; font.pixelSize: 21; subtle: true
                                    visible: search.text.length > 0
                                    Accessible.name: "Xóa nội dung tìm kiếm"
                                    onClicked: { search.clear(); search.forceActiveFocus() }
                                }
                            }
                            SelectBox { objectName: "lessonSortOrder"; model: ["Mới tạo nhất", "Tạo lâu nhất", "Mới cập nhật", "Tên bài A–Z"]; currentIndex: ["created_desc", "created_asc", "updated_desc", "title_asc"].indexOf(bridge.lessonOrder); Layout.preferredWidth: 168; onActivated: { root.libraryPage = 1; bridge.setLessonOrder(["created_desc", "created_asc", "updated_desc", "title_asc"][currentIndex]) } }
                            LibraryAction {
                                objectName: "libraryViewToggle"
                                readonly property bool cardView: bridge.libraryView === "grid"
                                implicitWidth: 40; implicitHeight: 40; Layout.preferredWidth: 40
                                Accessible.name: cardView ? "Chuyển sang danh sách" : "Chuyển sang thẻ lớn"
                                Accessible.description: cardView ? "Đang xem thẻ lớn 16:9" : "Đang xem danh sách"
                                ToolTip.visible: hovered; ToolTip.delay: 400
                                ToolTip.text: cardView ? "Đang xem thẻ · Bấm để xem danh sách" : "Đang xem danh sách · Bấm để xem thẻ"
                                onClicked: bridge.setLibraryView(cardView ? "list" : "grid")
                                contentItem: Item {
                                    Grid { objectName: "libraryGridIcon"; anchors.centerIn: parent; columns: 2; spacing: 4; visible: bridge.libraryView === "grid"
                                        Repeater { model: 4; Rectangle { width: 8; height: 8; radius: 1; color: AppTheme.adapt("#eaf3ff"); border.width: 1.5; border.color: root.blue } }
                                    }
                                    Column { objectName: "libraryListIcon"; anchors.centerIn: parent; spacing: 5; visible: bridge.libraryView !== "grid"
                                        Repeater { model: 3; Row { spacing: 4
                                            Rectangle { width: 3; height: 2; radius: 1; color: root.blue }
                                            Rectangle { width: 13; height: 2; radius: 1; color: root.blue }
                                        } }
                                    }
                                }
                            }
                        }
                        RowLayout { id: libraryToolbar; objectName: "libraryToolbar"; visible: root.page === "library"; Layout.fillWidth: true; spacing: 6
                            RowLayout { objectName: "libraryFilters"; Layout.fillWidth: true; spacing: 6
                                LibraryFilter { id: subjectFilter; objectName: "librarySubjectFilter"; emptyLabel: "Môn học"; Layout.fillWidth: true; Layout.minimumWidth: 78; Layout.preferredWidth: 94; model: bridge.librarySubjects; textRole: "label"; valueRole: "id"; onActivated: root.libraryPage = 1 }
                                LibraryFilter { id: gradeFilter; objectName: "libraryGradeFilter"; emptyLabel: "Khối lớp"; Layout.fillWidth: true; Layout.minimumWidth: 72; Layout.preferredWidth: 80; model: bridge.libraryGrades; textRole: "label"; valueRole: "id"; onActivated: root.libraryPage = 1 }
                                LibraryFilter { id: stateFilter; objectName: "libraryStateFilter"; emptyLabel: "Trạng thái"; Layout.fillWidth: true; Layout.minimumWidth: 80; Layout.preferredWidth: 90; textRole: "label"; valueRole: "id"; model: [{id:"",label:"Tất cả trạng thái"},{id:"ready",label:"Đã duyệt nội dung"},{id:"review",label:"Cần xử lý"},{id:"draft",label:"Bản nháp"}]; onActivated: root.libraryPage = 1 }
                                LibraryFilter { id: voiceFilter; objectName: "libraryVoiceFilter"; emptyLabel: "Giọng đọc"; Layout.fillWidth: true; Layout.minimumWidth: 78; Layout.preferredWidth: 92; textRole: "label"; valueRole: "id"; model: [{id:"",label:"Tất cả giọng đọc"},{id:"en",label:"Có bản giọng Anh"},{id:"vi",label:"Có bản giọng Việt"},{id:"both",label:"Có bản giọng Việt–Anh"},{id:"none",label:"Chưa có giọng"}]; onActivated: root.libraryPage = 1 }
                            }
                            LibraryAction { objectName: "libraryClearFilters"; text: "↺"; font.pixelSize: 18; Layout.preferredWidth: 30; Accessible.name: "Xóa bộ lọc"; ToolTip.visible: hovered; ToolTip.text: "Xóa bộ lọc"; onClicked: { search.clear(); subjectFilter.currentIndex = 0; gradeFilter.currentIndex = 0; stateFilter.currentIndex = 0; voiceFilter.currentIndex = 0; root.libraryPage = 1 } }
                            LibraryCheck { objectName: "librarySelectAll"; text: "Chọn tất cả"; ToolTip.visible: hovered; ToolTip.delay: 600; ToolTip.text: "Chọn toàn bộ " + root.libraryResult.total + " bài khớp bộ lọc, kể cả các trang khác.\nĐổi bộ lọc sẽ bỏ chọn."; Accessible.description: ToolTip.text; checkState: !root.selectedLessons.length ? Qt.Unchecked : root.selectedLessons.length === root.libraryResult.total ? Qt.Checked : Qt.PartiallyChecked; nextCheckState: function() { return checkState === Qt.Checked ? Qt.Unchecked : Qt.Checked }; enabled: root.libraryResult.total > 0; onClicked: root.selectedLessons = checked ? root.libraryResult.ids.slice() : [] }
                            LibraryAction { objectName: "libraryDeselectAll"; text: "Bỏ chọn"; subtle: true; enabled: root.selectedLessons.length > 0; onClicked: root.selectedLessons = [] }
                            LibraryAction { objectName: "libraryDownloadSelected"; text: "Tải đã chọn"; ToolTip.visible: hovered; ToolTip.text: "Tải " + root.selectedLessons.length + " bài đã chọn"; enabled: root.selectedLessons.length > 0 && !bridge.busy && !bridge.narrationBusy; onClicked: root.downloadLibraryLessons(root.selectedLessons) }
                            LibraryAction { objectName: "libraryDeleteSelected"; text: "Xóa đã chọn"; danger: true; ToolTip.visible: hovered; ToolTip.text: "Đưa " + root.selectedLessons.length + " bài đã chọn vào thùng rác"; enabled: root.selectedLessons.length > 0 && !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !root.classroom.running; onClicked: { bulkDeleteDialog.identities = root.selectedLessons.slice(); bulkDeleteDialog.open() } }
                            Label {
                                objectName: "libraryResultCount"
                                text: root.selectedLessons.length ? "Đã chọn " + root.selectedLessons.length + " bài" : root.libraryResult.total + (root.libraryFiltersActive ? " kết quả" : " bài")
                                color: root.muted; font.pixelSize: 11; Layout.leftMargin: 3
                                Layout.minimumWidth: implicitWidth
                                HoverHandler { id: libraryCountHover }
                                ToolTip.visible: libraryCountHover.hovered; ToolTip.delay: 600
                                ToolTip.text: "Tìm thấy " + root.libraryResult.total + " trong tổng số " + bridge.lessons.length + " bài giảng." + (root.selectedLessons.length ? "\nĐã chọn " + root.selectedLessons.length + " bài. Đổi bộ lọc sẽ bỏ chọn." : "")
                                Accessible.name: text; Accessible.description: ToolTip.text
                            }
                        }
                    }
                }
                ContentScrollView {
                    id: libraryHomeScroll; objectName: "libraryHomeScroll"; outerGutter: true; barObjectName: "libraryScrollBar"; anchors.fill: parent; anchors.margins: 30
                    anchors.topMargin: root.page === "library" ? libraryPinnedHeader.y + libraryPinnedHeader.height + 12 : 30
                    visible: root.page === "home" || root.page === "library"
                    contentWidth: availableWidth
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    ColumnLayout {
                        width: libraryHomeScroll.availableWidth; spacing: root.page === "home" ? 18 : 12
                        HomeWelcome {
                            objectName: "homeWelcome"
                            visible: root.page === "home"; Layout.fillWidth: true; bridge: root.appBridge
                            inputError: root.inputDocumentError
                            onChooseDocument: { root.go("new"); documentOpen.open() }
                            onDocumentDropped: function(urls) { if (root.acceptInputDocuments(urls)) root.go("new") }
                            onContinueWork: root.go(bridge.narrationBusy ? "voice" : "new")
                            onOpenLibrary: root.go("library")
                            onOpenNarration: root.go("voice")
                            onOpenTeaching: { companion.collapsed = false; companion.choosingLesson = !bridge.teachingSession.state.bound; bridge.showCompanion(companion) }
                            onOpenClassroom: root.go("classroom")
                        }
                        Surface {
                            objectName: "updateBanner"
                            visible: root.page === "home" && bridge.updateState.available
                            Layout.fillWidth: true; implicitHeight: bridge.updateState.downloading ? 114 : 85
                            ColumnLayout { anchors.fill: parent; anchors.margins: 17; spacing: 8
                                RowLayout { Layout.fillWidth: true; spacing: 12
                                    ColumnLayout { Layout.fillWidth: true; spacing: 3
                                        Caption { text: "Bản cài BiliClass " + bridge.updateState.version; font.pixelSize: 15 }
                                        Copy { text: bridge.updateState.message; Layout.fillWidth: true }
                                    }
                                    MainAction { text: bridge.updateState.ready ? "Mở bản mới" : "Cập nhật"; primary: true; enabled: !bridge.updateState.downloading && !bridge.busy && !root.classroom.running; onClicked: bridge.updateState.ready ? bridge.applyDownloadedUpdate() : bridge.downloadUpdate() }
                                    MainAction { visible: bridge.updateState.downloading; text: "Hủy tải"; onClicked: bridge.cancelUpdate() }
                                }
                                ProgressBar { visible: bridge.updateState.downloading; Layout.fillWidth: true; value: bridge.updateState.progress / 100 }
                            }
                        }
                        Surface { visible: root.page === "library" && bridge.lessons.length > 0 && root.libraryResult.total === 0; Layout.fillWidth: true; implicitHeight: 106
                            ColumnLayout { anchors.fill: parent; anchors.margins: 20; spacing: 7
                                Caption { text: "Không có bài phù hợp" }
                                Copy { text: "Thử từ khóa ngắn hơn hoặc dùng Xóa bộ lọc để xem lại toàn bộ bài."; Layout.fillWidth: true }
                            }
                        }
                        Surface {
                            visible: root.page === "library" && bridge.lessons.length === 0; Layout.fillWidth: true; implicitHeight: 202
                            ColumnLayout { anchors.centerIn: parent; spacing: 13; Label { text: "Bài giảng đầu tiên bắt đầu từ đây"; color: root.ink; font.pixelSize: 19; font.weight: Font.DemiBold }
                                Copy { text: "Tải PPTX, DOCX, PDF có văn bản, TXT hoặc dán nội dung."; Layout.alignment: Qt.AlignHCenter }
                                MainAction { visible: root.page === "library"; text: "Chuyển đổi bài giảng"; primary: true; Layout.alignment: Qt.AlignHCenter; onClicked: root.go("new") } }
                        }
                        ColumnLayout {
                            visible: root.page === "library" && !root.libraryLarge; Layout.fillWidth: true; spacing: 8
                            Repeater {
                                model: root.page === "library" && !root.libraryLarge ? root.libraryResult.rows : []
                                delegate: LessonSurface {
                                    required property var modelData
                                    required property int index
                                    lessonId: modelData.id
                                    selectionExclusions: [rowCheck, rowStatus, rowContentWarning, rowOpen, rowVoice, rowDownload, rowMore, rowDelete]
                                    objectName: "lessonCard_" + modelData.id
                                    Layout.fillWidth: true; implicitHeight: Math.max(92, lessonRow.implicitHeight + 24)
                                    GridLayout {
                                        id: lessonRow; anchors.fill: parent; anchors.margins: 12
                                        readonly property bool wideActions: width >= 1000
                                        columns: wideActions ? 5 : 4; columnSpacing: 12; rowSpacing: 6
                                        LibraryCheck { id: rowCheck; lessonIdentity: modelData.id; objectName: "lessonSelect_" + modelData.id; visible: root.page === "library"; Layout.column: 0; Layout.row: 0; Layout.rowSpan: lessonRow.wideActions ? 1 : 2; Layout.preferredWidth: 28; checked: root.selectedLessons.indexOf(modelData.id) >= 0; Accessible.name: "Chọn " + modelData.title; onClicked: root.selectLibraryLesson(modelData.id, checked) }
                                        Rectangle { Layout.column: 1; Layout.row: 0; Layout.rowSpan: lessonRow.wideActions ? 1 : 2; width: 36; height: 38; radius: 8; color: AppTheme.adapt("#edf4ff"); Label { anchors.centerIn: parent; text: "VI\nEN"; color: root.blue; font.pixelSize: 12; font.weight: Font.Bold; lineHeight: 1.1 } }
                                        ColumnLayout { Layout.column: 2; Layout.row: 0; Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 3
                                            Label { objectName: "lessonTitle_" + modelData.id; text: modelData.title; color: root.ink; font.pixelSize: 15; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true; Layout.minimumWidth: 0 }
                                            Copy { Layout.fillWidth: true; text: modelData.subject + "  ·  " + modelData.education_level + " " + modelData.grade + "  ·  " + (modelData.slides_count ? modelData.slides_count + " slide" : modelData.segments_count + " phần"); font.pixelSize: 12 }
                                            LibraryContentWarning { id: rowContentWarning; objectName: "lessonContentWarning_" + modelData.id; showWarnings: bridge.experimentalTeaching; review: modelData.review || ({}); enabled: !bridge.busy; onRequestInspect: { root.libraryReviewTarget = modelData.id; bridge.openLesson(modelData.id) } Layout.fillWidth: true; Layout.minimumWidth: 0 }
                                            Copy { objectName: "lessonCreated_" + modelData.id; text: (modelData.created_at_estimated ? "Lưu: " : "Tạo: ") + bridge.lessonDateLabel(modelData.created_at); font.pixelSize: 10; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.topMargin: 8 }
                                        }
                                        LessonStatus { id: rowStatus; lessonRow: modelData; Layout.column: 3; Layout.row: 0; Layout.minimumWidth: 96; Layout.preferredWidth: 96; Layout.maximumWidth: 96 }
                                        RowLayout {
                                        Layout.column: lessonRow.wideActions ? 4 : 2; Layout.row: lessonRow.wideActions ? 0 : 1; Layout.columnSpan: lessonRow.wideActions ? 1 : 2; Layout.fillWidth: !lessonRow.wideActions; spacing: 8
                                        LibraryRowAction { id: rowOpen; objectName: "lessonOpen_" + modelData.id; text: bridge.openingTeachingLesson === modelData.id ? "Đang mở…" : "Mở PowerPoint"; Layout.minimumWidth: 128; Layout.preferredWidth: 128; Layout.maximumWidth: 128; primary: true; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; ToolTip.visible: hovered; ToolTip.text: "Mở bài và gắn Mascot với bài này. Bấm F5 khi sẵn sàng trình chiếu."; onClicked: bridge.openTeachingLibraryLesson(modelData.id) }
                                        LibraryRowAction { id: rowVoice; objectName: "lessonNarrate_" + modelData.id; text: "Tạo giọng đọc"; enabled: !bridge.busy && !bridge.narrationBusy; ToolTip.visible: hovered; ToolTip.text: "Chọn ngôn ngữ, giọng và vị trí loa; không mở PowerPoint."; onClicked: bridge.openLessonNarration(modelData.id) }
                                        LibraryDownloadButton { id: rowDownload; objectName: "lessonDownload_" + modelData.id; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: root.downloadLibraryLessons([modelData.id]) }
                                        Item { visible: !lessonRow.wideActions; Layout.fillWidth: true }
                                        LibraryAction { id: rowMore; objectName: "lessonMore_" + modelData.id; text: "⋯"; font.pixelSize: 20; implicitHeight: 34; Accessible.name: "Thao tác với " + modelData.title; onClicked: rowMenu.popup() }
                                        Menu { id: rowMenu; parent: rowMore; x: parent.width - width; y: parent.height
                                            MenuItem { objectName: "lessonPreview_" + modelData.id; text: "Xem bài giảng"; enabled: !bridge.busy && !bridge.narrationBusy; onTriggered: bridge.openLesson(modelData.id) }
                                            MenuItem { objectName: "lessonEdit_" + modelData.id; text: "Đổi tên / thông tin bài"; enabled: !bridge.busy && !bridge.powerpointState.active; onTriggered: { metadataDialog.lessonData = modelData; metadataDialog.open() } }
                                        }
                                        LibraryTrashButton { id: rowDelete; objectName: "lessonDelete_" + modelData.id; Accessible.name: "Xóa bài giảng " + modelData.title; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !root.classroom.running; onClicked: { deleteLessonDialog.lessonId = modelData.id; deleteLessonDialog.lessonTitle = modelData.title; deleteLessonDialog.open() } }

                                        }
                                    }
                                }
                            }
                        }
                        GridLayout {
                            id: libraryGrid; objectName: "libraryGrid"
                            visible: root.libraryLarge; Layout.fillWidth: true
                            columns: Math.max(1, Math.min(4, Math.floor((width + 16) / 330)))
                            columnSpacing: 16; rowSpacing: 16
                            Repeater {
                                model: root.libraryLarge ? root.libraryResult.rows : []
                                delegate: LessonSurface {
                                    id: largeCard
                                    required property var modelData
                                    lessonId: modelData.id
                                    selectionExclusions: [cardCheck, cardStatus, cardContentWarning, cardOpen, cardVoice, cardDownload, largeCardMore, largeCardDelete]
                                    readonly property var cover: bridge.libraryCovers.images[modelData.id] || ({loading:true,image:""})
                                    objectName: "lessonCard_" + modelData.id
                                    Layout.fillWidth: true; Layout.preferredWidth: 1
                                    Layout.alignment: Qt.AlignTop
                                    implicitHeight: cardContent.implicitHeight + 28
                                    ColumnLayout {
                                        id: cardContent; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; spacing: 10
                                        RowLayout { Layout.fillWidth: true
                                            LibraryCheck { id: cardCheck; lessonIdentity: modelData.id; objectName: "lessonSelect_" + modelData.id; checked: root.selectedLessons.indexOf(modelData.id) >= 0; Accessible.name: "Chọn " + modelData.title; onClicked: root.selectLibraryLesson(modelData.id, checked) }
                                            Item { Layout.fillWidth: true }
                                            LessonStatus { id: cardStatus; lessonRow: modelData }
                                        }
                                        Rectangle {
                                            objectName: "lessonCover_" + modelData.id
                                            Layout.fillWidth: true; implicitHeight: width * 9 / 16
                                            color: AppTheme.adapt("#e9eef5"); radius: 8; clip: true
                                            Image { objectName: "lessonCoverImage_" + modelData.id; anchors.fill: parent; source: largeCard.cover.image; asynchronous: true; sourceSize.width: 640; sourceSize.height: 360; fillMode: Image.PreserveAspectFit }
                                            Column { visible: !largeCard.cover.image; anchors.centerIn: parent; spacing: 6
                                                Label { text: largeCard.cover.loading ? "Đang tải ảnh slide…" : "Chưa có ảnh xem trước"; color: root.muted; font.pixelSize: 12; anchors.horizontalCenter: parent.horizontalCenter }
                                                Label { text: "Mở bài để xem nội dung"; visible: !largeCard.cover.loading; color: root.muted; font.pixelSize: 11; anchors.horizontalCenter: parent.horizontalCenter }
                                            }
                                        }
                                        Label { objectName: "lessonTitle_" + modelData.id; text: modelData.title; color: root.ink; font.pixelSize: 15; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true; Layout.minimumWidth: 0 }
                                        RowLayout { Layout.fillWidth: true; spacing: 10
                                            Copy { objectName: "lessonCardMetadata_" + modelData.id; Layout.fillWidth: true; Layout.minimumWidth: 0; font.pixelSize: 12; wrapMode: Text.NoWrap; elide: Text.ElideRight; text: modelData.subject + " · " + modelData.education_level + " " + modelData.grade + " · " + (modelData.slides_count ? modelData.slides_count + " slide" : modelData.segments_count + " phần")
                                                ToolTip.visible: metadataHover.hovered && truncated; ToolTip.text: text
                                                HoverHandler { id: metadataHover }
                                            }
                                            Copy { objectName: "lessonCardCreated_" + modelData.id; font.pixelSize: 10; text: bridge.lessonDateLabel(modelData.created_at).split(" · ").pop(); Layout.minimumWidth: implicitWidth; Layout.alignment: Qt.AlignRight }
                                        }
                                        LibraryContentWarning { id: cardContentWarning; objectName: "lessonContentWarning_" + modelData.id; showWarnings: bridge.experimentalTeaching; review: modelData.review || ({}); enabled: !bridge.busy; onRequestInspect: { root.libraryReviewTarget = modelData.id; bridge.openLesson(modelData.id) } Layout.fillWidth: true; Layout.minimumWidth: 0 }
                                        MainAction { id: cardOpen; objectName: "lessonOpen_" + modelData.id; text: bridge.openingTeachingLesson === modelData.id ? "Đang mở…" : "Mở PowerPoint"; primary: true; Layout.fillWidth: true; onClicked: bridge.openTeachingLibraryLesson(modelData.id); enabled: !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning }
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            MainAction { id: cardVoice; objectName: "lessonNarrate_" + modelData.id; text: "Tạo giọng đọc"; Layout.fillWidth: true; onClicked: bridge.openLessonNarration(modelData.id); enabled: !bridge.busy && !bridge.narrationBusy }
                                            LibraryDownloadButton { id: cardDownload; objectName: "lessonDownload_" + modelData.id; implicitWidth: 40; implicitHeight: 40; onClicked: root.downloadLibraryLessons([modelData.id]); enabled: !bridge.busy && !bridge.narrationBusy }
                                            LibraryAction { id: largeCardMore; objectName: "lessonMore_" + modelData.id; text: "⋯"; font.pixelSize: 20; implicitHeight: 40; Accessible.name: "Thao tác với " + modelData.title; onClicked: largeCardMenu.popup() }
                                            Menu { id: largeCardMenu; parent: largeCardMore; x: parent.width - width; y: parent.height
                                                MenuItem { objectName: "lessonPreview_" + modelData.id; text: "Xem bài giảng"; enabled: !bridge.busy && !bridge.narrationBusy; onTriggered: bridge.openLesson(modelData.id) }
                                                MenuItem { objectName: "lessonEdit_" + modelData.id; text: "Đổi tên / thông tin bài"; enabled: !bridge.busy && !bridge.powerpointState.active; onTriggered: { metadataDialog.lessonData = modelData; metadataDialog.open() } }
                                            }
                                            LibraryTrashButton { id: largeCardDelete; objectName: "lessonDelete_" + modelData.id; implicitHeight: 40; Accessible.name: "Xóa bài giảng " + modelData.title; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !root.classroom.running; onClicked: { deleteLessonDialog.lessonId = modelData.id; deleteLessonDialog.lessonTitle = modelData.title; deleteLessonDialog.open() } }
                                        }
                                    }
                                }
                            }
                            // Keep empty columns when a search returns fewer cards than fit in a row.
                            Repeater {
                                model: root.libraryLarge ? Math.max(0, libraryGrid.columns - root.libraryResult.rows.length) : 0
                                Item { Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0 }
                            }
                        }
                        RowLayout { visible: root.page === "library" && root.libraryResult.pages > 1; Layout.fillWidth: true
                            Copy { text: root.libraryResult.start + "–" + root.libraryResult.end + " / " + root.libraryResult.total + " bài" }
                            Item { Layout.fillWidth: true }
                            MainAction { objectName: "libraryPreviousPage"; text: "Trước"; enabled: root.libraryResult.page > 1; onClicked: root.libraryPage = root.libraryResult.page - 1 }
                            Copy { text: "Trang " + root.libraryResult.page + " / " + root.libraryResult.pages }
                            MainAction { objectName: "libraryNextPage"; text: "Tiếp"; enabled: root.libraryResult.page < root.libraryResult.pages; onClicked: root.libraryPage = root.libraryResult.page + 1 }
                        }
                        Label { visible: bridge.experimentalTeaching && root.page === "home" && root.classroom.sessions.length > 0; text: "Tiết gần đây"; color: root.ink; font.pixelSize: 18; font.weight: Font.DemiBold }
                        Repeater { model: bridge.experimentalTeaching && root.page === "home" ? root.classroom.sessions : []
                            delegate: Surface { required property var modelData; required property int index; visible: index < 3; Layout.fillWidth: true; implicitHeight: 72
                                RowLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                                    ColumnLayout { Layout.fillWidth: true; spacing: 4
                                        Caption { text: modelData.title; Layout.fillWidth: true; elide: Text.ElideRight }
                                        Copy { text: [modelData.lesson_title, modelData.subject, modelData.grade ? "Khối " + modelData.grade : ""].filter(function(value) { return !!value }).join(" · "); Layout.fillWidth: true; font.pixelSize: 11 }
                                    }
                                    Pill { text: modelData.status === "ended" ? "Đã kết thúc" : "Đang mở" }
                                    MainAction { text: "Xem báo cáo"; onClicked: { root.classroom.openReport(modelData.id); root.go("reports") } }
                                }
                            }
                        }

                    }
                }

                ContentScrollView {
                    id: creationScroll; objectName: "creationScroll"; outerGutter: true
                    anchors.fill: parent; anchors.margins: 30; anchors.bottomMargin: creationFooter.height + 12
                    visible: root.page === "new"; contentWidth: availableWidth
                    background: DropArea {
                        objectName: root.selectedFile ? "creationDocumentDrop" : ""
                        anchors.fill: parent; enabled: !!root.selectedFile && !bridge.busy && !bridge.narrationBusy
                        onDropped: function(drop) { if (drop.hasUrls) { root.acceptInputDocuments(drop.urls); drop.acceptProposedAction() } }
                    }
                    ColumnLayout {
                        width: parent.width; spacing: root.compactCreation ? 8 : 12
                        RowLayout { Layout.fillWidth: true
                            Heading { text: "Chuyển đổi bài giảng PowerPoint"; font.pixelSize: root.tightCreation ? 24 : 27; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                            MainAction { objectName: root.selectedFile ? "chooseInputDocumentButton" : ""; visible: !!root.selectedFile; text: "Chọn bài khác"; enabled: !bridge.busy && !bridge.inputDocuments.busy && !bridge.narrationBusy; onClicked: documentOpen.open() }
                            MainAction { objectName: "removeInputDocumentButton"; visible: !!root.selectedFile; text: "Hủy bài đang chọn"; danger: true; symbol: "×"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: root.removeInputDocument() }
                        }
                        Copy { text: "Chọn PowerPoint → Chọn kiểu chuyển đổi → Thiết kế bài giảng → Tạo bài giảng."; Layout.fillWidth: true }
                        PowerPointUpload {
                            objectName: "creationSourceArea"; visible: !root.selectedFile; illustrated: true; compact: true; Layout.fillWidth: true
                            chooseObjectName: root.selectedFile ? "" : "chooseInputDocumentButton"
                            dropObjectName: root.selectedFile ? "" : "creationDocumentDrop"
                            errorObjectName: "creationDocumentError"
                            fileName: bridge.inputDocuments.busy ? "Đang kiểm tra tệp…" : root.selectedFileName; errorText: root.inputDocumentError
                            busy: bridge.busy || bridge.inputDocuments.busy; working: bridge.narrationBusy || !!bridge.browserState.running
                            workingTitle: bridge.narrationBusy ? "Đang tạo giọng đọc" : "Bài giảng đang được chuyển đổi"
                            workingDetail: bridge.narrationBusy ? "Chờ tạo giọng xong hoặc dừng tạo giọng trước khi chuyển đổi bài mới. Các đoạn đã tạo được giữ lại." : "Theo dõi tiến độ; các phần đã xong được lưu lại."
                            progressLabel: bridge.narrationBusy ? "Xem tiến độ tạo giọng" : "Xem tiến độ chuyển đổi"
                            onChooseFile: documentOpen.open()
                            onFilesDropped: function(urls) { root.acceptInputDocuments(urls) }
                            onRemoveFile: root.removeInputDocument()
                            onShowProgress: root.go(bridge.narrationBusy ? "voice" : "chatgpt")
                        }
                        GridLayout {
                            id: creationOverview; objectName: "creationLessonOverview"; visible: !!root.selectedFile
                            Layout.fillWidth: true; columns: creationScroll.availableWidth >= 760 ? 2 : 1; columnSpacing: 24; rowSpacing: 12
                            ColumnLayout {
                                objectName: "creationLessonDetails"; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.alignment: Qt.AlignTop; spacing: 12
                                ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 6
                                    Heading {
                                        objectName: "creationSelectedLessonTitle"
                                        text: titleInput.text || root.selectedFileName.replace(/\.[^.]+$/, "")
                                        font.pixelSize: 20; Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.Wrap
                                        ToolTip.visible: creationTitleHover.hovered
                                        ToolTip.text: root.selectedFileName; ToolTip.delay: 500
                                        HoverHandler { id: creationTitleHover }
                                    }
                                    Copy { Layout.fillWidth: true; text: [root.creationSubject, educationInput.currentText + " " + gradeInput.currentText, "PowerPoint gốc"].filter(function(value) { return !!value }).join(" · ") }
                                }
                                Copy { text: "✓ Đã chọn tệp · Chưa chuyển đổi"; color: AppTheme.success; font.pixelSize: 12; Layout.fillWidth: true }
                                Copy { objectName: "creationSelectedSlideCount"; text: (bridge.inputDocuments.preview.total ? bridge.inputDocuments.preview.total + " slide · " : "") + "Chọn cấu hình chuyển đổi ở bên dưới"; color: root.ink; Layout.fillWidth: true }
                                MainAction { objectName: "creationOpenPowerPoint"; text: "Mở PowerPoint"; Layout.alignment: Qt.AlignLeft; enabled: root.creationPowerPoint && !bridge.busy && !bridge.inputDocuments.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; onClicked: bridge.openInputPowerPoint(root.selectedFile) }
                                Copy { visible: !!root.inputDocumentError; text: root.inputDocumentError; color: AppTheme.warning; Layout.fillWidth: true }
                            }
                            ColumnLayout {
                                Layout.preferredWidth: Math.min(creationScroll.availableWidth >= 1000 ? 304 : 240, creationScroll.availableWidth)
                                Layout.minimumWidth: Layout.preferredWidth; Layout.maximumWidth: Layout.preferredWidth
                                Layout.alignment: Qt.AlignTop | Qt.AlignRight; spacing: 8
                                MainAction { objectName: "creationPreviewButton"; text: root.creationPreviewExpanded ? "Ẩn xem trước" : "Xem trước slide"; subtle: true; implicitHeight: 32; Layout.alignment: Qt.AlignRight; enabled: root.creationPreviewExpanded || !!bridge.inputDocuments.preview.image; onClicked: { if (root.creationPreviewExpanded) root.creationPreviewExpanded = false; else root.showCreationPreview() } }
                                Surface {
                                    objectName: "creationSelectedSlidePreview"; visible: !root.creationPreviewExpanded; Layout.fillWidth: true; implicitHeight: width * 9 / 16; radius: 10; color: AppTheme.adapt("#e9eef5")
                                    Image { objectName: "creationSelectedSlideImage"; anchors.fill: parent; anchors.margins: 3; source: bridge.inputDocuments.preview.image || ""; fillMode: Image.PreserveAspectFit; sourceSize.width: 640; asynchronous: true; cache: true }
                                    BusyIndicator { anchors.centerIn: parent; running: !!bridge.inputDocuments.preview.busy; visible: running }
                                    ColumnLayout { anchors.centerIn: parent; width: parent.width - 24; visible: !bridge.inputDocuments.preview.busy && !bridge.inputDocuments.preview.image
                                        Copy { text: bridge.inputDocuments.preview.error ? "Chưa tải được ảnh slide" : "Xem trước slide"; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; font.pixelSize: 12 }
                                        MainAction { text: "Thử lại"; implicitHeight: 30; Layout.alignment: Qt.AlignHCenter; onClicked: bridge.inputDocuments.retryPreview() }
                                    }
                                    Accessible.role: Accessible.Button; Accessible.name: "Phóng to xem trước slide gốc"
                                    Accessible.onPressAction: if (bridge.inputDocuments.preview.image) root.showCreationPreview()
                                    TapHandler { onTapped: if (bridge.inputDocuments.preview.image) root.showCreationPreview() }
                                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                                }
                            }
                        }
                        TextArea { id: pasteInput; objectName: "lessonContent"; visible: false }
                        Surface {
                            id: creationSlidePreview; objectName: "creationExpandedSlidePreview"
                            visible: !!root.selectedFile && root.creationPreviewExpanded
                            Layout.fillWidth: true; implicitHeight: Math.max(260, Math.min(560, (root.height - 150) * .62)); color: AppTheme.adapt("#e9eef5")
                            Image { objectName: "creationExpandedSlideImage"; anchors.fill: parent; anchors.margins: 6; source: bridge.inputDocuments.preview.image || ""; fillMode: Image.PreserveAspectFit; asynchronous: true; cache: true; sourceSize.width: 1600; opacity: bridge.inputDocuments.preview.busy ? .6 : 1 }
                            BusyIndicator { anchors.centerIn: parent; running: !!bridge.inputDocuments.preview.busy; visible: running }
                            ColumnLayout {
                                visible: !bridge.inputDocuments.preview.image && !bridge.inputDocuments.preview.busy
                                anchors.centerIn: parent; width: parent.width - 70; spacing: 12
                                Copy { text: bridge.inputDocuments.preview.error || "Ảnh slide chưa được tải."; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                MainAction { objectName: "retryCreationSlidePreview"; text: "Tải lại slide"; Layout.alignment: Qt.AlignHCenter; onClicked: bridge.inputDocuments.retryPreview() }
                            }
                        }
                        RowLayout {
                            objectName: "creationSlideNavigation"; visible: !!root.selectedFile && root.creationPreviewExpanded; Layout.fillWidth: true
                            Item { Layout.fillWidth: true }
                            MainAction { objectName: "creationPreviousSlide"; text: "‹"; implicitHeight: 34; enabled: !bridge.inputDocuments.preview.busy && (bridge.inputDocuments.preview.slide || 1) > 1; onClicked: bridge.inputDocuments.showSlide(bridge.inputDocuments.preview.slide - 1) }
                            Copy { objectName: "creationSlideCounter"; text: "Slide " + (bridge.inputDocuments.preview.slide || 1) + " / " + (bridge.inputDocuments.preview.total || 0); color: root.ink }
                            MainAction { objectName: "creationNextSlide"; text: "›"; implicitHeight: 34; enabled: !bridge.inputDocuments.preview.busy && (bridge.inputDocuments.preview.slide || 1) < bridge.inputDocuments.preview.total; onClicked: bridge.inputDocuments.showSlide((bridge.inputDocuments.preview.slide || 1) + 1) }
                            Item { Layout.fillWidth: true }
                        }
                        Surface {
                            objectName: "creationConfiguration"; Layout.fillWidth: true; implicitHeight: config.height + (root.compactCreation ? 24 : 38)
                            ColumnLayout {
                                id: config; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: root.compactCreation ? 12 : 19; spacing: root.compactCreation ? 6 : 12; enabled: !bridge.busy
                                Caption { visible: !root.tightCreation; text: "Cấu hình bài giảng"; font.pixelSize: 15 }
                                GridLayout {
                                    Layout.fillWidth: true; columns: 12; columnSpacing: 12; rowSpacing: root.compactCreation ? 4 : 7
                                    Caption { text: "Tên bài học"; Layout.columnSpan: 4 } Caption { text: "Môn học"; Layout.columnSpan: 4 }
                                    Caption { text: "Cấp học"; Layout.columnSpan: 2 } Caption { text: "Khối lớp"; Layout.columnSpan: 2 }
                                    Field {
                                        id: titleInput; objectName: "lessonTitle"; implicitHeight: root.compactCreation ? 36 : 43
                                        Layout.fillWidth: true; Layout.columnSpan: 4; Layout.preferredWidth: 320; Layout.minimumWidth: 120; Layout.alignment: Qt.AlignTop
                                        placeholderText: "Tên bài giảng"; maximumLength: 180
                                        onTextChanged: if (!activeFocus) cursorPosition = 0
                                        onActiveFocusChanged: if (!activeFocus) cursorPosition = 0
                                        ToolTip.visible: titleInputHover.hovered && titleInput.contentWidth > titleInput.width - titleInput.leftPadding - titleInput.rightPadding
                                        ToolTip.text: text; ToolTip.delay: 500
                                        HoverHandler { id: titleInputHover }
                                    }
                                    ColumnLayout {
                                        Layout.fillWidth: true; Layout.columnSpan: 4; Layout.preferredWidth: 320; Layout.minimumWidth: 120; Layout.alignment: Qt.AlignTop; spacing: 7
                                        Choice {
                                            id: subjectInput; objectName: "lessonSubject"; implicitHeight: root.compactCreation ? 36 : 43; Layout.fillWidth: true
                                            model: bridge.conversionSubjects; currentIndex: -1; leftPadding: 12; rightPadding: 36
                                            onActivated: { root.creationSubjectOverridden = true; if (currentText !== "Khác") bridge.rememberConversionSubject(currentText) }
                                            displayText: currentIndex < 0 ? "Chọn môn học" : currentText
                                            Accessible.name: "Môn học"
                                            contentItem: Text {
                                                text: subjectInput.displayText; font: subjectInput.font
                                                color: subjectInput.currentIndex < 0 ? root.muted : root.ink
                                                verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight
                                            }
                                            delegate: ItemDelegate {
                                                required property string modelData
                                                required property int index
                                                width: subjectList.width - 16; height: 38
                                                text: modelData; font: subjectInput.font
                                                highlighted: subjectInput.highlightedIndex === index
                                                contentItem: Text { text: parent.text; font: parent.font; color: root.ink; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                                                background: Rectangle { radius: 5; color: parent.highlighted || parent.hovered ? AppTheme.adapt("#e8f1ff") : "transparent" }
                                            }
                                            popup: Popup {
                                                id: subjectPopup; objectName: "creationSubjectPopup"
                                                y: subjectInput.height + 4; width: Math.min(root.width - 32, Math.max(subjectInput.width, 400)); padding: 6
                                                implicitHeight: Math.min(contentItem.implicitHeight + 12, 400, root.height - 60)
                                                contentItem: ListView {
                                                    id: subjectList; objectName: "creationSubjectList"; clip: true
                                                    implicitHeight: contentHeight; model: subjectPopup.visible ? subjectInput.delegateModel : null
                                                    currentIndex: subjectInput.highlightedIndex; highlightMoveDuration: 0
                                                    ScrollBar.vertical: SlimScrollBar { }
                                                }
                                                background: Rectangle { color: AppTheme.surface; radius: 8; border.color: root.line }
                                            }
                                        }
                                        Field { id: customSubjectInput; objectName: "creationCustomSubject"; implicitHeight: root.compactCreation ? 36 : 43; visible: subjectInput.currentText === "Khác"; Layout.fillWidth: true; placeholderText: "Nhập tên môn học khác"; maximumLength: 100; Accessible.name: "Tên môn học khác"; onTextEdited: root.creationSubjectOverridden = true; onEditingFinished: bridge.rememberConversionSubject(text) }
                                    }
                                    Choice {
                                        id: educationInput; objectName: "creationEducation"; implicitHeight: root.compactCreation ? 36 : 43
                                        model: ["THPT", "THCS", "Tiểu học"]; currentIndex: model.indexOf(bridge.conversionClassSelection.education)
                                        onActivated: { gradeInput.currentIndex = 0; bridge.rememberConversionClass(currentText, bridge.educationGrades(currentText)[0]) }
                                        Layout.columnSpan: 2; Layout.preferredWidth: 160; Layout.minimumWidth: 115; Layout.fillWidth: true; Layout.alignment: Qt.AlignTop
                                    }
                                    Choice {
                                        id: gradeInput; objectName: "creationGrade"; implicitHeight: root.compactCreation ? 36 : 43
                                        model: bridge.educationGrades(educationInput.currentText)
                                        currentIndex: { const saved = bridge.conversionClassSelection; const index = model.indexOf(saved.grade); return saved.education === educationInput.currentText && index >= 0 ? index : 0 }
                                        onModelChanged: { const saved = bridge.conversionClassSelection; const index = model.indexOf(saved.grade); currentIndex = saved.education === educationInput.currentText && index >= 0 ? index : 0 }
                                        onActivated: bridge.rememberConversionClass(educationInput.currentText, currentText)
                                        Layout.columnSpan: 2; Layout.preferredWidth: 130; Layout.minimumWidth: 80; Layout.fillWidth: true; Layout.alignment: Qt.AlignTop
                                    }
                                }
                                Caption { objectName: "conversionFormatTitle"; text: "Kiểu chuyển đổi" }
                                GridLayout {
                                    id: creationFormat; objectName: "creationFormat"
                                    property int currentIndex: 0
                                    readonly property int count: root.conversionFormats.length
                                    ButtonGroup { id: conversionChoices }
                                    columns: width >= 960 ? 4 : 2; columnSpacing: 10; rowSpacing: 10; Layout.fillWidth: true
                                    Repeater {
                                        model: root.conversionFormats
                                        ConversionChoice {
                                            required property var modelData
                                            required property int index
                                            choiceName: "formatChoice_" + modelData.id
                                            choiceGroup: conversionChoices
                                            label: modelData.label; detail: modelData.detail
                                            selected: creationFormat.currentIndex === index; showPreview: true; compact: root.compactCreation; tight: root.tightCreation
                                            Layout.fillWidth: true; Layout.preferredWidth: 1
                                            onChosen: creationFormat.currentIndex = index
                                            onPreviewRequested: root.showConversionExample(index)
                                        }
                                    }
                                }
                                Copy { objectName: "creationFormatDescription"; visible: false; text: root.selectedConversionFormat.detail }
                                Caption { text: "Thiết kế bài giảng" }
                                GridLayout {
                                    id: creationWorkflow; objectName: "creationWorkflow"
                                    property int currentIndex: 0
                                    ButtonGroup { id: designChoices }
                                    columns: 2; columnSpacing: 10; Layout.fillWidth: true
                                    ConversionChoice {
                                        choiceName: "creationKeepOriginal"
                                        compact: root.compactCreation; tight: root.tightCreation
                                        choiceGroup: designChoices
                                        label: "Giữ thiết kế PowerPoint gốc"
                                        detail: bridge.googleTranslation ? "Giữ nền, hình và công thức. Song ngữ tự căn từng vùng; tiếng Anh 100% thay chữ tại vị trí gốc. Vùng quá chật có trang tiếp nối song ngữ. Chữ trong ảnh và hiệu ứng cần đối chiếu." : root.creationPowerPoint ? "Dùng đúng PowerPoint đầu vào: giữ thiết kế, hình, thứ tự slide và hiệu ứng; chuyển ngôn ngữ theo kiểu đã chọn." : root.creationCanKeepSource ? "Chọn tệp PPTX để giữ thiết kế, hình, thứ tự slide và hiệu ứng của PowerPoint đầu vào." : "Word/PDF/ảnh hoặc nội dung dán không có thiết kế PowerPoint gốc; dùng mẫu mới."
                                        selected: creationWorkflow.currentIndex === 0
                                        enabled: root.creationCanKeepSource; Layout.fillWidth: true; Layout.preferredWidth: 1
                                        onChosen: { root.preferredCreationDesign = 0; creationWorkflow.currentIndex = 0 }
                                    }
                                    ConversionChoice {
                                        choiceName: "creationUseTemplate"
                                        compact: root.compactCreation; tight: root.tightCreation
                                        choiceGroup: designChoices
                                        label: "Tạo theo mẫu mới"
                                        detail: "Dùng bộ mẫu BiliClass, tự chọn bố cục và chia trang khi dài. Giữ hình cùng nội dung; hiệu ứng gốc không được tái dựng."
                                        selected: creationWorkflow.currentIndex === 1
                                        Layout.fillWidth: true; Layout.preferredWidth: 1
                                        onChosen: { root.preferredCreationDesign = 1; creationWorkflow.currentIndex = 1 }
                                    }
                                }
                                Caption { visible: !root.creationKeepSource; text: "Chọn mẫu BiliClass" }
                                TemplatePresetPicker {
                                    id: creationPreset; objectName: "creationPreset"; visible: !root.creationKeepSource; Layout.fillWidth: true
                                    onPreviewRequested: function(preset) { creationTemplatePreview.preset = preset; creationTemplatePreview.open() }
                                }
                                RowLayout {
                                    visible: !bridge.googleTranslation
                                    Layout.fillWidth: true
                                    Caption { text: "Ghi chú thêm · không bắt buộc"; Layout.fillWidth: true }
                                    Copy { text: teacherNotesInput.text.trim().length + " / 6.000"; color: teacherNotesInput.text.trim().length > 6000 ? AppTheme.adapt("#ab5b20") : root.muted; font.pixelSize: 11 }
                                }
                                ContentScrollView {
                                    visible: !bridge.googleTranslation
                                    Layout.fillWidth: true; Layout.preferredHeight: 90;
                                    TextArea {
                                        id: teacherNotesInput; objectName: "creationTeacherNotes"
                                        enabled: !bridge.busy; wrapMode: TextEdit.Wrap; selectByMouse: true
                                        placeholderText: "Ví dụ: giữ các bước giải; dùng thuật ngữ dễ hiểu cho học sinh lớp 7; chú ý phần chữ trong hình…"
                                        color: root.ink; font.pixelSize: 13
                                        background: Rectangle { radius: 8; color: AppTheme.adapt("#fafcff"); border.color: root.line }
                                    }
                                }
                            }
                        }
                        Surface {
                            visible: !bridge.googleTranslation
                            Layout.fillWidth: true; implicitHeight: promptHeader.height + 28 + (root.creationPromptVisible ? 278 : 0)
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 14; spacing: 8
                                RowLayout {
                                    id: promptHeader; Layout.fillWidth: true
                                    Caption { text: "03   Nội dung yêu cầu" }
                                    Item { Layout.fillWidth: true }
                                    MainAction { objectName: "creationPromptToggle"; text: root.creationPromptVisible ? "Ẩn prompt" : "Hiện prompt"; iconName: "view"; subtle: true; implicitHeight: 30; onClicked: root.creationPromptVisible = !root.creationPromptVisible }
                                }
                                ContentScrollView {
                                    visible: root.creationPromptVisible; Layout.fillWidth: true; Layout.preferredHeight: 270;
                                    TextArea { objectName: "creationPromptText"; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; text: root.creationPrompt.prompt || ""; color: root.ink; font.pixelSize: 12; background: Rectangle { radius: 8; color: AppTheme.adapt("#fafcff"); border.color: root.line } }
                                }
                            }
                        }

                    }
                }
                Rectangle {
                    id: creationFooter; objectName: "creationFooter"
                    visible: root.page === "new" || (root.page === "voice" && !root.voiceResultShown); anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
                    height: visible ? creationFooterContent.implicitHeight + 24 : 0; color: AppTheme.adapt("#f3f7fc")
                    Rectangle { anchors.top: parent.top; height: 1; width: parent.width; color: root.line }
                    ColumnLayout {
                        id: creationFooterContent
                        anchors.fill: parent; anchors.leftMargin: 28; anchors.rightMargin: 28; anchors.topMargin: 12; anchors.bottomMargin: 12; spacing: 3
                        RowLayout {
                            objectName: "creationFooterPrimaryRow"; Layout.fillWidth: true; spacing: 16
                            ConversionConfiguration {
                                objectName: "conversionConfigurationSummary"; visible: root.page === "new"; Layout.fillWidth: true; Layout.minimumWidth: 0
                                formatLabel: root.selectedConversionFormat.label
                                formatId: root.selectedConversionFormat.id
                                keepSource: root.creationKeepSource
                                templateName: creationPreset.currentText
                                subject: root.creationSubject; education: educationInput.currentText; grade: gradeInput.currentText
                            }
                            NarrationConfiguration {
                                objectName: "narrationConfiguration"; visible: root.page === "voice"; Layout.fillWidth: true; Layout.minimumWidth: 0
                                mode: root.narrationMode
                                voiceName: (bridge.multilingualVoices.find(function(v) { return v.id === root.narrationVoice }) || {}).name || ""
                                pairLabel: bridge.voicePairDetails(root.narrationVoice).label || ""
                                rate: root.narrationRate; readable: root.narrationReadableSlides; total: root.narrationEligibleSlides
                                vietnameseSlides: root.narrationCoverage.vi || 0; englishSlides: root.narrationCoverage.en || 0
                                hasLesson: !!bridge.quickResult.path
                                positionLabel: speakerPositionChoice.currentText
                            }
                            MainAction { objectName: "createLessonButton"; visible: root.page === "new"; text: bridge.busy ? "Đang chuẩn bị…" : "Chuyển đổi bài giảng"; primary: true; enabled: !bridge.busy && !bridge.inputDocuments.busy && !bridge.narrationBusy && !root.inputDocumentError && root.creationPrompt.ready; onClicked: bridge.convertDocument(titleInput.text, root.creationSubject, educationInput.currentText, gradeInput.currentText, pasteInput.text, root.selectedFile, root.selectedConversionFormat.id, ["standard", "visual", "practice"][creationPreset.currentIndex], root.creationKeepSource ? "source" : "template", teacherNotesInput.text) }
                            MainAction { objectName: "createLessonNarrationButton"; visible: root.page === "voice" && !root.narrationComplete; primary: true; text: bridge.narrationBusy ? "Đang tạo giọng…" : "Tạo giọng đọc"; enabled: !!bridge.quickResult.path && !!root.narrationDraft.total && !!root.narrationVoice && !root.narrationDraft.ready && bridge.narrationWorkspace.configurationEnabled; onClicked: bridge.createLessonNarrationWithVoice(root.narrationMode, root.narrationVoice, root.narrationRate) }
                            MainAction { objectName: "cancelLessonNarrationButton"; danger: true; symbol: "■"; text: bridge.lessonNarration.stopping ? "Đang dừng…" : "Dừng"; enabled: !bridge.lessonNarration.stopping; visible: (root.page === "voice" || root.page === "result") && !!bridge.lessonNarration.running; onClicked: bridge.cancelLessonNarration() }
                        }
                        Copy { visible: root.page === "new" && bridge.narrationBusy; text: "Đang tạo giọng đọc · Chờ hoàn tất hoặc dừng trước khi chuyển đổi bài mới."; Layout.fillWidth: true; font.pixelSize: 12 }
                        MainAction { objectName: "resumeCreationTask"; text: bridge.browserState.phase === "completed" ? "Mở bài vừa chuyển đổi" : "Tiếp tục bài đang chuẩn bị"; visible: root.page === "new" && !!bridge.chatgptRequest.folder && !bridge.narrationBusy; attention: bridge.browserState.phase === "completed"; subtle: !attention; implicitHeight: attention ? 36 : 28; font.pixelSize: 11; onClicked: root.go("chatgpt") }
                        MainAction { objectName: "resumeNarrationTask"; text: "Mở bài vừa tạo giọng"; attention: true; implicitHeight: 36; font.pixelSize: 11; visible: root.page === "voice" && !!bridge.recentNarrationResult.lesson_id && !bridge.narrationBusy; enabled: !bridge.busy; onClicked: bridge.openRecentNarrationResult() }
                    }
                }

                ContentScrollView {
                    id: conversionProgressScroll; objectName: "conversionProgressScroll"; outerGutter: true; anchors.fill: parent; anchors.margins: 30; visible: root.page === "chatgpt"; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout { Heading { text: "Tạo bài giảng song ngữ"; font.pixelSize: 28 } Item { Layout.fillWidth: true } MainAction { text: "Đổi cấu hình"; subtle: true; enabled: !bridge.browserState.running; onClicked: root.go("new") } }
                        Copy { Layout.fillWidth: true; text: (bridge.chatgptRequest.config || {}).title || "Chuẩn bị tài liệu trước khi gửi"; color: root.ink; font.pixelSize: 17 }
                        Surface {
                            visible: bridge.browserState.phase !== "completed" && (bridge.googleTranslation || bridge.browserAI.automatic && bridge.browserState.phase !== "manual")
                            Layout.fillWidth: true; implicitHeight: autoBrowserSteps.height + 42
                            ColumnLayout {
                                id: autoBrowserSteps; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 21; spacing: 14
                                RowLayout { Layout.fillWidth: true
                                    BusyIndicator { running: !!bridge.browserState.running; visible: running; implicitWidth: 34; implicitHeight: 34 }
                                    Caption { text: bridge.browserState.running ? "Đang tạo bài giảng" : bridge.browserState.phase === "error" ? "Chuyển đổi tạm dừng" : "Bài giảng song ngữ"; font.pixelSize: 18; Layout.fillWidth: true }
                                }
                                Copy { objectName: "browserConversionStatus"; text: bridge.browserState.displayMessage; Layout.fillWidth: true; font.pixelSize: 15; color: root.ink }
                                RowLayout {
                                    Layout.fillWidth: true
                                    Copy { objectName: "browserConversionStage"; text: bridge.browserState.displayStage; Layout.fillWidth: true; color: root.ink }
                                    Caption { objectName: "browserConversionPercent"; text: (bridge.browserState.percent || 0) + "%"; font.pixelSize: 22 }
                                }
                                ProgressBar {
                                    id: conversionBar; objectName: "browserConversionProgressBar"; Layout.fillWidth: true
                                    from: 0; to: 100; value: bridge.browserState.percent || 0
                                    indeterminate: false
                                    background: Rectangle { implicitHeight: 9; radius: 4.5; color: AppTheme.adapt("#e8eff9") }
                                    contentItem: Item {
                                        implicitHeight: 9; clip: true
                                        Rectangle {
                                            id: conversionCompletedFill; objectName: "browserConversionCompletedFill"
                                            width: parent.width * conversionBar.visualPosition; height: parent.height; radius: 4.5; color: root.blue; clip: true
                                            Rectangle {
                                                id: conversionPulse; objectName: "browserConversionPulse"
                                                visible: !!bridge.browserState.running && !!bridge.browserState.waiting
                                                width: parent.width * 0.32; height: parent.height; radius: 4.5; color: AppTheme.adapt("#ffffff"); opacity: 0.32
                                                NumberAnimation on x { from: -conversionPulse.width; to: conversionPulse.parent.width; duration: 1500; loops: Animation.Infinite; running: conversionPulse.visible && conversionBar.visible && root.visible }
                                            }
                                        }
                                    }
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    Copy { objectName: "browserConversionElapsed"; text: "Thời gian xử lý: " + bridge.conversionClock.label; color: root.ink }
                                    Item { Layout.fillWidth: true }
                                    Copy { objectName: "browserConversionClockState"; text: bridge.conversionClock.status; color: bridge.browserState.running ? root.blue : root.muted }
                                }
                                Copy { objectName: "browserConversionLongWait"; Layout.fillWidth: true; visible: !!bridge.conversionClock.longWait && !bridge.browserState.stopping; text: "Bài đang mất nhiều thời gian hơn thường lệ. BiliClass vẫn theo dõi kết quả và sẽ báo ngay nếu cần bạn xử lý."; color: AppTheme.adapt("#a66318"); font.pixelSize: 12 }
                                RowLayout { Layout.fillWidth: true
                                    MainAction { objectName: "browserConversionResume"; text: !bridge.googleTranslation && bridge.browserAI.webMode && bridge.browserState.needsLogin ? "Kết nối và tiếp tục" : bridge.browserState.errorCode === "submission" ? "Kiểm tra và tiếp tục" : "Tiếp tục chuyển đổi"; primary: true; visible: !bridge.browserState.running && bridge.browserState.phase !== "completed" && !!bridge.chatgptRequest.folder; enabled: !bridge.busy && (bridge.googleTranslation || !bridge.browserAI.loginBusy); onClicked: { if (!bridge.googleTranslation && bridge.browserAI.webMode && (bridge.browserState.needsLogin || bridge.browserState.errorCode === "submission")) bridge.reconnectBrowserAI(); else bridge.runBrowserAI() } }
                                    MainAction { objectName: "browserConversionSettings"; text: bridge.googleTranslation ? "Kiểm tra Google Dịch" : "Đăng nhập / Browser AI"; visible: !bridge.browserState.running && bridge.browserState.phase === "error" && (bridge.googleTranslation ? ["api_settings", "api_key", "api_budget", "api_quota", "api_request"].indexOf(bridge.browserState.errorCode) >= 0 : !!bridge.browserState.needsLogin); enabled: !bridge.busy; onClicked: { root.go("settings"); settingsPanel.activeTab = 6 } }
                                    Item { Layout.fillWidth: true }
                                    MainAction { id: conversionCancel; objectName: "browserConversionCancel"; danger: true; symbol: "×"; text: bridge.browserState.stopping ? "Đang hủy…" : "Hủy chuyển đổi"; visible: !!bridge.browserState.running; enabled: !bridge.browserState.stopping; onClicked: { if (bridge.googleTranslation) { cancelConversionDialog.conversionId = bridge.browserState.conversionId || ""; cancelConversionDialog.open() } else bridge.cancelJob() } }
                                }
                            }
                        }
                        Surface {
                            objectName: "conversionCompletion"
                            visible: bridge.browserState.phase === "completed" && !bridge.browserState.running
                            Layout.fillWidth: true; implicitHeight: completedConversionBody.implicitHeight + 44
                            ColumnLayout {
                                id: completedConversionBody
                                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 22; spacing: 20
                                RowLayout {
                                    Layout.fillWidth: true; spacing: 14
                                    Rectangle {
                                        Layout.preferredWidth: 46; Layout.preferredHeight: 46; radius: 23; color: AppTheme.adapt("#e8f6f0")
                                        Label { anchors.centerIn: parent; text: "✓"; color: AppTheme.adapt("#168567"); font.pixelSize: 26; font.bold: true }
                                    }
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 5
                                        Heading { text: "Đã tạo bài giảng"; font.pixelSize: 22; Layout.fillWidth: true }
                                        Copy { objectName: "conversionCompletionSummary"; text: root.lessonData.id === bridge.browserState.lessonId ? (bridge.quickResult.total || 0) + " slide · Đã lưu trong Bài giảng" : "Đã lưu trong Bài giảng"; Layout.fillWidth: true }
                                    }
                                }
                                GridLayout {
                                    objectName: "conversionCompletionActions"
                                    Layout.fillWidth: true; Layout.maximumWidth: 900; Layout.alignment: Qt.AlignHCenter
                                    columns: width >= 700 ? 4 : 2; columnSpacing: 12; rowSpacing: 10
                                    MainAction { objectName: "openConvertedVoiceButton"; text: "Tạo giọng đọc"; primary: true; Layout.fillWidth: true; Layout.preferredWidth: 1; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: bridge.openConvertedLesson() }
                                    MainAction { objectName: "downloadCompletedConversion"; text: "Tải bài giảng"; iconName: "download"; Layout.fillWidth: true; Layout.preferredWidth: 1; enabled: root.lessonData.id === bridge.browserState.lessonId && !!bridge.quickResult.path && !bridge.busy && !bridge.narrationBusy; onClicked: presentationNoVoiceSave.openSuggested() }
                                    MainAction { objectName: "teachCompletedConversion"; text: "Mở PowerPoint"; Layout.fillWidth: true; Layout.preferredWidth: 1; enabled: root.lessonData.id === bridge.browserState.lessonId && !!bridge.quickResult.path && !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; ToolTip.visible: hovered; ToolTip.text: "Mở bài và gắn với Mascot để dạy."; onClicked: bridge.openTeachingLibraryLesson(bridge.browserState.lessonId) }
                                    MainAction { objectName: "libraryAfterConversion"; text: "Về Bài giảng"; Layout.fillWidth: true; Layout.preferredWidth: 1; enabled: !bridge.busy && !bridge.narrationBusy && root.lessonData.id === bridge.browserState.lessonId; onClicked: root.showNarratedLessonInLibrary() }
                                }
                                ConversionCompletionPreview {
                                    objectName: "conversionCompletionPreview"
                                    Layout.fillWidth: true; Layout.maximumWidth: 1080; Layout.alignment: Qt.AlignHCenter
                                    bridge: root.bridgeRef
                                    lessonId: bridge.browserState.lessonId || ""
                                    previewHeight: Math.max(220, Math.min(460, root.height - 490))
                                }
                            }
                        }
                        Surface {
                            visible: bridge.browserState.phase !== "completed" && !bridge.googleTranslation && (!bridge.browserAI.automatic || bridge.browserState.phase === "manual")
                            Layout.fillWidth: true; implicitHeight: chatgptSteps.height + 42
                            ColumnLayout {
                                id: chatgptSteps; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 21; spacing: 18
                                Caption { text: "1. Gửi prompt và tài liệu trong browser"; font.pixelSize: 17 }
                                Copy { Layout.fillWidth: true; text: "Mở ChatGPT bằng tài khoản của thầy cô. Dán prompt, đính kèm " + (bridge.chatgptRequest.attachments || []).join(" và ") + ", rồi bấm Gửi. Gói ZIP dùng để lưu/chia sẻ; giải nén trước nếu gửi từ ZIP." }
                                RowLayout { Layout.fillWidth: true; MainAction { objectName: "copyChatGPTPromptButton"; text: "Sao chép prompt"; primary: true; enabled: !!bridge.chatgptRequest.folder; onClicked: bridge.copyChatGPTPrompt() } MainAction { objectName: "openChatGPTFolderButton"; text: "Mở thư mục tài liệu"; onClicked: bridge.openChatGPTFolder() } MainAction { objectName: "openChatGPTButton"; text: "Mở ChatGPT"; onClicked: bridge.openChatGPT() } }
                                Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: root.line }
                                Caption { text: "2. Tải PowerPoint kết quả về máy"; font.pixelSize: 17 }
                                Copy { Layout.fillWidth: true; text: "Tải file .pptx do ChatGPT tạo. Nếu ChatGPT chỉ trả văn bản, yêu cầu xuất PowerPoint có thể tải xuống. Khả năng tạo tệp và lượt dùng phụ thuộc tài khoản của thầy cô." }
                                Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: root.line }
                                Caption { text: "3. Nhận bài, xem trình chiếu, dùng để dạy"; font.pixelSize: 17 }
                                Copy { Layout.fillWidth: true; text: "BiliClass giữ nguyên file nhận về. Trợ giảng đọc cặp Việt–Anh nhận diện được từ chữ hoặc ghi chú slide; không tự dịch lại." }
                                MainAction { objectName: "receiveChatGPTDeckButton"; text: "Nhận PowerPoint từ ChatGPT"; iconName: "download"; primary: true; enabled: !bridge.busy && !!bridge.chatgptRequest.folder; onClicked: chatgptDeckOpen.open() }
                            }
                        }
                        MainAction { visible: !bridge.googleTranslation; text: chatgptPromptPreview.visible ? "Ẩn prompt" : "Xem prompt đã cấu hình"; subtle: true; onClicked: chatgptPromptPreview.visible = !chatgptPromptPreview.visible }
                        ContentScrollView { id: chatgptPromptPreview; visible: false; Layout.fillWidth: true; Layout.preferredHeight: 240;
                            TextArea { readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 13; text: bridge.chatgptRequest.prompt || ""; color: root.ink }
                        }
                    }
                }

                ContentScrollView {
                    id: resultScroll; objectName: "resultScroll"; outerGutter: true
                    anchors.fill: parent; anchors.margins: root.compactVoice ? 18 : 28; anchors.bottomMargin: creationFooter.height + 12; visible: root.page === "result" || (root.page === "voice" && !root.voiceResultShown); contentWidth: availableWidth
                    ColumnLayout {
                        width: resultScroll.availableWidth; spacing: root.compactVoice ? 12 : 18
                        ColumnLayout { visible: root.page === "voice"; Layout.fillWidth: true; spacing: 12
                            RowLayout { Layout.fillWidth: true
                                Heading { objectName: "voicePageHeading"; text: "Tạo giọng đọc bài giảng"; font.pixelSize: 27; Layout.fillWidth: true }
                                MainAction { objectName: "changeVoiceSource"; visible: !!bridge.quickResult.path; text: root.voiceSourceExpanded ? "Thu gọn" : "Chọn bài khác"; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.teachingTransitioning; onClicked: root.voiceSourceExpanded = !root.voiceSourceExpanded }
                                MainAction { objectName: "dismissVoiceLesson"; visible: !!bridge.quickResult.path; danger: true; symbol: "×"; text: bridge.lessonNarration.stopping ? "Đang hủy…" : "Hủy bài đang chọn"; Accessible.description: "Bỏ bài đang chọn khỏi màn tạo giọng; bài đã lưu vẫn còn trong thư viện."; enabled: !bridge.busy && !bridge.lessonNarration.stopping && !bridge.powerpointState.active && !bridge.teachingTransitioning; onClicked: bridge.dismissNarrationLesson() }
                            }
                            Copy { objectName: "voiceWorkflowGuide"; text: "Chọn PowerPoint có sẵn hoặc bài trong thư viện → Chọn cấu hình giọng đọc và ngôn ngữ → Tạo giọng đọc"; Layout.fillWidth: true; font.pixelSize: 12 }
                            PowerPointUpload { objectName: "voiceSourceArea"; visible: !bridge.quickResult.path || root.voiceSourceExpanded; illustrated: true; compact: true; Layout.fillWidth: true; chooseObjectName: "chooseVoicePresentation"; dropObjectName: "voicePresentationDrop"; busy: bridge.busy || bridge.narrationBusy; loadingFileName: bridge.narrationImportName
                                illustrationSource: "../assets/powerpoint-narration.png"; illustrationClipRect: Qt.rect(40, 200, 1408, 750)
                                onChooseFile: voicePresentationOpen.open()
                                onFilesDropped: function(urls) { if (urls.length === 1) bridge.importNarrationPresentation(urls[0]) }
                            }
                            RowLayout { visible: !bridge.quickResult.path || root.voiceSourceExpanded; Layout.fillWidth: true
                                Choice { id: voiceLibraryPicker; objectName: "voiceLibraryPicker"; model: bridge.lessons; textRole: "title"; Layout.fillWidth: true; Layout.minimumWidth: 0; enabled: bridge.narrationWorkspace.configurationEnabled }
                                MainAction { objectName: "selectVoiceLibraryLesson"; text: "Dùng bài trong thư viện"; enabled: bridge.narrationWorkspace.configurationEnabled && voiceLibraryPicker.currentIndex >= 0; onClicked: bridge.narrationWorkspace.selectLibrary(bridge.lessons[voiceLibraryPicker.currentIndex].id) }
                            }
                            Copy { objectName: "voiceWorkspaceError"; visible: bridge.error && !bridge.busy; text: bridge.message; color: AppTheme.adapt("#a66318"); Layout.fillWidth: true }
                            RowLayout { visible: bridge.busy; Layout.fillWidth: true; spacing: 12
                                ProgressBar { indeterminate: true; Layout.preferredWidth: 120 }
                                Copy { objectName: "voiceImportProgressMessage"; text: bridge.narrationImportName ? "Đang chuẩn bị lời đọc…" : bridge.message; Layout.fillWidth: true }
                            }
                        }
                        ColumnLayout { Layout.fillWidth: true; spacing: root.compactVoice ? 12 : 18
                        MainAction { id: backToLibraryAction; objectName: "backToLibraryButton"; visible: root.page !== "voice"; text: "Trở lại thư viện"; iconName: "back"; subtle: true; implicitHeight: 32; Layout.alignment: Qt.AlignRight; enabled: !bridge.busy; onClicked: root.requestAction(function() { bridge.returnToLibrary() }) }
                        GridLayout {
                            id: voiceOverview; objectName: "voiceLessonOverview"
                            visible: root.page !== "voice" || !!bridge.quickResult.path
                            Layout.fillWidth: true; columnSpacing: 24; rowSpacing: 12
                            columns: root.page === "voice" && !!bridge.quickResult.path && !root.voicePreviewExpanded && width >= 760 ? 2 : 1
                            ColumnLayout {
                                objectName: "voiceLessonDetails"
                                Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.alignment: Qt.AlignTop; spacing: 12
                        RowLayout {
                            id: resultHeadingRow
                            visible: root.page !== "voice" || !!bridge.quickResult.path; Layout.fillWidth: true
                            ColumnLayout {
                                Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 6
                                Heading { objectName: "resultLessonTitle"; font.pixelSize: root.page === "voice" ? 20 : 27; Layout.fillWidth: true; Layout.minimumWidth: 0; text: root.lessonData.title || "Bài giảng song ngữ" }
                                Copy { Layout.fillWidth: true; Layout.minimumWidth: 0; text: [root.lessonData.subject, ((root.lessonData.education_level || "") + " " + (root.lessonData.grade || "")).trim(), root.lessonData.voice_only ? "PowerPoint nguyên bản · Tạo giọng độc lập" : bridge.conversionLabel].filter(function(value) { return !!value }).join(" · ") }
                            }
                            LibraryAction {
                                id: resultMoreAction; objectName: "resultMoreButton"
                                parent: root.page === "voice" ? voicePreviewActions : resultHeadingRow
                                text: "⋯"; font.pixelSize: 24; subtle: true
                                implicitWidth: 32; implicitHeight: 32
                                Layout.minimumWidth: 32; Layout.preferredWidth: 32; Layout.maximumWidth: 32
                                enabled: !bridge.busy
                                Accessible.name: "Thao tác khác"
                                ToolTip.visible: hovered; ToolTip.text: "Thao tác khác"; ToolTip.delay: 500
                                onClicked: resultMoreMenu.popup()
                            }
                            Menu { id: resultMoreMenu; objectName: "resultMoreMenu"; parent: resultMoreAction; x: parent.width - width; y: parent.height
                                MenuItem { objectName: "reviewNarrationScript"; text: "Kiểm tra / sửa lời đọc…"; enabled: !!bridge.quickResult.path && !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.teachingTransitioning; onTriggered: narrationScript.open() }
                                MenuItem { text: "Sửa thông tin bài"; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active; onTriggered: { metadataDialog.lessonData = root.lessonData; metadataDialog.open() } }
                                MenuItem { objectName: "editLessonDetailsButton"; text: "Sửa nội dung bài giảng…"; visible: !root.lessonData.voice_only; height: visible ? implicitHeight : 0; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active; onTriggered: bridge.editLesson(root.lessonData.id) }
                                MenuItem { objectName: "voiceDownloadWithoutNarrationMenu"; text: "Tải PowerPoint không giọng…"; visible: root.page === "voice" && !!root.narrationDraft.ready; height: visible ? implicitHeight : 0; enabled: !!bridge.quickResult.path && !bridge.busy && !bridge.narrationBusy; onTriggered: presentationNoVoiceSave.openSuggested() }
                            }
                        }
                        LessonStateStrip { objectName: "lessonWorkflowState"; visible: root.page === "voice" && !!root.lessonData.id; state: bridge.workflowState; showPreparation: bridge.experimentalTeaching; showContentReview: bridge.experimentalTeaching; Layout.fillWidth: true }
                        LessonInformation {
                            objectName: "lessonInformation"; visible: root.page === "result"; Layout.fillWidth: true
                            lesson: root.lessonData; voices: bridge.narrationVariants
                            conversion: bridge.conversionLabel; slides: bridge.quickResult.total || (root.lessonData.segments || []).length
                        }
                        Copy { visible: root.page === "voice" && bridge.narrationWorkspace.summary.silent > 0; text: bridge.narrationWorkspace.summary.silent + " slide được chọn không đọc"; Layout.fillWidth: true; font.pixelSize: 12 }
                        RowLayout { visible: root.page === "voice" && !!bridge.quickResult.path; Layout.fillWidth: true
                            Copy { objectName: "voiceSourceSummary"; Layout.fillWidth: true; Layout.minimumWidth: 0; color: root.ink; text: bridge.narrationWorkspace.summary.total + " slide · có lời Việt: " + bridge.narrationWorkspace.summary.vi + " · có lời Anh: " + bridge.narrationWorkspace.summary.en + (bridge.narrationWorkspace.summary.empty ? " · " + bridge.narrationWorkspace.summary.empty + " slide chưa có lời đọc" : "") }
                        }
                        Flow { visible: root.page === "voice" && !!bridge.quickResult.path && !root.narrationDraft.ready; Layout.fillWidth: true; spacing: 10
                            MainAction { objectName: "voiceDownloadWithoutNarration"; text: "Tải PowerPoint không giọng"; iconName: "download"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: presentationNoVoiceSave.openSuggested() }
                            MainAction { objectName: "voiceTeachWithoutNarration"; text: "Mở PowerPoint"; enabled: !bridge.busy && !bridge.previewBusy && !bridge.narrationBusy; onClicked: root.prepareTeaching() }
                        }
                            }
                            ColumnLayout {
                                visible: root.page === "voice" && !!bridge.quickResult.path
                                Layout.preferredWidth: Math.min(voiceOverview.width >= 1000 ? 304 : 240, voiceOverview.width)
                                Layout.minimumWidth: Layout.preferredWidth; Layout.maximumWidth: Layout.preferredWidth
                                Layout.alignment: Qt.AlignTop | Qt.AlignRight; spacing: 8
                                RowLayout {
                                    id: voicePreviewActions; objectName: "voicePreviewActions"
                                    Layout.fillWidth: true; spacing: 6
                                    Item { Layout.fillWidth: true }
                                    MainAction { objectName: "toggleVoiceSlidePreview"; text: root.voicePreviewExpanded ? "Ẩn xem trước" : "Xem trước slide"; subtle: true; implicitHeight: 32; onClicked: { if (root.voicePreviewExpanded) { root.voicePreviewExpanded = false; bridge.stopSpeech() } else root.showNarrationPreview() } }
                                }
                                Surface {
                                    objectName: "voiceSlideThumbnail"; visible: !root.voicePreviewExpanded
                                    Layout.fillWidth: true; implicitHeight: width * 9 / 16; radius: 10; color: AppTheme.adapt("#e9eef5")
                                    Accessible.role: Accessible.Button; Accessible.name: "Phóng to xem trước slide"
                                    Accessible.onPressAction: root.showNarrationPreview()
                                    Image { id: voiceThumbnailImage; objectName: "voiceSlideThumbnailImage"; anchors.fill: parent; anchors.margins: 3; source: parent.visible ? bridge.quickResult.image || "" : ""; fillMode: Image.PreserveAspectFit; sourceSize.width: 640; asynchronous: true; cache: true }
                                    NarrationSpeakerPreview {
                                        objectName: "thumbnailSpeakerPreview"
                                        visible: voiceThumbnailImage.status === Image.Ready && !bridge.previewBusy
                                        x: voiceThumbnailImage.x + (voiceThumbnailImage.width - width) / 2
                                        y: voiceThumbnailImage.y + (voiceThumbnailImage.height - height) / 2
                                        width: voiceThumbnailImage.paintedWidth; height: voiceThumbnailImage.paintedHeight
                                        mode: root.narrationMode; position: bridge.narrationWorkspace.speakerPosition
                                    }
                                    Copy { visible: !bridge.quickResult.image; anchors.centerIn: parent; text: bridge.previewBusy ? "Đang tải slide…" : "Xem trước slide"; font.pixelSize: 12 }
                                    TapHandler { onTapped: root.showNarrationPreview() }
                                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                                }
                            }
                        }
                        RowLayout {
                            objectName: "resultStatusActions"; visible: root.page !== "voice"; Layout.fillWidth: true; spacing: 0
                            Item { Layout.fillWidth: true }
                            Flow { Layout.preferredWidth: Math.min(500, parent.width); spacing: 10
                            MainAction { objectName: "convertCurrentLessonButton"; visible: !bridge.quickResult.path; text: "Xem trình chiếu"; primary: true; enabled: !bridge.busy; onClicked: bridge.convertCurrentLesson() }
                            MainAction { objectName: "useConvertedLessonButton"; visible: !!bridge.quickResult.path; text: "Mở PowerPoint"; primary: true; enabled: !bridge.busy && !bridge.previewBusy && !bridge.narrationBusy && !bridge.teachingTransitioning; onClicked: bridge.openTeachingLibraryLesson(root.lessonData.id) }
                            MainAction { objectName: "downloadPresentationButton"; visible: !!bridge.quickResult.path; text: "Tải PowerPoint"; iconName: "download"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: finalPresentationSave.openSuggested() }
                            MainAction { objectName: "resultCreateNarrationButton"; visible: !!bridge.quickResult.path; text: "Tạo giọng đọc"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: bridge.openLessonNarration(root.lessonData.id) }
                            }
                        }
                        RowLayout { Layout.fillWidth: true; visible: root.resultDetails
                            Copy { objectName: "lessonReviewSummary"; Layout.fillWidth: true; color: AppTheme.adapt("#a66318"); text: {
                                const missing = (bridge.quickResult.missing || []).length;
                                return missing ? missing + " phần còn thiếu nội dung song ngữ." : "BiliClass tự căn chỉnh bố cục khi chuyển đổi, mở hoặc tải bài giảng."
                            } }
                            MainAction { objectName: "resultDetailsButton"; text: root.resultDetails ? "Ẩn chi tiết" : "Xem chi tiết"; subtle: true; implicitHeight: 32; onClicked: root.resultDetails = !root.resultDetails }
                        }
                        ProgressBar { visible: root.page !== "voice" && bridge.busy; indeterminate: true; Layout.fillWidth: true }
                        Surface {
                            id: lessonSlidePreview; objectName: "lessonSlidePreview"; visible: root.page !== "voice" || (!!bridge.quickResult.path && root.voicePreviewExpanded); Layout.fillWidth: true; implicitHeight: Math.max(260, Math.min(560, (root.height - 150) * .62)); color: AppTheme.adapt("#e9eef5")
                            Image { id: expandedSlideImage; objectName: "convertedSlideImage"; anchors.fill: parent; anchors.margins: 6; source: bridge.quickResult.image || ""; fillMode: Image.PreserveAspectFit; asynchronous: true; cache: true; sourceSize.width: 1600; opacity: bridge.previewBusy ? .6 : 1 }
                            NarrationSpeakerPreview {
                                objectName: "expandedSpeakerPreview"
                                visible: root.page === "voice" && expandedSlideImage.status === Image.Ready && !bridge.previewBusy
                                x: expandedSlideImage.x + (expandedSlideImage.width - width) / 2
                                y: expandedSlideImage.y + (expandedSlideImage.height - height) / 2
                                width: expandedSlideImage.paintedWidth; height: expandedSlideImage.paintedHeight
                                mode: root.narrationMode; position: bridge.narrationWorkspace.speakerPosition
                            }
                            BusyIndicator { anchors.centerIn: parent; running: bridge.previewBusy; visible: running }
                            ColumnLayout {
                                visible: !bridge.quickResult.image; anchors.centerIn: parent; width: parent.width - 70; spacing: 12
                                Caption { visible: !bridge.previewBusy; text: bridge.busy ? "BiliClass đang tạo bài giảng…" : bridge.quickResult.path ? "Xem trước slide" : "Từ tài liệu của thầy cô đến bài giảng song ngữ"; font.pixelSize: 19; Layout.alignment: Qt.AlignHCenter }
                                Copy { visible: !bridge.previewBusy; text: bridge.quickResult.preview_note || (bridge.quickResult.path ? "Ảnh slide chưa được tải." : "Giữ thiết kế gốc hoặc tạo theo mẫu BiliClass."); Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                MainAction { objectName: "retrySlidePreview"; visible: !!bridge.quickResult.path && !bridge.previewBusy && !bridge.busy; text: "Tải lại slide"; Layout.alignment: Qt.AlignHCenter; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide || 1) }
                            }
                        }
                        RowLayout {
                            objectName: "resultSlideNavigation"; Layout.fillWidth: true; visible: !!bridge.quickResult.path && (root.page !== "voice" || root.voicePreviewExpanded)
                            Item { Layout.fillWidth: true; visible: root.page !== "voice" || !root.narrationComplete }
                            MainAction { objectName: "resultPreviousSlide"; text: "‹"; implicitHeight: 34; enabled: !bridge.busy && (bridge.quickResult.slide || 1) > 1; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide - 1) }
                            Copy { objectName: "resultSlideCounter"; text: "Slide " + (bridge.quickResult.slide || 1) + " / " + (bridge.quickResult.total || 0); color: root.ink }
                            MainAction { objectName: "resultNextSlide"; text: "›"; implicitHeight: 34; enabled: !bridge.busy && (bridge.quickResult.slide || 1) < bridge.quickResult.total; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide + 1) }
                            Item { Layout.fillWidth: true }
                            RowLayout {
                                objectName: "createdNarrationListening"; visible: root.page === "voice" && root.narrationComplete
                                spacing: 8
                                MainAction { objectName: "listenCreatedEnglish"; text: "Nghe Anh"; iconName: "play"; implicitHeight: 34; visible: root.narrationMode !== "vi"; enabled: !bridge.busy; ToolTip.visible: hovered; ToolTip.text: "Nghe giọng Anh đã tạo của slide đang xem"; onClicked: bridge.narrationWorkspace.listenCreated(bridge.quickResult.slide || 1, "en", root.narrationDraft.id) }
                                MainAction { objectName: "listenCreatedVietnamese"; text: "Nghe Việt"; iconName: "play"; implicitHeight: 34; visible: root.narrationMode !== "en"; enabled: !bridge.busy; ToolTip.visible: hovered; ToolTip.text: "Nghe giọng Việt đã tạo của slide đang xem"; onClicked: bridge.narrationWorkspace.listenCreated(bridge.quickResult.slide || 1, "vi", root.narrationDraft.id) }
                                MainAction { objectName: "stopCreatedNarration"; text: "Dừng nghe"; implicitHeight: 34; danger: true; symbol: "■"; onClicked: bridge.stopSpeech() }
                            }
                        }
                        Surface {
                            id: lessonNarrationPanel; objectName: "lessonNarrationPanel"; visible: root.page === "voice"
                            readonly property real contentPadding: root.compactVoice ? 16 : 20
                            Layout.fillWidth: true
                            implicitHeight: narrationForm.height + contentPadding * 2
                            ColumnLayout {
                                id: narrationForm; objectName: "narrationConfigurationForm"; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: lessonNarrationPanel.contentPadding; spacing: root.compactVoice ? 10 : 12
                                Caption { objectName: "narrationConfigurationTitle"; text: "Cấu hình tạo giọng đọc"; font.pixelSize: 15; Layout.fillWidth: true }
                                RowLayout { Layout.fillWidth: true
                                    Caption { Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap; text: root.narrationComplete ? "Hoàn tất giọng đọc" : root.page === "voice" ? "Giọng đọc và ngôn ngữ" : "Tạo giọng đọc · không bắt buộc" }
                                    Item { Layout.fillWidth: true }
                                    MainAction { objectName: "toggleCompletedNarrationConfiguration"; visible: root.page === "voice" && root.narrationComplete; text: root.voiceConfigurationExpanded ? "Ẩn cấu hình" : "Đổi cấu hình"; subtle: true; implicitHeight: 30; onClicked: { root.voiceConfigurationExpanded = !root.voiceConfigurationExpanded; if (root.voiceConfigurationExpanded) root.narrationOptionsPinned = true } }
                                    Copy { objectName: "lessonNarrationState"; Layout.maximumWidth: narrationForm.width * 0.55; visible: bridge.narrationBusy; text: "Đang tạo giọng…"; color: root.narrationDraft.ready ? AppTheme.adapt("#168567") : root.muted }
                                }
                                ColumnLayout {
                                objectName: "narrationCreationOptions"; Layout.fillWidth: true
                                visible: !root.narrationComplete || root.voiceConfigurationExpanded
                                spacing: root.compactVoice ? 12 : 16
                                GridLayout { Layout.fillWidth: true; columns: width >= 640 ? 3 : 2; columnSpacing: 10; rowSpacing: 8
                                    Choice { objectName: "lessonNarrationVoiceChoice"; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.preferredWidth: 290
                                        Accessible.name: "Cặp giọng Việt–Mỹ"; hoverEnabled: true
                                        ToolTip.visible: hovered; ToolTip.text: "Chọn cặp giọng Việt–Mỹ. Mỗi ngôn ngữ có một người đọc riêng."
                                        model: bridge.multilingualVoices; textRole: "name"; valueRole: "id"
                                        currentIndex: Math.max(0, bridge.multilingualVoices.map(function(v) { return v.id }).indexOf(root.narrationVoice))
                                        enabled: !bridge.busy && !bridge.narrationBusy; onActivated: { bridge.stopSpeech(); root.narrationVoice = currentValue; bridge.saveMultilingualVoice(root.narrationVoice, root.narrationRate); if (root.page === "voice") root.narrationOptionsPinned = true }
                                    }
                                    Choice { objectName: "lessonNarrationRateChoice"; Layout.preferredWidth: 100; model: ["82%", "88%", "94%", "100%", "106%", "112%", "118%"]
                                        Accessible.name: "Tốc độ đọc"; hoverEnabled: true
                                        ToolTip.visible: hovered; ToolTip.text: "Tốc độ đọc: 100% là bình thường; số nhỏ hơn đọc chậm hơn."
                                        currentIndex: root.narrationRate + 3; enabled: !bridge.busy && !bridge.narrationBusy
                                        onActivated: { bridge.stopSpeech(); root.narrationRate = currentIndex - 3; bridge.saveMultilingualVoice(root.narrationVoice, root.narrationRate); if (root.page === "voice") root.narrationOptionsPinned = true }
                                    }
                                    MainAction { objectName: "previewLessonNarrationVoice"; text: root.narrationPreviewActive ? "Dừng" : "Nghe thử"; iconName: root.narrationPreviewActive ? "pause" : "play"; enabled: !!root.narrationVoice && !bridge.narrationBusy
                                        ToolTip.visible: hovered
                                        ToolTip.text: root.narrationMode === "both" ? "Nghe mẫu dài giọng Việt, rồi giọng Anh–Mỹ trong cặp đã chọn." : "Nghe mẫu dài tiếng " + (root.narrationMode === "vi" ? "Việt" : "Anh–Mỹ") + " bằng giọng và tốc độ đã chọn."
                                        onClicked: {
                                            if (root.narrationPreviewActive) { bridge.stopSpeech(); return }
                                            const samples = bridge.voicePreviewSamples
                                            if (root.narrationMode === "both") bridge.previewMultilingualVoice(root.narrationVoice, root.narrationRate, samples.vi + "\n" + samples.en)
                                            else bridge.previewNarrationLanguage(root.narrationMode, root.narrationVoice, root.narrationRate, samples[root.narrationMode])
                                        }
                                    }
                                }
                                GridLayout { objectName: "narrationLanguagePositionRow"; Layout.fillWidth: true; uniformCellWidths: true
                                columns: parent.width >= 2 * Math.max(narrationLanguageChoices.naturalWidth, narrationPositionRow.implicitWidth) + columnSpacing ? 2 : 1; columnSpacing: 24; rowSpacing: 10
                                Item { objectName: "narrationLanguageCell"; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.alignment: Qt.AlignVCenter
                                implicitHeight: narrationLanguageChoices.implicitHeight
                                GridLayout { id: narrationLanguageChoices; objectName: "narrationLanguageChoices"; anchors.centerIn: parent; width: Math.min(720, parent.width); columns: 3; columnSpacing: 8; uniformCellWidths: true
                                    readonly property real naturalWidth: 3 * 160 + columnSpacing * 2
                                    ButtonGroup { id: narrationLanguages }
                                    ConversionChoice { choiceName: "narrationEnglish"; label: "Tiếng Anh"; detail: "Chỉ đọc lời tiếng Anh của bài."; fitContent: true; Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; choiceGroup: narrationLanguages; selected: root.narrationMode === "en"; enabled: !bridge.busy && !bridge.narrationBusy && (!bridge.quickResult.path || bridge.narrationInputLanguages.en); onChosen: root.chooseNarrationMode("en") }
                                    ConversionChoice { choiceName: "narrationVietnamese"; label: "Tiếng Việt"; detail: "Chỉ đọc lời tiếng Việt của bài."; fitContent: true; Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; choiceGroup: narrationLanguages; selected: root.narrationMode === "vi"; enabled: !bridge.busy && !bridge.narrationBusy && (!bridge.quickResult.path || bridge.narrationInputLanguages.vi); onChosen: root.chooseNarrationMode("vi") }
                                    ConversionChoice { choiceName: "narrationBoth"; label: "Cả Anh và Việt"; detail: "Hai loa riêng VI và EN trên mỗi slide."; fitContent: true; Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; choiceGroup: narrationLanguages; selected: root.narrationMode === "both"; enabled: !bridge.busy && !bridge.narrationBusy && (!bridge.quickResult.path || bridge.narrationInputLanguages.vi && bridge.narrationInputLanguages.en); onChosen: root.chooseNarrationMode("both") }
                                }
                                }
                                Item { objectName: "narrationPositionCell"; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.alignment: Qt.AlignVCenter
                                implicitHeight: narrationPositionControls.implicitHeight
                                ColumnLayout { id: narrationPositionControls; objectName: "narrationPositionControls"; anchors.centerIn: parent; width: Math.min(420, parent.width); spacing: 8
                                RowLayout { id: narrationPositionRow; Layout.alignment: Qt.AlignHCenter; spacing: 10
                                    Caption { text: "Vị trí loa" }
                                    Choice { objectName: "narrationSpeakerPosition"; Layout.preferredWidth: 170
                                        id: speakerPositionChoice; Accessible.name: "Vị trí loa trên slide"; hoverEnabled: true
                                        ToolTip.visible: hovered; ToolTip.text: "Cố định cùng vị trí trên mọi slide. Đổi vị trí dùng lại giọng đã lưu."
                                        readonly property var positionKeys: ["top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right"]
                                        model: ["Trái trên", "Giữa trên", "Phải trên", "Trái dưới", "Giữa dưới", "Phải dưới"]
                                        currentIndex: Math.max(0, positionKeys.indexOf(bridge.narrationWorkspace.speakerPosition))
                                        enabled: bridge.narrationWorkspace.configurationEnabled
                                        onActivated: bridge.narrationWorkspace.setSpeakerPosition(positionKeys[currentIndex])
                                        popup: Popup {
                                            objectName: "speakerPositionPopup"; y: speakerPositionChoice.height + 4; width: 300
                                            x: speakerPositionChoice.width - width; padding: 8
                                            implicitHeight: contentItem.implicitHeight + topPadding + bottomPadding
                                            background: Rectangle { radius: 9; color: AppTheme.surface; border.color: AppTheme.line }
                                            contentItem: GridLayout {
                                                columns: 3; rowSpacing: 6; columnSpacing: 6
                                                Repeater {
                                                    model: speakerPositionChoice.model
                                                    MainAction {
                                                        required property string modelData
                                                        required property int index
                                                        objectName: "speakerPosition_" + speakerPositionChoice.positionKeys[index]
                                                        Layout.fillWidth: true; implicitHeight: 38; leftPadding: 8; rightPadding: 8
                                                        text: modelData; font.pixelSize: 12; primary: speakerPositionChoice.currentIndex === index
                                                        onClicked: {
                                                            bridge.narrationWorkspace.setSpeakerPosition(speakerPositionChoice.positionKeys[index])
                                                            speakerPositionChoice.popup.close()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        contentItem: RowLayout {
                                            spacing: 9
                                            Rectangle { Layout.preferredWidth: 32; Layout.preferredHeight: 20; radius: 3; color: AppTheme.adapt("#f3f7fc"); border.color: AppTheme.adapt("#b8c9df")
                                                Rectangle { width: 7; height: 5; radius: 1; color: root.blue; y: speakerPositionChoice.currentIndex < 3 ? 2 : 12; x: [3, 12, 21][speakerPositionChoice.currentIndex % 3] || 3 }
                                            }
                                            Label { text: speakerPositionChoice.currentText; color: root.ink; font.pixelSize: 13; Layout.fillWidth: true; elide: Text.ElideRight }
                                        }
                                    }
                                }
                                Copy { objectName: "narrationPositionDescription"; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; font.pixelSize: 12; text: "Chọn nơi đặt loa trên tất cả slide." }
                                }
                                }
                                }
                                Copy {
                                    objectName: "narrationLanguageAvailability"; Layout.fillWidth: true; font.pixelSize: 12
                                    visible: !!bridge.quickResult.path && (bridge.narrationInputLanguages.vi !== bridge.narrationInputLanguages.en)
                                    text: bridge.narrationInputLanguages.vi
                                        ? "Bài hiện có lời tiếng Việt. Muốn tạo giọng Anh hoặc Anh–Việt, hãy chuyển bài sang song ngữ trước."
                                        : "Bài hiện có lời tiếng Anh. Muốn tạo cả hai giọng, cần có thêm lời tiếng Việt."
                                }
                                NarrationConfiguration {
                                    objectName: "completedNarrationConfiguration"; visible: root.narrationComplete && root.page !== "voice"; Layout.fillWidth: true
                                    mode: root.narrationMode
                                    voiceName: (bridge.multilingualVoices.find(function(v) { return v.id === root.narrationVoice }) || {}).name || ""
                                    pairLabel: bridge.voicePairDetails(root.narrationVoice).label || ""
                                    rate: root.narrationRate; readable: root.narrationReadableSlides; total: root.narrationEligibleSlides
                                    vietnameseSlides: root.narrationCoverage.vi || 0; englishSlides: root.narrationCoverage.en || 0
                                    hasLesson: !!bridge.quickResult.path
                                    positionLabel: speakerPositionChoice.currentText
                                }
                                Copy { visible: !bridge.multilingualVoices.length; text: "Bộ giọng chưa sẵn sàng. Kiểm tra trong Cài đặt → Giọng đọc trước khi tạo."; color: AppTheme.adapt("#a66318"); Layout.fillWidth: true }
                                RowLayout { objectName: "narrationScriptNotice"; visible: root.page === "voice" && !!bridge.quickResult.path && (root.narrationMode === "both" ? root.narrationPartialSlides > 0 : root.narrationSkippedSlides > 0); Layout.fillWidth: true
                                    Copy { objectName: "narrationCoverageMessage"; Layout.fillWidth: true; font.pixelSize: 12; color: AppTheme.adapt("#a66318"); text: root.narrationMode === "both" ? (root.narrationEligibleSlides - root.narrationCoverage.vi) + " slide thiếu lời Việt · " + (root.narrationEligibleSlides - root.narrationCoverage.en) + " slide thiếu lời Anh. Tool sẽ đọc phần đã có; có thể bổ sung tại đây." : root.narrationSkippedSlides + " slide chưa có lời " + (root.narrationMode === "en" ? "tiếng Anh" : "tiếng Việt") + ". Tool đã tự phân loại; slide chỉ có ảnh hoặc không có lời sẽ được bỏ qua." }
                                    MainAction { objectName: "fixMissingNarration"; text: "Kiểm tra / bổ sung"; subtle: true; implicitHeight: 32; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.teachingTransitioning; onClicked: { bridge.narrationWorkspace.selectProblem(root.narrationMode); narrationScript.open() } }
                                }
                                CheckBox { objectName: "embedPresentationVoice"; visible: root.page !== "voice" && !!bridge.quickResult.path && !!bridge.selectedNarrationVariant; checked: root.includeDownloadVoice; onClicked: root.includeDownloadVoice = checked; text: "Kèm loa đọc toàn bộ lời đã lưu của slide khi bấm" }
                                }
                                RowLayout { Layout.fillWidth: true; visible: !!bridge.lessonNarration.running
                                    ProgressBar { objectName: "lessonNarrationProgressBar"; Layout.fillWidth: true; from: 0; to: 100; value: bridge.lessonNarration.percent || 0 }
                                    Caption { objectName: "lessonNarrationPercent"; text: (bridge.lessonNarration.percent || 0) + "%" }
                                }
                                RowLayout { Layout.fillWidth: true; visible: !!bridge.narrationPreparation.lesson_id && (bridge.lessonNarration.running || bridge.narrationClock.elapsedSeconds > 0 && !root.narrationDraft.ready)
                                    Copy { objectName: "lessonNarrationElapsed"; text: "Thời gian tạo giọng: " + root.durationText(bridge.narrationClock.elapsedSeconds); color: root.ink; font.pixelSize: 12 }
                                    Item { Layout.fillWidth: true }
                                    Copy { text: (bridge.lessonNarration.complete || 0) + " / " + (bridge.lessonNarration.total || 0) + " đoạn sẵn sàng"; color: root.muted; font.pixelSize: 12 }
                                }
                                Copy { objectName: "narrationPreparationStatus"; Layout.fillWidth: true; visible: !!bridge.lessonNarration.message && !root.narrationDraft.ready; text: bridge.lessonNarration.message || ""; color: root.muted; font.pixelSize: 12 }
                                NarrationReadyCard {
                                    objectName: "narrationReadyNextStep"; visible: !!bridge.quickResult.path && !!root.narrationDraft.ready && !bridge.narrationBusy
                                    Layout.fillWidth: true; busy: bridge.busy || bridge.narrationBusy; opening: bridge.teachingTransitioning
                                    summary: root.narrationDraft.title || ""; total: root.narrationDraft.total || 0
                                    coverage: bridge.narrationWorkspace.playbackCoverage
                                    onOpenPowerPoint: bridge.openNarratedPowerPoint(root.narrationDraft.id)
                                    onShowInLibrary: root.showNarratedLessonInLibrary()
                                    onDownloadPresentation: { if (root.narrationDraft.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(root.narrationDraft.id); if (bridge.selectedNarrationVariant === root.narrationDraft.id) { root.includeDownloadVoice = true; presentationSave.openSuggested() } }
                                    onDownloadAudio: { if (root.narrationDraft.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(root.narrationDraft.id); if (bridge.selectedNarrationVariant === root.narrationDraft.id) narrationAudioSave.openSuggested() }
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; visible: !!bridge.powerpointState.active || !!bridge.teachingTransitioning
                            Copy { text: bridge.powerpointState.message || "Đang trình chiếu"; Layout.fillWidth: true }
                            MainAction { text: "Slide trước"; enabled: bridge.powerpointState.active; onClicked: bridge.navigatePowerPoint("previous") }
                            MainAction { text: "Slide tiếp"; enabled: bridge.powerpointState.active; onClicked: bridge.navigatePowerPoint("next") }
                            MainAction { text: "Đọc tiếng Anh"; enabled: bridge.powerpointState.active && !bridge.busy && !!bridge.audioAvailable.en; onClicked: bridge.readSlideEnglish() }
                            MainAction { text: "Đọc tiếng Việt"; enabled: bridge.powerpointState.active && !bridge.busy && !!bridge.audioAvailable.vi; onClicked: bridge.speakSegment("vi") }
                            MainAction { text: "Đóng trình chiếu"; onClicked: bridge.stopPowerPoint() }
                        }
                        RowLayout { visible: bridge.powerpointState.active; Layout.fillWidth: true
                            Copy { text: bridge.englishReaderState.message; Layout.fillWidth: true }
                            MainAction { text: bridge.englishReaderState.state === "paused" ? "Tiếp tục" : "Tạm dừng"; enabled: ["reading", "preparing", "paused"].indexOf(bridge.englishReaderState.state) >= 0; onClicked: bridge.englishReaderState.state === "paused" ? bridge.resumeEnglish() : bridge.pauseEnglish() }
                            MainAction { text: "Dừng đọc"; onClicked: bridge.stopSpeech() }
                            MainAction { text: "Đọc lại"; enabled: !bridge.busy; onClicked: bridge.readSlideEnglish() }
                        }
                        Surface {
                            objectName: "lessonDetailsPanel"; visible: root.resultDetails
                            Layout.fillWidth: true; implicitHeight: resultInfo.height + 32
                            ColumnLayout {
                                id: resultInfo; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16; spacing: 10
                                Copy { visible: !!bridge.narrationPreparation.total; text: "Giọng đọc: " + (bridge.narrationPreparation.complete || 0) + "/" + bridge.narrationPreparation.total + " đoạn đã sẵn sàng"; Layout.fillWidth: true }
                                Copy { visible: bridge.experimentalTeaching && !!root.lessonData.conversion_format && (root.lessonData.questions || []).length > 0; text: (root.lessonData.questions || []).filter(function(q) { return !q.approved }).length + " câu hỏi nháp · xem và duyệt riêng trong Chỉnh sửa chi tiết → Trợ giảng & Quiz."; Layout.fillWidth: true }
                                Copy { Layout.fillWidth: true; text: (bridge.quickResult.missing || []).length ? "Chưa đủ song ngữ: " + bridge.quickResult.missing.slice(0, 8).join(", ") : "Kiểm tra thuật ngữ, số liệu và ý nghĩa trong bản trình chiếu. Có thể tạo thêm giọng đọc khi cần." }
                                Copy { Layout.fillWidth: true; visible: (((root.lessonData.source || {}).warnings || []).length > 0); text: ((root.lessonData.source || {}).warnings || []).slice(0, 3).join("\n") }
                            }
                        }
                        }
                    }
                }

                NarrationResult {
                    anchors.fill: parent; anchors.margins: root.compactVoice ? 18 : 28
                    visible: root.page === "voice" && root.voiceResultShown
                    bridge: root.bridgeRef
                    record: root.narrationDraft
                    coverage: bridge.narrationWorkspace.playbackCoverage
                    onRequestLibrary: root.showNarratedLessonInLibrary()
                    onRequestConfiguration: root.openVoiceConfiguration()
                    onRequestPowerPoint: bridge.openNarratedPowerPoint(root.narrationDraft.id)
                    onRequestDownload: {
                        if (root.narrationDraft.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(root.narrationDraft.id)
                        if (bridge.selectedNarrationVariant === root.narrationDraft.id) { root.includeDownloadVoice = true; presentationSave.openSuggested() }
                    }
                    onRequestAudio: {
                        if (root.narrationDraft.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(root.narrationDraft.id)
                        if (bridge.selectedNarrationVariant === root.narrationDraft.id) narrationAudioSave.openSuggested()
                    }
                }

                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 23; spacing: 15; visible: root.page === "editor"; enabled: !bridge.busy
                    RowLayout {
                        Layout.fillWidth: true
                        ColumnLayout { spacing: 5; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.maximumWidth: 310
                            Heading { text: root.lessonData.title || "Chọn một bài học"; font.pixelSize: 22; Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 1 }
                            Copy { text: (root.lessonData.subject || "") + " · " + (root.lessonData.education_level || "") + " " + (root.lessonData.grade || ""); font.pixelSize: 11 }
                            MainAction { objectName: "backToConvertedLessonButton"; text: "Bản trình chiếu"; iconName: "back"; subtle: true; implicitHeight: 28; onClicked: root.go("result") }
                        }
                        Item { Layout.fillWidth: true }
                        Pill { text: root.dirty ? "Chưa lưu thay đổi" : "Đã lưu trên máy"; tone: root.dirty ? AppTheme.adapt("#ad651d") : AppTheme.adapt("#168567") }
                        MainAction { text: "Lịch sử"; enabled: !!root.lessonData.id; onClicked: root.requestAction(function() { historyDialog.open() }) }
                        MainAction { objectName: "previewButton"; text: root.keepSourceDesign ? "So sánh gốc / song ngữ" : "Xem trước"; iconName: "view"; enabled: !!root.lessonData.id && !bridge.busy; onClicked: root.requestAction(function() { if (root.keepSourceDesign) bridge.comparePowerPoint(1); else { root.rescue = false; preview.show() } }) }
                        MainAction { text: "PPTX"; enabled: !bridge.busy; onClicked: root.requestAction(function() { deckSave.openSuggested() }) }
                        MainAction { text: "Gói bài"; primary: true; enabled: !!root.lessonData.id && !bridge.busy; onClicked: root.requestAction(function() { packSave.openSuggested() }) }
                    }
                    Copy { visible: ((root.lessonData.source || {}).warnings || []).length > 0; text: ((root.lessonData.source || {}).warnings || []).join("\n"); color: AppTheme.adapt("#ad651d"); font.pixelSize: 11; Layout.fillWidth: true }
                    RowLayout {
                        Layout.fillWidth: true; spacing: 12
                        CheckBox { objectName: "keepPowerPointDesign"; text: "Giữ thiết kế gốc"; visible: bridge.powerpointAvailable && !root.lessonData.external_deck; checked: root.keepSourceDesign; onClicked: { let style = checked ? "source" : "template"; root.requestAction(function() { bridge.setPresentationStyle(style) }) } }
                        Choice { id: presetChoice; objectName: "presetChoice"; visible: !root.keepSourceDesign; model: ["Chuẩn lớp học", "Trực quan", "Luyện tập & tương tác"]; currentIndex: Math.max(0, ["standard", "visual", "practice"].indexOf(root.lessonData.teaching_preset || "standard")); Layout.preferredWidth: 195; onActivated: bridge.setTeachingPreset(["standard", "visual", "practice"][currentIndex]) }
                        MainAction { objectName: "editorTemplatesButton"; text: "Mẫu"; visible: !root.keepSourceDesign; onClicked: root.requestAction(function() { templateGallery.forCreation = false; templateGallery.preset = root.lessonData.teaching_preset || "standard"; templateGallery.level = root.lessonData.level || 0; templateGallery.layout = root.lessonData.layout || "line_pair"; templateGallery.open() }) }
                        Pill { visible: !!root.lessonData.conversion_format; text: bridge.conversionLabel }
                        MainAction { text: "Trợ giảng & Quiz"; objectName: "teachingButton"; visible: bridge.experimentalTeaching; onClicked: root.requestAction(function() { teachingDialog.open() }) }
                        Item { Layout.fillWidth: true }
                        MainAction { objectName: "readinessButton"; text: "Chuẩn bị lên lớp"; visible: bridge.experimentalTeaching; onClicked: root.requestAction(function() { bridge.refreshReadiness(); readinessDialog.open() }) }
                    }
                    RowLayout { visible: bridge.powerpointAvailable; Layout.fillWidth: true; spacing: 9
                        Copy { text: bridge.powerpointState.active ? bridge.powerpointState.message : root.keepSourceDesign ? (bridge.experimentalTeaching ? "Giữ thiết kế gốc · theo cách chuyển đổi đã chọn · trợ giảng dùng nội dung đã duyệt" : "Giữ thiết kế gốc · theo cách chuyển đổi đã chọn") : "Nguồn PowerPoint · mở bản chỉ đọc"; Layout.fillWidth: true; font.pixelSize: 11 }
                        MainAction { objectName: "openPowerPointButton"; text: root.keepSourceDesign ? "Mở PowerPoint song ngữ" : "Mở PowerPoint gốc"; visible: !bridge.powerpointState.active; enabled: !!root.lessonData.id && !bridge.busy && !bridge.teachingTransitioning; implicitHeight: 32; onClicked: root.requestAction(function() { if (root.keepSourceDesign) bridge.startBilingualPowerPoint(); else bridge.startPowerPoint() }) }
                        MainAction { text: "Slide trước"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.navigatePowerPoint("previous") }
                        MainAction { text: "Đến slide đoạn này"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.navigatePowerPoint("goto") }
                        MainAction { text: "Slide tiếp"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.navigatePowerPoint("next") }
                        MainAction { text: "Đóng PowerPoint"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.stopPowerPoint() }
                    }
                    RowLayout {
                        Layout.fillWidth: true; spacing: 12
                        Copy { text: "Giữ cặp ngôn ngữ đang có; phần dịch mới là bản nháp để thầy cô duyệt."; Layout.fillWidth: true; font.pixelSize: 11 }
                    }
                    RowLayout {
                        Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16
                        Surface {
                            Layout.preferredWidth: 208; Layout.fillHeight: true
                            ColumnLayout { anchors.fill: parent; anchors.margins: 15; spacing: 12
                                Caption { text: "Nội dung bài"; font.pixelSize: 14 }
                                Copy { text: bridge.approvedCount + "/" + ((root.lessonData.segments || []).length) + " đoạn đã duyệt"; font.pixelSize: 11 }
                                ProgressBar { Layout.fillWidth: true; value: bridge.approvedCount / Math.max(1, (root.lessonData.segments || []).length) }
                                ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: root.lessonData.segments || []
                                    delegate: ItemDelegate {
                                        required property var modelData; required property int index
                                        width: ListView.view.width; height: 84
                                        onClicked: { let target = index; root.requestAction(function() { bridge.selectSegment(target) }) }
                                        background: Rectangle { color: index === bridge.segmentIndex ? AppTheme.adapt("#eaf3ff") : parent.hovered ? AppTheme.adapt("#f5f8fc") : "transparent"; radius: 9; border.color: index === bridge.segmentIndex ? AppTheme.adapt("#a8cdff") : "transparent" }
                                        contentItem: ColumnLayout { spacing: 6
                                            Label { text: (index + 1) + ". " + modelData.locator; color: index === bridge.segmentIndex ? root.blue : root.ink; font.pixelSize: 11; font.weight: Font.DemiBold; elide: Text.ElideRight; Layout.fillWidth: true }
                                            Copy { text: (modelData.vi || modelData.en).replace(/\n/g, " "); maximumLineCount: 2; elide: Text.ElideRight; font.pixelSize: 10; Layout.fillWidth: true }
                                            Copy { text: modelData.approved ? "✓ Đã duyệt" : modelData.vi && modelData.en ? "● Chờ duyệt" : "○ Chưa đủ song ngữ"; font.pixelSize: 9; color: modelData.approved ? AppTheme.adapt("#168567") : root.muted }
                                        }
                                    }
                                }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumWidth: 0
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 21; spacing: 13
                                RowLayout { Layout.fillWidth: true
                                    Caption { text: bridge.segment.locator || "Nội dung"; font.pixelSize: 15; Layout.fillWidth: true; elide: Text.ElideRight }
                                    Pill { text: root.dirty ? "Đang chỉnh sửa" : bridge.segment.approved ? "Đã duyệt" : "Bản nháp"; tone: bridge.segment.approved && !root.dirty ? AppTheme.adapt("#168567") : AppTheme.adapt("#9c651b") }
                                }
                                RowLayout { Layout.fillWidth: true; spacing: 7
                                    MainAction { text: "Thông tin bài"; implicitHeight: 30; subtle: true; onClicked: root.requestAction(function() { metadataDialog.open() }) }
                                    MainAction { text: "Tệp nguồn"; implicitHeight: 30; subtle: true; visible: !!root.lessonData.source; onClicked: bridge.openSourceCopy() }
                                    MainAction { text: "Nguồn"; implicitHeight: 30; subtle: true; onClicked: sourceDialog.open() }
                                    MainAction { text: "Tách đoạn"; implicitHeight: 30; subtle: true; onClicked: splitDialog.open() }
                                    Item { Layout.fillWidth: true }
                                }
                                RowLayout { Layout.fillWidth: true; visible: !root.keepSourceDesign
                                    Caption { text: "Loại slide" }
                                    Choice { objectName: "slideTypeChoice"; model: bridge.slideTypes; textRole: "label"; valueRole: "id"; Layout.fillWidth: true; currentIndex: Math.max(0, bridge.slideTypes.map(function(item) { return item.id }).indexOf(bridge.currentSlideType)); onActivated: { let selected = currentValue; root.requestAction(function() { bridge.setSlideType(selected) }) } }
                                }
                                RowLayout { Layout.fillWidth: true; Caption { text: "VI   Tiếng Việt" } Item { Layout.fillWidth: true }  }
                                ContentScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 56;
                                    TextArea { id: viEdit; objectName: "viEditor"; wrapMode: TextEdit.Wrap; selectByMouse: true; color: root.ink; font.pixelSize: 15; padding: 13; onTextChanged: root.edited(); background: Rectangle { radius: 9; color: AppTheme.adapt("#f8fafd"); border.color: parent.activeFocus ? root.blue : root.line } }
                                }
                                RowLayout { Layout.fillWidth: true; Caption { text: "EN   English"; color: root.blue } Item { Layout.fillWidth: true }
                                     }
                                ContentScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 56;
                                    TextArea { id: enEdit; objectName: "enEditor"; wrapMode: TextEdit.Wrap; selectByMouse: true; color: AppTheme.adapt("#1855a6"); font.pixelSize: 15; padding: 13; placeholderText: "Lời đọc tiếng Anh tương ứng với slide…"; onTextChanged: root.edited(); background: Rectangle { radius: 9; color: AppTheme.adapt("#f4f8ff"); border.color: parent.activeFocus ? root.blue : AppTheme.adapt("#d4e4fc") } }
                                }
                                MainAction { text: "Tìm bản dịch gần giống đã duyệt"; iconName: "search"; implicitHeight: 30; enabled: !bridge.busy && !lockedCheck.checked; onClicked: { root.translationSource = bridge.segment.source_language || root.lessonData.source_language || "vi"; if (!root.dirty || root.save(false)) bridge.suggestSimilar(root.translationSource) } }
                                Copy { text: "Kiểm tra lời đọc, thuật ngữ, số liệu và công thức trước khi duyệt. Chỉnh lời đọc ở đây không thay chữ trong PowerPoint đã nhận."; font.pixelSize: 10; Layout.fillWidth: true }
                                Copy { visible: bridge.reviewWarnings.length > 0; text: bridge.reviewWarnings.join("\n"); color: AppTheme.adapt("#ad651d"); font.pixelSize: 11; Layout.fillWidth: true }
                                RowLayout {
                                    Layout.fillWidth: true
                                    CheckBox { id: lockedCheck; text: "Khóa nội dung"; font.pixelSize: 11; onToggled: root.edited() }
                                    Item { Layout.fillWidth: true }
                                    MainAction { objectName: "saveDraftButton"; text: "Lưu nháp"; iconName: "save"; enabled: !!root.lessonData.id; onClicked: root.save(false) }
                                    MainAction { objectName: "approveButton"; text: "✓  Duyệt đoạn"; primary: true; enabled: !!root.lessonData.id && enEdit.text.trim() !== "" && viEdit.text.trim() !== ""; onClicked: root.save(true) }
                                }
                            }
                        }
                    }
                    Copy { text: root.statusLabel(bridge.status) + "  ·  Tự lưu bản nháp sau khi ngừng nhập" + (root.keepSourceDesign ? "  ·  Xem bài song ngữ bằng PowerPoint" : "  ·  Xem trước hiện hỗ trợ văn bản"); font.pixelSize: 10; Layout.fillWidth: true }
                }

                ClassroomPage { objectName: "classroomPage"; anchors.fill: parent; anchors.margins: 26; visible: root.page === "classroom"; classroom: root.classroom; bridge: root.bridgeRef; onRequestLibrary: root.go("library"); onRequestPreparation: { bridge.refreshReadiness(); readinessDialog.open() } onRequestEditor: teachingDialog.openQuestions(); onRequestReports: root.go("reports") }
                ReportsPage { objectName: "reportsPage"; anchors.fill: parent; anchors.margins: 26; visible: root.page === "reports"; classroom: root.classroom; bridge: root.bridgeRef; onRequestClassroom: root.go("classroom") }

                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 30; spacing: 16
                    visible: root.page === "reference"
                    RowLayout { Layout.fillWidth: true; Heading { text: "Thuật ngữ & kiến thức"; Layout.fillWidth: true } MainAction { text: "Về Cài đặt"; onClicked: { root.go("settings"); settingsPanel.activeTab = 5 } } }
                    Copy { text: "Tra cứu và quản lý nội dung đã lưu khi cần. Không cần cấu hình kho dữ liệu để chuyển đổi bài giảng."; Layout.fillWidth: true }
                    RowLayout {
                        MainAction { objectName: "teacherDataTab"; text: "Thuật ngữ của tôi"; primary: root.referenceTab === 0; onClicked: root.referenceTab = 0 }
                        MainAction { objectName: "foundationDataTab"; text: "Kiến thức có nguồn"; primary: root.referenceTab === 1; onClicked: root.referenceTab = 1 }
                    }
                    Item {
                        Layout.fillWidth: true; Layout.fillHeight: true
                ContentScrollView {
                    id: termsScroll; objectName: "termsScroll"; outerGutter: true; anchors.fill: parent; anchors.margins: 0; visible: root.referenceTab === 0; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 20
                        Copy { text: "Thuật ngữ thầy cô đã duyệt để tra cứu và giữ cách dùng từ nhất quán. Dữ liệu riêng vẫn được lưu và sao lưu trên máy."; Layout.fillWidth: true }
                        Surface { Layout.fillWidth: true; implicitHeight: termForm.height + 40
                            ColumnLayout { id: termForm; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 20; spacing: 12
                                Caption { text: "Thêm hoặc cập nhật thuật ngữ"; font.pixelSize: 16 }
                                RowLayout { Layout.fillWidth: true; spacing: 12
                                    Field { id: termSubject; placeholderText: "Môn học"; Layout.fillWidth: true; maximumLength: 100 }
                                    Field { id: termVi; placeholderText: "Thuật ngữ tiếng Việt"; Layout.fillWidth: true; maximumLength: 300 }
                                    Field { id: termEn; placeholderText: "English term"; Layout.fillWidth: true; maximumLength: 300 }
                                }
                                RowLayout { CheckBox { id: termLocked; checked: true; text: "Đánh dấu thuật ngữ ưu tiên"; font.pixelSize: 12 } Item { Layout.fillWidth: true } MainAction { text: "Lưu thuật ngữ"; primary: true; onClicked: bridge.saveTerm(termSubject.text, termVi.text, termEn.text, termLocked.checked) } }
                            }
                        }
                        RowLayout { Layout.fillWidth: true
                            Field { id: termSearch; objectName: "termSearch"; placeholderText: "Tìm thuật ngữ Việt, Anh hoặc môn…"; Layout.fillWidth: true; maximumLength: 300; onTextChanged: root.termPage = 1 }
                            SelectBox { id: termSubjectFilter; objectName: "termSubjectFilter"; model: ["Tất cả môn học"].concat(bridge.terms.map(function(row) { return row.subject }).filter(function(subject, index, all) { return all.indexOf(subject) === index }).sort()); Layout.preferredWidth: 185; onActivated: root.termPage = 1 }
                        }
                        Copy { text: root.filteredTerms.length + " / " + bridge.terms.length + " thuật ngữ" }
                        Copy { visible: bridge.terms.length === 0; text: "Chưa có thuật ngữ. Thêm các từ cần dùng nhất quán trong bài giảng của thầy cô."; Layout.fillWidth: true }
                        Copy { visible: bridge.terms.length > 0 && root.filteredTerms.length === 0; text: "Không tìm thấy thuật ngữ. Thử bỏ bớt từ khóa hoặc bộ lọc."; Layout.fillWidth: true }
                        Repeater { model: root.filteredTerms.slice((root.termPage - 1) * 20, root.termPage * 20)
                            delegate: Surface { required property var modelData; Layout.fillWidth: true; implicitHeight: 80
                                RowLayout { anchors.fill: parent; anchors.margins: 17; spacing: 20
                                    Pill { text: modelData.subject; Layout.maximumWidth: 160 }
                                    Label { text: modelData.vi; color: root.ink; font.pixelSize: 14; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                                    Label { text: modelData.en; color: root.blue; font.pixelSize: 14; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                                    MainAction { text: "Sửa"; iconName: "edit"; subtle: true; onClicked: { termSubject.text = modelData.subject; termVi.text = modelData.vi; termEn.text = modelData.en; termLocked.checked = !!modelData.locked } }
                                    MainAction { text: "Xóa"; iconName: "delete"; subtle: true; onClicked: { deleteTermDialog.termId = modelData.id; deleteTermDialog.open() } }
                                }
                            }
                        }
                        RowLayout { visible: root.filteredTerms.length > 20; Layout.fillWidth: true
                            MainAction { text: "Trước"; enabled: root.termPage > 1; onClicked: root.termPage-- }
                            Copy { text: "Trang " + root.termPage + " / " + Math.max(1, Math.ceil(root.filteredTerms.length / 20)) }
                            MainAction { text: "Tiếp"; enabled: root.termPage * 20 < root.filteredTerms.length; onClicked: root.termPage++ }
                        }
                    }
                }

                ContentScrollView {
                    id: knowledgeScroll; objectName: "knowledgeScroll"; outerGutter: true; anchors.fill: parent; anchors.margins: 0; visible: root.referenceTab === 1; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout { Layout.fillWidth: true
                            ColumnLayout { Layout.fillWidth: true; spacing: 6
                                Copy { text: "Tra cứu nền tảng offline, xem nguồn chính thức và chọn từng thuật ngữ để đưa vào kho riêng của thầy cô."; Layout.fillWidth: true }
                            }
                            MainAction { text: "Cài gói kiến thức"; iconName: "upload"; primary: true; onClicked: knowledgeOpen.open() }
                        }
                        Surface { Layout.fillWidth: true; implicitHeight: knowledgeFilters.implicitHeight + 36
                            RowLayout { id: knowledgeFilters; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 18; spacing: 10
                                Field { id: knowledgeQuery; objectName: "knowledgeSearch"; placeholderText: "Tìm thuật ngữ, môn học hoặc tiếng Anh"; Layout.fillWidth: true; maximumLength: 300; onTextChanged: knowledgeSearchTimer.restart() }
                                Field { id: knowledgeSubject; placeholderText: "Lọc theo môn"; Layout.preferredWidth: 170 }
                                Field { id: knowledgeGrade; placeholderText: "Khối/cấp"; Layout.preferredWidth: 120 }
                            }
                        }
                        RowLayout { Layout.fillWidth: true; spacing: 10
                            Pill { text: bridge.knowledgeStats.entries + " mục" }
                            Pill { text: bridge.knowledgeStats.sources + " nguồn"; tone: AppTheme.adapt("#168567") }
                            Pill { text: bridge.knowledgeStats.packs + " gói"; tone: AppTheme.adapt("#8a5a00") }
                            Item { Layout.fillWidth: true }
                        }
                        Copy { text: "Ưu tiên: bản thầy cô đã duyệt → kiến thức nền → dữ liệu online có nguồn. Bản dịch từ kho nền vẫn cần duyệt. ‘Đưa vào kho riêng’ lưu cách dùng từ cho môn này."; Layout.fillWidth: true }
                        Repeater { model: root.knowledgeResults
                            delegate: Surface { required property var modelData; Layout.fillWidth: true; implicitHeight: knowledgeCard.implicitHeight + 30
                                ColumnLayout { id: knowledgeCard; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 15; spacing: 7
                                    RowLayout { Layout.fillWidth: true
                                        Pill { text: modelData.subject; tone: root.blue; Layout.maximumWidth: 230 }
                                        Pill { text: modelData.kind; tone: AppTheme.adapt("#8a5a00") }
                                        Item { Layout.fillWidth: true }
                                        MainAction { text: "Đưa vào kho riêng"; iconName: "save"; subtle: true; onClicked: bridge.promoteKnowledgeTerm(modelData.id) }
                                    }
                                    RowLayout { Layout.fillWidth: true; spacing: 18
                                        Label { text: modelData.vi; color: root.ink; font.pixelSize: 15; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                        Label { text: modelData.en; color: root.blue; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                    Copy { visible: !!modelData.definition_vi; text: modelData.definition_vi; Layout.fillWidth: true }
                                    Copy { visible: modelData.sources.length > 0; text: "Nguồn: " + modelData.sources[0].title; font.pixelSize: 11; Layout.fillWidth: true }
                                }
                            }
                        }
                        Copy { visible: root.knowledgeResults.length === 0; text: "Chưa có mục phù hợp. Hãy thử bỏ bớt bộ lọc hoặc cài một gói kiến thức mới."; Layout.fillWidth: true }
                        Caption { text: "Nguồn đã tích hợp"; font.pixelSize: 16 }
                        Repeater { model: bridge.knowledgeSources
                            delegate: Surface { required property var modelData; Layout.fillWidth: true; implicitHeight: sourceText.implicitHeight + 28
                                Copy { id: sourceText; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; text: modelData.title + "\n" + modelData.document_no + " · " + modelData.source_url; font.pixelSize: 11; wrapMode: Text.WordWrap }
                            }
                        }
                    }
                }

                    }
                }

                SettingsPage {
                    id: settingsPanel
                    anchors.fill: parent; anchors.margins: 26; visible: root.page === "settings"
                    bridge: root.bridgeRef
                    onRequestBackup: backupOpen.open()
                    onRequestLibrary: libraryOpen.open()
                    onRequestRelocation: relocationFolder.open()
                    onRequestBackupSave: backupSave.openSuggested()
                    onRequestSupportReport: supportReportSave.openSuggested()
                    onRequestLogo: logoOpen.open()
                    onRequestReference: root.go("reference")
                }
            }
            Rectangle {
                objectName: "applicationFooter"
                visible: true
                Layout.fillWidth: true; implicitHeight: footerContent.implicitHeight + 16
                color: root.taskRunning ? AppTheme.adapt("#eaf3ff") : AppTheme.adapt("#ffffff")
                RowLayout {
                    id: footerContent
                    anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 25; anchors.rightMargin: 25; spacing: 18
                    RowLayout { Layout.fillWidth: true; spacing: 10
                        BusyIndicator { visible: root.taskRunning; running: root.taskRunning; Layout.preferredWidth: 23; Layout.preferredHeight: 23 }
                        TaskStatusLink { id: statusMessage; objectName: "applicationStatusMessage"; returnable: root.taskElsewhere; Layout.maximumWidth: Math.max(120, parent.width - 200); text: !root.taskRunning ? root.idleActivity : bridge.narrationBusy ? "Đang tạo giọng đọc · " + (bridge.lessonNarration.percent || 0) + "%" : bridge.browserState.running ? (bridge.browserState.displayMessage || "Đang chuyển đổi bài giảng…") : bridge.inputDocuments.busy ? "Đang đọc PowerPoint…" : bridge.busy ? bridge.message || "Đang thực hiện tác vụ…" : bridge.updateState.message || "Đang tải bản mới…"; onReturnRequested: root.returnToTask() }
                        Item { Layout.fillWidth: true }
                        MainAction { objectName: "applicationCancel"; visible: bridge.busy && bridge.jobCancellable && !conversionCancel.visible; text: "Dừng tác vụ"; implicitHeight: 30; onClicked: bridge.cancelJob() }
                        MainAction { objectName: "applicationCancelNarration"; visible: bridge.narrationBusy && root.page !== "voice"; text: "Dừng tạo giọng"; implicitHeight: 30; enabled: !bridge.lessonNarration.stopping; onClicked: bridge.cancelLessonNarration() }
                    }
                }
            }
        }
    }
    Dialog {
        id: creationTemplatePreview; objectName: "creationTemplateImageDialog"
        property string preset: "standard"
        title: ({standard: "Chuẩn lớp học", visual: "Trực quan", practice: "Luyện tập & tương tác"})[preset] || "Xem mẫu"
        modal: true; anchors.centerIn: parent
        width: Math.min(1080, root.width - 48); height: Math.min(root.height - 64, width * 9 / 16 + 100)
        standardButtons: Dialog.Close
        contentItem: Image { objectName: "creationTemplateImage"; source: "../assets/templates/universal2026/previews/" + creationTemplatePreview.preset + ".png"; fillMode: Image.PreserveAspectFit; asynchronous: true; smooth: true }
    }
    FolderDialog { id: relocationFolder; objectName: "relocationFolderDialog"; title: "Chọn ổ hoặc thư mục chứa thư viện mới"; onAccepted: relocationConfirm.open() }
    Popup {
        id: operationError; objectName: "operationErrorNotice"
        property string notice: ""
        x: root.width - width - 24; y: 24
        width: Math.min(540, root.width - 48); padding: 16
        modal: false; focus: false; closePolicy: Popup.CloseOnEscape
        background: Rectangle { color: AppTheme.adapt("#fff8f4"); border.color: AppTheme.adapt("#e9c5ae"); radius: 12 }
        contentItem: ColumnLayout {
            spacing: 10
            RowLayout {
                Layout.fillWidth: true
                Caption { text: "Chưa hoàn tất thao tác"; Layout.fillWidth: true }
                MainAction { objectName: "dismissOperationError"; text: "Đóng"; subtle: true; implicitHeight: 28; onClicked: operationError.close() }
            }
            ScrollView {
                id: errorScroll; Layout.fillWidth: true; Layout.preferredHeight: Math.min(180, errorDescription.implicitHeight); clip: true
                contentWidth: availableWidth
                Copy { id: errorDescription; objectName: "operationErrorText"; width: errorScroll.availableWidth; text: operationError.notice; color: AppTheme.adapt("#a44727") }
            }
        }
    }
    SuggestedSaveDialog { id: backupSave; objectName: "backupSaveDialog"; title: "Lưu bản sao thư viện"; currentFolder: bridge.downloadsDirectory; defaultSuffix: "bcbackup"; nameFilters: ["BiliClass Backup (*.bcbackup)"]; suggestionProvider: function() { return bridge.exportSuggestion("bcbackup") }; onAccepted: bridge.backupLibrary(selectedFile.toString()) }
    SuggestedSaveDialog { id: supportReportSave; title: "Lưu chẩn đoán kỹ thuật"; currentFolder: bridge.downloadsDirectory; suggestionProvider: function() { return bridge.exportSuggestion("json") }; defaultSuffix: "json"; nameFilters: ["Chẩn đoán BiliClass (*.json)"]; onAccepted: bridge.exportSupportReport(selectedFile.toString()) }
    Dialog { id: relocationConfirm; objectName: "relocationConfirmDialog"; anchors.centerIn: parent; modal: true; title: "Chuyển cả thư viện"; width: Math.min(root.width - 64, 620)
        contentItem: ColumnLayout { spacing: 14
            Copy { text: "Nơi mới: " + bridge.storageControls.destination(relocationFolder.selectedFolder.toString()); Layout.fillWidth: true; wrapMode: Text.WrapAnywhere }
            Copy { text: "BiliClass sẽ sao chép và kiểm tra bài giảng, giọng đọc, cấu hình rồi mở lại. Khi thư viện mới mở thành công, dữ liệu đã chuyển ở nơi cũ được dọn để giải phóng dung lượng."; Layout.fillWidth: true }
            RowLayout { Layout.fillWidth: true; Item { Layout.fillWidth: true }
                MainAction { text: "Hủy"; onClicked: relocationConfirm.close() }
                MainAction { objectName: "confirmRelocationButton"; text: "Chuyển và mở lại"; primary: true; onClicked: { relocationConfirm.close(); root.requestAction(function() { bridge.storageControls.relocate(relocationFolder.selectedFolder.toString()) }) } }
            }
        }
    }
    Rectangle { anchors.fill: parent; z: 100; color: AppTheme.adapt("#eefaFCff"); visible: bridge.storageControls.moving
        ColumnLayout { anchors.centerIn: parent; spacing: 16
            BusyIndicator { running: parent.visible; Layout.alignment: Qt.AlignHCenter }
            Heading { text: "Đang chuyển thư viện"; Layout.alignment: Qt.AlignHCenter }
            Copy { text: "Đang sao chép và kiểm tra. BiliClass sẽ mở lại khi hoàn tất."; Layout.alignment: Qt.AlignHCenter }
        }
    }
    NarrationScriptDialog { id: narrationScript; workspace: bridge.narrationWorkspace; appBridge: bridge; voice: root.narrationVoice; rate: root.narrationRate; working: bridge.busy || bridge.narrationBusy }
    SuggestedSaveDialog { id: finalPresentationSave; objectName: "finalPresentationSaveDialog"; title: "Tải PowerPoint"; nameFilters: ["PowerPoint (*.pptx)"]; defaultSuffix: "pptx"; currentFolder: bridge.downloadsDirectory; suggestionProvider: function() { return root.lessonData.id ? bridge.libraryDownloadSuggestion([root.lessonData.id], true) : "" }; onAccepted: bridge.downloadFinalPresentation(selectedFile.toString()) }
    SuggestedSaveDialog { id: narrationAudioSave; objectName: "narrationAudioSaveDialog"; title: "Lưu audio theo slide"; nameFilters: ["Audio theo slide (*.zip)"]; defaultSuffix: "zip"; currentFolder: bridge.downloadsDirectory; suggestionProvider: function() { return bridge.exportSuggestion("zip") }; onAccepted: bridge.narrationWorkspace.exportAudio(selectedFile.toString()) }
    FileDialog { id: voicePresentationOpen; objectName: "voicePresentationFileDialog"; title: "Chọn PowerPoint để tạo giọng đọc"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.importNarrationPresentation(selectedFile.toString()) }
    FileDialog { id: documentOpen; objectName: "creationFileDialog"; title: "Chọn file PowerPoint"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: root.acceptInputDocuments([selectedFile.toString()]) }
    FileDialog { id: chatgptDeckOpen; title: "Nhận PowerPoint đã tải từ ChatGPT"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.receiveChatGPTDeck(selectedFile.toString()) }
    FileDialog { id: logoOpen; title: "Chọn logo trường"; nameFilters: ["Ảnh (*.png *.jpg *.jpeg)"]; onAccepted: bridge.saveSchoolLogo(selectedFile.toString()) }
    FileDialog { id: packOpen; title: "Nhập gói bài BiliClass"; nameFilters: ["BiliClass (*.biliclass)"]; onAccepted: bridge.importPack(selectedFile.toString()) }
    SuggestedSaveDialog { id: deckSave; title: "Xuất PowerPoint song ngữ mới"; currentFolder: bridge.downloadsDirectory; suggestionProvider: function() { return bridge.exportSuggestion("pptx") }; defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.exportPowerPoint(selectedFile.toString()) }
    SuggestedSaveDialog { id: presentationNoVoiceSave; objectName: "presentationNoVoiceSaveDialog"; title: "Tải PowerPoint không kèm giọng đọc"; currentFolder: bridge.downloadsDirectory; defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"]; suggestionProvider: function() { return bridge.presentationDownloadSuggestion(false) }; onAccepted: bridge.downloadPresentationWithVoice(selectedFile.toString(), false) }
    SuggestedSaveDialog { id: presentationSave; objectName: "presentationSaveDialog"; title: "Tải PowerPoint · " + (bridge.lessonNarration.title || "Không kèm giọng đọc"); currentFolder: bridge.downloadsDirectory; defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"]; suggestionProvider: function() { return bridge.presentationDownloadSuggestion(!!bridge.selectedNarrationVariant && root.includeDownloadVoice) }; onAccepted: bridge.downloadPresentationWithVoice(selectedFile.toString(), !!bridge.selectedNarrationVariant && root.includeDownloadVoice) }
    SuggestedSaveDialog { id: packSave; title: "Xuất gói bài BiliClass"; currentFolder: bridge.downloadsDirectory; suggestionProvider: function() { return bridge.exportSuggestion("biliclass") }; defaultSuffix: "biliclass"; nameFilters: ["BiliClass (*.biliclass)"]; onAccepted: bridge.exportPack(selectedFile.toString()) }
    FileDialog { id: knowledgeOpen; title: "Cài gói kiến thức có nguồn"; nameFilters: ["BiliClass Knowledge (*.biliknowledge)"]; onAccepted: bridge.installKnowledgePack(selectedFile.toString()) }
    FileDialog { id: backupOpen; title: "Chọn bản sao thư viện"; nameFilters: ["BiliClass Backup (*.bcbackup)"]; onAccepted: restoreDestination.open() }
    FolderDialog { id: restoreDestination; objectName: "restoreDestinationDialog"; title: "Chọn nơi lưu dữ liệu khôi phục · BiliClass sẽ mở lại khi xong"; onAccepted: bridge.restoreLibraryTo(backupOpen.selectedFile.toString(), selectedFolder.toString()) }
    FolderDialog { id: libraryOpen; title: "Chọn thư viện và mở lại BiliClass"; onAccepted: root.requestAction(function() { bridge.openLibrary(libraryOpen.selectedFolder.toString()) }) }
    Dialog {
        id: existingNarration; objectName: "existingNarrationDialog"; anchors.centerIn: parent; modal: true
        property var selection: ({})
        title: "Bản giọng này đã được tạo"
        width: Math.min(600, root.width - 50)
        ColumnLayout {
            width: parent.width; spacing: 14
            Copy { Layout.fillWidth: true; text: "Bài này đã có âm thanh hợp lệ với " + (existingNarration.selection.title || "giọng đã chọn") + " và cấu hình đang chọn. Bạn muốn dùng bản có sẵn hay tạo lại?" }
            Copy { Layout.fillWidth: true; text: "Tạo lại sẽ tổng hợp âm thanh mới cho cấu hình này. Bản cũ được giữ cho đến khi tạo xong."; font.pixelSize: 12 }
            Flow { Layout.fillWidth: true; spacing: 8
                MainAction { text: "Đóng"; onClicked: existingNarration.close() }
                MainAction { objectName: "regenerateExistingNarration"; text: "Tạo lại"; danger: true; onClicked: { const c = existingNarration.selection; existingNarration.close(); bridge.confirmExistingNarration(c.lesson_id, c.revision, c.mode, c.voice, c.rate, true) } }
                MainAction { objectName: "useExistingNarration"; text: "Dùng bản có sẵn"; primary: true; onClicked: { const c = existingNarration.selection; existingNarration.close(); bridge.confirmExistingNarration(c.lesson_id, c.revision, c.mode, c.voice, c.rate, false) } }
            }
        }
    }
    Dialog {
        id: wholeLessonReview; objectName: "wholeLessonReview"; anchors.centerIn: parent; modal: true
        title: "Chuẩn bị dạy"; width: Math.min(660, root.width - 80)
        ColumnLayout {
            width: parent.width; spacing: 13
            Caption { text: root.lessonData.title || "Bài giảng"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            Copy { text: (bridge.quickResult.total || 0) + " slide · Chọn bản giọng trước khi mở trình chiếu"; Layout.fillWidth: true }
            Choice {
                objectName: "teachingNarrationVariantChoice"; Layout.fillWidth: true; Layout.minimumWidth: 0
                model: bridge.narrationVariants; textRole: "title"; valueRole: "id"
                currentIndex: Math.max(0, bridge.narrationVariants.map(function(row) { return row.id }).indexOf(bridge.selectedNarrationVariant))
                enabled: !bridge.busy && !bridge.narrationBusy
                onActivated: { root.narrationOptionsPinned = false; bridge.selectNarrationVariant(currentValue) }
            }
            Copy { objectName: "teachingNarrationSummary"; Layout.fillWidth: true; color: bridge.selectedNarrationVariant && !bridge.lessonNarration.ready ? AppTheme.adapt("#a66318") : AppTheme.adapt("#168567"); text: !bridge.selectedNarrationVariant ? "Dạy bằng PowerPoint không kèm giọng đọc." : bridge.lessonNarration.ready ? bridge.lessonNarration.title + ". Giọng chỉ phát khi thầy cô bấm nút đọc." : "Bản giọng này chưa hoàn tất. Quay lại tạo tiếp hoặc chọn bản khác." }
            Copy { Layout.fillWidth: true; text: bridge.quickResult.draft ? "Xác nhận thầy cô đã kiểm tra nội dung, lời đọc, số liệu và bố cục. BiliClass sẽ mở PowerPoint và gắn bài với Mascot. Bấm Trình chiếu (F5) khi sẵn sàng." : "Bài đã được duyệt. Mở PowerPoint và gắn bài cùng bản giọng đã chọn với Mascot. Bấm Trình chiếu (F5) khi sẵn sàng." }
            ContentScrollView {
                visible: (bridge.quickResult.warnings || []).length > 0; Layout.fillWidth: true; Layout.preferredHeight: 150; contentWidth: availableWidth
                Copy { width: parent.width; text: (bridge.quickResult.warnings || []).join("\n\n"); color: AppTheme.adapt("#a66318") }
            }
            RowLayout {
                Layout.fillWidth: true; Item { Layout.fillWidth: true }
                MainAction { text: "Xem lại bài"; onClicked: wholeLessonReview.close() }
                MainAction { objectName: "confirmWholeLessonButton"; text: bridge.quickResult.draft ? "Đã kiểm tra · Mở bài để dạy" : "Mở bài giảng để dạy"; primary: true; enabled: !bridge.busy && !bridge.previewBusy && !bridge.narrationBusy && (!bridge.selectedNarrationVariant || bridge.lessonNarration.ready) && !root.lessonLayoutFailures; onClicked: { wholeLessonReview.close(); bridge.useConvertedLesson() } }
            }
        }
    }
    Dialog {
        id: lessonReviewHelp; objectName: "lessonReviewHelpDialog"; anchors.centerIn: parent; modal: true
        title: "Kiểm tra bài giảng"; width: Math.min(650, root.width - 70)
        ColumnLayout {
            width: parent.width; spacing: 12
            Caption { text: root.lessonData.title || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
            Copy { objectName: "lessonReviewExplanation"; text: bridge.lessonReview.detail || ""; Layout.fillWidth: true }
            ProgressBar { visible: bridge.busy; indeterminate: true; Layout.fillWidth: true }
            Flow { Layout.fillWidth: true; spacing: 8
                MainAction { objectName: "reviewBuildPreview"; text: "Xem bản trình chiếu"; visible: !bridge.lessonReview.canInspect && !bridge.quickResult.path && bridge.lessonReview.canConfirm; enabled: !bridge.busy; onClicked: { lessonReviewHelp.close(); bridge.convertCurrentLesson() } }
                MainAction { objectName: "reviewEditText"; text: "Xem/sửa nội dung"; enabled: !bridge.busy; onClicked: { lessonReviewHelp.close(); root.go("editor") } }
            }
            RowLayout { Layout.fillWidth: true
                MainAction { text: "Đóng"; onClicked: lessonReviewHelp.close() }
                Item { Layout.fillWidth: true }
                MainAction { objectName: "reviewConfirmLesson"; text: bridge.lessonReview.kind === "ready" ? "Tiếp tục dạy" : "Xem và xác nhận để dạy"; primary: true; enabled: bridge.lessonReview.canConfirm && !!bridge.quickResult.path && !bridge.busy && !bridge.previewBusy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.teachingTransitioning; onClicked: { lessonReviewHelp.close(); wholeLessonReview.open() } }
            }
        }
    }
    Dialog {
        id: comparisonDialog; objectName: "comparisonDialog"; anchors.centerIn: parent; modal: true
        title: "Đối chiếu bố cục bằng PowerPoint"; width: Math.min(1280, root.width - 50); height: Math.min(800, root.height - 65)
        ColumnLayout {
            anchors.fill: parent; spacing: 12
            RowLayout {
                Layout.fillWidth: true
                Copy { text: "Bản nguồn · slide " + (bridge.comparison.source_slide || 1); Layout.fillWidth: true }
                Copy { text: "Bản xuất · slide " + (bridge.comparison.output_slide || 1) + "/" + (bridge.comparison.total || 1); Layout.fillWidth: true }
            }
            RowLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: 12
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: AppTheme.adapt("#e9eef5"); border.color: root.line
                    Image { anchors.fill: parent; anchors.margins: 3; source: bridge.comparison.source_image || ""; fillMode: Image.PreserveAspectFit }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: AppTheme.adapt("#e9eef5"); border.color: root.line
                    Image { anchors.fill: parent; anchors.margins: 3; source: bridge.comparison.result_image || ""; fillMode: Image.PreserveAspectFit }
                }
            }
            ContentScrollView {
                id: comparisonReport; Layout.fillWidth: true; Layout.preferredHeight: Math.min(110, comparisonWarnings.implicitHeight + 4); contentWidth: availableWidth
                Copy { id: comparisonWarnings; width: comparisonReport.availableWidth; text: (bridge.conversionReport || []).filter(function(item) { return !item.slide || item.slide === bridge.comparison.source_slide }).map(function(item) { return (item.warnings || []).join("\n") || item.message || (item.action === "added" ? "Đã thêm vùng hỗ trợ vào khoảng trống." : item.action === "support_pages" ? "Slide kín: phần hỗ trợ nằm ở trang kế tiếp." : "Giữ nội dung gốc hoặc ưu tiên ngôn ngữ đã chọn.") }).join("\n"); font.pixelSize: 11 }
            }
            Copy { text: "Ảnh đối chiếu xác nhận bố cục tĩnh. Mở PowerPoint để kiểm tra hiệu ứng, video và âm thanh."; Layout.fillWidth: true; font.pixelSize: 11 }
            RowLayout {
                MainAction { text: "Slide trước"; enabled: !bridge.busy && (bridge.comparison.output_slide || 1) > 1; onClicked: bridge.comparePowerPoint(bridge.comparison.output_slide - 1) }
                MainAction { text: "Slide tiếp"; enabled: !bridge.busy && bridge.comparison.output_slide < bridge.comparison.total; onClicked: bridge.comparePowerPoint(bridge.comparison.output_slide + 1) }
                Item { Layout.fillWidth: true }
                MainAction { text: "Mở trong PowerPoint"; enabled: !bridge.busy; onClicked: bridge.previewSourcePowerPoint() }
                MainAction { text: "Xuất PPTX"; primary: true; enabled: !bridge.busy; onClicked: deckSave.openSuggested() }
                MainAction { text: "Đóng"; onClicked: comparisonDialog.close() }
            }
        }
    }
    Dialog { id: metadataDialog; objectName: "lessonMetadataDialog"; anchors.centerIn: parent; modal: true; title: "Sửa bài giảng"; width: 500
        property var lessonData: ({})
        onOpened: { if (!lessonData.id) lessonData = root.lessonData; metaTitle.text = lessonData.title; metaSubject.text = lessonData.subject; metaEducation.text = lessonData.education_level; metaGrade.text = lessonData.grade }
        onClosed: lessonData = ({})
        contentItem: ColumnLayout { spacing: 12
            Field { id: metaTitle; objectName: "metadataLessonTitle"; placeholderText: "Tên bài"; Layout.fillWidth: true; maximumLength: 200 }
            Field { id: metaSubject; placeholderText: "Môn học"; Layout.fillWidth: true; maximumLength: 200 }
            RowLayout { Field { id: metaEducation; placeholderText: "Cấp học"; Layout.fillWidth: true; maximumLength: 200 } Field { id: metaGrade; placeholderText: "Khối"; Layout.fillWidth: true; maximumLength: 200 } }
            Copy { text: "Đổi môn sẽ đưa văn bản về trạng thái cần duyệt lại."; Layout.fillWidth: true }
            RowLayout {
                MainAction { text: "Sửa nội dung bài giảng"; enabled: !bridge.busy; onClicked: { const lessonId = metadataDialog.lessonData.id; metadataDialog.close(); bridge.editLesson(lessonId) } }
                Item { Layout.fillWidth: true }
                MainAction { text: "Hủy"; onClicked: metadataDialog.close() }
                MainAction { objectName: "saveLessonMetadataButton"; text: "Lưu"; primary: true; onClicked: if (bridge.editLessonMetadata(metadataDialog.lessonData.id, metaTitle.text, metaSubject.text, metaEducation.text, metaGrade.text)) metadataDialog.close() }
            }
        }
    }
    Dialog { id: cancelConversionDialog; objectName: "cancelConversionDialog"; anchors.centerIn: parent; modal: true; title: "Hủy và xóa bài đang tạo?"; width: Math.min(root.width - 48, 520)
        property string conversionId: ""
        contentItem: ColumnLayout { spacing: 16
            Copy { text: "Chuyển đổi sẽ dừng và bài giảng đang tạo sẽ bị xóa. File PowerPoint gốc và các bài giảng khác được giữ nguyên."; Layout.fillWidth: true }
            RowLayout { Item { Layout.fillWidth: true }
                MainAction { objectName: "keepConvertingButton"; text: "Tiếp tục chuyển đổi"; primary: true; onClicked: cancelConversionDialog.close() }
                MainAction { objectName: "confirmCancelConversionButton"; text: "Hủy và xóa bài"; danger: true; symbol: "×"; enabled: !!bridge.browserState.running && !bridge.browserState.stopping && bridge.browserState.conversionId === cancelConversionDialog.conversionId; onClicked: { bridge.discardConversion(cancelConversionDialog.conversionId); cancelConversionDialog.close() } }
            }
        }
    }
    Dialog { id: deleteLessonDialog; objectName: "deleteLessonDialog"; anchors.centerIn: parent; modal: true; title: "Xóa bài giảng?"; width: 470
        property string lessonId: ""
        property string lessonTitle: ""
        contentItem: ColumnLayout { spacing: 16
            Caption { text: deleteLessonDialog.lessonTitle; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            Copy { text: "Bài sẽ được đưa vào thùng rác. Có thể khôi phục; bản PowerPoint, âm thanh và báo cáo lớp được giữ lại."; Layout.fillWidth: true }
            RowLayout { Item { Layout.fillWidth: true } MainAction { objectName: "cancelDeleteLessonButton"; text: "Hủy"; onClicked: deleteLessonDialog.close() } MainAction { objectName: "confirmDeleteLessonButton"; text: "Xóa bài"; danger: true; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: if (bridge.trashLesson(deleteLessonDialog.lessonId)) deleteLessonDialog.close() } }
        }
    }
    Dialog { id: bulkDeleteDialog; objectName: "bulkDeleteLessonsDialog"; anchors.centerIn: parent; modal: true; title: "Xóa " + identities.length + " bài đã chọn?"; width: Math.min(root.width - 48, 500)
        property var identities: []
        contentItem: ColumnLayout { spacing: 16
            Copy { text: "Các bài đã chọn sẽ vào thùng rác. Có thể khôi phục trong Chia sẻ & quản lý. PowerPoint, âm thanh và báo cáo lớp được giữ lại."; Layout.fillWidth: true }
            RowLayout { Item { Layout.fillWidth: true } MainAction { objectName: "cancelBulkDeleteLessons"; text: "Hủy"; onClicked: bulkDeleteDialog.close() } MainAction { objectName: "confirmBulkDeleteLessons"; text: "Xóa đã chọn"; danger: true; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: if (bridge.trashLessons(bulkDeleteDialog.identities)) bulkDeleteDialog.close() } }
        }
    }
    Dialog { id: libraryDownloadDialog; objectName: "libraryDownloadDialog"; anchors.centerIn: parent; modal: true; title: "Tải " + identities.length + " bài giảng"; width: Math.min(root.width - 48, 530)
        property var identities: []
        contentItem: ColumnLayout { spacing: 16
            Copy { text: libraryDownloadDialog.identities.length > 1 ? "Các PowerPoint được gói trong một file ZIP. Mỗi bài có tên riêng và thông tin giọng đọc." : "Tải file PowerPoint của bài đã chọn."; Layout.fillWidth: true }
            CheckBox { id: libraryDownloadVoice; objectName: "libraryDownloadVoice"; text: "Kèm bản giọng đã chọn, nếu đã tạo đủ"; checked: true }
            Copy { text: "Bài chưa tạo đủ giọng sẽ tải không kèm âm thanh. Muốn đổi người đọc hoặc loại giọng, mở bài rồi chọn bản cần dùng trước khi tải."; Layout.fillWidth: true; font.pixelSize: 12 }
            RowLayout { Item { Layout.fillWidth: true } MainAction { text: "Hủy"; onClicked: libraryDownloadDialog.close() } MainAction { objectName: "confirmLibraryDownload"; text: "Chọn nơi lưu"; primary: true; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: { libraryDownloadDialog.close(); libraryDownloadSave.openSuggested() } } }
        }
    }
    SuggestedSaveDialog { id: libraryDownloadSave; objectName: "libraryDownloadSave"; title: "Lưu bài giảng"; currentFolder: bridge.downloadsDirectory; defaultSuffix: libraryDownloadDialog.identities.length > 1 ? "zip" : "pptx"; nameFilters: libraryDownloadDialog.identities.length > 1 ? ["Bộ bài giảng (*.zip)"] : ["PowerPoint (*.pptx)"]; suggestionProvider: function() { return bridge.libraryDownloadSuggestion(libraryDownloadDialog.identities, libraryDownloadVoice.checked) }; onAccepted: bridge.downloadLibraryPresentations(libraryDownloadDialog.identities, selectedFile.toString(), libraryDownloadVoice.checked) }
    Dialog { id: lessonTrashDialog; objectName: "lessonTrashDialog"; anchors.centerIn: parent; modal: true; title: "Thùng rác bài giảng"; width: Math.min(root.width - 64, 880); height: Math.min(root.height - 64, 560)
        property var selected: []
        readonly property var identities: bridge.trashedLessons.map(function(row) { return row.id })
        readonly property bool canChange: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.teachingTransitioning && !root.classroom.running
        onOpened: selected = []
        onIdentitiesChanged: {
            const kept = selected.filter(function(id) { return identities.indexOf(id) >= 0 })
            if (kept.length !== selected.length) selected = kept
        }
        function choose(identity, checked) {
            const list = selected.filter(function(id) { return id !== identity })
            if (checked) list.push(identity)
            selected = list
        }
        function confirmPurge(ids) {
            purgeTrashDialog.identities = ids.slice()
            purgeTrashDialog.open()
        }
        contentItem: ColumnLayout { spacing: 12
            Copy { text: "Khôi phục để đưa bài về thư viện. Xóa vĩnh viễn sẽ bỏ bài và lịch sử chỉnh sửa khỏi thùng rác."; Layout.fillWidth: true }
            Flow { Layout.fillWidth: true; spacing: 6
                LibraryCheck { objectName: "trashSelectAll"; text: "Chọn tất cả (" + lessonTrashDialog.identities.length + ")"; checkState: !lessonTrashDialog.selected.length ? Qt.Unchecked : lessonTrashDialog.selected.length === lessonTrashDialog.identities.length ? Qt.Checked : Qt.PartiallyChecked; nextCheckState: function() { return checkState === Qt.Checked ? Qt.Unchecked : Qt.Checked }; enabled: lessonTrashDialog.identities.length > 0; onClicked: lessonTrashDialog.selected = checked ? lessonTrashDialog.identities.slice() : [] }
                LibraryAction { objectName: "trashDeselectAll"; text: "Bỏ chọn"; subtle: true; enabled: lessonTrashDialog.selected.length > 0; onClicked: lessonTrashDialog.selected = [] }
                LibraryAction { objectName: "trashRestoreSelected"; text: "Khôi phục đã chọn"; enabled: lessonTrashDialog.canChange && lessonTrashDialog.selected.length > 0; onClicked: bridge.restoreLessons(lessonTrashDialog.selected) }
                LibraryAction { objectName: "trashPurgeSelected"; text: "Xóa đã chọn"; danger: true; enabled: lessonTrashDialog.canChange && lessonTrashDialog.selected.length > 0; onClicked: lessonTrashDialog.confirmPurge(lessonTrashDialog.selected) }
                LibraryAction { objectName: "trashRestoreAll"; text: "Khôi phục tất cả"; enabled: lessonTrashDialog.canChange && lessonTrashDialog.identities.length > 0; onClicked: bridge.restoreLessons(lessonTrashDialog.identities) }
                LibraryAction { objectName: "trashPurgeAll"; text: "Xóa tất cả"; danger: true; enabled: lessonTrashDialog.canChange && lessonTrashDialog.identities.length > 0; onClicked: lessonTrashDialog.confirmPurge(lessonTrashDialog.identities) }
            }
            Copy { text: lessonTrashDialog.selected.length + " / " + lessonTrashDialog.identities.length + " bài đã chọn"; font.pixelSize: 11; Layout.fillWidth: true }
            Copy { visible: bridge.trashedLessons.length === 0; text: "Thùng rác đang trống." }
            ContentScrollView { Layout.fillWidth: true; Layout.fillHeight: true; contentWidth: availableWidth
                ColumnLayout { width: parent.width; spacing: 10
                    Repeater { model: bridge.trashedLessons
                        RowLayout { required property var modelData; Layout.fillWidth: true
                            LibraryCheck { objectName: "trashSelect_" + modelData.id; Layout.preferredWidth: 28; checked: lessonTrashDialog.selected.indexOf(modelData.id) >= 0; Accessible.name: "Chọn " + modelData.title; onClicked: lessonTrashDialog.choose(modelData.id, checked) }
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Caption { text: modelData.title; Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight }
                                Copy { text: "Xóa: " + bridge.lessonDateLabel(modelData.deleted_at); font.pixelSize: 11 }
                            }
                            LibraryAction { objectName: "restoreLesson_" + modelData.id; text: "Khôi phục"; enabled: lessonTrashDialog.canChange; onClicked: bridge.restoreLesson(modelData.id) }
                            LibraryAction { objectName: "purgeLesson_" + modelData.id; text: "Xóa vĩnh viễn"; danger: true; enabled: lessonTrashDialog.canChange; onClicked: lessonTrashDialog.confirmPurge([modelData.id]) }
                        }
                    }
                }
            }
            RowLayout { Layout.fillWidth: true; Item { Layout.fillWidth: true } LibraryAction { objectName: "closeLessonTrash"; text: "Đóng"; onClicked: lessonTrashDialog.close() } }
        }
    }
    Dialog { id: purgeTrashDialog; objectName: "purgeTrashDialog"; anchors.centerIn: parent; modal: true; title: "Xóa vĩnh viễn " + identities.length + " bài giảng?"; width: Math.min(root.width - 64, 540)
        property var identities: []
        contentItem: ColumnLayout { spacing: 16
            Copy { text: "Sẽ xóa " + purgeTrashDialog.identities.length + " bài cùng lịch sử chỉnh sửa. Không thể khôi phục các bài này từ thùng rác. Báo cáo lớp học, bản sao lưu và tệp dùng chung được giữ lại."; Layout.fillWidth: true }
            RowLayout { Layout.fillWidth: true; Item { Layout.fillWidth: true } MainAction { objectName: "cancelPurgeTrash"; text: "Hủy"; onClicked: purgeTrashDialog.close() } MainAction { objectName: "confirmPurgeTrash"; text: "Xóa vĩnh viễn"; danger: true; enabled: lessonTrashDialog.canChange; onClicked: if (bridge.purgeLessons(purgeTrashDialog.identities)) purgeTrashDialog.close() } }
        }
    }
    Dialog {
        id: unsaved; objectName: "unsavedDialog"; anchors.centerIn: parent; modal: true; title: "Lưu thay đổi trước khi tiếp tục?"; width: 465
        contentItem: ColumnLayout { spacing: 19; Copy { text: "Đoạn đang chỉnh sửa chưa được lưu. Lưu nháp sẽ chuyển đoạn về trạng thái chờ duyệt."; Layout.fillWidth: true }
            RowLayout { MainAction { objectName: "stayButton"; text: "Ở lại"; onClicked: unsaved.close() } MainAction { text: "Bỏ thay đổi"; onClicked: { unsaved.close(); root.loadFields(); if (root.pendingAction) root.pendingAction() } } MainAction { text: "Lưu nháp"; primary: true; onClicked: { if (root.save(false)) { unsaved.close(); if (root.pendingAction) root.pendingAction() } } } }
    }
    }
    Dialog {
        id: memoryDialog; objectName: "memoryChoiceDialog"; anchors.centerIn: parent; modal: true
        title: "Chọn bản dịch từng duyệt"; width: Math.min(root.width - 50, 680); height: Math.min(root.height - 60, 510)
        onClosed: bridge.dismissMemoryChoices()
        contentItem: ColumnLayout { spacing: 14
            Copy { text: "Chỉ dùng nội dung từng duyệt trong cùng môn. Gợi ý gần giống có thể khác số liệu hoặc ý nghĩa. Chọn làm nháp rồi kiểm tra và duyệt lại."; Layout.fillWidth: true }
            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: bridge.memoryChoices
                delegate: ItemDelegate { required property int index; required property var modelData; objectName: "memoryChoice" + index
                    width: ListView.view.width; height: 92
                    background: Rectangle { radius: 10; color: parent.hovered ? AppTheme.adapt("#eaf3ff") : AppTheme.adapt("#f8fafd"); border.color: parent.hovered ? root.blue : root.line }
                    contentItem: ColumnLayout { spacing: 6
                        Caption { text: modelData.text; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight }
                        Copy { text: modelData.similarity ? "Gần giống " + modelData.similarity + "% · Nguồn: " + modelData.source : modelData.count + " lần duyệt · " + modelData.lessons.join(", "); Layout.fillWidth: true; font.pixelSize: 11; elide: Text.ElideRight }
                    }
                    onClicked: bridge.useMemoryChoice(index)
                }
            }
            RowLayout { Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                MainAction { text: "Đóng"; onClicked: bridge.closeMemoryChoices() }
            }
        }
    }
    Dialog { id: reviewWarning; property string details: ""; anchors.centerIn: parent; modal: true; title: "Kiểm tra số và ký hiệu"; width: 540; standardButtons: Dialog.Ok | Dialog.Cancel
        Copy { width: parent.width; text: reviewWarning.details + "\n\nChỉ nhấn OK nếu thầy cô đã kiểm tra và muốn duyệt cặp này." }
        onAccepted: bridge.saveSegment(viEdit.text, enEdit.text, true, lockedCheck.checked)
    }
    Dialog { id: busyDialog; anchors.centerIn: parent; modal: true; title: "Đang xử lý bài học"; standardButtons: Dialog.Ok; Copy { text: "Hãy chờ tác vụ hiện tại hoàn tất trước khi đóng ứng dụng." } }
    Dialog { id: updateBusyDialog; anchors.centerIn: parent; modal: true; title: "Đang tải bản cập nhật"; standardButtons: Dialog.Ok; Copy { text: "Chờ tải xong hoặc bấm Hủy tải trước khi đóng ứng dụng." } }
    Dialog {
        id: updateDialog; objectName: "updateDialog"; anchors.centerIn: parent; modal: true
        title: "Cập nhật BiliClass"; width: Math.min(540, root.width - 80)
        contentItem: ColumnLayout { spacing: 16
            Caption { text: "Bản cài BiliClass " + bridge.updateState.version; Layout.fillWidth: true }
            Copy { text: bridge.developmentMode ? "Cài bản Windows đầy đủ để sử dụng và cập nhật thuận tiện. Thư viện bài giảng được giữ lại; thư mục mã nguồn vẫn giữ nguyên." : "Bản mới được tải, kiểm tra và cài tự động. Thư viện bài giảng được giữ lại."; Layout.fillWidth: true }
            Copy { text: bridge.updateState.message; Layout.fillWidth: true }
            ProgressBar { visible: bridge.updateState.downloading; Layout.fillWidth: true; value: bridge.updateState.progress / 100 }
            RowLayout { Layout.fillWidth: true; Item { Layout.fillWidth: true }
                MainAction { text: "Đóng"; onClicked: updateDialog.close() }
                MainAction { visible: bridge.updateState.downloading; text: "Hủy tải"; onClicked: bridge.cancelUpdate() }
                MainAction { objectName: "installUpdateButton"; text: bridge.updateState.ready ? "Mở bản mới" : "Cập nhật"; primary: true; enabled: !bridge.updateState.downloading && !bridge.busy && !root.classroom.running; onClicked: bridge.updateState.ready ? bridge.applyDownloadedUpdate() : bridge.downloadUpdate() }
            }
        }
    }
    Dialog { id: deleteTermDialog; property string termId: ""; anchors.centerIn: parent; modal: true; title: "Xóa thuật ngữ này?"; standardButtons: Dialog.Ok | Dialog.Cancel; onAccepted: bridge.deleteTerm(termId) }
    Dialog {
        id: readinessDialog; objectName: "readinessDialog"; anchors.centerIn: parent; modal: true; title: "Chuẩn bị bài giảng"; width: 730; height: Math.min(root.height - 50, 670)
        contentItem: ColumnLayout { spacing: 13
            Copy { text: bridge.readiness.text_ready ? "Văn bản đã duyệt và nguồn còn nguyên vẹn." : "Còn nội dung cần kiểm tra trước khi dạy."; color: bridge.readiness.text_ready ? AppTheme.adapt("#168567") : AppTheme.adapt("#ad651d"); Layout.fillWidth: true }
            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: bridge.readiness.checks
                delegate: Rectangle { required property var modelData; width: ListView.view.width; height: 64; radius: 10; color: modelData.ok ? AppTheme.adapt("#eef9f3") : AppTheme.adapt("#fff7eb")
                    RowLayout { anchors.fill: parent; anchors.margins: 12; spacing: 14
                        Label { text: modelData.ok ? "✓" : "○"; color: modelData.ok ? AppTheme.adapt("#168567") : AppTheme.adapt("#ad651d"); font.pixelSize: 22 }
                        ColumnLayout { spacing: 4; Layout.fillWidth: true; Caption { text: modelData.label } Copy { text: modelData.detail; font.pixelSize: 11; Layout.fillWidth: true } }
                    }
                }
            }
            Copy { text: bridge.busy ? bridge.message : "Có thể dạy bằng văn bản khi chưa có âm thanh. Quiz và mạng lớp học không bắt buộc cho bài song ngữ."; Layout.fillWidth: true; font.pixelSize: 11 }
            RowLayout { Layout.fillWidth: true
                MainAction { objectName: "prepareEnglishAudio"; text: "Chuẩn bị audio EN"; enabled: !bridge.busy && !!bridge.voiceSettings.en; onClicked: bridge.prepareAudio("en") }
                MainAction { text: "Chuẩn bị audio VI"; enabled: !bridge.busy && !!bridge.voiceSettings.vi; onClicked: bridge.prepareAudio("vi") }
                Item { Layout.fillWidth: true }
                MainAction { visible: bridge.busy; text: "Dừng tác vụ"; onClicked: bridge.cancelJob() }
                MainAction { text: "Làm mới"; enabled: !bridge.busy; onClicked: bridge.refreshReadiness() }
            }
            RowLayout { Layout.fillWidth: true; MainAction { text: "Đóng"; onClicked: readinessDialog.close() } Item { Layout.fillWidth: true } MainAction { text: "Xem trước bài"; enabled: !bridge.busy; onClicked: { readinessDialog.close(); root.rescue = false; preview.show() } } MainAction { objectName: "commitPreparationButton"; text: "Chốt bản chuẩn bị"; primary: true; enabled: !bridge.busy && bridge.readiness.text_ready && !bridge.readiness.prepared_ready; onClicked: bridge.prepareLesson() } }
        }
    }
    Dialog {
        id: sourceDialog; anchors.centerIn: parent; modal: true; title: "Văn bản trích xuất ban đầu"; width: 680; height: 420; standardButtons: Dialog.Close
        ContentScrollView { anchors.fill: parent;  TextArea { text: bridge.segment.source_text || ""; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; color: root.ink; font.pixelSize: 15 } }
    }
    Dialog {
        id: splitDialog; anchors.centerIn: parent; modal: true; width: 500; title: "Tách đoạn theo con trỏ"; standardButtons: Dialog.Ok | Dialog.Cancel
        Copy { width: parent.width; text: "Đặt con trỏ tại điểm muốn tách trong mỗi ô Việt/Anh có nội dung trước khi dùng nút này. Hai phần sẽ thành hai đoạn cần duyệt lại. Có thể khôi phục bằng Lịch sử." }
        onAccepted: { let viPosition = viEdit.cursorPosition; let enPosition = enEdit.cursorPosition; if (!root.dirty || root.save(false)) bridge.splitSegment(viPosition, enPosition) }
    }
    Dialog {
        id: historyDialog; objectName: "historyDialog"; anchors.centerIn: parent; modal: true; title: "Lịch sử lưu gần đây"; width: 660; height: 480; standardButtons: Dialog.Close
        ColumnLayout { anchors.fill: parent; spacing: 13
            Copy { text: "Giữ 30 phiên bản trước. Khôi phục tạo một phiên bản mới và yêu cầu duyệt lại, bản hiện tại vẫn có trong lịch sử."; Layout.fillWidth: true }
            Copy { visible: bridge.history.length === 0; text: "Chưa có phiên bản trước." }
            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: bridge.history
                delegate: ItemDelegate { required property var modelData; width: ListView.view.width; height: 58
                    contentItem: RowLayout { Copy { text: "Phiên bản " + modelData.revision + " · " + new Date(modelData.saved_at).toLocaleString(); Layout.fillWidth: true } MainAction { text: "Khôi phục"; onClicked: { bridge.restoreRevision(modelData.revision); historyDialog.close() } } }
                }
            }
        }
    }

    HelpDialog { id: helpDialog; objectName: "helpDialog" }
    CompanionWindow {
        id: companion; objectName: "companionWindow"; bridge: root.bridgeRef
        onRequestSettings: { root.showNormal(); root.raise(); root.requestActivate(); root.requestAction(function() { root.page = "settings"; settingsPanel.activeTab = 3; companion.collapsed = true }) }
    }
    TeachingDialog { id: teachingDialog; objectName: "teachingDialog"; teaching: root.teaching; bridge: root.bridgeRef; onClosed: bridge.refreshReadiness() }
    ProjectorWindow { id: projector; objectName: "projectorWindow"; bridge: root.bridgeRef }
    property var bridgeRef: bridge
    TemplateGallery {
        id: templateGallery; objectName: "templateGallery"
        bridge: root.bridgeRef
        conversionFormat: forCreation ? root.selectedConversionFormat.id
            : ({split_view:"parallel_columns", line_pair:"sentence_pairs", keyword_overlay:"integrated_keywords", english_rescue:"english_only"})[layout] || "sentence_pairs"
        onApplyPreset: function(preset) {
            if (forCreation) creationPreset.currentIndex = ["standard", "visual", "practice"].indexOf(preset)
            else bridge.setTeachingPreset(preset)
        }
    }
    Dialog {
        id: conversionExample; objectName: "conversionExampleDialog"
        property int formatIndex: 0
        modal: true; anchors.centerIn: parent
        width: Math.min(1050, root.width - 64); height: Math.min(700, root.height - 52)
        title: root.conversionFormats[formatIndex].label + " · Mẫu bố cục"
        standardButtons: Dialog.Close
        contentItem: ColumnLayout {
            spacing: 12
            Copy { text: root.conversionFormats[conversionExample.formatIndex].detail; Layout.fillWidth: true; font.pixelSize: 14 }
            ConversionLayoutPreview {
                objectName: "conversionExampleSlide"
                bridge: root.bridgeRef
                conversionFormat: root.conversionFormats[conversionExample.formatIndex].id
                preset: ["standard", "visual", "practice"][creationPreset.currentIndex]
                Layout.fillWidth: true; Layout.fillHeight: true
            }
            Copy { text: "Ví dụ minh họa vị trí ngôn ngữ. Nội dung, hình và thiết kế đầu ra dùng theo tài liệu và lựa chọn của thầy cô."; Layout.fillWidth: true; font.pixelSize: 12 }
            MainAction { objectName: "selectConversionExample"; text: "Chọn kiểu này"; primary: true; Layout.alignment: Qt.AlignRight; onClicked: { creationFormat.currentIndex = conversionExample.formatIndex; conversionExample.close() } }
        }
    }

    Window {
        id: preview; objectName: "lessonPreview"; modality: Qt.NonModal; title: "BiliClass · Bàn điều khiển giảng dạy"; width: 1080; height: 730; minimumWidth: 800; minimumHeight: 600; color: AppTheme.adapt("#f3f7fc")
        property bool showTools: false
        onClosing: { bridge.stopSpeech(); if (bridge.busy) bridge.cancelJob() }
        Shortcut { sequence: "Escape"; onActivated: preview.close() }
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 12
            RowLayout { Layout.fillWidth: true
                Image { source: "book.svg"; sourceSize.width: 32; sourceSize.height: 32 }
                Caption { text: "BiliClass"; font.pixelSize: 21 }
                Item { Layout.fillWidth: true }
                Pill { visible: !!root.lessonData.conversion_format || bridge.experimentalTeaching; text: root.lessonData.conversion_format ? bridge.conversionLabel : "L" + bridge.policy.level + " · " + bridge.policy.name }
                MainAction { visible: bridge.experimentalTeaching; text: preview.showTools ? "Thu trợ giảng" : "Trợ giảng"; onClicked: preview.showTools = !preview.showTools }
                MainAction { text: preview.visibility === Window.FullScreen ? "Thu nhỏ" : "Toàn màn hình"; onClicked: preview.visibility === Window.FullScreen ? preview.showNormal() : preview.showFullScreen() }
                MainAction { text: "Đóng  ×"; onClicked: preview.close() }
            }
            Copy { text: bridge.segment.approved ? "Xem trước văn bản đã duyệt · " + (root.lessonData.title || "") : "BẢN NHÁP CHƯA DUYỆT · Chỉ dùng để kiểm tra nội dung"; color: bridge.segment.approved ? root.muted : AppTheme.adapt("#ad651d"); Layout.fillWidth: true }
            RowLayout { visible: bridge.settings.show_profile; Layout.fillWidth: true; spacing: 10
                SchoolLogo { objectName: "previewSchoolLogo"; visible: !!bridge.schoolLogoUrl; source: bridge.schoolLogoUrl; roundMask: bridge.schoolLogoRound; Layout.preferredWidth: 50; Layout.preferredHeight: 50 }
                Copy { text: root.profileLabel; Layout.fillWidth: true }
            }
            TemplateSlide { objectName: "lessonTemplatePreview"; Layout.fillWidth: true; Layout.fillHeight: true; plan: root.templatePages[root.templatePageIndex] || ({}) }
            RowLayout { visible: root.templatePages.length > 1; Layout.fillWidth: true
                MainAction { text: "Trang mẫu trước"; enabled: root.templatePageIndex > 0; onClicked: root.templatePageIndex-- }
                Copy { text: (root.templatePageIndex + 1) + " / " + root.templatePages.length }
                MainAction { text: "Trang mẫu tiếp"; enabled: root.templatePageIndex < root.templatePages.length - 1; onClicked: root.templatePageIndex++ }
            }
            Copy { visible: bridge.experimentalTeaching && root.presentationContent.needs_easy_en; text: "Chưa có lời giải thích Anh đơn giản đã duyệt; đang xem lời đọc chính."; font.pixelSize: 11; Layout.fillWidth: true }
            AssistantPanel { visible: bridge.experimentalTeaching && preview.showTools; teaching: root.teaching; bridge: root.bridgeRef; Layout.fillWidth: true; Layout.preferredHeight: bridge.mascotSettings.visible ? Math.max(130, bridge.mascotSettings.size + 40) : 130 }
            RowLayout { visible: bridge.experimentalTeaching && preview.showTools; Layout.fillWidth: true
                Choice { id: projectorScreen; model: bridge.screens; textRole: "name"; currentIndex: bridge.screens.length > 1 ? 1 : 0; Layout.fillWidth: true }
                MainAction { text: "Mở màn hình lớp"; onClicked: { projector.quiz = false; bridge.showProjector(projector, projectorScreen.currentIndex) } }
                MainAction { text: "Trợ giảng nổi"; onClicked: bridge.showCompanion(companion) }
                MainAction { text: "VI Rescue trên màn hình lớp"; onClicked: projector.rescue = !projector.rescue }
            }
            RowLayout { visible: bridge.experimentalTeaching && preview.showTools; Layout.fillWidth: true; Item { Layout.fillWidth: true } MainAction { text: bridge.segment.approved ? "Đọc English" : "Nghe nháp EN"; enabled: !bridge.busy && !!bridge.audioAvailable.en && !!bridge.segment.en; onClicked: bridge.speakSegment("en") } MainAction { text: bridge.segment.approved ? "Đọc tiếng Việt" : "Nghe nháp VI"; enabled: !bridge.busy && !!bridge.audioAvailable.vi && !!bridge.segment.vi; onClicked: bridge.speakSegment("vi") } MainAction { text: "Dừng đọc"; onClicked: { bridge.stopSpeech(); if (bridge.busy) bridge.cancelJob() } } Item { Layout.fillWidth: true } }
            RowLayout { Layout.fillWidth: true; MainAction { text: "←  Trước"; enabled: !bridge.busy && bridge.segmentIndex > 0; onClicked: { bridge.stopSpeech(); bridge.selectSegment(bridge.segmentIndex - 1); root.rescue = false } } Item { Layout.fillWidth: true } Copy { text: (bridge.segmentIndex + 1) + " / " + (root.lessonData.segments || []).length } Item { Layout.fillWidth: true } MainAction { text: root.rescue ? "Ẩn tiếng Việt" : "VI Rescue"; onClicked: root.rescue = !root.rescue } MainAction { text: "Tiếp  →"; primary: true; enabled: !bridge.busy && bridge.segmentIndex < (root.lessonData.segments || []).length - 1; onClicked: { bridge.stopSpeech(); bridge.selectSegment(bridge.segmentIndex + 1); root.rescue = false } } }
        }
    }
}
