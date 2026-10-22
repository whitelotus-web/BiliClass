import QtQuick
import QtQuick.Controls

Button {
    id: status
    property bool returnable: false
    property string returnLabel: "Quay lại tác vụ đang chạy"
    signal returnRequested()
    enabled: returnable
    focusPolicy: returnable ? Qt.TabFocus : Qt.NoFocus
    implicitWidth: contentItem.implicitWidth + leftPadding + rightPadding
    implicitHeight: Math.max(23, contentItem.implicitHeight + topPadding + bottomPadding)
    leftPadding: returnable ? 8 : 0; rightPadding: leftPadding
    topPadding: 2; bottomPadding: 2
    font.pixelSize: 11
    Accessible.role: returnable ? Accessible.Button : Accessible.StaticText
    Accessible.name: text
    Accessible.description: returnable ? returnLabel : ""
    onClicked: returnRequested()
    ToolTip.visible: returnable && hovered
    ToolTip.delay: 400
    ToolTip.text: returnLabel
    contentItem: Label {
        text: status.text; font: status.font; textFormat: Text.PlainText
        color: status.returnable ? AppTheme.blue : AppTheme.muted
        wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: 6
        color: !status.returnable ? "transparent" : status.down || status.hovered ? AppTheme.hover : AppTheme.surface
        border.color: status.returnable ? (status.visualFocus ? AppTheme.blue : AppTheme.line) : "transparent"
        border.width: status.visualFocus ? 2 : 1
    }
    HoverHandler { cursorShape: status.returnable ? Qt.PointingHandCursor : Qt.ArrowCursor }
}
