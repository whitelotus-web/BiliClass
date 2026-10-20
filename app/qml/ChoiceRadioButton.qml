import QtQuick
import QtQuick.Controls

RadioButton {
    id: radio
    opacity: enabled ? 1 : .45
    property bool highlightSelection: false
    background: Rectangle {
        radius: 7
        color: radio.highlightSelection && radio.checked ? AppTheme.adapt("#f2f7ff") : "transparent"
        border.width: 1
        border.color: radio.highlightSelection ? (radio.checked ? AppTheme.adapt("#dce8f8") : AppTheme.line) : "transparent"
    }
    indicator: Rectangle {
        objectName: radio.objectName + "Indicator"
        x: radio.highlightSelection ? 6 : 0; y: (radio.height - height) / 2
        width: 18; height: 18; radius: 9
        color: AppTheme.surface; border.width: radio.visualFocus ? 2 : 1
        border.color: radio.checked ? AppTheme.adapt("#0869f9") : AppTheme.adapt("#8c9eb8")
        Rectangle { anchors.centerIn: parent; width: 10; height: 10; radius: 5; color: AppTheme.adapt("#0869f9"); visible: radio.checked }
    }
    contentItem: Text {
        leftPadding: 25
        text: radio.text; color: AppTheme.adapt("#112650"); font.pixelSize: 13; font.weight: Font.DemiBold
        wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter
    }
}
