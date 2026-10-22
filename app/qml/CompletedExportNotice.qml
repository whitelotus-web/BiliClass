import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: notice
    required property var appBridge
    readonly property var exportState: appBridge.completedExport
    visible: !!exportState.phase
    spacing: 12
    Label {
        objectName: "completedExportMessage"
        Layout.fillWidth: true; Layout.minimumWidth: 0
        font.pixelSize: 12; wrapMode: Text.WrapAnywhere
        color: notice.exportState.phase === "error" ? AppTheme.danger : AppTheme.muted
        text: notice.exportState.phase === "saving" ? "Đang tự lưu PowerPoint có giọng…"
              : notice.exportState.path ? "Đã tự lưu PowerPoint" + (notice.exportState.fallback ? " trong thư mục BiliClass" : " cạnh file gốc") + ": " + notice.exportState.path
              : notice.exportState.message || ""
    }
    ActionButton {
        objectName: "openCompletedExportFolder"; text: "Mở thư mục"
        implicitHeight: 32; visible: !!notice.exportState.path
        onClicked: notice.appBridge.openCompletedExportFolder()
    }
}
