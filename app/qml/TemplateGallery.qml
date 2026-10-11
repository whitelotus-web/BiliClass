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
    property string conversionFormat: "sentence_pairs"
    property string selectedRole: "language"
    readonly property var roles: [
        {id:"language", label:"Kiểu song ngữ đã chọn"}, {id:"title", label:"Tên bài"},
        {id:"concept", label:"Kiến thức"}, {id:"visual", label:"Hình & chú thích"},
        {id:"practice", label:"Luyện tập"}
    ]
    readonly property var modeNames: ({parallel_columns:"Hai cột song ngữ", sentence_pairs:"Song ngữ từng câu", integrated_keywords:"Tích hợp từ khóa", english_only:"Tiếng Anh 100%"})
    signal applyPreset(string preset)
    title: "Mẫu bài giảng"
    modal: true
    width: Math.min(1180, parent.width - 32)
    height: Math.min(870, parent.height - 28)
    anchors.centerIn: parent
    standardButtons: Dialog.Close
    onOpened: selectedRole = "language"
    onConversionFormatChanged: selectedRole = "language"
    contentItem: ColumnLayout {
        spacing: 10
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Repeater {
                model: gallery.bridge.templatePresets
                ActionButton {
                    required property var modelData
                    objectName: "referencePreset_" + modelData.id
                    Layout.fillWidth: true
                    text: modelData.label; primary: gallery.preset === modelData.id
                    onClicked: gallery.preset = modelData.id
                }
            }
        }
        Label {
            Layout.fillWidth: true
            text: (gallery.bridge.templatePresets[["standard", "visual", "practice"].indexOf(gallery.preset)] || {}).description || ""
            color: "#667997"; wrapMode: Text.WordWrap; font.pixelSize: 14
        }
        RowLayout {
            Layout.fillWidth: true
            Label { text: "Kiểu đã chọn: " + gallery.modeNames[gallery.conversionFormat]; color: "#112650"; font.bold: true; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            ActionButton { text: "Dùng mẫu này"; primary: true; onClicked: { gallery.applyPreset(gallery.preset); gallery.close() } }
        }
        RowLayout {
            Layout.fillWidth: true; spacing: 8
            Repeater {
                model: gallery.roles
                ItemDelegate {
                    id: thumbnail
                    required property var modelData
                    objectName: "templateThumbnail_" + modelData.id
                    Layout.fillWidth: true; Layout.preferredHeight: 115
                    onClicked: gallery.selectedRole = modelData.id
                    background: Rectangle { color: "white"; radius: 6; border.width: 2; border.color: gallery.selectedRole === thumbnail.modelData.id ? "#0869f9" : "#e0e8f3" }
                    contentItem: ColumnLayout {
                        spacing: 3
                        Image {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            source: gallery.bridge.templatePreviewImage(gallery.preset, thumbnail.modelData.id, gallery.conversionFormat)
                            fillMode: Image.PreserveAspectFit; asynchronous: false; mipmap: true
                        }
                        Label { text: thumbnail.modelData.label; font.pixelSize: 12; color: "#112650"; Layout.alignment: Qt.AlignHCenter }
                    }
                }
            }
        }
        Image {
            id: sampleSlide; objectName: "templateSampleSlide"
            Layout.fillWidth: true; Layout.fillHeight: true
            source: gallery.bridge.templatePreviewImage(gallery.preset, gallery.selectedRole, gallery.conversionFormat)
            fillMode: Image.PreserveAspectFit; asynchronous: false; mipmap: true
        }
        Label {
            Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#667997"; font.pixelSize: 12
            text: gallery.selectedRole === "language"
                ? "Ví dụ thể hiện đúng kiểu song ngữ đã chọn. Nội dung minh họa không được gửi cho ChatGPT."
                : "Ảnh minh họa vai trò và phong cách slide. Khi chuyển đổi, ngôn ngữ luôn theo kiểu đã chọn; nội dung và hình lấy từ tài liệu thầy cô."
        }
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Dùng cho lớp 1–12 và mọi môn. BiliClass gửi mẫu trống; ChatGPT điều chỉnh chữ, hình và cách diễn đạt theo môn/khối."
                Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#667997"; font.pixelSize: 12
            }
            ActionButton { text: "Mở PowerPoint mẫu trống"; onClicked: gallery.bridge.openTemplateSample(gallery.preset) }
        }
    }
}