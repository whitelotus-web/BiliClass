import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: upload
    property bool busy: false
    property bool reading: false
    property string fileName: ""
    property int paragraphCount: 0
    property bool wholeDocument: false
    readonly property bool loaded: fileName.length > 0
    signal chooseFile()
    signal fileDropped(string url)
    signal wholeDocumentToggled(bool checked)
    implicitHeight: content.implicitHeight + 28
    radius: 16; color: drop.containsDrag ? AppTheme.selected : AppTheme.surface
    border.color: drop.containsDrag ? AppTheme.blue : AppTheme.line
    border.width: drop.containsDrag ? 2 : 1
    RowLayout {
        id: content; anchors.horizontalCenter: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter
        width: upload.loaded ? parent.width - 28 : Math.min(parent.width - 44, 840); spacing: upload.loaded ? 16 : 24
        Image {
            objectName: "wordUploadIllustration"
            source: "../assets/word-convert.png"; fillMode: Image.PreserveAspectFit
            // Clip in decoded-image coordinates, after the proportional size reduction.
            sourceClipRect: Qt.rect(32, 37, 386, 224)
            sourceSize.width: 440; sourceSize.height: 294; smooth: true; mipmap: true
            Layout.preferredWidth: upload.loaded ? 95 : upload.width < 650 ? 110 : 220; Layout.preferredHeight: upload.loaded ? 56 : 118
            Accessible.ignored: true
        }
        ColumnLayout {
            Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 7
            Label { text: upload.loaded ? upload.fileName : upload.reading ? "Đang đọc tài liệu Word…" : upload.busy ? "Đang có tác vụ khác" : "Tải lên bài giảng Word (.docx)"; textFormat: Text.PlainText; color: AppTheme.blue; font.pixelSize: upload.loaded ? 16 : 19; font.bold: true; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideMiddle; horizontalAlignment: upload.loaded ? Text.AlignLeft : Text.AlignHCenter; Layout.fillWidth: true }
            Label { text: upload.loaded ? upload.paragraphCount + " đoạn · " + (upload.wholeDocument ? "Dịch toàn bộ phần chữ" : "Chỉ dịch phần được chọn") + " · File gốc được giữ nguyên" : "Chọn hoặc kéo thả một file. Sau đó chọn những câu, đoạn cần dịch."; color: AppTheme.muted; font.pixelSize: 13; wrapMode: Text.WordWrap; horizontalAlignment: upload.loaded ? Text.AlignLeft : Text.AlignHCenter; Layout.fillWidth: true }
            WordAction { objectName: "wordUploadChoose"; visible: !upload.loaded; text: upload.busy ? "Chờ hoàn tất tác vụ…" : "Chọn file Word"; primary: true; implicitHeight: 44; font.pixelSize: 14; Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: 258; enabled: !upload.busy; onClicked: upload.chooseFile() }
            Label { visible: !upload.loaded; text: "Chỉ hỗ trợ tệp .docx tối đa 50 MB · Giữ nguyên file gốc"; color: AppTheme.muted; font.pixelSize: 12; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
        }
        CheckBox { id: wholeDocumentChoice; objectName: "wordWholeDocument"; visible: upload.loaded; text: "Dịch toàn bộ"; checked: upload.wholeDocument; enabled: !upload.busy
            implicitHeight: 32; leftPadding: 0; rightPadding: 0; spacing: 6
            indicator: Rectangle { objectName: "wordWholeDocumentIndicator"; x: 0; y: (wholeDocumentChoice.height - height) / 2; width: 16; height: 16; radius: 3; opacity: wholeDocumentChoice.enabled ? 1 : .45
                color: wholeDocumentChoice.checked ? AppTheme.blue : AppTheme.field
                border.width: wholeDocumentChoice.visualFocus ? 2 : 1
                border.color: wholeDocumentChoice.checked || wholeDocumentChoice.visualFocus ? AppTheme.blue : AppTheme.muted
                Text { anchors.centerIn: parent; visible: wholeDocumentChoice.checked; text: "✓"; color: AppTheme.dark ? "#112650" : "white"; font.pixelSize: 12 }
            }
            contentItem: Text { text: wholeDocumentChoice.text; leftPadding: wholeDocumentChoice.indicator.width + wholeDocumentChoice.spacing; color: wholeDocumentChoice.enabled ? AppTheme.ink : AppTheme.disabled; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter }
            palette.windowText: AppTheme.ink
            ToolTip.visible: hovered; ToolTip.text: "Dịch toàn bộ phần chữ có thể chỉnh sửa. Hình, công thức và phần đang khóa được giữ nguyên."
            onClicked: upload.wholeDocumentToggled(checked)
        }
    }
    DropArea {
        id: drop; objectName: "wordDocumentDrop"; anchors.fill: parent; enabled: !upload.busy
        onEntered: function(event) { event.accepted = event.hasUrls && event.urls.length === 1 }
        onDropped: function(event) {
            if (event.urls.length === 1) { upload.fileDropped(event.urls[0].toString()); event.acceptProposedAction() }
        }
    }
}
