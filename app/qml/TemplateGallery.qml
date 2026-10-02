import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: gallery
    required property var bridge
    property string preset: "standard"
    property int level: 2
    property string layout: "line_pair"
    property bool forCreation: false
    signal applyPreset(string preset)
    title: "Mẫu bài giảng song ngữ"
    modal: true
    width: Math.min(1020, parent.width - 48)
    height: Math.min(760, parent.height - 40)
    anchors.centerIn: parent
    standardButtons: Dialog.Close
    contentItem: ColumnLayout {
        spacing: 12
        RowLayout {
            Layout.fillWidth: true
            ComboBox {
                id: presetChoice; objectName: "templatePresetChoice"
                model: gallery.bridge.templatePresets; textRole: "label"; valueRole: "id"
                currentIndex: Math.max(0, ["standard", "visual", "practice"].indexOf(gallery.preset))
                Layout.fillWidth: true
                onActivated: gallery.preset = currentValue
            }
            ComboBox {
                id: blockChoice; objectName: "templateBlockChoice"
                model: gallery.bridge.slideTypes; textRole: "label"; valueRole: "id"
                Layout.fillWidth: true
            }
            ActionButton { text: "Dùng mẫu này"; primary: true; onClicked: { gallery.applyPreset(gallery.preset); gallery.close() } }
        }
        Label {
            Layout.fillWidth: true
            text: (gallery.bridge.templatePresets[presetChoice.currentIndex] || {}).description || ""
            color: "#667997"; wrapMode: Text.WordWrap; font.pixelSize: 13
        }
        TemplateSlide {
            id: sampleSlide; objectName: "templateSampleSlide"
            Layout.fillWidth: true; Layout.fillHeight: true
            plan: gallery.bridge.templateExample(gallery.preset, blockChoice.currentValue || "title", gallery.level, gallery.layout)
        }
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "14 loại slide dùng chung cho mọi môn. Thầy cô cung cấp và duyệt nội dung bài."
                Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#667997"; font.pixelSize: 12
            }
            ActionButton { text: "Mở PowerPoint mẫu"; onClicked: gallery.bridge.openTemplateSample(gallery.preset) }
        }
    }
}
