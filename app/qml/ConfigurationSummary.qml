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
        Item {
            id: values; objectName: card.objectName + "Values"
            width: parent.width; implicitHeight: arrangement.height
            property int revision: 0
            // Each wrapped row is centered independently; the heading stays left.
            property var arrangement: {
                let generation = revision
                let row = [], used = 0, rowHeight = 0, y = 0, positions = []
                function finishRow() {
                    let x = Math.max(0, (width - used) / 2)
                    for (let entry of row) {
                        positions[entry.index] = {x: x, y: y}
                        x += entry.width + 6
                    }
                    y += rowHeight + 6
                    row = []; used = 0; rowHeight = 0
                }
                for (let i = 0; i < badges.count; ++i) {
                    let badge = badges.itemAt(i)
                    if (!badge) continue
                    let w = Math.min(width, badge.implicitWidth)
                    if (row.length && used + 6 + w > width) finishRow()
                    used += (row.length ? 6 : 0) + w
                    row.push({index: i, width: w})
                    rowHeight = Math.max(rowHeight, badge.height)
                }
                if (row.length) finishRow()
                return {positions: positions, height: Math.max(0, y - 6)}
            }
            Repeater {
                id: badges
                model: card.entries
                onItemAdded: values.revision++
                onItemRemoved: values.revision++
                Rectangle {
                    required property var modelData
                    required property int index
                    objectName: card.objectName + "_" + modelData.key
                    implicitWidth: value.implicitWidth + 16
                    width: Math.min(values.width, implicitWidth)
                    x: (values.arrangement.positions[index] || {}).x || 0
                    y: (values.arrangement.positions[index] || {}).y || 0
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
