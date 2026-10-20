import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property bool primary: false
    property bool danger: false
    property string symbol: ""
    property string iconName: ""
    property int iconSize: 22
    property bool externalHovered: false
    property bool inactiveStatus: false
    readonly property bool pointerHovered: hovered || externalHovered
    implicitHeight: 38
    leftPadding: 14; rightPadding: 14
    font.pixelSize: 12; font.weight: Font.DemiBold
    contentItem: RowLayout {
        spacing: 6
        Item { Layout.fillWidth: true }
        ThemedImage { darkTint: !control.enabled ? (control.inactiveStatus ? AppTheme.muted : AppTheme.disabled) : control.primary ? AppTheme.accentText : control.danger ? AppTheme.danger : AppTheme.blue; visible: !!control.iconName; source: control.iconName ? "../assets/actions/" + control.iconName + (control.iconName === "presentation" ? (control.primary ? "-white.svg" : ".svg") : control.iconName === "speaker" ? ".svg" : ".png") : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: control.iconSize; Layout.preferredHeight: control.iconSize; opacity: control.enabled || AppTheme.dark ? 1 : .4 }
        Text { visible: !!control.symbol; text: control.symbol; font: control.font; color: control.enabled ? (control.danger ? AppTheme.adapt("#c92d37") : AppTheme.adapt("#0869f9")) : AppTheme.adapt("#96a6bc") }
        Text { objectName: "actionButtonLabel"; text: control.text; font: control.font; color: !control.enabled ? (control.inactiveStatus ? AppTheme.muted : AppTheme.disabled) : control.primary ? AppTheme.accentText : control.danger ? AppTheme.adapt("#c92d37") : AppTheme.adapt("#0869f9"); verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight; Layout.minimumWidth: 0; Layout.maximumWidth: Math.max(0, control.availableWidth - (control.iconName ? control.iconSize + 6 : 0) - (control.symbol ? 18 : 0)) }
        Item { Layout.fillWidth: true }
    }
    background: Rectangle { radius: 8; color: !control.enabled ? AppTheme.adapt("#edf1f7") : control.primary ? (control.down ? AppTheme.adapt("#0055d8") : AppTheme.accent) : control.danger ? (control.pointerHovered ? AppTheme.adapt("#ffe4e7") : AppTheme.adapt("#fff6f7")) : control.pointerHovered ? AppTheme.adapt("#eaf3ff") : AppTheme.surface; border.color: control.primary ? "transparent" : control.danger ? AppTheme.adapt("#f1b8be") : AppTheme.adapt("#cbdcf4"); border.width: control.visualFocus ? 2 : 1 }
}
