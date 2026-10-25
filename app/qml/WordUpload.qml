import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: upload
    property bool busy: false
    property bool reading: false
    signal chooseFile()
    signal fileDropped(string url)
    implicitHeight: content.implicitHeight + 28
    radius: 16; color: drop.containsDrag ? AppTheme.selected : AppTheme.surface
    border.color: drop.containsDrag ? AppTheme.blue : AppTheme.line
    border.width: drop.containsDrag ? 2 : 1
    RowLayout {
        id: content; anchors.horizontalCenter: parent.horizontalCenter; anchors.top: parent.top; anchors.topMargin: 14
        width: Math.min(parent.width - 44, 840); spacing: 24
        Image {
            source: "../assets/actions/document-word.svg"; fillMode: Image.PreserveAspectFit
            sourceSize.width: 128; sourceSize.height: 144
            Layout.preferredWidth: 220; Layout.preferredHeight: 110
            Accessible.ignored: true
        }
        ColumnLayout {
            Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 7
            Label { text: upload.reading ? "Đang đọc tài liệu Word…" : upload.busy ? "Đang có tác vụ khác" : "Tải lên bài giảng Word (.docx)"; color: AppTheme.blue; font.pixelSize: 19; font.bold: true; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
            Label { text: "Chọn hoặc kéo thả một file. Sau đó chọn những câu, đoạn cần dịch."; color: AppTheme.muted; font.pixelSize: 13; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
            WordAction { objectName: "wordUploadChoose"; text: upload.busy ? "Chờ hoàn tất tác vụ…" : "Chọn file Word"; primary: true; implicitHeight: 44; font.pixelSize: 14; Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: 258; enabled: !upload.busy; onClicked: upload.chooseFile() }
            Label { text: "Chỉ hỗ trợ tệp .docx tối đa 50 MB · Giữ nguyên file gốc"; color: AppTheme.muted; font.pixelSize: 12; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
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
