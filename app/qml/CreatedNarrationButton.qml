import QtQuick
import QtQuick.Controls

ActionButton {
    id: control
    required property var appBridge
    required property string language
    property int slideNumber: 1
    property string recordId: ""
    property bool shortLabel: false
    readonly property var playback: appBridge.narrationWorkspace.createdPlayback
    readonly property bool playing: playback.record_id === recordId
        && playback.slide === slideNumber && playback.language === language
    readonly property string listenLabel: shortLabel
        ? (language === "vi" ? "Nghe Việt" : "Nghe Anh")
        : (language === "vi" ? "Nghe giọng Việt" : "Nghe giọng Anh")

    // Keep the hit area and neighbouring button in place when playback changes.
    implicitWidth: Math.ceil(Math.max(labelSize.width, stopSize.width))
        + leftPadding + rightPadding + iconSize + 24
    text: playing ? "Dừng nghe" : listenLabel
    iconName: playing ? "" : "play"
    symbol: playing ? "■" : ""
    danger: playing
    enabled: playing || !appBridge.busy
    Accessible.name: playing ? "Dừng nghe giọng " + (language === "vi" ? "Việt" : "Anh") : listenLabel
    ToolTip.visible: hovered
    ToolTip.text: playing ? Accessible.name : "Nghe giọng " + (language === "vi" ? "Việt" : "Anh") + " đã tạo của slide đang xem"
    onClicked: appBridge.narrationWorkspace.toggleCreated(slideNumber, language, recordId)
    TextMetrics { id: labelSize; font: control.font; text: control.shortLabel ? "Nghe Việt" : "Nghe giọng Việt" }
    TextMetrics { id: stopSize; font: control.font; text: "Dừng nghe" }
}
