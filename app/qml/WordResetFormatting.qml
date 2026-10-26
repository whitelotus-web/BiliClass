import QtQuick
import QtQuick.Controls

ToolButton {
    id: control
    implicitWidth: 30; implicitHeight: 28; padding: 2
    Accessible.name: "Đặt lại định dạng"
    Accessible.description: "Màu xanh, in nghiêng, không tô sáng, Font gốc và Size gốc."
    ToolTip.visible: hovered; ToolTip.text: "Đặt lại định dạng"
    contentItem: Item {
        Text { x: 1; anchors.verticalCenter: parent.verticalCenter; text: "A"; font.pixelSize: 18; font.bold: true; color: AppTheme.ink }
        Rectangle { x: 12; y: 9; width: 13; height: 7; radius: 1; rotation: -45; color: "#ed8aa7"; border.color: "#a65b72"
            Rectangle { anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom; width: 4; color: "#f3f5f8"; radius: 1 }
        }
    }
    background: Rectangle { radius: 4; color: control.hovered ? AppTheme.selected : "transparent"; border.width: control.visualFocus ? 1 : 0; border.color: AppTheme.blue }
}
