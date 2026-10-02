import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: panel
    required property var teaching
    required property var bridge
    title: "Chuẩn bị trợ giảng & câu hỏi"
    modal: true
    width: Math.min(parent.width - 40, 920)
    height: Math.min(parent.height - 40, 730)
    anchors.centerIn: parent
    standardButtons: Dialog.Close
    property string itemId: ""
    property string questionId: ""
    readonly property var kinds: ["explanation", "easy_en", "example", "prompt", "question", "rescue", "vocabulary"]
    function clearItem() { itemId = ""; itemVi.text = ""; itemEn.text = ""; itemReview.checked = false }
    function clearQuestion() { questionId = ""; qVi.text = ""; qEn.text = ""; options.text = ""; rationale.text = ""; qReview.checked = false; conceptLabel.text = ""; pairGroup.text = ""; rationaleEn.text = "" }
    onOpened: { clearItem(); clearQuestion() }
    contentItem: ColumnLayout {
        spacing: 12
        Label { text: "Nội dung gắn với: " + (bridge.segment.locator || ""); color: "#112650"; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
        TabBar { id: tabs; objectName: "teachingTabs"; Layout.fillWidth: true; TabButton { text: "Trợ giảng" } TabButton { text: "Câu hỏi kiểm tra" } }
        StackLayout {
            currentIndex: tabs.currentIndex; Layout.fillWidth: true; Layout.fillHeight: true
            RowLayout {
                spacing: 16
                ListView { Layout.preferredWidth: 235; Layout.fillHeight: true; clip: true; spacing: 8; model: teaching.items
                    delegate: ItemDelegate { required property var modelData; width: ListView.view.width; height: 74
                        contentItem: Label { text: (modelData.approved ? "Đã duyệt · " : "Nháp · ") + modelData.kind + "\n" + (modelData.vi || modelData.en); elide: Text.ElideRight; maximumLineCount: 3; wrapMode: Text.WordWrap; color: "#112650"; textFormat: Text.PlainText }
                        onClicked: { panel.itemId = modelData.id; kind.currentIndex = panel.kinds.indexOf(modelData.kind); itemVi.text = modelData.vi; itemEn.text = modelData.en; itemReview.checked = modelData.approved }
                    }
                }
                ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 10
                    SelectBox { id: kind; Layout.fillWidth: true; model: ["Giải thích", "English đơn giản (L2)", "Ví dụ", "Câu điều hành lớp (L1+)", "Câu hỏi thảo luận", "VI Rescue", "Từ vựng"] }
                    Label { text: "Tiếng Việt"; color: "#112650" }
                    ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; TextArea { id: itemVi; objectName: "supportVi"; wrapMode: TextEdit.Wrap; selectByMouse: true; placeholderText: "Nội dung theo bài đang dạy…" } }
                    Label { text: "English"; color: "#0869f9" }
                    ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; TextArea { id: itemEn; objectName: "supportEn"; wrapMode: TextEdit.Wrap; selectByMouse: true; placeholderText: "Prepared English explanation, example or prompt…" } }
                    CheckBox { id: itemReview; objectName: "supportReview"; text: "Đã kiểm tra và duyệt mục này" }
                    RowLayout {
                        ActionButton { text: "Mục mới"; onClicked: panel.clearItem() }
                        ActionButton { text: "Lấy đoạn hiện tại"; onClicked: { itemVi.text = bridge.segment.vi || ""; itemEn.text = bridge.segment.en || ""; itemReview.checked = false } }
                        ActionButton { text: "Lưu"; iconName: "save"; objectName: "saveSupportButton"; onClicked: if (teaching.saveSupport(panel.itemId, panel.kinds[kind.currentIndex], itemVi.text, itemEn.text, itemReview.checked)) panel.clearItem() }
                        ActionButton { text: "Xóa"; iconName: "delete"; enabled: !!panel.itemId; onClicked: { teaching.deleteSupport(panel.itemId); panel.clearItem() } }
                    }
                }
            }
            RowLayout {
                spacing: 16
                ListView { Layout.preferredWidth: 235; Layout.fillHeight: true; clip: true; spacing: 8; model: teaching.questions
                    delegate: ItemDelegate { required property var modelData; width: ListView.view.width; height: 80
                        contentItem: Label { text: (modelData.approved ? "Đã duyệt · " : "Nháp · ") + modelData.concept_label + "\n" + modelData.vi; maximumLineCount: 3; elide: Text.ElideRight; wrapMode: Text.WordWrap; color: "#112650"; textFormat: Text.PlainText }
                        onClicked: { panel.questionId = modelData.id; qKind.currentIndex = ["single", "true_false", "poll"].indexOf(modelData.kind); qVi.text = modelData.vi; qEn.text = modelData.en; options.text = modelData.options.map(o => o.vi + " | " + o.en + (o.misconception ? " | " + o.misconception : "")).join("\n"); correct.currentIndex = modelData.correct ? modelData.correct.charCodeAt(0) - 65 : 0; rationale.text = modelData.rationale_vi; qReview.checked = modelData.approved; conceptLabel.text = modelData.concept_label; pairGroup.text = modelData.comparison_group || ""; rationaleEn.text = modelData.rationale_en || "" }
                    }
                }
                ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 8
                    SelectBox { id: qKind; model: ["Chọn một đáp án", "Đúng / Sai", "Khảo sát không chấm điểm"]; Layout.fillWidth: true }
                    RowLayout { Layout.fillWidth: true
                        TextField { id: conceptLabel; placeholderText: "Tên khái niệm/chủ đề"; Layout.fillWidth: true; maximumLength: 150 }
                        TextField { id: pairGroup; placeholderText: "Mã cặp câu tương đương (tùy chọn)"; Layout.fillWidth: true; maximumLength: 100; ToolTip.visible: hovered; ToolTip.text: "Dùng cùng mã cho hai câu khác nhau tương đương về nội dung và độ khó. Dùng để đối chiếu Việt/Anh có điều kiện." }
                    }
                    TextField { id: qVi; objectName: "questionVi"; placeholderText: "Câu hỏi tiếng Việt"; Layout.fillWidth: true; maximumLength: 5000 }
                    TextField { id: qEn; objectName: "questionEn"; placeholderText: "Question in English"; Layout.fillWidth: true; maximumLength: 5000 }
                    Label { text: "Mỗi dòng: lựa chọn Việt | English | hiểu nhầm (tùy chọn)"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; TextArea { id: options; objectName: "questionOptions"; wrapMode: TextEdit.Wrap; selectByMouse: true; placeholderText: "Có | Yes\nKhông | No" } }
                    RowLayout { visible: qKind.currentIndex !== 2; Label { text: "Đáp án đúng" } SelectBox { id: correct; model: ["A", "B", "C", "D", "E", "F"] } }
                    TextField { id: rationale; placeholderText: "Giải thích đáp án (chỉ công bố sau khi đóng câu)"; Layout.fillWidth: true; maximumLength: 5000 }
                    TextField { id: rationaleEn; placeholderText: "Explanation in English (after reveal)"; Layout.fillWidth: true; maximumLength: 5000 }
                    CheckBox { id: qReview; objectName: "questionReview"; text: "Đã kiểm tra câu hỏi và đáp án" }
                    RowLayout {
                        ActionButton { text: "Câu mới"; onClicked: panel.clearQuestion() }
                        ActionButton { text: "Lưu câu hỏi"; iconName: "save"; objectName: "saveQuestionButton"; onClicked: if (teaching.saveQuestion(panel.questionId, ["single", "true_false", "poll"][qKind.currentIndex], qVi.text, qEn.text, options.text, correct.currentIndex, rationale.text, qReview.checked, conceptLabel.text, pairGroup.text, rationaleEn.text)) panel.clearQuestion() }
                        ActionButton { text: "Xóa"; iconName: "delete"; enabled: !!panel.questionId; onClicked: { teaching.deleteQuestion(panel.questionId); panel.clearQuestion() } }
                    }
                }
            }
        }
        Label { text: bridge.message; color: bridge.error ? "#b14828" : "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11; textFormat: Text.PlainText }
    }
}
