import QtQuick

Image {
    required property string iconName
    // Fit the supplied artwork; the original PNGs remain unchanged.
    readonly property var crops: ({
        "keyboard-help": Qt.rect(450, 412, 505, 493),
        "collapse": Qt.rect(493, 363, 268, 541),
        "settings": Qt.rect(374, 401, 507, 534),
        "hide": Qt.rect(280, 360, 694, 550)
    })
    source: "../assets/mascot-controls/" + iconName + ".png"
    sourceClipRect: crops[iconName] || Qt.rect(0, 0, 0, 0)
    fillMode: Image.PreserveAspectFit
    smooth: true
    cache: true
}
