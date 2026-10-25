import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    required property var appBridge
    readonly property var word: appBridge.wordDocuments
    property bool trash: false
    signal showPowerPoint()
    signal createWord()
    function folded(value) { return String(value).toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d") }
    onVisibleChanged: if (visible) word.refreshLibrary(trash)
    ColumnLayout {
        anchors.fill: parent; spacing: 12
        RowLayout { Layout.fillWidth: true
            WordAction { objectName: "wordLibraryPowerPoint"; text: "PowerPoint"; onClicked: page.showPowerPoint() }
            WordAction { objectName: "wordLibraryWord"; text: "Word"; primary: true }
            Item { Layout.fillWidth: true }
        }
        RowLayout { Layout.fillWidth: true
            Label { text: page.trash ? "Thùng rác Word" : "Thư viện bài giảng Word"; color: AppTheme.ink; font.pixelSize: 25; font.bold: true; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            WordAction { objectName: "wordLibraryCreate"; text: "Chuyển đổi Word"; primary: true; enabled: !appBridge.busy; onClicked: page.createWord() }
        }
        Label { text: "Bài Word, bản dịch đang chuẩn bị và kết quả song ngữ được lưu riêng tại đây."; color: AppTheme.muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        RowLayout { Layout.fillWidth: true
            TextField { id: search; objectName: "wordLibrarySearch"; placeholderText: "Tìm bài Word, môn học…"; color: AppTheme.ink; Layout.fillWidth: true; implicitHeight: 40
                background: Rectangle { color: AppTheme.field; radius: 8; border.color: AppTheme.line } }
            WordAction { objectName: "wordLibraryRefresh"; text: "Làm mới"; enabled: !appBridge.busy; onClicked: page.word.refreshLibrary(page.trash) }
            WordAction { objectName: "wordLibraryTrash"; text: page.trash ? "Về thư viện" : "Thùng rác Word"; enabled: !appBridge.busy; onClicked: { page.trash = !page.trash; page.word.refreshLibrary(page.trash) } }
        }
        ListView {
            id: records; objectName: "wordLibraryList"; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 10
            model: page.word.library.filter(function(row) { return page.folded(row.title + " " + row.subject).indexOf(page.folded(search.text)) >= 0 })
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            delegate: Rectangle {
                id: documentRow; required property var modelData; required property int index
                width: ListView.view.width - 12; height: contents.implicitHeight + 26; radius: 11; color: AppTheme.surface; border.color: AppTheme.line
                ColumnLayout { id: contents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 13; spacing: 8
                    Label { text: documentRow.modelData.title; color: AppTheme.ink; font.bold: true; font.pixelSize: 16; textFormat: Text.PlainText; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Label { text: (documentRow.modelData.subject || "Word") + " · " + (documentRow.modelData.phase === "completed" ? "Đã lưu song ngữ" : documentRow.modelData.phase === "review" ? "Chờ xem và lưu" : "Đang chuẩn bị / có thể tiếp tục"); color: AppTheme.muted; font.pixelSize: 12 }
                    Flow { Layout.fillWidth: true; spacing: 8
                        WordAction { text: "Xem / tiếp tục"; visible: !page.trash; primary: true; enabled: !page.appBridge.busy; onClicked: page.word.loadRecord(documentRow.modelData.id) }
                        WordAction { text: "Mở Word"; visible: !page.trash && !!documentRow.modelData.output_sha256; enabled: !page.appBridge.busy; onClicked: page.word.openOutput(documentRow.modelData.id) }
                        WordAction { text: "Mở thư mục"; visible: !page.trash; enabled: !page.appBridge.busy; onClicked: page.word.openFolder(documentRow.modelData.id) }
                        WordAction { text: page.trash ? "Khôi phục" : "Đưa vào thùng rác"; danger: !page.trash; enabled: !page.appBridge.busy; onClicked: page.word.trash(documentRow.modelData.id, !page.trash) }
                    }
                }
            }
            Label { anchors.centerIn: parent; visible: records.count === 0; text: page.trash ? "Thùng rác Word đang trống" : "Chưa có tài liệu Word phù hợp"; color: AppTheme.muted; font.pixelSize: 16 }
        }
    }
}
