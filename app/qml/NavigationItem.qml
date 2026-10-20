import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property string iconName: "home"
    property bool selected: false
    implicitHeight: 48
    leftPadding: 14
    activeFocusOnTab: true
    Accessible.name: text
    background: Rectangle {
        radius: 10
        color: control.selected ? AppTheme.adapt("#eaf3ff") : control.down ? AppTheme.adapt("#e0edff") : control.hovered ? AppTheme.adapt("#f4f7fc") : "transparent"
        border.width: control.visualFocus ? 2 : 0
        border.color: AppTheme.adapt("#0869f9")
    }
    contentItem: RowLayout {
        spacing: 13
        NavigationIcon { name: control.iconName; active: control.selected; Layout.preferredWidth: 29; Layout.preferredHeight: 29 }
        Label { text: control.text; font.pixelSize: 14; font.weight: control.selected ? Font.DemiBold : Font.Normal; color: control.selected ? AppTheme.adapt("#0869f9") : AppTheme.adapt("#667997"); Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap }
    }
}
