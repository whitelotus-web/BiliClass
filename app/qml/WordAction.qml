import QtQuick
import QtQuick.Controls

Button {
    id: button
    property bool primary: false
    property bool danger: false
    implicitHeight: 40
    leftPadding: 15; rightPadding: 15
    font.pixelSize: 12; font.weight: Font.DemiBold
    contentItem: Label {
        text: button.text; font: button.font
        color: !button.enabled ? AppTheme.disabled : button.primary ? AppTheme.accentText : button.danger ? AppTheme.danger : AppTheme.blue
        horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    background: Rectangle {
        radius: 9
        color: !button.enabled ? AppTheme.disabledSurface : button.primary ? AppTheme.accent : button.hovered ? AppTheme.hover : AppTheme.surface
        border.color: button.visualFocus ? AppTheme.blue : button.primary ? AppTheme.accent : AppTheme.line
        border.width: button.visualFocus ? 2 : 1
    }
}
