import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs
import QtQuick.Templates as T

Window {
    id: companion
    palette: AppPalette {}
    required property var bridge
    signal requestSettings()
    property bool collapsed: true
    property bool choosingLesson: false
    property bool showAssistant: true
    property bool disposing: false
    readonly property var session: bridge.teachingSession.state
    readonly property var availableAudio: session.bound ? bridge.teachingSession.audio : bridge.audioAvailable
    readonly property var reader: session.bound ? bridge.teachingSession.reader : bridge.englishReaderState
    function readText(language, label) {
        if (!session.bound && !bridge.companionCanRead) return "Chọn bài giảng để đọc"
        if (!session.active && !bridge.companionCanRead) return "Bấm Trình chiếu để đọc"
        if (!availableAudio[language]) return "Slide này chưa có giọng " + label
        const shortLabel = {en: "Anh", vi: "Việt", both: "Việt–Anh"}[language]
        return reader.language === language && reader.state === "reading" ? "Tạm dừng · " + shortLabel : reader.language === language && reader.state === "paused" ? "Đọc tiếp · " + shortLabel : "Đọc " + label
    }
    function readIcon(language) { return reader.language === language && reader.state === "reading" ? "pause" : "play" }
    readonly property var response: session.bound ? (session.response || {}) : bridge.teachingContext.response
    property bool mascotAtRight: bridge.mascotSettings.position === "right"
    property bool mascotAtBottom: true
    readonly property int mascotExtent: Math.max(90, Math.min(178, bridge.mascotSettings.size + 18))
    readonly property bool hasResponse: bridge.companionCanRead && !companion.response.untouched
    readonly property bool compactPanel: bridge.mascotSettings.size <= 65
    readonly property int controlHeight: compactPanel ? 30 : bridge.companionPanelSize === "large" ? 44 : bridge.companionPanelSize === "small" ? 34 : 38
    readonly property int controlFont: bridge.companionPanelSize === "large" ? 14 : bridge.companionPanelSize === "small" ? 12 : 13
    readonly property int audioCount: Number(!!availableAudio.en) + Number(!!availableAudio.vi) + Number(!!availableAudio.both)

    function saveLocation() {
        bridge.saveMascotLocation(companion.x + mascotButton.x, companion.y + mascotButton.y)
        bridge.showCompanion(companion)
    }
    function hoveringControl(item) {
        const area = panelMoveArea
        if (!area.containsMouse) return false
        const point = area.mapToItem(item, Qt.point(area.mouseX, area.mouseY))
        return point.x >= 0 && point.y >= 0 && point.x < item.width && point.y < item.height
    }
    component MoveArea: MouseArea {
        property bool dragged: false
        property bool toggleOnClick: false
        property var exclusionRoot: null
        property real pressGlobalX: 0
        property real pressGlobalY: 0
        property int startWindowX: 0
        property int startWindowY: 0
        // Include disabled controls: attempting to use a button must not drag
        // the panel instead. Text selection and scrollbars retain their input.
        function blocked(item, point) {
            if (!item || !item.visible) return false
            const local = mapToItem(item, point)
            if (local.x < 0 || local.y < 0 || local.x >= item.width || local.y >= item.height) return false
            if (item instanceof T.AbstractButton || item instanceof T.ComboBox || item instanceof T.Slider ||
                item instanceof T.TextArea || item instanceof TextEdit || item instanceof T.ScrollBar) return true
            const children = item.children || []
            for (let i = 0; i < children.length; ++i)
                if (blocked(children[i], point)) return true
            return false
        }
        readonly property bool overControl: exclusionRoot ? blocked(exclusionRoot, Qt.point(mouseX, mouseY)) : false
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        hoverEnabled: true
        preventStealing: true
        cursorShape: overControl ? Qt.ArrowCursor : pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
        onPressed: function(mouse) {
            dragged = false
            if (exclusionRoot && blocked(exclusionRoot, Qt.point(mouse.x, mouse.y))) {
                mouse.accepted = false
                return
            }
            const point = mapToGlobal(Qt.point(mouse.x, mouse.y))
            pressGlobalX = point.x
            pressGlobalY = point.y
            startWindowX = companion.x
            startWindowY = companion.y
        }
        onPositionChanged: function(mouse) {
            if (!pressed) return
            const point = mapToGlobal(Qt.point(mouse.x, mouse.y))
            const deltaX = point.x - pressGlobalX
            const deltaY = point.y - pressGlobalY
            if (!dragged && Math.abs(deltaX) + Math.abs(deltaY) < 7) return
            dragged = true
            companion.x = Math.round(startWindowX + deltaX)
            companion.y = Math.round(startWindowY + deltaY)
        }
        onReleased: if (dragged) {
            companion.saveLocation()
            bridge.focusTeachingPresentation()
        }
        onCanceled: if (dragged) companion.saveLocation()
        onClicked: {
            if (!dragged) {
                bridge.focusTeachingPresentation()
                if (toggleOnClick) companion.collapsed = !companion.collapsed
            }
        }
        onWheel: function(wheel) { wheel.accepted = false }
    }

    // An owned tool window is hidden by Windows when its owner is minimized.
    transientParent: null
    flags: Qt.Tool | Qt.FramelessWindowHint | (bridge.mascotSettings.always_on_top ? Qt.WindowStaysOnTopHint : 0) | Qt.NoDropShadowWindowHint | Qt.WindowDoesNotAcceptFocus
    title: "BiliClass · Trợ giảng"
    width: collapsed ? mascotExtent : Math.min(Screen.desktopAvailableWidth - 16, compactPanel ? 280 : bridge.companionPanelSize === "large" ? 400 : bridge.companionPanelSize === "small" ? 320 : 356)
    height: collapsed ? mascotExtent : Math.min(Screen.desktopAvailableHeight - 16, mascotExtent + menuContent.implicitHeight + 32)
    color: "transparent"

    function reposition() {
        if (visible && !disposing) Qt.callLater(function() { if (visible && !disposing) bridge.showCompanion(companion) })
    }
    Component.onDestruction: disposing = true
    onWidthChanged: reposition()
    onHeightChanged: reposition()
    onVisibleChanged: if (!visible) mascotContextMenu.close()
    Shortcut { sequence: "Escape"; onActivated: companion.collapsed = true }

    Shortcut { sequence: "F5"; onActivated: bridge.startTeachingShow() }
    FileDialog { id: teachingFile; objectName: "companionPresentationDialog"; title: "Chọn PowerPoint để dạy cùng Mascot"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.openTeachingPresentation(selectedFile.toString()) }
    function choosePresentation() { teachingFile.open() }
    Rectangle {
        id: menu
        objectName: "companionMenu"
        visible: !companion.collapsed
        x: 4; y: companion.mascotAtBottom ? 4 : companion.mascotExtent + 4
        width: companion.width - 8
        height: companion.height - companion.mascotExtent - 8
        radius: 15; color: Qt.rgba(AppTheme.dark ? 24 / 255 : 249 / 255, AppTheme.dark ? 36 / 255 : 251 / 255, AppTheme.dark ? 56 / 255 : 1, bridge.companionPanelOpacity / 100); border.color: AppTheme.adapt("#cbdcf4")
        ContentScrollView {
            id: controlScroll
            objectName: "companionControlsScroll"
            anchors.fill: parent; anchors.margins: companion.compactPanel ? 9 : 12; contentWidth: availableWidth
            rightPadding: 0
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical: SlimScrollBar {
                parent: menu; x: menu.width - 10; y: 12; width: 7; height: menu.height - 24
                visible: companion.visible && !companion.collapsed && size < 1
            }
            CompanionControls { id: menuContent; width: controlScroll.availableWidth; bridge: companion.bridge; companion: companion }
        }
        MoveArea {
            id: panelMoveArea
            objectName: "companionPanelMoveArea"
            exclusionRoot: menu
            Accessible.name: "Kéo bảng trợ giảng để di chuyển"
            ToolTip.visible: containsMouse && !overControl && mouseY < 48 && !pressed
            ToolTip.delay: 600
            ToolTip.text: "Kéo để di chuyển"
        }
    }

    Item {
        id: mascotButton
        objectName: "mascotToggle"
        width: companion.mascotExtent; height: companion.mascotExtent
        x: companion.mascotAtRight ? companion.width - width : 0
        y: companion.mascotAtBottom ? companion.height - height : 0
        z: 2
        Mascot {
            objectName: "mascotCompanion"
            anchors.fill: parent
            character: bridge.settings.mascot
            expression: bridge.mascotState
            subject: bridge.mascotAccessorySubject
            accessories: bridge.mascotSettings.accessories
            showSubjectBadge: false
            reducedMotion: bridge.mascotSettings.reduced_motion
        }
        MoveArea {
            id: mascotMouse
            toggleOnClick: true
            Accessible.role: Accessible.Button
            Accessible.name: companion.collapsed ? "Mở công cụ trợ giảng" : "Thu gọn công cụ trợ giảng"
        }
        MouseArea {
            objectName: "mascotContextArea"
            anchors.fill: parent; acceptedButtons: Qt.RightButton
            onClicked: function(mouse) { mascotContextMenu.popup(mouse.x, mouse.y) }
        }
        Menu {
            id: mascotContextMenu; objectName: "mascotContextMenu"
            popupType: Popup.Window
            palette: AppPalette {}
            width: Math.ceil(Math.max(contextSettings.implicitWidth, contextHide.implicitWidth)) + leftPadding + rightPadding
            padding: 4
            CompanionMenuItem { id: contextSettings; objectName: "mascotContextSettings"; text: "Cài đặt"; iconName: "settings"; onTriggered: companion.requestSettings() }
            CompanionMenuItem { id: contextHide; objectName: "mascotContextHide"; text: "Ẩn mini"; iconName: "hide"; onTriggered: companion.hide() }
        }
    }
}
