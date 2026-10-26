import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Control {
    id: control
    property real pointSize: 0
    property string sourceSize: ""
    property alias editText: input.text
    property string error: ""
    property bool dirty: false
    readonly property var commonSizes: ["Size gốc", "8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"]
    signal chosen()
    implicitWidth: 82; implicitHeight: 38; padding: 2; hoverEnabled: true
    Accessible.name: "Cỡ chữ tiếng Anh"
    Accessible.description: error
    ToolTip.visible: hovered
    ToolTip.text: "Size"
    function refresh() {
        input.text = pointSize > 0 ? pointSize.toString() : "Size gốc"
        dirty = false
    }
    function commit(value) {
        const text = value.trim()
        const original = text === "Size gốc" || text === "Cỡ gốc"
        const size = original ? 0 : Number(text.replace(",", "."))
        if (original || text && isFinite(size) && size >= 1 && size <= 1638 && Math.round(size * 2) === size * 2) {
            pointSize = size
            error = ""
            refresh()
            chosen()
        } else {
            error = "Nhập cỡ từ 1 đến 1638 pt, theo bước 0,5 pt."
            refresh()
        }
    }
    function openSizes() {
        const below = control.mapToItem(Overlay.overlay, 0, control.height + 4)
        const above = control.mapToItem(Overlay.overlay, 0, 0)
        sizes.x = Math.max(8, Math.min(below.x, sizes.parent.width - sizes.width - 8))
        sizes.y = Math.max(8, Math.min(below.y + sizes.height <= sizes.parent.height - 8 ? below.y : above.y - sizes.height - 4, sizes.parent.height - sizes.height - 8))
        sizes.open()
    }
    Component.onCompleted: refresh()
    onPointSizeChanged: if (!input.activeFocus) refresh()
    onSourceSizeChanged: if (pointSize === 0 && !input.activeFocus) refresh()
    background: Rectangle { radius: 7; color: AppTheme.field; border.color: input.activeFocus || sizes.visible ? AppTheme.blue : AppTheme.line }
    contentItem: RowLayout { spacing: 0
        TextField {
            id: input; objectName: "wordFontSizeInput"; Layout.fillWidth: true; Layout.minimumWidth: 0; Layout.fillHeight: true
            leftPadding: 4; rightPadding: 0; topPadding: 0; bottomPadding: 0
            font.pixelSize: 12; color: AppTheme.ink; placeholderText: "Size gốc"; selectByMouse: true
            Accessible.name: "Nhập cỡ chữ tiếng Anh"
            background: Item { }
            onTextEdited: control.dirty = true
            onAccepted: { if (control.dirty) control.commit(text) }
            onEditingFinished: { if (control.dirty) control.commit(text); else if (!activeFocus) control.refresh() }
            Keys.onDownPressed: control.openSizes()
        }
        ToolButton { objectName: "wordFontSizeArrow"; text: "⌄"; Layout.preferredWidth: 16; Layout.fillHeight: true; padding: 0
            Accessible.name: "Danh sách cỡ chữ"
            contentItem: Text { text: parent.text; color: AppTheme.muted; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14 }
            background: Item { }
            onClicked: control.openSizes()
        }
    }
    Popup {
        id: sizes; objectName: "wordFontSizePopup"; parent: Overlay.overlay; width: 104; padding: 4; focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        height: Math.min(360, parent.height - 16)
        background: Rectangle { color: AppTheme.surface; radius: 7; border.color: AppTheme.line }
        onOpened: { sizeList.currentIndex = Math.max(0, control.commonSizes.indexOf(control.pointSize > 0 ? control.pointSize.toString() : "Size gốc")); sizeList.forceActiveFocus() }
        contentItem: ListView {
            id: sizeList; objectName: "wordFontSizeList"; clip: true; implicitHeight: contentHeight; model: control.commonSizes; keyNavigationEnabled: true
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            Keys.onReturnPressed: { control.commit(control.commonSizes[currentIndex]); sizes.close() }
            delegate: ItemDelegate {
                required property string modelData; required property int index
                width: 96; height: 30; text: modelData; highlighted: sizeList.currentIndex === index
                contentItem: Text { text: parent.text; color: AppTheme.ink; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 4; color: parent.highlighted || parent.hovered ? AppTheme.selected : "transparent" }
                onClicked: { control.commit(modelData); sizes.close() }
            }
        }
    }
}
