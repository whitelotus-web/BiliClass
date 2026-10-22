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
    readonly property color foreground: languages.length ? AppTheme.success
        : tone === "checking" ? AppTheme.blue : (AppTheme.dark ? AppTheme.muted : "#526278")
    readonly property string description: languages.length ? "Có giọng " + languages.map(function(v) { return v === "vi" ? "Việt" : "Anh" }).join(" + ")
        : audio.status === "checking" ? "Đang kiểm tra giọng…"
        : "Chưa có giọng"
    readonly property string text: languages.length && !expanded ? languages.map(function(v) { return v.toUpperCase() }).join(" + ") : description
    spacing: 4
    Accessible.role: Accessible.StaticText
    Accessible.name: description
    ThemedImage {
        objectName: "libraryVoiceSpeakerIcon"
        visible: !badge.languages.length
        tintEnabled: true
        darkTint: badge.foreground
        source: badge.tone === "checking" ? "../assets/actions/refresh.png" : "../assets/actions/speaker-off.svg"
        sourceSize.width: 48; sourceSize.height: 48; fillMode: Image.PreserveAspectFit
        Layout.preferredWidth: 18; Layout.preferredHeight: 18
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
            darkTint: badge.foreground
            fillMode: Image.PreserveAspectFit; smooth: true; mipmap: true
            Layout.preferredWidth: 24; Layout.preferredHeight: 22
            Accessible.ignored: true
        }
    }
}
