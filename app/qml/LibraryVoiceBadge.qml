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
    readonly property string description: languages.length ? "Có giọng " + languages.map(function(v) { return v === "vi" ? "Việt" : "Anh" }).join(" + ")
        : audio.status === "checking" ? "Đang kiểm tra giọng…"
        : "Chưa có giọng"
    readonly property string text: languages.length && !expanded ? languages.map(function(v) { return v.toUpperCase() }).join(" + ") : description
    spacing: 5
    Accessible.role: Accessible.StaticText
    Accessible.name: description
    ThemedImage {
        objectName: "libraryVoiceSpeakerIcon"
        darkTint: badge.foreground
        source: badge.tone === "checking" ? "../assets/actions/refresh.png" : badge.languages.length ? "../assets/actions/speaker-ready.svg" : "../assets/actions/speaker-off.svg"
        sourceSize.width: 48; sourceSize.height: 48; fillMode: Image.PreserveAspectFit
        Layout.preferredWidth: 18; Layout.preferredHeight: 18
        Accessible.ignored: true
    }
    Label {
        objectName: "libraryVoiceStatusText"
        visible: badge.languages.length > 0
        text: badge.text; color: badge.foreground
        font.pixelSize: 11; font.weight: badge.expanded || badge.languages.length ? Font.DemiBold : Font.Normal
        Layout.fillWidth: true; Layout.minimumWidth: 0; elide: Text.ElideRight
        Accessible.ignored: true
    }
}
