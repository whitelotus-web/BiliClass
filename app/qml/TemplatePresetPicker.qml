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
            color: picker.currentIndex === card.index ? AppTheme.adapt("#f2f7ff") : "transparent"
            border.width: 1
            border.color: picker.currentIndex === card.index ? AppTheme.adapt("#dce8f8") : AppTheme.line
            MouseArea {
                anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                onClicked: {
                    radio.forceActiveFocus(Qt.MouseFocusReason)
                    picker.currentIndex = card.index
                }
            }
            ColumnLayout {
                id: contents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 10; spacing: 6
                Image {
                    objectName: "creationPresetPreview_" + card.modelData.id
                    source: "../assets/templates/universal2026/previews/" + card.modelData.id + ".png"
                    Layout.fillWidth: true; Layout.preferredHeight: Math.min(138, width * 9 / 16)
                    fillMode: Image.PreserveAspectFit; asynchronous: true; smooth: true
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: picker.currentIndex = card.index }
                }
                ChoiceRadioButton {
                    id: radio
                    objectName: "creationPresetSelect_" + card.modelData.id
                    ButtonGroup.group: choices; checked: picker.currentIndex === card.index
                    text: card.modelData.name; font.pixelSize: 13; font.bold: true
                    Layout.fillWidth: true; onClicked: picker.currentIndex = card.index
                }
                RowLayout {
                    Layout.fillWidth: true; spacing: 10
                    Label { objectName: "creationPresetDetail_" + card.modelData.id; text: card.modelData.detail; color: AppTheme.adapt("#667997"); font.pixelSize: 11; Layout.fillWidth: true; Layout.minimumWidth: 0; wrapMode: Text.WordWrap }
                    PreviewButton {
                        objectName: "creationPresetView_" + card.modelData.id
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: picker.previewRequested(card.modelData.id)
                    }
                }
            }
        }
    }
}
