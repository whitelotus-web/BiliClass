import QtQuick
import QtQuick.Controls

Item {
    id: view
    property string conversionFormat: "parallel_columns"
    property string preset: "standard"
    readonly property real factor: Math.min(width / 960, height / 540)
    readonly property bool englishOnly: conversionFormat === "english_only"
    readonly property color accent: preset === "practice" ? "#138578" : preset === "visual" ? "#bf6427" : "#0869f9"
    implicitWidth: 960; implicitHeight: 540
    Rectangle {
        width: 960; height: 540; anchors.centerIn: parent; scale: view.factor
        color: view.preset === "visual" ? "#fffcf6" : "white"; border.color: "#dce6f3"; clip: true
        Rectangle { x: 0; y: 0; width: 960; height: 8; color: view.accent }
        Label {
            x: 40; y: 38; width: 880; height: 70
            text: view.englishOnly ? "Area of a rectangle" : view.conversionFormat === "integrated_keywords"
                ? "Diện tích hình chữ nhật (Area of a rectangle)" : "Diện tích hình chữ nhật\nArea of a rectangle"
            color: "#112650"; font.pixelSize: 27; font.bold: true; wrapMode: Text.WordWrap
        }
        Rectangle { x: 40; y: 122; width: 880; height: 1; color: "#dce6f3" }
        Item {
            visible: view.conversionFormat === "parallel_columns"
            Label { x: 40; y: 150; width: 420; text: "TIẾNG VIỆT"; color: "#667997"; font.pixelSize: 17; font.bold: true }
            Label { x: 40; y: 192; width: 420; text: "Diện tích hình chữ nhật bằng chiều dài nhân chiều rộng.\n\nChiều dài: 6 m. Chiều rộng: 3 m."; color: "#112650"; font.pixelSize: 25; wrapMode: Text.WordWrap }
            Rectangle { x: 480; y: 148; width: 1; height: 174; color: "#dce6f3" }
            Label { x: 510; y: 150; width: 410; text: "ENGLISH"; color: view.accent; font.pixelSize: 17; font.bold: true }
            Label { x: 510; y: 192; width: 410; text: "The area of a rectangle equals length times width.\n\nLength: 6 m. Width: 3 m."; color: view.accent; font.pixelSize: 25; wrapMode: Text.WordWrap }
        }
        Item {
            visible: view.conversionFormat === "sentence_pairs"
            Label { x: 40; y: 151; width: 880; text: "Diện tích hình chữ nhật bằng chiều dài nhân chiều rộng."; color: "#112650"; font.pixelSize: 25 }
            Label { x: 40; y: 195; width: 880; text: "The area of a rectangle equals length times width."; color: view.accent; font.pixelSize: 25; font.italic: true }
            Label { x: 40; y: 267; width: 880; text: "Chiều dài: 6 m. Chiều rộng: 3 m."; color: "#112650"; font.pixelSize: 25 }
            Label { x: 40; y: 311; width: 880; text: "Length: 6 m. Width: 3 m."; color: view.accent; font.pixelSize: 25; font.italic: true }
        }
        Label {
            visible: view.conversionFormat === "integrated_keywords"
            x: 40; y: 156; width: 880; height: 190
            text: "Diện tích <b>(area)</b> hình chữ nhật bằng chiều dài <b>(length)</b> nhân chiều rộng <b>(width)</b>.<br><br>Chiều dài: 6 m. Chiều rộng: 3 m."
            textFormat: Text.RichText; color: "#112650"; font.pixelSize: 28; wrapMode: Text.WordWrap
        }
        Label {
            visible: view.englishOnly
            x: 40; y: 158; width: 880; height: 175
            text: "The area of a rectangle equals length times width.\n\nLength: 6 m. Width: 3 m."
            color: "#112650"; font.pixelSize: 29; wrapMode: Text.WordWrap
        }
        Rectangle {
            x: 72; y: 402; width: 210; height: 96
            color: "#edf5ff"; border.color: view.accent; border.width: 3
            Label { anchors.centerIn: parent; text: "A = 18 m²"; font.pixelSize: 22; font.bold: true; color: "#112650" }
            Label { anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.top; anchors.bottomMargin: 7; text: "6 m"; color: "#667997"; font.pixelSize: 20 }
            Label { anchors.left: parent.right; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: "3 m"; color: "#667997"; font.pixelSize: 20 }
        }
        Label { x: 460; y: 420; width: 460; text: "A = l × w = 6 × 3 = 18 m²"; color: "#112650"; font.pixelSize: 29; font.bold: true }
    }
}
