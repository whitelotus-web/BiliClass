import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    id: page
    required property var classroom
    required property var bridge
    spacing: 17
    Label { text: "Báo cáo tiết học"; font.pixelSize: 28; font.bold: true; color: "#112650" }
    RowLayout { Layout.fillWidth: true
        SelectBox { id: sessions; model: classroom.sessions; textRole: "title"; Layout.fillWidth: true }
        ActionButton { text: "Xem kết quả"; iconName: "view"; enabled: classroom.sessions.length > 0; onClicked: classroom.openReport(classroom.sessions[sessions.currentIndex].id) }
        ActionButton { text: "Làm mới"; iconName: "refresh"; onClicked: classroom.refreshReports() }
    }
    Label { visible: classroom.sessions.length === 0; text: "Chưa có phiên học. Kết quả xuất hiện sau khi bắt đầu lớp và nhận phản hồi."; wrapMode: Text.WordWrap; Layout.fillWidth: true; color: "#667997" }
    ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; contentWidth: availableWidth; clip: true
        ColumnLayout { width: parent.width; spacing: 18
            Label { text: classroom.selectedReport.title || "Chọn một phiên để xem"; font.pixelSize: 23; font.bold: true; color: "#112650"; textFormat: Text.PlainText }
            RowLayout { visible: !!classroom.selectedReport.id; Layout.fillWidth: true
                Label { text: [classroom.selectedReport.lesson_title || "Bài không còn trong thư viện", classroom.selectedReport.subject || "", classroom.selectedReport.grade ? "Khối " + classroom.selectedReport.grade : "", classroom.selectedReport.conversion_label || "Bài đã lưu", "Bản " + (classroom.selectedReport.revision || "?")].filter(function(value) { return !!value }).join(" · "); color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                ActionButton { text: "Mở bài gốc"; enabled: !!classroom.selectedReport.lesson_id; onClicked: bridge.openLesson(classroom.selectedReport.lesson_id) }
            }
            Label { visible: !!classroom.selectedReport.id; text: classroom.selectedReport.recommendation || ""; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Repeater { model: classroom.selectedReport.concepts || []
                ColumnLayout { required property var modelData; Layout.fillWidth: true; spacing: 5
                    Label { text: modelData.label; color: "#112650"; font.bold: true; textFormat: Text.PlainText }
                    ProgressBar { Layout.fillWidth: true; value: (modelData.percent || 0) / 100 }
                    Label { text: modelData.correct + "/" + modelData.answered + " phản hồi đúng · " + modelData.questions + " câu · " + modelData.people + " người" + (modelData.confidence === "insufficient" ? " · Mẫu còn ít, chưa phân loại mức hiểu" : ""); color: modelData.confidence === "insufficient" ? "#667997" : "#168567"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                }
            }
            Repeater { model: classroom.selectedReport.rounds || []
                Rectangle { required property var modelData; Layout.fillWidth: true; implicitHeight: roundContent.implicitHeight + 28; radius: 12; color: "white"; border.color: "#e0e8f3"
                    ColumnLayout { id: roundContent; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; spacing: 7
                        Label { text: (modelData.recheck_of ? "Kiểm tra lại · " : "") + modelData.prompt; font.bold: true; color: "#112650"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                        Label { text: modelData.answered + "/" + modelData.eligible + " đã trả lời · " + modelData.unanswered + " chưa trả lời · " + (modelData.kind === "poll" ? "Khảo sát không chấm điểm" : modelData.correct + "/" + modelData.answered + " đúng") + " · " + modelData.status; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        Repeater { model: modelData.options
                            Label { required property var modelData; text: modelData.id + ": " + modelData.count + " (" + (modelData.percent === null ? "chưa có dữ liệu" : modelData.percent + "%") + ")" + (modelData.count > 0 && modelData.misconception ? " · Có dấu hiệu: " + modelData.misconception : ""); color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                        }
                    }
                }
            }
            Repeater { model: classroom.selectedReport.comparisons || []
                Label { required property var modelData; text: "Kiểm tra lại: " + modelData.before + "% → " + modelData.after + "% · " + modelData.before_count + " / " + modelData.after_count + " người. " + modelData.note; color: "#0869f9"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
            }
            Label { visible: !!classroom.selectedReport.id && (classroom.selectedReport.rounds || []).length === 0; text: "Phiên này chưa có dữ liệu kiểm tra. Không suy ra mức hiểu bài từ số lần nghe hoặc xem tiếng Việt."; wrapMode: Text.WordWrap; Layout.fillWidth: true; color: "#667997" }
        }
    }
    RowLayout { Layout.fillWidth: true
        ActionButton { text: "Xuất CSV"; iconName: "download"; enabled: !!classroom.selectedReport.id; onClicked: csvSave.open() }
        ActionButton { text: "CSV từng phản hồi"; iconName: "download"; enabled: !!classroom.selectedReport.id; onClicked: responsesSave.open() }
        ActionButton { text: "Xóa phiên"; iconName: "delete"; enabled: !!classroom.selectedReport.id; onClicked: deleteDialog.open() }
        Item { Layout.fillWidth: true }
        SelectBox { id: host; model: classroom.interfaces; textRole: "name"; visible: classroom.selectedReport.status === "active" }
        ActionButton { text: "Mở lại phiên"; visible: classroom.selectedReport.status === "active"; enabled: !classroom.running && !classroom.busy; onClicked: classroom.start("", "anonymous", 50, classroom.interfaces[host.currentIndex].host, classroom.selectedReport.id) }
    }
    Label { text: classroom.message; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
    FileDialog { id: responsesSave; title: "Xuất từng phản hồi"; fileMode: FileDialog.SaveFile; nameFilters: ["CSV (*.csv)"]; defaultSuffix: "csv"; onAccepted: classroom.exportResponses(selectedFile.toString()) }
    FileDialog { id: csvSave; title: "Xuất kết quả"; fileMode: FileDialog.SaveFile; nameFilters: ["CSV (*.csv)"]; defaultSuffix: "csv"; onAccepted: classroom.exportReport(selectedFile.toString()) }
    Dialog { id: deleteDialog; anchors.centerIn: parent; modal: true; title: "Xóa phiên và toàn bộ câu trả lời?"; standardButtons: Dialog.Ok | Dialog.Cancel; onAccepted: classroom.deleteReport(classroom.selectedReport.id) }
}
