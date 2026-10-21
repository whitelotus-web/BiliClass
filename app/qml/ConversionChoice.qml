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
    implicitHeight: Math.max(fitContent ? 78 : compact ? (tight ? 64 : 78) : 90,
                             choiceContent.implicitHeight + (compact ? 16 : 24))
    radius: 10
    color: selected ? AppTheme.adapt("#f2f7ff") : "transparent"
    border.width: 1
    border.color: selected ? AppTheme.adapt("#dce8f8") : AppTheme.line
    opacity: enabled ? 1 : .5
    HoverHandler { id: cardHover }
    ToolTip.visible: card.compact && cardHover.hovered
    ToolTip.delay: 600
    ToolTip.text: card.detail
    // Behind the content: the preview button keeps its own action, while
    // descriptions and padding select the same option as the radio button.
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            radio.forceActiveFocus(Qt.MouseFocusReason)
            card.chosen()
        }
    }
    ColumnLayout {
        id: choiceContent
        anchors.fill: parent; anchors.margins: card.compact ? 8 : 12; spacing: card.compact ? 3 : 5
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
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Label { objectName: card.choiceName + "Detail"; text: card.detail; Layout.fillWidth: true; Layout.minimumWidth: 0; color: AppTheme.adapt("#667997"); font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText; maximumLineCount: card.compact ? (card.tight ? 1 : 2) : 2147483647; elide: card.compact ? Text.ElideRight : Text.ElideNone }
            PreviewButton {
                objectName: card.choiceName + "Preview"
                visible: card.showPreview; Layout.alignment: Qt.AlignVCenter
                onClicked: card.previewRequested()
            }
        }
    }
}
