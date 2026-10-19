import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: overview
    required property var bridge
    signal openLibrary()
    signal createLesson()
    Layout.fillWidth: true; spacing: 14
    readonly property var summary: bridge.librarySummary
    RowLayout {
        Layout.fillWidth: true
        Label { objectName: "homeOverviewHeading"; text: "Tổng quan bài giảng"; color: "#16314f"; font.pixelSize: 19; font.weight: Font.DemiBold; Layout.fillWidth: true }
        ActionButton { objectName: "homeOverviewLibrary"; text: "Mở thư viện"; onClicked: overview.openLibrary() }
    }
    RowLayout {
        Layout.fillWidth: true; spacing: 12
        Repeater {
            model: [
                {label: "Tổng bài giảng", value: overview.summary.total, icon: "lessons", color: "#0869f9", tint: "#eef5ff"},
                {label: "Sẵn sàng dạy", value: overview.summary.ready, icon: "classroom", color: "#168567", tint: "#eef8f4"},
                {label: "Đã có giọng đọc", value: overview.summary.voiced, icon: "voice", color: "#0869f9", tint: "#eef5ff"},
                {label: "Cần hoàn thiện", value: Math.max(0, overview.summary.total - overview.summary.ready), icon: "bilingual", color: "#a66318", tint: "#fbf5eb"}
            ]
            Rectangle {
                required property var modelData
                required property int index
                Layout.fillWidth: true; Layout.preferredWidth: 1; implicitHeight: 116
                color: "white"; radius: 13; border.color: "#dce7f5"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: overview.width < 1000 ? 14 : 18; spacing: 7
                    RowLayout {
                        Layout.fillWidth: true
                        Label { objectName: "homeMetricValue" + index; text: modelData.value; color: modelData.color; font.pixelSize: 29; font.weight: Font.DemiBold; Layout.fillWidth: true }
                        Rectangle { width: 34; height: 34; radius: 10; color: modelData.tint
                            Image { anchors.centerIn: parent; width: 28; height: 28; source: "../assets/navigation/" + modelData.icon + ".png"; sourceSize.width: 64; sourceSize.height: 64; fillMode: Image.PreserveAspectFit }
                        }
                    }
                    Label { text: modelData.label; color: "#526987"; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                }
            }
        }
    }
    Rectangle {
        Layout.fillWidth: true; implicitHeight: recentContent.implicitHeight + 32
        color: "white"; radius: 14; border.color: "#dce7f5"
        ColumnLayout {
            id: recentContent; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 16; spacing: 8
            Label { text: "Bài gần đây"; color: "#16314f"; font.pixelSize: 15; font.weight: Font.DemiBold; Layout.bottomMargin: 4 }
            Repeater {
                model: overview.bridge.recentLessons.slice(0, 3)
                Button {
                    id: recentButton
                    required property var modelData
                    required property int index
                    objectName: "homeRecentLesson" + index
                    Layout.fillWidth: true; implicitHeight: Math.max(72, recentRow.implicitHeight + 22); padding: 11
                    enabled: !overview.bridge.busy && !overview.bridge.narrationBusy
                    Accessible.name: "Mở " + modelData.title
                    onClicked: overview.bridge.openLesson(modelData.id)
                    background: Rectangle { radius: 9; color: recentButton.hovered ? "#f2f7fe" : "transparent"; border.color: recentButton.visualFocus ? "#0869f9" : "transparent" }
                    contentItem: RowLayout {
                        id: recentRow; spacing: 12
                        Rectangle { width: 42; height: 46; radius: 9; color: "#edf4ff"
                            Image { anchors.centerIn: parent; width: 34; height: 34; source: "../assets/navigation/lessons.png"; fillMode: Image.PreserveAspectFit }
                        }
                        ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 5
                            Label { objectName: "homeRecentTitle" + recentButton.index; text: recentButton.modelData.title; color: "#16314f"; font.pixelSize: 14; font.weight: Font.DemiBold; textFormat: Text.PlainText; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
                            Label { text: [recentButton.modelData.subject, recentButton.modelData.grade ? "Lớp " + recentButton.modelData.grade : "", recentButton.modelData.slides_count ? recentButton.modelData.slides_count + " slide" : ""].filter(function(value) { return !!value }).join(" · "); color: "#687e9b"; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        }
                        Label { visible: !!(recentButton.modelData.narration || {}).ready; text: "Có giọng đọc"; color: "#168567"; font.pixelSize: 11 }
                        Label { text: "Mở bài  →"; color: "#0869f9"; font.pixelSize: 12; font.weight: Font.DemiBold; Layout.leftMargin: 10 }
                    }
                }
            }
            ColumnLayout {
                visible: !overview.summary.total; Layout.fillWidth: true; Layout.topMargin: 12; Layout.bottomMargin: 12; spacing: 10
                Label { text: "Thư viện đang chờ bài giảng đầu tiên"; color: "#16314f"; font.pixelSize: 15; Layout.alignment: Qt.AlignHCenter }
                Label { text: "Chuyển ngữ PowerPoint hoặc tạo giọng cho bài có sẵn để bắt đầu."; color: "#687e9b"; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                ActionButton { objectName: "homeOverviewCreate"; text: "Chuyển đổi bài giảng"; primary: true; Layout.alignment: Qt.AlignHCenter; onClicked: overview.createLesson() }
            }
        }
    }
}
