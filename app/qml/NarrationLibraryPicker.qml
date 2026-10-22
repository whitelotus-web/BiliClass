import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: picker
    property var model: []
    property var selectedIds: []
    readonly property int count: model.length
    readonly property int selectedCount: selectedIds.length
    implicitHeight: trigger.implicitHeight
    onEnabledChanged: if (!enabled) choices.close()
    onModelChanged: {
        const ids = model.map(function(row) { return row.id })
        selectedIds = selectedIds.filter(function(id) { return ids.indexOf(id) >= 0 })
    }
    function toggle(identity) {
        const next = selectedIds.slice()
        const index = next.indexOf(identity)
        if (index >= 0) next.splice(index, 1)
        else if (next.length < 100) next.push(identity)
        selectedIds = next
    }
    function closePopup() { choices.close() }
    ActionButton {
        id: trigger
        objectName: "voiceLibraryPickerButton"
        width: parent.width
        text: picker.selectedCount ? "Đã chọn " + picker.selectedCount + " bài trong thư viện" : "Chọn bài trong thư viện…"
        enabled: picker.count > 0
        onClicked: choices.opened ? choices.close() : choices.open()
        Accessible.description: "Tích chọn một hoặc nhiều bài để tạo giọng đọc lần lượt."
        contentItem: RowLayout {
            Label { text: trigger.text; elide: Text.ElideRight; color: trigger.enabled ? AppTheme.ink : AppTheme.disabled; font: trigger.font; Layout.fillWidth: true; Layout.minimumWidth: 0 }
            Label { text: choices.opened ? "▴" : "▾"; color: AppTheme.muted }
        }
    }
    Popup {
        id: choices
        objectName: "voiceLibraryPickerPopup"
        y: trigger.height + 4; width: picker.width; padding: 10; margins: 12
        implicitHeight: content.implicitHeight + 20
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle { radius: 10; color: AppTheme.surface; border.color: AppTheme.line }
        contentItem: ColumnLayout {
            id: content
            spacing: 8
            RowLayout {
                Layout.fillWidth: true
                Label { text: picker.selectedCount + " bài đã chọn"; color: AppTheme.ink; font.pixelSize: 12; Layout.fillWidth: true }
                ActionButton { objectName: "voiceLibrarySelectAll"; text: "Chọn tất cả"; implicitHeight: 30; onClicked: picker.selectedIds = picker.model.slice(0, 100).map(function(row) { return row.id }) }
                ActionButton { objectName: "voiceLibraryClearSelection"; text: "Bỏ chọn"; implicitHeight: 30; enabled: picker.selectedCount > 0; onClicked: picker.selectedIds = [] }
            }
            ListView {
                id: rows
                objectName: "voiceLibraryPickerRows"
                Layout.fillWidth: true; Layout.preferredHeight: Math.min(240, count * 44)
                clip: true; model: picker.model; boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar {}
                delegate: CheckDelegate {
                    id: choice
                    required property var modelData
                    width: rows.width; height: 44; leftPadding: 34; rightPadding: 14
                    objectName: "voiceLibraryChoice_" + modelData.id
                    checked: picker.selectedIds.indexOf(modelData.id) >= 0
                    enabled: checked || picker.selectedCount < 100
                    onClicked: picker.toggle(modelData.id)
                    text: modelData.title
                    Accessible.name: text
                    background: Rectangle { radius: 6; color: choice.checked ? AppTheme.selected : choice.hovered ? AppTheme.hover : "transparent"; border.color: choice.visualFocus ? AppTheme.blue : "transparent" }
                    indicator: Rectangle {
                        x: 8; y: (choice.height - height) / 2; width: 16; height: 16; radius: 3
                        color: choice.checked ? AppTheme.accent : "transparent"
                        border.color: choice.checked ? AppTheme.accent : AppTheme.muted
                        Label { anchors.centerIn: parent; text: "✓"; visible: choice.checked; color: AppTheme.accentText; font.pixelSize: 13 }
                    }
                    contentItem: Label { text: choice.text; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter; color: AppTheme.ink; font.pixelSize: 12 }
                    ToolTip.visible: hovered; ToolTip.delay: 600; ToolTip.text: text
                }
            }
            Label { visible: picker.count > 100; text: "Tối đa 100 bài mỗi lượt."; color: AppTheme.muted; font.pixelSize: 12 }
            ActionButton { objectName: "voiceLibraryPickerDone"; text: "Xong"; Layout.alignment: Qt.AlignRight; implicitHeight: 30; onClicked: choices.close() }
        }
    }
}
