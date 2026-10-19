import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: controls
    required property var bridge
    required property var companion
    spacing: 9

    component PanelAction: ActionButton {
        id: panelAction
        externalHovered: controls.companion.hoveringControl(panelAction)
        ToolTip.delay: 500
        Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0
        implicitHeight: controls.companion.controlHeight
        font.pixelSize: controls.companion.controlFont
        leftPadding: 9; rightPadding: 9
    }
    component HeaderAction: ToolButton {
        id: tool
        property string hint: ""
        property string glyph: ""
        property url imageSource: ""
        property bool standardHint: true
        readonly property bool pointerHovered: hovered || controls.companion.hoveringControl(tool)
        implicitWidth: 30; implicitHeight: 30
        Accessible.name: hint
        ToolTip.visible: standardHint && pointerHovered; ToolTip.text: hint; ToolTip.delay: 400
        contentItem: Item {
            Image { anchors.centerIn: parent; width: 21; height: 21; source: tool.imageSource; visible: tool.imageSource.toString().length > 0; fillMode: Image.PreserveAspectFit }
            Label { anchors.centerIn: parent; text: tool.glyph; visible: tool.imageSource.toString().length === 0; color: "#486385"; font.pixelSize: 19 }
        }
        background: Rectangle { radius: 7; color: tool.down ? "#d8e9ff" : tool.pointerHovered ? "#eaf2ff" : "transparent"; border.color: tool.visualFocus ? "#0869ff" : "transparent" }
    }

    RowLayout {
        Layout.fillWidth: true; spacing: 3
        Label { text: "Trợ giảng"; color: "#112650"; font.pixelSize: 15; font.weight: Font.DemiBold; Layout.fillWidth: true }
        HeaderAction { objectName: "resetCompanionPosition"; glyph: "↘"; hint: "Đưa Mascot về góc phải dưới"; onClicked: { bridge.resetMascotLocation(); bridge.showCompanion(companion) } }
        HeaderAction {
            id: shortcutHelp; objectName: "companionShortcutGuideToggle"; glyph: "?"; hint: "Rê chuột để xem hướng dẫn phím"; standardHint: false
            ToolTip {
                objectName: "companionShortcutTooltip"
                visible: shortcutHelp.pointerHovered; delay: 250; timeout: -1
                width: Math.min(370, controls.companion.width - 20)
                x: -width + shortcutHelp.width; y: shortcutHelp.height + 6
                padding: 12
                background: Rectangle { color: "#ffffff"; border.color: "#cbdcf4"; radius: 10 }
                contentItem: ShortcutGuide { settings: controls.bridge.mascotShortcuts }
            }
        }
        HeaderAction { objectName: "companionSettings"; imageSource: "../assets/navigation/settings-active.png"; hint: "Cài đặt Mascot"; onClicked: companion.requestSettings() }
        HeaderAction { objectName: "hideCompanion"; glyph: "−"; hint: "Ẩn trợ giảng nổi"; onClicked: companion.hide() }
    }
    Label {
        objectName: "companionBoundLesson"
        text: companion.session.bound ? companion.session.title : bridge.companionCanRead ? bridge.lesson.title : "Chưa gắn với bài giảng"
        color: companion.session.bound ? "#112650" : "#667997"; font.pixelSize: companion.controlFont
        font.weight: Font.DemiBold; Layout.fillWidth: true; elide: Text.ElideRight; textFormat: Text.PlainText
        ToolTip.visible: lessonHover.hovered; ToolTip.text: text
        HoverHandler { id: lessonHover }
    }
    Label { visible: !!companion.session.bound; text: bridge.mascotSubject; color: "#667997"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
    PanelAction { objectName: "companionChooseLesson"; text: companion.choosingLesson ? "Thu chọn bài" : companion.session.bound ? "Đổi bài giảng" : "Chọn bài giảng"; primary: !companion.session.bound; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: companion.choosingLesson = !companion.choosingLesson }
    ColumnLayout {
        visible: companion.choosingLesson; Layout.fillWidth: true; spacing: 6
        ComboBox { id: teachingLibrary; objectName: "companionLibraryPicker"; Layout.fillWidth: true; model: bridge.lessons; textRole: "title"; enabled: !bridge.busy && !bridge.narrationBusy }
        RowLayout { Layout.fillWidth: true; spacing: 6
            PanelAction { objectName: "companionSelectLibrary"; text: "Mở bài đã chọn"; enabled: teachingLibrary.currentIndex >= 0 && !bridge.busy && !bridge.narrationBusy; onClicked: { bridge.openTeachingLibraryLesson(bridge.lessons[teachingLibrary.currentIndex].id); companion.choosingLesson = false } }
            PanelAction { objectName: "companionSelectFile"; text: "Chọn file…"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: companion.choosePresentation() }
        }
    }
    Label { visible: !companion.session.bound && !bridge.companionCanRead; text: "Chọn bài trong thư viện hoặc file PowerPoint để Mascot điều khiển."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 12 }
    RowLayout {
        visible: !!bridge.powerpointState.opened; Layout.fillWidth: true; spacing: 6
        PanelAction { objectName: "companionStartShow"; text: bridge.powerpointState.active ? "Đang trình chiếu" : "Trình chiếu · F5"; primary: !bridge.powerpointState.active; iconName: "fullscreen"; enabled: !bridge.powerpointState.active; onClicked: bridge.startTeachingShow() }
        PanelAction { objectName: "companionEndShow"; text: "Kết thúc"; visible: !!bridge.powerpointState.active && !!companion.session.bound; onClicked: bridge.navigatePowerPoint("end_show") }
    }
    RowLayout {
        visible: !!companion.session.bound || bridge.companionCanRead; Layout.fillWidth: true; spacing: 8
        PanelAction { objectName: "companionPrevious"; text: "Trước"; iconName: "previous"; enabled: bridge.companionCanRead && bridge.powerpointState.slide > 1; ToolTip.visible: pointerHovered; ToolTip.text: "Về slide trước · Phím ← để lùi từng hiệu ứng"; onClicked: bridge.navigatePowerPoint("previous_slide") }
        Label { objectName: "companionSlidePosition"; text: bridge.powerpointState.active ? "Slide " + bridge.powerpointState.slide + " / " + bridge.powerpointState.total : "Sẵn sàng"; color: "#486385"; font.pixelSize: companion.controlFont; horizontalAlignment: Text.AlignHCenter; Layout.preferredWidth: 94 }
        PanelAction { objectName: "companionNext"; text: "Sau"; iconName: "next"; enabled: bridge.companionCanRead && bridge.powerpointState.slide < bridge.powerpointState.total; ToolTip.visible: pointerHovered; ToolTip.text: "Sang slide tiếp · Phím → để tiến từng hiệu ứng"; onClicked: bridge.navigatePowerPoint("next_slide") }
    }
    GridLayout {
        objectName: "companionAudioControls"; visible: bridge.companionCanRead && companion.audioCount > 0
        Layout.fillWidth: true; columns: Math.max(1, companion.audioCount); columnSpacing: 6; uniformCellWidths: true
        PanelAction { objectName: "companionReadEnglish"; visible: !!companion.availableAudio.en; enabled: bridge.companionCanRead && !!companion.availableAudio.en; text: "Anh"; iconName: companion.readIcon("en") === "pause" ? "pause" : "speaker-en"; ToolTip.visible: pointerHovered; ToolTip.text: companion.readText("en", "tiếng Anh"); Accessible.name: companion.readText("en", "tiếng Anh"); onClicked: bridge.companionRead("en") }
        PanelAction { objectName: "companionReadVietnamese"; visible: !!companion.availableAudio.vi; enabled: bridge.companionCanRead && !!companion.availableAudio.vi; text: "Việt"; iconName: companion.readIcon("vi") === "pause" ? "pause" : "speaker-vi"; ToolTip.visible: pointerHovered; ToolTip.text: companion.readText("vi", "tiếng Việt"); Accessible.name: companion.readText("vi", "tiếng Việt"); onClicked: bridge.companionRead("vi") }
        PanelAction { objectName: "companionReadBoth"; visible: !!companion.availableAudio.both; enabled: bridge.companionCanRead && !!companion.availableAudio.both; text: "Việt–Anh"; iconName: companion.readIcon("both") === "pause" ? "pause" : "speaker-both"; ToolTip.visible: pointerHovered; ToolTip.text: companion.readText("both", "Việt–Anh"); Accessible.name: companion.readText("both", "Việt–Anh"); onClicked: bridge.companionRead("both") }
    }
    Label {
        objectName: "companionAudioHint"; visible: !!companion.session.bound && (!bridge.companionCanRead || companion.audioCount < 3)
        text: !bridge.companionCanRead ? "Bấm Trình chiếu để đọc giọng đã tạo."
            : companion.audioCount === 0 ? "Slide này chưa có giọng đọc. Tạo giọng trong BiliClass nếu cần."
            : "Nút sáng là giọng có trên slide này."
        color: "#667997"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true
    }
    RowLayout {
        visible: companion.session.bound && !!companion.session.active && companion.audioCount > 0; Layout.fillWidth: true; spacing: 6
        Label { text: "Âm lượng"; font.pixelSize: 12; color: "#667997" }
        Slider { objectName: "companionVolume"; from: 0; to: 100; stepSize: 5; value: companion.reader.volume === undefined ? 80 : companion.reader.volume; Layout.fillWidth: true; onMoved: bridge.teachingSession.setVolume(Math.round(value)); onPressedChanged: if (!pressed) bridge.focusTeachingPresentation() }
        Label { text: (companion.reader.volume === undefined ? 80 : companion.reader.volume) + "%"; font.pixelSize: 12; color: "#102e54" }
    }
    Rectangle { visible: !!companion.session.bound || bridge.companionCanRead; Layout.fillWidth: true; implicitHeight: 1; color: "#e0e8f4" }
    RowLayout {
        visible: !!companion.session.bound || bridge.companionCanRead; Layout.fillWidth: true
        Label { text: "Trợ giảng"; color: "#112650"; font.pixelSize: companion.controlFont; font.weight: Font.DemiBold; Layout.fillWidth: true }
        ToolButton { objectName: "companionAssistantToggle"; text: companion.showAssistant ? "Thu gọn" : "Mở công cụ"; font.pixelSize: 11; implicitHeight: 26; onClicked: companion.showAssistant = !companion.showAssistant }
    }
    GridLayout {
        visible: companion.showAssistant && (!!companion.session.bound || bridge.companionCanRead); Layout.fillWidth: true
        columns: 2; columnSpacing: 6; rowSpacing: 6
        PanelAction { objectName: "companionExplain"; text: "Giải thích Anh"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("explanation", "en") }
        PanelAction { text: "Ví dụ"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("example", "en") }
        PanelAction { text: "Câu hỏi gợi mở"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("question", "en") }
        PanelAction { text: "Gợi ý Việt"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("rescue", "vi") }
    }
    ContentScrollView {
        objectName: "companionResponseScroll"
        visible: companion.hasResponse; Layout.fillWidth: true; Layout.preferredHeight: 150
        TextArea { objectName: "companionResponseText"; text: companion.response.text || ""; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: companion.controlFont; color: "#112650"; background: null; textFormat: TextEdit.PlainText }
    }
    ComboBox {
        objectName: "companionReadingScope"; visible: !!companion.session.can_choose_scope && companion.showAssistant
        Layout.fillWidth: true; model: ["Đọc toàn bộ slide", "Đọc theo hiệu ứng đang hiện"]
        currentIndex: companion.session.reading_scope === "visible" ? 1 : 0
        ToolTip.visible: hovered; ToolTip.text: "Đọc toàn bộ dùng lời đã lưu, kể cả phần xuất hiện sau. Đọc theo hiệu ứng chỉ đọc phần xác định đang hiện."
        onActivated: bridge.teachingSession.setReadingScope(currentIndex === 1 ? "visible" : "full_slide")
    }
    Label { visible: !!companion.session.warning; text: companion.session.warning || ""; color: "#a66318"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
    Label { objectName: "companionReaderStatus"; visible: !!companion.reader.message && companion.reader.state !== "stopped"; text: companion.reader.message; color: companion.reader.state === "error" ? "#b14828" : "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
    RowLayout {
        visible: !!companion.session.bound; Layout.fillWidth: true; spacing: 6
        PanelAction { objectName: "companionOpenLesson"; text: "Xem bài đang gắn"; implicitHeight: 30; font.pixelSize: 11; onClicked: companion.requestOpenLesson() }
        PanelAction { objectName: "companionUnbind"; text: "Ngắt gắn bài"; implicitHeight: 30; font.pixelSize: 11; onClicked: bridge.stopPowerPoint() }
    }
}
