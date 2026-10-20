import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Frame {
    id: picker
    required property var bridge
    objectName: "applicationAppearanceCard"
    padding: 22
    background: Rectangle { radius: 16; color: AppTheme.surface; border.color: AppTheme.line }
    ColumnLayout {
        width: parent.width; spacing: 12
        Label { text: "Giao diện ứng dụng"; font.pixelSize: 19; font.weight: Font.Bold; color: AppTheme.ink }
        RowLayout {
            Layout.fillWidth: true; spacing: 14
            Repeater {
                model: [{value: "light", label: "Sáng"}, {value: "dark", label: "Tối"}]
                Button {
                    id: choice
                    required property var modelData
                    readonly property bool night: modelData.value === "dark"
                    objectName: "applicationTheme" + (night ? "Dark" : "Light")
                    implicitWidth: 166; implicitHeight: 126; padding: 10
                    Layout.fillWidth: true; Layout.preferredWidth: 166; Layout.minimumWidth: 110; Layout.maximumWidth: 210
                    checkable: true; checked: picker.bridge.applicationTheme === modelData.value
                    Accessible.role: Accessible.RadioButton; Accessible.name: "Giao diện " + modelData.label
                    onClicked: picker.bridge.setApplicationTheme(modelData.value)
                    background: Rectangle {
                        radius: 12; color: choice.hovered ? AppTheme.hover : AppTheme.surface
                        border.color: choice.checked || choice.visualFocus ? AppTheme.blue : AppTheme.line
                        border.width: choice.checked || choice.visualFocus ? 2 : 1
                    }
                    contentItem: ColumnLayout {
                        spacing: 8
                        // These two fixed swatches preview the actual modes.
                        Rectangle {
                            Layout.fillWidth: true; Layout.fillHeight: true; radius: 6
                            color: choice.night ? "#101827" : "#f3f7fc"
                            border.color: choice.night ? "#34465e" : "#dfe8f4"
                            Rectangle { x: 1; y: 1; width: 27; height: parent.height - 2; radius: 5; color: choice.night ? "#182438" : "#ffffff"
                                Rectangle { x: 8; y: 10; width: 11; height: 3; radius: 1; color: "#337cff" }
                                Repeater { model: 3; Rectangle { required property int index; x: 8; y: 22 + index * 9; width: 11; height: 2; radius: 1; color: choice.night ? "#657993" : "#b8c8de" } }
                            }
                            Rectangle { x: 37; y: 11; width: parent.width - 48; height: 3; radius: 1; color: choice.night ? "#afbed2" : "#667997" }
                            Rectangle { x: 37; y: 23; width: parent.width - 48; height: 27; radius: 4; color: choice.night ? "#182438" : "#ffffff"; border.color: choice.night ? "#34465e" : "#dfe8f4"
                                Rectangle { x: 7; y: 7; width: parent.width - 20; height: 2; radius: 1; color: choice.night ? "#657993" : "#b8c8de" }
                                Rectangle { x: 7; y: 14; width: parent.width - 32; height: 2; radius: 1; color: choice.night ? "#657993" : "#b8c8de" }
                            }
                            Rectangle { x: 37; y: 58; width: 30; height: 7; radius: 3; color: "#1764db" }
                        }
                        RowLayout { Layout.fillWidth: true
                            Label { text: choice.modelData.label; color: AppTheme.ink; font.pixelSize: 13; font.weight: Font.DemiBold; Layout.fillWidth: true }
                            Label { text: "✓"; visible: choice.checked; color: AppTheme.blue; font.pixelSize: 15; font.bold: true; Accessible.ignored: true }
                        }
                    }
                }
            }
        }
    }
}
