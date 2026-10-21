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
    readonly property string tone: languages.length ? "ready" : audio.status === "checking" ? "checking" : "none"
    readonly property color foreground: tone === "ready" ? (AppTheme.dark ? AppTheme.success : "#126746") : tone === "checking" ? (AppTheme.dark ? AppTheme.blue : "#145bb5") : (AppTheme.dark ? AppTheme.muted : "#526278")
    readonly property color fill: tone === "ready" ? (AppTheme.dark ? "#173c32" : "#e7f6ec")
        : tone === "checking" ? (AppTheme.dark ? "#203b60" : "#e7f0ff")
        : (AppTheme.dark ? "#263246" : "#edf1f6")
    readonly property color outline: tone === "ready" ? (AppTheme.dark ? "#35634f" : "#b7dfc7")
        : tone === "checking" ? (AppTheme.dark ? "#3c5e88" : "#c3d6f3") : AppTheme.line
    readonly property string text: languages.length ? (expanded ? "Có giọng " + languages.map(function(v) { return v === "vi" ? "Việt" : "Anh" }).join(" + ") : languages.map(function(v) { return v.toUpperCase() }).join(" · "))
        : audio.status === "checking" ? "Đang kiểm tra giọng…"
        : "Chưa có giọng"
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
        text: badge.text; color: badge.foreground
        font.pixelSize: 11; font.weight: badge.expanded || badge.languages.length ? Font.DemiBold : Font.Normal
        Layout.fillWidth: true; Layout.minimumWidth: 0; elide: Text.ElideRight
        Accessible.ignored: true
    }
}
