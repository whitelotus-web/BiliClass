import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property bool primary: false
    property string iconName: ""
    implicitHeight: 38
    leftPadding: 14; rightPadding: 14
    font.pixelSize: 12; font.weight: Font.DemiBold
    contentItem: RowLayout {
        spacing: 6
        Item { Layout.fillWidth: true }
        Image { visible: !!control.iconName; source: control.iconName ? "../assets/actions/" + control.iconName + ".png" : ""; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 22; Layout.preferredHeight: 22; opacity: control.enabled ? 1 : .4 }
        Text { text: control.text; font: control.font; color: !control.enabled ? "#96a6bc" : control.primary ? "white" : "#0869f9"; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        Item { Layout.fillWidth: true }
    }
    background: Rectangle { radius: 8; color: !control.enabled ? "#edf1f7" : control.primary ? (control.down ? "#0055d8" : "#0869f9") : control.hovered ? "#eaf3ff" : "white"; border.color: control.primary ? "transparent" : "#cbdcf4"; border.width: control.visualFocus ? 2 : 1 }
}
