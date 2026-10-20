import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property string mode: "both"
    property string voiceName: ""
    property int rate: 0
    property int readable: 0
    property int total: 0
    property bool hasLesson: false
    property string positionLabel: ""
    radius: 9; color: AppTheme.adapt("#f5f8fd"); border.color: AppTheme.adapt("#e0e8f3")
    implicitHeight: content.implicitHeight + 24
    ColumnLayout {
        id: content
        anchors.fill: parent; anchors.margins: 12; spacing: 5
        RowLayout {
        Layout.fillWidth: true
        Label {
            objectName: "narrationConfigurationTitle"
            text: "Cấu hình đã chọn · " + (card.voiceName || "Chọn người đọc") + " · " + (100 + card.rate * 6) + "% · " +
                (card.mode === "both" ? "Việt + Anh" : card.mode === "vi" ? "Tiếng Việt" : "Tiếng Anh")
            color: AppTheme.adapt("#112650"); font.pixelSize: 13; font.weight: Font.DemiBold
            Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        ToolButton {
            id: configurationInfo; text: "ⓘ"; font.pixelSize: 19; implicitWidth: 30; implicitHeight: 28
            Accessible.name: "Giải thích cấu hình giọng đọc"
            ToolTip {
                id: configurationTip; visible: configurationInfo.hovered || configurationInfo.activeFocus; delay: 350
                width: Math.min(420, card.width - 24)
                text: "Loa đọc lời đã lưu của slide khi bấm, kể cả phần xuất hiện sau. Chữ OCR được dịch trên ảnh không tự đưa vào lời đọc. Đọc theo từng hiệu ứng có thể chọn riêng trong Mascot."
                contentItem: Label { text: configurationTip.text; wrapMode: Text.WordWrap; color: AppTheme.adapt("#112650"); font.pixelSize: 12 }
            }
        }
        }
        Label {
            objectName: "narrationConfigurationExplanation"
            text: (card.mode === "both" ? "Tạo hai loa riêng trên slide: Anh và Việt. Mỗi loa đọc một ngôn ngữ."
                : card.mode === "vi" ? "Tạo loa tiếng Việt trên slide." : "Tạo loa tiếng Anh trên slide.") +
                (card.positionLabel ? " Vị trí: " + card.positionLabel.toLowerCase() + "." : "")
            color: AppTheme.adapt("#667997"); font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            objectName: "narrationConfigurationCoverage"
            text: card.hasLesson ? card.readable + "/" + card.total + " slide có lời đọc. Slide không có lời giữ im lặng."
                                  : "Chọn bài giảng để kiểm tra lời đọc."
            color: AppTheme.adapt("#667997"); font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
    }
}
