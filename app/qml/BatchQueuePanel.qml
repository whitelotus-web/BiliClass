import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: panel
    required property var controller
    required property string kind
    property bool working: false
    property bool footerActions: true
    signal newBatchRequested()
    readonly property var queueState: controller.state
    readonly property bool applies: queueState.kind === kind && (queueState.total || 0) > 0 && (!queueState.complete || queueState.shown)
    readonly property int activeIndex: {
        const items = queueState.rows || []
        for (let index = 0; index < items.length; ++index) if (items[index].status === "running") return index
        return -1
    }
    readonly property var currentRow: {
        const items = queueState.rows || []
        return items.find(function(row) { return row.id === panel.queueState.current_row_id }) || ({})
    }
    function duration(seconds) {
        const total = Math.max(0, Math.floor(seconds || 0))
        return [Math.floor(total / 3600), Math.floor(total / 60) % 60, total % 60]
            .map(function(part) { return String(part).padStart(2, "0") }).join(":")
    }
    function followActive() {
        if (activeIndex < 0 || !applies || !queueState.shown) return
        rows.forceLayout()
        rows.positionViewAtIndex(activeIndex, ListView.Contain)
    }
    onActiveIndexChanged: followActive()
    visible: applies
    implicitHeight: content.implicitHeight + 28
    radius: 12; color: AppTheme.surface; border.color: queueState.complete ? AppTheme.success : AppTheme.line
    ColumnLayout {
        id: content
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14
        spacing: 10
        RowLayout {
            Layout.fillWidth: true
            Label { visible: !!panel.queueState.complete; text: "✓"; color: AppTheme.success; font.pixelSize: 24; Accessible.ignored: true }
            Label {
                objectName: "batchHeading_" + panel.kind
                Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap
                font.pixelSize: 15; font.weight: Font.DemiBold; color: AppTheme.ink
                text: panel.queueState.complete
                    ? (panel.kind === "voice" ? "Đã tạo giọng đọc cho " : "Đã chuyển đổi ") + panel.queueState.total + " bài giảng"
                    : "Hàng đợi · " + (panel.queueState.total || 0) + " bài" + (panel.queueState.running ? " · Đang xử lý lần lượt" : "")
            }
            ActionButton {
                objectName: "batchShow_" + panel.kind; text: "Xem danh sách"; visible: !panel.queueState.shown
                implicitHeight: 32; onClicked: panel.controller.show()
            }
        }
        Label {
            objectName: "batchCompletionNotice_" + panel.kind
            visible: !!panel.queueState.complete; Layout.fillWidth: true; wrapMode: Text.WordWrap
            text: "Các bài đã được lưu vào Thư viện. Xem kết quả bên dưới, chọn lượt khác hoặc về Thư viện khi sẵn sàng."
            color: AppTheme.ink; font.pixelSize: 13
        }
        Label {
            visible: !!panel.queueState.shown; Layout.fillWidth: true; wrapMode: Text.WordWrap
            color: AppTheme.muted; font.pixelSize: 12
            text: panel.queueState.complete ? panel.queueState.summary || ""
                : panel.queueState.phase === "draft" ? "Dùng cấu hình chung ở trên. Tên bài lấy theo từng file."
                : (panel.queueState.summary || "") + " · " + ((panel.queueState.counts || {}).done || 0) + " hoàn tất · "
                  + ((panel.queueState.counts || {}).failed || 0) + " lỗi · " + ((panel.queueState.counts || {}).waiting || 0) + " chờ"
        }
        ColumnLayout {
            visible: !!panel.queueState.shown && panel.queueState.phase !== "draft"
            Layout.fillWidth: true; spacing: 8
            RowLayout {
                visible: !!panel.currentRow.id && panel.queueState.phase !== "finished"; Layout.fillWidth: true
                Label {
                    Layout.fillWidth: true; Layout.minimumWidth: 0; elide: Text.ElideMiddle; textFormat: Text.PlainText
                    text: panel.currentRow.name || ""; color: AppTheme.ink; font.pixelSize: 13
                }
                Label {
                    objectName: "batchPercent_" + panel.kind
                    text: (panel.currentRow.percent || 0) + "%"; color: AppTheme.ink; font.pixelSize: 13; font.bold: true
                }
            }
            ProgressBar {
                objectName: "batchProgress_" + panel.kind
                visible: !!panel.currentRow.id && panel.queueState.phase !== "finished"
                value: (panel.currentRow.percent || 0) / 100; Layout.fillWidth: true; implicitHeight: 6
            }
            RowLayout {
                Layout.fillWidth: true
                Label {
                    objectName: "batchFileTime_" + panel.kind
                    text: "Thời gian bài này: " + panel.duration(panel.currentRow.elapsed_seconds)
                    visible: !!panel.currentRow.id && !panel.queueState.complete; color: AppTheme.muted; font.pixelSize: 12
                }
                Item { Layout.fillWidth: true }
                Label {
                    objectName: "batchTotalTime_" + panel.kind
                    text: "Tổng thời gian: " + panel.duration(panel.queueState.elapsed_seconds)
                    color: AppTheme.muted; font.pixelSize: 12
                }
            }
        }
        Label {
            objectName: "batchMessage_" + panel.kind
            visible: !!panel.queueState.shown && !!panel.queueState.message && panel.queueState.phase === "paused"
            text: panel.queueState.message || ""; textFormat: Text.PlainText
            Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: AppTheme.danger
        }
        ListView {
            id: rows
            objectName: "batchRows_" + panel.kind
            visible: !!panel.queueState.shown; Layout.fillWidth: true
            Layout.preferredHeight: Math.min(270, Math.ceil(contentHeight) + 2)
            clip: true; spacing: 8; model: panel.visible && panel.applies && panel.queueState.shown ? panel.queueState.rows || [] : []
            ScrollBar.vertical: SlimScrollBar { policy: rows.contentHeight > 270 ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff }
            currentIndex: panel.activeIndex
            onModelChanged: { panel.followActive(); Qt.callLater(panel.followActive) }
            delegate: Rectangle {
                required property var modelData
                required property int index
                width: rows.width - (rows.contentHeight > 270 ? 20 : 0); implicitHeight: line.implicitHeight + 18
                radius: 8; color: modelData.status === "running" ? AppTheme.adapt("#e8f1ff") : "transparent"
                border.color: AppTheme.line
                RowLayout {
                    id: line
                    anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 9
                    spacing: 10
                    Label { text: (index + 1) + "."; color: AppTheme.muted; font.pixelSize: 12 }
                    ColumnLayout {
                        Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
                        Label {
                            objectName: "batchName_" + modelData.id
                            text: modelData.name; textFormat: Text.PlainText
                            color: AppTheme.ink; font.pixelSize: 13; elide: Text.ElideMiddle; Layout.fillWidth: true
                            ToolTip.visible: fileHover.hovered; ToolTip.text: text
                            HoverHandler { id: fileHover }
                        }
                        Label {
                            objectName: "batchStatus_" + modelData.id
                            text: modelData.message || "Chờ xử lý"; textFormat: Text.PlainText
                            font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true
                            color: modelData.status === "failed" ? AppTheme.danger : modelData.status === "done" ? AppTheme.success : AppTheme.muted
                        }
                        Label {
                            visible: modelData.status === "done" || modelData.status === "failed"
                            text: "Thời gian: " + panel.duration(modelData.elapsed_seconds)
                            color: AppTheme.muted; font.pixelSize: 12
                        }
                    }
                    ActionButton {
                        objectName: "batchResult_" + modelData.id; text: panel.kind === "word" ? "Mở Word" : "Xem bài"; implicitHeight: 32
                        visible: !!modelData.lesson_id || panel.kind === "word" && modelData.status === "done" && !!modelData.word_id; enabled: !panel.working
                        onClicked: panel.controller.openResult(modelData.id)
                    }
                    ActionButton {
                        objectName: "batchFolder_" + modelData.id; text: "Mở thư mục"; implicitHeight: 32
                        visible: !!modelData.output; enabled: !panel.working
                        ToolTip.visible: hovered; ToolTip.text: modelData.output || ""
                        onClicked: panel.controller.openFolder(modelData.id)
                    }
                    ActionButton {
                        objectName: "batchRemove_" + modelData.id; text: "×"; implicitHeight: 32; implicitWidth: 32
                        visible: panel.queueState.phase === "draft"; enabled: !panel.working
                        Accessible.name: "Bỏ " + modelData.name + " khỏi hàng đợi"
                        onClicked: panel.controller.remove(modelData.id)
                    }
                }
            }
        }
        Flow {
            visible: panel.footerActions && !!panel.queueState.shown && !panel.queueState.running; Layout.fillWidth: true; spacing: 8
            ActionButton {
                objectName: "batchResume_" + panel.kind; text: "Tiếp tục"; visible: !!panel.queueState.canResume && panel.queueState.phase !== "draft"
                enabled: !panel.working; onClicked: panel.controller.resume()
            }
            ActionButton {
                objectName: "batchRetry_" + panel.kind; text: "Thử lại bài lỗi"; visible: !!panel.queueState.canRetry
                enabled: !panel.working; onClicked: panel.controller.retryFailed()
            }
            ActionButton {
                objectName: "batchClear_" + panel.kind; text: "Bỏ danh sách"; enabled: !panel.working; visible: !panel.queueState.complete
                ToolTip.visible: hovered; ToolTip.text: "Giữ nguyên các bài và file đã tạo"
                onClicked: panel.controller.clear()
            }
            ActionButton {
                objectName: "batchNew_" + panel.kind
                text: panel.kind === "voice" ? "Tạo giọng cho bài khác" : "Chuyển đổi bài khác"
                visible: !!panel.queueState.complete; enabled: !panel.working
                onClicked: panel.newBatchRequested()
            }
            ActionButton {
                objectName: "batchLibrary_" + panel.kind; text: "Về Thư viện"; primary: true
                visible: !!panel.queueState.complete; enabled: !panel.working
                onClicked: panel.controller.finish()
            }
        }
    }
}
