import QtQuick
import QtQuick.Controls

Rectangle {
    id: card
    property var entries: []
    radius: 9; color: AppTheme.adapt("#f5f8fd"); border.color: AppTheme.line
    implicitHeight: content.implicitHeight + 20
    Column {
        id: content
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
        anchors.margins: 10; spacing: 6
        Label { text: "Cấu hình đã chọn"; color: AppTheme.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
        Flow {
            id: values; objectName: card.objectName + "Values"
            width: parent.width; spacing: 6
            Repeater {
                model: card.entries
                Rectangle {
                    required property var modelData
                    objectName: card.objectName + "_" + modelData.key
                    width: Math.min(values.width, value.implicitWidth + 16)
                    height: value.implicitHeight + 8; radius: 5
                    color: modelData.emphasis ? AppTheme.selected : AppTheme.raised
                    Label {
                        id: value; x: 8; y: 4; width: parent.width - 16
                        text: modelData.text; textFormat: Text.PlainText; wrapMode: Text.WordWrap
                        color: modelData.emphasis ? AppTheme.blue : AppTheme.ink
                        font.pixelSize: 12; font.weight: modelData.emphasis ? Font.DemiBold : Font.Normal
                    }
                }
            }
        }
    }
}
