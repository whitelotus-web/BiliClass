import QtQuick
import QtQuick.Controls

ScrollBar {
    id: bar
    implicitWidth: 18
    implicitHeight: 18
    padding: 6
    minimumSize: 0.06
    policy: ScrollBar.AsNeeded
    hoverEnabled: true
    Accessible.name: orientation === Qt.Vertical ? "Cuộn trang" : "Cuộn ngang"
    contentItem: Rectangle {
        implicitWidth: 6; implicitHeight: 6; radius: 3
        color: bar.pressed ? "#637f9f" : bar.hovered ? "#8ca3bf" : "#bdcbdc"
    }
    background: null
}
