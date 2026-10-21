import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Frame {
    id: checks
    required property var bridge
    property bool expanded: false
    readonly property var report: bridge.lessonDiagnostics
    readonly property var pages: report.pages || []
    property int selected: 0
    readonly property var page: pages.length ? pages[Math.min(selected, pages.length - 1)] : ({})
    signal viewRequested(int slide)
    padding: 10
    visible: !!report.remaining || !!report.image_note
    background: Rectangle { objectName: checks.objectName + "Background"; radius: 10; color: AppTheme.warningSurface; border.color: AppTheme.warningLine }
    contentItem: ColumnLayout {
        spacing: 7
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
                Label { objectName: checks.objectName + "Title"; text: checks.report.title || "Cần xem lại trước khi dạy"; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.warningInk; font.pixelSize: 14; font.weight: Font.DemiBold }
                Label { objectName: checks.objectName + "Summary"; text: checks.report.summary || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.ink; font.pixelSize: 13 }
            }
            ActionButton { text: checks.expanded ? "Thu gọn" : "Xem vị trí"; implicitHeight: 30; onClicked: checks.expanded = !checks.expanded }
        }
        Label {
            objectName: checks.objectName + "ImageNote"
            visible: !!text; text: checks.report.image_note || ""
            Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText
            color: AppTheme.ink; font.pixelSize: 13
        }
        ColumnLayout {
            visible: checks.expanded; Layout.fillWidth: true; spacing: 6
            RowLayout {
                Layout.fillWidth: true
                ComboBox {
                    objectName: checks.objectName + "Page"
                    Layout.fillWidth: true; Layout.minimumWidth: 0
                    model: checks.pages.map(function(row) { return "Slide " + row.slide + (row.source_slide !== row.slide ? " · nguồn " + row.source_slide : "") + (row.failed ? " · Còn lỗi bố cục" : " · Cần đối chiếu") })
                    currentIndex: Math.min(checks.selected, checks.pages.length - 1)
                    onActivated: function(index) { checks.selected = index }
                }
                ActionButton { objectName: checks.objectName + "View"; text: "Xem slide"; implicitHeight: 32; enabled: !checks.bridge.busy && !checks.bridge.narrationBusy && !checks.bridge.powerpointState.active; onClicked: checks.viewRequested(checks.page.slide) }
                ActionButton { objectName: checks.objectName + "Repair"; text: "Kiểm tra và tự sửa"; implicitHeight: 32; visible: !!checks.report.failures; enabled: !checks.bridge.busy && !checks.bridge.narrationBusy && !checks.bridge.powerpointState.opened && !checks.bridge.powerpointState.active; onClicked: checks.bridge.repairConvertedLesson() }
            }
            Repeater {
                model: checks.page.issues || []
                Label {
                    required property var modelData
                    Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText
                    color: AppTheme.ink; font.pixelSize: 13
                    text: "• " + modelData.message + (modelData.excerpt ? " Vùng: “" + modelData.excerpt + "”." : "") + " " + modelData.action
                }
            }
        }
    }
}
