import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property string label: ""
    property string detail: ""
    property bool selected: false
    property bool showPreview: false
    property string choiceName: ""
    property var choiceGroup: null
    signal chosen()
    signal previewRequested()
    implicitHeight: showPreview ? 138 : 90
    radius: 10
    color: selected ? "#edf5ff" : "#ffffff"
    border.width: selected ? 2 : 1
    border.color: selected ? "#0869f9" : "#dce6f3"
    opacity: enabled ? 1 : .5
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 12; spacing: 5
        RadioButton {
            id: radio; objectName: card.choiceName
            Layout.fillWidth: true
            checked: card.selected
            ButtonGroup.group: card.choiceGroup
            text: card.label
            onClicked: card.chosen()
            Accessible.name: card.label
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
        Label { text: card.detail; Layout.fillWidth: true; Layout.fillHeight: true; color: "#667997"; font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
        ActionButton {
            objectName: card.choiceName + "Preview"
            visible: card.showPreview; text: "Xem mẫu bố cục"; iconName: "view"
            implicitHeight: 29; font.pixelSize: 11
            onClicked: card.previewRequested()
        }
    }
}
