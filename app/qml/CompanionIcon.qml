import QtQuick
import QtQuick.Window

ThemedImage {
    required property string iconName
    source: "../assets/mascot-controls/" + iconName + ".svg"
    // Rasterize the rounded vector strokes above display resolution, including
    // Windows scaling, so small icons retain smooth, even edges.
    sourceSize.width: Math.ceil(width * Screen.devicePixelRatio * 2)
    sourceSize.height: Math.ceil(height * Screen.devicePixelRatio * 2)
    fillMode: Image.PreserveAspectFit
    smooth: true
    mipmap: true
    cache: true
}
