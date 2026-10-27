import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: preview
    property string family: "Times New Roman"
    property real pointSize: 12
    property color textColor: "#17263b"
    property string highlight: "none"
    property bool bold: false
    property bool italic: true
    property bool underline: false
    property bool strike: false
    property string mode: "below"
    readonly property bool columns: mode === "columns"
    readonly property string sampleVietnamese: "Khám phá ý tưởng mới."
    readonly property string sampleEnglish: "Explore new ideas."
    function escaped(value) { return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;") }
    function englishMarkup(value) {
        let content = escaped(value)
        if (strike) content = "<s>" + content + "</s>"
        if (underline) content = "<u>" + content + "</u>"
        if (italic) content = "<i>" + content + "</i>"
        if (bold) content = "<b>" + content + "</b>"
        const fill = highlight === "none" ? "" : ";background-color:#" + highlight
        return '<font face="' + escaped(family) + '" color="' + textColor + '"><span style="font-size:' + pointSize + 'pt' + fill + '">' + content + '</span></font>'
    }
    implicitWidth: 300; implicitHeight: 108; spacing: 4
    Label { objectName: "wordDemoHeading"; text: "Xem trước song ngữ"; horizontalAlignment: Text.AlignHCenter; color: AppTheme.muted; font.pixelSize: 12; Layout.fillWidth: true }
    Rectangle { objectName: "wordDemoFrame"; Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 72
        radius: 12; color: AppTheme.surface; border.color: AppTheme.line
        Rectangle { anchors.fill: parent; anchors.margins: 8; color: "white"; radius: 5; clip: true
            ContentScrollView { id: sampleScroll; anchors.fill: parent; anchors.margins: 6; contentWidth: availableWidth
                Item { id: example; width: sampleScroll.availableWidth
                    height: preview.mode === "keywords" ? keywords.implicitHeight : preview.columns ? Math.max(vietnamese.implicitHeight, englishLine.height) : preview.mode === "english" ? englishLine.height : vietnamese.implicitHeight + 4 + englishLine.height
                    Text { id: vietnamese; objectName: "wordDemoVietnamese"; visible: preview.mode === "below" || preview.columns; text: preview.sampleVietnamese; color: "#17263b"; font.family: "Times New Roman"; font.pointSize: 11; wrapMode: Text.Wrap; width: preview.columns ? (parent.width - 12) / 2 : parent.width }
                    Rectangle { objectName: "wordDemoColumnDivider"; visible: preview.columns; x: (parent.width - 1) / 2; width: 1; height: example.height; color: "#d5dbe4" }
                    Item { id: englishLine; visible: preview.mode !== "keywords"; x: preview.columns ? (parent.width + 12) / 2 : 0; y: preview.mode === "below" ? vietnamese.implicitHeight + 4 : 0; width: preview.columns ? (parent.width - 12) / 2 : parent.width; height: englishText.implicitHeight
                        Rectangle { visible: preview.highlight !== "none"; width: Math.min(parent.width, englishText.paintedWidth); height: englishText.paintedHeight; color: visible ? "#" + preview.highlight : "transparent" }
                        Text { id: englishText; objectName: "wordDemoEnglish"; text: preview.sampleEnglish; width: parent.width; wrapMode: Text.Wrap
                            color: preview.textColor; font.family: preview.family; font.pointSize: preview.pointSize
                            font.bold: preview.bold; font.italic: preview.italic; font.underline: preview.underline; font.strikeout: preview.strike
                        }
                    }
                    Text { id: keywords; objectName: "wordDemoKeywords"; visible: preview.mode === "keywords"; width: parent.width; wrapMode: Text.Wrap; textFormat: Text.RichText; color: "#17263b"; font.family: "Times New Roman"; font.pointSize: 11
                        text: "Khám phá (" + preview.englishMarkup("explore") + ") ý tưởng (" + preview.englishMarkup("ideas") + ") mới."
                    }
                }
            }
        }
    }
}
