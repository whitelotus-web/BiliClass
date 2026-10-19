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
    objectName: choiceName + "Card"
    property var choiceGroup: null
    signal chosen()
    signal previewRequested()
    implicitHeight: compact ? (tight ? 64 : 78) : showPreview ? 138 : 90
    radius: 10
    color: selected ? "#f2f7ff" : "transparent"
    border.width: 1
    border.color: selected ? "#dce8f8" : "transparent"
    opacity: enabled ? 1 : .5
    HoverHandler { id: cardHover }
    ToolTip.visible: card.compact && cardHover.hovered
    ToolTip.delay: 600
    ToolTip.text: card.detail
    ColumnLayout {
        anchors.fill: parent; anchors.margins: card.compact ? 8 : 12; spacing: card.compact ? 3 : 5
        RowLayout {
          Layout.fillWidth: true; spacing: 6
        ChoiceRadioButton {
            id: radio; objectName: card.choiceName
            Layout.fillWidth: true
            checked: card.selected
            ButtonGroup.group: card.choiceGroup
            text: card.label
            onClicked: card.chosen()
            Accessible.name: card.label
            Accessible.description: card.detail
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
