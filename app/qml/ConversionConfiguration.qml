import QtQuick

ConfigurationSummary {
    id: card
    property string formatLabel: ""
    property string formatId: "parallel_columns"
    property bool keepSource: true
    property string templateName: ""
    property string subject: ""
    property string education: ""
    property string grade: ""
    entries: [
        {key: "language", text: card.formatLabel || "Chọn ngôn ngữ", emphasis: true},
        {key: "design", text: card.keepSource ? "Giữ thiết kế gốc" : "Mẫu: " + (card.templateName || "BiliClass")},
        {key: "subject", text: card.subject || "Chưa chọn môn học"},
        {key: "class", text: [card.education, card.grade ? "Lớp " + card.grade : ""].filter(function(v) { return !!v }).join(" · ") || "Chưa chọn lớp"}
    ]
}
