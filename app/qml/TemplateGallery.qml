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
    width: Math.min(1180, parent.width - 32)
    height: Math.min(870, parent.height - 28)
    anchors.centerIn: parent
    standardButtons: Dialog.Close
    contentItem: ColumnLayout {
        spacing: 10
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Repeater {
                model: gallery.bridge.templatePresets
                ActionButton {
                    required property var modelData
                    Layout.fillWidth: true
                    text: modelData.label; primary: gallery.preset === modelData.id
                    onClicked: gallery.preset = modelData.id
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            ComboBox {
                id: presetChoice; objectName: "templatePresetChoice"
                model: gallery.bridge.templatePresets; textRole: "label"; valueRole: "id"
                currentIndex: Math.max(0, ["standard", "visual", "practice"].indexOf(gallery.preset))
                visible: false
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
            color: "#667997"; wrapMode: Text.WordWrap; font.pixelSize: 14
        }
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Repeater {
                model: ["title", "visual", "example", "practice"]
                ItemDelegate {
                    id: thumbnail
                    required property string modelData
                    objectName: "templateThumbnail_" + modelData
                    Layout.fillWidth: true; Layout.preferredHeight: 115
                    onClicked: {
                        for (let i = 0; i < gallery.bridge.slideTypes.length; i++)
                            if (gallery.bridge.slideTypes[i].id === modelData) blockChoice.currentIndex = i
                    }
                    background: Rectangle { color: "white"; radius: 6; border.width: 2; border.color: blockChoice.currentValue === thumbnail.modelData ? "#0869f9" : "#e0e8f3" }
                    contentItem: ColumnLayout {
                        spacing: 3
                        TemplateSlide { Layout.fillWidth: true; Layout.fillHeight: true; plan: gallery.bridge.templateExample(gallery.preset, thumbnail.modelData, gallery.level, gallery.layout) }
                        Label { text: ({title:"Tên bài", visual:"Hình & chú thích", example:"Ví dụ", practice:"Luyện tập"})[thumbnail.modelData]; font.pixelSize: 12; color: "#112650"; Layout.alignment: Qt.AlignHCenter }
                    }
                }
            }
        }
        TemplateSlide {
            id: sampleSlide; objectName: "templateSampleSlide"
            Layout.fillWidth: true; Layout.fillHeight: true
            plan: gallery.bridge.templateExample(gallery.preset, blockChoice.currentValue || "title", gallery.level, gallery.layout)
        }
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Bấm hình nhỏ để xem slide lớn. Ví dụ chỉ minh họa thiết kế; mẫu dùng cho mọi môn, với nội dung và hình từ bài của thầy cô."
                Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#667997"; font.pixelSize: 12
            }
            ActionButton { text: "Mở PowerPoint mẫu"; onClicked: gallery.bridge.openTemplateSample(gallery.preset) }
        }
    }
}
