import QtQuick
import QtQuick.Controls

RadioButton {
    id: radio
    property bool highlightSelection: false
    background: Rectangle {
        radius: 7
        color: radio.highlightSelection && radio.checked ? "#f2f7ff" : "transparent"
        border.width: 1
        border.color: radio.highlightSelection && radio.checked ? "#dce8f8" : "transparent"
    }
    indicator: Rectangle {
        objectName: radio.objectName + "Indicator"
        x: radio.highlightSelection ? 6 : 0; y: (radio.height - height) / 2
        width: 18; height: 18; radius: 9
        color: "white"; border.width: radio.visualFocus ? 2 : 1
        border.color: radio.checked ? "#0869f9" : "#8c9eb8"
        Rectangle { anchors.centerIn: parent; width: 10; height: 10; radius: 5; color: "#0869f9"; visible: radio.checked }
    }
    contentItem: Text {
        leftPadding: 25
        text: radio.text; color: "#112650"; font.pixelSize: 13; font.weight: Font.DemiBold
        wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter
    }
}
