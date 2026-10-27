import QtQuick
import QtQuick.Controls

Button {
    id: button
    property bool moon: false
    readonly property color ink: checked || hovered ? AppTheme.blue : AppTheme.ink
    implicitWidth: 22; implicitHeight: 24; padding: 2
    Accessible.name: moon ? "Nền văn bản tối" : "Nền văn bản sáng"
    Accessible.checkable: true; Accessible.checked: checked
    ToolTip.visible: hovered; ToolTip.text: Accessible.name
    onInkChanged: icon.requestPaint()
    background: Rectangle { radius: 5; color: button.checked || button.hovered ? AppTheme.selected : "transparent"; border.width: button.checked || button.visualFocus ? 1 : 0; border.color: AppTheme.blue }
    contentItem: Canvas {
        id: icon
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            ctx.translate((width - 18) / 2, (height - 18) / 2)
            ctx.strokeStyle = button.ink
            ctx.lineWidth = 1.5; ctx.lineCap = "round"; ctx.lineJoin = "round"
            if (button.moon) {
                ctx.beginPath(); ctx.moveTo(11, 2)
                ctx.bezierCurveTo(3, -1, -1, 11, 6, 15)
                ctx.bezierCurveTo(11, 18, 17, 12, 16, 8)
                ctx.bezierCurveTo(11, 12, 5, 7, 11, 2)
                ctx.closePath(); ctx.stroke()
            } else {
                ctx.beginPath(); ctx.arc(9, 9, 3.2, 0, Math.PI * 2); ctx.stroke()
                for (let i = 0; i < 8; ++i) {
                    const angle = i * Math.PI / 4
                    ctx.beginPath(); ctx.moveTo(9 + Math.cos(angle) * 5.5, 9 + Math.sin(angle) * 5.5)
                    ctx.lineTo(9 + Math.cos(angle) * 7.5, 9 + Math.sin(angle) * 7.5); ctx.stroke()
                }
            }
        }
    }
}
