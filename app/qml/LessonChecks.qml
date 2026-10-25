import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Frame {
    id: checks
    required property var bridge
    property bool expanded: false
    readonly property var report: bridge.lessonDiagnostics
    readonly property var pages: report.pages || []
    readonly property var terminology: report.terminology || ({})
    property int selected: 0
    readonly property var page: pages.length ? pages[Math.min(selected, pages.length - 1)] : ({})
    signal viewRequested(int slide)
    function showSelected() {
        if (page.slide && !bridge.busy && !bridge.narrationBusy && !bridge.powerpointState.active && !bridge.powerpointState.starting)
            viewRequested(page.slide)
    }
    Connections {
        target: checks.bridge
        function onQuickResultChanged() {
            if (!checks.expanded) return
            var slide = checks.bridge.quickResult.slide
            for (var index = 0; index < checks.pages.length; index++) {
                if (checks.pages[index].slide === slide) {
                    checks.selected = index
                    return
                }
            }
        }
    }
    onExpandedChanged: { if (expanded) showSelected() }
    padding: 10
    visible: !!report.has_report || !!report.image_note || !!terminology.summary
    background: Rectangle { objectName: checks.objectName + "Background"; radius: 10; color: checks.report.attention ? AppTheme.warningSurface : "transparent"; border.color: checks.report.attention ? AppTheme.warningLine : AppTheme.line }
    contentItem: ColumnLayout {
        spacing: 7
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
                Label { objectName: checks.objectName + "Title"; text: checks.report.title || "Kiểm tra tự động"; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: checks.report.attention ? AppTheme.warningInk : AppTheme.ink; font.pixelSize: 14; font.weight: Font.DemiBold }
                Label { objectName: checks.objectName + "Summary"; visible: !!checks.report.attention || checks.expanded; text: checks.report.summary || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.ink; font.pixelSize: 13 }
            }
            ActionButton { objectName: checks.objectName + "Repair"; text: "Thử căn lại"; implicitHeight: 32; visible: !!checks.report.attention; enabled: !checks.bridge.busy && !checks.bridge.narrationBusy && !checks.bridge.powerpointState.opened && !checks.bridge.powerpointState.active; onClicked: checks.bridge.repairConvertedLesson() }
            ActionButton { objectName: checks.objectName + "Toggle"; text: checks.expanded ? "Thu gọn" : checks.report.attention ? "Xem lỗi còn lại" : "Chi tiết và phạm vi"; implicitHeight: 30; onClicked: checks.expanded = !checks.expanded }
        }
        Label {
            objectName: checks.objectName + "ImageNote"
            visible: checks.expanded && !!text; text: checks.report.image_note || ""
            Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText
            color: AppTheme.ink; font.pixelSize: 13
        }
        ColumnLayout {
            visible: checks.expanded; Layout.fillWidth: true; spacing: 6
            Label { objectName: checks.objectName + "Scope"; text: checks.report.scope_note || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.ink; font.pixelSize: 13 }
            Label { objectName: checks.objectName + "Terminology"; visible: !!text; text: checks.terminology.summary || ""; textFormat: Text.PlainText; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.ink; font.pixelSize: 13 }
            Label { visible: !!checks.terminology.inferred; text: "Môn tham khảo được suy ra từ nội dung: " + (checks.terminology.subject || ""); textFormat: Text.PlainText; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.ink; font.pixelSize: 13 }
            Repeater {
                model: checks.terminology.concerns || []
                Label { required property var modelData; text: (modelData.slide ? "Slide nguồn " + modelData.slide + ": " : "") + modelData.message + " “" + modelData.excerpt + "”"; textFormat: Text.PlainText; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.warningInk; font.pixelSize: 13 }
            }
            Label { visible: !!checks.terminology.unresolved && checks.terminology.unresolved.length > 0; text: "Chưa tìm được tham chiếu phù hợp: " + (checks.terminology.unresolved || []).join(", "); textFormat: Text.PlainText; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: AppTheme.ink; font.pixelSize: 13 }
            Label { visible: !!checks.terminology.sources && checks.terminology.sources.length > 0; text: "Nguồn thuật ngữ tham khảo:\n" + (checks.terminology.sources || []).join("\n"); textFormat: Text.PlainText; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: AppTheme.ink; font.pixelSize: 12 }
            RowLayout {
                visible: checks.pages.length > 0
                Layout.fillWidth: true
                ComboBox {
                    objectName: checks.objectName + "Page"
                    Layout.fillWidth: true; Layout.minimumWidth: 0
                    model: checks.pages.map(function(row) { return "Slide " + row.slide + (row.source_slide !== row.slide ? " · nguồn " + row.source_slide : "") + (row.failed ? " · Chưa sửa xong bố cục" : row.attention ? " · Chưa hoàn thiện" : " · Giới hạn kiểm tra") })
                    currentIndex: Math.min(checks.selected, checks.pages.length - 1)
                    onActivated: function(index) { checks.selected = index; checks.showSelected() }
                }
                ActionButton { objectName: checks.objectName + "View"; text: "Xem slide"; implicitHeight: 32; enabled: !!checks.page.slide && !checks.bridge.busy && !checks.bridge.narrationBusy && !checks.bridge.powerpointState.active; onClicked: checks.viewRequested(checks.page.slide) }
            }
            Repeater {
                model: checks.page.issues || []
                Label {
                    required property var modelData
                    Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText
                    color: AppTheme.ink; font.pixelSize: 13
                    text: "• " + modelData.message + (modelData.location ? " " + modelData.location : "") + (modelData.excerpt ? " Vùng: “" + modelData.excerpt + "”." : "") + " " + modelData.action
                }
            }
        }
    }
}
