import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: styles; spacing: 2
    property bool compact: false
    property bool bold: false
    property bool italic: true
    property bool underline: false
    property bool strike: false
    property string script: "normal"
    readonly property string description: {
        let values = []
        if (bold) values.push("Đậm")
        if (italic) values.push("Nghiêng")
        if (underline) values.push("Gạch chân")
        if (strike) values.push("Gạch ngang")
        if (script !== "normal") values.push(script === "subscript" ? "Chỉ số dưới" : "Số mũ")
        return values.join(" · ") || "Bình thường"
    }
    signal chosen()
    implicitHeight: 38
    component StyleButton: Button {
        implicitWidth: styles.compact ? 26 : 31; implicitHeight: 28; padding: 2
        Layout.preferredHeight: 28; Layout.maximumHeight: 28; Layout.alignment: Qt.AlignVCenter
        property string hint: ""
        Accessible.name: hint
        ToolTip.visible: hovered; ToolTip.text: hint
        background: Rectangle { radius: 4; color: parent.checked || parent.hovered ? AppTheme.selected : "transparent"; border.width: parent.checked || parent.visualFocus ? 1 : 0; border.color: AppTheme.blue }
        contentItem: Text { text: parent.text; color: AppTheme.ink; font: parent.font; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
    }
    StyleButton { objectName: "wordStyleBold"; text: "B"; font.bold: true; font.pixelSize: 16; checked: styles.bold; hint: "In đậm"; onClicked: { styles.bold = !styles.bold; styles.chosen() } }
    StyleButton { objectName: "wordStyleItalic"; text: "I"; font.italic: true; font.family: "Georgia"; font.pixelSize: 17; checked: styles.italic; hint: "In nghiêng"; onClicked: { styles.italic = !styles.italic; styles.chosen() } }
    StyleButton { objectName: "wordStyleUnderline"; text: "U"; font.underline: true; font.pixelSize: 15; checked: styles.underline; hint: "Gạch chân"; onClicked: { styles.underline = !styles.underline; styles.chosen() } }
    StyleButton { objectName: "wordStyleStrike"; text: "abc"; font.strikeout: true; font.pixelSize: styles.compact ? 11 : 12; checked: styles.strike; hint: "Gạch ngang"; onClicked: { styles.strike = !styles.strike; styles.chosen() } }
}
