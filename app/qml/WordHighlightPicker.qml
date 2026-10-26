import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: picker
    property string colorCode: "none"
    readonly property bool noColor: colorCode === "none"
    signal chosen()
    implicitWidth: 40; implicitHeight: 38
    Accessible.name: noColor ? "Tô sáng chữ: Không màu" : "Tô sáng chữ: #" + colorCode
    ToolTip.visible: hovered; ToolTip.text: Accessible.name
    function choose(code) { colorCode = code; colors.close(); chosen() }
    onClicked: {
        const point = picker.mapToItem(Overlay.overlay, 0, picker.height + 4)
        colors.x = Math.max(8, Math.min(point.x, colors.parent.width - colors.width - 8))
        colors.y = Math.max(8, Math.min(point.y, colors.parent.height - colors.height - 8))
        colors.open()
    }
    contentItem: Item {
        Item { width: 24; height: 24; anchors.centerIn: parent
            Text { x: 1; y: 0; text: "ab"; font.pixelSize: 11; color: AppTheme.ink }
            Canvas { x: 5; y: 1; width: 20; height: 20
                onPaint: {
                    const ctx = getContext("2d")
                    ctx.reset()
                    ctx.fillStyle = "#7c838c"
                    ctx.beginPath(); ctx.moveTo(4, 13); ctx.lineTo(12, 4); ctx.lineTo(17, 8); ctx.lineTo(9, 17); ctx.closePath(); ctx.fill()
                    ctx.fillStyle = "#40464f"
                    ctx.beginPath(); ctx.moveTo(4, 13); ctx.lineTo(9, 17); ctx.lineTo(3, 19); ctx.closePath(); ctx.fill()
                    ctx.strokeStyle = "#e4e8ed"; ctx.lineWidth = 1.2
                    ctx.beginPath(); ctx.moveTo(10, 6); ctx.lineTo(15, 10); ctx.stroke()
                }
            }
            Rectangle { x: 0; y: 20; width: 24; height: 4; radius: 1; color: picker.noColor ? "#FFFF00" : "#" + picker.colorCode }
        }
        Text { anchors.right: parent.right; anchors.bottom: parent.bottom; text: "⌄"; font.pixelSize: 10; color: AppTheme.muted }
    }
    background: Rectangle { radius: 5; color: picker.hovered || colors.visible || !picker.noColor ? AppTheme.selected : "transparent"; border.width: picker.visualFocus || colors.visible || !picker.noColor ? 1 : 0; border.color: AppTheme.blue }
    Popup {
        id: colors; objectName: "wordHighlightPalette"; parent: Overlay.overlay; width: 164; padding: 8
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle { radius: 8; color: AppTheme.surface; border.color: AppTheme.line }
        contentItem: ColumnLayout { spacing: 6
            GridLayout { columns: 5; columnSpacing: 4; rowSpacing: 4
                Repeater { model: ["FFFF00", "00FF00", "00FFFF", "FF00FF", "0000FF", "FF0000", "000080", "008080", "008000", "800080", "800000", "808000", "808080", "C0C0C0", "000000"]
                    Button { id: swatch; required property string modelData; objectName: "wordHighlight_" + modelData
                        implicitWidth: 26; implicitHeight: 26; padding: 2
                        Accessible.name: "Tô sáng #" + modelData
                        onClicked: picker.choose(modelData)
                        background: Rectangle { color: "#" + swatch.modelData; radius: 2; border.width: picker.colorCode === swatch.modelData || swatch.hovered ? 2 : 1; border.color: picker.colorCode === swatch.modelData || swatch.hovered ? AppTheme.blue : AppTheme.line }
                    }
                }
            }
            ItemDelegate { objectName: "wordHighlightNone"; text: "Không màu"; Layout.fillWidth: true; implicitHeight: 30
                highlighted: picker.noColor; onClicked: picker.choose("none")
                contentItem: Text { text: parent.text; color: AppTheme.ink; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 4; color: parent.hovered || parent.highlighted ? AppTheme.selected : "transparent" }
            }
        }
    }
}
