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
        Label { objectName: "translationGroupCount"; text: (usage.health.keyCount || 0) + " key · " + (usage.health.counterCount || 0) + " bộ đếm riêng"; color: "#667997"; font.pixelSize: 12 }
    }
    Label { visible: !usage.health.configured; text: "Thêm API key để bắt đầu dịch."; color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true }
    RowLayout { visible: !!usage.health.configured; Layout.fillWidth: true
        Label { text: "Đã ghi riêng theo key tại máy"; color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true }
        Label { objectName: "translationTotalUsage"; text: usage.number(usage.health.used) + " / " + usage.number(usage.health.totalBudget) + " ký tự"; color: "#112650"; font.pixelSize: 12; font.weight: Font.DemiBold }
    }
    Label { objectName: "translationLegacyUsage"; visible: (usage.health.legacyUsed || 0) > 0; text: "Lịch sử chung trước khi tách: " + usage.number(usage.health.legacyUsed) + " ký tự. Giữ nguyên lịch sử; bộ đếm riêng ghi từ RC69."; color: "#9c651b"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    Label { text: "Giới hạn do BiliClass đặt, không phải số dư Google Cloud."; color: "#667997"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
}
