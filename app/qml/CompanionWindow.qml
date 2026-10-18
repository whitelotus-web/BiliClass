import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

Window {
    id: companion
    required property var bridge
    signal requestOpenLesson()
    signal requestSettings()
    property bool collapsed: true
    property bool choosingLesson: false
    property bool showAssistant: true
    property bool showShortcutGuide: false
    property bool disposing: false
    readonly property var session: bridge.teachingSession.state
    readonly property var availableAudio: session.bound ? bridge.teachingSession.audio : bridge.audioAvailable
    readonly property var reader: session.bound ? bridge.teachingSession.reader : bridge.englishReaderState
    function readText(language, label) {
        const shortLabel = {en: "Anh", vi: "Việt", both: "Việt–Anh"}[language]
        return reader.language === language && reader.state === "reading" ? "Tạm dừng · " + shortLabel : reader.language === language && reader.state === "paused" ? "Đọc tiếp · " + shortLabel : "Đọc " + label
    }
    function readIcon(language) { return reader.language === language && reader.state === "reading" ? "pause" : "play" }
    readonly property var response: session.bound ? (session.response || {}) : bridge.teachingContext.response
    property bool mascotAtRight: bridge.mascotSettings.position === "right"
    property bool mascotAtBottom: true
    readonly property int mascotExtent: Math.max(90, Math.min(178, bridge.mascotSettings.size + 18))
    readonly property bool hasResponse: bridge.companionCanRead && !companion.response.untouched
    readonly property int controlHeight: bridge.companionPanelSize === "large" ? 46 : bridge.companionPanelSize === "small" ? 36 : 40
    readonly property int controlFont: bridge.companionPanelSize === "large" ? 14 : bridge.companionPanelSize === "small" ? 12 : 13
    readonly property int audioCount: Number(!!availableAudio.en) + Number(!!availableAudio.vi) + Number(!!availableAudio.both)

    // An owned tool window is hidden by Windows when its owner is minimized.
    transientParent: null
    flags: Qt.Tool | Qt.FramelessWindowHint | (bridge.mascotSettings.always_on_top ? Qt.WindowStaysOnTopHint : 0) | Qt.NoDropShadowWindowHint | Qt.WindowDoesNotAcceptFocus
    title: "BiliClass · Trợ giảng"
    width: collapsed ? mascotExtent : Math.min(Screen.desktopAvailableWidth - 16, bridge.companionPanelSize === "large" ? 432 : bridge.companionPanelSize === "small" ? 344 : 384)
    height: collapsed ? mascotExtent : Math.min(Screen.desktopAvailableHeight - 16, mascotExtent + menuContent.implicitHeight + 32)
    color: "transparent"

    function reposition() {
        if (visible && !disposing) Qt.callLater(function() { if (visible && !disposing) bridge.showCompanion(companion) })
    }
    Component.onDestruction: disposing = true
    onWidthChanged: reposition()
    onHeightChanged: reposition()
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
        radius: 15; color: Qt.rgba(249 / 255, 251 / 255, 1, bridge.companionPanelOpacity / 100); border.color: "#cbdcf4"
        ContentScrollView {
            id: controlScroll
            objectName: "companionControlsScroll"
            anchors.fill: parent; anchors.margins: 12; contentWidth: availableWidth
            rightPadding: 0
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical: SlimScrollBar {
                parent: menu; x: menu.width - 10; y: 12; width: 7; height: menu.height - 24
                visible: companion.visible && !companion.collapsed && size < 1
            }
            CompanionControls { id: menuContent; width: controlScroll.availableWidth; bridge: companion.bridge; companion: companion }
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
            subject: bridge.mascotSubject
            accessories: bridge.mascotSettings.accessories
            showSubjectBadge: false
            reducedMotion: bridge.mascotSettings.reduced_motion
        }
        MouseArea {
            id: mascotMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
            property real pressGlobalX: 0
            property real pressGlobalY: 0
            property int startWindowX: 0
            property int startWindowY: 0
            property bool dragged: false
            onPressed: function(mouse) {
                const point = mapToGlobal(Qt.point(mouse.x, mouse.y))
                pressGlobalX = point.x
                pressGlobalY = point.y
                startWindowX = companion.x
                startWindowY = companion.y
                dragged = false
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
            onReleased: {
                if (dragged) {
                    bridge.saveMascotLocation(companion.x + mascotButton.x, companion.y + mascotButton.y)
                    bridge.showCompanion(companion)
                }
            }
            onClicked: { if (!dragged) companion.collapsed = !companion.collapsed }
            Accessible.role: Accessible.Button
            Accessible.name: companion.collapsed ? "Mở công cụ trợ giảng" : "Thu gọn công cụ trợ giảng"
        }
    }
}
