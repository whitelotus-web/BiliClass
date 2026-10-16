import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Window

ApplicationWindow {
    id: root
    visible: true
    width: 1366; height: 850
    minimumWidth: 1080; minimumHeight: 700
    title: "BiliClass · " + bridge.appVersion + " · " + bridge.appSubtitle + (bridge.developmentMode ? " · Bản nguồn" : "")
    color: "#f3f7fc"
    property string page: "home"
    onPageChanged: {
        if (page === "glossary" || page === "knowledge") {
            referenceTab = page === "knowledge" ? 1 : 0
            page = "reference"
        }
    }
    property color ink: "#112650"
    property color muted: "#667997"
    property color blue: "#0869f9"
    property color line: "#e0e8f3"
    property bool dirty: false
    property bool loadingFields: false
    property var pendingAction: null
    property string selectedFile: ""
    property string selectedFileName: ""
    property string inputDocumentError: ""
    property bool pasteMode: false
    property bool creationPromptVisible: false
    property bool includeDownloadVoice: true
    property bool resultDetails: false
    property string narrationMode: "en"
    property string narrationVoice: bridge.voiceSettings.voice || ""
    property int narrationRate: bridge.voiceSettings.rate || 0
    readonly property var narrationDrafts: bridge.narrationCreationChoices(bridge.narrationVariants, root.narrationVoice, root.narrationRate)
    readonly property var narrationDraft: narrationDrafts[root.narrationMode] || ({})
    function chooseNarrationMode(mode) {
        narrationMode = mode
        const choice = narrationDrafts[mode] || {}
        if (choice.ready && choice.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(choice.id)
    }
    function prepareTeaching(identity) {
        if (bridge.busy || bridge.narrationBusy || bridge.powerpointState.active || bridge.powerpointState.starting) return
        bridge.stopSpeech()
        if (identity !== undefined && identity !== bridge.selectedNarrationVariant) {
            bridge.selectNarrationVariant(identity)
            if (bridge.selectedNarrationVariant !== identity) return
        }
        wholeLessonReview.open()
    }
    property int libraryPage: 1
    property bool librarySelecting: false
    property var selectedLessons: []
    readonly property string librarySelectionScope: [search.text, subjectFilter.currentValue, gradeFilter.currentValue, stateFilter.currentValue, voiceFilter.currentValue].join("|")
    onLibrarySelectionScopeChanged: selectedLessons = []
    onLibraryResultChanged: {
        const kept = selectedLessons.filter(function(id) { return (libraryResult.ids || []).indexOf(id) >= 0 })
        if (kept.length !== selectedLessons.length) selectedLessons = kept
    }
    function selectLibraryLesson(identity, selected) {
        const list = selectedLessons.filter(function(id) { return id !== identity })
        if (selected) list.push(identity)
        selectedLessons = list
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
    readonly property bool keepSourceDesign: bridge.lesson.presentation_style === "source"
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
    readonly property var creationPrompt: page === "new" ? bridge.conversionPromptPreview(
        titleInput.text, creationSubject, educationInput.currentText, gradeInput.currentText, pasteInput.text,
        selectedFile, selectedConversionFormat.id,
        ["standard", "visual", "practice"][creationPreset.currentIndex], creationKeepSource ? "source" : "template", teacherNotesInput.text) : ({prompt: "", ready: false})
    property var templatePages: bridge.templatePages(rescue)
    property int templatePageIndex: 0
    function refreshTemplate() { templatePages = bridge.templatePages(rescue); templatePageIndex = 0 }
    function acceptInputDocuments(urls) {
        let selection = bridge.selectInputDocument(urls)
        if (!selection.valid) { inputDocumentError = bridge.message; return false }
        inputDocumentError = ""
        let previousTitle = selectedFileName.replace(/\.[^.]+$/, "")
        selectedFile = selection.url
        selectedFileName = selection.name
        pasteInput.text = ""
        pasteMode = false
        if (!titleInput.text.trim() || titleInput.text === previousTitle) titleInput.text = selection.name.replace(/\.[^.]+$/, "")
        bridge.clearInputAssessment()
        return true
    }
    function removeInputDocument() {
        if (titleInput.text === selectedFileName.replace(/\.[^.]+$/, "")) titleInput.text = ""
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
        return value === "READY_TO_TEACH" ? "Đã duyệt văn bản" : value === "REVIEW_REQUIRED" ? "Chờ duyệt" : "Bản nháp"
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
        } else page = destination
    }) }
    function edited() {
        if (!loadingFields) { dirty = true; autoSaveTimer.restart() }
    }
    onClosing: function(close) {
        if (bridge.updateApplying) { close.accepted = true }
        else if (bridge.updateState.downloading) { close.accepted = false; updateBusyDialog.open() }
        else if (bridge.busy) { close.accepted = false; busyDialog.open() }
        else if (dirty) { close.accepted = false; requestAction(function() { Qt.quit() }) }
    }
    Connections {
        target: bridge
        function onUpdateAvailable() { updateDialog.open() }
        function onPowerpointSlideChanged(slide) { if (!root.dirty) bridge.followPowerPoint() }
        function onPowerpointStarted() {
            if (bridge.mascotSettings.visible) {
                companion.collapsed = true
                bridge.showCompanion(companion, true)
            }
        }
        function onProjectClassroomRequested() { projector.quiz = true; bridge.showProjector(projector, bridge.screens.length > 1 ? 1 : 0) }
        function onNavigate(destination) { root.page = destination === "browser-settings" ? "settings" : destination; if (destination === "result") root.resultDetails = false; if (destination === "browser-settings") settingsPanel.activeTab = 6; root.loadFields(); if (destination === "result" || destination === "editor") { titleInput.text = ""; subjectInput.currentIndex = -1; customSubjectInput.text = ""; pasteInput.text = ""; teacherNotesInput.text = ""; root.inputDocumentError = ""; root.preferredCreationDesign = 0; root.selectedFile = ""; root.selectedFileName = "" } }
        function onSelectionChanged() { root.loadFields(); let mode = bridge.lessonNarration.mode; root.narrationMode = ["vi", "en", "both"].indexOf(mode) >= 0 ? mode : "en"; root.narrationVoice = bridge.lessonNarration.voice || bridge.voiceSettings.voice || ""; root.narrationRate = bridge.lessonNarration.voice ? bridge.lessonNarration.rate : bridge.voiceSettings.rate }
        function onComparisonReady() { comparisonDialog.open() }
        function onChanged() { root.presentationContent = bridge.presentationContent(root.rescue); root.refreshTemplate() }
        function onMemoryChoicesAvailable() { memoryDialog.open() }
        function onCloseMemoryChoicesRequested() { memoryDialog.close() }
        function onMascotPreferencesSaved(visible) {
            if (visible) {
                companion.collapsed = true
                bridge.showCompanion(companion)
            } else companion.hide()
        }
    }
    Timer {
        id: autoSaveTimer; interval: 1800; repeat: false
        onTriggered: {
            if (root.dirty && !bridge.busy && bridge.autoSave(viEdit.text, enEdit.text, lockedCheck.checked)) root.dirty = false
        }
    }

    Component.onCompleted: Qt.callLater(function() { if (bridge.lessons.length === 0 && root.page === "home") helpDialog.open() })
    Shortcut { sequence: "F1"; onActivated: helpDialog.open() }
    component Heading: Label { color: root.ink; font.pixelSize: 27; font.weight: Font.Bold; wrapMode: Text.WordWrap }
    component Copy: Label { color: root.muted; font.pixelSize: 13; wrapMode: Text.WordWrap; lineHeight: 1.25; textFormat: Text.PlainText }
    component Caption: Label { color: root.ink; font.pixelSize: 13; font.weight: Font.DemiBold; textFormat: Text.PlainText }
    component Action: Button {
        id: action
        property bool danger: false
        property bool primary: false
        property bool subtle: false
        property string iconName: ""
        implicitHeight: 43
        leftPadding: 17; rightPadding: 17
        font.pixelSize: 13; font.weight: Font.DemiBold
        contentItem: RowLayout {
            spacing: 7
            Item { Layout.fillWidth: true }
            Image { visible: !!action.iconName; source: action.iconName ? "../assets/actions/" + action.iconName + ".png" : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 23; Layout.preferredHeight: 23; opacity: action.enabled ? 1 : .4 }
            Text { text: action.text; font: action.font; color: !action.enabled ? "#96a6bc" : action.primary ? "white" : action.danger ? "#b14828" : root.blue; verticalAlignment: Text.AlignVCenter }
            Item { Layout.fillWidth: true }
        }
        background: Rectangle {
            radius: 9
            color: !action.enabled ? "#e8eef5" : action.primary ? (action.down ? "#0055d8" : action.hovered ? "#147aff" : root.blue) : action.hovered ? "#e8f1ff" : (action.subtle ? "transparent" : "white")
            border.color: action.primary || action.subtle ? "transparent" : "#cbdcf4"
            border.width: action.visualFocus ? 2 : 1
        }
    }
    component Field: TextField {
        implicitHeight: 43; selectByMouse: true
        color: root.ink; placeholderTextColor: "#8a99b0"; font.pixelSize: 13
        leftPadding: 12; rightPadding: 12
        background: Rectangle { radius: 8; color: "white"; border.color: parent.activeFocus ? root.blue : root.line }
    }
    component Choice: ComboBox {
        implicitHeight: 43; font.pixelSize: 13
        palette.buttonText: root.ink; palette.text: root.ink; palette.highlight: root.blue
        background: Rectangle { radius: 8; color: "white"; border.color: parent.activeFocus ? root.blue : root.line }
    }
    component Surface: Rectangle { color: "white"; radius: 16; border.color: root.line }
    component Pill: Rectangle {
        property string text: ""
        property color tone: root.blue
        implicitHeight: 28; implicitWidth: pillText.implicitWidth + 22; radius: 14
        color: Qt.rgba(tone.r, tone.g, tone.b, 0.08)
        Label { id: pillText; anchors.centerIn: parent; text: parent.text; color: parent.tone; font.pixelSize: 11; font.weight: Font.DemiBold }
    }

    RowLayout {
        anchors.fill: parent; spacing: 0
        Rectangle {
            Layout.preferredWidth: 216; Layout.fillHeight: true; color: "white"
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: root.line }
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 20; spacing: 8
                RowLayout {
                    Layout.topMargin: 13; Layout.bottomMargin: 3; spacing: 9
                    Image { source: "book.svg"; sourceSize.width: 35; sourceSize.height: 35; Layout.preferredWidth: 35; Layout.preferredHeight: 35 }
                    Label { text: "Bili<span style='color:#ff7d2b'>Class</span>"; textFormat: Text.RichText; color: root.ink; font.pixelSize: 25; font.weight: Font.Bold }
                }
                Copy { text: "CÙNG DẠY. CÙNG TIẾN XA."; font.pixelSize: 9; font.letterSpacing: 0.8; Layout.bottomMargin: 31 }
                ScrollView {
                    id: sidebarNavigation; objectName: "sidebarNavigation"
                    Layout.fillWidth: true; Layout.fillHeight: true
                    clip: true; contentWidth: availableWidth
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    ColumnLayout {
                        width: sidebarNavigation.availableWidth; spacing: 8
                        Repeater {
                            model: [{key:"home", label:"Trang chủ", icon:"home"}, {key:"library", label:"Bài giảng", icon:"lessons"}, {key:"classroom", label:"Lớp học", icon:"classroom"}, {key:"reports", label:"Báo cáo", icon:"reports"}, {key:"reference", label:"Thuật ngữ & kiến thức", icon:"data"}, {key:"settings", label:"Cài đặt", icon:"settings"}]
                            delegate: Button {
                                required property var modelData
                                objectName: "navigation" + modelData.key
                                readonly property bool selected: root.page === modelData.key || (modelData.key === "library" && ["editor", "new", "result", "chatgpt"].indexOf(root.page) >= 0)
                                Layout.fillWidth: true; implicitHeight: 48; leftPadding: 14
                                onClicked: root.go(modelData.key)
                                background: Rectangle { radius: 10; color: parent.selected ? "#eaf3ff" : parent.hovered ? "#f4f7fc" : "transparent" }
                                contentItem: RowLayout {
                                    spacing: 13
                                    Image { source: "../assets/navigation/" + modelData.icon + (selected ? "-active" : "") + ".png"; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 29; Layout.preferredHeight: 29 }
                                    Label { text: modelData.label; font.pixelSize: 14; font.weight: selected ? Font.DemiBold : Font.Normal; color: selected ? root.blue : root.muted; Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap }
                                }
                            }
                        }
                    }
                }
                Button {
                    objectName: "openCompanion"
                    visible: bridge.mascotSettings.visible
                    Layout.fillWidth: true; implicitHeight: 58
                    onClicked: bridge.showCompanion(companion)
                    background: Rectangle { radius: 11; color: parent.hovered ? "#e6f1ff" : "#f4f8fe" }
                    contentItem: RowLayout {
                        spacing: 7
                        Mascot { character: bridge.settings.mascot; expression: bridge.mascotState; reducedMotion: bridge.mascotSettings.reduced_motion; accessories: false; Layout.preferredWidth: 42; Layout.preferredHeight: 48 }
                        Label { text: "Mở trợ giảng nổi"; color: root.blue; font.pixelSize: 12; font.weight: Font.DemiBold; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                    }
                }
                Rectangle { Layout.fillWidth: true; height: 1; color: root.line; Layout.topMargin: 14; Layout.bottomMargin: 12 }
                RowLayout {
                    Layout.fillWidth: true; spacing: 10
                    Item {
                        Layout.preferredWidth: 40; Layout.preferredHeight: 40
                        Image {
                            id: sidebarSchoolLogo; objectName: "sidebarSchoolLogo"
                            anchors.fill: parent; source: bridge.schoolLogoUrl; cache: false
                            fillMode: Image.PreserveAspectFit; visible: status === Image.Ready
                            Accessible.name: "Logo trường"
                        }
                        Rectangle {
                            objectName: "sidebarProfileInitial"
                            anchors.centerIn: parent; width: 36; height: 36; radius: 18; color: "#fff0df"
                            visible: sidebarSchoolLogo.status !== Image.Ready
                            Label { anchors.centerIn: parent; text: (bridge.settings.teacher || "G").charAt(0).toUpperCase(); color: "#ab611f"; font.weight: Font.Bold }
                        }
                    }
                    ColumnLayout { Layout.fillWidth: true; spacing: 3
                        Label { objectName: "sidebarTeacherName"; text: bridge.settings.teacher; color: root.ink; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.Wrap; textFormat: Text.PlainText }
                        Copy { text: bridge.settings.school || "Giáo viên · Local"; font.pixelSize: 10; Layout.fillWidth: true; wrapMode: Text.Wrap; textFormat: Text.PlainText }
                    }
                }
                Action { objectName: "sidebarHelpButton"; text: "Hướng dẫn · F1"; implicitHeight: 32; subtle: true; Layout.alignment: Qt.AlignHCenter; onClicked: helpDialog.open() }
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
            Rectangle {
                Layout.fillWidth: true; height: 70; color: "#ffffff"
                Rectangle { anchors.bottom: parent.bottom; height: 1; width: parent.width; color: root.line }
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 30; anchors.rightMargin: 30
                    Copy { text: (root.page === "editor" || root.page === "result") ? "Bài học  /  " + (bridge.lesson.title || "") : bridge.appSubtitle; color: root.ink; elide: Text.ElideRight; Layout.fillWidth: true; maximumLineCount: 1 }
                    Action { objectName: "backToConvertedLessonButton"; visible: root.page === "editor"; text: "Bản trình chiếu"; iconName: "back"; subtle: true; implicitHeight: 32; onClicked: root.go("result") }
                    Pill { text: "ANH  ⇄  VIỆT" }
                    Pill { text: "Lưu trên máy"; tone: "#168567"; Layout.leftMargin: 10 }
                }
            }
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                ScrollView {
                    objectName: "libraryHomeScroll"; anchors.fill: parent; anchors.margins: 30
                    visible: root.page === "home" || root.page === "library"
                    clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 23
                        RowLayout {
                            Layout.fillWidth: true
                            ColumnLayout { Layout.fillWidth: true; spacing: 8; Heading { objectName: "libraryHomeHeading"; Layout.fillWidth: true; wrapMode: Text.WordWrap; text: root.page === "home" ? "Chào " + bridge.settings.teacher : "Thư viện bài giảng"; font.pixelSize: 28 }
                                Copy { text: root.page === "home" ? "Tiếp tục chuẩn bị bài và sẵn sàng cho tiết dạy." : "Tìm đúng bài, chọn bản giọng và mở để dạy hoặc tải PowerPoint."; Layout.fillWidth: true } }
                            Item { Layout.fillWidth: true }
                            Action { text: "+  Bài học mới"; primary: true; onClicked: root.go("new") }
                        }
                        Rectangle {
                            visible: root.page === "home"
                            objectName: "homeWorkPanel"; Layout.fillWidth: true; implicitHeight: 200; radius: 19; color: "#e6f0ff"
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 28; spacing: 28
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 13
                                    Caption { text: bridge.narrationBusy || bridge.browserState.running ? "Công việc đang xử lý" : "Chuẩn bị cho tiết dạy"; color: root.blue }
                                    Label { text: bridge.narrationBusy ? "Đang tạo giọng đọc" : bridge.browserState.running ? "Đang chuyển đổi bài giảng" : "Chọn bài và bắt đầu tiết học"; color: root.ink; font.pixelSize: 23; font.weight: Font.Bold; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                                    Copy { Layout.fillWidth: true; text: bridge.narrationBusy ? "Các đoạn âm thanh đã xong được lưu để tiếp tục." : bridge.browserState.running ? bridge.browserState.message || "BiliClass đang xử lý tài liệu." : bridge.librarySummary.total + " bài trong thư viện · " + bridge.librarySummary.ready + " bài đã duyệt · " + bridge.librarySummary.voiced + " bài có giọng đọc sẵn sàng." }
                                    RowLayout { Layout.fillWidth: true
                                        Action { objectName: "homeContinueWork"; text: bridge.narrationBusy || bridge.browserState.running ? "Xem công việc đang làm" : "Chọn bài để dạy"; onClicked: { if (bridge.narrationBusy && bridge.narrationTaskLessonId) bridge.openLesson(bridge.narrationTaskLessonId); else if (bridge.browserState.running) root.go("new"); else root.go("library") } }
                                        Action { objectName: "homeClassroomButton"; text: "Lớp học"; subtle: true; onClicked: root.go("classroom") }
                                    }
                                }
                                Image {
                                    Layout.preferredWidth: 154; Layout.fillHeight: true
                                    source: bridge.settings.mascot === "Lumi" ? "../assets/lumi-welcome.png" : "../assets/milo-welcome.png"
                                    fillMode: Image.PreserveAspectFit; sourceSize.width: 420; sourceSize.height: 420
                                    Accessible.name: bridge.settings.mascot + " chào thầy cô"
                                }
                            }
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
                                    Action { text: bridge.updateState.ready ? "Mở bản mới" : "Cập nhật"; primary: true; enabled: !bridge.updateState.downloading && !bridge.busy && !root.classroom.running; onClicked: bridge.updateState.ready ? bridge.applyDownloadedUpdate() : bridge.downloadUpdate() }
                                    Action { visible: bridge.updateState.downloading; text: "Hủy tải"; onClicked: bridge.cancelUpdate() }
                                }
                                ProgressBar { visible: bridge.updateState.downloading; Layout.fillWidth: true; value: bridge.updateState.progress / 100 }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Label { text: root.page === "home" ? "Bài vừa cập nhật" : "Tất cả bài giảng"; color: root.ink; font.pixelSize: 18; font.weight: Font.DemiBold }
                            Copy { objectName: "libraryResultCount"; text: root.page === "home" ? bridge.lessons.length + " bài" : root.libraryResult.total + " / " + bridge.lessons.length + " bài"; Layout.leftMargin: 8 }
                            Item { Layout.fillWidth: true }
                            Action { visible: root.page === "home"; text: "Xem toàn bộ"; subtle: true; onClicked: root.go("library") }
                            Action { objectName: "librarySelectMode"; visible: root.page === "library"; text: root.librarySelecting ? "Xong" : "Chọn bài"; subtle: true; onClicked: { root.librarySelecting = !root.librarySelecting; root.selectedLessons = [] } }
                            Action { id: libraryManagementAction; visible: root.page === "library"; objectName: "libraryManagementButton"; text: "Chia sẻ & quản lý"; subtle: true; onClicked: libraryManagementMenu.popup() }
                            Menu { id: libraryManagementMenu; parent: libraryManagementAction; x: parent.width - width; y: parent.height
                                MenuItem { objectName: "importSharedLessonButton"; text: "Nhận gói bài từ giáo viên khác…"; onTriggered: packOpen.open() }
                                MenuItem { text: "Thùng rác (" + bridge.trashedLessons.length + ")"; onTriggered: lessonTrashDialog.open() }
                            }
                        }
                        RowLayout { visible: root.page === "library"; Layout.fillWidth: true; spacing: 12
                            Field { id: search; objectName: "librarySearch"; Layout.fillWidth: true; placeholderText: "Tìm tên bài, môn, khối… có thể gõ không dấu"; onTextChanged: root.libraryPage = 1 }
                            SelectBox { objectName: "lessonSortOrder"; model: ["Mới tạo nhất", "Tạo lâu nhất", "Mới cập nhật", "Tên bài A–Z"]; currentIndex: ["created_desc", "created_asc", "updated_desc", "title_asc"].indexOf(bridge.lessonOrder); Layout.preferredWidth: 168; onActivated: { root.libraryPage = 1; bridge.setLessonOrder(["created_desc", "created_asc", "updated_desc", "title_asc"][currentIndex]) } }
                        }
                        GridLayout { objectName: "libraryFilters"; visible: root.page === "library"; Layout.fillWidth: true; columns: width >= 980 ? 5 : 3; columnSpacing: 10; rowSpacing: 10
                            Choice { id: subjectFilter; objectName: "librarySubjectFilter"; Layout.fillWidth: true; Layout.minimumWidth: 0; model: bridge.librarySubjects; textRole: "label"; valueRole: "id"; onActivated: root.libraryPage = 1 }
                            Choice { id: gradeFilter; objectName: "libraryGradeFilter"; Layout.fillWidth: true; Layout.minimumWidth: 0; model: bridge.libraryGrades; textRole: "label"; valueRole: "id"; onActivated: root.libraryPage = 1 }
                            Choice { id: stateFilter; objectName: "libraryStateFilter"; Layout.fillWidth: true; Layout.minimumWidth: 0; textRole: "label"; valueRole: "id"; model: [{id:"",label:"Tất cả trạng thái"},{id:"ready",label:"Đã duyệt để dạy"},{id:"review",label:"Cần kiểm tra"},{id:"draft",label:"Bản nháp"}]; onActivated: root.libraryPage = 1 }
                            Choice { id: voiceFilter; objectName: "libraryVoiceFilter"; Layout.fillWidth: true; Layout.minimumWidth: 0; textRole: "label"; valueRole: "id"; model: [{id:"",label:"Tất cả giọng đọc"},{id:"en",label:"Có bản giọng Anh"},{id:"vi",label:"Có bản giọng Việt"},{id:"both",label:"Có bản giọng Việt–Anh"},{id:"none",label:"Chưa tạo giọng"},{id:"partial",label:"Giọng chưa hoàn tất"}]; onActivated: root.libraryPage = 1 }
                            Action { objectName: "libraryClearFilters"; text: "Xóa bộ lọc"; subtle: true; onClicked: { search.clear(); subjectFilter.currentIndex = 0; gradeFilter.currentIndex = 0; stateFilter.currentIndex = 0; voiceFilter.currentIndex = 0; root.libraryPage = 1 } }
                        }
                        Flow { visible: root.page === "library" && root.librarySelecting; Layout.fillWidth: true; spacing: 10
                            CheckBox { objectName: "librarySelectAll"; text: "Chọn tất cả (" + root.libraryResult.total + ")"; checked: root.libraryResult.total > 0 && root.selectedLessons.length === root.libraryResult.total; enabled: root.libraryResult.total > 0; onClicked: root.selectedLessons = checked ? root.libraryResult.ids.slice() : [] }
                            Action { objectName: "libraryDeselectAll"; text: "Bỏ chọn"; subtle: true; enabled: root.selectedLessons.length > 0; onClicked: root.selectedLessons = [] }
                            Action { objectName: "libraryDownloadSelected"; text: "Tải đã chọn (" + root.selectedLessons.length + ")"; enabled: root.selectedLessons.length > 0 && !bridge.busy && !bridge.narrationBusy; onClicked: root.downloadLibraryLessons(root.selectedLessons) }
                            Action { objectName: "libraryDeleteSelected"; text: "Xóa đã chọn (" + root.selectedLessons.length + ")"; danger: true; enabled: root.selectedLessons.length > 0 && !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !root.classroom.running; onClicked: { bulkDeleteDialog.identities = root.selectedLessons.slice(); bulkDeleteDialog.open() } }
                        }
                        Copy { visible: root.page === "library" && root.librarySelecting; text: "Chọn tất cả áp dụng cho toàn bộ kết quả đang lọc, gồm các trang khác. Đổi bộ lọc sẽ bỏ chọn."; Layout.fillWidth: true; font.pixelSize: 11 }
                        Surface { visible: root.page === "library" && bridge.lessons.length > 0 && root.libraryResult.total === 0; Layout.fillWidth: true; implicitHeight: 106
                            ColumnLayout { anchors.fill: parent; anchors.margins: 20; spacing: 7
                                Caption { text: "Không có bài phù hợp" }
                                Copy { text: "Thử từ khóa ngắn hơn hoặc dùng Xóa bộ lọc để xem lại toàn bộ bài."; Layout.fillWidth: true }
                            }
                        }
                        Surface {
                            visible: bridge.lessons.length === 0; Layout.fillWidth: true; implicitHeight: 202
                            ColumnLayout { anchors.centerIn: parent; spacing: 13; Label { text: "Bài giảng đầu tiên bắt đầu từ đây"; color: root.ink; font.pixelSize: 19; font.weight: Font.DemiBold }
                                Copy { text: "Tải PPTX, DOCX, PDF có văn bản, TXT hoặc dán nội dung."; Layout.alignment: Qt.AlignHCenter }
                                Action { text: "+  Tạo bài học"; primary: true; Layout.alignment: Qt.AlignHCenter; onClicked: root.go("new") } }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 10
                            Repeater {
                                model: root.page === "home" ? bridge.recentLessons : root.libraryResult.rows
                                delegate: Surface {
                                    required property var modelData
                                    required property int index
                                    objectName: "lessonCard_" + modelData.id
                                    Layout.fillWidth: true; implicitHeight: Math.max(root.page === "home" ? 96 : 120, lessonRow.implicitHeight + 32)
                                    RowLayout {
                                        id: lessonRow; anchors.fill: parent; anchors.margins: 16; spacing: 14
                                        CheckBox { objectName: "lessonSelect_" + modelData.id; visible: root.page === "library" && root.librarySelecting; checked: root.selectedLessons.indexOf(modelData.id) >= 0; Accessible.name: "Chọn " + modelData.title; onClicked: root.selectLibraryLesson(modelData.id, checked) }
                                        Rectangle { width: 44; height: 48; radius: 10; color: "#edf4ff"; Label { anchors.centerIn: parent; text: "VI\nEN"; color: root.blue; font.pixelSize: 12; font.weight: Font.Bold; lineHeight: 1.1 } }
                                        ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 5
                                            Label { text: modelData.title; color: root.ink; font.pixelSize: 15; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true; Layout.minimumWidth: 0 }
                                            Copy { Layout.fillWidth: true; text: modelData.subject + "  ·  " + modelData.education_level + " " + modelData.grade + "  ·  " + (modelData.slides_count ? modelData.slides_count + " slide" : modelData.segments_count + " phần"); font.pixelSize: 12 }
                                            Copy { objectName: "lessonCreated_" + modelData.id; Layout.fillWidth: true; visible: root.page === "library"; text: (modelData.created_at_estimated ? "Lưu sớm nhất còn lại: " : "Tạo: ") + bridge.lessonDateLabel(modelData.created_at); font.pixelSize: 11 }
                                            Copy { objectName: "lessonNarrationBadge_" + modelData.id; Layout.fillWidth: true; text: (modelData.narration || {}).label || "Chưa có giọng đọc"; font.pixelSize: 11; color: (modelData.narration || {}).ready ? "#168567" : root.muted }
                                        }
                                        Pill { text: modelData.quality_failures ? "Cần kiểm tra" : modelData.prepared ? "Đã chốt bài" : root.statusLabel(modelData.status); tone: modelData.prepared ? "#168567" : "#9c651b" }
                                        Action { objectName: "lessonOpen_" + modelData.id; text: "Mở bài"; enabled: !bridge.busy; onClicked: bridge.openLesson(modelData.id) }
                                        Action { objectName: "lessonDownload_" + modelData.id; text: "Tải"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: root.downloadLibraryLessons([modelData.id]) }
                                        Action { objectName: "lessonEdit_" + modelData.id; visible: root.page === "library"; text: "Sửa"; subtle: true; enabled: !bridge.busy && !bridge.powerpointState.active; onClicked: { metadataDialog.lessonData = modelData; metadataDialog.open() } }
                                        Action { objectName: "lessonDelete_" + modelData.id; visible: root.page === "library"; text: "Xóa"; danger: true; subtle: true; enabled: !bridge.busy && !bridge.powerpointState.active; onClicked: { deleteLessonDialog.lessonId = modelData.id; deleteLessonDialog.lessonTitle = modelData.title; deleteLessonDialog.open() } }
                                    }
                                }
                            }
                        }
                        RowLayout { visible: root.page === "library" && root.libraryResult.pages > 1; Layout.fillWidth: true
                            Copy { text: root.libraryResult.start + "–" + root.libraryResult.end + " / " + root.libraryResult.total + " bài" }
                            Item { Layout.fillWidth: true }
                            Action { objectName: "libraryPreviousPage"; text: "Trước"; enabled: root.libraryResult.page > 1; onClicked: root.libraryPage = root.libraryResult.page - 1 }
                            Copy { text: "Trang " + root.libraryResult.page + " / " + root.libraryResult.pages }
                            Action { objectName: "libraryNextPage"; text: "Tiếp"; enabled: root.libraryResult.page < root.libraryResult.pages; onClicked: root.libraryPage = root.libraryResult.page + 1 }
                        }
                        Label { visible: root.page === "home" && root.classroom.sessions.length > 0; text: "Tiết gần đây"; color: root.ink; font.pixelSize: 18; font.weight: Font.DemiBold }
                        Repeater { model: root.page === "home" ? root.classroom.sessions : []
                            delegate: Surface { required property var modelData; required property int index; visible: index < 3; Layout.fillWidth: true; implicitHeight: 72
                                RowLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                                    ColumnLayout { Layout.fillWidth: true; spacing: 4
                                        Caption { text: modelData.title; Layout.fillWidth: true; elide: Text.ElideRight }
                                        Copy { text: [modelData.lesson_title, modelData.subject, modelData.grade ? "Khối " + modelData.grade : ""].filter(function(value) { return !!value }).join(" · "); Layout.fillWidth: true; font.pixelSize: 11 }
                                    }
                                    Pill { text: modelData.status === "ended" ? "Đã kết thúc" : "Đang mở" }
                                    Action { text: "Xem báo cáo"; onClicked: { root.classroom.openReport(modelData.id); root.go("reports") } }
                                }
                            }
                        }
                        Copy { visible: root.page === "home"; text: "Lộ trình   01  Nhập nội dung    →    02  Biên tập Anh–Việt    →    03  Duyệt    →    04  Chốt bản chuẩn bị    →    05  Dạy và xem báo cáo"; font.pixelSize: 11; Layout.topMargin: 2; Layout.bottomMargin: 12 }
                    }
                }

                ScrollView {
                    objectName: "creationScroll"
                    anchors.fill: parent; anchors.margins: 28; anchors.bottomMargin: 103
                    visible: root.page === "new"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 16
                        RowLayout { Heading { text: "Từ tài liệu đến bài giảng song ngữ"; font.pixelSize: 27 } Item { Layout.fillWidth: true } Action { text: "Thư viện"; iconName: "back"; subtle: true; onClicked: root.go("library") } }
                        Copy { text: "Nhập tài liệu → chọn kiểu chuyển đổi → chuyển đổi → xem trình chiếu → dùng để dạy."; Layout.fillWidth: true }
                        Surface {
                            objectName: "creationSourceArea"
                            Layout.fillWidth: true; implicitHeight: sourceInputs.height + 36
                            color: sourceDrop.containsDrag ? "#edf5ff" : "white"
                            border.color: sourceDrop.containsDrag ? root.blue : root.line
                            border.width: sourceDrop.containsDrag ? 2 : 1
                            DropArea {
                                id: sourceDrop; objectName: "creationDocumentDrop"
                                anchors.fill: parent; enabled: !bridge.busy
                                onEntered: function(drag) { drag.accepted = drag.hasUrls && drag.urls.length === 1 }
                                onDropped: function(drop) {
                                    let urls = []
                                    for (let i = 0; i < drop.urls.length; i++) urls.push(drop.urls[i].toString())
                                    if (root.acceptInputDocuments(urls)) drop.acceptProposedAction()
                                    else drop.accepted = false
                                }
                            }
                            ColumnLayout {
                                id: sourceInputs; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 18; spacing: 10
                                RowLayout {
                                    Layout.fillWidth: true
                                    Caption { text: "01   Tài liệu đầu vào"; font.pixelSize: 15 }
                                    Item { Layout.fillWidth: true }
                                    Action { objectName: "chooseInputDocumentButton"; text: root.selectedFile ? "Đổi tài liệu" : "Chọn từ máy tính"; iconName: "upload"; enabled: !bridge.busy; onClicked: documentOpen.open() }
                                }
                                Copy { objectName: "creationDropHint"; text: sourceDrop.containsDrag ? "Thả tài liệu vào đây" : "Kéo thả một tài liệu vào đây · PPTX tối đa 200 MB · DOCX, PDF, TXT, PNG/JPG tối đa 50 MB"; color: sourceDrop.containsDrag ? root.blue : root.muted; Layout.fillWidth: true; font.pixelSize: 12 }
                                Copy { objectName: "creationDocumentError"; visible: !!root.inputDocumentError; text: root.inputDocumentError; color: "#ab5b20"; Layout.fillWidth: true; font.pixelSize: 12 }
                                RowLayout {
                                    visible: !!root.selectedFile; Layout.fillWidth: true
                                    Caption { objectName: "creationSelectedFilename"; text: root.selectedFileName; elide: Text.ElideMiddle; Layout.fillWidth: true }
                                    Pill { text: "Đã nhận tệp" }
                                    Action { objectName: "removeInputDocumentButton"; text: "Bỏ tệp"; subtle: true; implicitHeight: 30; enabled: !bridge.busy; onClicked: root.removeInputDocument() }
                                }
                                Action { visible: !root.selectedFile; text: root.pasteMode ? "Thu gọn nội dung" : "Hoặc dán nội dung bài học"; subtle: true; implicitHeight: 28; enabled: !bridge.busy; onClicked: root.pasteMode = !root.pasteMode }
                                ScrollView { visible: root.pasteMode && !root.selectedFile; Layout.fillWidth: true; Layout.preferredHeight: 110; clip: true
                                    TextArea { id: pasteInput; objectName: "lessonContent"; enabled: !bridge.busy; wrapMode: TextEdit.Wrap; selectByMouse: true; color: root.ink; font.pixelSize: 13; placeholderText: "Dán nội dung tiếng Việt hoặc song ngữ…"; background: Rectangle { color: "#fafcff"; radius: 8; border.color: root.line } }
                                }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; implicitHeight: config.height + 38
                            ColumnLayout {
                                id: config; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 19; spacing: 12; enabled: !bridge.busy
                                Caption { text: "02   Cấu hình bài giảng"; font.pixelSize: 15 }
                                GridLayout {
                                    Layout.fillWidth: true; columns: 12; columnSpacing: 12; rowSpacing: 7
                                    Caption { text: "Tên bài học"; Layout.columnSpan: 4 } Caption { text: "Môn học"; Layout.columnSpan: 4 }
                                    Caption { text: "Cấp học"; Layout.columnSpan: 2 } Caption { text: "Khối lớp"; Layout.columnSpan: 2 }
                                    Field { id: titleInput; objectName: "lessonTitle"; Layout.fillWidth: true; Layout.columnSpan: 4; Layout.preferredWidth: 320; Layout.minimumWidth: 120; Layout.alignment: Qt.AlignTop; placeholderText: "Tên bài giảng"; maximumLength: 180 }
                                    ColumnLayout {
                                        Layout.fillWidth: true; Layout.columnSpan: 4; Layout.preferredWidth: 320; Layout.minimumWidth: 120; Layout.alignment: Qt.AlignTop; spacing: 7
                                        Choice {
                                            id: subjectInput; objectName: "lessonSubject"; Layout.fillWidth: true
                                            model: bridge.conversionSubjects; currentIndex: -1; leftPadding: 12; rightPadding: 36
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
                                                background: Rectangle { radius: 5; color: parent.highlighted || parent.hovered ? "#e8f1ff" : "transparent" }
                                            }
                                            popup: Popup {
                                                id: subjectPopup; objectName: "creationSubjectPopup"
                                                y: subjectInput.height + 4; width: Math.min(root.width - 32, Math.max(subjectInput.width, 400)); padding: 6
                                                implicitHeight: Math.min(contentItem.implicitHeight + 12, 400, root.height - 60)
                                                contentItem: ListView {
                                                    id: subjectList; objectName: "creationSubjectList"; clip: true
                                                    implicitHeight: contentHeight; model: subjectPopup.visible ? subjectInput.delegateModel : null
                                                    currentIndex: subjectInput.highlightedIndex; highlightMoveDuration: 0
                                                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                                }
                                                background: Rectangle { color: "white"; radius: 8; border.color: root.line }
                                            }
                                        }
                                        Field { id: customSubjectInput; objectName: "creationCustomSubject"; visible: subjectInput.currentText === "Khác"; Layout.fillWidth: true; placeholderText: "Nhập tên môn học khác"; maximumLength: 100; Accessible.name: "Tên môn học khác" }
                                    }
                                    Choice { id: educationInput; objectName: "creationEducation"; model: ["THPT", "THCS", "Tiểu học"]; Layout.columnSpan: 2; Layout.preferredWidth: 160; Layout.minimumWidth: 115; Layout.fillWidth: true; Layout.alignment: Qt.AlignTop }
                                    Choice { id: gradeInput; objectName: "creationGrade"; model: bridge.educationGrades(educationInput.currentText); onModelChanged: currentIndex = 0; Layout.columnSpan: 2; Layout.preferredWidth: 130; Layout.minimumWidth: 80; Layout.fillWidth: true; Layout.alignment: Qt.AlignTop }
                                }
                                Caption { text: "Kiểu chuyển đổi · chọn một" }
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
                                            selected: creationFormat.currentIndex === index; showPreview: true
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
                                        choiceGroup: designChoices
                                        label: "Giữ thiết kế PowerPoint gốc"
                                        detail: bridge.googleTranslation ? "Giữ nền, hình và công thức. Song ngữ tự căn từng vùng; tiếng Anh 100% thay chữ tại vị trí gốc. Vùng quá chật có trang tiếp nối song ngữ. Chữ trong ảnh và hiệu ứng cần đối chiếu." : root.creationPowerPoint ? "Dùng đúng PowerPoint đầu vào: giữ thiết kế, hình, thứ tự slide và hiệu ứng; chuyển ngôn ngữ theo kiểu đã chọn." : root.creationCanKeepSource ? "Chọn tệp PPTX để giữ thiết kế, hình, thứ tự slide và hiệu ứng của PowerPoint đầu vào." : "Word/PDF/ảnh hoặc nội dung dán không có thiết kế PowerPoint gốc; dùng mẫu mới."
                                        selected: creationWorkflow.currentIndex === 0
                                        enabled: root.creationCanKeepSource; Layout.fillWidth: true; Layout.preferredWidth: 1
                                        onChosen: { root.preferredCreationDesign = 0; creationWorkflow.currentIndex = 0 }
                                    }
                                    ConversionChoice {
                                        choiceName: "creationUseTemplate"
                                        choiceGroup: designChoices
                                        label: "Tạo theo mẫu mới"
                                        detail: bridge.customTemplate.name ? "Điền chữ vào mẫu PowerPoint riêng tại máy, tự chia trang; hình nguồn có trang riêng. Hiệu ứng nguồn không được tái dựng." : "Dàn trang tại máy theo bộ Universal 2026. Tự chọn bố cục, giữ hình cùng nội dung; chia trang khi dài. Hiệu ứng nguồn không được tái dựng."
                                        selected: creationWorkflow.currentIndex === 1
                                        Layout.fillWidth: true; Layout.preferredWidth: 1
                                        onChosen: { root.preferredCreationDesign = 1; creationWorkflow.currentIndex = 1 }
                                    }
                                }
                                RowLayout {
                                    visible: !root.creationKeepSource; Layout.fillWidth: true
                                    Caption { text: bridge.customTemplate.name ? "Mẫu riêng" : "Mẫu BiliClass" }
                                    Choice { id: creationPreset; objectName: "creationPreset"; visible: !bridge.customTemplate.name; model: ["Chuẩn lớp học", "Trực quan", "Luyện tập & tương tác"]; Layout.fillWidth: true }
                                    Copy { visible: !!bridge.customTemplate.name; text: bridge.customTemplate.name || ""; Layout.fillWidth: true; Layout.minimumWidth: 0 }
                                    Action { objectName: "creationTemplatesButton"; text: bridge.googleTranslation ? "Xem PowerPoint mẫu" : "Xem slide mẫu"; iconName: "view"; enabled: !bridge.busy; onClicked: { if (bridge.googleTranslation) bridge.openLocalTemplateSample(["standard", "visual", "practice"][creationPreset.currentIndex], root.selectedConversionFormat.id); else { templateGallery.forCreation = true; templateGallery.preset = ["standard", "visual", "practice"][creationPreset.currentIndex]; templateGallery.level = root.selectedConversionFormat.level; templateGallery.layout = root.selectedConversionFormat.layout; templateGallery.open() } } }
                                }
                                Flow { visible: !root.creationKeepSource && bridge.googleTranslation; Layout.fillWidth: true; spacing: 10
                                    Action { objectName: "chooseCustomTemplateButton"; text: "Chọn mẫu PowerPoint riêng…"; enabled: !bridge.busy; onClicked: customTemplateOpen.open() }
                                    Action { objectName: "clearCustomTemplateButton"; visible: !!bridge.customTemplate.name; text: "Dùng mẫu BiliClass"; enabled: !bridge.busy; onClicked: bridge.clearCustomTemplate() }
                                }
                                Copy { visible: !root.creationKeepSource && !bridge.customTemplate.name; Layout.fillWidth: true; Layout.minimumWidth: 0; text: "Universal 2026 · 23 bố cục mỗi phong cách. Tự chọn theo tiêu đề, nội dung, hình, công thức, bảng hoặc câu hỏi; giữ đủ chữ và tự chia trang khi cần." }
                                CheckBox { objectName: "templateBookends"; visible: !root.creationKeepSource && !bridge.customTemplate.name; text: "Thêm bìa và trang kết thúc"; checked: bridge.templateBookends; onToggled: bridge.setTemplateBookends(checked) }
                                ColumnLayout { visible: !root.creationKeepSource && !!bridge.customTemplate.name; Layout.fillWidth: true; spacing: 8
                                    Copy { Layout.fillWidth: true; Layout.minimumWidth: 0; text: "Chọn số trang trong file mẫu · 0 để bỏ trang tuỳ chọn. Tool điền chữ vào ô tiêu đề/nội dung, giữ nền và hình của mẫu. Để chỉ định đúng ô, đặt tên BCL_TITLE và BCL_CONTENT trong Selection Pane của PowerPoint." }
                                    GridLayout { columns: 4; columnSpacing: 12; rowSpacing: 6; Layout.fillWidth: true
                                        Caption { text: "Bìa (tuỳ chọn)" }
                                        SpinBox { id: templateCover; objectName: "templateCoverPage"; from: 0; to: (bridge.customTemplate.pages || []).length; value: (bridge.customTemplate.roles || {}).cover || 0; editable: true }
                                        Caption { text: "Intro (tuỳ chọn)" }
                                        SpinBox { id: templateIntro; objectName: "templateIntroPage"; from: 0; to: templateCover.to; value: (bridge.customTemplate.roles || {}).intro || 0; editable: true }
                                        Caption { text: "Nội dung" }
                                        SpinBox { id: templateContent; objectName: "templateContentPage"; from: 1; to: Math.max(1, templateCover.to); value: (bridge.customTemplate.roles || {}).content || 1; editable: true }
                                        Caption { text: "Kết thúc (tuỳ chọn)" }
                                        SpinBox { id: templateEnding; objectName: "templateEndingPage"; from: 0; to: templateCover.to; value: (bridge.customTemplate.roles || {}).ending || 0; editable: true }
                                    }
                                    Action { objectName: "saveCustomTemplateRolesButton"; text: "Lưu vai trò trang mẫu"; enabled: !bridge.busy; onClicked: bridge.setCustomTemplateRoles(templateCover.value, templateIntro.value, templateContent.value, templateEnding.value) }
                                }
                                RowLayout {
                                    visible: !bridge.googleTranslation
                                    Layout.fillWidth: true
                                    Caption { text: "Ghi chú thêm · không bắt buộc"; Layout.fillWidth: true }
                                    Copy { text: teacherNotesInput.text.trim().length + " / 6.000"; color: teacherNotesInput.text.trim().length > 6000 ? "#ab5b20" : root.muted; font.pixelSize: 11 }
                                }
                                ScrollView {
                                    visible: !bridge.googleTranslation
                                    Layout.fillWidth: true; Layout.preferredHeight: 90; clip: true
                                    TextArea {
                                        id: teacherNotesInput; objectName: "creationTeacherNotes"
                                        enabled: !bridge.busy; wrapMode: TextEdit.Wrap; selectByMouse: true
                                        placeholderText: "Ví dụ: giữ các bước giải; dùng thuật ngữ dễ hiểu cho học sinh lớp 7; chú ý phần chữ trong hình…"
                                        color: root.ink; font.pixelSize: 13
                                        background: Rectangle { radius: 8; color: "#fafcff"; border.color: root.line }
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
                                    Action { objectName: "creationPromptToggle"; text: root.creationPromptVisible ? "Ẩn prompt" : "Hiện prompt"; iconName: "view"; subtle: true; implicitHeight: 30; onClicked: root.creationPromptVisible = !root.creationPromptVisible }
                                }
                                ScrollView {
                                    visible: root.creationPromptVisible; Layout.fillWidth: true; Layout.preferredHeight: 270; clip: true
                                    TextArea { objectName: "creationPromptText"; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; text: root.creationPrompt.prompt || ""; color: root.ink; font.pixelSize: 12; background: Rectangle { radius: 8; color: "#fafcff"; border.color: root.line } }
                                }
                            }
                        }
                        Action { text: "Tiếp tục bài đang chuẩn bị"; visible: !!bridge.chatgptRequest.folder; subtle: true; onClicked: root.go("chatgpt") }
                    }
                }
                Rectangle {
                    visible: root.page === "new"; anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
                    height: 85; color: "#f3f7fc"
                    Rectangle { anchors.top: parent.top; height: 1; width: parent.width; color: root.line }
                    RowLayout {
                        anchors.fill: parent; anchors.leftMargin: 28; anchors.rightMargin: 28; spacing: 16
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 3
                            Copy { text: "Nhận bài giảng song ngữ trước · tạo giọng đọc sau nếu cần."; Layout.fillWidth: true; font.pixelSize: 12 }
                            Action { text: bridge.googleTranslation ? "Google Dịch · " + (bridge.googleSettings.state.configured ? "Đã lưu API key" : "Cần thêm API key") : bridge.browserAI.serviceLabel + ": " + bridge.browserAI.activeLabel + " · Browser AI"; subtle: true; implicitHeight: 28; onClicked: { root.go("settings"); settingsPanel.activeTab = 6 } }
                        }
                        Action { objectName: "createLessonButton"; text: bridge.busy ? "Đang chuẩn bị…" : "Chuyển đổi bài giảng"; primary: true; enabled: !bridge.busy && !root.inputDocumentError && root.creationPrompt.ready; onClicked: bridge.convertDocument(titleInput.text, root.creationSubject, educationInput.currentText, gradeInput.currentText, pasteInput.text, root.selectedFile, root.selectedConversionFormat.id, ["standard", "visual", "practice"][creationPreset.currentIndex], root.creationKeepSource ? "source" : "template", teacherNotesInput.text) }
                    }
                }

                ScrollView {
                    anchors.fill: parent; anchors.margins: 30; visible: root.page === "chatgpt"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout { Heading { text: "Tạo bài giảng song ngữ"; font.pixelSize: 28 } Item { Layout.fillWidth: true } Action { text: "Đổi cấu hình"; subtle: true; enabled: !bridge.browserState.running; onClicked: root.go("new") } }
                        Copy { Layout.fillWidth: true; text: (bridge.chatgptRequest.config || {}).title || "Chuẩn bị tài liệu trước khi gửi"; color: root.ink; font.pixelSize: 17 }
                        Surface {
                            visible: bridge.googleTranslation || bridge.browserAI.automatic && bridge.browserState.phase !== "manual"
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
                                    background: Rectangle { implicitHeight: 9; radius: 4.5; color: "#e8eff9" }
                                    contentItem: Item {
                                        implicitHeight: 9; clip: true
                                        Rectangle {
                                            id: conversionCompletedFill; objectName: "browserConversionCompletedFill"
                                            width: parent.width * conversionBar.visualPosition; height: parent.height; radius: 4.5; color: root.blue; clip: true
                                            Rectangle {
                                                id: conversionPulse; objectName: "browserConversionPulse"
                                                visible: !!bridge.browserState.running && !!bridge.browserState.waiting
                                                width: parent.width * 0.32; height: parent.height; radius: 4.5; color: "#ffffff"; opacity: 0.32
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
                                Copy { objectName: "browserConversionLongWait"; Layout.fillWidth: true; visible: !!bridge.conversionClock.longWait; text: "Bài đang mất nhiều thời gian hơn thường lệ. BiliClass vẫn theo dõi kết quả và sẽ báo ngay nếu cần bạn xử lý."; color: "#a66318"; font.pixelSize: 12 }
                                Copy { Layout.fillWidth: true; text: "Bài giảng song ngữ · Trình chiếu · Giọng đọc · Trợ giảng" }
                                RowLayout { Layout.fillWidth: true
                                    Action { objectName: "browserConversionResume"; text: !bridge.googleTranslation && bridge.browserAI.webMode && bridge.browserState.needsLogin ? "Kết nối và tiếp tục" : bridge.browserState.errorCode === "submission" ? "Kiểm tra và tiếp tục" : "Tiếp tục chuyển đổi"; primary: true; visible: !bridge.browserState.running && bridge.browserState.phase !== "completed"; enabled: !bridge.busy && (bridge.googleTranslation || !bridge.browserAI.loginBusy) && !!bridge.chatgptRequest.folder; onClicked: { if (!bridge.googleTranslation && bridge.browserAI.webMode && (bridge.browserState.needsLogin || bridge.browserState.errorCode === "submission")) bridge.reconnectBrowserAI(); else bridge.runBrowserAI() } }
                                    Action { id: conversionCancel; objectName: "browserConversionCancel"; text: "Dừng"; visible: !!bridge.browserState.running; onClicked: bridge.cancelJob() }
                                    Action { text: bridge.googleTranslation ? "Cấu hình Google Dịch" : "Đăng nhập / Browser AI"; visible: !bridge.browserState.running && (bridge.googleTranslation || !!bridge.browserState.needsLogin); enabled: !bridge.busy; onClicked: { root.go("settings"); settingsPanel.activeTab = 6 } }
                                }
                                Copy { text: bridge.browserState.running ? "BiliClass tự động xử lý. Bài giảng sẽ xuất hiện trong thư viện khi hoàn tất." : "Tài liệu và các phần đã hoàn tất được lưu để tiếp tục."; Layout.fillWidth: true; font.pixelSize: 12 }
                            }
                        }
                        Surface {
                            visible: !bridge.googleTranslation && (!bridge.browserAI.automatic || bridge.browserState.phase === "manual")
                            Layout.fillWidth: true; implicitHeight: chatgptSteps.height + 42
                            ColumnLayout {
                                id: chatgptSteps; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 21; spacing: 18
                                Caption { text: "1. Gửi prompt và tài liệu trong browser"; font.pixelSize: 17 }
                                Copy { Layout.fillWidth: true; text: "Mở ChatGPT bằng tài khoản của thầy cô. Dán prompt, đính kèm " + (bridge.chatgptRequest.attachments || []).join(" và ") + ", rồi bấm Gửi. Gói ZIP dùng để lưu/chia sẻ; giải nén trước nếu gửi từ ZIP." }
                                RowLayout { Layout.fillWidth: true; Action { objectName: "copyChatGPTPromptButton"; text: "Sao chép prompt"; primary: true; enabled: !!bridge.chatgptRequest.folder; onClicked: bridge.copyChatGPTPrompt() } Action { objectName: "openChatGPTFolderButton"; text: "Mở thư mục tài liệu"; onClicked: bridge.openChatGPTFolder() } Action { objectName: "openChatGPTButton"; text: "Mở ChatGPT"; onClicked: bridge.openChatGPT() } }
                                Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: root.line }
                                Caption { text: "2. Tải PowerPoint kết quả về máy"; font.pixelSize: 17 }
                                Copy { Layout.fillWidth: true; text: "Tải file .pptx do ChatGPT tạo. Nếu ChatGPT chỉ trả văn bản, yêu cầu xuất PowerPoint có thể tải xuống. Khả năng tạo tệp và lượt dùng phụ thuộc tài khoản của thầy cô." }
                                Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: root.line }
                                Caption { text: "3. Nhận bài, xem trình chiếu, dùng để dạy"; font.pixelSize: 17 }
                                Copy { Layout.fillWidth: true; text: "BiliClass giữ nguyên file nhận về. Trợ giảng đọc cặp Việt–Anh nhận diện được từ chữ hoặc ghi chú slide; không tự dịch lại." }
                                Action { objectName: "receiveChatGPTDeckButton"; text: "Nhận PowerPoint từ ChatGPT"; iconName: "download"; primary: true; enabled: !bridge.busy && !!bridge.chatgptRequest.folder; onClicked: chatgptDeckOpen.open() }
                            }
                        }
                        Action { visible: !bridge.googleTranslation; text: chatgptPromptPreview.visible ? "Ẩn prompt" : "Xem prompt đã cấu hình"; subtle: true; onClicked: chatgptPromptPreview.visible = !chatgptPromptPreview.visible }
                        ScrollView { id: chatgptPromptPreview; visible: false; Layout.fillWidth: true; Layout.preferredHeight: 240; clip: true
                            TextArea { readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 13; text: bridge.chatgptRequest.prompt || ""; color: root.ink }
                        }
                    }
                }

                ScrollView {
                    id: resultScroll; objectName: "resultScroll"
                    anchors.fill: parent; anchors.margins: 28; visible: root.page === "result"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: resultScroll.availableWidth; spacing: 18
                        Action { objectName: "backToLibraryButton"; text: "Trở lại thư viện"; iconName: "back"; subtle: true; implicitHeight: 32; Layout.alignment: Qt.AlignRight; enabled: !bridge.busy; onClicked: root.requestAction(function() { bridge.returnToLibrary() }) }
                        RowLayout {
                            Layout.fillWidth: true
                            ColumnLayout {
                                Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 6
                                Heading { objectName: "resultLessonTitle"; Layout.fillWidth: true; Layout.minimumWidth: 0; text: bridge.lesson.title || "Bài giảng song ngữ" }
                                Copy { Layout.fillWidth: true; Layout.minimumWidth: 0; text: [bridge.lesson.subject, bridge.lesson.education_level + " " + bridge.lesson.grade, bridge.conversionLabel].join(" · ") }
                            }
                            Action { id: resultMoreAction; objectName: "resultMoreButton"; text: "Thao tác khác"; subtle: true; enabled: !bridge.busy; onClicked: resultMoreMenu.popup() }
                            Menu { id: resultMoreMenu; parent: resultMoreAction; x: parent.width - width; y: parent.height
                                MenuItem { objectName: "editLessonDetailsButton"; text: "Sửa nội dung trợ giảng"; enabled: !bridge.busy && !bridge.powerpointState.active; onTriggered: bridge.editLesson(bridge.lesson.id) }
                                MenuItem { text: "Sửa thông tin bài"; enabled: !bridge.busy && !bridge.powerpointState.active; onTriggered: { metadataDialog.lessonData = bridge.lesson; metadataDialog.open() } }
                                MenuItem { objectName: "openConvertedDeckButton"; text: "Mở trong PowerPoint"; enabled: !!bridge.quickResult.path; onTriggered: bridge.openConvertedDeck() }
                                MenuItem { text: root.resultDetails ? "Ẩn thông tin kiểm tra" : "Thông tin kiểm tra"; onTriggered: root.resultDetails = !root.resultDetails }
                                MenuItem { objectName: "shareLessonPackButton"; text: "Gửi gói bài cho giáo viên khác…"; onTriggered: packSave.open() }
                                MenuItem { text: "Chuyển đổi từ tài liệu khác…"; enabled: !bridge.powerpointState.active; onTriggered: root.go("new") }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; spacing: 12
                            Pill { text: "1 · Bài giảng song ngữ"; tone: (((bridge.lesson.slide_quality || {}).counts || {}).FAIL) ? "#a66318" : "#168567" }
                            Copy { text: "→" }
                            Pill { text: bridge.lessonNarration.ready ? "2 · Giọng đọc đã sẵn sàng" : "2 · Giọng đọc (tuỳ chọn)"; tone: bridge.lessonNarration.ready ? "#168567" : root.muted }
                            Item { Layout.fillWidth: true }
                        }
                        Copy { visible: bridge.narrationVariants.length > 1; text: "Bản dùng để dạy / tải PowerPoint"; color: root.ink }
                        Choice {
                            objectName: "lessonNarrationVariantChoice"; visible: bridge.narrationVariants.length > 1
                            Layout.fillWidth: true; Layout.minimumWidth: 0
                            model: bridge.narrationVariants; textRole: "title"; valueRole: "id"
                            currentIndex: Math.max(0, bridge.narrationVariants.map(function(row) { return row.id }).indexOf(bridge.selectedNarrationVariant))
                            enabled: !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.powerpointState.starting
                            onActivated: bridge.selectNarrationVariant(currentValue)
                        }
                        GridLayout {
                            objectName: "resultStatusActions"; Layout.fillWidth: true; columnSpacing: 16; rowSpacing: 10
                            columns: width >= 680 ? 2 : 1
                            Copy { objectName: "resultSaveStatus"; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.alignment: Qt.AlignVCenter; text: bridge.busy ? "Đang hoàn thiện bài giảng…" : ((bridge.lesson.slide_quality || {}).counts || {}).FAIL ? "Bản nháp đã lưu. Một phần nội dung cần kiểm tra trước khi dùng để dạy." : bridge.quickResult.path ? (bridge.lessonNarration.ready ? "Bài giảng và giọng đọc đã lưu. Xem lại nội dung trước khi dùng để dạy." : "Bài giảng song ngữ đã lưu. Bạn có thể tải PowerPoint hoặc tạo thêm giọng đọc.") : "Tạo bản trình chiếu từ nội dung đã lưu."; color: root.ink }
                            RowLayout { Layout.alignment: Qt.AlignRight | Qt.AlignVCenter; spacing: 10; layoutDirection: Qt.RightToLeft
                            Action { objectName: "convertCurrentLessonButton"; visible: !bridge.quickResult.path; text: "Xem trình chiếu"; primary: true; enabled: !bridge.busy; onClicked: bridge.convertCurrentLesson() }
                            Action { objectName: "downloadPresentationButton"; visible: !!bridge.quickResult.path; text: "Tải PowerPoint"; iconName: "download"; enabled: !bridge.busy; onClicked: presentationSave.open() }
                            Action { objectName: "useConvertedLessonButton"; visible: !!bridge.quickResult.path; text: "Dùng để dạy"; primary: true; enabled: !bridge.busy && !bridge.previewBusy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.powerpointState.starting; onClicked: root.prepareTeaching() }
                            }
                        }
                        RowLayout { Layout.fillWidth: true; visible: root.resultDetails
                            Copy { objectName: "lessonReviewSummary"; Layout.fillWidth: true; color: "#a66318"; text: {
                                const counts = (bridge.lesson.slide_quality || {}).counts || {};
                                const missing = (bridge.quickResult.missing || []).length;
                                return counts.FAIL ? counts.FAIL + " slide cần sửa trước khi dùng để dạy." : missing ? missing + " phần còn thiếu nội dung song ngữ." : counts.CHECK ? counts.CHECK + " slide cần rà soát nội dung trước khi dạy." : bridge.lesson.external_deck && !bridge.lesson.slide_quality ? "Bài giảng cần được rà soát trước khi dạy." : "Xem lại nội dung và lời đọc trước khi dạy."
                            } }
                            Action { objectName: "resultDetailsButton"; text: root.resultDetails ? "Ẩn chi tiết" : "Xem chi tiết"; subtle: true; implicitHeight: 32; onClicked: root.resultDetails = !root.resultDetails }
                        }
                        ProgressBar { visible: bridge.busy; indeterminate: true; Layout.fillWidth: true }
                        Surface {
                            objectName: "lessonSlidePreview"; Layout.fillWidth: true; implicitHeight: Math.max(260, Math.min(560, (root.height - 150) * .62)); color: "#e9eef5"
                            Image { objectName: "convertedSlideImage"; anchors.fill: parent; anchors.margins: 6; source: bridge.quickResult.image || ""; fillMode: Image.PreserveAspectFit; asynchronous: true; cache: true; sourceSize.width: 1600; opacity: bridge.previewBusy ? .6 : 1 }
                            BusyIndicator { anchors.centerIn: parent; running: bridge.previewBusy; visible: running }
                            ColumnLayout {
                                visible: !bridge.quickResult.image; anchors.centerIn: parent; width: parent.width - 70; spacing: 12
                                Caption { text: bridge.busy ? "BiliClass đang tạo bài giảng…" : bridge.quickResult.path ? "Bản trình chiếu đã tạo" : "Từ tài liệu của thầy cô đến bài giảng song ngữ"; font.pixelSize: 19; Layout.alignment: Qt.AlignHCenter }
                                Copy { text: bridge.quickResult.preview_note || "PowerPoint giữ thiết kế gốc. Tài liệu và ảnh được chuyển thành slide theo mẫu BiliClass."; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                            }
                        }
                        RowLayout {
                            objectName: "resultSlideNavigation"; Layout.fillWidth: true; visible: !!bridge.quickResult.path
                            Item { Layout.fillWidth: true }
                            Action { objectName: "resultPreviousSlide"; text: "‹"; implicitHeight: 34; enabled: !bridge.busy && !bridge.powerpointState.active && !bridge.powerpointState.starting && (bridge.quickResult.slide || 1) > 1; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide - 1) }
                            Copy { objectName: "resultSlideCounter"; text: "Slide " + (bridge.quickResult.slide || 1) + " / " + (bridge.quickResult.total || 0); color: root.ink }
                            Action { objectName: "resultNextSlide"; text: "›"; implicitHeight: 34; enabled: !bridge.busy && !bridge.powerpointState.active && !bridge.powerpointState.starting && (bridge.quickResult.slide || 1) < bridge.quickResult.total; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide + 1) }
                            Item { Layout.fillWidth: true }
                        }
                        Surface {
                            objectName: "lessonNarrationPanel"; visible: !!bridge.quickResult.path
                            Layout.fillWidth: true; implicitHeight: narrationForm.height + 28
                            ColumnLayout {
                                id: narrationForm; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; spacing: 8
                                RowLayout { Layout.fillWidth: true
                                    Caption { Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap; text: "Tạo giọng đọc · không bắt buộc" }
                                    Item { Layout.fillWidth: true }
                                    Copy { objectName: "lessonNarrationState"; Layout.maximumWidth: narrationForm.width * 0.55; text: bridge.lessonNarration.title || bridge.lessonNarration.label || "Chưa có giọng đọc"; color: bridge.lessonNarration.ready ? "#168567" : root.muted }
                                }
                                GridLayout { Layout.fillWidth: true; columns: width >= 640 ? 4 : 2; columnSpacing: 10; rowSpacing: 8
                                    Choice { objectName: "lessonNarrationVoiceChoice"; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.preferredWidth: 290
                                        model: bridge.multilingualVoices; textRole: "name"; valueRole: "id"
                                        currentIndex: Math.max(0, bridge.multilingualVoices.map(function(v) { return v.id }).indexOf(root.narrationVoice))
                                        enabled: !bridge.narrationBusy; onActivated: { bridge.stopSpeech(); root.narrationVoice = currentValue }
                                    }
                                    Choice { objectName: "lessonNarrationRateChoice"; Layout.preferredWidth: 100; model: ["82%", "88%", "94%", "100%", "106%", "112%", "118%"]
                                        currentIndex: root.narrationRate + 3; enabled: !bridge.narrationBusy
                                        onActivated: { bridge.stopSpeech(); root.narrationRate = currentIndex - 3 }
                                    }
                                    Action { objectName: "previewLessonNarrationVoice"; text: bridge.voiceUiState.phase === "preparing" ? "Đang chuẩn bị…" : "Nghe thử"; iconName: "play"; enabled: !!root.narrationVoice && !bridge.narrationBusy
                                        onClicked: bridge.previewMultilingualVoice(root.narrationVoice, root.narrationRate, "Xin chào các em. Let's learn together.")
                                    }
                                    Action { objectName: "stopLessonNarrationPreview"; text: "Dừng nghe"; onClicked: bridge.stopSpeech() }
                                }
                                Flow { Layout.fillWidth: true; spacing: 10
                                    ButtonGroup { id: narrationLanguages }
                                    RadioButton { objectName: "narrationEnglish"; text: "Tiếng Anh · " + ((root.narrationDrafts.en || {}).label || "Chưa tạo"); ButtonGroup.group: narrationLanguages; checked: root.narrationMode === "en"; enabled: !bridge.narrationBusy; onClicked: root.chooseNarrationMode("en") }
                                    RadioButton { objectName: "narrationVietnamese"; text: "Tiếng Việt · " + ((root.narrationDrafts.vi || {}).label || "Chưa tạo"); ButtonGroup.group: narrationLanguages; checked: root.narrationMode === "vi"; enabled: !bridge.narrationBusy; onClicked: root.chooseNarrationMode("vi") }
                                    RadioButton { objectName: "narrationBoth"; text: "Việt + Anh · " + ((root.narrationDrafts.both || {}).label || "Chưa tạo"); ButtonGroup.group: narrationLanguages; checked: root.narrationMode === "both"; enabled: !bridge.narrationBusy; onClicked: root.chooseNarrationMode("both") }
                                    Action { objectName: "createLessonNarrationButton"; primary: true; text: bridge.narrationBusy ? "Đang tạo giọng…" : root.narrationDraft.ready ? "Đã tạo đủ giọng" : root.narrationDraft.phase === "checking" ? "Đang kiểm tra…" : root.narrationDraft.phase === "partial" ? "Tiếp tục tạo giọng" : "Tạo giọng đọc"; enabled: !!root.narrationDraft.canCreate && !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.powerpointState.starting; onClicked: bridge.createLessonNarrationWithVoice(root.narrationMode, root.narrationVoice, root.narrationRate) }
                                    Action { objectName: "cancelLessonNarrationButton"; text: "Dừng"; visible: !!bridge.lessonNarration.running; onClicked: bridge.cancelLessonNarration() }
                                }
                                Copy { Layout.fillWidth: true; font.pixelSize: 12; text: "Một bài có thể lưu nhiều bản giọng. Chọn bản cần dùng khi dạy hoặc tải. Bản Song ngữ có nút Việt, Anh và đọc chung trên slide."; color: root.muted }
                                CheckBox { objectName: "embedPresentationVoice"; visible: !!bridge.selectedNarrationVariant; checked: root.includeDownloadVoice; onClicked: root.includeDownloadVoice = checked; text: "Tải PowerPoint kèm bản giọng đã chọn · lời đọc hiện rõ trên slide" }
                                RowLayout { Layout.fillWidth: true; visible: !!bridge.lessonNarration.running
                                    ProgressBar { objectName: "lessonNarrationProgressBar"; Layout.fillWidth: true; from: 0; to: 100; value: bridge.lessonNarration.percent || 0 }
                                    Caption { objectName: "lessonNarrationPercent"; text: (bridge.lessonNarration.percent || 0) + "%" }
                                }
                                RowLayout { Layout.fillWidth: true; visible: !!bridge.narrationPreparation.lesson_id && (bridge.lessonNarration.running || bridge.narrationClock.elapsedSeconds > 0)
                                    Copy { objectName: "lessonNarrationElapsed"; text: "Thời gian tạo giọng: " + root.durationText(bridge.narrationClock.elapsedSeconds); color: root.ink; font.pixelSize: 12 }
                                    Item { Layout.fillWidth: true }
                                    Copy { text: (bridge.lessonNarration.complete || 0) + " / " + (bridge.lessonNarration.total || 0) + " đoạn sẵn sàng"; color: root.muted; font.pixelSize: 12 }
                                }
                                Copy { objectName: "narrationPreparationStatus"; Layout.fillWidth: true; visible: !!bridge.lessonNarration.message; text: bridge.lessonNarration.message || ""; color: root.muted; font.pixelSize: 12 }
                                Rectangle {
                                    objectName: "narrationReadyNextStep"; visible: !!root.narrationDraft.ready && !bridge.narrationBusy
                                    Layout.fillWidth: true; implicitHeight: narrationNextContent.implicitHeight + 28
                                    radius: 10; color: "#eef8f4"; border.color: "#d2eade"
                                    ColumnLayout { id: narrationNextContent; anchors.fill: parent; anchors.margins: 14; spacing: 9
                                        Caption { text: "Giọng đọc đã sẵn sàng · Bước tiếp theo"; color: "#168567"; Layout.fillWidth: true }
                                        Copy { text: root.narrationDraft.title || ""; color: root.ink; Layout.fillWidth: true }
                                        Flow { Layout.fillWidth: true; spacing: 10
                                            Action { objectName: "continueAfterNarrationButton"; text: "Tiếp tục: chuẩn bị dạy"; primary: true; enabled: !bridge.busy && !bridge.powerpointState.active && !bridge.powerpointState.starting; onClicked: root.prepareTeaching(root.narrationDraft.id) }
                                            Action { objectName: "downloadAfterNarrationButton"; text: "Tải PowerPoint"; iconName: "download"; enabled: !bridge.busy; onClicked: { if (root.narrationDraft.id !== bridge.selectedNarrationVariant) bridge.selectNarrationVariant(root.narrationDraft.id); if (bridge.selectedNarrationVariant === root.narrationDraft.id) presentationSave.open() } }
                                        }
                                    }
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; visible: !!bridge.powerpointState.active || !!bridge.powerpointState.starting
                            Copy { text: bridge.powerpointState.message || "Đang trình chiếu"; Layout.fillWidth: true }
                            Action { text: "Slide trước"; enabled: bridge.powerpointState.active; onClicked: bridge.navigatePowerPoint("previous") }
                            Action { text: "Slide tiếp"; enabled: bridge.powerpointState.active; onClicked: bridge.navigatePowerPoint("next") }
                            Action { text: "Đọc tiếng Anh"; enabled: bridge.powerpointState.active && !bridge.busy && !!bridge.audioAvailable.en; onClicked: bridge.readSlideEnglish() }
                            Action { text: "Đọc tiếng Việt"; enabled: bridge.powerpointState.active && !bridge.busy && !!bridge.audioAvailable.vi; onClicked: bridge.speakSegment("vi") }
                            Action { objectName: "resultReadBoth"; text: "Đọc Việt–Anh chung"; enabled: bridge.powerpointState.active && !bridge.busy && !!bridge.audioAvailable.both; onClicked: bridge.readBothLanguages() }
                            Action { text: "Đóng trình chiếu"; onClicked: bridge.stopPowerPoint() }
                        }
                        RowLayout { visible: bridge.powerpointState.active; Layout.fillWidth: true
                            Copy { text: bridge.englishReaderState.message; Layout.fillWidth: true }
                            Action { text: bridge.englishReaderState.state === "paused" ? "Tiếp tục" : "Tạm dừng"; enabled: ["reading", "preparing", "paused"].indexOf(bridge.englishReaderState.state) >= 0; onClicked: bridge.englishReaderState.state === "paused" ? bridge.resumeEnglish() : bridge.pauseEnglish() }
                            Action { text: "Dừng đọc"; onClicked: bridge.stopSpeech() }
                            Action { text: "Đọc lại"; enabled: !bridge.busy; onClicked: bridge.readSlideEnglish() }
                        }
                        Surface {
                            objectName: "lessonDetailsPanel"; visible: root.resultDetails
                            Layout.fillWidth: true; implicitHeight: resultInfo.height + 32
                            ColumnLayout {
                                id: resultInfo; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16; spacing: 10
                                RowLayout { Layout.fillWidth: true; visible: !!bridge.lesson.external_deck
                                    Copy { Layout.fillWidth: true; text: (bridge.lesson.slide_quality || {}).counts ? "Kiểm tra slide: " + (bridge.lesson.slide_quality.counts.FAIL || 0) + " cần sửa · " + (bridge.lesson.slide_quality.counts.CHECK || 0) + " cần rà soát" : "Chưa kiểm tra toàn bộ slide và lời đọc" }
                                    Action { objectName: "inspectSlideQualityButton"; text: bridge.lesson.slide_quality && bridge.lesson.slide_quality.counts ? "Kiểm tra lại" : "Kiểm tra toàn bộ slide"; enabled: !bridge.busy && !bridge.powerpointState.active; onClicked: bridge.inspectSlideQuality() }
                                }
                                Copy { visible: !!bridge.narrationPreparation.total; text: "Giọng đọc: " + (bridge.narrationPreparation.complete || 0) + "/" + bridge.narrationPreparation.total + " đoạn đã sẵn sàng"; Layout.fillWidth: true }
                                Copy { objectName: "currentSlideQuality"; visible: !!bridge.lesson.slide_quality && !!bridge.quickResult.path; Layout.fillWidth: true; color: "#a66318"; text: { const rows = (bridge.lesson.slide_quality || {}).slides || []; const row = rows[(bridge.quickResult.slide || 1) - 1]; return row ? "Slide " + row.slide + ": " + (row.status === "FAIL" ? "Cần sửa" : row.status === "CHECK" ? "Cần rà soát" : "Đã kiểm tra") + "\n" + row.issues.map(function(i) { return i.message || i.code }).join("\n") : "" } }
                                Copy { visible: !!bridge.lesson.conversion_format && (bridge.lesson.questions || []).length > 0; text: (bridge.lesson.questions || []).filter(function(q) { return !q.approved }).length + " câu hỏi nháp · xem và duyệt riêng trong Chỉnh sửa chi tiết → Trợ giảng & Quiz."; Layout.fillWidth: true }
                                Copy { Layout.fillWidth: true; text: (bridge.quickResult.missing || []).length ? "Chưa đủ song ngữ: " + bridge.quickResult.missing.slice(0, 8).join(", ") : "Kiểm tra thuật ngữ, số liệu và ý nghĩa trong bản trình chiếu. Trợ giảng, quiz và giọng đọc có thể bổ sung khi cần." }
                                Copy { objectName: "returnedDeckReviewNotes"; Layout.fillWidth: true; visible: !!bridge.slideQualityDetails; text: bridge.slideQualityDetails; color: "#a66318" }
                                Copy { Layout.fillWidth: true; visible: (((bridge.lesson.source || {}).warnings || []).length > 0); text: ((bridge.lesson.source || {}).warnings || []).slice(0, 3).join("\n") }
                            }
                        }
                    }
                }

                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 23; spacing: 15; visible: root.page === "editor"; enabled: !bridge.busy
                    RowLayout {
                        Layout.fillWidth: true
                        ColumnLayout { spacing: 5; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.maximumWidth: 310
                            Heading { text: bridge.lesson.title || "Chọn một bài học"; font.pixelSize: 22; Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 1 }
                            Copy { text: (bridge.lesson.subject || "") + " · " + (bridge.lesson.education_level || "") + " " + (bridge.lesson.grade || ""); font.pixelSize: 11 } }
                        Item { Layout.fillWidth: true }
                        Pill { text: root.dirty ? "Chưa lưu thay đổi" : "Đã lưu trên máy"; tone: root.dirty ? "#ad651d" : "#168567" }
                        Action { text: "Lịch sử"; enabled: !!bridge.lesson.id; onClicked: root.requestAction(function() { historyDialog.open() }) }
                        Action { objectName: "previewButton"; text: root.keepSourceDesign ? "So sánh gốc / song ngữ" : "Xem trước"; iconName: "view"; enabled: !!bridge.lesson.id && !bridge.busy; onClicked: root.requestAction(function() { if (root.keepSourceDesign) bridge.comparePowerPoint(1); else { root.rescue = false; preview.show() } }) }
                        Action { text: "PPTX"; enabled: !bridge.busy; onClicked: root.requestAction(function() { deckSave.open() }) }
                        Action { text: "Gói bài"; primary: true; enabled: !!bridge.lesson.id && !bridge.busy; onClicked: root.requestAction(function() { packSave.open() }) }
                    }
                    Copy { visible: ((bridge.lesson.source || {}).warnings || []).length > 0; text: ((bridge.lesson.source || {}).warnings || []).join("\n"); color: "#ad651d"; font.pixelSize: 11; Layout.fillWidth: true }
                    RowLayout {
                        Layout.fillWidth: true; spacing: 12
                        CheckBox { objectName: "keepPowerPointDesign"; text: "Giữ thiết kế gốc"; visible: bridge.powerpointAvailable && !bridge.lesson.external_deck; checked: root.keepSourceDesign; onClicked: { let style = checked ? "source" : "template"; root.requestAction(function() { bridge.setPresentationStyle(style) }) } }
                        Choice { id: presetChoice; objectName: "presetChoice"; visible: !root.keepSourceDesign; model: ["Chuẩn lớp học", "Trực quan", "Luyện tập & tương tác"]; currentIndex: Math.max(0, ["standard", "visual", "practice"].indexOf(bridge.lesson.teaching_preset || "standard")); Layout.preferredWidth: 195; onActivated: bridge.setTeachingPreset(["standard", "visual", "practice"][currentIndex]) }
                        Action { objectName: "editorTemplatesButton"; text: "Mẫu"; visible: !root.keepSourceDesign; onClicked: root.requestAction(function() { templateGallery.forCreation = false; templateGallery.preset = bridge.lesson.teaching_preset || "standard"; templateGallery.level = bridge.lesson.level || 0; templateGallery.layout = bridge.lesson.layout || "line_pair"; templateGallery.open() }) }
                        Pill { visible: !!bridge.lesson.conversion_format; text: bridge.conversionLabel }
                        Action { text: "Trợ giảng & Quiz"; objectName: "teachingButton"; onClicked: root.requestAction(function() { teachingDialog.open() }) }
                        Item { Layout.fillWidth: true }
                        Action { objectName: "readinessButton"; text: "Chuẩn bị lên lớp"; onClicked: root.requestAction(function() { bridge.refreshReadiness(); readinessDialog.open() }) }
                    }
                    RowLayout { visible: bridge.powerpointAvailable; Layout.fillWidth: true; spacing: 9
                        Copy { text: bridge.powerpointState.active ? bridge.powerpointState.message : root.keepSourceDesign ? "Giữ thiết kế gốc · theo cách chuyển đổi đã chọn · trợ giảng dùng nội dung đã duyệt" : "Nguồn PowerPoint · mở bản chỉ đọc"; Layout.fillWidth: true; font.pixelSize: 11 }
                        Action { objectName: "openPowerPointButton"; text: root.keepSourceDesign ? "Trình chiếu song ngữ" : "Chiếu bản gốc"; visible: !bridge.powerpointState.active; enabled: !!bridge.lesson.id && !bridge.busy; implicitHeight: 32; onClicked: root.requestAction(function() { if (root.keepSourceDesign) bridge.startBilingualPowerPoint(); else bridge.startPowerPoint() }) }
                        Action { text: "Slide trước"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.navigatePowerPoint("previous") }
                        Action { text: "Đến slide đoạn này"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.navigatePowerPoint("goto") }
                        Action { text: "Slide tiếp"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.navigatePowerPoint("next") }
                        Action { text: "Đóng PowerPoint"; visible: bridge.powerpointState.active; implicitHeight: 32; onClicked: bridge.stopPowerPoint() }
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
                                Copy { text: bridge.approvedCount + "/" + ((bridge.lesson.segments || []).length) + " đoạn đã duyệt"; font.pixelSize: 11 }
                                ProgressBar { Layout.fillWidth: true; value: bridge.approvedCount / Math.max(1, (bridge.lesson.segments || []).length) }
                                ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: bridge.lesson.segments || []
                                    delegate: ItemDelegate {
                                        required property var modelData; required property int index
                                        width: ListView.view.width; height: 84
                                        onClicked: { let target = index; root.requestAction(function() { bridge.selectSegment(target) }) }
                                        background: Rectangle { color: index === bridge.segmentIndex ? "#eaf3ff" : parent.hovered ? "#f5f8fc" : "transparent"; radius: 9; border.color: index === bridge.segmentIndex ? "#a8cdff" : "transparent" }
                                        contentItem: ColumnLayout { spacing: 6
                                            Label { text: (index + 1) + ". " + modelData.locator; color: index === bridge.segmentIndex ? root.blue : root.ink; font.pixelSize: 11; font.weight: Font.DemiBold; elide: Text.ElideRight; Layout.fillWidth: true }
                                            Copy { text: (modelData.vi || modelData.en).replace(/\n/g, " "); maximumLineCount: 2; elide: Text.ElideRight; font.pixelSize: 10; Layout.fillWidth: true }
                                            Copy { text: modelData.approved ? "✓ Đã duyệt" : modelData.vi && modelData.en ? "● Chờ duyệt" : "○ Chưa đủ song ngữ"; font.pixelSize: 9; color: modelData.approved ? "#168567" : root.muted }
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
                                    Pill { text: root.dirty ? "Đang chỉnh sửa" : bridge.segment.approved ? "Đã duyệt" : "Bản nháp"; tone: bridge.segment.approved && !root.dirty ? "#168567" : "#9c651b" }
                                }
                                RowLayout { Layout.fillWidth: true; spacing: 7
                                    Action { text: "Thông tin bài"; implicitHeight: 30; subtle: true; onClicked: root.requestAction(function() { metadataDialog.open() }) }
                                    Action { text: "Tệp nguồn"; implicitHeight: 30; subtle: true; visible: !!bridge.lesson.source; onClicked: bridge.openSourceCopy() }
                                    Action { text: "Nguồn"; implicitHeight: 30; subtle: true; onClicked: sourceDialog.open() }
                                    Action { text: "Tách đoạn"; implicitHeight: 30; subtle: true; onClicked: splitDialog.open() }
                                    Item { Layout.fillWidth: true }
                                }
                                RowLayout { Layout.fillWidth: true; visible: !root.keepSourceDesign
                                    Caption { text: "Loại slide" }
                                    Choice { objectName: "slideTypeChoice"; model: bridge.slideTypes; textRole: "label"; valueRole: "id"; Layout.fillWidth: true; currentIndex: Math.max(0, bridge.slideTypes.map(function(item) { return item.id }).indexOf(bridge.currentSlideType)); onActivated: { let selected = currentValue; root.requestAction(function() { bridge.setSlideType(selected) }) } }
                                }
                                RowLayout { Layout.fillWidth: true; Caption { text: "VI   Tiếng Việt" } Item { Layout.fillWidth: true }  }
                                ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 56; clip: true
                                    TextArea { id: viEdit; objectName: "viEditor"; wrapMode: TextEdit.Wrap; selectByMouse: true; color: root.ink; font.pixelSize: 15; padding: 13; onTextChanged: root.edited(); background: Rectangle { radius: 9; color: "#f8fafd"; border.color: parent.activeFocus ? root.blue : root.line } }
                                }
                                RowLayout { Layout.fillWidth: true; Caption { text: "EN   English"; color: root.blue } Item { Layout.fillWidth: true }
                                     }
                                ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 56; clip: true
                                    TextArea { id: enEdit; objectName: "enEditor"; wrapMode: TextEdit.Wrap; selectByMouse: true; color: "#1855a6"; font.pixelSize: 15; padding: 13; placeholderText: "Lời đọc tiếng Anh tương ứng với slide…"; onTextChanged: root.edited(); background: Rectangle { radius: 9; color: "#f4f8ff"; border.color: parent.activeFocus ? root.blue : "#d4e4fc" } }
                                }
                                Action { text: "Tìm bản dịch gần giống đã duyệt"; iconName: "search"; implicitHeight: 30; enabled: !bridge.busy && !lockedCheck.checked; onClicked: { root.translationSource = bridge.segment.source_language || bridge.lesson.source_language || "vi"; if (!root.dirty || root.save(false)) bridge.suggestSimilar(root.translationSource) } }
                                Copy { text: "Kiểm tra lời đọc, thuật ngữ, số liệu và công thức trước khi duyệt. Chỉnh lời đọc ở đây không thay chữ trong PowerPoint đã nhận."; font.pixelSize: 10; Layout.fillWidth: true }
                                Copy { visible: bridge.reviewWarnings.length > 0; text: bridge.reviewWarnings.join("\n"); color: "#ad651d"; font.pixelSize: 11; Layout.fillWidth: true }
                                RowLayout {
                                    Layout.fillWidth: true
                                    CheckBox { id: lockedCheck; text: "Khóa nội dung"; font.pixelSize: 11; onToggled: root.edited() }
                                    Item { Layout.fillWidth: true }
                                    Action { objectName: "saveDraftButton"; text: "Lưu nháp"; iconName: "save"; enabled: !!bridge.lesson.id; onClicked: root.save(false) }
                                    Action { objectName: "approveButton"; text: "✓  Duyệt đoạn"; primary: true; enabled: !!bridge.lesson.id && enEdit.text.trim() !== "" && viEdit.text.trim() !== ""; onClicked: root.save(true) }
                                }
                            }
                        }
                    }
                    Copy { text: root.statusLabel(bridge.status) + "  ·  Tự lưu bản nháp sau khi ngừng nhập" + (root.keepSourceDesign ? "  ·  Xem bài song ngữ bằng PowerPoint" : "  ·  Xem trước hiện hỗ trợ văn bản"); font.pixelSize: 10; Layout.fillWidth: true }
                }

                ClassroomPage { objectName: "classroomPage"; anchors.fill: parent; anchors.margins: 26; visible: root.page === "classroom"; classroom: root.classroom; bridge: root.bridgeRef; onRequestLibrary: root.go("library"); onRequestPreparation: { bridge.refreshReadiness(); readinessDialog.open() } onRequestEditor: bridge.editLesson(bridge.lesson.id); onRequestReports: root.go("reports") }
                ReportsPage { objectName: "reportsPage"; anchors.fill: parent; anchors.margins: 26; visible: root.page === "reports"; classroom: root.classroom; bridge: root.bridgeRef; onRequestClassroom: root.go("classroom") }

                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 30; spacing: 16
                    visible: root.page === "reference"
                    Heading { text: "Thuật ngữ & kiến thức" }
                    Copy { text: "Tra cứu và quản lý nội dung đã lưu khi cần. Không cần cấu hình kho dữ liệu để chuyển đổi bài giảng."; Layout.fillWidth: true }
                    RowLayout {
                        Action { objectName: "teacherDataTab"; text: "Thuật ngữ của tôi"; primary: root.referenceTab === 0; onClicked: root.referenceTab = 0 }
                        Action { objectName: "foundationDataTab"; text: "Kiến thức có nguồn"; primary: root.referenceTab === 1; onClicked: root.referenceTab = 1 }
                    }
                    Item {
                        Layout.fillWidth: true; Layout.fillHeight: true
                ScrollView {
                    anchors.fill: parent; anchors.margins: 0; visible: root.referenceTab === 0; clip: true; contentWidth: availableWidth
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
                                RowLayout { CheckBox { id: termLocked; checked: true; text: "Đánh dấu thuật ngữ ưu tiên"; font.pixelSize: 12 } Item { Layout.fillWidth: true } Action { text: "Lưu thuật ngữ"; primary: true; onClicked: bridge.saveTerm(termSubject.text, termVi.text, termEn.text, termLocked.checked) } }
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
                                    Action { text: "Sửa"; iconName: "edit"; subtle: true; onClicked: { termSubject.text = modelData.subject; termVi.text = modelData.vi; termEn.text = modelData.en; termLocked.checked = !!modelData.locked } }
                                    Action { text: "Xóa"; iconName: "delete"; subtle: true; onClicked: { deleteTermDialog.termId = modelData.id; deleteTermDialog.open() } }
                                }
                            }
                        }
                        RowLayout { visible: root.filteredTerms.length > 20; Layout.fillWidth: true
                            Action { text: "Trước"; enabled: root.termPage > 1; onClicked: root.termPage-- }
                            Copy { text: "Trang " + root.termPage + " / " + Math.max(1, Math.ceil(root.filteredTerms.length / 20)) }
                            Action { text: "Tiếp"; enabled: root.termPage * 20 < root.filteredTerms.length; onClicked: root.termPage++ }
                        }
                    }
                }

                ScrollView {
                    anchors.fill: parent; anchors.margins: 0; visible: root.referenceTab === 1; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout { Layout.fillWidth: true
                            ColumnLayout { Layout.fillWidth: true; spacing: 6
                                Copy { text: "Tra cứu nền tảng offline, xem nguồn chính thức và chọn từng thuật ngữ để đưa vào kho riêng của thầy cô."; Layout.fillWidth: true }
                            }
                            Action { text: "Cài gói kiến thức"; iconName: "upload"; primary: true; onClicked: knowledgeOpen.open() }
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
                            Pill { text: bridge.knowledgeStats.sources + " nguồn"; tone: "#168567" }
                            Pill { text: bridge.knowledgeStats.packs + " gói"; tone: "#8a5a00" }
                            Item { Layout.fillWidth: true }
                        }
                        Copy { text: "Ưu tiên: bản thầy cô đã duyệt → kiến thức nền → dữ liệu online có nguồn. Bản dịch từ kho nền vẫn cần duyệt. ‘Đưa vào kho riêng’ lưu cách dùng từ cho môn này."; Layout.fillWidth: true }
                        Repeater { model: root.knowledgeResults
                            delegate: Surface { required property var modelData; Layout.fillWidth: true; implicitHeight: knowledgeCard.implicitHeight + 30
                                ColumnLayout { id: knowledgeCard; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 15; spacing: 7
                                    RowLayout { Layout.fillWidth: true
                                        Pill { text: modelData.subject; tone: root.blue; Layout.maximumWidth: 230 }
                                        Pill { text: modelData.kind; tone: "#8a5a00" }
                                        Item { Layout.fillWidth: true }
                                        Action { text: "Đưa vào kho riêng"; iconName: "save"; subtle: true; onClicked: bridge.promoteKnowledgeTerm(modelData.id) }
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
                    onRequestLogo: logoOpen.open()
                }
            }
            Rectangle {
                objectName: "applicationFooter"
                Layout.fillWidth: true; implicitHeight: footerContent.implicitHeight + 16
                color: bridge.error ? "#fff0eb" : bridge.busy ? "#eaf3ff" : "#ffffff"
                RowLayout {
                    id: footerContent
                    anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 25; anchors.rightMargin: 25; spacing: 18
                    RowLayout { Layout.fillWidth: true; spacing: 10
                        BusyIndicator { visible: bridge.busy; running: bridge.busy; Layout.preferredWidth: 23; Layout.preferredHeight: 23 }
                        Label { id: statusMessage; objectName: "applicationStatusMessage"; text: (root.page === "chatgpt" || bridge.browserState.running || bridge.browserState.phase === "error" && bridge.message === bridge.browserState.message) && (bridge.googleTranslation || bridge.browserAI.automatic) ? bridge.browserState.displayMessage : bridge.message || "Sẵn sàng · Dữ liệu bài giảng được lưu tại máy"; color: bridge.error ? "#b14828" : root.muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                        Action { objectName: "applicationCancel"; visible: bridge.busy && !conversionCancel.visible; text: "Dừng tác vụ"; implicitHeight: 30; onClicked: bridge.cancelJob() }
                    }
                }
            }
        }
    }
    FileDialog { id: documentOpen; objectName: "creationFileDialog"; title: "Chọn tài liệu bài giảng"; nameFilters: ["Tài liệu (*.pptx *.docx *.pdf *.txt *.png *.jpg *.jpeg)"]; onAccepted: root.acceptInputDocuments([selectedFile.toString()]) }
    FileDialog { id: customTemplateOpen; title: "Chọn mẫu PowerPoint có khung chữ chỉnh sửa được"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.selectCustomTemplate(selectedFile.toString()) }
    FileDialog { id: chatgptDeckOpen; title: "Nhận PowerPoint đã tải từ ChatGPT"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.receiveChatGPTDeck(selectedFile.toString()) }
    FileDialog { id: logoOpen; title: "Chọn logo trường"; nameFilters: ["Ảnh (*.png *.jpg *.jpeg)"]; onAccepted: bridge.saveSchoolLogo(selectedFile.toString()) }
    FileDialog { id: packOpen; title: "Nhập gói bài BiliClass"; nameFilters: ["BiliClass (*.biliclass)"]; onAccepted: bridge.importPack(selectedFile.toString()) }
    FileDialog { id: deckSave; title: "Xuất PowerPoint song ngữ mới"; fileMode: FileDialog.SaveFile; defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.exportPowerPoint(selectedFile.toString()) }
    FileDialog { id: presentationSave; objectName: "presentationSaveDialog"; title: "Tải PowerPoint · " + (bridge.lessonNarration.title || "Không kèm giọng đọc"); fileMode: FileDialog.SaveFile; currentFolder: bridge.downloadsDirectory; defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"]; onVisibleChanged: if (visible) selectedFile = bridge.presentationDownloadSuggestion(!!bridge.selectedNarrationVariant && root.includeDownloadVoice); onAccepted: bridge.downloadPresentationWithVoice(selectedFile.toString(), !!bridge.selectedNarrationVariant && root.includeDownloadVoice) }
    FileDialog { id: packSave; title: "Xuất gói bài BiliClass"; fileMode: FileDialog.SaveFile; defaultSuffix: "biliclass"; nameFilters: ["BiliClass (*.biliclass)"]; onAccepted: bridge.exportPack(selectedFile.toString()) }
    FileDialog { id: knowledgeOpen; title: "Cài gói kiến thức có nguồn"; nameFilters: ["BiliClass Knowledge (*.biliknowledge)"]; onAccepted: bridge.installKnowledgePack(selectedFile.toString()) }
    FileDialog { id: backupOpen; title: "Khôi phục vào thư mục mới"; nameFilters: ["BiliClass Backup (*.bcbackup)"]; onAccepted: bridge.restoreLibrary(selectedFile.toString()) }
    FolderDialog { id: libraryOpen; title: "Chọn thư mục thư viện đã khôi phục"; onAccepted: root.requestAction(function() { bridge.openLibrary(libraryOpen.selectedFolder.toString()) }) }
    Dialog {
        id: wholeLessonReview; objectName: "wholeLessonReview"; anchors.centerIn: parent; modal: true
        title: "Chuẩn bị dạy"; width: Math.min(660, root.width - 80)
        ColumnLayout {
            width: parent.width; spacing: 13
            Caption { text: bridge.lesson.title || "Bài giảng"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            Copy { text: (bridge.quickResult.total || 0) + " slide · Chọn bản giọng trước khi mở trình chiếu"; Layout.fillWidth: true }
            Choice {
                objectName: "teachingNarrationVariantChoice"; Layout.fillWidth: true; Layout.minimumWidth: 0
                model: bridge.narrationVariants; textRole: "title"; valueRole: "id"
                currentIndex: Math.max(0, bridge.narrationVariants.map(function(row) { return row.id }).indexOf(bridge.selectedNarrationVariant))
                enabled: !bridge.busy && !bridge.narrationBusy
                onActivated: bridge.selectNarrationVariant(currentValue)
            }
            Copy { objectName: "teachingNarrationSummary"; Layout.fillWidth: true; color: bridge.selectedNarrationVariant && !bridge.lessonNarration.ready ? "#a66318" : "#168567"; text: !bridge.selectedNarrationVariant ? "Dạy bằng PowerPoint không kèm giọng đọc." : bridge.lessonNarration.ready ? bridge.lessonNarration.title + ". Giọng chỉ phát khi thầy cô bấm nút đọc." : "Bản giọng này chưa hoàn tất. Quay lại tạo tiếp hoặc chọn bản khác." }
            Copy { Layout.fillWidth: true; text: bridge.quickResult.draft ? "Xác nhận thầy cô đã kiểm tra nội dung Việt–Anh, thuật ngữ, số liệu và bố cục. BiliClass sẽ lưu xác nhận và mở trình chiếu." : "Bài đã được duyệt. Bắt đầu dạy để mở trình chiếu; các nút đọc trên mascot sẽ hoạt động theo bản giọng đã chọn." }
            Copy { objectName: "teachingLayoutBlocker"; visible: (((bridge.lesson.slide_quality || {}).counts || {}).FAIL || 0) > 0; Layout.fillWidth: true; color: "#a66318"; text: "Bản PowerPoint còn " + ((((bridge.lesson.slide_quality || {}).counts || {}).FAIL) || 0) + " slide cần sửa trước khi dạy. Chọn Xem lại bài để kiểm tra." }
            ScrollView {
                visible: (bridge.quickResult.warnings || []).length > 0; Layout.fillWidth: true; Layout.preferredHeight: 150; clip: true; contentWidth: availableWidth
                Copy { width: parent.width; text: (bridge.quickResult.warnings || []).join("\n\n"); color: "#a66318" }
            }
            RowLayout {
                Layout.fillWidth: true; Item { Layout.fillWidth: true }
                Action { text: "Xem lại bài"; onClicked: wholeLessonReview.close() }
                Action { objectName: "confirmWholeLessonButton"; text: bridge.quickResult.draft ? "Đã kiểm tra · Bắt đầu dạy" : "Bắt đầu dạy"; primary: true; enabled: !bridge.busy && !bridge.previewBusy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.powerpointState.starting && (!bridge.selectedNarrationVariant || bridge.lessonNarration.ready) && !((((bridge.lesson.slide_quality || {}).counts || {}).FAIL) || 0); onClicked: { wholeLessonReview.close(); bridge.useConvertedLesson() } }
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
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: "#e9eef5"; border.color: root.line
                    Image { anchors.fill: parent; anchors.margins: 3; source: bridge.comparison.source_image || ""; fillMode: Image.PreserveAspectFit }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: "#e9eef5"; border.color: root.line
                    Image { anchors.fill: parent; anchors.margins: 3; source: bridge.comparison.result_image || ""; fillMode: Image.PreserveAspectFit }
                }
            }
            ScrollView {
                id: comparisonReport; Layout.fillWidth: true; Layout.preferredHeight: Math.min(110, comparisonWarnings.implicitHeight + 4); clip: true; contentWidth: availableWidth
                Copy { id: comparisonWarnings; width: comparisonReport.availableWidth; text: (bridge.conversionReport || []).filter(function(item) { return !item.slide || item.slide === bridge.comparison.source_slide }).map(function(item) { return (item.warnings || []).join("\n") || item.message || (item.action === "added" ? "Đã thêm vùng hỗ trợ vào khoảng trống." : item.action === "support_pages" ? "Slide kín: phần hỗ trợ nằm ở trang kế tiếp." : "Giữ nội dung gốc hoặc ưu tiên ngôn ngữ đã chọn.") }).join("\n"); font.pixelSize: 11 }
            }
            Copy { text: "Ảnh đối chiếu xác nhận bố cục tĩnh. Mở PowerPoint để kiểm tra hiệu ứng, video và âm thanh."; Layout.fillWidth: true; font.pixelSize: 11 }
            RowLayout {
                Action { text: "Slide trước"; enabled: !bridge.busy && (bridge.comparison.output_slide || 1) > 1; onClicked: bridge.comparePowerPoint(bridge.comparison.output_slide - 1) }
                Action { text: "Slide tiếp"; enabled: !bridge.busy && bridge.comparison.output_slide < bridge.comparison.total; onClicked: bridge.comparePowerPoint(bridge.comparison.output_slide + 1) }
                Item { Layout.fillWidth: true }
                Action { text: "Mở trong PowerPoint"; enabled: !bridge.busy; onClicked: bridge.previewSourcePowerPoint() }
                Action { text: "Xuất PPTX"; primary: true; enabled: !bridge.busy; onClicked: deckSave.open() }
                Action { text: "Đóng"; onClicked: comparisonDialog.close() }
            }
        }
    }
    Dialog { id: metadataDialog; objectName: "lessonMetadataDialog"; anchors.centerIn: parent; modal: true; title: "Sửa bài giảng"; width: 500
        property var lessonData: ({})
        onOpened: { if (!lessonData.id) lessonData = bridge.lesson; metaTitle.text = lessonData.title; metaSubject.text = lessonData.subject; metaEducation.text = lessonData.education_level; metaGrade.text = lessonData.grade }
        onClosed: lessonData = ({})
        contentItem: ColumnLayout { spacing: 12
            Field { id: metaTitle; objectName: "metadataLessonTitle"; placeholderText: "Tên bài"; Layout.fillWidth: true; maximumLength: 200 }
            Field { id: metaSubject; placeholderText: "Môn học"; Layout.fillWidth: true; maximumLength: 200 }
            RowLayout { Field { id: metaEducation; placeholderText: "Cấp học"; Layout.fillWidth: true; maximumLength: 200 } Field { id: metaGrade; placeholderText: "Khối"; Layout.fillWidth: true; maximumLength: 200 } }
            Copy { text: "Đổi môn sẽ đưa văn bản về trạng thái cần duyệt lại."; Layout.fillWidth: true }
            RowLayout {
                Action { text: "Sửa nội dung trợ giảng"; enabled: !bridge.busy; onClicked: { const lessonId = metadataDialog.lessonData.id; metadataDialog.close(); bridge.editLesson(lessonId) } }
                Item { Layout.fillWidth: true }
                Action { text: "Hủy"; onClicked: metadataDialog.close() }
                Action { objectName: "saveLessonMetadataButton"; text: "Lưu"; primary: true; onClicked: if (bridge.editLessonMetadata(metadataDialog.lessonData.id, metaTitle.text, metaSubject.text, metaEducation.text, metaGrade.text)) metadataDialog.close() }
            }
        }
    }
    Dialog { id: deleteLessonDialog; objectName: "deleteLessonDialog"; anchors.centerIn: parent; modal: true; title: "Xóa bài giảng?"; width: 470
        property string lessonId: ""
        property string lessonTitle: ""
        contentItem: ColumnLayout { spacing: 16
            Caption { text: deleteLessonDialog.lessonTitle; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            Copy { text: "Bài sẽ được đưa vào thùng rác. Có thể khôi phục; bản PowerPoint, âm thanh và báo cáo lớp được giữ lại."; Layout.fillWidth: true }
            RowLayout { Item { Layout.fillWidth: true } Action { objectName: "cancelDeleteLessonButton"; text: "Hủy"; onClicked: deleteLessonDialog.close() } Action { objectName: "confirmDeleteLessonButton"; text: "Xóa bài"; danger: true; onClicked: { bridge.trashLesson(deleteLessonDialog.lessonId); deleteLessonDialog.close() } } }
        }
    }
    Dialog { id: bulkDeleteDialog; objectName: "bulkDeleteLessonsDialog"; anchors.centerIn: parent; modal: true; title: "Xóa " + identities.length + " bài đã chọn?"; width: Math.min(root.width - 48, 500)
        property var identities: []
        contentItem: ColumnLayout { spacing: 16
            Copy { text: "Các bài đã chọn sẽ vào thùng rác. Có thể khôi phục trong Chia sẻ & quản lý. PowerPoint, âm thanh và báo cáo lớp được giữ lại."; Layout.fillWidth: true }
            RowLayout { Item { Layout.fillWidth: true } Action { objectName: "cancelBulkDeleteLessons"; text: "Hủy"; onClicked: bulkDeleteDialog.close() } Action { objectName: "confirmBulkDeleteLessons"; text: "Xóa đã chọn"; danger: true; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: { if (bridge.trashLessons(bulkDeleteDialog.identities)) { root.selectedLessons = []; bulkDeleteDialog.close() } } } }
        }
    }
    Dialog { id: libraryDownloadDialog; objectName: "libraryDownloadDialog"; anchors.centerIn: parent; modal: true; title: "Tải " + identities.length + " bài giảng"; width: Math.min(root.width - 48, 530)
        property var identities: []
        contentItem: ColumnLayout { spacing: 16
            Copy { text: libraryDownloadDialog.identities.length > 1 ? "Các PowerPoint được gói trong một file ZIP. Mỗi bài có tên riêng và thông tin giọng đọc." : "Tải file PowerPoint của bài đã chọn."; Layout.fillWidth: true }
            CheckBox { id: libraryDownloadVoice; objectName: "libraryDownloadVoice"; text: "Kèm bản giọng đã chọn, nếu đã tạo đủ"; checked: true }
            Copy { text: "Bài chưa tạo đủ giọng sẽ tải không kèm âm thanh. Muốn đổi người đọc hoặc loại giọng, mở bài rồi chọn bản cần dùng trước khi tải."; Layout.fillWidth: true; font.pixelSize: 12 }
            RowLayout { Item { Layout.fillWidth: true } Action { text: "Hủy"; onClicked: libraryDownloadDialog.close() } Action { objectName: "confirmLibraryDownload"; text: "Chọn nơi lưu"; primary: true; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: { libraryDownloadDialog.close(); libraryDownloadSave.open() } } }
        }
    }
    FileDialog { id: libraryDownloadSave; objectName: "libraryDownloadSave"; title: "Lưu bài giảng"; currentFolder: bridge.downloadsDirectory; fileMode: FileDialog.SaveFile; defaultSuffix: libraryDownloadDialog.identities.length > 1 ? "zip" : "pptx"; nameFilters: libraryDownloadDialog.identities.length > 1 ? ["Bộ bài giảng (*.zip)"] : ["PowerPoint (*.pptx)"]; onAccepted: bridge.downloadLibraryPresentations(libraryDownloadDialog.identities, selectedFile.toString(), libraryDownloadVoice.checked) }
    Dialog { id: lessonTrashDialog; objectName: "lessonTrashDialog"; anchors.centerIn: parent; modal: true; title: "Thùng rác bài giảng"; width: 680; height: 440; standardButtons: Dialog.Close
        contentItem: ColumnLayout { spacing: 12
            Copy { text: "Khôi phục bài về thư viện với nội dung và ngày tạo trước khi xóa."; Layout.fillWidth: true }
            Copy { visible: bridge.trashedLessons.length === 0; text: "Thùng rác đang trống." }
            ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; contentWidth: availableWidth
                ColumnLayout { width: parent.width; spacing: 10
                    Repeater { model: bridge.trashedLessons
                        RowLayout { required property var modelData; Layout.fillWidth: true
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Caption { text: modelData.title; Layout.fillWidth: true; elide: Text.ElideRight }
                                Copy { text: "Xóa: " + bridge.lessonDateLabel(modelData.deleted_at); font.pixelSize: 11 }
                            }
                            Action { objectName: "restoreLesson_" + modelData.id; text: "Khôi phục"; onClicked: bridge.restoreLesson(modelData.id) }
                        }
                    }
                }
            }
        }
    }
    Dialog {
        id: unsaved; objectName: "unsavedDialog"; anchors.centerIn: parent; modal: true; title: "Lưu thay đổi trước khi tiếp tục?"; width: 465
        contentItem: ColumnLayout { spacing: 19; Copy { text: "Đoạn đang chỉnh sửa chưa được lưu. Lưu nháp sẽ chuyển đoạn về trạng thái chờ duyệt."; Layout.fillWidth: true }
            RowLayout { Action { objectName: "stayButton"; text: "Ở lại"; onClicked: unsaved.close() } Action { text: "Bỏ thay đổi"; onClicked: { unsaved.close(); root.loadFields(); if (root.pendingAction) root.pendingAction() } } Action { text: "Lưu nháp"; primary: true; onClicked: { if (root.save(false)) { unsaved.close(); if (root.pendingAction) root.pendingAction() } } } }
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
                    background: Rectangle { radius: 10; color: parent.hovered ? "#eaf3ff" : "#f8fafd"; border.color: parent.hovered ? root.blue : root.line }
                    contentItem: ColumnLayout { spacing: 6
                        Caption { text: modelData.text; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight }
                        Copy { text: modelData.similarity ? "Gần giống " + modelData.similarity + "% · Nguồn: " + modelData.source : modelData.count + " lần duyệt · " + modelData.lessons.join(", "); Layout.fillWidth: true; font.pixelSize: 11; elide: Text.ElideRight }
                    }
                    onClicked: bridge.useMemoryChoice(index)
                }
            }
            RowLayout { Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Action { text: "Đóng"; onClicked: bridge.closeMemoryChoices() }
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
                Action { text: "Đóng"; onClicked: updateDialog.close() }
                Action { visible: bridge.updateState.downloading; text: "Hủy tải"; onClicked: bridge.cancelUpdate() }
                Action { objectName: "installUpdateButton"; text: bridge.updateState.ready ? "Mở bản mới" : "Cập nhật"; primary: true; enabled: !bridge.updateState.downloading && !bridge.busy && !root.classroom.running; onClicked: bridge.updateState.ready ? bridge.applyDownloadedUpdate() : bridge.downloadUpdate() }
            }
        }
    }
    Dialog { id: deleteTermDialog; property string termId: ""; anchors.centerIn: parent; modal: true; title: "Xóa thuật ngữ này?"; standardButtons: Dialog.Ok | Dialog.Cancel; onAccepted: bridge.deleteTerm(termId) }
    Dialog {
        id: readinessDialog; objectName: "readinessDialog"; anchors.centerIn: parent; modal: true; title: "Chuẩn bị bài giảng"; width: 730; height: Math.min(root.height - 50, 670)
        contentItem: ColumnLayout { spacing: 13
            Copy { text: bridge.readiness.text_ready ? "Văn bản đã duyệt và nguồn còn nguyên vẹn." : "Còn nội dung cần kiểm tra trước khi dạy."; color: bridge.readiness.text_ready ? "#168567" : "#ad651d"; Layout.fillWidth: true }
            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: bridge.readiness.checks
                delegate: Rectangle { required property var modelData; width: ListView.view.width; height: 64; radius: 10; color: modelData.ok ? "#eef9f3" : "#fff7eb"
                    RowLayout { anchors.fill: parent; anchors.margins: 12; spacing: 14
                        Label { text: modelData.ok ? "✓" : "○"; color: modelData.ok ? "#168567" : "#ad651d"; font.pixelSize: 22 }
                        ColumnLayout { spacing: 4; Layout.fillWidth: true; Caption { text: modelData.label } Copy { text: modelData.detail; font.pixelSize: 11; Layout.fillWidth: true } }
                    }
                }
            }
            Copy { text: bridge.busy ? bridge.message : "Có thể dạy bằng văn bản khi chưa có âm thanh. Quiz và mạng lớp học không bắt buộc cho bài song ngữ."; Layout.fillWidth: true; font.pixelSize: 11 }
            RowLayout { Layout.fillWidth: true
                Action { objectName: "prepareEnglishAudio"; text: "Chuẩn bị audio EN"; enabled: !bridge.busy && !!bridge.voiceSettings.en; onClicked: bridge.prepareAudio("en") }
                Action { text: "Chuẩn bị audio VI"; enabled: !bridge.busy && !!bridge.voiceSettings.vi; onClicked: bridge.prepareAudio("vi") }
                Item { Layout.fillWidth: true }
                Action { visible: bridge.busy; text: "Dừng tác vụ"; onClicked: bridge.cancelJob() }
                Action { text: "Làm mới"; enabled: !bridge.busy; onClicked: bridge.refreshReadiness() }
            }
            RowLayout { Layout.fillWidth: true; Action { text: "Đóng"; onClicked: readinessDialog.close() } Item { Layout.fillWidth: true } Action { text: "Xem trước bài"; enabled: !bridge.busy; onClicked: { readinessDialog.close(); root.rescue = false; preview.show() } } Action { objectName: "commitPreparationButton"; text: "Chốt bản chuẩn bị"; primary: true; enabled: !bridge.busy && bridge.readiness.text_ready && !bridge.readiness.prepared_ready; onClicked: bridge.prepareLesson() } }
        }
    }
    Dialog {
        id: sourceDialog; anchors.centerIn: parent; modal: true; title: "Văn bản trích xuất ban đầu"; width: 680; height: 420; standardButtons: Dialog.Close
        ScrollView { anchors.fill: parent; clip: true; TextArea { text: bridge.segment.source_text || ""; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; color: root.ink; font.pixelSize: 15 } }
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
                    contentItem: RowLayout { Copy { text: "Phiên bản " + modelData.revision + " · " + new Date(modelData.saved_at).toLocaleString(); Layout.fillWidth: true } Action { text: "Khôi phục"; onClicked: { bridge.restoreRevision(modelData.revision); historyDialog.close() } } }
                }
            }
        }
    }

    HelpDialog { id: helpDialog; objectName: "helpDialog" }
    CompanionWindow { id: companion; objectName: "companionWindow"; bridge: root.bridgeRef; onRequestOpenLesson: { root.showNormal(); root.raise(); root.requestActivate(); root.go(bridge.lesson.id ? "result" : "library") } }
    TeachingDialog { id: teachingDialog; objectName: "teachingDialog"; teaching: root.teaching; bridge: root.bridgeRef }
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
            Action { objectName: "selectConversionExample"; text: "Chọn kiểu này"; primary: true; Layout.alignment: Qt.AlignRight; onClicked: { creationFormat.currentIndex = conversionExample.formatIndex; conversionExample.close() } }
        }
    }

    Window {
        id: preview; objectName: "lessonPreview"; modality: Qt.NonModal; title: "BiliClass · Bàn điều khiển giảng dạy"; width: 1080; height: 730; minimumWidth: 800; minimumHeight: 600; color: "#f3f7fc"
        property bool showTools: false
        onClosing: { bridge.stopSpeech(); if (bridge.busy) bridge.cancelJob() }
        Shortcut { sequence: "Escape"; onActivated: preview.close() }
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 12
            RowLayout { Layout.fillWidth: true; Image { source: "book.svg"; sourceSize.width: 32; sourceSize.height: 32 } Caption { text: "BiliClass"; font.pixelSize: 21 } Item { Layout.fillWidth: true } Pill { text: bridge.lesson.conversion_format ? bridge.conversionLabel : "L" + bridge.policy.level + " · " + bridge.policy.name } Action { text: preview.showTools ? "Thu trợ giảng" : "Trợ giảng"; onClicked: preview.showTools = !preview.showTools } Action { text: preview.visibility === Window.FullScreen ? "Thu nhỏ" : "Toàn màn hình"; onClicked: preview.visibility === Window.FullScreen ? preview.showNormal() : preview.showFullScreen() } Action { text: "Đóng  ×"; onClicked: preview.close() } }
            Copy { text: bridge.segment.approved ? "Xem trước văn bản đã duyệt · " + (bridge.lesson.title || "") : "BẢN NHÁP CHƯA DUYỆT · Chỉ dùng để kiểm tra nội dung"; color: bridge.segment.approved ? root.muted : "#ad651d"; Layout.fillWidth: true }
            RowLayout { visible: bridge.settings.show_profile; Layout.fillWidth: true; spacing: 10
                Image { objectName: "previewSchoolLogo"; visible: !!bridge.schoolLogoUrl; source: bridge.schoolLogoUrl; cache: false; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 50; Layout.preferredHeight: 50 }
                Copy { text: root.profileLabel; Layout.fillWidth: true }
            }
            TemplateSlide { objectName: "lessonTemplatePreview"; Layout.fillWidth: true; Layout.fillHeight: true; plan: root.templatePages[root.templatePageIndex] || ({}) }
            RowLayout { visible: root.templatePages.length > 1; Layout.fillWidth: true
                Action { text: "Trang mẫu trước"; enabled: root.templatePageIndex > 0; onClicked: root.templatePageIndex-- }
                Copy { text: (root.templatePageIndex + 1) + " / " + root.templatePages.length }
                Action { text: "Trang mẫu tiếp"; enabled: root.templatePageIndex < root.templatePages.length - 1; onClicked: root.templatePageIndex++ }
            }
            Copy { visible: root.presentationContent.needs_easy_en; text: "Chưa có lời giải thích Anh đơn giản đã duyệt; đang xem lời đọc chính."; font.pixelSize: 11; Layout.fillWidth: true }
            AssistantPanel { visible: preview.showTools; teaching: root.teaching; bridge: root.bridgeRef; Layout.fillWidth: true; Layout.preferredHeight: bridge.mascotSettings.visible ? Math.max(130, bridge.mascotSettings.size + 40) : 130 }
            RowLayout { visible: preview.showTools; Layout.fillWidth: true
                Choice { id: projectorScreen; model: bridge.screens; textRole: "name"; currentIndex: bridge.screens.length > 1 ? 1 : 0; Layout.fillWidth: true }
                Action { text: "Mở màn hình lớp"; onClicked: { projector.quiz = false; bridge.showProjector(projector, projectorScreen.currentIndex) } }
                Action { text: "Trợ giảng nổi"; onClicked: bridge.showCompanion(companion) }
                Action { text: "VI Rescue trên màn hình lớp"; onClicked: projector.rescue = !projector.rescue }
            }
            RowLayout { visible: preview.showTools; Layout.fillWidth: true; Item { Layout.fillWidth: true } Action { text: bridge.segment.approved ? "Đọc English" : "Nghe nháp EN"; enabled: !bridge.busy && !!bridge.audioAvailable.en && !!bridge.segment.en; onClicked: bridge.speakSegment("en") } Action { text: bridge.segment.approved ? "Đọc tiếng Việt" : "Nghe nháp VI"; enabled: !bridge.busy && !!bridge.audioAvailable.vi && !!bridge.segment.vi; onClicked: bridge.speakSegment("vi") } Action { text: "Dừng đọc"; onClicked: { bridge.stopSpeech(); if (bridge.busy) bridge.cancelJob() } } Item { Layout.fillWidth: true } }
            RowLayout { Layout.fillWidth: true; Action { text: "←  Trước"; enabled: !bridge.busy && bridge.segmentIndex > 0; onClicked: { bridge.stopSpeech(); bridge.selectSegment(bridge.segmentIndex - 1); root.rescue = false } } Item { Layout.fillWidth: true } Copy { text: (bridge.segmentIndex + 1) + " / " + (bridge.lesson.segments || []).length } Item { Layout.fillWidth: true } Action { text: root.rescue ? "Ẩn tiếng Việt" : "VI Rescue"; onClicked: root.rescue = !root.rescue } Action { text: "Tiếp  →"; primary: true; enabled: !bridge.busy && bridge.segmentIndex < (bridge.lesson.segments || []).length - 1; onClicked: { bridge.stopSpeech(); bridge.selectSegment(bridge.segmentIndex + 1); root.rescue = false } } }
        }
    }
}
