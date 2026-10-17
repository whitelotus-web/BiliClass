import QtQuick

Item {
    id: artwork
    property string name: "home"
    property bool active: false
    objectName: name + "NavigationIcon"
    implicitWidth: 29; implicitHeight: 29
    Image {
        anchors.fill: parent
        visible: artwork.name !== "narration"
        source: visible ? "../assets/navigation/" + artwork.name + (artwork.active ? "-active" : "") + ".png" : ""
        sourceSize.width: 64; sourceSize.height: 64
        fillMode: Image.PreserveAspectFit
    }
    Canvas {
        id: narrationArt
        objectName: artwork.name + "NavigationArt"
        anchors.fill: parent
        visible: artwork.name === "narration"
        property url imageUrl: Qt.resolvedUrl("../assets/navigation/narration.png")
        property bool highlighted: artwork.active
        Component.onCompleted: if (visible) loadImage(imageUrl)
        onVisibleChanged: if (visible) { loadImage(imageUrl); requestPaint() }
        onImageLoaded: requestPaint()
        onHighlightedChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            if (!visible || !isImageLoaded(imageUrl)) return
            const context = getContext("2d")
            context.clearRect(0, 0, width, height)
            context.globalCompositeOperation = "source-over"
            // Keep the supplied PNG unchanged; its transparent margin is only
            // cropped while drawing into the same 29 px frame as the other tabs.
            context.drawImage(imageUrl, 198, 200, 914, 914, 0, 0, width, height)
            if (highlighted) {
                context.globalCompositeOperation = "source-in"
                context.fillStyle = "#0869f9"
                context.fillRect(0, 0, width, height)
                context.globalCompositeOperation = "source-over"
            }
        }
    }
}
