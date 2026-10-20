import QtQuick

ConfigurationSummary {
    id: card
    property string mode: "both"
    property string voiceName: ""
    property string pairLabel: ""
    property int rate: 0
    property int readable: 0
    property int total: 0
    property int vietnameseSlides: 0
    property int englishSlides: 0
    property bool hasLesson: false
    property string positionLabel: ""
    readonly property var names: pairLabel ? pairLabel.split(" – ") : voiceName.split(" · ")[0].split(" + ")
    readonly property string selectedVoice: mode === "both" ? names.join(" + ") : names[mode === "en" && names.length > 1 ? 1 : 0] || "Chọn giọng"
    entries: [
        {key: "language", text: card.mode === "both" ? "Việt + Anh" : card.mode === "vi" ? "Tiếng Việt" : "Tiếng Anh", emphasis: true},
        {key: "voice", text: "Giọng: " + (card.selectedVoice || "Chưa chọn")},
        {key: "rate", text: "Tốc độ: " + (100 + card.rate * 6) + "%"},
        {key: "speakers", text: (card.mode === "both" ? "2 loa" : "1 loa") + (card.positionLabel ? " · " + card.positionLabel : "")},
        {key: "coverage", text: !card.hasLesson ? "Chưa chọn bài" : card.mode === "both"
            ? "Slide có lời: Việt " + card.vietnameseSlides + "/" + card.total + " · Anh " + card.englishSlides + "/" + card.total
            : card.readable + "/" + card.total + " slide có lời"}
    ]
}
