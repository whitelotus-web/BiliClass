import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: controls
    required property var bridge
    required property var companion
    spacing: companion.compactPanel ? 5 : 8

    component PanelAction: ActionButton {
        id: panelAction
        externalHovered: controls.companion.hoveringControl(panelAction)
        ToolTip.delay: 500
        Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0
        implicitHeight: controls.companion.controlHeight
        font.pixelSize: controls.companion.controlFont
        iconSize: controls.companion.compactPanel ? 16 : controls.bridge.companionPanelSize === "small" ? 18 : controls.bridge.companionPanelSize === "large" ? 22 : 20
        leftPadding: 7; rightPadding: 7
    }
    component HeaderAction: ToolButton {
        id: tool
        property string hint: ""
        required property string iconName
        property bool standardHint: true
        readonly property bool pointerHovered: hovered || controls.companion.hoveringControl(tool)
        implicitWidth: 30; implicitHeight: 30
        Accessible.name: hint
        ToolTip.visible: standardHint && pointerHovered; ToolTip.text: hint; ToolTip.delay: 400
        contentItem: Item {
            CompanionIcon { anchors.centerIn: parent; width: 21; height: 21; iconName: tool.iconName }
        }
        background: Rectangle { radius: 7; color: tool.down ? AppTheme.adapt("#d8e9ff") : tool.pointerHovered ? AppTheme.adapt("#eaf2ff") : "transparent"; border.color: tool.visualFocus ? AppTheme.adapt("#0869ff") : "transparent" }
    }

    RowLayout {
        Layout.fillWidth: true; spacing: 7
        Label { text: "Trợ giảng"; color: AppTheme.adapt("#112650"); font.pixelSize: companion.compactPanel ? 13 : 15; font.weight: Font.DemiBold; Layout.fillWidth: true }
        HeaderAction { objectName: "collapseCompanionPanel"; iconName: "collapse"; hint: "Thu bảng về Mascot"; onClicked: companion.collapsed = true }
        HeaderAction {
            id: shortcutHelp; objectName: "companionShortcutGuideToggle"; iconName: "keyboard-help"; hint: "Rê chuột để xem hướng dẫn phím"; standardHint: false
            ToolTip {
                objectName: "companionShortcutTooltip"
                visible: shortcutHelp.pointerHovered; delay: 250; timeout: -1
                width: Math.min(370, controls.companion.width - 20)
                x: -width + shortcutHelp.width; y: shortcutHelp.height + 6
                padding: 12
                background: Rectangle { color: AppTheme.adapt("#ffffff"); border.color: AppTheme.adapt("#cbdcf4"); radius: 10 }
                contentItem: ShortcutGuide { settings: controls.bridge.mascotShortcuts }
            }
        }
        HeaderAction { objectName: "companionSettings"; iconName: "settings"; hint: "Cài đặt Mascot"; onClicked: companion.requestSettings() }
        HeaderAction { objectName: "hideCompanion"; iconName: "hide"; hint: "Ẩn trợ giảng nổi"; onClicked: companion.hide() }
    }
    Label {
        objectName: "companionBoundLesson"
        text: companion.session.bound ? companion.session.title : bridge.companionCanRead ? bridge.lesson.title : "Chưa gắn với bài giảng"
        color: companion.session.bound ? AppTheme.adapt("#112650") : AppTheme.adapt("#667997"); font.pixelSize: companion.controlFont
        font.weight: Font.DemiBold; Layout.fillWidth: true; elide: Text.ElideRight; textFormat: Text.PlainText
        ToolTip.visible: lessonHover.hovered; ToolTip.text: text
        HoverHandler { id: lessonHover }
    }
    Label { visible: !!companion.session.bound; text: bridge.mascotSubject; color: AppTheme.adapt("#667997"); font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
    PanelAction { objectName: "companionChooseLesson"; text: companion.choosingLesson ? "Thu chọn bài" : companion.session.bound ? "Đổi bài giảng" : "Chọn bài giảng"; primary: !companion.session.bound; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: companion.choosingLesson = !companion.choosingLesson }
    ColumnLayout {
        visible: companion.choosingLesson; Layout.fillWidth: true; spacing: 6
        ComboBox { id: teachingLibrary; objectName: "companionLibraryPicker"; Layout.fillWidth: true; model: bridge.lessons; textRole: "title"; enabled: !bridge.busy && !bridge.narrationBusy }
        RowLayout { Layout.fillWidth: true; spacing: 6
            PanelAction { objectName: "companionSelectLibrary"; text: "Mở bài đã chọn"; enabled: teachingLibrary.currentIndex >= 0 && !bridge.busy && !bridge.narrationBusy; onClicked: { bridge.openTeachingLibraryLesson(bridge.lessons[teachingLibrary.currentIndex].id); companion.choosingLesson = false } }
            PanelAction { objectName: "companionSelectFile"; text: "Chọn file…"; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: companion.choosePresentation() }
        }
    }
    Label { visible: !companion.session.bound && !bridge.companionCanRead; text: "Chọn bài trong thư viện hoặc file PowerPoint để Mascot điều khiển."; color: AppTheme.adapt("#667997"); wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 12 }
    RowLayout {
        visible: !!bridge.powerpointState.opened; Layout.fillWidth: true; spacing: 6
        PanelAction { objectName: "companionStartShow"; text: bridge.powerpointState.active ? "Đang chiếu" : controls.companion.compactPanel ? "Chiếu · F5" : "Trình chiếu · F5"; inactiveStatus: bridge.powerpointState.active; primary: !bridge.powerpointState.active; iconName: "presentation"; enabled: !bridge.powerpointState.active; ToolTip.visible: pointerHovered; ToolTip.text: bridge.powerpointState.active ? "PowerPoint đang trình chiếu" : "Bắt đầu trình chiếu PowerPoint · F5"; onClicked: bridge.startTeachingShow() }
        PanelAction { objectName: "companionEndShow"; text: "Kết thúc"; danger: true; visible: !!bridge.powerpointState.active && !!companion.session.bound; onClicked: bridge.navigatePowerPoint("end_show") }
    }
    Label {
        objectName: "companionAudioHint"; visible: !!companion.session.bound && text.length > 0
        Layout.preferredHeight: Math.max(16, contentHeight)
        text: !bridge.companionCanRead ? "Bấm Trình chiếu để đọc giọng đã tạo."
            : companion.reader.state === "error" ? companion.reader.message || ""
            : companion.audioCount === 0 ? "Phần đang hiện chưa có giọng đọc."
            : ""
        color: companion.reader.state === "error" ? AppTheme.adapt("#b14828") : AppTheme.adapt("#667997"); font.pixelSize: 11
        wrapMode: Text.WordWrap; Layout.fillWidth: true
        ToolTip.visible: statusHover.hovered && truncated; ToolTip.text: text
        HoverHandler { id: statusHover }
    }
    RowLayout {
        objectName: "companionReadingOptions"
        visible: !!companion.session.can_choose_scope && bridge.companionCanRead
        Layout.fillWidth: true; spacing: 4
        ButtonGroup { id: readingGroup }
        component ScopeChoice: RadioButton {
            id: choice
            required property string mode
            required property string hint
            readonly property bool pointerHovered: hovered || controls.companion.hoveringControl(choice)
            Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.minimumWidth: 0
            implicitHeight: 28; padding: 3; spacing: 4
            ButtonGroup.group: readingGroup
            checked: controls.companion.session.reading_mode === mode
            onClicked: controls.bridge.teachingSession.setReadingScope(mode)
            Accessible.name: "Cách đọc: " + text
            ToolTip.visible: pointerHovered; ToolTip.text: hint; ToolTip.delay: 500
            indicator: Rectangle {
                x: Math.max(choice.leftPadding, (choice.width - scopeLabel.implicitWidth) / 2); y: (choice.height - height) / 2
                width: 14; height: 14; radius: 3
                color: choice.checked ? AppTheme.accent : AppTheme.field
                border.color: choice.checked || choice.visualFocus ? AppTheme.adapt("#0869ff") : AppTheme.adapt("#b0c4e0")
                Label { anchors.centerIn: parent; text: "✓"; color: AppTheme.accentText; font.pixelSize: 11; visible: choice.checked }
            }
            contentItem: Label {
                id: scopeLabel
                text: choice.text; leftPadding: choice.indicator.width + choice.spacing
                color: choice.checked ? AppTheme.adapt("#075acb") : AppTheme.adapt("#486385")
                font.pixelSize: controls.bridge.companionPanelSize === "small" ? 10 : 11
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
            }
            background: Rectangle {
                radius: 5; color: choice.checked ? AppTheme.adapt("#eaf2ff") : choice.pointerHovered ? AppTheme.adapt("#f0f5fc") : "transparent"
                border.color: choice.visualFocus ? AppTheme.adapt("#0869ff") : "transparent"
            }
        }
        ScopeChoice { objectName: "companionReadingAuto"; mode: "auto"; text: "Tự động"; hint: "Theo hiệu ứng slide; ưu tiên phần mới hiện. Bấm loa để đọc." }
        ScopeChoice { objectName: "companionReadingVisible"; mode: "visible"; text: "Đang hiện"; hint: "Đọc nội dung hiện trên màn chiếu." }
        ScopeChoice { objectName: "companionReadingFull"; mode: "full_slide"; text: "Toàn slide"; hint: "Đọc toàn bộ lời của slide, kể cả phần chưa hiện." }
    }
    Rectangle { visible: bridge.experimentalTeaching && (!!companion.session.bound || bridge.companionCanRead); Layout.fillWidth: true; implicitHeight: 1; color: AppTheme.adapt("#e0e8f4") }
    RowLayout {
        visible: bridge.experimentalTeaching && (!!companion.session.bound || bridge.companionCanRead); Layout.fillWidth: true
        Label { text: "Trợ giảng"; color: AppTheme.adapt("#112650"); font.pixelSize: companion.controlFont; font.weight: Font.DemiBold; Layout.fillWidth: true }
        ToolButton { objectName: "companionAssistantToggle"; text: companion.showAssistant ? "Thu gọn" : "Mở công cụ"; font.pixelSize: 11; implicitHeight: 26; onClicked: companion.showAssistant = !companion.showAssistant }
    }
    GridLayout {
        visible: bridge.experimentalTeaching && companion.showAssistant && (!!companion.session.bound || bridge.companionCanRead); Layout.fillWidth: true
        columns: 2; columnSpacing: 6; rowSpacing: 6
        PanelAction { objectName: "companionExplain"; text: "Giải thích Anh"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("explanation", "en") }
        PanelAction { text: "Ví dụ"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("example", "en") }
        PanelAction { text: "Câu hỏi gợi mở"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("question", "en") }
        PanelAction { text: "Gợi ý Việt"; enabled: bridge.companionCanRead; onClicked: bridge.companionAsk("rescue", "vi") }
    }
    ContentScrollView {
        objectName: "companionResponseScroll"
        visible: bridge.experimentalTeaching && companion.hasResponse; Layout.fillWidth: true; Layout.preferredHeight: 150
        TextArea { objectName: "companionResponseText"; text: companion.response.text || ""; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: companion.controlFont; color: AppTheme.adapt("#112650"); background: null; textFormat: TextEdit.PlainText }
    }
    Label { visible: !!companion.session.warning; text: companion.session.warning || ""; color: AppTheme.adapt("#a66318"); wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
    RowLayout {
        visible: companion.session.bound && !!companion.session.active; Layout.fillWidth: true; spacing: 6
        Label { text: "Âm lượng"; font.pixelSize: 12; color: AppTheme.adapt("#667997") }
        Slider {
            id: volumeSlider; objectName: "companionVolume"
            from: 0; to: 100; stepSize: 5; Layout.fillWidth: true
            value: companion.reader.volume === undefined ? 80 : companion.reader.volume
            onMoved: bridge.teachingSession.setVolume(Math.round(value))
            onPressedChanged: if (!pressed) bridge.focusTeachingPresentation()
            WheelHandler {
                target: null; acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                property real remainder: 0
                onWheel: function(event) {
                    remainder += event.angleDelta.y ? event.angleDelta.y / 120 : event.pixelDelta.y / 40
                    const steps = Math.trunc(remainder)
                    if (steps) {
                        remainder -= steps
                        bridge.teachingSession.setVolume(Math.max(0, Math.min(100, Math.round(volumeSlider.value) + steps * 5)))
                    }
                    event.accepted = true
                }
            }
        }
        Label { text: (companion.reader.volume === undefined ? 80 : companion.reader.volume) + "%"; font.pixelSize: 12; color: AppTheme.adapt("#102e54") }
    }
    GridLayout {
        objectName: "companionAudioControls"; visible: !!companion.session.bound || bridge.companionCanRead
        Layout.fillWidth: true; columns: 2; columnSpacing: 6; uniformCellWidths: true
        PanelAction { objectName: "companionReadEnglish"; enabled: bridge.companionCanRead && !!companion.availableAudio.en; text: "Anh"; iconName: companion.readIcon("en") === "pause" ? "pause" : "speaker"; ToolTip.visible: pointerHovered; ToolTip.text: companion.readText("en", "tiếng Anh"); Accessible.name: companion.readText("en", "tiếng Anh"); onClicked: bridge.companionRead("en") }
        PanelAction { objectName: "companionReadVietnamese"; enabled: bridge.companionCanRead && !!companion.availableAudio.vi; text: "Việt"; iconName: companion.readIcon("vi") === "pause" ? "pause" : "speaker"; ToolTip.visible: pointerHovered; ToolTip.text: companion.readText("vi", "tiếng Việt"); Accessible.name: companion.readText("vi", "tiếng Việt"); onClicked: bridge.companionRead("vi") }
    }
    RowLayout {
        visible: !!companion.session.bound || bridge.companionCanRead; Layout.fillWidth: true; spacing: 8
        PanelAction { objectName: "companionPrevious"; text: "Trước"; iconName: "previous"; enabled: bridge.companionCanRead; onClicked: bridge.navigatePowerPoint("previous") }
        Label { objectName: "companionSlidePosition"; text: bridge.powerpointState.active ? "Slide " + bridge.powerpointState.slide + " / " + bridge.powerpointState.total : "Sẵn sàng"; color: AppTheme.adapt("#486385"); font.pixelSize: companion.controlFont; horizontalAlignment: Text.AlignHCenter; Layout.preferredWidth: 94 }
        PanelAction { objectName: "companionNext"; text: "Sau"; iconName: "next"; enabled: bridge.companionCanRead; onClicked: bridge.navigatePowerPoint("next") }
    }
}
