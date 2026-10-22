import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var controller
    required property var bridge
    required property string kind
    readonly property var queueState: controller.state
    readonly property var inputState: controller.inputs.state
    readonly property var documents: controller.inputs.previewer
    readonly property var preview: documents.preview
    readonly property var selected: inputState.selected || ({})
    property bool expanded: false
    readonly property bool working: bridge.busy || bridge.narrationBusy
    visible: queueState.kind === kind && queueState.phase === "draft" && !!queueState.shown && !!queueState.total
    spacing: 12
    onVisibleChanged: if (!visible) expanded = false
    GridLayout {
        Layout.fillWidth: true; columns: width >= 760 ? 2 : 1; columnSpacing: 24; rowSpacing: 12
        Rectangle {
            Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.alignment: Qt.AlignTop
            implicitHeight: listContent.implicitHeight + 28
            radius: 12; color: AppTheme.surface; border.color: AppTheme.line
            ColumnLayout {
                id: listContent
                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14
                spacing: 10
                Label { text: "Hàng đợi · " + (panel.queueState.total || 0) + " bài"; font.pixelSize: 15; font.weight: Font.DemiBold; color: AppTheme.ink }
                Label { text: "Chọn bài để xem trước. Dùng chung cấu hình bên dưới."; font.pixelSize: 12; color: AppTheme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                ListView {
                    id: rows
                    objectName: "batchInputRows_" + panel.kind
                    Layout.fillWidth: true; Layout.preferredHeight: Math.min(252, contentHeight + 2)
                    clip: true; spacing: 7; model: panel.visible ? panel.inputState.rows || [] : []
                    currentIndex: (panel.inputState.rows || []).findIndex(function(row) { return row.id === panel.inputState.selected_id })
                    function followSelection() { if (currentIndex >= 0) positionViewAtIndex(currentIndex, ListView.Contain) }
                    onCurrentIndexChanged: Qt.callLater(followSelection)
                    onModelChanged: Qt.callLater(followSelection)
                    ScrollBar.vertical: SlimScrollBar { policy: rows.contentHeight > 252 ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff }
                    delegate: Button {
                        id: rowButton
                        required property var modelData
                        required property int index
                        objectName: "batchInputChoice_" + modelData.id
                        width: rows.width - (rows.contentHeight > 252 ? 20 : 0)
                        implicitHeight: Math.max(62, rowContents.implicitHeight + 18)
                        leftPadding: 9; rightPadding: 9; topPadding: 9; bottomPadding: 9
                        Accessible.name: "Xem trước " + modelData.name
                        Accessible.selected: panel.inputState.selected_id === modelData.id
                        onClicked: panel.controller.inputs.select(modelData.id)
                        background: Rectangle {
                            radius: 8; color: panel.inputState.selected_id === rowButton.modelData.id ? AppTheme.selected : rowButton.hovered ? AppTheme.hover : AppTheme.surface
                            border.color: rowButton.visualFocus || panel.inputState.selected_id === rowButton.modelData.id ? AppTheme.blue : AppTheme.line
                            border.width: rowButton.visualFocus ? 2 : 1
                        }
                        contentItem: RowLayout {
                            id: rowContents
                            spacing: 8
                            Label { text: (rowButton.index+1) + "."; color: AppTheme.muted; font.pixelSize: 12 }
                            ColumnLayout {
                                Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
                                Label {
                                    text: rowButton.modelData.name; textFormat: Text.PlainText; elide: Text.ElideMiddle
                                    color: AppTheme.ink; font.pixelSize: 13; font.weight: Font.DemiBold; Layout.fillWidth: true
                                    ToolTip.visible: rowButton.hovered; ToolTip.text: text; ToolTip.delay: 500
                                }
                                Label {
                                    objectName: "batchInputDetails_" + rowButton.modelData.id
                                    text: rowButton.modelData.error || (rowButton.modelData.total ? rowButton.modelData.total + " slide · " + (rowButton.modelData.bytes / 1048576).toFixed(1) + " MB" : "Đang đọc thông tin bài giảng…")
                                    textFormat: Text.PlainText; elide: Text.ElideRight; font.pixelSize: 12
                                    color: rowButton.modelData.error ? AppTheme.warning : AppTheme.muted; Layout.fillWidth: true
                                    ToolTip.visible: rowButton.hovered && !!rowButton.modelData.error; ToolTip.text: rowButton.modelData.error || ""
                                }
                            }
                            ActionButton {
                                objectName: "batchInputOpen_" + rowButton.modelData.id
                                text: "Mở PowerPoint"; implicitHeight: 32; leftPadding: 9; rightPadding: 9; font.pixelSize: 11
                                enabled: !panel.working && !rowButton.modelData.error && !panel.bridge.teachingTransitioning
                                onClicked: panel.bridge.openInputPowerPoint(rowButton.modelData.url)
                            }
                            ActionButton {
                                objectName: "batchInputRemove_" + rowButton.modelData.id
                                text: "×"; danger: true; implicitWidth: 30; implicitHeight: 30; leftPadding: 5; rightPadding: 5
                                enabled: !panel.working
                                Accessible.name: "Bỏ " + rowButton.modelData.name + " khỏi hàng đợi"
                                ToolTip.visible: hovered; ToolTip.text: Accessible.name
                                onClicked: panel.controller.remove(rowButton.modelData.id)
                            }
                        }
                    }
                }
            }
        }
        ColumnLayout {
            Layout.preferredWidth: Math.min(panel.width >= 1000 ? 304 : 240, panel.width)
            Layout.minimumWidth: Layout.preferredWidth; Layout.maximumWidth: Layout.preferredWidth
            Layout.alignment: Qt.AlignTop | Qt.AlignRight; spacing: 8
            ActionButton {
                objectName: "batchInputPreviewToggle_" + panel.kind
                text: panel.expanded ? "Thu gọn xem trước" : "Xem trước slide"; implicitHeight: 32
                Layout.alignment: Qt.AlignRight; enabled: !!panel.selected.id
                onClicked: panel.expanded = !panel.expanded
            }
            Label { text: panel.selected.name || ""; textFormat: Text.PlainText; elide: Text.ElideMiddle; font.pixelSize: 12; color: AppTheme.muted; Layout.fillWidth: true }
            Rectangle {
                objectName: "batchInputThumbnail_" + panel.kind
                visible: !panel.expanded; Layout.fillWidth: true; implicitHeight: width * 9 / 16
                radius: 10; color: AppTheme.adapt("#e9eef5"); border.color: AppTheme.line
                Image { objectName: "batchInputImage_" + panel.kind; anchors.fill: parent; anchors.margins: 3; source: panel.preview.image || ""; fillMode: Image.PreserveAspectFit; sourceSize.width: 640; asynchronous: true }
                BusyIndicator { anchors.centerIn: parent; visible: running; running: !!panel.preview.busy || panel.documents.busy }
                ColumnLayout {
                    anchors.centerIn: parent; width: parent.width - 24
                    visible: !panel.preview.image && !panel.preview.busy && !panel.documents.busy
                    Label { text: panel.selected.error || panel.preview.error || "Xem trước slide"; textFormat: Text.PlainText; color: AppTheme.muted; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    ActionButton { text: "Thử lại"; visible: !panel.selected.error; implicitHeight: 30; Layout.alignment: Qt.AlignHCenter; onClicked: panel.documents.retryPreview() }
                }
                TapHandler { onTapped: panel.expanded = true }
                HoverHandler { cursorShape: Qt.PointingHandCursor }
                Accessible.role: Accessible.Button; Accessible.name: "Phóng to xem trước slide"; Accessible.onPressAction: panel.expanded = true
            }
        }
    }
    Rectangle {
        objectName: "batchInputExpanded_" + panel.kind
        visible: panel.expanded; Layout.fillWidth: true; implicitHeight: Math.max(260, Math.min(540, width * 9 / 16))
        radius: 10; color: AppTheme.adapt("#e9eef5")
        Image { anchors.fill: parent; anchors.margins: 6; source: panel.preview.image || ""; fillMode: Image.PreserveAspectFit; sourceSize.width: 1600; asynchronous: true; opacity: panel.preview.busy ? .6 : 1 }
        BusyIndicator { anchors.centerIn: parent; visible: running; running: !!panel.preview.busy || panel.documents.busy }
    }
    RowLayout {
        Layout.fillWidth: true
        Item { Layout.fillWidth: true }
        ActionButton { objectName: "batchInputPrevious_" + panel.kind; text: "‹"; implicitHeight: 32; enabled: !panel.preview.busy && (panel.preview.slide || 1) > 1; onClicked: panel.documents.showSlide(panel.preview.slide - 1) }
        Label { objectName: "batchInputCounter_" + panel.kind; text: "Slide " + (panel.preview.slide || 1) + " / " + (panel.preview.total || panel.selected.total || 0); color: AppTheme.ink; font.pixelSize: 12 }
        ActionButton { objectName: "batchInputNext_" + panel.kind; text: "›"; implicitHeight: 32; enabled: !panel.preview.busy && (panel.preview.slide || 1) < (panel.preview.total || 0); onClicked: panel.documents.showSlide((panel.preview.slide || 1) + 1) }
        Item { Layout.fillWidth: true }
    }
}
