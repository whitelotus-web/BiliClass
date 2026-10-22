import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    required property var settings
    spacing: 9
    Label { objectName: "shortcutGuideTitle"; text: "Hướng dẫn phím và chuột"; font.pixelSize: 14; font.bold: true; color: AppTheme.adapt("#102e54") }
    Repeater {
        model: [{key: settings.state.labels.en, action: "Đọc / tạm dừng tiếng Anh"},
                {key: settings.state.labels.vi, action: "Đọc / tạm dừng tiếng Việt"},
                {key: settings.state.labels.previous + " / " + settings.state.labels.next, action: "Lùi / tiến hiệu ứng, slide"},
                {key: settings.state.labels.volume_up + " / " + settings.state.labels.volume_down, action: "Âm lượng lời đọc ±5%"},
                {key: "F5", action: "Bắt đầu trình chiếu"},
                {key: "Esc", action: "Thoát trình chiếu"}]
        RowLayout {
            required property var modelData
            required property int index
            Layout.fillWidth: true; spacing: 10
            Rectangle {
                implicitWidth: 112; implicitHeight: 30; color: AppTheme.adapt("#f0f4fa"); border.color: AppTheme.adapt("#cbdcf4"); radius: 5
                Label { objectName: "shortcutHelpKey" + index; anchors.centerIn: parent; text: modelData.key; color: AppTheme.adapt("#102e54"); font.pixelSize: 12; font.bold: true; font.family: "Segoe UI Symbol" }
            }
            Label { text: modelData.action; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: AppTheme.adapt("#526888") }
        }
    }
    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: AppTheme.adapt("#e0e8f4") }
    RowLayout {
        Layout.fillWidth: true; spacing: 10
        Rectangle {
            implicitWidth: 112; implicitHeight: 54; color: AppTheme.adapt("#f0f4fa"); border.color: AppTheme.adapt("#cbdcf4"); radius: 5
            RowLayout {
                anchors.centerIn: parent; spacing: 7
                CompanionIcon { objectName: "shortcutMouseWheelIcon"; iconName: "mouse-wheel"; Layout.preferredWidth: 27; Layout.preferredHeight: 27 }
                Label { text: "Lăn chuột"; font.pixelSize: 11; font.bold: true; color: AppTheme.adapt("#102e54") }
            }
        }
        Label { objectName: "shortcutMouseNavigation"; text: "↑ Lùi · ↓ Tiến hiệu ứng, slide\nTrên slide hoặc bảng trợ giảng, ngoài vùng âm lượng."; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: AppTheme.adapt("#526888") }
    }
    RowLayout {
        Layout.fillWidth: true; spacing: 10
        Rectangle {
            implicitWidth: 112; implicitHeight: 42; color: AppTheme.adapt("#f0f4fa"); border.color: AppTheme.adapt("#cbdcf4"); radius: 5
            RowLayout {
                anchors.centerIn: parent; spacing: 7
                CompanionIcon { iconName: "mouse-wheel"; Layout.preferredWidth: 27; Layout.preferredHeight: 27 }
                Label { text: "Âm lượng"; font.pixelSize: 11; font.bold: true; color: AppTheme.adapt("#102e54") }
            }
        }
        Label { objectName: "shortcutMouseVolume"; text: "↑ Tăng · ↓ Giảm 5%\nLăn trong cả hàng Âm lượng."; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: AppTheme.adapt("#526888") }
    }
    Label { text: "Bấm Mascot để dùng phím cho bài đang gắn. Đổi phím trong Cài đặt → Mascot."; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 11; color: AppTheme.adapt("#667997") }
}
