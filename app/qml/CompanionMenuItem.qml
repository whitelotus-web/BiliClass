import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

MenuItem {
    id: item
    required property string iconName
    icon.source: "../assets/mascot-controls/" + iconName + ".svg"
    icon.color: "transparent"
    leftPadding: 12; rightPadding: 12; topPadding: 8; bottomPadding: 8
    contentItem: RowLayout {
        spacing: 10
        CompanionIcon { iconName: item.iconName; Layout.preferredWidth: 21; Layout.preferredHeight: 21 }
        Label { text: item.text; font: item.font; color: "#112650"; Layout.fillWidth: true }
    }
    background: Rectangle { radius: 6; color: item.down ? "#d8e9ff" : item.highlighted ? "#eaf2ff" : "transparent" }
}
