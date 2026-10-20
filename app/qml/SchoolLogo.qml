import QtQuick
import QtQuick.Window
import QtQuick.Effects

Item {
    id: badge
    property alias source: artwork.source
    readonly property alias status: artwork.status
    property bool roundMask: false
    implicitWidth: 40; implicitHeight: 40
    Accessible.name: "Logo trường"
    Image {
        id: artwork
        anchors.fill: parent
        cache: false; smooth: true; mipmap: true
        fillMode: Image.PreserveAspectFit
        sourceSize.width: Math.ceil(width * Screen.devicePixelRatio * 2)
        layer.enabled: badge.roundMask
        layer.effect: MultiEffect {
            maskEnabled: true; maskSource: circleMask
            maskThresholdMin: 0.5; maskSpreadAtMin: 1
        }
    }
    Rectangle {
        id: circle
        anchors.centerIn: parent
        width: Math.min(badge.width, badge.height); height: width; radius: width/2
        color: "white"
    }
    ShaderEffectSource {
        id: circleMask
        sourceItem: circle; hideSource: true; visible: false
        live: badge.roundMask
    }
}
