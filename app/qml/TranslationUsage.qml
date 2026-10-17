import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: usage
    required property var health
    spacing: 8
    function number(value) { return Number(value || 0).toLocaleString(Qt.locale("vi_VN"), "f", 0) }
    RowLayout { Layout.fillWidth: true
        Label { text: "Mức dùng tháng này"; color: "#112650"; font.pixelSize: 14; font.bold: true; Layout.fillWidth: true }
        Label { objectName: "translationGroupCount"; text: (usage.health.keyCount || 0) + " key · " + (usage.health.groupCount || 0) + " nhóm đếm"; color: "#667997"; font.pixelSize: 12 }
    }
    Label { visible: !usage.health.configured; text: "Thêm API key để bắt đầu dịch."; color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true }
    RowLayout { visible: !!usage.health.configured; Layout.fillWidth: true
        Label { text: "Đã ghi nhận tại máy"; color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true }
        Label { objectName: "translationTotalUsage"; text: usage.number(usage.health.used) + " / " + usage.number(usage.health.totalBudget) + " ký tự"; color: "#112650"; font.pixelSize: 12; font.weight: Font.DemiBold }
    }
    Repeater {
        model: usage.health.groups || []
        delegate: ColumnLayout {
            required property var modelData
            Layout.fillWidth: true; spacing: 4
            RowLayout { visible: (usage.health.groupCount || 0) > 1; Layout.fillWidth: true
                Label { text: modelData.project === "mặc định" ? "Nhóm chung" : modelData.project; color: "#112650"; font.pixelSize: 12; Layout.fillWidth: true }
                Label { text: usage.number(modelData.used) + " / " + usage.number(modelData.budget); color: "#667997"; font.pixelSize: 12 }
            }
            ProgressBar { Layout.fillWidth: true; from: 0; to: 100; value: modelData.percent
                background: Rectangle { implicitHeight: 5; color: "#e8eef7"; radius: 2 }
                contentItem: Item { implicitHeight: 5; Rectangle { width: parent.width * Math.min(1, modelData.percent / 100); height: parent.height; radius: 2; color: modelData.level === "normal" ? "#168567" : modelData.level === "warning" ? "#d59020" : "#b14828" } }
            }
            Label { visible: modelData.blocked || modelData.level !== "normal"; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: "#b14828"
                text: modelData.blocked ? "Key đang bị từ chối; kiểm tra trên Google Cloud." : modelData.level === "exhausted" ? "Đã chạm giới hạn đặt tại máy." : "Sắp chạm giới hạn đặt tại máy."
            }
        }
    }
    Label { visible: !!usage.health.unverified; text: "Các key này đang dùng chung một nhóm đếm."; color: "#9c651b"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    Label { text: "Giới hạn do BiliClass đặt, không phải số dư Google Cloud."; color: "#667997"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
}
