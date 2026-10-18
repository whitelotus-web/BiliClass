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
    radius: 9; color: "#f5f8fd"; border.color: "#e0e8f3"
    implicitHeight: content.implicitHeight + 24
    ColumnLayout {
        id: content
        anchors.fill: parent; anchors.margins: 12; spacing: 5
        Label {
            objectName: "narrationConfigurationTitle"
            text: (card.voiceName || "Chọn người đọc") + " · " + (100 + card.rate * 6) + "% · " +
                (card.mode === "both" ? "Việt + Anh" : card.mode === "vi" ? "Tiếng Việt" : "Tiếng Anh")
            color: "#112650"; font.pixelSize: 13; font.weight: Font.DemiBold
            Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            objectName: "narrationConfigurationExplanation"
            text: card.mode === "both" ? "Tạo lời đọc cho cả hai ngôn ngữ. PowerPoint có nút loa Việt, loa Anh và đọc Việt–Anh chung để thầy cô chọn khi dạy."
                : card.mode === "vi" ? "Tạo lời đọc tiếng Việt và nút loa Việt trên slide. Phù hợp khi cần giải thích nội dung bằng tiếng Việt."
                : "Tạo lời đọc tiếng Anh và nút loa Anh trên slide. Phù hợp khi luyện nghe hoặc dạy bằng tiếng Anh."
            color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            text: "Loa đọc toàn bộ lời đã lưu của slide khi bấm, kể cả phần xuất hiện sau. Đọc theo từng hiệu ứng được chọn riêng trong Mascot."
            color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            objectName: "narrationConfigurationCoverage"
            text: card.hasLesson ? card.readable + "/" + card.total + " slide có lời phù hợp. Có thể kiểm tra lời đọc hoặc nghe thử trước khi tạo."
                                  : "Chọn bài giảng để kiểm tra lời đọc cho cấu hình này."
            color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
    }
}
