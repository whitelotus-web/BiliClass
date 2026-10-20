import QtQuick
import QtQuick.Controls

ToolButton {
    id: warning
    property var review: ({})
    signal requestInspect()
    visible: ["repair", "incomplete"].indexOf(review.kind) >= 0
    text: review.kind === "repair" ? "Cần kiểm tra bố cục" : review.label || "Cần kiểm tra nội dung"
    padding: 0; implicitHeight: 18
    ToolTip.visible: hovered; ToolTip.delay: 500; ToolTip.text: review.detail || ""
    contentItem: Label { text: warning.text; color: AppTheme.warning; font.pixelSize: 11; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
    background: null
    onClicked: requestInspect()
}
