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
    property bool fitContent: false
    property string choiceName: ""
    objectName: choiceName + "Card"
    property var choiceGroup: null
    signal chosen()
    signal previewRequested()
    implicitHeight: fitContent ? Math.max(78, choiceContent.implicitHeight + 24) : compact ? (tight ? (showPreview ? 66 : 64) : 78) : showPreview ? 138 : 90
    radius: 10
    color: selected ? AppTheme.adapt("#f2f7ff") : "transparent"
    border.width: 1
    border.color: selected ? AppTheme.adapt("#dce8f8") : AppTheme.line
    opacity: enabled ? 1 : .5
    HoverHandler { id: cardHover }
    ToolTip.visible: card.compact && cardHover.hovered
    ToolTip.delay: 600
    ToolTip.text: card.detail
    ColumnLayout {
        id: choiceContent
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
          PreviewButton { objectName: card.compact ? card.choiceName + "Preview" : ""; visible: card.showPreview && card.compact; onClicked: card.previewRequested() }
        }
        Label { objectName: card.choiceName + "Detail"; text: card.detail; Layout.fillWidth: true; Layout.fillHeight: true; color: AppTheme.adapt("#667997"); font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText; maximumLineCount: card.compact ? (card.tight ? 1 : 2) : 2147483647; elide: card.compact ? Text.ElideRight : Text.ElideNone }
        PreviewButton {
            objectName: card.compact ? "" : card.choiceName + "Preview"
            visible: card.showPreview && !card.compact; Layout.alignment: Qt.AlignRight
            onClicked: card.previewRequested()
        }
    }
}
