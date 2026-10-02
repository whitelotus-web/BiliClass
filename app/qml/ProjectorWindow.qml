import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Window {
    id: projection
    required property var bridge
    property bool rescue: false
    property bool quiz: false
    readonly property bool showMascot: bridge.mascotSettings.visible &&
        (quiz ? bridge.mascotSettings.show_quiz :
        (!!bridge.teachingContext.response.available && bridge.teachingContext.response.action === "explanation" ? bridge.mascotSettings.show_explanation : true))
    property var classState: bridge.classroomContext.state
    property var content: bridge.presentationContent(rescue)
    Connections { target: bridge; function onChanged() { projection.content = bridge.presentationContent(projection.rescue) } }
    onRescueChanged: content = bridge.presentationContent(rescue)
    color: "#f3f7fc"
    title: "BiliClass · Màn hình lớp học"
    width: 1280; height: 720
    minimumWidth: 800; minimumHeight: 500
    Shortcut { sequence: "Escape"; onActivated: projection.close() }
    Connections { target: bridge; function onSelectionChanged() { projection.rescue = false } }
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 40; spacing: 22
        RowLayout { Label { text: "BiliClass"; color: "#112650"; font.pixelSize: 25; font.bold: true } Item { Layout.fillWidth: true } Label { text: "L" + (bridge.lesson.level || 0); color: "#0869f9"; font.pixelSize: 20 } }
        Label { text: bridge.lesson.title || ""; font.pixelSize: 30; font.bold: true; color: "#112650"; Layout.fillWidth: true; elide: Text.ElideRight; textFormat: Text.PlainText }
        RowLayout { visible: bridge.settings.show_profile; Layout.fillWidth: true; spacing: 12
            Image { objectName: "projectorSchoolLogo"; visible: !!bridge.schoolLogoUrl; source: bridge.schoolLogoUrl; cache: false; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: 56; Layout.preferredHeight: 56 }
            Label { objectName: "projectorProfile"; text: [bridge.settings.teacher, bridge.settings.school].filter(function(value) { return !!value }).join("  ·  "); font.pixelSize: 16; color: "#667997"; Layout.fillWidth: true; elide: Text.ElideRight; textFormat: Text.PlainText }
        }
        ScrollView { visible: !projection.quiz; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; contentWidth: availableWidth
            ColumnLayout { width: parent.width; spacing: 25
                Label { visible: !bridge.segment.approved; text: "Thầy cô đang chuẩn bị nội dung tiếp theo."; font.pixelSize: 27; color: "#667997"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                GridLayout { visible: !!bridge.segment.approved; columns: projection.content.columns; Layout.fillWidth: true; columnSpacing: 30; rowSpacing: 22
                    Label { visible: projection.content.show_vi; text: projection.content.vi; color: "#112650"; font.pixelSize: 32; wrapMode: Text.WordWrap; Layout.fillWidth: true; Layout.preferredWidth: 1; textFormat: Text.PlainText }
                    Label { visible: projection.content.show_en; text: projection.content.en; color: "#0869f9"; font.pixelSize: 30; font.italic: bridge.lesson.layout === "line_pair"; wrapMode: Text.WordWrap; Layout.fillWidth: true; Layout.preferredWidth: 1; textFormat: Text.PlainText }
                }
                Label { visible: !!bridge.segment.approved && projection.content.needs_keywords; text: "Chưa có từ khóa song ngữ khớp với đoạn này."; color: "#667997"; font.pixelSize: 20; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Label { visible: !!bridge.segment.approved && !!bridge.teachingContext.response.available; text: bridge.teachingContext.response.text; font.pixelSize: 26; color: "#112650"; Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
            }
        }
        ScrollView { visible: projection.quiz; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; contentWidth: availableWidth
            ColumnLayout { width: parent.width; spacing: 20
                Label { text: projection.classState.title || "Chưa có lớp đang mở"; color: "#112650"; font.pixelSize: 26; Layout.fillWidth: true; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
                Label { text: projection.classState.round ? ((projection.classState.round.language === "en" ? "" : projection.classState.round.vi) + "\n" + (projection.classState.round.language === "vi" ? "" : projection.classState.round.en)) : "Quét QR để tham gia lớp"; font.pixelSize: 32; color: "#112650"; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                Repeater { model: (projection.classState.round || {}).options || []
                    Label { required property var modelData; text: modelData.id + " · " + (projection.classState.round.language === "en" ? modelData.en : projection.classState.round.language === "vi" ? modelData.vi : modelData.vi + " / " + modelData.en); color: "#0869f9"; font.pixelSize: 25; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
                }
                Label { visible: (projection.classState.round || {}).status === "revealed"; text: (projection.classState.round || {}).kind === "poll" ? "Khảo sát không chấm điểm" : "Đáp án: " + ((projection.classState.round || {}).correct || ""); color: "#168567"; font.pixelSize: 28; font.bold: true; Layout.fillWidth: true }
                Image { source: bridge.classroomContext.qrImage; Layout.preferredWidth: 150; Layout.preferredHeight: 150; fillMode: Image.PreserveAspectFit; smooth: false }
                Label { text: bridge.classroomContext.joinUrl; font.pixelSize: 14; color: "#667997"; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; textFormat: Text.PlainText }
            }
        }
        RowLayout { Layout.fillWidth: true
            Mascot { objectName: "mascotProjectorLeft"; visible: projection.showMascot && bridge.mascotSettings.position === "left"; character: bridge.settings.mascot; expression: bridge.mascotState; subject: bridge.lesson.subject || ""; accessories: bridge.mascotSettings.accessories; reducedMotion: bridge.mascotSettings.reduced_motion; Layout.preferredWidth: bridge.mascotSettings.size; Layout.preferredHeight: bridge.mascotSettings.size + 15 }
            Item { Layout.fillWidth: true }
            ActionButton { text: rescue ? "Ẩn tiếng Việt" : "VI Rescue"; onClicked: projection.rescue = !projection.rescue }
            Mascot { objectName: "mascotProjectorRight"; visible: projection.showMascot && bridge.mascotSettings.position === "right"; character: bridge.settings.mascot; expression: bridge.mascotState; subject: bridge.lesson.subject || ""; accessories: bridge.mascotSettings.accessories; reducedMotion: bridge.mascotSettings.reduced_motion; Layout.preferredWidth: bridge.mascotSettings.size; Layout.preferredHeight: bridge.mascotSettings.size + 15 }
        }
    }
}
