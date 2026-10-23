import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ColumnLayout {
    id: controls
    required property var bridge
    required property var companion
    spacing: companion.compactPanel ? 5 : 8
    property real volumeWheelRemainder: 0
    property real navigationWheelRemainder: 0
    function handlePanelWheel(event, source) {
        if (!companion.visible || companion.collapsed || !companion.session.bound || !companion.session.active ||
                bridge.teachingTransitioning || companion.choosingLesson || event.modifiers !== Qt.NoModifier) {
            volumeWheelRemainder = navigationWheelRemainder = 0
            event.accepted = false
            return
        }
        const point = source.mapToItem(volumeArea, Qt.point(event.x, event.y))
        const overVolume = volumeArea.visible && point.x >= 0 && point.x < volumeArea.width && point.y >= -5 && point.y < volumeArea.height + 5
        const delta = event.angleDelta.y ? event.angleDelta.y / 120 : event.pixelDelta.y / 40
        if (!delta) { event.accepted = false; return }
        if (overVolume) {
            navigationWheelRemainder = 0
            volumeWheelRemainder += delta
            const steps = Math.trunc(volumeWheelRemainder)
            volumeWheelRemainder -= steps
            if (steps) bridge.teachingSession.setVolume(Math.max(0, Math.min(100, Math.round(volumeSlider.value) + steps * 5)))
        } else {
            volumeWheelRemainder = 0
            navigationWheelRemainder += delta
            const steps = Math.trunc(navigationWheelRemainder)
            navigationWheelRemainder -= steps
            for (let step = 0; step < Math.abs(steps); ++step)
                bridge.navigatePowerPoint(steps > 0 ? "previous" : "next")
        }
        event.accepted = true
    }

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
            id: shortcutHelp; objectName: "companionShortcutGuideToggle"; iconName: "keyboard-help"; hint: "Hướng dẫn phím và chuột"; standardHint: false
            ToolTip {
                id: shortcutTooltip
                objectName: "companionShortcutTooltip"
                popupType: Popup.Window
                visible: controls.companion.visible && !controls.companion.collapsed && shortcutHelp.pointerHovered; delay: 250; timeout: -1
                width: controls.companion.helpPanelRect().width
                onAboutToShow: {
                    const bounds = controls.bridge.availableScreenBounds(controls.companion)
                    const panel = controls.companion.helpPanelRect()
                    const anchor = shortcutHelp.mapToGlobal(Qt.point(0, 0))
                    const clamp = function(value, lower, upper) { return Math.max(lower, Math.min(upper, value)) }
                    let left = clamp(panel.x, bounds.x + 8, bounds.x + bounds.width - width - 8)
                    let top = panel.y - height - 8
                    if (top < bounds.y + 8) {
                        top = clamp(panel.y, bounds.y + 8, bounds.y + bounds.height - height - 8)
                        if (panel.x - width - 8 >= bounds.x + 8) left = panel.x - width - 8
                        else if (panel.x + panel.width + width + 16 <= bounds.x + bounds.width) left = panel.x + panel.width + 8
                        else top = panel.y + panel.height + 8
                    }
                    x = left - anchor.x; y = top - anchor.y
                }
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
        horizontalAlignment: !companion.session.bound && !bridge.companionCanRead ? Text.AlignHCenter : Text.AlignLeft
        ToolTip.visible: lessonHover.hovered; ToolTip.text: text
        HoverHandler { id: lessonHover }
    }
    RowLayout {
        visible: !!companion.session.bound; Layout.fillWidth: true; spacing: 8
        Label { text: bridge.mascotSubject; color: AppTheme.adapt("#667997"); font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
        HeaderAction { objectName: "companionCloseLesson"; iconName: "close-lesson"; hint: "Đóng bài giảng đang gắn với Mascot"; implicitWidth: 26; implicitHeight: 26; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; onClicked: { companion.choosingLesson = false; bridge.stopPowerPoint() } }
    }
    PanelAction { objectName: "companionChooseLesson"; text: companion.choosingLesson ? "Thu chọn bài" : companion.session.bound ? "Đổi bài giảng" : "Chọn bài giảng"; primary: !companion.session.bound; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; onClicked: companion.choosingLesson = !companion.choosingLesson }
    ColumnLayout {
        visible: companion.choosingLesson; Layout.fillWidth: true; spacing: 6
        ComboBox {
            id: teachingLibrary; objectName: "companionLibraryPicker"; Layout.fillWidth: true
            model: bridge.lessons; textRole: "title"; valueRole: "id"
            property string chosenLessonId: ""
            displayText: currentIndex < 0 && chosenLessonId ? "Bài đã chọn không còn trong thư viện" : currentText
            function keepSelection() {
                currentIndex = chosenLessonId ? indexOfValue(chosenLessonId) : count > 0 ? 0 : -1
                if (!chosenLessonId && currentIndex >= 0) chosenLessonId = currentValue || ""
            }
            onActivated: chosenLessonId = currentValue || ""
            onModelChanged: Qt.callLater(keepSelection)
            Component.onCompleted: keepSelection()
            enabled: !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning
        }
        RowLayout { Layout.fillWidth: true; spacing: 6
            PanelAction { objectName: "companionSelectLibrary"; text: "Mở bài đã chọn"; enabled: teachingLibrary.currentIndex >= 0 && teachingLibrary.currentValue === teachingLibrary.chosenLessonId && !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; onClicked: { bridge.openCompanionLibraryLesson(teachingLibrary.chosenLessonId); companion.choosingLesson = false } }
            PanelAction { objectName: "companionSelectFile"; text: "Chọn file…"; enabled: !bridge.busy && !bridge.narrationBusy && !bridge.teachingTransitioning; onClicked: companion.choosePresentation() }
        }
    }
    Label { visible: !companion.session.bound && !bridge.companionCanRead; text: "Chọn bài trong thư viện hoặc file PowerPoint để Mascot điều khiển."; color: AppTheme.adapt("#667997"); wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true; font.pixelSize: 12 }
    RowLayout {
        visible: !!bridge.powerpointState.opened; Layout.fillWidth: true; spacing: 6
        PanelAction { objectName: "companionStartShow"; text: bridge.powerpointState.show_pending === "start" ? "Đang bắt đầu…" : bridge.powerpointState.active ? "Đang chiếu" : "Trình chiếu · F5"; inactiveStatus: bridge.powerpointState.active; primary: !bridge.powerpointState.active; iconName: "presentation"; enabled: !bridge.powerpointState.active && !bridge.teachingTransitioning; ToolTip.visible: pointerHovered; ToolTip.text: bridge.powerpointState.active ? "PowerPoint đang trình chiếu" : "Bắt đầu trình chiếu PowerPoint · F5"; onClicked: bridge.startTeachingShow() }
        PanelAction { objectName: "companionEndShow"; text: "Kết thúc"; danger: true; enabled: !bridge.teachingTransitioning; visible: !!bridge.powerpointState.active && !!companion.session.bound; onClicked: bridge.navigatePowerPoint("end_show") }
    }
    Label {
        // Reserve the status line while bound: ordinary slide changes must not
        // resize a transparent native window and flash its backing texture.
        objectName: "companionAudioHint"; visible: !!companion.session.bound || text.length > 0
        Layout.preferredHeight: Math.max(16, contentHeight); horizontalAlignment: Text.AlignHCenter
        text: bridge.busy && bridge.openingTeachingLesson ? "Đang chuẩn bị bài giảng…"
            : bridge.teachingTransitioning ? bridge.powerpointState.message || "Đang chuyển bài giảng…"
            : !bridge.companionCanRead ? ""
            : companion.reader.state === "error" ? companion.reader.message || ""
            : companion.audioCount === 0 ? "Phần đang hiện chưa có giọng đọc."
            : ""
        color: companion.reader.state === "error" ? AppTheme.adapt("#b14828") : AppTheme.adapt("#667997"); font.pixelSize: 11
        wrapMode: Text.WordWrap; Layout.fillWidth: true
        ToolTip.visible: statusHover.hovered && truncated; ToolTip.text: text
        HoverHandler { id: statusHover }
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
        id: volumeArea; objectName: "companionVolumeArea"
        visible: companion.session.bound && !!companion.session.active; Layout.fillWidth: true; spacing: 6
        Label { objectName: "companionVolumeLabel"; text: "Âm lượng"; font.pixelSize: 12; color: AppTheme.adapt("#667997") }
        Slider {
            id: volumeSlider; objectName: "companionVolume"
            from: 0; to: 100; stepSize: 5; Layout.fillWidth: true
            value: companion.reader.volume === undefined ? 80 : companion.reader.volume
            onMoved: bridge.teachingSession.setVolume(Math.round(value))
            onPressedChanged: if (!pressed) bridge.focusTeachingPresentation()
        }
        Label { objectName: "companionVolumePercent"; text: (companion.reader.volume === undefined ? 80 : companion.reader.volume) + "%"; font.pixelSize: 12; color: AppTheme.adapt("#102e54") }
    }
    RowLayout {
        visible: !!companion.session.bound; Layout.fillWidth: true; spacing: 8
        Label { text: "Nghỉ giữa đoạn"; color: AppTheme.adapt("#667997"); font.pixelSize: 12; Layout.fillWidth: true }
        ReadingGapPicker { objectName: "companionReadingGap"; bridge: controls.bridge; implicitHeight: controls.companion.controlHeight; Layout.preferredWidth: 112; font.pixelSize: controls.companion.controlFont }
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
