import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property string label: ""
    property string detail: ""
    property bool selected: false
    property bool showPreview: false
    property bool compact: false
    property bool tight: false
    property string choiceName: ""
    property var choiceGroup: null
    signal chosen()
    signal previewRequested()
    implicitHeight: compact ? (tight ? 64 : 78) : showPreview ? 138 : 90
    radius: 10
    color: selected ? "#edf5ff" : "#ffffff"
    border.width: selected ? 2 : 1
    border.color: selected ? "#0869f9" : "#dce6f3"
    opacity: enabled ? 1 : .5
    HoverHandler { id: cardHover }
    ToolTip.visible: card.compact && cardHover.hovered
    ToolTip.delay: 600
    ToolTip.text: card.detail
    ColumnLayout {
        anchors.fill: parent; anchors.margins: card.compact ? 8 : 12; spacing: card.compact ? 3 : 5
        RowLayout {
          Layout.fillWidth: true; spacing: 6
        RadioButton {
            id: radio; objectName: card.choiceName
            Layout.fillWidth: true
            checked: card.selected
            ButtonGroup.group: card.choiceGroup
            text: card.label
            onClicked: card.chosen()
            Accessible.name: card.label
            Accessible.description: card.detail
            indicator: Rectangle {
                x: 0; y: (radio.height - height) / 2
                width: 18; height: 18; radius: 9
                color: "white"; border.width: radio.visualFocus ? 2 : 1
                border.color: radio.checked ? "#0869f9" : "#8c9eb8"
                Rectangle { anchors.centerIn: parent; width: 10; height: 10; radius: 5; color: "#0869f9"; visible: radio.checked }
            }
            contentItem: Text {
                leftPadding: 25
                text: radio.text; color: "#112650"; font.pixelSize: 13; font.weight: Font.DemiBold
                wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter
            }
        }
          ActionButton { objectName: card.compact ? card.choiceName + "Preview" : ""; visible: card.showPreview && card.compact; text: "Xem mẫu"; implicitHeight: 26; font.pixelSize: 11; onClicked: card.previewRequested() }
        }
        Label { text: card.detail; Layout.fillWidth: true; Layout.fillHeight: true; color: "#667997"; font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText; maximumLineCount: card.compact ? (card.tight ? 1 : 2) : 2147483647; elide: card.compact ? Text.ElideRight : Text.ElideNone }
        ActionButton {
            objectName: card.compact ? "" : card.choiceName + "Preview"
            visible: card.showPreview && !card.compact; text: "Xem mẫu bố cục"; iconName: "view"
            implicitHeight: 29; font.pixelSize: 11
            onClicked: card.previewRequested()
        }
    }
}
