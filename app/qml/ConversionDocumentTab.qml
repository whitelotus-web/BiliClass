import QtQuick
import QtQuick.Controls

Button {
    id: tab
    property bool word: false
    property bool selected: false
    text: word ? "Word" : "PowerPoint"
    implicitWidth: 76; implicitHeight: 48; padding: 7
    Accessible.role: Accessible.PageTab
    Accessible.name: "Chuyển đổi bài giảng " + text
    Accessible.selected: selected
    ToolTip.visible: hovered; ToolTip.delay: 350
    ToolTip.text: "Chuyển đổi " + text + " sang song ngữ"
    contentItem: Item {
        Row {
            anchors.centerIn: parent; spacing: 5
            Image {
                objectName: tab.objectName + "Logo"
                source: tab.word ? "../assets/actions/document-word.svg" : "../assets/actions/document-powerpoint.svg"
                width: 30; height: 34; sourceSize.width: 96; sourceSize.height: 108
                fillMode: Image.PreserveAspectFit; Accessible.ignored: true
            }
            Image {
                objectName: tab.objectName + "Conversion"
                width: 19; height: 22; anchors.verticalCenter: parent.verticalCenter
                source: "../assets/actions/conversion-arrows.svg"; sourceSize.width: 64; sourceSize.height: 64
                fillMode: Image.PreserveAspectFit
                Accessible.ignored: true
            }
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
