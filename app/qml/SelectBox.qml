import QtQuick
import QtQuick.Controls

ComboBox {
    id: control
    implicitHeight: 39
    font.pixelSize: 12
    leftPadding: 12; rightPadding: 28
    contentItem: Text { text: control.displayText; font: control.font; color: "#112650"; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
    background: Rectangle { color: "white"; radius: 8; border.color: control.activeFocus ? "#0869f9" : "#d8e4f3" }
}
