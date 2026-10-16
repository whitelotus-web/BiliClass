import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: home
    required property var bridge
    signal chooseDocument()
    signal continueWork()
    signal openLibrary()
    signal openClassroom()
    readonly property bool working: bridge.narrationBusy || bridge.browserState.running
    spacing: 16
    component HomeButton: Button {
        property bool primary: true
        implicitHeight: 42; leftPadding: 18; rightPadding: 18
        contentItem: Label { text: parent.text; color: "white"; font.pixelSize: 13; font.weight: Font.DemiBold; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { implicitWidth: 140; implicitHeight: 42; radius: 10; color: parent.enabled ? (parent.down ? "#0755ce" : parent.hovered ? "#1678ff" : "#0869f7") : "#b6c9e4"; border.width: parent.visualFocus ? 2 : 0; border.color: "#102b50" }
    }

    Rectangle {
        objectName: "homeWelcomeHero"
        Layout.fillWidth: true; implicitHeight: Math.max(170, greeting.implicitHeight + 40)
        radius: 18
        gradient: Gradient { orientation: Gradient.Horizontal; GradientStop { position: 0; color: "#f9fcff" } GradientStop { position: 1; color: "#e7f1ff" } }
        RowLayout {
            anchors.fill: parent; anchors.margins: 22; spacing: 20
            ColumnLayout {
                id: greeting; Layout.fillWidth: true; spacing: 9
                Label { text: "Chào " + (home.bridge.settings.teacher || "Thầy cô") + "!"; color: "#102b50"; font.pixelSize: home.width > 1000 ? 32 : 27; font.weight: Font.Bold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                Rectangle { width: 32; height: 4; radius: 2; color: "#ff8624" }
                Label { text: "Chuyển ngữ thông minh. Nâng tầm bài giảng."; color: "#244b7b"; font.pixelSize: 15; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                Label { text: "Chuẩn bị bài Việt–Anh hoặc tiếng Anh, xem lại và tự tin lên lớp."; color: "#667c97"; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            Image {
                Layout.preferredWidth: home.width > 1000 ? 195 : 145; Layout.fillHeight: true
                source: home.bridge.settings.mascot === "Lumi" ? "../assets/lumi-welcome.png" : "../assets/milo-welcome.png"
                sourceSize.width: 420; fillMode: Image.PreserveAspectFit
                Accessible.name: home.bridge.settings.mascot + " chào thầy cô"
            }
        }
    }
    Rectangle {
        objectName: "homeWorkPanel"
        Layout.fillWidth: true; implicitHeight: Math.max(112, startRow.implicitHeight + 32)
        radius: 15; color: "white"; border.color: "#cedff4"
        DropArea {
            anchors.fill: parent
            enabled: !home.working && !home.bridge.busy
            onDropped: function(drop) { if (drop.hasUrls) { home.documentDropped(drop.urls); drop.acceptProposedAction() } }
        }
        RowLayout {
            id: startRow; anchors.fill: parent; anchors.margins: 18; spacing: 18
            Rectangle {
                Layout.preferredWidth: 52; Layout.preferredHeight: 58; radius: 10; color: "#fff2e8"
                Label { anchors.centerIn: parent; text: home.working ? "…" : "PPT"; color: "#d76322"; font.pixelSize: 16; font.bold: true }
            }
            ColumnLayout {
                Layout.fillWidth: true; spacing: 6
                Label { text: home.working ? (home.bridge.narrationBusy ? "Giọng đọc đang được chuẩn bị" : "Bài giảng đang chuyển ngữ") : "Bắt đầu từ tài liệu của thầy cô"; font.pixelSize: 17; font.weight: Font.DemiBold; color: "#102b50"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Label { text: home.working ? "Phần đã hoàn tất được lưu để tiếp tục." : "Kéo thả tệp vào đây, hoặc chọn tài liệu để bắt đầu."; color: "#667c97"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Label { visible: !home.working; text: "PowerPoint · Word · PDF · Văn bản · Ảnh"; color: "#8090a7"; font.pixelSize: 11 }
            }
            HomeButton {
                objectName: "homeContinueWork"; primary: true; implicitHeight: 42
                text: home.working ? "Tiếp tục công việc" : "Chọn tài liệu"
                enabled: home.working || !home.bridge.busy
                onClicked: home.working ? home.continueWork() : home.chooseDocument()
            }
        }
    }
    GridLayout {
        objectName: "homeWorkflow"
        Layout.fillWidth: true; columns: home.width > 760 ? 4 : 2; columnSpacing: 18; rowSpacing: 12
        Repeater {
            model: [
                { title: "Chọn tài liệu", detail: "Bài có sẵn hoặc nội dung mới" },
                { title: "Chuyển ngữ", detail: "Song ngữ hoặc tiếng Anh" },
                { title: "Xem lại bài", detail: "Chỉnh nội dung · giọng tùy chọn" },
                { title: "Sẵn sàng dạy", detail: "PowerPoint và mascot" }
            ]
            delegate: RowLayout {
                required property var modelData; required property int index
                Layout.fillWidth: true; spacing: 9
                Rectangle { width: 26; height: 26; radius: 8; color: "#e7f0ff"; Label { anchors.centerIn: parent; text: index + 1; color: "#0869f7"; font.pixelSize: 12; font.bold: true } }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 4
                    Label { text: modelData.title; color: "#23456d"; font.pixelSize: 12; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Label { text: modelData.detail; color: "#8090a7"; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                }
            }
        }
    }
    signal documentDropped(var urls)
}
