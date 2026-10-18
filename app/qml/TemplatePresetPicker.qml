import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

GridLayout {
    id: picker
    property int currentIndex: 0
    readonly property int count: presets.length
    readonly property var presets: [
        {id: "standard", name: "Chuẩn lớp học", detail: "Rõ ràng, dễ theo dõi"},
        {id: "visual", name: "Trực quan", detail: "Nổi bật hình và nội dung"},
        {id: "practice", name: "Luyện tập & tương tác", detail: "Câu hỏi và hoạt động"}
    ]
    readonly property string currentText: presets[currentIndex].name
    signal previewRequested(string preset)
    columns: width >= 620 ? 3 : 1; columnSpacing: 12; rowSpacing: 12
    ButtonGroup { id: choices }
    Repeater {
        model: picker.presets
        Rectangle {
            id: card
            required property var modelData
            required property int index
            objectName: "creationPresetCard_" + modelData.id
            Layout.fillWidth: true; Layout.preferredWidth: 1
            implicitHeight: contents.implicitHeight + 20; radius: 10
            color: picker.currentIndex === index ? "#edf5ff" : "white"
            border.color: picker.currentIndex === index ? "#0869ff" : "#d6e2f3"
            border.width: picker.currentIndex === index ? 2 : 1
            ColumnLayout {
                id: contents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 10; spacing: 6
                Image {
                    objectName: "creationPresetPreview_" + card.modelData.id
                    source: "../assets/templates/universal2026/previews/" + card.modelData.id + ".png"
                    Layout.fillWidth: true; Layout.preferredHeight: Math.min(138, width * 9 / 16)
                    fillMode: Image.PreserveAspectFit; asynchronous: true; smooth: true
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: picker.currentIndex = card.index }
                }
                RadioButton {
                    objectName: "creationPresetSelect_" + card.modelData.id
                    ButtonGroup.group: choices; checked: picker.currentIndex === card.index
                    text: card.modelData.name; font.pixelSize: 13; font.bold: true
                    Layout.fillWidth: true; onClicked: picker.currentIndex = card.index
                }
                Label { text: card.modelData.detail; color: "#667997"; font.pixelSize: 11; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Button {
                    objectName: "creationPresetView_" + card.modelData.id
                    text: "Xem mẫu"; implicitHeight: 31; Layout.alignment: Qt.AlignRight
                    onClicked: picker.previewRequested(card.modelData.id)
                    contentItem: Label { text: parent.text; color: "#0869ff"; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    background: Rectangle { color: parent.hovered ? "#e7f1ff" : "white"; radius: 7; border.color: "#cbdcf4" }
                }
            }
        }
    }
}
