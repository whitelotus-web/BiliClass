import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Button {
    id: picker
    property string colorCode: "original"
    property string recentColor: "1667B1"
    readonly property bool original: colorCode === "original"
    readonly property color inkColor: original ? AppTheme.ink : "#" + colorCode
    signal chosen()
    implicitHeight: 38
    implicitWidth: 74
    Accessible.name: original ? "Màu tiếng Anh: giữ nguyên màu gốc" : "Màu tiếng Anh: #" + colorCode
    ToolTip.visible: hovered; ToolTip.text: Accessible.name
    function choose(code) {
        colorCode = code
        if (code !== "original") recentColor = code
        colors.close()
        chosen()
    }
    onClicked: {
        const point = picker.mapToItem(Overlay.overlay, 0, picker.height + 4)
        colors.x = Math.max(8, Math.min(point.x, Overlay.overlay.width - colors.width - 8))
        colors.y = Math.max(8, Math.min(point.y, Overlay.overlay.height - colors.height - 8))
        colors.open()
    }
    contentItem: RowLayout { spacing: 8
        Item { implicitWidth: 24; implicitHeight: 26; Layout.alignment: Qt.AlignVCenter
            Text { id: colorLetter; text: "A"; font.family: "Georgia"; font.pixelSize: 22; font.bold: true; color: AppTheme.ink; anchors.horizontalCenter: parent.horizontalCenter }
            Rectangle { width: 24; height: 3; radius: 1; y: colorLetter.baselineOffset + 1; color: "#e53935" }
        }
        Text { text: "⌄"; color: AppTheme.muted; font.pixelSize: 16 }
    }
    background: Rectangle { radius: 7; color: picker.hovered || colors.visible || !picker.original ? AppTheme.selected : "transparent"; border.width: picker.activeFocus || colors.visible || !picker.original ? 1 : 0; border.color: AppTheme.blue }
    Popup {
        id: colors; objectName: "wordColorPalette"; parent: Overlay.overlay; width: 296; padding: 12
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle { color: AppTheme.surface; radius: 9; border.color: AppTheme.line }
        contentItem: ColumnLayout { spacing: 10
            CheckBox { objectName: "wordKeepOriginalColor"; text: "Giữ nguyên màu gốc"; checked: picker.original; palette.windowText: AppTheme.ink
                onClicked: picker.choose(checked ? "original" : picker.recentColor) }
            Rectangle { Layout.fillWidth: true; height: 1; color: AppTheme.line }
            Label { text: "Màu chủ đề"; color: AppTheme.ink; font.bold: true; font.pixelSize: 12 }
            GridLayout { columns: 10; columnSpacing: 3; rowSpacing: 3
                Repeater {
                    model: ["FFFFFF","000000","E7E6E6","44546A","4472C4","ED7D31","A5A5A5","FFC000","5B9BD5","70AD47",
                        "F2F2F2","7F7F7F","D0CECE","D6DCE4","D9E2F3","FBE4D5","EDEDED","FFF2CC","DDEBF7","E2EFD9",
                        "D9D9D9","595959","AEAAAA","ADB9CA","B4C6E7","F7CAAC","DBDBDB","FFE599","BDD7EE","C5E0B3",
                        "BFBFBF","3F3F3F","757171","8496B0","8EA9DB","F4B083","C9C9C9","FFD966","9DC3E6","A8D08D",
                        "A5A5A5","262626","3A3838","323E4F","2F5496","C55A11","7B7B7B","BF9000","2E75B5","538135",
                        "7F7F7F","0D0D0D","181717","222A35","203864","833C0B","525252","806000","1F4E78","375623"]
                    delegate: Swatch { required property string modelData; code: modelData }
                }
            }
            Label { text: "Màu tiêu chuẩn"; color: AppTheme.ink; font.bold: true; font.pixelSize: 12 }
            Row { spacing: 3
                Repeater { model: ["C00000","FF0000","FFC000","FFFF00","92D050","00B050","00B0F0","0070C0","002060","7030A0"]
                    delegate: Swatch { required property string modelData; code: modelData }
                }
            }
            Button { objectName: "wordMoreColors"; text: "Màu khác…"; flat: true; palette.buttonText: AppTheme.blue; onClicked: { colors.close(); custom.selectedColor = picker.original ? "#1667B1" : picker.inkColor; custom.open() } }
        }
    }
    component Swatch: Button {
        id: swatch; required property string code
        objectName: "wordColor_" + code
        implicitWidth: 24; implicitHeight: 24; padding: 0
        Accessible.name: "Chọn màu #" + code
        ToolTip.visible: hovered; ToolTip.text: "#" + code
        onClicked: picker.choose(code)
        background: Rectangle { radius: 1; color: "#" + swatch.code; border.width: swatch.hovered || picker.colorCode === swatch.code || swatch.visualFocus ? 2 : 1; border.color: swatch.hovered || picker.colorCode === swatch.code || swatch.visualFocus ? AppTheme.blue : "#b4bcc8" }
        contentItem: Item { }
    }
    ColorDialog { id: custom; title: "Màu chữ tiếng Anh"; selectedColor: "#1667B1"; onAccepted: picker.choose(selectedColor.toString().replace("#", "").toUpperCase()) }
}
