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
    readonly property bool pointerHovered: hovered || externalHovered
    implicitHeight: 38
    leftPadding: 14; rightPadding: 14
    font.pixelSize: 12; font.weight: Font.DemiBold
    contentItem: RowLayout {
        spacing: 6
        Item { Layout.fillWidth: true }
        Image { visible: !!control.iconName; source: control.iconName ? "../assets/actions/" + control.iconName + (control.iconName === "presentation" ? (control.primary ? "-white.svg" : ".svg") : ".png") : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: control.iconSize; Layout.preferredHeight: control.iconSize; opacity: control.enabled ? 1 : .4 }
        Text { visible: !!control.symbol; text: control.symbol; font: control.font; color: control.enabled ? (control.danger ? "#c92d37" : "#0869f9") : "#96a6bc" }
        Text { text: control.text; font: control.font; color: !control.enabled ? "#96a6bc" : control.primary ? "white" : control.danger ? "#c92d37" : "#0869f9"; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        Item { Layout.fillWidth: true }
    }
    background: Rectangle { radius: 8; color: !control.enabled ? "#edf1f7" : control.primary ? (control.down ? "#0055d8" : "#0869f9") : control.danger ? (control.pointerHovered ? "#ffe4e7" : "#fff6f7") : control.pointerHovered ? "#eaf3ff" : "white"; border.color: control.primary ? "transparent" : control.danger ? "#f1b8be" : "#cbdcf4"; border.width: control.visualFocus ? 2 : 1 }
}
