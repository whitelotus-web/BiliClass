import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: home
    required property var bridge
    signal chooseDocument()
    signal continueWork()
    signal openLibrary()
    signal openClassroom()
    signal documentDropped(var urls)
    readonly property bool working: bridge.narrationBusy || bridge.browserState.running
    readonly property var recent: bridge.recentLessons.length ? bridge.recentLessons[0] : ({})
    readonly property var featured: bridge.lesson.id ? bridge.lesson : recent
    spacing: 18
    component Copy: Label { color: "#6e7e92"; font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText; Layout.fillWidth: true }
    RowLayout {
        objectName: "homeWelcomeHero"; Layout.fillWidth: true; spacing: 16
        ColumnLayout { Layout.fillWidth: true; spacing: 7
            Label { text: "Chào " + (home.bridge.settings.teacher || "Thầy cô"); color: "#16314f"; font.pixelSize: 27; font.weight: Font.Bold; wrapMode: Text.WordWrap; Layout.fillWidth: true; textFormat: Text.PlainText }
            Copy { text: "Hôm nay thầy cô muốn chuẩn bị bài hay bắt đầu tiết dạy?"; font.pixelSize: 14 }
        }
        Image { source: home.bridge.settings.mascot === "Lumi" ? "../assets/lumi-welcome.png" : "../assets/milo-welcome.png"; sourceSize.width: 180; Layout.preferredWidth: 72; Layout.preferredHeight: 78; fillMode: Image.PreserveAspectFit; Accessible.name: home.bridge.settings.mascot }
    }
    GridLayout { Layout.fillWidth: true; columns: 2; columnSpacing: 16; rowSpacing: 12
        Rectangle {
            objectName: "homeWorkPanel"; Layout.fillWidth: true; Layout.preferredWidth: 3
            implicitHeight: Math.max(216, focusContent.implicitHeight + 40); radius: 13; color: "white"; border.color: "#d9e4f0"
            Rectangle { width: 4; height: parent.height-40; x: 0; y: 20; radius: 2; color: "#0869f9" }
            ColumnLayout { id: focusContent; anchors.fill: parent; anchors.margins: 20; spacing: 13
                Label { text: home.working ? "ĐANG XỬ LÝ" : home.featured.id ? "TIẾP TỤC VỚI BÀI GIẢNG" : "BẮT ĐẦU BÀI GIẢNG ĐẦU TIÊN"; font.pixelSize: 10; font.letterSpacing: .6; font.weight: Font.DemiBold; color: "#6e7e92" }
                Label { objectName: "homeFeaturedTitle"; text: home.working ? (home.bridge.narrationBusy ? "Giọng đọc đang được chuẩn bị" : "Bài giảng đang chuyển ngữ") : home.featured.title || "Đưa tài liệu vào BiliClass"; color: "#16314f"; font.pixelSize: 21; font.weight: Font.DemiBold; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight; textFormat: Text.PlainText }
                Copy { text: home.working ? "Xem tiến độ hoặc tiếp tục phần đang làm. Các phần đã xong được lưu lại." : home.featured.id ? [home.featured.subject, home.featured.grade ? "Khối " + home.featured.grade : "", "Mở bài để chọn giọng và chuẩn bị dạy"].filter(function(s) { return !!s }).join(" · ") : "Chọn PowerPoint, Word, PDF, văn bản hoặc ảnh; xem lại bản chuyển ngữ trước khi dạy." }
                Item { Layout.fillHeight: true }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    ActionButton { objectName: "homeContinueWork"; primary: true; text: home.working ? "Xem tiến độ" : home.featured.id ? "Mở bài giảng" : "Chọn tài liệu"; enabled: home.working || !home.bridge.busy; onClicked: { if (home.working) home.continueWork(); else if (home.featured.id) home.bridge.openLesson(home.featured.id); else home.chooseDocument() } }
                    ActionButton { objectName: "homeLibraryButton"; text: "Thư viện"; onClicked: home.openLibrary() }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true; Layout.preferredWidth: 2; Layout.fillHeight: true; radius: 13; color: "#edf3fa"
            ColumnLayout { anchors.fill: parent; anchors.margins: 18; spacing: 10
                Label { text: "Thao tác nhanh"; font.pixelSize: 15; font.weight: Font.DemiBold; color: "#16314f" }
                ActionButton { objectName: "homeChooseDocument"; text: "Chuyển đổi tài liệu"; iconName: "upload"; Layout.fillWidth: true; enabled: !home.bridge.busy && !home.working; onClicked: home.chooseDocument() }
                Copy { text: "Hoặc kéo thả tệp vào vùng này."; font.pixelSize: 11 }
                Rectangle { height: 1; Layout.fillWidth: true; color: "#d7e2ef" }
                ActionButton { objectName: "homeClassroomButton"; text: home.bridge.classroomContext.running ? "Trở lại lớp đang mở" : "Hỏi đáp cùng lớp"; iconName: "students"; Layout.fillWidth: true; onClicked: home.openClassroom() }
                Copy { text: home.bridge.classroomContext.running ? (home.bridge.classroomContext.state.joined || 0) + " học sinh đã tham gia" : "Mở QR cho học sinh cùng mạng trả lời câu hỏi."; font.pixelSize: 11 }
            }
            DropArea { anchors.fill: parent; enabled: !home.working && !home.bridge.busy; onDropped: function(drop) { if (drop.hasUrls) { home.documentDropped(drop.urls); drop.acceptProposedAction() } } }
        }
    }
    RowLayout { objectName: "homeLibrarySummary"; Layout.fillWidth: true; spacing: 18
        Copy { text: home.bridge.librarySummary.total + " bài giảng" }
        Copy { text: home.bridge.librarySummary.ready + " bài đã duyệt" }
        Copy { text: home.bridge.librarySummary.voiced + " bài có giọng" }
    }
}
