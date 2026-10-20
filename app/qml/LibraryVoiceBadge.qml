import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: badge
    property var audio: ({})
    property bool expanded: false
    readonly property var languages: {
        const result = []
        const variants = audio.variants || []
        const ready = variants.length ? variants.filter(function(v) { return !!v.ready }) : (audio.ready ? [audio] : [])
        for (const language of ["vi", "en"])
            if (ready.some(function(v) { return v.mode === language || v.mode === "both" })) result.push(language)
        return result
    }
    readonly property bool unfinished: [audio].concat(audio.variants || []).some(function(v) { return ["partial", "pending", "stale"].indexOf(v.status) >= 0 })
    readonly property string text: languages.length ? (expanded ? "Có giọng " + languages.map(function(v) { return v === "vi" ? "Việt" : "Anh" }).join(" + ") : languages.map(function(v) { return v.toUpperCase() }).join(" · "))
        : audio.status === "checking" ? "Đang kiểm tra giọng…"
        : audio.status === "unknown" ? "Chưa kiểm tra giọng"
        : unfinished ? "Giọng chưa đủ" : "Chưa có giọng"
    spacing: 4
    Accessible.role: Accessible.StaticText
    Accessible.name: languages.length ? "Đã có giọng đọc: " + languages.map(function(v) { return v === "vi" ? "tiếng Việt" : "tiếng Anh" }).join(", ") : text
    Image {
        objectName: "libraryVoiceSpeakerIcon"
        visible: badge.languages.length > 0
        source: "../assets/actions/speaker.svg"; sourceSize.width: 32; sourceSize.height: 32
        Layout.preferredWidth: 15; Layout.preferredHeight: 15
        Accessible.ignored: true
    }
    Label {
        objectName: "libraryVoiceStatusText"
        text: badge.text; color: badge.languages.length ? AppTheme.adapt("#0869f9") : AppTheme.adapt("#667997")
        font.pixelSize: 11; font.weight: badge.expanded || badge.languages.length ? Font.DemiBold : Font.Normal
        Layout.fillWidth: true; Layout.minimumWidth: 0; elide: Text.ElideRight
        Accessible.ignored: true
    }
}
