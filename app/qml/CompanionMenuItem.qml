import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

MenuItem {
    id: item
    required property string iconName
    icon.source: "../assets/mascot-controls/" + iconName + ".svg"
    icon.color: "transparent"
    implicitWidth: leftPadding + contentItem.implicitWidth + rightPadding
    implicitHeight: Math.max(32, topPadding + contentItem.implicitHeight + bottomPadding)
    leftPadding: 10; rightPadding: 10; topPadding: 6; bottomPadding: 6
    contentItem: RowLayout {
        spacing: 8
        CompanionIcon { iconName: item.iconName; Layout.preferredWidth: 18; Layout.preferredHeight: 18 }
        Label { text: item.text; font: item.font; color: AppTheme.adapt("#112650"); Layout.fillWidth: true }
    }
    background: Rectangle { radius: 6; color: item.down ? AppTheme.adapt("#d8e9ff") : item.highlighted ? AppTheme.adapt("#eaf2ff") : "transparent" }
}
