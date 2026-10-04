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
    title: bridge.developmentMode ? "BiliClass · Bản phát triển từ mã nguồn" : "BiliClass · Không gian bài giảng song ngữ"
    color: "#f3f7fc"
    property string page: "home"
    property color ink: "#112650"
    property color muted: "#667997"
    property color blue: "#0869f9"
    property color line: "#e0e8f3"
    property bool dirty: false
    property bool loadingFields: false
    property var pendingAction: null
    property string selectedFile: ""
    property string selectedFileName: ""
    property bool advancedCreation: false
    property bool pasteMode: false
    property bool resultDetails: false
    readonly property bool creationPowerPoint: selectedFileName.toLowerCase().endsWith(".pptx")
    readonly property bool creationKeepSource: creationPowerPoint && creationWorkflow.currentIndex === 0
    readonly property bool keepSourceDesign: bridge.lesson.presentation_style === "source"
    onCreationPowerPointChanged: Qt.callLater(function() { creationWorkflow.currentIndex = creationPowerPoint ? 0 : 1; creationMode.currentIndex = 0 })
    property bool rescue: false
    property var presentationContent: bridge.presentationContent(rescue)
    onRescueChanged: { presentationContent = bridge.presentationContent(rescue); refreshTemplate() }
    property string translationSource: "vi"
    property var teaching: bridge.teachingContext
    property var classroom: bridge.classroomContext
    property string profileLabel: [bridge.settings.teacher, bridge.settings.school].filter(function(value) { return !!value }).join("  ·  ")
    readonly property var layoutKeys: ["keyword_overlay", "line_pair", "split_view", "english_rescue", "level_auto"]
    readonly property var levels: ["L0 · Làm quen", "L1 · Tiếp xúc", "L2 · Cầu nối", "L3 · Kết hợp", "L4 · Ưu tiên English"]
    property var templatePages: bridge.templatePages(rescue)
    property int templatePageIndex: 0
    function refreshTemplate() { templatePages = bridge.templatePages(rescue); templatePageIndex = 0 }

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
    function go(destination) { requestAction(function() { page = destination }) }
    function translateCurrent() {
        if (!dirty || save(false)) bridge.translate(translationSource)
    }
    function edited() {
        if (!loadingFields) { dirty = true; autoSaveTimer.restart() }
    }
    function prepareTranslation(source) {
        translationSource = source
        if (source === "vi" ? enEdit.text.trim() : viEdit.text.trim()) replaceTranslation.open()
        else translateCurrent()
    }
    onClosing: function(close) {
        if (bridge.updateApplying) { close.accepted = true }
        else if (bridge.updateState.downloading) { close.accepted = false; updateBusyDialog.open() }
        else if (bridge.busy) { close.accepted = false; busyDialog.open() }
        else if (dirty) { close.accepted = false; requestAction(function() { Qt.quit() }) }
    }
    Connections {
        target: bridge
        function onPowerpointSlideChanged(slide) { if (!root.dirty) bridge.followPowerPoint() }
        function onProjectClassroomRequested() { projector.quiz = true; bridge.showProjector(projector, bridge.screens.length > 1 ? 1 : 0) }
        function onNavigate(destination) { root.page = destination === "browser-settings" ? "settings" : destination; if (destination === "browser-settings") settingsPanel.activeTab = 6; root.loadFields(); if (destination === "result" || destination === "editor") { titleInput.text = ""; subjectInput.text = ""; pasteInput.text = ""; root.selectedFile = ""; root.selectedFileName = "" } }
        function onSelectionChanged() { root.loadFields() }
        function onInputAssessmentChanged() { if (bridge.inputAssessment.recommended_mode) creationMode.currentIndex = bridge.inputAssessment.recommended_mode === "preserve" ? 1 : 0 }
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
            Text { text: action.text; font: action.font; color: !action.enabled ? "#96a6bc" : action.primary ? "white" : root.blue; verticalAlignment: Text.AlignVCenter }
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
                Repeater {
                    model: [{key:"home", label:"Trang chủ", icon:"home"}, {key:"library", label:"Bài giảng", icon:"lessons"}, {key:"classroom", label:"Lớp học", icon:"classroom"}, {key:"reports", label:"Báo cáo", icon:"reports"}, {key:"glossary", label:"Thuật ngữ", icon:"glossary"}, {key:"knowledge", label:"Kho kiến thức", icon:"data"}, {key:"settings", label:"Cài đặt", icon:"settings"}]
                    delegate: Button {
                        required property var modelData
                        readonly property bool selected: root.page === modelData.key || (modelData.key === "library" && ["editor", "new", "result", "chatgpt"].indexOf(root.page) >= 0)
                        Layout.fillWidth: true; implicitHeight: 48; leftPadding: 14
                        onClicked: root.go(modelData.key)
                        background: Rectangle { radius: 10; color: parent.selected ? "#eaf3ff" : parent.hovered ? "#f4f7fc" : "transparent" }
                        contentItem: RowLayout {
                            spacing: 13
                            Image { source: "../assets/navigation/" + modelData.icon + (selected ? "-active" : "") + ".png"; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 29; Layout.preferredHeight: 29 }
                            Label { text: modelData.label; font.pixelSize: 14; font.weight: selected ? Font.DemiBold : Font.Normal; color: selected ? root.blue : root.muted; Layout.fillWidth: true }
                        }
                    }
                }
                Item { Layout.fillHeight: true }
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
                    spacing: 10
                    Rectangle { width: 36; height: 36; radius: 18; color: "#fff0df"; Label { anchors.centerIn: parent; text: (bridge.settings.teacher || "G").charAt(0).toUpperCase(); color: "#ab611f"; font.weight: Font.Bold } }
                    ColumnLayout { spacing: 3; Label { text: bridge.settings.teacher; color: root.ink; font.pixelSize: 12; elide: Text.ElideRight; Layout.maximumWidth: 110 } Copy { text: bridge.settings.school || "Giáo viên · Local"; font.pixelSize: 10; elide: Text.ElideRight; Layout.maximumWidth: 130 } }
                }
                Action { text: "Hướng dẫn · F1"; implicitHeight: 32; subtle: true; onClicked: helpDialog.open() }
                Action { visible: !bridge.developmentMode; text: bridge.updateState.checking ? "Đang kiểm tra…" : "Kiểm tra cập nhật"; implicitHeight: 32; subtle: true; enabled: !bridge.updateState.checking && !bridge.updateState.downloading; onClicked: bridge.checkForUpdates(false) }
                Copy { text: bridge.developmentMode ? "Bản phát triển từ mã nguồn" : "Bản dùng thử · " + bridge.appVersion; font.pixelSize: 9; Layout.topMargin: 12 }
            }
        }
        ColumnLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 0
            Rectangle {
                Layout.fillWidth: true; height: 70; color: "#ffffff"
                Rectangle { anchors.bottom: parent.bottom; height: 1; width: parent.width; color: root.line }
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 30; anchors.rightMargin: 30
                    Copy { text: (root.page === "editor" || root.page === "result") ? "Bài học  /  " + (bridge.lesson.title || "") : "Không gian bài giảng song ngữ"; color: root.ink; elide: Text.ElideRight; Layout.fillWidth: true; maximumLineCount: 1 }
                    Action { objectName: "backToConvertedLessonButton"; visible: root.page === "editor"; text: "Bản trình chiếu"; iconName: "back"; subtle: true; implicitHeight: 32; onClicked: root.go("result") }
                    Pill { text: "ANH  ⇄  VIỆT" }
                    Pill { text: "Lưu trên máy"; tone: "#168567"; Layout.leftMargin: 10 }
                }
            }
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                ScrollView {
                    anchors.fill: parent; anchors.margins: 30
                    visible: root.page === "home" || root.page === "library"
                    clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 23
                        RowLayout {
                            Layout.fillWidth: true
                            ColumnLayout { spacing: 8; Heading { text: root.page === "home" ? "Chào " + bridge.settings.teacher + ",\ncùng mở thêm khả năng." : "Bài học của tôi"; font.pixelSize: 30 }
                                Copy { text: "Một bài giảng. Hai ngôn ngữ. Theo cách dạy của thầy cô."; Layout.fillWidth: true } }
                            Item { Layout.fillWidth: true }
                            Action { text: "+  Bài học mới"; primary: true; onClicked: root.go("new") }
                        }
                        Rectangle {
                            visible: root.page === "home"
                            Layout.fillWidth: true; implicitHeight: 206; radius: 19; color: "#e6f0ff"
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 28; spacing: 28
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 13
                                    Pill { text: "CHUẨN BỊ HÔM NAY, TỰ TIN LÊN LỚP" }
                                    Label { text: "Giữ mạch bài giảng.\nMở cầu nối Anh–Việt."; color: root.ink; font.pixelSize: 25; font.weight: Font.Bold; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                                    Copy { text: "Nhập bài có sẵn, chỉnh bản song ngữ và duyệt từng đoạn.\nPhù hợp nhiều môn học và nhiều cách tổ chức bài giảng."; Layout.fillWidth: true }
                                }
                                Image {
                                    Layout.preferredWidth: 235; Layout.fillHeight: true
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
                                        Caption { text: "Có BiliClass " + bridge.updateState.version + " mới"; font.pixelSize: 15 }
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
                            Label { text: root.page === "home" ? "Tiếp tục chuẩn bị bài" : "Thư viện cá nhân"; color: root.ink; font.pixelSize: 18; font.weight: Font.DemiBold }
                            Copy { text: bridge.lessons.length + " bài học"; Layout.leftMargin: 8 }
                            Item { Layout.fillWidth: true }
                            Action { text: "Nhập gói .biliclass"; iconName: "upload"; subtle: true; onClicked: packOpen.open() }
                        }
                        Field { id: search; visible: root.page === "library"; Layout.fillWidth: true; placeholderText: "Tìm theo tên bài, môn hoặc khối lớp…" }
                        Surface {
                            visible: bridge.lessons.length === 0; Layout.fillWidth: true; implicitHeight: 202
                            ColumnLayout { anchors.centerIn: parent; spacing: 13; Label { text: "Bài giảng đầu tiên bắt đầu từ đây"; color: root.ink; font.pixelSize: 19; font.weight: Font.DemiBold }
                                Copy { text: "Tải PPTX, DOCX, PDF có văn bản, TXT hoặc dán nội dung."; Layout.alignment: Qt.AlignHCenter }
                                Action { text: "+  Tạo bài học"; primary: true; Layout.alignment: Qt.AlignHCenter; onClicked: root.go("new") } }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 10
                            Repeater {
                                model: bridge.lessons
                                delegate: Surface {
                                    required property var modelData
                                    required property int index
                                    visible: (root.page !== "home" || index < 4) && (root.page === "home" || (modelData.title + modelData.subject + modelData.grade).toLowerCase().indexOf(search.text.toLowerCase()) >= 0)
                                    Layout.fillWidth: true; implicitHeight: 102
                                    RowLayout {
                                        anchors.fill: parent; anchors.margins: 19; spacing: 17
                                        Rectangle { width: 57; height: 62; radius: 12; color: ["#e7f1ff", "#ecf7ef", "#fff2e7"][index % 3]; Label { anchors.centerIn: parent; text: "VI\nEN"; color: root.blue; font.pixelSize: 16; font.weight: Font.Bold; lineHeight: 1.1 } }
                                        ColumnLayout { Layout.fillWidth: true; spacing: 7; Label { text: modelData.title; color: root.ink; font.pixelSize: 16; font.weight: Font.DemiBold; elide: Text.ElideRight; Layout.fillWidth: true } Copy { text: modelData.subject + "  ·  " + modelData.education_level + " " + modelData.grade + "  ·  " + modelData.segments_count + " đoạn" } }
                                        ColumnLayout { spacing: 8; Pill { text: modelData.prepared ? "Đã chốt bài" : root.statusLabel(modelData.status); tone: modelData.prepared ? "#168567" : "#9c651b" } Copy { text: modelData.approved_count + "/" + modelData.segments_count + " đoạn đã duyệt"; font.pixelSize: 11 } }
                                        Action { text: "Mở bài  →"; onClicked: bridge.openLesson(modelData.id) }
                                    }
                                }
                            }
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
                    anchors.fill: parent; anchors.margins: 28; visible: root.page === "new"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 16
                        RowLayout { Heading { text: "Từ tài liệu đến bài giảng song ngữ"; font.pixelSize: 27 } Item { Layout.fillWidth: true } Action { text: "Thư viện"; iconName: "back"; subtle: true; onClicked: root.go("library") } }
                        Copy { text: "Nhập tài liệu → chọn level và cách trình bày → chuyển đổi → xem trình chiếu → dùng để dạy."; Layout.fillWidth: true }
                        Surface {
                            Layout.fillWidth: true; implicitHeight: sourceInputs.height + 36
                            ColumnLayout {
                                id: sourceInputs; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 18; spacing: 10
                                RowLayout {
                                    Layout.fillWidth: true
                                    Caption { text: "01   Tài liệu đầu vào"; font.pixelSize: 15 }
                                    Copy { text: "PPTX · DOCX · PDF · TXT · PNG/JPG · tối đa 50 MB"; Layout.fillWidth: true; font.pixelSize: 12 }
                                    Action { text: root.selectedFile ? "Đổi tệp" : "Chọn tài liệu"; iconName: "upload"; enabled: !bridge.busy; onClicked: documentOpen.open() }
                                }
                                RowLayout {
                                    visible: !!root.selectedFile; Layout.fillWidth: true
                                    Caption { text: root.selectedFileName; elide: Text.ElideMiddle; Layout.fillWidth: true }
                                    Action { text: "Bỏ tệp"; subtle: true; implicitHeight: 30; enabled: !bridge.busy; onClicked: { root.selectedFile = ""; root.selectedFileName = ""; bridge.clearInputAssessment() } }
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
                                    Layout.fillWidth: true; columns: 4; columnSpacing: 14; rowSpacing: 8
                                    Caption { text: "Tên bài học"; Layout.columnSpan: 2 } Caption { text: "Môn học" } Caption { text: "Khối lớp" }
                                    Field { id: titleInput; objectName: "lessonTitle"; Layout.fillWidth: true; Layout.columnSpan: 2; placeholderText: "Tên bài giảng"; maximumLength: 180 }
                                    Field { id: subjectInput; objectName: "lessonSubject"; Layout.fillWidth: true; placeholderText: "Môn của thầy cô"; maximumLength: 100 }
                                    Choice { id: gradeInput; objectName: "creationGrade"; editable: true; model: ["10", "11", "12", "6", "7", "8", "9"]; Layout.preferredWidth: 130; Layout.fillWidth: true }
                                    Caption { text: "Level song ngữ"; Layout.columnSpan: 2 } Caption { text: "Sắp xếp Việt–Anh"; Layout.columnSpan: 2 }
                                    Choice { id: creationLevel; objectName: "creationLevel"; Layout.columnSpan: 2; model: root.levels; currentIndex: 2; Layout.fillWidth: true }
                                    Choice { id: creationLayout; objectName: "creationLayout"; Layout.columnSpan: 2; model: ["Cùng dòng · từ khóa", "Hai dòng · EN in nghiêng", "Hai cột VI / EN", "English chính · Việt hỗ trợ", "Tự sắp xếp theo level"]; currentIndex: 4; Layout.fillWidth: true }
                                    Caption { text: "Chuyển đổi theo"; Layout.columnSpan: 2 } Caption { text: "Thực hiện bằng"; Layout.columnSpan: 2 }
                                    Choice { id: creationWorkflow; objectName: "creationWorkflow"; model: root.creationPowerPoint ? ["Giữ PowerPoint gốc", "Theo mẫu BiliClass"] : ["Giữ PowerPoint gốc (cần PPTX)", "Theo mẫu BiliClass"]; currentIndex: 1; enabled: root.creationPowerPoint; Layout.columnSpan: 2; Layout.fillWidth: true }
                                    Choice { id: conversionProvider; objectName: "conversionProvider"; model: ["Browser AI · ChatGPT", "BiliClass ngoại tuyến"]; Layout.columnSpan: 2; Layout.fillWidth: true; onActivated: { if (currentIndex === 1 && root.selectedFile) bridge.assessInput(root.selectedFile, sourceLanguage.currentIndex === 0 ? "vi" : "en"); else bridge.clearInputAssessment() } }
                                }
                                RowLayout {
                                    visible: !root.creationKeepSource; Layout.fillWidth: true
                                    Caption { text: "Mẫu BiliClass" }
                                    Choice { id: creationPreset; objectName: "creationPreset"; model: ["Chuẩn lớp học", "Trực quan", "Luyện tập & tương tác"]; Layout.fillWidth: true }
                                    Action { objectName: "creationTemplatesButton"; text: "Xem slide mẫu"; iconName: "view"; onClicked: { templateGallery.forCreation = true; templateGallery.preset = ["standard", "visual", "practice"][creationPreset.currentIndex]; templateGallery.level = creationLevel.currentIndex; templateGallery.layout = root.layoutKeys[creationLayout.currentIndex]; templateGallery.open() } }
                                }
                                Copy { text: root.creationKeepSource ? "Giữ hình, thiết kế và thứ tự slide; thêm song ngữ phù hợp với level đã chọn." : "Tạo slide mới theo mẫu, lấy nội dung và hình từ tài liệu của thầy cô."; Layout.fillWidth: true; font.pixelSize: 12 }
                                GridLayout {
                                    visible: root.advancedCreation; columns: 4; Layout.fillWidth: true; columnSpacing: 12; rowSpacing: 8
                                    Caption { text: "Cấp học" } Caption { text: "Phần đã song ngữ"; Layout.columnSpan: 3 }
                                    Choice { id: educationInput; editable: true; model: ["THPT", "THCS", "Tiểu học"]; Layout.fillWidth: true }
                                    Choice { id: creationMode; objectName: "creationMode"; model: ["Bổ sung theo level", "Giữ nguyên + trợ giảng", "Slide Việt/Anh kế tiếp"]; Layout.columnSpan: 3; Layout.fillWidth: true }
                                    Caption { visible: conversionProvider.currentIndex === 1; text: "Ngôn ngữ OCR/dự phòng" }
                                    Choice { id: sourceLanguage; objectName: "sourceLanguage"; visible: conversionProvider.currentIndex === 1; model: ["Tiếng Việt", "English"]; Layout.fillWidth: true; onActivated: { if (root.selectedFile) bridge.assessInput(root.selectedFile, currentIndex === 0 ? "vi" : "en") } }
                                    Copy { visible: conversionProvider.currentIndex === 1; text: "OCR và giọng đọc cần gói model trên máy."; Layout.columnSpan: 2; Layout.fillWidth: true; font.pixelSize: 11 }
                                    CheckBox { objectName: "creationManualChatGPT"; visible: conversionProvider.currentIndex === 0; text: "Gửi / nhận PowerPoint thủ công"; checked: !bridge.browserAI.automatic; Layout.columnSpan: 2; onClicked: bridge.browserAI.saveOptions(!checked, bridge.browserAI.audio) }
                                    CheckBox { objectName: "creationBrowserAudio"; visible: conversionProvider.currentIndex === 0; text: "Chuẩn bị giọng đọc"; checked: bridge.browserAI.audio; Layout.columnSpan: 2; onClicked: bridge.browserAI.saveOptions(bridge.browserAI.automatic, checked) }
                                }
                            }
                        }
                        Copy { objectName: "inputAssessmentLabel"; visible: conversionProvider.currentIndex === 1 && !!bridge.inputAssessment.label; text: "Đầu vào: " + (bridge.inputAssessment.label || "") + " · Giữ cặp có sẵn, bổ sung phần thiếu."; Layout.fillWidth: true }
                        RowLayout {
                            Layout.fillWidth: true
                            Action { objectName: "advancedCreationButton"; text: root.advancedCreation ? "Thu gọn" : "Tùy chọn thêm"; subtle: true; enabled: !bridge.busy; onClicked: root.advancedCreation = !root.advancedCreation }
                            Item { Layout.fillWidth: true }
                            Action { objectName: "createLessonButton"; text: bridge.busy ? "Đang chuẩn bị…" : conversionProvider.currentIndex === 0 ? (bridge.browserAI.automatic ? "Chuyển đổi bằng ChatGPT" : "Chuẩn bị & mở ChatGPT") : "Chuyển đổi bài giảng"; primary: true; enabled: !bridge.busy; onClicked: {
                                if (conversionProvider.currentIndex === 0 && bridge.browserAI.automatic) bridge.convertBrowserAI(titleInput.text, subjectInput.text, educationInput.editText, gradeInput.editText, pasteInput.text, root.selectedFile, creationLevel.currentIndex, root.layoutKeys[creationLayout.currentIndex], ["standard", "visual", "practice"][creationPreset.currentIndex], root.creationKeepSource ? "source" : "template", root.advancedCreation ? ["level", "preserve", "paired"][creationMode.currentIndex] : "level")
                                else if (conversionProvider.currentIndex === 0) bridge.prepareChatGPT(titleInput.text, subjectInput.text, educationInput.editText, gradeInput.editText, pasteInput.text, root.selectedFile, creationLevel.currentIndex, root.layoutKeys[creationLayout.currentIndex], ["standard", "visual", "practice"][creationPreset.currentIndex], root.creationKeepSource ? "source" : "template", root.advancedCreation ? ["level", "preserve", "paired"][creationMode.currentIndex] : "level")
                                else bridge.convertLesson(titleInput.text, subjectInput.text, educationInput.editText, gradeInput.editText, pasteInput.text, root.selectedFile, sourceLanguage.currentIndex === 0 ? "vi" : "en", creationLevel.currentIndex, root.layoutKeys[creationLayout.currentIndex], ["standard", "visual", "practice"][creationPreset.currentIndex], root.creationKeepSource ? "source" : "template", root.advancedCreation ? ["level", "preserve", "paired"][creationMode.currentIndex] : "level")
                            } }
                        }
                        Copy { text: conversionProvider.currentIndex === 0 ? (bridge.browserAI.automatic ? (bridge.browserAI.webMode ? "BiliClass gửi prompt và tài liệu bằng phiên web ChatGPT đã đăng nhập, nhận PowerPoint rồi chuẩn bị giọng đọc. Khả năng tạo tệp và số lượt dùng phụ thuộc tài khoản Free/Plus." : "Dùng hạn mức ChatGPT của tài khoản đã kết nối. BiliClass gửi nội dung/hình nguồn, nhận song ngữ rồi dựng PowerPoint và chuẩn bị trợ giảng tại máy.") : "BiliClass tạo prompt và gói tài liệu tại máy. Thầy cô gửi trong ChatGPT, tải PowerPoint về rồi nhận vào tool.") : "Chuyển đổi tại máy bằng model đã cài. Xem bản trình chiếu rồi xác nhận cả bài một lần."; Layout.fillWidth: true; font.pixelSize: 12 }
                        Action { visible: conversionProvider.currentIndex === 0; text: "Tài khoản: " + bridge.browserAI.activeLabel + " · Browser AI"; subtle: true; onClicked: { root.go("settings"); settingsPanel.activeTab = 6 } }
                        Action { text: "Tiếp tục gói ChatGPT đã chuẩn bị"; visible: !!bridge.chatgptRequest.folder; subtle: true; onClicked: root.go("chatgpt") }
                    }
                }

                ScrollView {
                    anchors.fill: parent; anchors.margins: 30; visible: root.page === "chatgpt"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout { Heading { text: "Chuyển đổi với ChatGPT"; font.pixelSize: 28 } Item { Layout.fillWidth: true } Action { text: "Đổi cấu hình"; subtle: true; onClicked: root.go("new") } }
                        Copy { Layout.fillWidth: true; text: (bridge.chatgptRequest.config || {}).title || "Chuẩn bị tài liệu trước khi gửi"; color: root.ink; font.pixelSize: 17 }
                        Surface {
                            visible: bridge.browserAI.automatic && bridge.browserState.phase !== "manual"
                            Layout.fillWidth: true; implicitHeight: autoBrowserSteps.height + 42
                            ColumnLayout {
                                id: autoBrowserSteps; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 21; spacing: 14
                                RowLayout { Layout.fillWidth: true
                                    BusyIndicator { running: !!bridge.browserState.running; visible: running; implicitWidth: 34; implicitHeight: 34 }
                                    Caption { text: bridge.browserState.running ? "ChatGPT đang xử lý bài" : "Kết nối ChatGPT"; font.pixelSize: 18; Layout.fillWidth: true }
                                }
                                Copy { objectName: "browserConversionStatus"; text: bridge.browserState.message || "Yêu cầu đã chuẩn bị. Bấm Tiếp tục để gửi/chờ qua tài khoản đã chọn."; Layout.fillWidth: true; font.pixelSize: 15; color: root.ink }
                                Copy { Layout.fillWidth: true; text: bridge.browserAI.webMode ? "Gửi tài liệu → nhận PowerPoint song ngữ → chuẩn bị giọng đọc → xem trình chiếu → xác nhận để dạy." : "Đọc bài gốc → xử lý song ngữ → tạo PowerPoint tại máy → xem trình chiếu → xác nhận để dạy." }
                                RowLayout { Layout.fillWidth: true
                                    Action { objectName: "browserConversionResume"; text: bridge.browserAI.webMode && bridge.browserState.needsLogin ? "Đăng nhập và tiếp tục" : "Tiếp tục yêu cầu"; primary: true; visible: !bridge.browserState.running; enabled: !bridge.busy && !bridge.browserAI.loginBusy && !!bridge.chatgptRequest.folder; onClicked: { if (bridge.browserState.needsConfirmation) planRetryDialog.open(); else if (bridge.browserAI.webMode && bridge.browserState.needsLogin) bridge.reconnectBrowserAI(); else bridge.runBrowserAI() } }
                                    Action { objectName: "browserConversionCancel"; text: "Dừng"; visible: !!bridge.browserState.running; onClicked: bridge.cancelJob() }
                                    Action { text: "Gửi/nhận thủ công"; enabled: !bridge.busy; onClicked: bridge.useManualChatGPT() }
                                    Action { text: "Đăng nhập / Browser AI"; enabled: !bridge.busy; onClicked: { root.go("settings"); settingsPanel.activeTab = 6 } }
                                }
                                Copy { text: bridge.browserAI.webMode ? "Yêu cầu giữ nguyên tài khoản đã gửi. Nếu hết hạn mức hoặc cần xác minh, tool dừng để bạn xử lý; không tự gửi lại hay đổi tài khoản." : "Các phần hoàn tất được lưu để dùng lại. Nếu kết nối bị ngắt giữa chừng, bạn sẽ xác nhận trước khi gửi lại phần chưa rõ kết quả."; Layout.fillWidth: true; font.pixelSize: 12 }
                            }
                        }
                        Surface {
                            visible: !bridge.browserAI.automatic || bridge.browserState.phase === "manual"
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
                        Action { text: chatgptPromptPreview.visible ? "Ẩn prompt" : "Xem prompt đã cấu hình"; subtle: true; onClicked: chatgptPromptPreview.visible = !chatgptPromptPreview.visible }
                        ScrollView { id: chatgptPromptPreview; visible: false; Layout.fillWidth: true; Layout.preferredHeight: 240; clip: true
                            TextArea { readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 13; text: bridge.chatgptRequest.prompt || ""; color: root.ink }
                        }
                    }
                }

                ScrollView {
                    anchors.fill: parent; anchors.margins: 28; visible: root.page === "result"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout {
                            Layout.fillWidth: true
                            ColumnLayout {
                                Layout.fillWidth: true; spacing: 6
                                Heading { text: bridge.lesson.title || "Bài giảng song ngữ" }
                                Copy { text: [bridge.lesson.subject, bridge.lesson.education_level + " " + bridge.lesson.grade, root.levels[bridge.lesson.level || 0]].join(" · ") }
                            }
                            Action { objectName: "editLessonDetailsButton"; text: "Chỉnh sửa chi tiết"; subtle: true; enabled: !bridge.busy; onClicked: root.go("editor") }
                        }
                        RowLayout {
                            Layout.fillWidth: true; spacing: 12
                            Copy { Layout.fillWidth: true; text: bridge.busy || bridge.error ? bridge.message : bridge.quickResult.path ? (bridge.quickResult.draft ? "Đã tạo bản trình chiếu · Xem kết quả và xác nhận cả bài để dạy." : "Đã kiểm tra cả bài · Sẵn sàng trình chiếu.") : bridge.quickResult.missing && bridge.quickResult.missing.length ? "Còn " + bridge.quickResult.missing.length + " phần cần sửa trước khi tạo bản trình chiếu." : "Bấm Chuyển đổi để tự bổ sung song ngữ và tạo bản trình chiếu."; color: root.ink }
                            Action { objectName: "convertCurrentLessonButton"; visible: !bridge.quickResult.path; text: "Chuyển đổi bài giảng"; primary: true; enabled: !bridge.busy; onClicked: bridge.convertCurrentLesson() }
                            Action { objectName: "openConvertedDeckButton"; visible: !!bridge.quickResult.path; text: "Xem toàn bộ bài"; enabled: !bridge.busy; onClicked: bridge.openConvertedDeck() }
                            Action { objectName: "useConvertedLessonButton"; visible: !!bridge.quickResult.path; text: "Dùng để dạy"; primary: true; enabled: !bridge.busy && !bridge.powerpointState.active; onClicked: { if (bridge.quickResult.draft) wholeLessonReview.open(); else bridge.useConvertedLesson() } }
                        }
                        ProgressBar { visible: bridge.busy; indeterminate: true; Layout.fillWidth: true }
                        Surface {
                            Layout.fillWidth: true; implicitHeight: Math.max(280, Math.min(520, root.height - 430)); color: "#e9eef5"
                            Image { objectName: "convertedSlideImage"; anchors.fill: parent; anchors.margins: 6; source: bridge.quickResult.image || ""; fillMode: Image.PreserveAspectFit }
                            ColumnLayout {
                                visible: !bridge.quickResult.image; anchors.centerIn: parent; width: parent.width - 70; spacing: 12
                                Caption { text: bridge.busy ? "BiliClass đang tạo bài giảng…" : bridge.quickResult.path ? "Bản trình chiếu đã tạo" : "Từ tài liệu của thầy cô đến bài giảng song ngữ"; font.pixelSize: 19; Layout.alignment: Qt.AlignHCenter }
                                Copy { text: bridge.quickResult.preview_note || "PowerPoint giữ thiết kế gốc. Tài liệu và ảnh được chuyển thành slide theo mẫu BiliClass."; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; visible: !!bridge.quickResult.path
                            Action { text: "‹"; implicitHeight: 34; enabled: !bridge.busy && (bridge.quickResult.slide || 1) > 1; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide - 1) }
                            Copy { text: "Slide " + (bridge.quickResult.slide || 1) + " / " + (bridge.quickResult.total || 0); color: root.ink }
                            Action { text: "›"; implicitHeight: 34; enabled: !bridge.busy && (bridge.quickResult.slide || 1) < bridge.quickResult.total; onClicked: bridge.previewConvertedSlide(bridge.quickResult.slide + 1) }
                            Item { Layout.fillWidth: true }
                            Action { text: "Chuyển đổi lại"; subtle: true; implicitHeight: 34; enabled: !bridge.busy && !bridge.powerpointState.active; onClicked: bridge.convertCurrentLesson() }
                        }
                        RowLayout {
                            Layout.fillWidth: true; visible: bridge.powerpointState.active
                            Copy { text: bridge.powerpointState.message || "Đang trình chiếu"; Layout.fillWidth: true }
                            Action { text: "Slide trước"; onClicked: bridge.navigatePowerPoint("previous") }
                            Action { text: "Slide tiếp"; onClicked: bridge.navigatePowerPoint("next") }
                            Action { text: "Đóng trình chiếu"; onClicked: bridge.stopPowerPoint() }
                        }
                        Action { objectName: "resultDetailsButton"; visible: !!bridge.quickResult.path || !!bridge.quickResult.missing; text: root.resultDetails ? "Thu gọn thông tin" : "Thông tin và điểm cần kiểm tra"; subtle: true; implicitHeight: 32; onClicked: root.resultDetails = !root.resultDetails }
                        Surface {
                            visible: root.resultDetails || !!bridge.quickResult.missing && bridge.quickResult.missing.length > 0
                            Layout.fillWidth: true; implicitHeight: resultInfo.height + 32
                            ColumnLayout {
                                id: resultInfo; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16; spacing: 10
                                Copy { Layout.fillWidth: true; text: (bridge.quickResult.missing || []).length ? "Chưa đủ song ngữ: " + bridge.quickResult.missing.slice(0, 8).join(", ") : "Kiểm tra thuật ngữ, số liệu và ý nghĩa trong bản trình chiếu. Trợ giảng, quiz và giọng đọc có thể bổ sung khi cần." }
                                Copy { Layout.fillWidth: true; visible: (bridge.quickResult.warnings || []).length > 0; text: (bridge.quickResult.warnings || []).slice(0, 8).join("\n"); color: "#a66318" }
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
                        CheckBox { objectName: "keepPowerPointDesign"; text: "Giữ thiết kế gốc"; visible: bridge.powerpointAvailable; checked: root.keepSourceDesign; onClicked: { let style = checked ? "source" : "template"; root.requestAction(function() { bridge.setPresentationStyle(style) }) } }
                        Choice { id: presetChoice; objectName: "presetChoice"; visible: !root.keepSourceDesign; model: ["Chuẩn lớp học", "Trực quan", "Luyện tập & tương tác"]; currentIndex: Math.max(0, ["standard", "visual", "practice"].indexOf(bridge.lesson.teaching_preset || "standard")); Layout.preferredWidth: 195; onActivated: bridge.setTeachingPreset(["standard", "visual", "practice"][currentIndex]) }
                        Action { objectName: "editorTemplatesButton"; text: "Mẫu"; visible: !root.keepSourceDesign; onClicked: root.requestAction(function() { templateGallery.forCreation = false; templateGallery.preset = bridge.lesson.teaching_preset || "standard"; templateGallery.level = bridge.lesson.level || 0; templateGallery.layout = bridge.lesson.layout || "line_pair"; templateGallery.open() }) }
                        Choice { id: levelChoice; model: bridge.lesson.level === 5 ? root.levels.concat(["L5 · Bài cũ"]) : root.levels; currentIndex: bridge.lesson.level === undefined ? 2 : bridge.lesson.level; Layout.preferredWidth: 194; onActivated: { if (currentIndex < 5) bridge.setPresentation(currentIndex, bridge.lesson.layout || "line_pair") } }
                        Choice { objectName: "conversionMode"; visible: root.keepSourceDesign; model: ["Bổ sung theo L0–L4", "Giữ nguyên + trợ giảng", "Slide Việt/Anh kế tiếp"]; currentIndex: Math.max(0, ["level", "preserve", "paired"].indexOf(bridge.lesson.conversion_mode || "paired")); Layout.preferredWidth: 210; onActivated: bridge.setConversionMode(["level", "preserve", "paired"][currentIndex]) }
                        Choice { id: layoutChoice; visible: !root.keepSourceDesign; model: ["Cùng dòng · từ khóa", "Hai dòng · EN in nghiêng", "Hai cột VI / EN", "English toàn phần", "Theo level L0–L4"]; currentIndex: Math.max(0, root.layoutKeys.indexOf(bridge.lesson.layout)); Layout.preferredWidth: 200; onActivated: bridge.setPresentation(bridge.lesson.level, root.layoutKeys[currentIndex]) }
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
                        Action { objectName: "translateMissingButton"; text: "Dịch phần còn thiếu"; implicitHeight: 32; enabled: !bridge.busy && !!bridge.lesson.id; onClicked: root.requestAction(function() { bridge.translateMissing() }) }
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
                                RowLayout { Layout.fillWidth: true; Caption { text: "VI   Tiếng Việt" } Item { Layout.fillWidth: true } Action { objectName: "translateToViButton"; text: "Dịch Anh → Việt"; implicitHeight: 30; enabled: !bridge.busy && !lockedCheck.checked && enEdit.text.trim() !== ""; onClicked: root.prepareTranslation("en") } }
                                ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 56; clip: true
                                    TextArea { id: viEdit; objectName: "viEditor"; wrapMode: TextEdit.Wrap; selectByMouse: true; color: root.ink; font.pixelSize: 15; padding: 13; onTextChanged: root.edited(); background: Rectangle { radius: 9; color: "#f8fafd"; border.color: parent.activeFocus ? root.blue : root.line } }
                                }
                                RowLayout { Layout.fillWidth: true; Caption { text: "EN   English"; color: root.blue } Item { Layout.fillWidth: true }
                                    Action { objectName: "translateButton"; text: bridge.busy ? "Đang dịch…" : "Dịch Việt → Anh"; implicitHeight: 30; enabled: !bridge.busy && !lockedCheck.checked && viEdit.text.trim() !== ""; onClicked: root.prepareTranslation("vi") } }
                                ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 56; clip: true
                                    TextArea { id: enEdit; objectName: "enEditor"; wrapMode: TextEdit.Wrap; selectByMouse: true; color: "#1855a6"; font.pixelSize: 15; padding: 13; placeholderText: "Nhập bản tiếng Anh hoặc tạo bản dịch nháp trên máy…"; onTextChanged: root.edited(); background: Rectangle { radius: 9; color: "#f4f8ff"; border.color: parent.activeFocus ? root.blue : "#d4e4fc" } }
                                }
                                Action { text: "Tìm bản dịch gần giống đã duyệt"; iconName: "search"; implicitHeight: 30; enabled: !bridge.busy && !lockedCheck.checked; onClicked: { root.translationSource = bridge.segment.source_language || bridge.lesson.source_language || "vi"; if (!root.dirty || root.save(false)) bridge.suggestSimilar(root.translationSource) } }
                                Copy { text: "Bản dịch máy cần thầy cô kiểm tra thuật ngữ, số liệu, công thức và ý nghĩa. Dịch thử tối đa 2.000 ký tự/đoạn."; font.pixelSize: 10; Layout.fillWidth: true }
                                Copy { visible: bridge.reviewWarnings.length > 0; text: bridge.reviewWarnings.join("\n"); color: "#ad651d"; font.pixelSize: 11; Layout.fillWidth: true }
                                RowLayout {
                                    Layout.fillWidth: true
                                    CheckBox { id: lockedCheck; text: "Khóa dịch tự động"; font.pixelSize: 11; onToggled: root.edited() }
                                    Item { Layout.fillWidth: true }
                                    Action { objectName: "saveDraftButton"; text: "Lưu nháp"; iconName: "save"; enabled: !!bridge.lesson.id; onClicked: root.save(false) }
                                    Action { objectName: "approveButton"; text: "✓  Duyệt đoạn"; primary: true; enabled: !!bridge.lesson.id && enEdit.text.trim() !== "" && viEdit.text.trim() !== ""; onClicked: root.save(true) }
                                }
                            }
                        }
                    }
                    Copy { text: root.statusLabel(bridge.status) + "  ·  Tự lưu bản nháp sau khi ngừng nhập" + (root.keepSourceDesign ? "  ·  Xem bài song ngữ bằng PowerPoint" : "  ·  Xem trước hiện hỗ trợ văn bản"); font.pixelSize: 10; Layout.fillWidth: true }
                }

                ClassroomPage { anchors.fill: parent; anchors.margins: 26; visible: root.page === "classroom"; classroom: root.classroom; bridge: root.bridgeRef }
                ReportsPage { anchors.fill: parent; anchors.margins: 26; visible: root.page === "reports"; classroom: root.classroom; bridge: root.bridgeRef }

                ScrollView {
                    anchors.fill: parent; anchors.margins: 30; visible: root.page === "glossary"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 20
                        Heading { text: "Thuật ngữ của thầy cô" }
                        Copy { text: "Giữ cách dùng từ nhất quán theo từng môn. Ứng dụng cũng nhớ các đoạn đã duyệt trong bài trước; khi có nhiều cách dịch, thầy cô được chọn."; Layout.fillWidth: true }
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
                        Copy { text: bridge.terms.length + " thuật ngữ đã lưu" }
                        Copy { visible: bridge.terms.length === 0; text: "Chưa có thuật ngữ. Thêm các từ cần dùng nhất quán trong bài giảng của thầy cô."; Layout.fillWidth: true }
                        Repeater { model: bridge.terms
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
                    }
                }

                ScrollView {
                    anchors.fill: parent; anchors.margins: 30; visible: root.page === "knowledge"; clip: true; contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width; spacing: 18
                        RowLayout { Layout.fillWidth: true
                            ColumnLayout { Layout.fillWidth: true; spacing: 6
                                Heading { text: "Kho kiến thức có nguồn" }
                                Copy { text: "Tra cứu nền tảng offline, xem nguồn chính thức và chọn từng thuật ngữ để đưa vào kho riêng của thầy cô."; Layout.fillWidth: true }
                            }
                            Action { text: "Cài gói kiến thức"; iconName: "upload"; primary: true; onClicked: knowledgeOpen.open() }
                        }
                        Surface { Layout.fillWidth: true; implicitHeight: knowledgeFilters.implicitHeight + 36
                            RowLayout { id: knowledgeFilters; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 18; spacing: 10
                                Field { id: knowledgeQuery; placeholderText: "Tìm thuật ngữ, môn học hoặc tiếng Anh"; Layout.fillWidth: true }
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
                        Repeater { model: bridge.searchKnowledge(knowledgeQuery.text, knowledgeSubject.text, knowledgeGrade.text)
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
                        Copy { visible: bridge.searchKnowledge(knowledgeQuery.text, knowledgeSubject.text, knowledgeGrade.text).length === 0; text: "Chưa có mục phù hợp. Hãy thử bỏ bớt bộ lọc hoặc cài một gói kiến thức mới."; Layout.fillWidth: true }
                        Caption { text: "Nguồn đã tích hợp"; font.pixelSize: 16 }
                        Repeater { model: bridge.knowledgeSources
                            delegate: Surface { required property var modelData; Layout.fillWidth: true; implicitHeight: sourceText.implicitHeight + 28
                                Copy { id: sourceText; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; text: modelData.title + "\n" + modelData.document_no + " · " + modelData.source_url; font.pixelSize: 11; wrapMode: Text.WordWrap }
                            }
                        }
                    }
                }

                SettingsPage {
                    id: settingsPanel
                    anchors.fill: parent; anchors.margins: 26; visible: root.page === "settings"
                    bridge: root.bridgeRef
                    onRequestModelPack: modelOpen.open()
                    onRequestBackup: backupOpen.open()
                    onRequestLibrary: libraryOpen.open()
                    onRequestLogo: logoOpen.open()
                }
            }
            Rectangle {
                Layout.fillWidth: true; implicitHeight: Math.max(38, statusMessage.implicitHeight + 20)
                color: bridge.error ? "#fff0eb" : bridge.busy ? "#eaf3ff" : "#ffffff"
                RowLayout { anchors.fill: parent; anchors.leftMargin: 25; anchors.rightMargin: 25; spacing: 10
                    BusyIndicator { visible: bridge.busy; running: bridge.busy; Layout.preferredWidth: 23; Layout.preferredHeight: 23 }
                    Label { id: statusMessage; text: bridge.message || "Sẵn sàng · Dữ liệu bài giảng được lưu tại máy"; color: bridge.error ? "#b14828" : root.muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                    Action { visible: bridge.busy; text: "Dừng tác vụ"; implicitHeight: 30; onClicked: bridge.cancelJob() }
                }
            }
        }
    }
    FileDialog { id: documentOpen; title: "Chọn tài liệu bài giảng"; nameFilters: ["Tài liệu (*.pptx *.docx *.pdf *.txt *.png *.jpg *.jpeg)"]; onAccepted: { root.selectedFile = selectedFile.toString(); root.selectedFileName = decodeURIComponent(selectedFile.toString().split("/").pop()); pasteInput.text = ""; if (!titleInput.text.trim()) titleInput.text = root.selectedFileName.replace(/\.[^.]+$/, ""); if (conversionProvider.currentIndex === 1) bridge.assessInput(root.selectedFile, sourceLanguage.currentIndex === 0 ? "vi" : "en"); else bridge.clearInputAssessment() } }
    FileDialog { id: chatgptDeckOpen; title: "Nhận PowerPoint đã tải từ ChatGPT"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.receiveChatGPTDeck(selectedFile.toString()) }
    FileDialog { id: logoOpen; title: "Chọn logo trường"; nameFilters: ["Ảnh (*.png *.jpg *.jpeg)"]; onAccepted: bridge.saveSchoolLogo(selectedFile.toString()) }
    FileDialog { id: packOpen; title: "Nhập gói bài BiliClass"; nameFilters: ["BiliClass (*.biliclass)"]; onAccepted: bridge.importPack(selectedFile.toString()) }
    FileDialog { id: deckSave; title: "Xuất PowerPoint song ngữ mới"; fileMode: FileDialog.SaveFile; defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.exportPowerPoint(selectedFile.toString()) }
    FileDialog { id: packSave; title: "Xuất gói bài BiliClass"; fileMode: FileDialog.SaveFile; defaultSuffix: "biliclass"; nameFilters: ["BiliClass (*.biliclass)"]; onAccepted: bridge.exportPack(selectedFile.toString()) }
    FileDialog { id: modelOpen; title: "Cài gói dịch ngoại tuyến"; nameFilters: ["BiliClass Language (*.bclanguage)"]; onAccepted: bridge.installModel(selectedFile.toString()) }
    FileDialog { id: knowledgeOpen; title: "Cài gói kiến thức có nguồn"; nameFilters: ["BiliClass Knowledge (*.biliknowledge)"]; onAccepted: bridge.installKnowledgePack(selectedFile.toString()) }
    FileDialog { id: backupOpen; title: "Khôi phục vào thư mục mới"; nameFilters: ["BiliClass Backup (*.bcbackup)"]; onAccepted: bridge.restoreLibrary(selectedFile.toString()) }
    FolderDialog { id: libraryOpen; title: "Chọn thư mục thư viện đã khôi phục"; onAccepted: root.requestAction(function() { bridge.openLibrary(libraryOpen.selectedFolder.toString()) }) }
    Dialog {
        id: wholeLessonReview; objectName: "wholeLessonReview"; anchors.centerIn: parent; modal: true
        title: "Xác nhận bài giảng để dạy"; width: Math.min(640, root.width - 80)
        ColumnLayout {
            width: parent.width; spacing: 16
            Copy { Layout.fillWidth: true; text: "Xác nhận thầy cô đã kiểm tra toàn bộ bản trình chiếu, gồm nội dung Việt–Anh, thuật ngữ, số liệu và bố cục. BiliClass sẽ lưu xác nhận cho cả bài và mở trình chiếu." }
            ScrollView {
                visible: (bridge.quickResult.warnings || []).length > 0; Layout.fillWidth: true; Layout.preferredHeight: 150; clip: true; contentWidth: availableWidth
                Copy { width: parent.width; text: (bridge.quickResult.warnings || []).join("\n\n"); color: "#a66318" }
            }
            RowLayout {
                Layout.fillWidth: true; Item { Layout.fillWidth: true }
                Action { text: "Xem lại bài"; onClicked: wholeLessonReview.close() }
                Action { objectName: "confirmWholeLessonButton"; text: "Đã kiểm tra · Trình chiếu"; primary: true; onClicked: { wholeLessonReview.close(); bridge.useConvertedLesson() } }
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
    Dialog { id: metadataDialog; anchors.centerIn: parent; modal: true; title: "Thông tin bài học"; width: 500
        onOpened: { metaTitle.text = bridge.lesson.title; metaSubject.text = bridge.lesson.subject; metaEducation.text = bridge.lesson.education_level; metaGrade.text = bridge.lesson.grade }
        contentItem: ColumnLayout { spacing: 12
            Field { id: metaTitle; placeholderText: "Tên bài"; Layout.fillWidth: true; maximumLength: 200 }
            Field { id: metaSubject; placeholderText: "Môn học"; Layout.fillWidth: true; maximumLength: 200 }
            RowLayout { Field { id: metaEducation; placeholderText: "Cấp học"; Layout.fillWidth: true; maximumLength: 200 } Field { id: metaGrade; placeholderText: "Khối"; Layout.fillWidth: true; maximumLength: 200 } }
            Copy { text: "Đổi môn sẽ đưa văn bản về trạng thái cần duyệt lại."; Layout.fillWidth: true }
            RowLayout { Action { text: "Đóng"; onClicked: metadataDialog.close() } Item { Layout.fillWidth: true } Action { text: "Lưu"; primary: true; onClicked: if (bridge.updateMetadata(metaTitle.text, metaSubject.text, metaEducation.text, metaGrade.text)) metadataDialog.close() } }
        }
    }
    Dialog {
        id: unsaved; objectName: "unsavedDialog"; anchors.centerIn: parent; modal: true; title: "Lưu thay đổi trước khi tiếp tục?"; width: 465
        contentItem: ColumnLayout { spacing: 19; Copy { text: "Đoạn đang chỉnh sửa chưa được lưu. Lưu nháp sẽ chuyển đoạn về trạng thái chờ duyệt."; Layout.fillWidth: true }
            RowLayout { Action { objectName: "stayButton"; text: "Ở lại"; onClicked: unsaved.close() } Action { text: "Bỏ thay đổi"; onClicked: { unsaved.close(); root.loadFields(); if (root.pendingAction) root.pendingAction() } } Action { text: "Lưu nháp"; primary: true; onClicked: { if (root.save(false)) { unsaved.close(); if (root.pendingAction) root.pendingAction() } } } }
    }
    }
    Dialog { id: replaceTranslation; anchors.centerIn: parent; modal: true; title: "Tạo lại bản dịch?"; width: 440; standardButtons: Dialog.Ok | Dialog.Cancel
        Copy { width: parent.width; text: "Bản dịch mới sẽ thay phần " + (root.translationSource === "vi" ? "tiếng Anh" : "tiếng Việt") + " hiện tại và cần được duyệt lại. Nội dung chỉ thay khi dịch thành công." }
        onAccepted: root.translateCurrent()
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
                Action { text: "Thử dịch máy"; enabled: root.translationSource === "vi" ? bridge.modelReady : bridge.reverseModelReady; onClicked: bridge.translateMemoryWithModel() }
                Item { Layout.fillWidth: true }
                Action { text: "Đóng"; onClicked: bridge.closeMemoryChoices() }
            }
        }
    }
    Dialog { id: reviewWarning; property string details: ""; anchors.centerIn: parent; modal: true; title: "Kiểm tra số và ký hiệu"; width: 540; standardButtons: Dialog.Ok | Dialog.Cancel
        Copy { width: parent.width; text: reviewWarning.details + "\n\nChỉ nhấn OK nếu thầy cô đã kiểm tra và muốn duyệt cặp này." }
        onAccepted: bridge.saveSegment(viEdit.text, enEdit.text, true, lockedCheck.checked)
    }
    Dialog { id: planRetryDialog; anchors.centerIn: parent; modal: true; title: "Gửi lại phần chưa xong?"; width: 500; standardButtons: Dialog.Ok | Dialog.Cancel
        Copy { width: parent.width; text: "Lượt trước bị ngắt, chưa rõ ChatGPT đã xử lý xong chưa. Gửi lại có thể dùng thêm hạn mức. Các phần đã nhận sẽ được dùng lại." }
        onAccepted: bridge.retryBrowserAI()
    }
    Dialog { id: busyDialog; anchors.centerIn: parent; modal: true; title: "Đang xử lý bài học"; standardButtons: Dialog.Ok; Copy { text: "Hãy chờ tác vụ hiện tại hoàn tất trước khi đóng ứng dụng." } }
    Dialog { id: updateBusyDialog; anchors.centerIn: parent; modal: true; title: "Đang tải bản cập nhật"; standardButtons: Dialog.Ok; Copy { text: "Chờ tải xong hoặc bấm Hủy tải ở Trang chủ trước khi đóng ứng dụng." } }
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
    CompanionWindow { id: companion; objectName: "companionWindow"; bridge: root.bridgeRef }
    TeachingDialog { id: teachingDialog; objectName: "teachingDialog"; teaching: root.teaching; bridge: root.bridgeRef }
    ProjectorWindow { id: projector; objectName: "projectorWindow"; bridge: root.bridgeRef }
    property var bridgeRef: bridge
    TemplateGallery {
        id: templateGallery; objectName: "templateGallery"
        bridge: root.bridgeRef
        onApplyPreset: function(preset) {
            if (forCreation) creationPreset.currentIndex = ["standard", "visual", "practice"].indexOf(preset)
            else bridge.setTeachingPreset(preset)
        }
    }

    Window {
        id: preview; objectName: "lessonPreview"; modality: Qt.NonModal; title: "BiliClass · Bàn điều khiển giảng dạy"; width: 1080; height: 730; minimumWidth: 800; minimumHeight: 600; color: "#f3f7fc"
        property bool showTools: false
        onClosing: { bridge.stopSpeech(); if (bridge.busy) bridge.cancelJob() }
        Shortcut { sequence: "Escape"; onActivated: preview.close() }
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 12
            RowLayout { Layout.fillWidth: true; Image { source: "book.svg"; sourceSize.width: 32; sourceSize.height: 32 } Caption { text: "BiliClass"; font.pixelSize: 21 } Item { Layout.fillWidth: true } Pill { text: "L" + bridge.policy.level + " · " + bridge.policy.name } Action { text: preview.showTools ? "Thu trợ giảng" : "Trợ giảng"; onClicked: preview.showTools = !preview.showTools } Action { text: preview.visibility === Window.FullScreen ? "Thu nhỏ" : "Toàn màn hình"; onClicked: preview.visibility === Window.FullScreen ? preview.showNormal() : preview.showFullScreen() } Action { text: "Đóng  ×"; onClicked: preview.close() } }
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
            Copy { visible: root.presentationContent.needs_easy_en; text: "L2: chưa có English đơn giản đã duyệt; đang xem bản dịch chính."; font.pixelSize: 11; Layout.fillWidth: true }
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
