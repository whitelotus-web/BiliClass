import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    required property var settings
    spacing: 9
    Label { text: "Hướng dẫn phím"; font.pixelSize: 14; font.bold: true; color: "#102e54" }
    Repeater {
        model: [{key: settings.state.labels.en, action: "Đọc / tạm dừng tiếng Anh"},
                {key: settings.state.labels.vi, action: "Đọc / tạm dừng tiếng Việt"},
                {key: settings.state.labels.both, action: "Đọc / tạm dừng Việt–Anh"},
                {key: "← / →", action: "Lùi / tiến hiệu ứng, slide"},
                {key: "↑ / ↓", action: "Âm lượng lời đọc ±5%"},
                {key: "F5", action: "Bắt đầu trình chiếu"},
                {key: "Esc", action: "Thoát trình chiếu"}]
        RowLayout {
            required property var modelData
            Layout.fillWidth: true; spacing: 10
            Rectangle {
                implicitWidth: 112; implicitHeight: 30; color: "#f0f4fa"; border.color: "#cbdcf4"; radius: 5
                Label { anchors.centerIn: parent; text: modelData.key; color: "#102e54"; font.pixelSize: 12; font.bold: true; font.family: "Segoe UI Symbol" }
            }
            Label { text: modelData.action; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: "#526888" }
        }
    }
    Label { text: "Bấm Mascot để dùng phím cho bài đang gắn. Đổi phím trong Cài đặt → Mascot."; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 11; color: "#667997" }
}
