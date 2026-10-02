import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: assistant
    required property var teaching
    required property var bridge
    implicitHeight: Math.max(160, bridge.mascotSettings.visible ? bridge.mascotSettings.size + 40 : 160)
    color: "#eaf3ff"
    radius: 16
    RowLayout {
        anchors.fill: parent; anchors.margins: 14; spacing: 18
        Mascot { objectName: "mascotAssistant"; character: bridge.settings.mascot; expression: bridge.mascotState; subject: bridge.lesson.subject || ""; accessories: bridge.mascotSettings.accessories; reducedMotion: bridge.mascotSettings.reduced_motion; visible: bridge.mascotSettings.visible && (bridge.mascotSettings.show_explanation || !teaching.response.available || teaching.response.action !== "explanation"); Layout.preferredWidth: bridge.mascotSettings.size; Layout.preferredHeight: bridge.mascotSettings.size + 15 }
        ColumnLayout { Layout.fillWidth: true; spacing: 8
            RowLayout { Label { text: bridge.settings.mascot + " · Trợ giảng theo bài"; font.bold: true; color: "#112650" } Item { Layout.fillWidth: true } SelectBox { id: language; model: ["English", "Tiếng Việt"]; implicitWidth: 125 } }
            Flow { Layout.fillWidth: true; spacing: 5
                Repeater { model: [{action:"explanation",label:"Giải thích"},{action:"example",label:"Ví dụ"},{action:"prompt",label:"Điều hành lớp"},{action:"question",label:"Hỏi lớp"},{action:"rescue",label:"VI Rescue"}]
                    ActionButton { required property var modelData; text: modelData.label; implicitHeight: 30; onClicked: teaching.ask(modelData.action, modelData.action === "rescue" ? "vi" : language.currentIndex === 0 ? "en" : "vi") }
                }
            }
            ScrollView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; TextArea { readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; text: teaching.response.text; color: "#112650"; font.pixelSize: 14; background: null } }
        }
    }
}
