import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: control
    required property var bridge
    property int rate: 0
    property string language: ""
    property string sliderName: ""
    property string labelName: ""
    signal edited(int rate)
    spacing: 8
    Label { text: "Tốc độ " + control.language; color: AppTheme.ink; font.pixelSize: 12; font.weight: Font.DemiBold }
    Slider {
        objectName: control.sliderName; Layout.fillWidth: true
        from: control.bridge.voiceSpeedChoices[0].rate; to: control.bridge.voiceSpeedChoices[control.bridge.voiceSpeedChoices.length - 1].rate
        value: control.rate; stepSize: 1; snapMode: Slider.SnapAlways
        enabled: control.bridge.multilingualVoices.length > 0
        Accessible.name: "Tốc độ " + control.language + " từ 60 đến 118 phần trăm"
        onMoved: control.edited(Math.round(value))
    }
    ComboBox {
        objectName: control.labelName; Layout.preferredWidth: 94; implicitHeight: 38
        model: control.bridge.voiceSpeedChoices; textRole: "label"; valueRole: "rate"
        currentIndex: model.map(function(row) { return row.rate }).indexOf(control.rate)
        enabled: control.bridge.multilingualVoices.length > 0
        Accessible.name: "Chọn phần trăm tốc độ " + control.language
        onActivated: control.edited(currentValue)
        contentItem: Label { text: parent.displayText; color: AppTheme.blue; font.pixelSize: 13; font.bold: true; verticalAlignment: Text.AlignVCenter; leftPadding: 8 }
        background: Rectangle { radius: 8; color: AppTheme.field; border.color: parent.activeFocus ? AppTheme.blue : AppTheme.line }
        ToolTip.visible: hovered; ToolTip.text: "100% là bình thường. Chọn số nhỏ hơn để đọc chậm."
    }
}
