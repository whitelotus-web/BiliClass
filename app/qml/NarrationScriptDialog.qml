import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: dialog
    property var workspace
    property string voice: ""
    property int rate: 0
    property bool working: false
    property var currentSlide: ({})
    readonly property bool editable: !!workspace && workspace.summary.editable
    readonly property bool dirty: editable && (vietnamese.text !== (currentSlide.vi || "") || english.text !== (currentSlide.en || ""))
    objectName: "narrationScriptDialog"
    title: "Kiểm tra / sửa lời đọc theo slide"
    modal: true; width: Math.min(880, parent.width - 60); height: Math.min(670, parent.height - 60)
    anchors.centerIn: parent
    closePolicy: Popup.CloseOnEscape
    function loadSlide() {
        currentSlide = workspace.slide
        vietnamese.text = currentSlide.vi || ""
        english.text = currentSlide.en || ""
    }
    onOpened: loadSlide()
    contentItem: ColumnLayout {
        spacing: 12
        Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; color: "#667997"; text: dialog.editable ? "Tool đã tự phân loại lời Việt–Anh. Có thể sửa ngay bên dưới; lời đọc lưu riêng, giữ nguyên slide PowerPoint. Lưu thay đổi rồi tạo lại giọng." : "Lời đọc của bài này lấy từ nội dung đã lưu. Chọn Sửa nội dung bài giảng để cập nhật." }
        ComboBox {
            objectName: "narrationScriptSlide"; Layout.fillWidth: true
            model: dialog.workspace ? dialog.workspace.summary.slides : []; textRole: "label"
            currentIndex: dialog.currentSlide.index || 0; enabled: !dialog.dirty
            onActivated: { dialog.workspace.selectSlide(currentIndex); dialog.loadSlide() }
        }
        Label { visible: dialog.dirty; text: "Có thay đổi chưa lưu. Lưu hoặc bấm Bỏ thay đổi trước khi đổi slide."; color: "#a66318"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        Label { objectName: "narrationClassificationReason"; text: dialog.currentSlide.classification ? dialog.currentSlide.classification.reason : ""; color: dialog.currentSlide.classification && dialog.currentSlide.classification.needs_review ? "#a66318" : "#667997"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        CheckBox { objectName: "narrationSilentSlide"; text: "Slide này không cần lời đọc"; checked: !!dialog.currentSlide.silent; enabled: dialog.editable && !dialog.working && !dialog.dirty; onClicked: { if (dialog.workspace.setSilent(dialog.currentSlide.id, checked, dialog.currentSlide.revision)) dialog.loadSlide() } }
        GridLayout {
            columns: 2; columnSpacing: 14; Layout.fillWidth: true; Layout.fillHeight: true
            Label { text: "Lời tiếng Việt"; color: "#112650"; font.bold: true }
            Label { text: "Lời tiếng Anh"; color: "#112650"; font.bold: true }
            ContentScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumWidth: 0
                background: Rectangle { radius: 8; color: "#fbfdff"; border.color: "#d6e4f6" }
                TextArea { id: vietnamese; objectName: "narrationScriptVietnamese"; readOnly: !dialog.editable || dialog.working; selectByMouse: true; wrapMode: TextEdit.Wrap; placeholderText: "Nhập lời đọc tiếng Việt cho slide này"; font.pixelSize: 14 }
            }
            ContentScrollView { Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumWidth: 0
                background: Rectangle { radius: 8; color: "#fbfdff"; border.color: "#d6e4f6" }
                TextArea { id: english; objectName: "narrationScriptEnglish"; readOnly: !dialog.editable || dialog.working; selectByMouse: true; wrapMode: TextEdit.Wrap; placeholderText: "Nhập lời đọc tiếng Anh cho slide này"; font.pixelSize: 14 }
            }
            ActionButton { objectName: "previewNarrationScriptVietnamese"; text: "Nghe thử lời Việt"; enabled: !dialog.working && !dialog.dirty && !!vietnamese.text.trim() && !!dialog.voice; onClicked: dialog.workspace.preview("vi", dialog.voice, dialog.rate) }
            ActionButton { objectName: "previewNarrationScriptEnglish"; text: "Nghe thử lời Anh"; enabled: !dialog.working && !dialog.dirty && !!english.text.trim() && !!dialog.voice; onClicked: dialog.workspace.preview("en", dialog.voice, dialog.rate) }
        }
        Label { text: "Nghe thử tối đa 250 ký tự đầu với giọng và tốc độ đang chọn."; color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        RowLayout { Layout.fillWidth: true
            ActionButton { text: "Dừng nghe"; onClicked: appBridge.stopSpeech() }
            Item { Layout.fillWidth: true }
            ActionButton { objectName: "discardNarrationScript"; text: dialog.dirty ? "Bỏ thay đổi" : "Đóng"; onClicked: dialog.close() }
            ActionButton { objectName: "saveNarrationScript"; text: "Lưu lời đọc"; primary: true; visible: dialog.editable; enabled: dialog.dirty && !dialog.working; onClicked: { if (dialog.workspace.save(dialog.currentSlide.id, vietnamese.text, english.text, dialog.currentSlide.revision)) dialog.loadSlide() } }
        }
    }
    property var appBridge
}
