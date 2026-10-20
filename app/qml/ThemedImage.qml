import QtQuick
import QtQuick.Effects

Item {
    id: image
    property color darkTint: AppTheme.icon
    property alias source: original.source
    property alias sourceSize: original.sourceSize
    property alias sourceClipRect: original.sourceClipRect
    property alias fillMode: original.fillMode
    property alias smooth: original.smooth
    property alias mipmap: original.mipmap
    property alias asynchronous: original.asynchronous
    property alias cache: original.cache
    readonly property alias status: original.status
    implicitWidth: 24
    implicitHeight: 24
    Image { id: original; anchors.fill: parent }
    ShaderEffectSource {
        id: mask
        sourceItem: original
        hideSource: AppTheme.dark
        live: AppTheme.dark
        visible: false
    }
    // Use the artwork's alpha, rather than its original dark luminance, for an
    // even foreground tint. The source crop and aspect ratio are preserved.
    Rectangle {
        anchors.fill: parent; color: image.darkTint; visible: AppTheme.dark
        layer.enabled: AppTheme.dark
        layer.effect: MultiEffect {
            maskEnabled: true; maskSource: mask
            maskThresholdMin: 0.5; maskSpreadAtMin: 1
        }
    }
}
