import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    id: page
    required property var classroom
    required property var bridge
    signal requestClassroom()
    readonly property var filteredSessions: classroom.sessions.filter(function(row) {
        const query = sessionSearch.text.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d")
        const text = [row.title, row.lesson_title, row.subject, row.grade].join(" ").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d")
        return query.split(/\s+/).every(function(word) { return text.indexOf(word) >= 0 }) && (sessionState.currentIndex === 0 || row.status === (sessionState.currentIndex === 1 ? "active" : "ended"))
    }).map(function(row) { return Object.assign({}, row, {display: row.title + " · " + bridge.lessonDateLabel(row.created)}) })
    onVisibleChanged: if (visible) { classroom.refreshReports(); classroom.refreshInterfaces() }
    spacing: 17
    RowLayout { Layout.fillWidth: true; Label { text: "Kết quả lớp học"; font.pixelSize: 28; font.bold: true; color: "#112650"; Layout.fillWidth: true } ActionButton { objectName: "reportBackClassroom"; text: "Về Lớp học"; onClicked: page.requestClassroom() } }
    Label { text: "Xem kết quả từ các tiết đã mở trong Lớp học. Chuyển bài giảng hoặc tạo giọng đọc không tạo báo cáo học sinh."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    RowLayout { Layout.fillWidth: true
        TextField { id: sessionSearch; objectName: "reportSearch"; Layout.fillWidth: true; placeholderText: "Tìm lớp, tên bài hoặc môn… có thể gõ không dấu"; selectByMouse: true }
        SelectBox { id: sessionState; objectName: "reportStateFilter"; model: ["Tất cả tiết học", "Đang mở", "Đã kết thúc"]; Layout.preferredWidth: 165 }
    }
    RowLayout { Layout.fillWidth: true
        SelectBox { id: sessions; objectName: "reportSessionPicker"; model: page.filteredSessions; textRole: "display"; Layout.fillWidth: true; onActivated: if (currentIndex >= 0) classroom.openReport(page.filteredSessions[currentIndex].id) }
        ActionButton { objectName: "openSelectedReport"; text: "Xem kết quả"; iconName: "view"; enabled: sessions.currentIndex >= 0 && sessions.currentIndex < page.filteredSessions.length; onClicked: classroom.openReport(page.filteredSessions[sessions.currentIndex].id) }
        ActionButton { text: "Làm mới"; iconName: "refresh"; onClicked: classroom.refreshReports() }
    }
    Label { objectName: "reportEmptyMessage"; visible: page.filteredSessions.length === 0; text: classroom.sessions.length === 0 ? "Chưa có tiết học. Mở Lớp học, cho học sinh tham gia và trả lời để có kết quả ở đây." : "Không có tiết phù hợp. Thử bỏ bớt từ khóa hoặc bộ lọc."; wrapMode: Text.WordWrap; Layout.fillWidth: true; color: "#667997" }
    ActionButton { objectName: "reportGoClassroom"; visible: classroom.sessions.length === 0; text: "Mở Lớp học"; onClicked: page.requestClassroom() }
    ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; contentWidth: availableWidth; clip: true
        ColumnLayout { width: parent.width; spacing: 18
            Label { text: classroom.selectedReport.title || "Chọn một phiên để xem"; font.pixelSize: 23; font.bold: true; color: "#112650"; textFormat: Text.PlainText }
            Label { visible: !!classroom.selectedReport.id; text: (classroom.selectedReport.participants_joined || 0) + " đã vào lớp · " + (classroom.selectedReport.participants_responded || 0) + " đã trả lời · " + (classroom.selectedReport.rounds || []).length + " lượt câu hỏi"; color: "#0869f9"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            RowLayout { visible: !!classroom.selectedReport.id; Layout.fillWidth: true
                Label { text: [classroom.selectedReport.lesson_title || "Bài không còn trong thư viện", classroom.selectedReport.subject || "", classroom.selectedReport.grade ? "Khối " + classroom.selectedReport.grade : "", classroom.selectedReport.conversion_label || "Bài đã lưu", "Bản " + (classroom.selectedReport.revision || "?")].filter(function(value) { return !!value }).join(" · "); color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                ActionButton { text: "Mở bài gốc"; enabled: !!classroom.selectedReport.lesson_id; onClicked: bridge.openLesson(classroom.selectedReport.lesson_id) }
            }
            Label { visible: !!classroom.selectedReport.id; text: "Tỷ lệ đúng tính trên số đã trả lời; tỷ lệ tham gia tính trên số đủ điều kiện của từng câu. Khảo sát không chấm đúng/sai."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            ActionButton { visible: !!classroom.selectedReport.id; text: reportAdvice.visible ? "Thu gọn nhận xét nâng cao" : "Nhận xét nâng cao"; onClicked: reportAdvice.visible = !reportAdvice.visible }
            Label { id: reportAdvice; visible: false; text: classroom.selectedReport.recommendation || ""; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
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
                        Label { text: modelData.answered + "/" + modelData.eligible + " đã trả lời · " + modelData.unanswered + " chưa trả lời · " + (modelData.kind === "poll" ? "Khảo sát không chấm điểm" : modelData.correct + "/" + modelData.answered + " đúng") + " · " + ({open:"Đang nhận",closed:"Đã đóng",revealed:"Đã công bố"}[modelData.status] || modelData.status); color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
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
    Flow { Layout.fillWidth: true; spacing: 10
        ActionButton { text: "Xuất CSV"; iconName: "download"; enabled: !!classroom.selectedReport.id; onClicked: csvSave.open() }
        ActionButton { text: "CSV từng phản hồi"; iconName: "download"; enabled: !!classroom.selectedReport.id; onClicked: responsesSave.open() }
        ActionButton { text: "Xóa phiên"; iconName: "delete"; enabled: !!classroom.selectedReport.id; onClicked: deleteDialog.open() }
        SelectBox { id: host; width: 185; model: classroom.interfaces; textRole: "name"; visible: classroom.selectedReport.status === "active" }
        ActionButton { text: "Mở lại tiết học"; visible: classroom.selectedReport.status === "active"; enabled: !classroom.running && !classroom.busy && host.currentIndex >= 0 && host.currentIndex < classroom.interfaces.length; onClicked: classroom.start("", "anonymous", 50, classroom.interfaces[host.currentIndex].host, classroom.selectedReport.id) }
    }
    Label { text: classroom.message; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
    FileDialog { id: responsesSave; title: "Xuất từng phản hồi"; fileMode: FileDialog.SaveFile; nameFilters: ["CSV (*.csv)"]; defaultSuffix: "csv"; onAccepted: classroom.exportResponses(selectedFile.toString()) }
    FileDialog { id: csvSave; title: "Xuất kết quả"; fileMode: FileDialog.SaveFile; nameFilters: ["CSV (*.csv)"]; defaultSuffix: "csv"; onAccepted: classroom.exportReport(selectedFile.toString()) }
    Dialog { id: deleteDialog; anchors.centerIn: parent; modal: true; title: "Xóa phiên và toàn bộ câu trả lời?"; standardButtons: Dialog.Ok | Dialog.Cancel; onAccepted: classroom.deleteReport(classroom.selectedReport.id) }
}
