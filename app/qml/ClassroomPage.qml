import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: page
    required property var classroom
    required property var bridge
    onVisibleChanged: if (visible && bridge.lesson.id) bridge.refreshReadiness()
    clip: true
    contentWidth: availableWidth
    ColumnLayout { width: page.availableWidth; spacing: 20
        Label { text: "Lớp học trực tiếp"; color: "#112650"; font.pixelSize: 28; font.bold: true }
        Label { text: classroom.message; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
        ColumnLayout { visible: !classroom.running; Layout.fillWidth: true; spacing: 13
            Label { text: bridge.lesson.title ? "Bài đã chọn: " + bridge.lesson.title + ". Chốt bản chuẩn bị trong Bài giảng trước khi mở lớp." : "Mở một bài trong Bài giảng, duyệt và chốt bản chuẩn bị rồi quay lại đây."; color: "#112650"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
            RowLayout { Layout.fillWidth: true
                SelectBox { id: lessonPicker; model: bridge.lessons; textRole: "title"; Layout.fillWidth: true }
                ActionButton { text: "Chọn bài"; enabled: bridge.lessons.length > 0 && lessonPicker.currentIndex >= 0; onClicked: bridge.selectLessonForClass(bridge.lessons[lessonPicker.currentIndex].id) }
            }
            Label { visible: !!bridge.lesson.id; text: bridge.readiness.prepared_ready ? "Bản bài hiện tại đã chốt. Có thể mở lớp bằng chữ; âm thanh và quiz là tùy chọn." : "Bài này chưa chốt bản chuẩn bị hiện tại. Mở bài để duyệt và chốt trước khi dạy."; color: bridge.readiness.prepared_ready ? "#168567" : "#ad651d"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField { id: title; objectName: "classTitle"; text: ""; placeholderText: "Tên lớp / tiết học, ví dụ: Lớp 11A"; maximumLength: 150; Layout.fillWidth: true }
            RowLayout { Layout.fillWidth: true
                SelectBox { id: mode; objectName: "classMode"; model: ["Ẩn danh", "Số chỗ ngồi"]; currentIndex: bridge.classroomSettings.mode === "seat" ? 1 : 0; Layout.fillWidth: true }
                Label { text: "Sĩ số tối đa" }
                SpinBox { id: size; objectName: "classSize"; from: 1; to: 200; value: bridge.classroomSettings.capacity; editable: true }
            }
            SelectBox { id: host; model: classroom.interfaces; textRole: "name"; Layout.fillWidth: true }
            Label { text: "Chọn Wi-Fi/Ethernet mà học sinh cùng kết nối. Địa chỉ 127.0.0.1 chỉ dùng thử trên máy này. Nếu không truy cập được: kiểm tra mạng chung, Windows Firewall và chế độ cô lập thiết bị của Wi-Fi."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            ActionButton { text: "Bắt đầu lớp"; objectName: "startClassButton"; enabled: !classroom.busy && !!bridge.lesson.id && title.text.trim() !== ""; onClicked: classroom.start(title.text, mode.currentIndex ? "seat" : "anonymous", size.value, classroom.interfaces[host.currentIndex].host, "") }
        }
        RowLayout { visible: classroom.running; Layout.fillWidth: true; spacing: 22
            Image { source: classroom.qrImage; Layout.preferredWidth: 180; Layout.preferredHeight: 180; fillMode: Image.PreserveAspectFit; smooth: false }
            ColumnLayout { Layout.fillWidth: true; spacing: 12
                Label { text: classroom.state.title || ""; font.pixelSize: 22; font.bold: true; color: "#112650"; Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
                Label { text: (classroom.state.joined || 0) + " / " + (classroom.state.capacity || 0) + " đã vào lớp"; font.pixelSize: 20; color: "#0869f9" }
                TextArea { text: classroom.joinUrl; readOnly: true; selectByMouse: true; wrapMode: TextEdit.WrapAnywhere; Layout.fillWidth: true; font.pixelSize: 11 }
                RowLayout { ActionButton { text: "Sao chép liên kết"; onClicked: classroom.copyUrl() } ActionButton { text: "Thử trang học sinh"; iconName: "students"; onClicked: classroom.openStudentPage() } ActionButton { text: "Chiếu câu hỏi"; iconName: "view"; onClicked: bridge.requestClassroomProjection() } }
            }
        }
        ColumnLayout { visible: classroom.running; Layout.fillWidth: true; spacing: 12
            RowLayout { Layout.fillWidth: true
                SelectBox { id: question; model: classroom.state.questions || []; textRole: "vi"; Layout.fillWidth: true }
                SpinBox { id: duration; from: 5; to: 3600; value: bridge.classroomSettings.duration; editable: true }
                Label { text: "giây" }
                SelectBox { id: language; model: ["Việt–Anh", "Tiếng Việt", "English"]; currentIndex: ["both", "vi", "en"].indexOf(bridge.classroomSettings.language) }
            }
            RowLayout { Layout.fillWidth: true
                ActionButton { text: "Mở câu hỏi"; iconName: "play"; objectName: "openQuestionButton"; enabled: (classroom.state.questions || []).length > 0 && (classroom.state.round || {}).status !== "open" && classroom.state.status === "active"; onClicked: classroom.openQuestion(classroom.state.questions[question.currentIndex].id, duration.value, ["both","vi","en"][language.currentIndex], false) }
                ActionButton { text: "Đóng câu"; enabled: (classroom.state.round || {}).status === "open"; onClicked: classroom.action("close") }
                ActionButton { text: "Công bố đáp án"; enabled: (classroom.state.round || {}).status === "closed"; onClicked: classroom.action("reveal") }
                ActionButton { text: "Kiểm tra lại"; iconName: "refresh"; enabled: !!classroom.state.round && classroom.state.round.status !== "open" && classroom.state.status === "active"; onClicked: classroom.openQuestion(classroom.state.round.question_id, duration.value, ["both","vi","en"][language.currentIndex], true) }
            }
            Label { visible: (classroom.state.questions || []).length === 0; text: "Phiên này không có câu hỏi đã duyệt. Thầy cô vẫn có thể dạy bằng bài song ngữ."; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Label { text: classroom.state.round ? classroom.state.round.vi : "Chưa mở câu hỏi"; font.pixelSize: 23; color: "#112650"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
            Label { text: classroom.state.round ? classroom.state.round.answered + " / " + classroom.state.round.eligible + " người đã trả lời" : ""; color: "#0869f9"; font.pixelSize: 20 }
            Repeater { model: (classroom.state.round || {}).options || []
                RowLayout { required property var modelData; Layout.fillWidth: true
                    Label { text: modelData.id + " · " + modelData.vi; color: "#112650"; Layout.preferredWidth: 260; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
                    ProgressBar { Layout.fillWidth: true; value: ((classroom.state.round.counts || {})[modelData.id] || 0) / Math.max(1, classroom.state.round.answered) }
                    Label { text: ((classroom.state.round.counts || {})[modelData.id] || 0) + " phản hồi"; color: "#667997" }
                }
            }
            RowLayout { ActionButton { text: "Kết thúc tiết học"; enabled: classroom.state.status === "active"; onClicked: endDialog.open() } ActionButton { text: "Ngắt máy chủ"; onClicked: classroom.disconnect() } }
        }
    }
    Dialog { id: endDialog; anchors.centerIn: parent; modal: true; title: "Kết thúc tiết học?"; standardButtons: Dialog.Ok | Dialog.Cancel; onAccepted: classroom.action("end") }
}
