import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: usage
    required property var health
    spacing: 9
    Label { text: "Ký tự dịch trong tháng · Ước tính tại máy"; color: "#112650"; font.pixelSize: 14; font.bold: true; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    Label { visible: !usage.health.configured; text: "Chưa có API key. Thêm key trong Cài đặt → Google Dịch."; color: "#9c651b"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    Repeater {
        model: usage.health.groups || []
        delegate: ColumnLayout {
            required property var modelData
            Layout.fillWidth: true; spacing: 4
            RowLayout { Layout.fillWidth: true
                Label { text: (modelData.unverified ? "Nhóm chung chưa xác minh" : modelData.project) + " · " + modelData.keyCount + " key"; color: "#112650"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Label { text: modelData.used.toLocaleString(Qt.locale("vi_VN"), "f", 0) + " / " + modelData.budget.toLocaleString(Qt.locale("vi_VN"), "f", 0); color: "#667997"; font.pixelSize: 12 }
            }
            ProgressBar { Layout.fillWidth: true; from: 0; to: 100; value: modelData.percent
                background: Rectangle { implicitHeight: 5; color: "#e8eef7"; radius: 2 }
                contentItem: Item { implicitHeight: 5; Rectangle { width: parent.width * Math.min(1, modelData.percent / 100); height: parent.height; radius: 2; color: modelData.level === "normal" ? "#168567" : modelData.level === "warning" ? "#d59020" : "#b14828" } }
            }
            Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12
                color: modelData.level === "normal" && !modelData.blocked ? "#667997" : "#b14828"
                text: modelData.blocked ? "Google đã từ chối key/hạn mức của nhóm này. Kiểm tra trên Cloud." : modelData.level === "exhausted" ? "Đã chạm giới hạn BiliClass. Nhóm này sẽ không nhận yêu cầu dịch mới." : "Còn khoảng " + modelData.remaining.toLocaleString(Qt.locale("vi_VN"), "f", 0) + " ký tự theo giới hạn BiliClass" + (modelData.level === "normal" ? "." : " · Gần giới hạn đã đặt.")
            }
        }
    }
    Label { visible: !!usage.health.unverified; text: "Các key chưa khai báo nhóm đang dùng chung bộ đếm lịch sử. Tên key hoặc Gmail riêng không xác minh được dự án Google Cloud."; color: "#9c651b"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    Label { text: "Số này chỉ gồm lượng ghi nhận tại máy, không phải số dư Google Cloud. Cảnh báo ở 80% và 95%; chặn gửi mới khi chạm giới hạn đã đặt. Bản dịch đã lưu vẫn dùng được."; color: "#667997"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
}
