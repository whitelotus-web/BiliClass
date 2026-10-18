import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

Window {
    id: companion
    required property var bridge
    signal requestOpenLesson()
    property bool collapsed: true
    property bool choosingLesson: false
    property bool showAssistant: false
    readonly property var session: bridge.teachingSession.state
    readonly property var availableAudio: session.bound ? bridge.teachingSession.audio : bridge.audioAvailable
    readonly property var reader: session.bound ? bridge.teachingSession.reader : bridge.englishReaderState
    readonly property var response: session.bound ? (session.response || {}) : bridge.teachingContext.response
    property bool mascotAtRight: bridge.mascotSettings.position === "right"
    property bool mascotAtBottom: true
    readonly property int mascotExtent: Math.max(90, Math.min(178, bridge.mascotSettings.size + 18))
    readonly property bool hasResponse: bridge.companionCanRead && !companion.response.untouched

    // An owned tool window is hidden by Windows when its owner is minimized.
    transientParent: null
    flags: Qt.Tool | Qt.FramelessWindowHint | (bridge.mascotSettings.always_on_top ? Qt.WindowStaysOnTopHint : 0) | Qt.NoDropShadowWindowHint | Qt.WindowDoesNotAcceptFocus
    title: "BiliClass · Trợ giảng"
    width: collapsed ? mascotExtent : 344
    height: collapsed ? mascotExtent : Math.min(Screen.desktopAvailableHeight - 16, mascotExtent + menuContent.implicitHeight + 32)
    color: "transparent"

    function reposition() {
        if (visible) Qt.callLater(function() { bridge.showCompanion(companion) })
    }
    onWidthChanged: reposition()
    onHeightChanged: reposition()
    Shortcut { sequence: "Escape"; onActivated: companion.collapsed = true }

    Shortcut { sequence: "F5"; onActivated: bridge.startTeachingShow() }
    FileDialog { id: teachingFile; objectName: "companionPresentationDialog"; title: "Chọn PowerPoint để dạy cùng Mascot"; nameFilters: ["PowerPoint (*.pptx)"]; onAccepted: bridge.openTeachingPresentation(selectedFile.toString()) }
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

        ContentScrollView {
          anchors.fill: parent; anchors.margins: 10; contentWidth: availableWidth
          ColumnLayout {
            id: menuContent
            width: parent.width; spacing: 7
            RowLayout {
                Layout.fillWidth: true
                Label { text: "Trợ giảng song ngữ"; color: "#112650"; font.pixelSize: 14; font.bold: true }
                Item { Layout.fillWidth: true }
                ActionButton { objectName: "resetCompanionPosition"; text: "Về góc"; implicitHeight: 28; onClicked: { bridge.resetMascotLocation(); bridge.showCompanion(companion) } }
                ActionButton { objectName: "hideCompanion"; text: "Ẩn"; implicitHeight: 28; onClicked: companion.hide() }
            }
            Label { visible: bridge.powerpointState.active; text: "Slide " + bridge.powerpointState.slide + " / " + bridge.powerpointState.total; color: "#667997"; font.pixelSize: 12 }
            Label { objectName: "companionBoundLesson"; text: companion.session.bound ? "Đang gắn: " + companion.session.title : bridge.companionCanRead ? bridge.lesson.title : "Chưa gắn với bài giảng"; color: "#112650"; font.pixelSize: 12; font.weight: Font.DemiBold; Layout.fillWidth: true; elide: Text.ElideRight; textFormat: Text.PlainText }
            ActionButton { objectName: "companionChooseLesson"; text: companion.choosingLesson ? "Thu chọn bài" : "Chọn / đổi bài giảng"; Layout.fillWidth: true; implicitHeight: 32; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: companion.choosingLesson = !companion.choosingLesson }
            ColumnLayout { visible: companion.choosingLesson; Layout.fillWidth: true; spacing: 6
                ComboBox { id: teachingLibrary; objectName: "companionLibraryPicker"; Layout.fillWidth: true; model: bridge.lessons; textRole: "title"; enabled: !bridge.busy && !bridge.narrationBusy }
                ActionButton { objectName: "companionSelectLibrary"; text: "Chọn từ thư viện"; Layout.fillWidth: true; implicitHeight: 32; enabled: teachingLibrary.currentIndex >= 0 && !bridge.busy && !bridge.narrationBusy; onClicked: { bridge.openTeachingLibraryLesson(bridge.lessons[teachingLibrary.currentIndex].id); companion.choosingLesson = false } }
                ActionButton { objectName: "companionSelectFile"; text: "Chọn file PowerPoint…"; Layout.fillWidth: true; implicitHeight: 32; enabled: !bridge.busy && !bridge.narrationBusy; onClicked: teachingFile.open() }
            }
            ActionButton { objectName: "companionStartShow"; text: "Trình chiếu (F5)"; visible: !!bridge.powerpointState.opened && !bridge.powerpointState.active; Layout.fillWidth: true; implicitHeight: 34; onClicked: bridge.startTeachingShow() }
            ActionButton { objectName: "companionEndShow"; text: "Kết thúc trình chiếu"; visible: !!bridge.powerpointState.active && !!companion.session.bound; Layout.fillWidth: true; implicitHeight: 30; onClicked: bridge.navigatePowerPoint("end_show") }
            Label { visible: !!companion.session.warning; text: companion.session.warning || ""; color: "#a66318"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
            ActionButton { objectName: "companionOpenLesson"; text: companion.session.bound ? "Xem bài đang gắn" : bridge.companionCanRead ? "Trở lại bài giảng" : "Mở bài để dạy"; iconName: "view"; Layout.fillWidth: true; implicitHeight: 32; onClicked: companion.requestOpenLesson() }
            Label { visible: !bridge.companionCanRead; text: companion.session.bound ? "Bài đã gắn với Mascot. Bấm Trình chiếu (F5) khi sẵn sàng." : "Chọn bài từ thư viện hoặc file PowerPoint để gắn với Mascot."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 10 }
            ActionButton { objectName: "companionAssistantToggle"; text: companion.showAssistant ? "Thu công cụ trợ giảng" : "Công cụ trợ giảng"; Layout.fillWidth: true; implicitHeight: 30; onClicked: companion.showAssistant = !companion.showAssistant }
            ComboBox {
                objectName: "companionReadingScope"; visible: !!companion.session.can_choose_scope
                Layout.fillWidth: true; model: ["Đọc toàn bộ slide", "Đọc phần đang hiện theo hiệu ứng"]
                currentIndex: companion.session.reading_scope === "visible" ? 1 : 0
                onActivated: bridge.teachingSession.setReadingScope(currentIndex === 1 ? "visible" : "full_slide")
            }
            Label {
                visible: !!companion.session.bound; Layout.fillWidth: true; wrapMode: Text.WordWrap
                text: companion.session.reading_scope === "visible" ? "Chỉ đọc lời đã xác định đang hiện; chuyển hiệu ứng rồi bấm đọc tiếp." : "Bấm đọc sẽ nghe trọn lời đã lưu của slide, kể cả phần xuất hiện sau."
                font.pixelSize: 11; color: "#667997"
            }
            GridLayout {
                Layout.fillWidth: true; columns: 2; columnSpacing: 6; rowSpacing: 5
                ActionButton { visible: companion.showAssistant; objectName: "companionExplain"; text: "Giải thích Anh"; enabled: bridge.companionCanRead; iconName: "view"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.companionAsk("explanation", "en") }
                ActionButton { visible: companion.showAssistant; text: "Ví dụ"; enabled: bridge.companionCanRead; iconName: "add"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.companionAsk("example", "en") }
                ActionButton { visible: companion.showAssistant; text: "Câu hỏi gợi mở"; enabled: bridge.companionCanRead; iconName: "students"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.companionAsk("question", "en") }
                ActionButton { visible: companion.showAssistant; text: "Gợi ý Việt"; enabled: bridge.companionCanRead; iconName: "back"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.companionAsk("rescue", "vi") }
                ActionButton { objectName: "companionReadEnglish"; visible: bridge.companionCanRead && !!companion.availableAudio.en; text: "Đọc tiếng Anh"; iconName: "play"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && !!companion.availableAudio.en; onClicked: bridge.companionRead("en") }
                ActionButton { objectName: "companionReadVietnamese"; visible: bridge.companionCanRead && !!companion.availableAudio.vi; text: "Đọc tiếng Việt"; iconName: "play"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && !!companion.availableAudio.vi; onClicked: bridge.companionRead("vi") }
                ActionButton { objectName: "companionReadBoth"; visible: bridge.companionCanRead && !!companion.availableAudio.both; text: "Đọc Việt–Anh chung"; iconName: "play"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && !!companion.availableAudio.both; onClicked: bridge.companionRead("both") }
                ActionButton { objectName: "companionStopSpeech"; text: "Dừng đọc"; danger: true; symbol: "■"; Layout.fillWidth: true; implicitHeight: 32; onClicked: bridge.teachingSession.state.bound ? bridge.teachingSession.stop() : bridge.stopSpeech() }
                ActionButton { objectName: "companionPauseEnglish"; text: companion.reader.state === "paused" ? "Tiếp tục" : "Tạm dừng"; iconName: "pause"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && ["reading", "preparing", "paused"].indexOf(companion.reader.state) >= 0; onClicked: bridge.teachingSession.state.bound ? bridge.teachingSession.pauseResume() : companion.reader.state === "paused" ? bridge.resumeEnglish() : bridge.pauseEnglish() }
                ActionButton { objectName: "companionReplayEnglish"; text: "Đọc lại"; iconName: "refresh"; Layout.fillWidth: true; implicitHeight: 32; enabled: bridge.companionCanRead && (!!companion.availableAudio.en || !!companion.availableAudio.vi); onClicked: bridge.replayCompanion() }
            }
            ActionButton { objectName: "companionUnbind"; text: "Ngắt gắn bài"; visible: !!companion.session.bound; Layout.fillWidth: true; implicitHeight: 28; onClicked: bridge.stopPowerPoint() }
            Label { objectName: "companionReaderStatus"; text: companion.reader.message; color: companion.reader.state === "error" ? "#b14828" : "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
            ContentScrollView {
                visible: companion.hasResponse
                Layout.fillWidth: true; Layout.preferredHeight: 150;
                TextArea { text: companion.response.text || ""; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.pixelSize: 13; color: "#112650"; background: null; textFormat: TextEdit.PlainText }
            }
            RowLayout {
                Layout.fillWidth: true
                ActionButton { objectName: "companionPrevious"; text: "Trước"; enabled: bridge.companionCanRead; iconName: "previous"; implicitHeight: 30; onClicked: bridge.navigatePowerPoint("previous_slide") }
                Item { Layout.fillWidth: true }
                ActionButton { text: "Theo slide"; visible: bridge.powerpointState.active && !companion.session.bound; implicitHeight: 30; onClicked: bridge.followPowerPoint() }
                ActionButton { objectName: "companionNext"; text: "Sau"; enabled: bridge.companionCanRead; iconName: "next"; implicitHeight: 30; onClicked: bridge.navigatePowerPoint("next_slide") }
            }
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
