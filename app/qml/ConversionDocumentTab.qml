import QtQuick
import QtQuick.Controls

Button {
    id: tab
    property bool word: false
    property bool selected: false
    text: word ? "Word" : "PowerPoint"
    implicitWidth: 64; implicitHeight: 64; padding: 6
    Accessible.role: Accessible.PageTab
    Accessible.name: "Chuyển đổi bài giảng " + text
    Accessible.selected: selected
    ToolTip.visible: hovered; ToolTip.delay: 350
    ToolTip.text: "Chuyển đổi " + text + " sang song ngữ"
    contentItem: Item {
        Image {
            objectName: tab.objectName + "Logo"
            anchors.centerIn: parent; width: 48; height: 48
            source: tab.word ? "../assets/actions/conversion-word.png" : "../assets/actions/conversion-powerpoint.png"
            sourceSize.width: 256; sourceSize.height: 256
            sourceClipRect: tab.word ? Qt.rect(28, 30, 200, 196) : Qt.rect(30, 35, 196, 188)
            fillMode: Image.PreserveAspectFit; Accessible.ignored: true
        }
    }
    background: Rectangle {
        radius: 9; color: tab.hovered || tab.down ? AppTheme.hover : "transparent"
        border.width: tab.visualFocus ? 2 : 0; border.color: AppTheme.blue
        Rectangle {
            anchors.bottom: parent.bottom; anchors.bottomMargin: 1
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 14; height: 2; radius: 1
            visible: tab.selected; color: AppTheme.accent
        }
    }
}
