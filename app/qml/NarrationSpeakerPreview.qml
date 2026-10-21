import QtQuick

Item {
    id: preview
    required property string mode
    required property string position
    readonly property var languages: mode === "both" ? ["vi", "en"] : [mode === "vi" ? "vi" : "en"]
    readonly property real iconSize: Math.max(16, Math.min(36, width * .06))
    readonly property real inset: Math.max(4, width * .0125)
    Accessible.role: Accessible.StaticText
    Accessible.name: "Vị trí loa minh họa: " + (mode === "both" ? "Việt và Anh" : mode === "vi" ? "Việt" : "Anh")
    Row {
        objectName: preview.objectName + "Group"
        spacing: Math.max(3, preview.iconSize * .12)
        x: preview.position.endsWith("_left") ? preview.inset
            : preview.position.endsWith("_center") ? (preview.width - width) / 2
            : preview.width - width - preview.inset
        y: preview.position.startsWith("top_") ? preview.inset : preview.height - height - preview.inset
        Repeater {
            model: preview.languages
            Image {
                required property string modelData
                objectName: preview.objectName + "_" + modelData
                width: preview.iconSize; height: preview.iconSize
                source: "../assets/slide-speakers/speaker-" + modelData + ".png"
                sourceSize.width: 1254; sourceSize.height: 1254
                // Same native picture crops used by speaker_artwork.py.
                sourceClipRect: modelData === "vi" ? Qt.rect(171, 248, 976, 976) : Qt.rect(143, 220, 1020, 1020)
                fillMode: Image.PreserveAspectFit; smooth: true; mipmap: true
                Accessible.ignored: true
            }
        }
    }
}
