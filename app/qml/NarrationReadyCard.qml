import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property string summary: ""
    property int total: 0
    property var coverage: ({})
    property bool busy: false
    signal openPowerPoint()
    signal checkPreview()
    signal downloadPresentation()
    signal downloadAudio()
    signal showInLibrary()
    radius: 10; color: "#eef8f4"; border.color: "#d2eade"
    implicitHeight: content.implicitHeight + 28
    ColumnLayout {
        id: content
        anchors.fill: parent; anchors.margins: 14; spacing: 10
        Label {
            objectName: "narrationCompletionTitle"
            text: "✓ Giọng đọc đã hoàn tất và lưu vào Bài giảng"
            color: "#168567"; font.pixelSize: 14; font.weight: Font.DemiBold
            Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            text: card.summary + " · " + card.total + "/" + card.total + " đoạn sẵn sàng"
            color: "#112650"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            text: (card.coverage.total ? card.coverage.readable + "/" + card.coverage.total + " slide có lời đọc · " : "") + "Loa đọc toàn bộ lời đã lưu của slide khi bấm, kể cả phần xuất hiện sau. Không tự phát theo hiệu ứng."
            color: "#667997"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            visible: (card.coverage.missing || 0) > 0 || (card.coverage.silent || 0) > 0
            text: (card.coverage.missing ? card.coverage.missing + " slide chưa có lời cho ngôn ngữ đã chọn. " : "") + (card.coverage.silent ? card.coverage.silent + " slide đã chọn không đọc." : "")
            color: "#a66318"; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Flow {
            Layout.fillWidth: true; spacing: 10
            ActionButton { objectName: "continueAfterNarrationButton"; text: "Mở PowerPoint"; primary: true; enabled: !card.busy; onClicked: card.openPowerPoint() }
            ActionButton { objectName: "checkCompletedNarrationButton"; text: "Kiểm tra slide và giọng"; enabled: !card.busy; onClicked: card.checkPreview() }
            ActionButton { objectName: "downloadAfterNarrationButton"; text: "Tải PowerPoint"; iconName: "download"; enabled: !card.busy; onClicked: card.downloadPresentation() }
            ActionButton { objectName: "downloadNarrationAudioButton"; text: "Tải audio (.zip)"; enabled: !card.busy; onClicked: card.downloadAudio() }
        }
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            ActionButton { objectName: "viewCompletedNarrationInLibrary"; text: "Xem trong Bài giảng"; enabled: !card.busy; onClicked: card.showInLibrary() }
        }
    }
}
