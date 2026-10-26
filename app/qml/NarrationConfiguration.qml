import QtQuick

ConfigurationSummary {
    id: card
    required property var appBridge
    property string mode: "both"
    property string voiceName: ""
    property string pairLabel: ""
    property int rate: 0
    property int enRate: rate
    property int readable: 0
    property int total: 0
    property int vietnameseSlides: 0
    property int englishSlides: 0
    property bool hasLesson: false
    property int batchCount: 0
    property string positionLabel: ""
    readonly property var names: pairLabel ? pairLabel.split(" – ") : voiceName.split(" · ")[0].split(" + ")
    readonly property string selectedVoice: mode === "both" ? names.join(" + ") : names[mode === "en" && names.length > 1 ? 1 : 0] || "Chọn giọng"
    entries: [
        {key: "language", text: card.mode === "both" ? "Việt + Anh" : card.mode === "vi" ? "Tiếng Việt" : "Tiếng Anh", emphasis: true},
        {key: "voice", text: "Giọng: " + (card.selectedVoice || "Chưa chọn")},
        {key: "rate", text: card.mode === "both" && card.rate !== card.enRate ? "Việt " + card.appBridge.voiceSpeedLabel(card.rate) + " · Anh " + card.appBridge.voiceSpeedLabel(card.enRate) : "Tốc độ: " + card.appBridge.voiceSpeedLabel(card.mode === "en" ? card.enRate : card.rate)},
        {key: "speakers", text: (card.mode === "both" ? "2 loa" : "1 loa") + (card.positionLabel ? " · " + card.positionLabel : "")},
        {key: "coverage", text: card.batchCount > 0 ? card.batchCount + " bài trong hàng đợi" : !card.hasLesson ? "Chưa chọn bài" : card.mode === "both"
            ? "Slide có lời: Việt " + card.vietnameseSlides + "/" + card.total + " · Anh " + card.englishSlides + "/" + card.total
            : card.readable + "/" + card.total + " slide có lời"}
    ]
}
