import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var settings
    Layout.fillWidth: true
    spacing: 12
    property var draft: Object.assign({}, settings.state.bindings)
    property string capturing: ""
    property string feedback: ""
    property bool invalid: false
    readonly property bool dirty: JSON.stringify(draft) !== JSON.stringify(settings.state.bindings)

    function capture(key, modifiers, repeated) {
        if (!capturing || repeated) return
        if (key === Qt.Key_Escape) { capturing = ""; feedback = "Đã hủy gán phím."; invalid = false; return }
        if ([Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta, Qt.Key_AltGr].indexOf(key) >= 0) return
        let base = key === Qt.Key_Space ? "Space" : key === Qt.Key_Return || key === Qt.Key_Enter ? "Enter" :
            key >= Qt.Key_A && key <= Qt.Key_Z || key >= Qt.Key_0 && key <= Qt.Key_9 ? String.fromCharCode(key) :
            key >= Qt.Key_F1 && key <= Qt.Key_F12 && key !== Qt.Key_F5 ? "F" + (key - Qt.Key_F1 + 1) : ""
        let mods = []
        if (modifiers & Qt.ControlModifier) mods.push("Ctrl")
        if (modifiers & Qt.AltModifier) mods.push("Alt")
        if (modifiers & Qt.ShiftModifier) mods.push("Shift")
        if (!base || modifiers & Qt.MetaModifier || mods.length !== (capturing === "both" ? 1 : 0)) {
            feedback = capturing === "both" ? "Nhấn đúng hai phím: Ctrl/Alt/Shift cùng chữ, số, Cách, Enter hoặc F1–F12 (trừ F5)." : "Nhấn một phím: chữ, số, Cách, Enter hoặc F1–F12 (trừ F5). Phím mũi tên giữ để chuyển hiệu ứng/slide."
            invalid = true; return
        }
        let value = mods.concat([base]).join("+")
        let next = Object.assign({}, draft)
        next[capturing] = value
        draft = next
        capturing = ""; feedback = "Bấm Lưu phím đọc để áp dụng."; invalid = false
    }

    Label { text: "Phím đọc khi trình chiếu"; color: "#102e54"; font.pixelSize: 17; font.bold: true }
    Label {
        text: "Bấm để phát → bấm lại để tạm dừng → bấm tiếp để đọc tiếp. Chỉ áp dụng trong cửa sổ trình chiếu bài đang gắn với BiliClass."
        Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#667997"; font.pixelSize: 12
    }
    Repeater {
        model: [{language: "en", label: "Đọc tiếng Anh", detail: "Một phím"}, {language: "vi", label: "Đọc tiếng Việt", detail: "Một phím"}, {language: "both", label: "Đọc hai ngôn ngữ", detail: "Hai phím cùng lúc"}]
        RowLayout {
            required property var modelData
            Layout.fillWidth: true; spacing: 12
            ColumnLayout {
                Layout.preferredWidth: 160; spacing: 3
                Label { text: modelData.label; color: "#102e54"; font.bold: true }
                Label { text: modelData.detail; color: "#667997"; font.pixelSize: 11 }
            }
            Button {
                id: bindingButton
                objectName: "shortcutBind" + modelData.language
                text: panel.capturing === modelData.language ? "Nhấn phím… (Esc hủy)" : panel.draft[modelData.language].replace("Space", "Cách") + "   ·   Đổi phím"
                Layout.preferredWidth: 220; implicitHeight: 40
                background: Rectangle { radius: 8; color: panel.capturing === modelData.language ? "#eaf3ff" : bindingButton.hovered ? "#f4f8ff" : "white"; border.color: bindingButton.activeFocus || panel.capturing === modelData.language ? "#0869f9" : "#cbdcf4"; border.width: bindingButton.visualFocus ? 2 : 1 }
                contentItem: Label { text: bindingButton.text; color: "#0869f9"; font.pixelSize: 12; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: { panel.capturing = modelData.language; panel.feedback = "Nhấn phím muốn gán; Esc để hủy."; panel.invalid = false; forceActiveFocus() }
                onActiveFocusChanged: if (!activeFocus && panel.capturing === modelData.language) panel.capturing = ""
                Keys.priority: Keys.BeforeItem
                Keys.onShortcutOverride: function(event) { if (panel.capturing === modelData.language) event.accepted = true }
                Keys.onPressed: function(event) { if (panel.capturing === modelData.language) { event.accepted = true; panel.capture(event.key, event.modifiers, event.isAutoRepeat) } }
                Keys.onReleased: function(event) { if (activeFocus) event.accepted = true }
            }
            Item { Layout.fillWidth: true }
        }
    }
    Label { text: "← / →: lùi / tiến hiệu ứng; hết hiệu ứng thì chuyển slide. ↑ / ↓: tăng / giảm âm lượng lời đọc (5% mỗi lần). Esc: thoát trình chiếu. Dừng đọc ■: dừng hẳn. Phím đọc chưa có giọng chỉ báo nhắc, không chuyển slide."; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12; color: "#667997" }
    Label {
        objectName: "shortcutFeedback"; visible: !!text
        text: panel.feedback || panel.settings.state.message
        color: panel.invalid || panel.settings.state.error ? "#b42d38" : "#168567"
        Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: 12
    }
    RowLayout {
        Layout.fillWidth: true
        ActionButton { objectName: "resetMascotShortcuts"; text: "Khôi phục phím mặc định"; onClicked: { panel.capturing = ""; panel.settings.reset(); panel.draft = Object.assign({}, panel.settings.state.bindings); panel.feedback = "" } }
        Item { Layout.fillWidth: true }
        ActionButton { objectName: "saveMascotShortcuts"; text: "Lưu phím đọc"; primary: true; enabled: panel.dirty && !panel.capturing; onClicked: { if (panel.settings.save(panel.draft)) panel.draft = Object.assign({}, panel.settings.state.bindings); panel.feedback = ""; panel.invalid = false } }
    }
}
