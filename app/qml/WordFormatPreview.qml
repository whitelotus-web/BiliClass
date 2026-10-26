import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: preview
    property string family: "Times New Roman"
    property real pointSize: 12
    property color textColor: "#17263b"
    property string highlight: "none"
    property bool bold: false
    property bool italic: true
    property bool underline: false
    property bool strike: false
    readonly property string sampleVietnamese: "Năng lượng được bảo toàn."
    readonly property string sampleEnglish: "Energy is conserved."
    implicitWidth: 300; implicitHeight: 130
    radius: 12; color: AppTheme.surface; border.color: AppTheme.line
    ColumnLayout { anchors.fill: parent; anchors.margins: 10; spacing: 6
        Label { text: "Xem trước định dạng"; color: AppTheme.muted; font.pixelSize: 11; Layout.fillWidth: true }
        Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: "white"; radius: 5; clip: true
            ContentScrollView { id: sampleScroll; anchors.fill: parent; anchors.margins: 6; contentWidth: availableWidth
                Column { width: sampleScroll.availableWidth; spacing: 6
                    Text { objectName: "wordDemoVietnamese"; text: preview.sampleVietnamese; color: "#17263b"; font.family: "Times New Roman"; font.pointSize: 11; wrapMode: Text.Wrap; width: parent.width }
                    Item { width: parent.width; height: englishText.implicitHeight
                        Rectangle { visible: preview.highlight !== "none"; width: Math.min(parent.width, englishText.paintedWidth); height: englishText.paintedHeight; color: visible ? "#" + preview.highlight : "transparent" }
                        Text { id: englishText; objectName: "wordDemoEnglish"; text: preview.sampleEnglish; width: parent.width; wrapMode: Text.Wrap
                            color: preview.textColor; font.family: preview.family; font.pointSize: preview.pointSize
                            font.bold: preview.bold; font.italic: preview.italic; font.underline: preview.underline; font.strikeout: preview.strike
                        }
                    }
                }
            }
        }
    }
}
