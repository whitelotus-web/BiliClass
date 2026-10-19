import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    objectName: "settingsPage"
    required property var bridge
    signal requestBackup()
    signal requestLibrary()
    signal requestRelocation()
    signal requestBackupSave()
    signal requestSupportReport()
    signal requestLogo()
    signal requestReference()
    property int activeTab: 0
    property bool showGoogleKeyEntry: false
    property string draftVoice: bridge.voiceSettings.voice
    property int draftRate: bridge.voiceSettings.rate
    readonly property var selectedVoicePair: bridge.voicePairDetails(draftVoice)
    function pairPreviewText() { return [vietnameseSample.text.trim(), englishSample.text.trim()].filter(function(value) { return !!value }).join("\n") }
    function chooseVoicePair(vi, en) { bridge.stopSpeech(); draftVoice = bridge.composeVoicePair(vi, en) }
    readonly property bool voiceDirty: draftVoice !== bridge.voiceSettings.voice || draftRate !== bridge.voiceSettings.rate
    onActiveTabChanged: { if (contentScroll.contentItem && contentScroll.contentItem.contentY !== undefined) contentScroll.contentItem.contentY = 0 }
    property string selectedMascot: bridge.settings.mascot
    property int mascotPreviewMode: 0
    property string selectedAccessorySubject: bridge.mascotAccessorySubject
    property bool accessorySubjectOverridden: false
    readonly property var accessorySubjects: {
        const subjects = bridge.conversionSubjects.filter(function(subject) { return subject !== "Khác" })
        for (const subject of [bridge.mascotAccessorySubject, page.selectedAccessorySubject])
            if (subject && subjects.indexOf(subject) < 0) subjects.push(subject)
        return subjects
    }
    readonly property string previewSubject: accessorySubjectChoice.currentText
    readonly property bool wideMascotLayout: contentScroll.availableWidth >= 1020
    readonly property bool mascotPreviewVisible: true
    readonly property string mascotPreviewText: selectedMascot === "Lumi"
        ? (mascotPreviewMode === 1 ? "Let's look at this idea step by step." : mascotPreviewMode === 2 ? "Take your time. Let's try the next question." : "Let's take this one step at a time.")
        : (mascotPreviewMode === 1 ? "Watch how this idea works!" : mascotPreviewMode === 2 ? "Great job! Ready for the next question?" : "Let's explore something new together!")
    function showMascotPreview(name) {
        selectedMascot = name
        mascotPreviewMode = 0
        if (!wideMascotLayout) Qt.callLater(function() {
            var viewport = contentScroll.contentItem
            var offset = stageCard.mapToItem(viewport, 0, 0).y
            viewport.contentY = Math.min(viewport.contentHeight - viewport.height, Math.max(0, viewport.contentY + offset - 10))
        })
    }
    clip: true
    Dialog {
        id: renameGoogleKey; objectName: "renameGoogleKeyDialog"
        property string keyId: ""
        title: "Tên riêng của key"; modal: true; anchors.centerIn: parent
        width: Math.min(440, page.width - 32)
        standardButtons: Dialog.Save | Dialog.Cancel
        contentItem: ColumnLayout { spacing: 12
            Label { text: "Số Key được giữ nguyên. Để trống để dùng tên tự động; đổi tên không đổi nhóm đếm hay hạn mức."; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 12; color: page.muted }
            TextField { id: keyDisplayName; objectName: "keyDisplayNameInput"; Layout.fillWidth: true; maximumLength: 80; placeholderText: "Ví dụ: Gmail cá nhân" }
        }
        onAccepted: bridge.googleSettings.rename(keyId, keyDisplayName.text)
    }

    readonly property color ink: "#112650"
    readonly property color muted: "#667997"
    readonly property color blue: "#0869f9"
    readonly property color line: "#dfe8f4"

    component Card: Frame {
        padding: 22
        background: Rectangle { color: "white"; radius: 16; border.color: page.line }
    }
    component Title: Label { color: page.ink; font.pixelSize: 19; font.weight: Font.Bold; wrapMode: Text.WordWrap }
    component Hint: Label { color: page.muted; font.pixelSize: 13; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component Field: TextField {
        implicitHeight: 44; font.pixelSize: 13; color: page.ink; selectByMouse: true
        background: Rectangle { radius: 9; color: "#fbfdff"; border.color: parent.activeFocus ? page.blue : page.line }
    }
    component Choice: ComboBox {
        implicitHeight: 44; font.pixelSize: 13
        background: Rectangle { radius: 9; color: "#fbfdff"; border.color: parent.activeFocus ? page.blue : page.line }
    }
    component SaveButton: Button {
        id: saveButton
        implicitHeight: 44; leftPadding: 22; rightPadding: 22
        font.pixelSize: 13; font.weight: Font.DemiBold
        contentItem: Label { text: saveButton.text; color: "white"; font: saveButton.font; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { radius: 9; color: saveButton.down ? "#0053d2" : saveButton.hovered ? "#147aff" : page.blue }
    }
    component SoftButton: Button {
        id: softButton
        property string iconName: ""
        implicitHeight: 42; leftPadding: 13; rightPadding: 13
        font.pixelSize: 12; font.weight: Font.DemiBold
        contentItem: RowLayout {
            spacing: 6
            Item { Layout.fillWidth: true }
            Image { visible: !!softButton.iconName; source: softButton.iconName ? "../assets/actions/" + softButton.iconName + ".png" : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 22; Layout.preferredHeight: 22; opacity: softButton.enabled ? 1 : .4 }
            Label { text: softButton.text; color: softButton.enabled ? page.blue : page.muted; font: softButton.font; verticalAlignment: Text.AlignVCenter }
            Item { Layout.fillWidth: true }
        }
        background: Rectangle { radius: 9; color: softButton.hovered ? "#edf5ff" : "white"; border.color: page.line }
    }

    ColumnLayout {
        anchors.fill: parent; spacing: 15
        Label { objectName: "settingsPageTitle"; text: "Cài đặt"; color: page.ink; font.pixelSize: 37; font.weight: Font.Bold }
        Hint { objectName: "settingsPageDescription"; Layout.fillWidth: true
            text: ({
                0: "Thông tin thầy cô, trường học và các lựa chọn dùng chung trên máy.",
                1: "Phiên bản, bản quyền và thông tin cập nhật của BiliClass.",
                2: "Chọn giọng đọc và tốc độ mặc định cho bài giảng.",
                3: "Chọn bạn đồng hành, cách hiển thị và phím tắt khi dạy cùng Mascot.",
                4: "Thiết lập mặc định cho lớp học và cách học sinh tham gia.",
                5: "Quản lý nơi lưu bài giảng, sao lưu và khôi phục dữ liệu.",
                6: bridge.googleTranslation ? "Thêm key Google Dịch và xem số ký tự còn lại của từng key." : "Kết nối tài khoản AI để chuyển đổi bài giảng."
            })[page.activeTab] || "Thiết lập BiliClass trên máy này."
        }

        RowLayout {
            Layout.fillWidth: true; spacing: 5
            Repeater {
                model: [
                    {name: "Chung", icon: "settings", tabId: 0}, {name: bridge.googleTranslation ? "Google Dịch" : "Browser AI", icon: "bilingual", tabId: 6},
                    {name: "Giọng đọc", icon: "voice", tabId: 2}, {name: "Mascot", icon: "mascot", tabId: 3},
                    {name: "Lớp học", icon: "classroom", tabId: 4}, {name: "Dữ liệu", icon: "data", tabId: 5},
                    {name: "Thông tin BiliClass", icon: "about", tabId: 1}
                ]
                Button {
                    id: tab
                    required property var modelData
                    required property int index
                    objectName: "settingsTab" + modelData.tabId
                    Layout.fillWidth: true; Layout.preferredWidth: modelData.tabId === 1 ? 1.35 : 1; implicitHeight: 57
                    onClicked: page.activeTab = modelData.tabId
                    background: Rectangle {
                        color: page.activeTab === tab.modelData.tabId ? "#e7f2ff" : tab.hovered ? "#f5f8fc" : "transparent"
                        radius: 11
                        Rectangle { anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter; width: parent.width - 35; height: 2; color: page.blue; visible: page.activeTab === tab.modelData.tabId }
                    }
                    contentItem: RowLayout {
                        spacing: 7
                        Image {
                            source: tab.modelData.tabId === 1 ? "../assets/navigation/about.png" : "../assets/navigation/" + tab.modelData.icon + (page.activeTab === tab.modelData.tabId ? "-active" : "") + ".png"
                            // The supplied artwork has a wide transparent border.
                            sourceClipRect: tab.modelData.tabId === 1 ? Qt.rect(184, 214, 888, 888) : Qt.rect(0, 0, 0, 0)
                            sourceSize.width: tab.modelData.tabId === 1 ? 1254 : 64
                            sourceSize.height: tab.modelData.tabId === 1 ? 1254 : 64
                            fillMode: Image.PreserveAspectFit
                            Layout.preferredWidth: 27; Layout.preferredHeight: 27
                        }
                        Label { text: tab.modelData.name; color: page.activeTab === tab.modelData.tabId ? page.blue : page.ink; font.pixelSize: 13; font.weight: page.activeTab === tab.modelData.tabId ? Font.Bold : Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    }
                }
            }
        }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: page.line }

        ContentScrollView {
            id: contentScroll; outerGutter: true
            objectName: "settingsContentScroll"
            Layout.fillWidth: true; Layout.fillHeight: true; contentWidth: availableWidth
            ColumnLayout { width: contentScroll.availableWidth; spacing: 14

        RowLayout {
            visible: page.activeTab === 0; Layout.fillWidth: true; spacing: 14
            Card {
                Layout.fillWidth: true; Layout.preferredWidth: 2; Layout.alignment: Qt.AlignTop
                ColumnLayout { width: parent.width; spacing: 17
                    Title { text: "Thông tin thầy cô" }
                    Hint { text: "Hồ sơ dùng chung trên máy. Môn và khối lớp cụ thể được chọn cho từng bài; tên lớp được nhập khi bắt đầu tiết học."; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true; spacing: 16
                        ColumnLayout { Layout.fillWidth: true; spacing: 6; Label { text: "Tên thầy/cô"; color: page.ink } Field { id: teacherName; objectName: "settingsTeacher"; text: bridge.settings.teacher; maximumLength: 100; Layout.fillWidth: true } }
                        ColumnLayout { Layout.fillWidth: true; spacing: 6; Label { text: "Trường"; color: page.ink } Field { id: schoolName; objectName: "settingsSchool"; text: bridge.settings.school; placeholderText: "Ví dụ: THPT ..."; maximumLength: 100; Layout.fillWidth: true } }
                    }
                    ColumnLayout { Layout.fillWidth: true; spacing: 6
                        Label { text: "Bộ môn giảng dạy"; color: page.ink }
                        Choice {
                            id: teachingSubjects; objectName: "settingsSubjects"; Layout.fillWidth: true
                            model: bridge.conversionSubjects; leftPadding: 12; rightPadding: 36
                            currentIndex: { const subject = bridge.defaultTeachingSubject; const index = model.indexOf(subject); return !subject ? -1 : index >= 0 ? index : model.indexOf("Khác") }
                            displayText: currentIndex < 0 ? "Chọn bộ môn giảng dạy" : currentText
                            Accessible.name: "Bộ môn giảng dạy"
                            contentItem: Text { text: teachingSubjects.displayText; font: teachingSubjects.font; color: teachingSubjects.currentIndex < 0 ? page.muted : page.ink; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                            delegate: ItemDelegate {
                                required property string modelData
                                required property int index
                                width: teachingSubjectList.width - 16; height: 38; text: modelData; font: teachingSubjects.font
                                highlighted: teachingSubjects.highlightedIndex === index
                                contentItem: Text { text: parent.text; font: parent.font; color: page.ink; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                                background: Rectangle { radius: 5; color: parent.highlighted || parent.hovered ? "#e8f1ff" : "transparent" }
                            }
                            popup: Popup {
                                id: teachingSubjectPopup; objectName: "settingsSubjectPopup"
                                y: teachingSubjects.height + 4; width: Math.min(page.width - 32, Math.max(teachingSubjects.width, 400)); padding: 6
                                implicitHeight: Math.min(contentItem.implicitHeight + 12, 400, page.height - 60)
                                contentItem: ListView {
                                    id: teachingSubjectList; clip: true; implicitHeight: contentHeight
                                    model: teachingSubjectPopup.visible ? teachingSubjects.delegateModel : null
                                    currentIndex: teachingSubjects.highlightedIndex; highlightMoveDuration: 0
                                    ScrollBar.vertical: SlimScrollBar { }
                                }
                                background: Rectangle { color: "white"; radius: 8; border.color: page.line }
                            }
                        }
                        Field { id: otherTeachingSubject; objectName: "settingsCustomSubject"; visible: teachingSubjects.currentText === "Khác"; text: bridge.conversionSubjects.indexOf(bridge.defaultTeachingSubject) < 0 ? bridge.defaultTeachingSubject : ""; placeholderText: "Nhập tên môn học khác"; maximumLength: 100; Layout.fillWidth: true }
                        Hint { text: "Môn mặc định cho bài mới ở Chuyển đổi bài giảng. Thầy cô vẫn có thể chọn môn khác cho từng bài."; Layout.fillWidth: true }
                    }
                    RowLayout { Layout.fillWidth: true
                        SoftButton { objectName: "uploadSchoolLogo"; text: "Tải logo trường (PNG/JPG)"; iconName: "upload"; onClicked: page.requestLogo() }
                        SoftButton { objectName: "removeSchoolLogo"; text: "Bỏ logo"; enabled: !!bridge.schoolLogoUrl; onClicked: bridge.removeSchoolLogo() }
                        Item { Layout.fillWidth: true }
                    }
                    Hint { text: "Logo tối đa 5 MB, tự lưu vào thư viện khi chọn và đi cùng bản sao lưu."; Layout.fillWidth: true }
                    CheckBox { id: showProfile; objectName: "settingsShowProfile"; text: "Hiện tên, trường và logo trên màn hình bài giảng"; checked: bridge.settings.show_profile }
                    RowLayout { Layout.fillWidth: true; Hint { text: "Cấp học và khối lớp nhớ lần chọn gần nhất; mỗi buổi chọn tên lớp riêng."; Layout.fillWidth: true } SaveButton { objectName: "saveProfile"; text: "Lưu thông tin"; enabled: teachingSubjects.currentText !== "Khác" || !!otherTeachingSubject.text.trim(); onClicked: bridge.savePrimaryTeachingProfile(teacherName.text, schoolName.text, teachingSubjects.currentText === "Khác" ? otherTeachingSubject.text : teachingSubjects.currentText, showProfile.checked) } }
                }
            }
            Card {
                Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.alignment: Qt.AlignTop
                ColumnLayout { width: parent.width; spacing: 9
                    Title { text: "Xem trước hồ sơ đã lưu" }
                    Hint { text: "Tên, trường và bộ môn bên dưới chỉ đổi sau khi bấm Lưu thông tin; logo được lưu ngay khi tải lên."; Layout.fillWidth: true }
                    Rectangle { Layout.fillWidth: true; implicitHeight: 126; radius: 11; color: "#f2f7ff"
                        RowLayout { anchors.fill: parent; anchors.margins: 14; spacing: 10
                            Image { objectName: "savedProfileLogo"; visible: !!bridge.schoolLogoUrl; source: bridge.schoolLogoUrl; cache: false; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 56; Layout.preferredHeight: 70 }
                            Rectangle { visible: !bridge.schoolLogoUrl; Layout.preferredWidth: 56; Layout.preferredHeight: 56; radius: 10; color: "white"; border.color: page.line
                                Label { anchors.centerIn: parent; text: "Logo"; color: page.muted; font.pixelSize: 12 }
                            }
                            ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 5
                                Label { text: "BiliClass"; color: page.blue; font.pixelSize: 12 }
                                Label { objectName: "savedProfileTeacher"; text: bridge.settings.teacher || "Thầy cô"; color: page.ink; font.pixelSize: 17; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
                                Hint { objectName: "savedProfileSchool"; text: bridge.settings.school || "Chưa thêm trường"; Layout.fillWidth: true }
                                Hint { objectName: "savedProfileSubjects"; text: bridge.settings.subjects.length ? "Bộ môn: " + bridge.settings.subjects.join(", ") : "Chưa thêm bộ môn"; Layout.fillWidth: true }
                            }
                        }
                    }
                    Hint { objectName: "savedProfileVisibility"; text: bridge.settings.show_profile ? "Đang hiện tên, trường và logo trong bài giảng." : "Đang ẩn tên, trường và logo trong bài giảng."; Layout.fillWidth: true }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 1; Layout.fillWidth: true; spacing: 14
            Card {
                objectName: "aboutBiliClassCard"; Layout.fillWidth: true; padding: 22
                ColumnLayout { width: parent.width; spacing: 17
                    RowLayout { Layout.fillWidth: true; spacing: 22
                        Image { objectName: "aboutBiliClassLogo"; source: "../assets/brand/biliclass.svg"; sourceSize.width: 224; sourceSize.height: 224; Layout.preferredWidth: 88; Layout.preferredHeight: 88; fillMode: Image.PreserveAspectFit; Accessible.name: "Logo BiliClass" }
                        ColumnLayout { Layout.fillWidth: true; spacing: 8
                            Label { text: "Bili<span style='color:#ff7d2b'>Class</span>"; textFormat: Text.RichText; color: page.ink; font.pixelSize: 34; font.bold: true }
                            Label { text: "CHUYỂN NGỮ THÔNG MINH\nNÂNG TẦM BÀI GIẢNG"; color: page.muted; font.pixelSize: 10; font.letterSpacing: 0.6 }
                            Hint { text: bridge.appSubtitle; font.pixelSize: 16; Layout.fillWidth: true }
                        }
                    }
                    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: page.line }
                    RowLayout { Layout.fillWidth: true; spacing: 20
                        ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.alignment: Qt.AlignTop; spacing: 6
                            Hint { text: "PHIÊN BẢN"; font.pixelSize: 10; font.letterSpacing: 1 }
                            Title { objectName: "aboutBiliClassVersion"; text: bridge.appVersion }
                            Hint { text: bridge.developmentMode ? "Đang chạy từ mã nguồn" : "Ứng dụng BiliClass cho Windows"; Layout.fillWidth: true }
                            SoftButton { objectName: "aboutCheckUpdate"; text: bridge.updateState.checking ? "Đang kiểm tra…" : "Kiểm tra cập nhật"; iconName: "refresh"; enabled: !bridge.updateState.checking && !bridge.updateState.downloading; onClicked: bridge.checkForUpdates(false) }
                        }
                        ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 2; Layout.alignment: Qt.AlignTop; spacing: 7
                            Hint { text: "BẢN QUYỀN"; font.pixelSize: 10; font.letterSpacing: 1 }
                            Title { objectName: "aboutBiliClassCopyright"; text: "Copyright © 2026 Nguyễn Diệu Linh"; font.pixelSize: 17; Layout.fillWidth: true }
                            Hint { text: "Giáo viên Tin học · Trường THPT Vân\u00a0Cốc"; Layout.fillWidth: true }
                            Hint { text: "All rights reserved."; font.pixelSize: 11; Layout.topMargin: 4 }
                        }
                    }
                    Hint { text: "Chuyển tài liệu thành bài giảng Việt–Anh, trình chiếu và đồng hành cùng thầy cô với giọng đọc, mascot trợ giảng. Thư viện bài giảng được lưu trên máy."; Layout.fillWidth: true }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 2; Layout.fillWidth: true; spacing: 14
            Card {
                objectName: "multilingualVoiceCard"; Layout.fillWidth: true; padding: 15
                ColumnLayout { width: parent.width; spacing: 7
                    RowLayout { Layout.fillWidth: true
                        Title { text: "Cặp giọng gợi ý"; Layout.fillWidth: true }
                        Hint { text: "Hoàn toàn ngoại tuyến"; color: "#168567"; font.pixelSize: 12 }
                    }
                    Hint { text: "Chọn nhanh một cặp, hoặc tự ghép giọng Việt và giọng Anh ở bên dưới."; Layout.fillWidth: true }
                    Hint { visible: !bridge.vieneuReady; color: "#ba581a"; text: "Chưa tìm thấy đủ bộ giọng Việt–Mỹ. Hãy cài bản BiliClass đầy đủ."; Layout.fillWidth: true }
                    GridLayout {
                        objectName: "multilingualVoiceGrid"; Layout.fillWidth: true
                        columns: width >= 720 ? 3 : width >= 480 ? 2 : 1; rowSpacing: 6; columnSpacing: 12
                        Repeater {
                            model: bridge.suggestedVoicePairs
                            Frame {
                                id: voiceOption
                                required property var modelData
                                required property int index
                                objectName: "multilingualVoiceOption" + index
                                Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; padding: 3
                                background: Rectangle { radius: 9; color: page.draftVoice === voiceOption.modelData.id ? "#f2f7ff" : "#fbfdff"; border.color: page.draftVoice === voiceOption.modelData.id ? "#dce8f8" : page.line }
                                contentItem: RadioButton {
                                    id: suggestedVoice
                                    objectName: "selectMultilingualVoice" + voiceOption.index
                                    text: voiceOption.modelData.name; implicitHeight: 42
                                    leftPadding: 38; rightPadding: 8
                                    checked: page.draftVoice === voiceOption.modelData.id
                                    indicator: Rectangle {
                                        x: 8; y: (suggestedVoice.height - height) / 2
                                        implicitWidth: 18; implicitHeight: 18; radius: 9
                                        color: "white"; border.color: suggestedVoice.checked ? page.blue : "#b9c9de"
                                        Rectangle { anchors.centerIn: parent; width: 10; height: 10; radius: 5; color: page.blue; visible: suggestedVoice.checked }
                                    }
                                    onClicked: { bridge.stopSpeech(); page.draftVoice = voiceOption.modelData.id }
                                    contentItem: Column {
                                        spacing: 3
                                        Label { text: voiceOption.modelData.label; color: page.ink; font.pixelSize: 13; font.weight: Font.DemiBold }
                                        Label { text: voiceOption.modelData.subtitle; color: page.muted; font.pixelSize: 12 }
                                    }
                                }
                            }
                        }
                    }
                    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: page.line; Layout.topMargin: 2; Layout.bottomMargin: 2 }
                    GridLayout {
                        objectName: "customVoiceColumns"; Layout.fillWidth: true
                        columns: width >= 650 ? 2 : 1; columnSpacing: 24; rowSpacing: 16
                        ColumnLayout {
                            objectName: "vietnameseVoiceColumn"; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; spacing: 8
                            Label { text: "Giọng tiếng Việt"; color: page.ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                            RowLayout { Layout.fillWidth: true; spacing: 8
                                Choice {
                                    objectName: "settingsVietnameseVoice"; Layout.fillWidth: true; Layout.minimumWidth: 0
                                    model: bridge.vietnameseVoices; textRole: "name"; valueRole: "id"
                                    currentIndex: model.map(function(row) { return row.id }).indexOf(page.selectedVoicePair.vi)
                                    enabled: model.length > 0
                                    onActivated: page.chooseVoicePair(currentValue, page.selectedVoicePair.en || bridge.englishVoices[0].id)
                                    Accessible.name: "Chọn giọng tiếng Việt để tự ghép cặp"
                                }
                                SoftButton { objectName: "previewVietnameseVoice"; text: "Nghe thử"; iconName: "play"; implicitHeight: 44
                                    enabled: !!page.selectedVoicePair.vi && !!vietnameseSample.text.trim()
                                    onClicked: bridge.previewNarrationLanguage("vi", page.draftVoice, page.draftRate, vietnameseSample.text)
                                }
                            }
                            TextArea {
                                id: vietnameseSample; objectName: "settingsVoiceSample"; Layout.fillWidth: true
                                implicitHeight: 88; padding: 10; font.pixelSize: 13; color: page.ink; wrapMode: TextEdit.Wrap; selectByMouse: true
                                text: bridge.voicePreviewSamples.vi; Accessible.name: "Nội dung nghe thử tiếng Việt"
                                background: Rectangle { radius: 9; color: "#fbfdff"; border.color: vietnameseSample.activeFocus ? page.blue : page.line }
                            }
                        }
                        ColumnLayout {
                            objectName: "englishVoiceColumn"; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0; spacing: 8
                            Label { text: "Giọng tiếng Anh · Mỹ"; color: page.ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                            RowLayout { Layout.fillWidth: true; spacing: 8
                                Choice {
                                    objectName: "settingsEnglishVoice"; Layout.fillWidth: true; Layout.minimumWidth: 0
                                    model: bridge.englishVoices; textRole: "name"; valueRole: "id"
                                    currentIndex: model.map(function(row) { return row.id }).indexOf(page.selectedVoicePair.en)
                                    enabled: model.length > 0
                                    onActivated: page.chooseVoicePair(page.selectedVoicePair.vi || bridge.vietnameseVoices[0].id, currentValue)
                                    Accessible.name: "Chọn giọng tiếng Anh để tự ghép cặp"
                                }
                                SoftButton { objectName: "previewEnglishVoice"; text: "Nghe thử"; iconName: "play"; implicitHeight: 44
                                    enabled: !!page.selectedVoicePair.en && !!englishSample.text.trim()
                                    onClicked: bridge.previewNarrationLanguage("en", page.draftVoice, page.draftRate, englishSample.text)
                                }
                            }
                            TextArea {
                                id: englishSample; objectName: "settingsEnglishVoiceSample"; Layout.fillWidth: true
                                implicitHeight: 88; padding: 10; font.pixelSize: 13; color: page.ink; wrapMode: TextEdit.Wrap; selectByMouse: true
                                text: bridge.voicePreviewSamples.en; Accessible.name: "Nội dung nghe thử tiếng Anh"
                                background: Rectangle { radius: 9; color: "#fbfdff"; border.color: englishSample.activeFocus ? page.blue : page.line }
                            }
                        }
                    }
                    RowLayout { Layout.fillWidth: true; spacing: 12
                        Label { text: "Tốc độ đọc"; color: page.ink; font.weight: Font.DemiBold }
                        Slider {
                            id: voiceRate; objectName: "settingsVoiceRate"; Layout.fillWidth: true
                            from: -3; to: 3; stepSize: 1; snapMode: Slider.SnapAlways
                            value: page.draftRate; onMoved: page.draftRate = Math.round(value)
                            enabled: bridge.multilingualVoices.length > 0
                            Accessible.name: "Tốc độ đọc từ 82 đến 118 phần trăm"
                        }
                        Label { objectName: "settingsVoiceSpeedLabel"; text: Math.round([.82, .88, .94, 1, 1.06, 1.12, 1.18][page.draftRate + 3] * 100) + "%"; color: page.blue; font.weight: Font.Bold; font.pixelSize: 16 }
                        SoftButton { objectName: "resetVoiceSpeed"; text: "100%"; implicitHeight: 36; onClicked: page.draftRate = 0 }
                    }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 3; Layout.fillWidth: true; spacing: 14
            GridLayout {
                Layout.fillWidth: true; columns: page.wideMascotLayout ? 3 : 2; columnSpacing: 12; rowSpacing: 12
                Repeater { model: [
                    {name: "Milo", image: "../assets/milo-welcome.png", mood: "Năng động · vui vẻ", detail: "Mang năng lượng tích cực vào lớp học.", strengths: ["Khởi động bài", "Hỏi lớp nhanh", "Khích lệ học sinh", "Hoạt động quiz"]},
                    {name: "Lumi", image: "../assets/lumi-welcome.png", mood: "Bình tĩnh · thân thiện", detail: "Đồng hành nhẹ nhàng qua từng ý học.", strengths: ["Giải thích rõ", "Đọc từ vựng", "VI Rescue", "Củng cố cuối bài"]}
                ]
                    Rectangle { id: mascotCard; required property var modelData; required property int index
                        readonly property bool chosen: page.selectedMascot === modelData.name
                        Layout.row: 0; Layout.column: index; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.preferredHeight: 300
                        radius: 16; color: chosen ? "#f2f7ff" : "white"; border.color: chosen ? "#dce8f8" : page.line; border.width: 1
                        MouseArea { objectName: "mascot" + mascotCard.modelData.name; anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: page.showMascotPreview(mascotCard.modelData.name) }
                        ColumnLayout { anchors.fill: parent; anchors.margins: 13; spacing: 7
                            RowLayout { Layout.fillWidth: true
                                Label { text: mascotCard.chosen ? "●  Đang chọn" : "○  Chọn bạn này"; color: mascotCard.chosen ? page.blue : page.muted; font.pixelSize: 12; font.bold: true }
                                Item { Layout.fillWidth: true }
                                Label { text: mascotCard.modelData.name === "Milo" ? "01 / NĂNG LƯỢNG" : "02 / ĐIỀM TĨNH"; color: page.muted; font.pixelSize: 9; font.bold: true }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 8
                                Image { source: mascotCard.modelData.image; Layout.preferredWidth: 118; Layout.preferredHeight: 139; fillMode: Image.PreserveAspectFit; sourceSize.width: 236; sourceSize.height: 278 }
                                ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
                                    Label { text: mascotCard.modelData.name; color: page.ink; font.pixelSize: 25; font.bold: true }
                                    Label { text: mascotCard.modelData.mood; color: mascotCard.modelData.name === "Milo" ? page.blue : "#a66b24"; font.pixelSize: 12; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    Hint { text: mascotCard.modelData.detail; Layout.fillWidth: true; font.pixelSize: 11 }
                                }
                            }
                            Rectangle { Layout.fillWidth: true; height: 1; color: page.line }
                            Label { text: "PHÙ HỢP KHI"; color: page.muted; font.pixelSize: 10; font.bold: true }
                            GridLayout { Layout.fillWidth: true; columns: 2; columnSpacing: 4; rowSpacing: 4
                                Repeater { model: mascotCard.modelData.strengths
                                    Label { required property string modelData; text: "✓  " + modelData; color: page.ink; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true; Layout.preferredWidth: 1 }
                                }
                            }
                            Item { Layout.fillHeight: true }
                        }
                    }
                }
                Rectangle { id: stageCard
                    Layout.row: page.wideMascotLayout ? 0 : 1; Layout.column: page.wideMascotLayout ? 2 : 0
                    Layout.columnSpan: page.wideMascotLayout ? 1 : 2; Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.preferredHeight: 300
                    radius: 16; color: "white"; border.color: page.line
                    ColumnLayout { anchors.fill: parent; anchors.margins: 13; spacing: 8
                        RowLayout { Layout.fillWidth: true
                            Label { text: "Xem trước khi dạy"; color: page.ink; font.pixelSize: 17; font.bold: true; Layout.fillWidth: true }
                            Label { text: "TRÊN MÀN CHIẾU"; color: page.blue; font.pixelSize: 9; font.bold: true }
                        }
                        Rectangle { id: mascotMiniSlide; objectName: "mascotMiniSlide"; Layout.fillWidth: true; Layout.fillHeight: true; radius: 12; clip: true; color: "#dcecff"
                            Rectangle { anchors.fill: parent; anchors.margins: 8; radius: 10; color: "#fafdff"; border.color: "#b7d5f8" }
                            Label { anchors.left: parent.left; anchors.leftMargin: 20; anchors.top: parent.top; anchors.topMargin: 17; text: page.mascotPreviewMode === 2 ? "CÂU HỎI NHANH" : page.mascotPreviewMode === 1 ? "GIẢI THÍCH" : "BÀI GIẢNG SONG NGỮ"; color: page.blue; font.pixelSize: 10; font.bold: true }
                            Label { anchors.left: parent.left; anchors.leftMargin: 20; anchors.top: parent.top; anchors.topMargin: 41; width: parent.width - 115; text: page.mascotPreviewMode === 2 ? "Cả lớp sẵn sàng chưa?" : page.mascotPreviewMode === 1 ? "Cùng hiểu từng bước" : "Cùng khám phá bài học"; color: page.ink; font.pixelSize: 14; font.bold: true; wrapMode: Text.WordWrap }
                            Rectangle { visible: page.mascotPreviewVisible; width: Math.max(110, Math.min(parent.width - mascotPreview.width - 36, 225)); height: Math.max(53, previewBubbleText.implicitHeight + 16); radius: 14; color: "white"; border.color: "#bed5f4"; anchors.top: parent.top; anchors.topMargin: 82; x: 18
                                Label { id: previewBubbleText; width: parent.width - 16; anchors.centerIn: parent; text: page.mascotPreviewText; color: page.ink; font.pixelSize: 11; font.bold: true; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter; textFormat: Text.PlainText }
                            }
                            Mascot { id: mascotPreview; objectName: "mascotPreview"; visible: page.mascotPreviewVisible; character: page.selectedMascot; expression: page.mascotPreviewMode === 1 ? "thinking" : page.mascotPreviewMode === 2 ? "celebrate" : "speaking"; subject: page.previewSubject; showSubjectBadge: false; accessories: mascotAccessories.checked; reducedMotion: reducedMotion.checked; width: Math.max(85, Math.min(120, mascotSize.value * .82)); height: width + 25; anchors.bottom: parent.bottom; anchors.bottomMargin: 5; x: parent.width - width - 16 }
                        }
                        RowLayout { Layout.fillWidth: true; spacing: 5
                            Repeater { model: ["Slide", "Giải thích", "Quiz"]
                                Button { id: contextButton; required property string modelData; required property int index; objectName: "mascotPreviewMode" + index; text: modelData; Layout.fillWidth: true; implicitHeight: 34; onClicked: page.mascotPreviewMode = index
                                    background: Rectangle { radius: 8; color: page.mascotPreviewMode === contextButton.index ? "#e8f2ff" : "white"; border.color: page.mascotPreviewMode === contextButton.index ? page.blue : page.line }
                                    contentItem: Label { text: contextButton.text; color: page.mascotPreviewMode === contextButton.index ? page.blue : page.muted; font.pixelSize: 11; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                        }
                        Hint { text: "Chọn nhân vật để xem trước. Nghe thử và chọn giọng tại Cài đặt → Giọng đọc."; Layout.fillWidth: true; font.pixelSize: 10 }
                    }
                }
            }
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 13
                    Title { text: "Cách hiển thị trong lớp" }
                    Hint { text: "Chọn phụ kiện và cách hiển thị. Xem trước thay đổi ngay; bấm Lưu để áp dụng."; Layout.fillWidth: true }
                    GridLayout { Layout.fillWidth: true; columns: page.width >= 800 ? 2 : 1; columnSpacing: 20; rowSpacing: 12
                    RowLayout { Layout.fillWidth: true; Layout.preferredWidth: 500; Layout.alignment: Qt.AlignVCenter; spacing: 10
                        CheckBox { id: mascotAccessories; objectName: "mascotAccessories"; text: "Hiện phụ kiện"; checked: bridge.mascotSettings.accessories }
                        CheckBox { id: reducedMotion; objectName: "mascotReducedMotion"; text: "Giảm chuyển động"; checked: bridge.mascotSettings.reduced_motion }
                        CheckBox { id: mascotOnTop; objectName: "mascotAlwaysOnTop"; text: "Luôn nổi trên cùng"; checked: bridge.mascotSettings.always_on_top }
                    }
                    ColumnLayout { objectName: "mascotAccessorySummary"; Layout.fillWidth: true; Layout.preferredWidth: 280; Layout.alignment: Qt.AlignVCenter; spacing: 5
                        Label { text: "Chọn phụ kiện theo môn"; color: page.ink; font.bold: true; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                        Choice { id: accessorySubjectChoice; objectName: "mascotAccessorySubject"; Layout.fillWidth: true; model: page.accessorySubjects; currentIndex: Math.max(0, model.indexOf(page.selectedAccessorySubject)); onActivated: { page.selectedAccessorySubject = currentText; page.accessorySubjectOverridden = true } }
                        Hint { objectName: "mascotThemeDescription"; text: mascotAccessories.checked ? mascotPreview.theme.label : "Phụ kiện đang tắt"; Layout.fillWidth: true; font.pixelSize: 11 }
                    }
                    }
                    Rectangle { Layout.fillWidth: true; height: 1; color: page.line }
                    ColumnLayout { Layout.fillWidth: true; spacing: 5
                        RowLayout { Layout.fillWidth: true; Label { text: "Kích thước Mascot và bảng trợ giảng"; color: page.ink; font.bold: true; Layout.fillWidth: true } Hint { text: Math.round(mascotSize.value) + " px" } }
                        RowLayout { Layout.fillWidth: true; spacing: 8
                            Slider { id: mascotSize; objectName: "mascotSize"; from: 60; to: 160; value: bridge.mascotSettings.size; Layout.fillWidth: true }
                            Repeater { model: [{label:"Nhỏ",size:80},{label:"Vừa",size:110},{label:"Lớn",size:150}]
                                Button { id: sizeChoice; required property var modelData; objectName: "mascotSize" + modelData.size; text: modelData.label; implicitWidth: 58; implicitHeight: 34; onClicked: mascotSize.value = modelData.size
                                    background: Rectangle { radius: 8; color: Math.abs(mascotSize.value - sizeChoice.modelData.size) < 16 ? "#e8f2ff" : "white"; border.color: Math.abs(mascotSize.value - sizeChoice.modelData.size) < 16 ? page.blue : page.line }
                                    contentItem: Label { text: sizeChoice.text; color: page.ink; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                        }
                    }
                    Hint { text: "Bảng trợ giảng đổi cỡ cùng nhân vật. Bấm Lưu để áp dụng cả hai."; Layout.fillWidth: true }
                    ColumnLayout { Layout.fillWidth: true; spacing: 5
                        RowLayout { Layout.fillWidth: true
                            Label { text: "Độ trong suốt của nền bảng"; color: page.ink; font.bold: true; Layout.fillWidth: true }
                            Hint { text: bridge.companionPanelOpacity === 100 ? "0% · Nền đặc" : (100 - bridge.companionPanelOpacity) + "%" }
                        }
                        Slider { objectName: "companionPanelTransparency"; from: 0; to: 70; stepSize: 1; value: 100 - bridge.companionPanelOpacity; Layout.fillWidth: true; onMoved: bridge.setCompanionPanelOpacity(100 - Math.round(value)); onPressedChanged: if (!pressed) bridge.flushCompanionAppearance() }
                        Hint { text: "Chỉ làm trong nền, chữ và nút vẫn rõ và bấm như cũ. Thay đổi tự lưu."; Layout.fillWidth: true }
                    }
                    RowLayout { Layout.fillWidth: true; Hint { text: "Kéo Mascot hoặc bảng để di chuyển; bấm ↓ để thu bảng. Đóng BiliClass sẽ tắt Mascot."; Layout.fillWidth: true } SaveButton { objectName: "saveMascot"; text: bridge.mascotSaving ? "Đang lưu…" : "Lưu cài đặt Mascot"; enabled: !bridge.mascotSaving; onClicked: bridge.saveMascotPreferences(page.selectedMascot, true, Math.round(mascotSize.value), "right", reducedMotion.checked, mascotAccessories.checked, true, true, page.accessorySubjectOverridden || bridge.mascotSettings.subject_mode === "fixed" ? "fixed" : "auto", accessorySubjectChoice.currentText, mascotOnTop.checked) } }
                }
            }
            Card { Layout.fillWidth: true
                MascotShortcuts { objectName: "mascotShortcutPanel"; width: parent.width; settings: bridge.mascotShortcuts }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 4; Layout.fillWidth: true; spacing: 14
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 16
                    Title { text: "Mặc định khi mở lớp học" }
                    Hint { text: "Giúp bắt đầu tiết học nhanh hơn. Thầy cô vẫn đổi được từng mục ngay trước khi bắt đầu lớp hoặc mở câu hỏi."; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true; spacing: 16
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Cách tham gia"; color: page.ink } Choice { id: classMode; objectName: "settingsClassMode"; model: ["Ẩn danh", "Số chỗ ngồi"]; currentIndex: bridge.classroomSettings.mode === "seat" ? 1 : 0; Layout.fillWidth: true } }
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Sĩ số tối đa"; color: page.ink } SpinBox { id: classCapacity; objectName: "settingsClassCapacity"; from: 1; to: 200; value: bridge.classroomSettings.capacity; editable: true; Layout.fillWidth: true } }
                    }
                    RowLayout { Layout.fillWidth: true; spacing: 16
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Thời gian trả lời mặc định"; color: page.ink } SpinBox { id: classDuration; from: 5; to: 3600; value: bridge.classroomSettings.duration; editable: true; Layout.fillWidth: true } }
                        ColumnLayout { Layout.fillWidth: true; Label { text: "Ngôn ngữ câu hỏi"; color: page.ink } Choice { id: classLanguage; model: ["Việt–Anh", "Tiếng Việt", "English"]; currentIndex: ["both", "vi", "en"].indexOf(bridge.classroomSettings.language); Layout.fillWidth: true } }
                    }
                    Hint { text: "QR và địa chỉ LAN được tạo theo mạng thật lúc bắt đầu lớp. Nếu mạng hoặc cổng đổi, ứng dụng báo QR mới; học sinh có thể dùng mã khôi phục."; Layout.fillWidth: true }
                    SaveButton { objectName: "saveClassroom"; text: "Lưu mặc định lớp học"; Layout.alignment: Qt.AlignRight; onClicked: bridge.saveClassroomSettings(classMode.currentIndex ? "seat" : "anonymous", classCapacity.value, classDuration.value, ["both", "vi", "en"][classLanguage.currentIndex]) }
                }
            }
        }

        ColumnLayout {
            visible: page.activeTab === 5; Layout.fillWidth: true; spacing: 14
            onVisibleChanged: if (visible) bridge.storageControls.refresh()
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 14
                    Title { text: "Nơi lưu bài giảng và giọng đọc" }
                    Hint { text: "Ứng dụng và thư viện lưu riêng. Chọn ổ D, E hoặc thư mục khác để tránh đầy ổ C."; Layout.fillWidth: true }
                    Hint { text: bridge.dataPath; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: page.ink }
                    Hint { objectName: "storageFreeSpace"; text: bridge.storageControls.state.free_bytes >= 0 ? "Ổ lưu còn " + (bridge.storageControls.state.free_bytes / 1073741824).toFixed(1) + " GiB trống" : "Chưa đọc được dung lượng ổ lưu"; Layout.fillWidth: true }
                    Hint {
                        objectName: "storageBackupStatus"
                        readonly property var backup: bridge.storageControls.state
                        text: backup.running ? "Đang sao lưu" + (backup.total ? " · " + backup.done + "/" + backup.total + " tệp" : "…")
                            : backup.status === "failed" ? "Sao lưu chưa thành công: " + backup.last_error
                            : backup.last_success ? "Sao lưu thành công gần nhất: " + new Date(backup.last_success).toLocaleString()
                            : "Chưa có bản sao lưu được xác nhận"
                        color: backup.status === "failed" && !backup.running ? "#a63d2f" : page.ink
                        Layout.fillWidth: true
                    }
                    Hint { visible: !!bridge.storageControls.state.last_path; text: bridge.storageControls.state.last_path || ""; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere }
                    Hint { text: bridge.storageControls.state.scope || ""; Layout.fillWidth: true }
                    Flow { Layout.fillWidth: true; spacing: 8
                        SaveButton { objectName: "relocateLibraryButton"; text: "Chuyển thư viện sang nơi khác"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: page.requestRelocation() }
                        SoftButton { text: "Mở thư mục"; onClicked: bridge.openData() }
                        SoftButton { objectName: "settingsBackup"; text: "Sao lưu thư viện"; enabled: !bridge.busy && !bridge.storageControls.state.running; onClicked: page.requestBackupSave() }
                        SoftButton { text: "Khôi phục bản sao"; enabled: !bridge.busy && !bridge.storageControls.state.running; onClicked: page.requestBackup() }
                        SoftButton { text: "Mở thư viện khác"; enabled: !bridge.busy; onClicked: page.requestLibrary() }
                        SoftButton { text: "Xuất chẩn đoán kỹ thuật"; enabled: !bridge.busy; onClicked: page.requestSupportReport() }
                    }
                    Hint { text: "Chuyển cả bài giảng, giọng, thuật ngữ và cấu hình; BiliClass kiểm tra rồi mở lại với thư viện mới. Bản cũ chỉ được dọn sau khi mở thành công."; Layout.fillWidth: true }
                    Hint { text: "Tải file: tên được gợi ý tự động; bạn chọn nơi lưu và BiliClass nhớ thư mục đã chọn."; Layout.fillWidth: true }
                }
            }
            Card { Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 12
                    Title { text: "Thuật ngữ & kiến thức · nâng cao" }
                    Hint { text: "Thuật ngữ đã khóa được dùng khi dịch đúng môn. Mở kho khi cần sửa cách dịch hoặc tra cứu; không cần thao tác ở đây mỗi lần tạo bài."; Layout.fillWidth: true }
                    SoftButton { objectName: "settingsReferenceButton"; text: "Quản lý thuật ngữ & kiến thức"; onClicked: page.requestReference() }
                }
            }
        }
        ColumnLayout {
            visible: bridge.googleTranslation && page.activeTab === 6; Layout.fillWidth: true; spacing: 14
            onVisibleChanged: if (visible) bridge.googleSettings.refresh()
            Card {
                Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 14
                    RowLayout { Layout.fillWidth: true; spacing: 12
                        Title { text: "Google Cloud Translation"; Layout.fillWidth: true }
                        SoftButton { objectName: "toggleGoogleKeyEntry"; visible: bridge.googleSettings.state.configured; text: page.showGoogleKeyEntry ? "Ẩn ô nhập" : "Thêm key"; onClicked: page.showGoogleKeyEntry = !page.showGoogleKeyEntry }
                        SoftButton {
                            id: googleKeyGuide; objectName: "googleKeyGuideButton"
                            text: "Hướng dẫn lấy Key"
                            Accessible.description: googleKeyGuideTip.text
                            onClicked: googleKeyGuideTip.open()
                            ToolTip {
                                id: googleKeyGuideTip; objectName: "googleKeyGuideTip"
                                visible: googleKeyGuide.hovered || googleKeyGuide.activeFocus
                                delay: 350; timeout: -1
                                width: Math.min(440, page.width - 32); padding: 14
                                closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
                                text: "Hướng dẫn lấy Key Google Cloud\n\n1. Bấm Lấy key, đăng nhập Google và chọn hoặc tạo dự án.\n2. Bật thanh toán cho dự án.\n3. Vào APIs & Services → Library, tìm và bật Cloud Translation API.\n4. Vào Credentials → Create credentials → API key.\n5. Giới hạn key chỉ dùng Cloud Translation API rồi sao chép key.\n6. Dán vào ô bên dưới, mỗi dòng: Tên dự án | key, rồi bấm Lưu key.\n\nDùng key Google Cloud Translation, không phải key Gemini."
                                contentItem: Label {
                                    text: googleKeyGuideTip.text; color: page.ink
                                    font.pixelSize: 13; wrapMode: Text.WordWrap
                                    textFormat: Text.PlainText
                                }
                                background: Rectangle { radius: 9; color: "#f7faff"; border.color: page.line }
                            }
                        }
                        SoftButton {
                            objectName: "getGoogleApiKey"; text: "Lấy key"
                            Accessible.name: "Mở Google Cloud để tạo API key"
                            onClicked: Qt.openUrlExternally("https://console.cloud.google.com/apis/credentials")
                            ToolTip.visible: hovered
                            ToolTip.text: "Mở trang quản lý API key trên Google Cloud"
                        }
                    }
                    Hint { text: "Dùng key theo thứ tự; tự chuyển khi hết giới hạn hoặc bị từ chối."; Layout.fillWidth: true }
                    Label { visible: !bridge.googleSettings.state.configured || page.showGoogleKeyEntry; text: "API key · mỗi key một dòng"; color: page.ink; font.bold: true }
                    ContentScrollView {
                        visible: !bridge.googleSettings.state.configured || page.showGoogleKeyEntry
                        Layout.fillWidth: true; Layout.preferredHeight: 130;
                        TextArea {
                            id: googleKeys; objectName: "googleApiKeys"; selectByMouse: true; wrapMode: TextEdit.NoWrap
                            placeholderText: "Tên dự án | API_KEY\nTên dự án khác | API_KEY\nHoặc chỉ nhập key trên mỗi dòng"
                            color: page.ink; font.pixelSize: 13
                            background: Rectangle { radius: 9; color: "#fbfdff"; border.color: page.line }
                        }
                    }
                    Hint { visible: !bridge.googleSettings.state.configured || page.showGoogleKeyEntry; text: "Mỗi key một dòng; có thể ghi Tên dự án | key. Mỗi key có bộ đếm riêng, mặc định tối đa 500.000 ký tự/tháng tại máy."; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true; spacing: 12
                        visible: !bridge.googleSettings.state.configured || page.showGoogleKeyEntry
                        Item { Layout.fillWidth: true }
                        SaveButton { objectName: "saveGoogleApiKeys"; text: "Lưu key"; enabled: !bridge.busy; onClicked: { if (bridge.googleSettings.save(googleKeys.text, bridge.googleSettings.state.budget)) { googleKeys.clear(); page.showGoogleKeyEntry = false } } }
                    }
                    Hint { text: "Key được mã hóa và lưu trên máy này."; Layout.fillWidth: true; font.pixelSize: 11 }
                }
            }
            Card {
                Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 13
                    RowLayout { Layout.fillWidth: true
                        Title { text: "Key đã lưu"; Layout.fillWidth: true }
                        SoftButton { objectName: "recheckGoogleApiKeys"; visible: bridge.googleSettings.state.keys.some(function(row) { return !!row.blocked }); text: "Thử lại key đã kiểm tra"; enabled: !bridge.busy; onClicked: bridge.googleSettings.recheck() }
                    }
                    Hint { visible: !bridge.googleSettings.state.configured; text: bridge.googleSettings.state.message || "Chưa có API key. Thêm key ở trên để bắt đầu."; Layout.fillWidth: true }
                    Repeater {
                        model: bridge.googleSettings.state.keys
                        delegate: RowLayout {
                            required property var modelData
                            Layout.fillWidth: true
                            ColumnLayout { Layout.fillWidth: true; spacing: 4
                                Label { text: modelData.name + " · " + modelData.label; color: page.ink; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
                                Hint { objectName: "googleKeyRemaining_" + modelData.id; text: "Còn " + Number(modelData.remaining).toLocaleString(Qt.locale("vi_VN"), "f", 0) + " / " + Number(modelData.budget).toLocaleString(Qt.locale("vi_VN"), "f", 0) + " ký tự"; color: modelData.blocked || modelData.remaining <= 0 ? "#b14828" : page.muted; Layout.fillWidth: true }
                                ProgressBar { objectName: "googleKeyProgress_" + modelData.id; Layout.fillWidth: true; from: 0; to: 100; value: modelData.percent
                                    background: Rectangle { implicitHeight: 5; radius: 2; color: "#e8eef7" }
                                    contentItem: Item { implicitHeight: 5; Rectangle { width: parent.width * Math.min(1, modelData.percent / 100); height: parent.height; radius: 2; color: modelData.percent >= 95 ? "#b14828" : modelData.percent >= 80 ? "#d59020" : "#168567" } }
                                }
                                Hint { visible: !!modelData.blocked || modelData.remaining <= 0; text: modelData.blocked ? "Key bị từ chối; tool sẽ thử key khác. Có thể kiểm tra rồi cho phép thử lại." : "Đã dùng hết giới hạn tháng này; tool tự chuyển key khác."; color: "#b14828"; Layout.fillWidth: true; font.pixelSize: 11 }
                            }
                            SoftButton { objectName: "renameGoogleKey_" + modelData.id; text: "Đổi tên"; enabled: !bridge.busy; onClicked: { renameGoogleKey.keyId = modelData.id; keyDisplayName.text = modelData.customName; renameGoogleKey.open() } }
                            SoftButton { text: "Xóa key"; enabled: !bridge.busy; onClicked: bridge.googleSettings.remove(modelData.id) }
                        }
                    }
                }
            }
        }

        ColumnLayout {
            visible: !bridge.googleTranslation && page.activeTab === 6; Layout.fillWidth: true; spacing: 14
            onVisibleChanged: { if (visible && bridge.browserAI.webMode) bridge.browserAI.refreshAccounts() }
            RowLayout {
                Layout.fillWidth: true; spacing: 22
                ButtonGroup { id: browserServices }
                ChoiceRadioButton { objectName: "browserServiceChatGPT"; text: "ChatGPT"; ButtonGroup.group: browserServices; checked: bridge.browserAI.service === "chatgpt"; enabled: !bridge.busy && !bridge.browserAI.loginBusy; onClicked: bridge.browserAI.chooseService("chatgpt") }
                ChoiceRadioButton { objectName: "browserServiceGemini"; text: "Gemini"; ButtonGroup.group: browserServices; checked: bridge.browserAI.service === "gemini"; enabled: !bridge.busy && !bridge.browserAI.loginBusy; onClicked: bridge.browserAI.chooseService("gemini") }
                Item { Layout.fillWidth: true }
            }
            Hint { Layout.fillWidth: true; text: "Bài mới dùng dịch vụ và tài khoản đã chọn. Model và suy luận được kiểm tra theo quyền tài khoản trước khi gửi." }
            Card {
                Layout.fillWidth: true
                ColumnLayout { width: parent.width; spacing: 18
                    RowLayout {
                        Layout.fillWidth: true; spacing: 14
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 6
                            Title { text: "Tài khoản " + bridge.browserAI.serviceLabel }
                            Hint { text: "Đăng nhập qua Chrome riêng cho từng tài khoản. BiliClass kiểm tra và lưu phiên trên máy."; Layout.fillWidth: true }
                        }
                        SaveButton {
                            objectName: "browserAccountAdd"
                            text: bridge.browserAI.disconnectBusy ? "Đang xóa…" : bridge.browserAI.loginAwaitingConfirmation ? "Kiểm tra và lưu" : bridge.browserAI.loginBusy ? "Hủy" : "Thêm tài khoản"
                            enabled: !bridge.busy && !bridge.browserAI.disconnectBusy
                            onClicked: bridge.browserAI.connectAccount()
                        }
                        SoftButton {
                            objectName: "browserAccountMenu"; text: "..."; implicitWidth: 42
                            visible: !bridge.browserAI.webMode && !!bridge.browserAI.activeId
                            enabled: !bridge.busy && !bridge.browserAI.loginBusy
                            Accessible.name: "Quản lý tài khoản ChatGPT"
                            onClicked: accountMenu.popup()
                            Menu {
                                id: accountMenu
                                MenuItem { text: "Dùng tài khoản khác"; onTriggered: bridge.browserAI.addAndSignIn() }
                                MenuItem { text: "Đăng nhập lại tài khoản này"; visible: bridge.browserAI.webMode; onTriggered: bridge.browserAI.signIn(bridge.browserAI.activeId) }
                                MenuItem { objectName: "browserAutoSelect"; text: "Tự động · ưu tiên Plus"; visible: bridge.browserAI.webMode; checkable: true; checked: bridge.browserAI.autoSelection; onTriggered: bridge.browserAI.preferPaid() }
                                Menu {
                                    id: savedAccountsMenu; objectName: "browserStoredAccountsMenu"
                                    title: "Cố định tài khoản để dùng / kiểm thử"; enabled: bridge.browserAI.accounts.length > 0
                                    Instantiator {
                                        model: bridge.browserAI.accounts
                                        delegate: MenuItem {
                                            required property var modelData
                                            text: modelData.label + (bridge.browserAI.webMode ? " · " + (modelData.plan === "unknown" ? "Chưa rõ gói" : modelData.plan || "Chưa rõ gói") : ""); checkable: true
                                            checked: !bridge.browserAI.autoSelection && bridge.browserAI.activeId === modelData.id
                                            onTriggered: bridge.browserAI.select(modelData.id)
                                        }
                                        onObjectAdded: function(index, object) { savedAccountsMenu.insertItem(index, object) }
                                        onObjectRemoved: function(index, object) { savedAccountsMenu.removeItem(object) }
                                    }
                                }
                                MenuItem { text: "Hạn mức trên ChatGPT"; visible: !bridge.browserAI.webMode; onTriggered: bridge.browserAI.openUsage() }
                                MenuSeparator {}
                                MenuItem { text: "Xóa kết nối trên máy"; onTriggered: bridge.browserAI.remove(bridge.browserAI.activeId) }
                            }
                        }
                    }
                    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: page.line }
                    ColumnLayout {
                        visible: bridge.browserAI.webMode; Layout.fillWidth: true; spacing: 18
                        ButtonGroup { id: browserAccountChoices }
                        ChoiceRadioButton { objectName: "browserAccountAutomatic"; text: "Tự chọn tài khoản đang kết nối"; checked: !bridge.browserAI.selectedAccount; ButtonGroup.group: browserAccountChoices; enabled: !bridge.busy && !bridge.browserAI.loginBusy; onClicked: bridge.browserAI.chooseAccount("") }
                        Hint { objectName: "browserEmptyAccounts"; visible: bridge.browserAI.accounts.length === 0; text: "Chưa có tài khoản " + bridge.browserAI.serviceLabel + ". Bấm Thêm tài khoản để đăng nhập."; Layout.fillWidth: true }
                        Repeater {
                            id: browserProfiles; objectName: "browserProfiles"
                            model: bridge.browserAI.webMode ? bridge.browserAI.accounts : []
                            delegate: ColumnLayout {
                                id: accountRow
                                objectName: "browserProfileRow"
                                required property var modelData
                                required property int index
                                property string accountId: modelData.id
                                Layout.fillWidth: true; spacing: 8
                                Rectangle { visible: accountRow.index > 0; Layout.fillWidth: true; implicitHeight: 1; color: page.line }
                                RowLayout {
                                    Layout.fillWidth: true; spacing: 16
                                    ChoiceRadioButton { objectName: "browserProfileSelect_" + accountRow.accountId; checked: bridge.browserAI.selectedAccount === accountRow.accountId; ButtonGroup.group: browserAccountChoices; enabled: !bridge.busy && !bridge.browserAI.loginBusy; Accessible.name: "Dùng tài khoản " + (accountRow.modelData.name || accountRow.modelData.label); onClicked: bridge.browserAI.chooseAccount(accountRow.accountId) }
                                    Rectangle { objectName: "browserProfileLight"; implicitWidth: 9; implicitHeight: 9; radius: 5; color: accountRow.modelData.color; Accessible.name: accountRow.modelData.status }
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 5
                                        Label { objectName: "browserProfileName"; text: accountRow.modelData.name || accountRow.modelData.label; color: page.ink; font.pixelSize: 18; font.weight: Font.DemiBold; Layout.fillWidth: true; elide: Text.ElideRight }
                                        Hint { text: accountRow.modelData.email || ""; visible: !!text && text !== accountRow.modelData.label; Layout.fillWidth: true }
                                        RowLayout {
                                            spacing: 12
                                            Label { objectName: "browserProfilePlan"; text: accountRow.modelData.plan === "unknown" ? "Chưa rõ gói" : accountRow.modelData.plan.charAt(0).toUpperCase() + accountRow.modelData.plan.slice(1); color: page.muted; font.pixelSize: 13 }
                                            Label { objectName: "browserProfileState"; text: accountRow.modelData.status; color: accountRow.modelData.color; font.pixelSize: 13 }
                                        }
                                    }
                                    SoftButton {
                                        objectName: "browserProfileOpen"; text: "Mở tài khoản"
                                        enabled: !bridge.busy && !bridge.browserAI.loginBusy
                                        Accessible.name: "Mở tài khoản " + (accountRow.modelData.name || accountRow.modelData.label)
                                        onClicked: bridge.browserAI.signIn(accountRow.accountId)
                                    }
                                    SoftButton {
                                        objectName: "browserProfileReconnect"
                                        visible: !accountRow.modelData.ready || accountRow.modelData.limited
                                        text: accountRow.modelData.recheck ? "Kiểm tra lại" : "Đăng nhập lại"
                                        enabled: !bridge.busy && !bridge.browserAI.loginBusy
                                        onClicked: { if (accountRow.modelData.recheck) bridge.browserAI.checkAccount(accountRow.accountId); else bridge.browserAI.signIn(accountRow.accountId) }
                                    }
                                    SoftButton {
                                        objectName: "browserProfileDelete"; text: "Xóa profile"
                                        enabled: !bridge.busy && !bridge.browserAI.loginBusy
                                        Accessible.name: "Xóa profile " + (accountRow.modelData.name || accountRow.modelData.label)
                                        onClicked: bridge.browserAI.remove(accountRow.accountId)
                                    }
                                }
                                Hint { objectName: "browserProfileError"; visible: !!accountRow.modelData.error && !accountRow.modelData.checking; text: accountRow.modelData.error; color: "#ab5b20"; Layout.fillWidth: true }
                            }
                        }
                    }
                    ColumnLayout {
                        visible: !bridge.browserAI.webMode; Layout.fillWidth: true; spacing: 18
                    RowLayout {
                        Layout.fillWidth: true; spacing: 8
                        Rectangle { implicitWidth: 8; implicitHeight: 8; radius: 4; color: bridge.browserAI.hasError ? "#c05b31" : bridge.browserAI.accountInfo.ready ? "#138578" : page.muted }
                        Label {
                            objectName: "browserConnectionState"
                            text: bridge.browserAI.disconnectBusy ? "Đang ngắt kết nối…" : bridge.browserAI.loginBusy ? "Đang kết nối…" : bridge.browserAI.hasError ? "Lần đăng nhập vừa rồi chưa thành công" : bridge.browserAI.accountInfo.ready ? "Đã đăng nhập · Tự lưu" : "Chưa đăng nhập"
                            font.pixelSize: 13; font.weight: Font.DemiBold; color: page.ink
                        }
                    }
                    ColumnLayout {
                        objectName: "browserAccountDetails"
                        visible: !!bridge.browserAI.accountInfo.ready; Layout.fillWidth: true; spacing: 6
                        Label { objectName: "browserAccountIdentity"; text: bridge.browserAI.accountInfo.name || bridge.browserAI.accountInfo.label || ""; color: page.ink; font.pixelSize: 21; font.weight: Font.DemiBold; Layout.fillWidth: true; elide: Text.ElideRight }
                        Hint { text: bridge.browserAI.accountInfo.email || ""; visible: !!bridge.browserAI.accountInfo.name && !!text; Layout.fillWidth: true }
                        Hint { objectName: "browserAccountSaved"; text: "Lưu lần cuối: " + (bridge.browserAI.accountInfo.saved || ""); Layout.fillWidth: true }
                    }
                    GridLayout {
                        visible: !!bridge.browserAI.accountInfo.ready; Layout.fillWidth: true
                        columns: 2; columnSpacing: 24; rowSpacing: 12
                        Hint { text: "Quyền xử lý bài" }
                        Hint { objectName: "browserAccountPermission"; text: bridge.browserAI.webMode ? "Dùng phiên đăng nhập web ChatGPT" : bridge.browserAI.accountInfo.ready ? "Đã cấp quyền dùng hạn mức ChatGPT" : "Chưa cấp quyền dùng hạn mức ChatGPT"; color: bridge.browserAI.accountInfo.ready ? "#138578" : "#ab5b20"; Layout.fillWidth: true }
                        Hint { text: "Gói tài khoản"; visible: !!bridge.browserAI.accountInfo.plan }
                        Hint { text: bridge.browserAI.accountInfo.plan === "unknown" ? "Chưa xác định trên web" : bridge.browserAI.accountInfo.plan || ""; visible: !!text; Layout.fillWidth: true }
                        Hint { text: "Bài mới"; visible: bridge.browserAI.webMode }
                        Hint { objectName: "browserSelectionPolicy"; text: bridge.browserAI.selectionLabel; visible: bridge.browserAI.webMode; Layout.fillWidth: true }
                        Hint { text: "Hạn mức còn lại" }
                        Hint { objectName: "browserQuotaStatus"; text: bridge.browserAI.quotaMessage; Layout.fillWidth: true }
                    }
                    }
                    RowLayout {
                        visible: bridge.browserAI.loginBusy || (!bridge.browserAI.webMode && bridge.browserAI.hasError); Layout.fillWidth: true; spacing: 10
                        BusyIndicator { visible: bridge.browserAI.loginBusy; running: visible; implicitWidth: 24; implicitHeight: 24 }
                        Hint { objectName: "browserAccountStatus"; text: bridge.browserAI.message; Layout.fillWidth: true; color: bridge.browserAI.hasError ? "#ab5b20" : page.blue }
                    }
                    Hint { visible: !bridge.browserAI.webMode; text: "Cửa sổ đăng nhập tự đóng khi xong. Chỉ khi có thông tin tài khoản ở đây thì kết nối mới được lưu."; Layout.fillWidth: true; font.pixelSize: 12 }
                }
            }
        }
            }
        }
        ColumnLayout {
            visible: page.activeTab === 2; Layout.fillWidth: true; spacing: 6
            RowLayout { Layout.fillWidth: true; spacing: 10
                SoftButton { objectName: "previewMultilingualVoice"; text: bridge.voiceUiState.phase === "preparing" ? "Đang chuẩn bị…" : "Nghe cả cặp"; iconName: "play"; enabled: !!page.draftVoice && !!page.pairPreviewText(); onClicked: bridge.previewMultilingualVoice(page.draftVoice, page.draftRate, page.pairPreviewText()) }
                SoftButton { objectName: "stopVoicePreview"; text: "Dừng nghe"; onClicked: bridge.stopSpeech() }
                Item { Layout.fillWidth: true }
                SaveButton { objectName: "saveMultilingualVoice"; text: bridge.voiceUiState.saving ? "Đang lưu…" : "Lưu cặp giọng và tốc độ"; enabled: !bridge.voiceUiState.saving && !!page.draftVoice; onClicked: bridge.saveMultilingualVoice(page.draftVoice, page.draftRate) }
            }
            Hint { objectName: "voiceSaveStatus"; text: bridge.voiceUiState.saving || bridge.voiceUiState.saveError ? bridge.voiceUiState.saveMessage : page.voiceDirty ? "Chưa lưu thay đổi · " + (page.selectedVoicePair.name || "") : bridge.voiceUiState.saveMessage || "Lần tạo giọng mới dùng cặp đã lưu. Bài đã tạo giữ nguyên âm thanh."; color: bridge.voiceUiState.saveError ? "#ba581a" : page.voiceDirty ? page.muted : "#168567"; Layout.fillWidth: true }
            Hint { objectName: "voicePreviewStatus"; visible: !!bridge.voiceUiState.message; text: bridge.voiceUiState.message; Layout.fillWidth: true }
        }
    }
}
