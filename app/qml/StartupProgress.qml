import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 540; height: 245
    minimumWidth: width; maximumWidth: width
    minimumHeight: height; maximumHeight: height
    title: "BiliClass · Kiểm tra dữ liệu"
    color: "#f6f9fe"
    flags: Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint
    property string operation: "Đang xác minh thư viện"
    property int completed: 0
    property int total: 0
    onClosing: function(close) { close.accepted = false }
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 28; spacing: 15
        Label { text: "BiliClass"; color: "#112650"; font.pixelSize: 26; font.bold: true }
        Label { text: window.operation; color: "#112650"; font.pixelSize: 16; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        ProgressBar { Layout.fillWidth: true; from: 0; to: Math.max(1, window.total); value: window.completed; indeterminate: !window.total }
        Label { text: window.total ? window.completed + " / " + window.total + " tệp đã kiểm tra" : "Đang chuẩn bị…"; color: "#667997" }
        Label { text: "Thư viện sẽ mở sau khi đối chiếu hoàn tất. Dữ liệu gốc vẫn được giữ."; color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    }
}
