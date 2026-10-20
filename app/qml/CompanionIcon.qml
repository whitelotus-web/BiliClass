import QtQuick

Image {
    required property string iconName
    // Fit the supplied artwork; the original PNGs remain unchanged.
    readonly property var crops: ({
        "keyboard-help": Qt.rect(413, 390, 595, 594),
        "collapse": Qt.rect(447, 374, 360, 617),
        "settings": Qt.rect(322, 339, 611, 642),
        "hide": Qt.rect(242, 343, 766, 628)
    })
    source: "../assets/mascot-controls/" + iconName + ".png"
    sourceClipRect: crops[iconName] || Qt.rect(0, 0, 0, 0)
    fillMode: Image.PreserveAspectFit
    smooth: true
    cache: true
}
