import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property var lesson: ({})
    property var voices: []
    property string conversion: ""
    property int slides: 0
    color: AppTheme.surface; radius: 16; border.color: AppTheme.adapt("#e0e8f3")
    readonly property var savedVoices: voices.filter(function(row) { return !!row.id && !!row.ready })
    implicitHeight: content.implicitHeight + 32
    ColumnLayout {
        id: content
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16
        spacing: 12
        Label { text: "Thông tin bài giảng"; color: AppTheme.adapt("#112650"); font.pixelSize: 15; font.weight: Font.DemiBold }
        GridLayout {
            Layout.fillWidth: true; columns: width >= 660 ? 4 : 2; columnSpacing: 20; rowSpacing: 10
            Label { text: "Chuyển ngữ"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
            Label { objectName: "lessonConversionInformation"; text: card.lesson.voice_only ? "PowerPoint nguyên bản" : card.conversion; color: AppTheme.adapt("#112650"); font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Label { text: "Số slide"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
            Label { text: card.slides; color: AppTheme.adapt("#112650"); font.pixelSize: 13; Layout.fillWidth: true }
            Label { text: "Thiết kế"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
            Label { text: card.lesson.presentation_style === "source" || card.lesson.voice_only ? "Giữ thiết kế PowerPoint gốc" : "Mẫu BiliClass"; color: AppTheme.adapt("#112650"); font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Label { text: "Môn · Lớp"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
            Label { text: [card.lesson.subject, card.lesson.education_level, card.lesson.grade ? "Lớp " + card.lesson.grade : ""].filter(function(value) { return !!value }).join(" · "); color: AppTheme.adapt("#112650"); font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Label { text: "Vị trí loa"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
            Label { text: ({bottom_left: "Trái dưới", bottom_center: "Giữa dưới", bottom_right: "Phải dưới"})[card.lesson.speaker_position || "bottom_right"]; color: AppTheme.adapt("#112650"); font.pixelSize: 13; Layout.fillWidth: true }
            Label { text: "Ngày tạo"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
            Label { text: card.lesson.created_at ? Qt.formatDateTime(new Date(card.lesson.created_at), "dd/MM/yyyy · HH:mm") : "—"; color: AppTheme.adapt("#112650"); font.pixelSize: 13; Layout.fillWidth: true }
        }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: AppTheme.adapt("#e0e8f3") }
        Label { text: "Giọng đọc"; color: AppTheme.adapt("#667997"); font.pixelSize: 13 }
        Label { objectName: "lessonNoVoiceInformation"; visible: !card.savedVoices.length; text: "Chưa có giọng đọc hoàn tất"; color: AppTheme.adapt("#112650"); font.pixelSize: 13 }
        Repeater {
            model: card.savedVoices
            Label {
                required property var modelData
                objectName: "lessonVoiceInformation_" + modelData.id
                text: modelData.title
                textFormat: Text.PlainText; wrapMode: Text.WordWrap; Layout.fillWidth: true
                color: AppTheme.adapt("#168567"); font.pixelSize: 13
            }
        }
    }
}
