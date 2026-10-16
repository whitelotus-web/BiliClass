import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Window {
    id: companion
    required property var bridge
    signal requestOpenLesson()
    property bool collapsed: true
    property bool mascotAtRight: bridge.mascotSettings.position === "right"
    property bool mascotAtBottom: true
    readonly property int mascotExtent: Math.max(90, Math.min(178, bridge.mascotSettings.size + 18))
    readonly property bool hasResponse: !bridge.teachingContext.response.untouched

    flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint | Qt.WindowDoesNotAcceptFocus
    title: "BiliClass · Trợ giảng"
    width: collapsed ? mascotExtent : 344
    height: collapsed ? mascotExtent : mascotExtent + (hasResponse ? 532 : 426)
    color: "transparent"

    function reposition() {
        if (visible) Qt.callLater(function() { bridge.showCompanion(companion) })
    }
    onWidthChanged: reposition()
    onHeightChanged: reposition()
    Shortcut { sequence: "Escape"; onActivated: { if (companion.collapsed) companion.hide(); else companion.collapsed = true } }

    Rectangle {
        id: menu
        objectName: "companionMenu"
        visible: !companion.collapsed
        x: 4; y: companion.mascotAtBottom ? 4 : companion.mascotExtent + 4
        width: companion.width - 8
        height: companion.height - companion.mascotExtent - 8
        radius: 17
        color: "#f9fbff"
        border.color: "#cbdcf4"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 12; spacing: 6
            RowLayout {
                Layout.fillWidth: true
                Label { text: "Trợ giảng song ngữ"; color: "#112650"; font.pixelSize: 14; font.bold: true }
                Item { Layout.fillWidth: true }
                ActionButton { objectName: "resetCompanionPosition"; text: "Về góc"; implicitHeight: 28; onClicked: { bridge.resetMascotLocation(); bridge.showCompanion(companion) } }
                ActionButton { objectName: "hideCompanion"; text: "Ẩn"; implicitHeight: 28; onClicked: companion.hide() }
            }
            Label { visible: bridge.powerpointState.active; text: "Slide " + bridge.powerpointState.slide + " / " + bridge.powerpointState.total; color: "#667997"; font.pixelSize: 12 }
            ActionButton { objectName: "companionOpenLesson"; text: bridge.companionCanRead ? "Trở lại bài giảng" : "Mở bài để dạy"; iconName: "view"; Layout.fillWidth: true; implicitHeight: 32; onClicked: companion.requestOpenLesson() }
            Label { visible: !bridge.companionCanRead; text: "Chọn Dùng để dạy để mở trình chiếu và bật các nút đọc."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 10 }
            GridLayout {
                Layout.fillWidth: true; columns: 2; columnSpacing: 6; rowSpacing: 5
                ActionButton { objectName: "companionExplain"; text: "English"; iconName: "view"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.teachingContext.ask("explanation", "en") }
                ActionButton { text: "Ví dụ"; iconName: "add"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.teachingContext.ask("example", "en") }
                ActionButton { text: "Hỏi lớp"; iconName: "students"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.teachingContext.ask("question", "en") }
                ActionButton { text: "VI Rescue"; iconName: "back"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.teachingContext.ask("rescue", "vi") }
                ActionButton { objectName: "companionReadEnglish"; text: "Đọc tiếng Anh"; iconName: "play"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && !!bridge.audioAvailable.en; onClicked: bridge.companionRead("en") }
                ActionButton { objectName: "companionReadVietnamese"; text: "Đọc tiếng Việt"; iconName: "play"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && !!bridge.audioAvailable.vi; onClicked: bridge.companionRead("vi") }
                ActionButton { objectName: "companionReadBoth"; text: "Đọc Việt–Anh chung"; iconName: "play"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && !!bridge.audioAvailable.both; onClicked: bridge.companionRead("both") }
                ActionButton { objectName: "companionStopSpeech"; text: "Dừng đọc"; iconName: "pause"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.stopSpeech() }
                ActionButton { objectName: "companionPauseEnglish"; text: bridge.englishReaderState.state === "paused" ? "Tiếp tục" : "Tạm dừng"; iconName: "pause"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && ["reading", "preparing", "paused"].indexOf(bridge.englishReaderState.state) >= 0; onClicked: bridge.englishReaderState.state === "paused" ? bridge.resumeEnglish() : bridge.pauseEnglish() }
                ActionButton { objectName: "companionReplayEnglish"; text: "Đọc lại"; iconName: "refresh"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && (!!bridge.audioAvailable.en || !!bridge.audioAvailable.vi); onClicked: bridge.replayCompanion() }
            }
            Label { objectName: "companionReaderStatus"; text: bridge.englishReaderState.message; color: bridge.englishReaderState.state === "error" ? "#b14828" : "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
            ScrollView {
                visible: companion.hasResponse
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                TextArea { text: bridge.teachingContext.response.text; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 13; color: "#112650"; background: null; textFormat: TextEdit.PlainText }
            }
            RowLayout {
                Layout.fillWidth: true
                ActionButton { objectName: "companionPrevious"; text: "Trước"; iconName: "previous"; implicitHeight: 30; onClicked: bridge.powerpointState.active ? bridge.navigatePowerPoint("previous") : bridge.selectSegment(bridge.segmentIndex - 1) }
                Item { Layout.fillWidth: true }
                ActionButton { text: "Theo slide"; visible: bridge.powerpointState.active; implicitHeight: 30; onClicked: bridge.followPowerPoint() }
                ActionButton { objectName: "companionNext"; text: "Sau"; iconName: "next"; implicitHeight: 30; onClicked: bridge.powerpointState.active ? bridge.navigatePowerPoint("next") : bridge.selectSegment(bridge.segmentIndex + 1) }
            }
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
