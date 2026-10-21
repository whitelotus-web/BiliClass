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
    readonly property string languageMode: languages.length === 2 ? "both" : languages[0] || ""
    readonly property color foreground: languageMode === "vi" ? (AppTheme.dark ? "#c4a7ff" : "#7c3aed")
        : languageMode === "en" || tone === "checking" ? AppTheme.blue
        : languageMode === "both" ? AppTheme.success : (AppTheme.dark ? AppTheme.muted : "#526278")
    readonly property color fill: languageMode === "vi" ? (AppTheme.dark ? "#35284d" : "#f3edff")
        : languageMode === "en" ? (AppTheme.dark ? "#203b60" : "#e7f0ff")
        : languageMode === "both" ? (AppTheme.dark ? "#173c32" : "#e7f6ec")
        : tone === "checking" ? (AppTheme.dark ? "#203b60" : "#e7f0ff")
        : (AppTheme.dark ? "#263246" : "#edf1f6")
    readonly property color outline: languageMode === "vi" ? (AppTheme.dark ? "#69508c" : "#d9c5fa")
        : languageMode === "en" ? (AppTheme.dark ? "#3c5e88" : "#c3d6f3")
        : languageMode === "both" ? (AppTheme.dark ? "#35634f" : "#b7dfc7")
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
        visible: !badge.languages.length
        darkTint: badge.foreground
        source: badge.tone === "checking" ? "../assets/actions/refresh.png" : "../assets/actions/speaker-off.svg"
        sourceSize.width: 48; sourceSize.height: 48; fillMode: Image.PreserveAspectFit
        Layout.preferredWidth: 24; Layout.preferredHeight: 24
        Accessible.ignored: true
    }
    Repeater {
        model: badge.languages
        ThemedImage {
            required property string modelData
            objectName: "libraryVoiceIcon_" + modelData
            source: "../assets/library-speakers/speaker-" + modelData + ".png"
            // The teacher's original PNGs stay untouched. Crop only their empty
            // canvas while displaying the language letters already in the art.
            sourceClipRect: modelData === "en" ? Qt.rect(386, 401, 526, 471) : Qt.rect(338, 422, 577, 457)
            tintEnabled: true
            darkTint: modelData === "en" ? AppTheme.blue : AppTheme.dark ? "#c4a7ff" : "#7c3aed"
            fillMode: Image.PreserveAspectFit; smooth: true; mipmap: true
            Layout.preferredWidth: 34; Layout.preferredHeight: 30
            Accessible.ignored: true
        }
    }
}
