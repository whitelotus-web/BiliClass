import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: win
    visible: true
    width: 1366; height: 768
    minimumWidth: 980; minimumHeight: 650
    title: "BiliClass · M0 Workbench"
    color: "#F5F8FD"
    property int pageIndex: 0
    readonly property color ink: "#102A50"
    readonly property color muted: "#64748B"
    readonly property color blue: "#1266E8"
    readonly property color line: "#E0E8F2"

    function status(key) {
        var r = bridge.reports[key]
        if (!r) return "Chưa chạy"
        if (r.status === "passed" || r.status === "measured") return "Đã kiểm chứng local"
        if (r.status === "review_required") return "Cần duyệt chất lượng"
        if (r.status === "needs_setup") return "Cần bổ sung gói"
        return "Cần xử lý"
    }
    function statusColor(key) {
        var r = bridge.reports[key]
        if (!r) return win.muted
        if (r.status === "passed" || r.status === "measured") return "#25815F"
        if (r.status === "failed") return "#BC3F42"
        return "#A36715"
    }
    component ActionButton: Button {
        id: button
        property bool primary: false
        implicitHeight: 42
        leftPadding: 18; rightPadding: 18
        font.pixelSize: 13; font.weight: Font.DemiBold
        background: Rectangle {
            radius: 10
            color: button.primary ? (button.hovered ? "#0756CD" : win.blue) : (button.hovered ? "#EEF5FF" : "white")
            border.color: button.primary ? color : win.line
            opacity: button.enabled ? 1 : 0.55
        }
        contentItem: Text {
            text: button.text; font: button.font
            color: button.primary ? "white" : win.ink
            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
            opacity: button.enabled ? 1 : 0.5
        }
    }
    component Panel: Rectangle { color: "white"; radius: 16; border.color: win.line }
    component Caption: Text { color: win.muted; font.pixelSize: 12; wrapMode: Text.WordWrap }
    component Body: Text { color: win.ink; font.pixelSize: 14; wrapMode: Text.WordWrap; lineHeight: 1.35 }
    component SectionTitle: Text { color: win.ink; font.pixelSize: 19; font.weight: Font.Bold }

    Rectangle {
        id: sidebar
        width: 210; height: parent.height; color: "#FFFFFF"
        Rectangle { anchors.right: parent.right; height: parent.height; width: 1; color: win.line }
        Column {
            x: 26; y: 32; spacing: 5
            Text { text: "Bili<span style='color:#F48235'>Class</span>"; textFormat: Text.RichText; color: win.ink; font.pixelSize: 31; font.weight: Font.Bold }
            Text { text: "TEACH MORE. REACH FURTHER."; color: win.muted; font.pixelSize: 8; font.letterSpacing: 1 }
        }
        Column {
            x: 16; y: 135; width: parent.width - 32; spacing: 7
            Repeater {
                model: ["Tổng quan", "Thử song ngữ", "Sẵn sàng giảng dạy"]
                delegate: Rectangle {
                    required property int index
                    required property string modelData
                    width: parent.width; height: 48; radius: 10
                    color: win.pageIndex === index ? "#EAF3FF" : navArea.containsMouse ? "#F5F8FD" : "transparent"
                    Row {
                        x: 15; anchors.verticalCenter: parent.verticalCenter; spacing: 13
                        Text { text: ["◫", "文", "✓"][index]; font.pixelSize: 20; color: win.pageIndex === index ? win.blue : win.muted }
                        Text { text: modelData; font.pixelSize: 13; font.weight: Font.DemiBold; color: win.pageIndex === index ? win.blue : win.muted; anchors.verticalCenter: parent.verticalCenter }
                    }
                    MouseArea { id: navArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.pageIndex = index }
                }
            }
        }
        Rectangle {
            x: 18; width: parent.width - 36; height: 120; anchors.bottom: bottomNote.top; anchors.bottomMargin: 24
            color: "#F5F8FD"; radius: 12
            Column {
                anchors.fill: parent; anchors.margins: 15; spacing: 10
                Text { text: "M0 / WORKBENCH"; color: win.blue; font.pixelSize: 10; font.weight: Font.Bold; font.letterSpacing: 1 }
                Caption { width: parent.width; text: "Bản thử kỹ thuật trước khi xây ứng dụng đầy đủ." }
                Text { text: "Kết quả thực · Giới hạn rõ"; color: win.ink; font.pixelSize: 10 }
            }
        }
        Caption { id: bottomNote; x: 25; width: 160; anchors.bottom: parent.bottom; anchors.bottomMargin: 28; text: "ANH–VIỆT · ĐA MÔN\nDữ liệu được xử lý tại máy."; font.pixelSize: 10; lineHeight: 1.5 }
    }

    ColumnLayout {
        anchors.left: sidebar.right; anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: footer.top
        anchors.margins: 30; spacing: 22
        RowLayout {
            Layout.fillWidth: true
            Text { text: "KHÔNG GIAN KIỂM CHỨNG"; color: win.muted; font.pixelSize: 10; font.weight: Font.DemiBold; font.letterSpacing: 1.5 }
            Item { Layout.fillWidth: true }
            Rectangle {
                implicitWidth: 122; implicitHeight: 28; radius: 14; color: "#E7F5EF"
                Text { anchors.centerIn: parent; text: "●  Xử lý tại máy"; color: "#23825B"; font.pixelSize: 11 }
            }
            ActionButton { text: "Mở kết quả  ↗"; implicitHeight: 34; onClicked: bridge.openReports() }
        }

        StackLayout {
            currentIndex: win.pageIndex; Layout.fillWidth: true; Layout.fillHeight: true
            ScrollView {
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.width; spacing: 20
                    RowLayout {
                        Layout.fillWidth: true; spacing: 22
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 12
                            Text { text: "Một bài giảng.\nNhiều cách tiếp cận."; color: win.ink; font.pixelSize: 32; font.weight: Font.Bold; lineHeight: 1.08 }
                            Body { Layout.maximumWidth: 530; Layout.fillWidth: true; text: "Kiểm chứng nền tảng để thầy cô đưa tiếng Anh vào bài học, theo cách mình kiểm soát."; color: win.muted }
                            Row { spacing: 10; Layout.topMargin: 6
                                ActionButton { text: "Thử lớp nội dung song ngữ  →"; primary: true; onClicked: win.pageIndex = 1 }
                                ActionButton { text: "Giọng đọc"; enabled: !bridge.busy; onClicked: bridge.runProbe("tts") }
                            }
                        }
                        Rectangle {
                            Layout.preferredWidth: 252; Layout.preferredHeight: 182; radius: 20; color: "#102D55"
                            Rectangle { x: 143; y: 15; width: 95; height: 95; radius: 48; color: "#1B3C65" }
                            Rectangle { x: 195; y: 142; width: 50; height: 50; radius: 25; color: "#F7B772" }
                            Column {
                                x: 24; y: 24; spacing: 13
                                Text { text: "CÙNG MỘT LỚP HỌC"; color: "#A7C3E7"; font.pixelSize: 9; font.letterSpacing: 1.4 }
                                Text { text: "Anh  ↔  Việt"; color: "white"; font.pixelSize: 28; font.weight: Font.Bold }
                                Rectangle { width: 54; height: 3; radius: 2; color: "#FFAB63" }
                                Text { text: "Môn học linh hoạt\nGiáo viên quyết định"; color: "#C1D4EA"; font.pixelSize: 12; lineHeight: 1.5 }
                            }
                        }
                    }
                    RowLayout { Layout.topMargin: 9; Layout.fillWidth: true
                        SectionTitle { text: "Bốn nền tảng cần kiểm chứng" }
                        Item { Layout.fillWidth: true }
                        Caption { text: "Kết quả local ≠ nghiệm thu thực địa" }
                    }
                    GridLayout {
                        Layout.fillWidth: true; columns: 2; rowSpacing: 14; columnSpacing: 14
                        Repeater {
                            model: [
                                {key:"powerpoint", label:"PowerPoint & cửa sổ nổi", n:"01", detail:"Đọc slide đang chiếu, giữ nguyên nguồn và thử chuyển trang.", action:"Thử PowerPoint"},
                                {key:"translation", label:"Dịch & phát âm ngoại tuyến", n:"02", detail:"60 ca hai chiều, nhiều nhóm môn. Đo CPU, bộ nhớ và chất lượng.", action:"Đo bộ dịch"},
                                {key:"lan", label:"Kết nối lớp học", n:"03", detail:"50 client mô phỏng, gửi lại đáp án và kết nối lại phiên.", action:"Thử máy chủ"},
                                {key:"qt", label:"Giao diện & bản Windows", n:"04", detail:"QML, tiếng Việt, ảnh chụp cửa sổ và bản chạy đóng gói.", action:"Xem kết quả"}
                            ]
                            delegate: Panel {
                                required property var modelData
                                Layout.fillWidth: true; Layout.preferredHeight: 146
                                ColumnLayout { anchors.fill: parent; anchors.margins: 18; spacing: 8
                                    RowLayout { Layout.fillWidth: true
                                        Text { text: modelData.n; color: win.blue; font.pixelSize: 11; font.weight: Font.Bold }
                                        Text { text: modelData.label; color: win.ink; font.pixelSize: 14; font.weight: Font.DemiBold }
                                        Item { Layout.fillWidth: true }
                                    }
                                    Caption { Layout.fillWidth: true; text: modelData.detail }
                                    Item { Layout.fillHeight: true }
                                    RowLayout { Layout.fillWidth: true
                                        Text { text: win.status(modelData.key); color: win.statusColor(modelData.key); font.pixelSize: 10 }
                                        Item { Layout.fillWidth: true }
                                        ActionButton { text: modelData.action; implicitHeight: 33; font.pixelSize: 11; enabled: !bridge.busy
                                            onClicked: modelData.key === "qt" ? bridge.openReports() : bridge.runProbe(modelData.key) }
                                    }
                                }
                            }
                        }
                    }
                    Caption { Layout.fillWidth: true; text: "M0 kiểm tra khả năng triển khai. Chưa thay thế kiểm thử trên laptop 8 GB, điện thoại và máy chiếu của lớp học." }
                }
            }
            ScrollView {
                clip: true; contentWidth: availableWidth; ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ColumnLayout {
                    width: parent.width; spacing: 18
                    SectionTitle { text: "Lớp nội dung Anh–Việt"; font.pixelSize: 27 }
                    Body { Layout.fillWidth: true; text: "Thử một đoạn bất kỳ và xem quy tắc L0–L5. Đây là bản dịch nháp để kiểm chứng engine."; color: win.muted }
                    Panel {
                        Layout.fillWidth: true; Layout.preferredHeight: 265
                        RowLayout { anchors.fill: parent; anchors.margins: 20; spacing: 22
                            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 1
                                RowLayout { Layout.fillWidth: true
                                    Text { text: "NỘI DUNG NGUỒN"; color: win.muted; font.pixelSize: 10; font.weight: Font.Bold }
                                    Item { Layout.fillWidth: true }
                                    ComboBox { id: direction; model: ["VI → EN", "EN → VI"]; implicitHeight: 34; implicitWidth: 110 }
                                }
                                ScrollView { Layout.fillWidth: true; Layout.fillHeight: true
                                    TextArea { id: sourceText; text: "Các em hãy thảo luận theo nhóm và giải thích câu trả lời của mình."; wrapMode: TextEdit.Wrap; font.pixelSize: 17; color: win.ink; padding: 12
                                        background: Rectangle { radius: 10; color: "#F6F9FD"; border.color: win.line } }
                                }
                                ActionButton { text: bridge.busy ? "Đang xử lý…" : "Dịch thử tại máy  →"; primary: true; enabled: !bridge.busy; onClicked: bridge.translate(sourceText.text, direction.currentIndex === 0 ? "vi" : "en") }
                            }
                            Rectangle { Layout.fillHeight: true; implicitWidth: 1; color: win.line }
                            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 1
                                Text { text: "BẢN DỊCH NHÁP"; color: win.blue; font.pixelSize: 10; font.weight: Font.Bold }
                                TextArea { Layout.fillWidth: true; Layout.fillHeight: true; readOnly: true; text: bridge.translation || "Bản dịch sẽ xuất hiện ở đây."; wrapMode: TextEdit.Wrap; font.pixelSize: 18; color: bridge.translation ? win.ink : "#93A0B3"; padding: 4; background: null }
                                Caption { Layout.fillWidth: true; text: "Kết quả model thô · Cần duyệt thuật ngữ và ý nghĩa." }
                            }
                        }
                    }
                    Panel { Layout.fillWidth: true; Layout.preferredHeight: 186
                        ColumnLayout { anchors.fill: parent; anchors.margins: 20; spacing: 13
                            RowLayout { Layout.fillWidth: true
                                SectionTitle { text: "Mức hỗ trợ tiếng Anh"; font.pixelSize: 16 }
                                Item { Layout.fillWidth: true }
                                Text { text: bridge.policy.name; color: win.blue; font.pixelSize: 13; font.weight: Font.DemiBold }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 8
                                Repeater { model: 6
                                    delegate: ActionButton { required property int index; text: "L" + index; Layout.fillWidth: true; primary: bridge.policy.level === index; onClicked: bridge.setLevel(index) }
                                }
                            }
                            Body { Layout.fillWidth: true; font.pixelSize: 13
                                text: "Ngôn ngữ chính: " + (bridge.policy.primary_language === "vi" ? "Tiếng Việt" : bridge.policy.primary_language === "en" ? "Tiếng Anh" : "Đan xen VI/EN")
                                      + "   ·   Giải thích EN: " + (bridge.policy.explanation_en ? "Có" : "Ẩn")
                                      + "   ·   VI Rescue: Sẵn sàng khi đã chuẩn bị nội dung" }
                            Caption { text: "Level chọn loại nội dung. Cách bố trí slide là thiết lập độc lập." }
                        }
                    }
                    Row { spacing: 10
                        ActionButton { text: "Nghe thử giọng EN"; onClicked: bridge.playEnglish() }
                        ActionButton { text: "Thử lớp nổi"; onClicked: overlay.visible = !overlay.visible }
                    }
                }
            }
            ScrollView {
                clip: true; contentWidth: availableWidth; ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ColumnLayout { width: parent.width; spacing: 18
                    SectionTitle { text: "Sẵn sàng trước khi đứng lớp"; font.pixelSize: 27 }
                    Body { Layout.fillWidth: true; text: "Các khả năng trên máy được kiểm tra riêng với trạng thái duyệt bài. M0 chưa có Lesson Pack để xác nhận bài sẵn sàng dạy."; color: win.muted }
                    Panel { Layout.fillWidth: true; Layout.preferredHeight: 350
                        ColumnLayout { anchors.fill: parent; anchors.margins: 23; spacing: 0
                            Repeater {
                                model: [
                                    {title:"Nguồn và bản dịch đã duyệt", detail:"Sẽ có trong luồng Lesson Builder M2–M3.", ok:false},
                                    {title:"Giọng đọc tiếng Anh", detail: bridge.reports.tts ? ("Đã tìm thấy " + bridge.reports.tts.voices.length + " giọng SAPI; xem báo cáo ngôn ngữ.") : "Chưa kiểm tra giọng được cài trên máy.", ok:bridge.reports.tts && bridge.reports.tts.status === "passed"},
                                    {title:"Âm thanh đã chuẩn bị", detail:"M0 tạo câu đọc thử; cache theo nội dung từng bài triển khai ở M4.", ok:false},
                                    {title:"Bài có thể dạy khi không có quiz", detail:"Mạng và câu hỏi chỉ cần khi giáo viên chọn kiểm tra lớp.", ok:true},
                                    {title:"Mạng lớp học thực tế", detail:"Cần điện thoại thật để xác nhận kết nối qua Wi-Fi/router.", ok:false}
                                ]
                                delegate: Item { required property var modelData; Layout.fillWidth: true; Layout.fillHeight: true
                                    RowLayout { anchors.fill: parent; spacing: 17
                                        Rectangle { implicitWidth: 28; implicitHeight: 28; radius: 14; color: modelData.ok ? "#E6F5EE" : "#FFF3E5"
                                            Text { anchors.centerIn: parent; text: modelData.ok ? "✓" : "·"; color: modelData.ok ? "#21845B" : "#B67823"; font.pixelSize: 17 }
                                        }
                                        ColumnLayout { Layout.fillWidth: true; spacing: 5
                                            Text { text: modelData.title; color: win.ink; font.pixelSize: 14; font.weight: Font.DemiBold }
                                            Caption { Layout.fillWidth: true; text: modelData.detail }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    Row { spacing: 10
                        ActionButton { text: "Kiểm tra giọng đọc"; primary: true; enabled: !bridge.busy; onClicked: bridge.runProbe("tts") }
                        ActionButton { text: "Xem báo cáo chi tiết"; onClicked: bridge.openReports() }
                    }
                }
            }
        }
    }
    Rectangle {
        id: footer; height: 45; anchors.bottom: parent.bottom; anchors.left: sidebar.right; anchors.right: parent.right
        color: "white"
        Rectangle { width: parent.width; height: 1; color: win.line }
        RowLayout { anchors.fill: parent; anchors.leftMargin: 30; anchors.rightMargin: 30; spacing: 12
            BusyIndicator { running: bridge.busy; visible: running; implicitWidth: 20; implicitHeight: 20 }
            Text { Layout.fillWidth: true; text: bridge.message; color: win.muted; font.pixelSize: 11; elide: Text.ElideRight }
            Text { text: "M0 · 0.0.1"; color: win.muted; font.pixelSize: 10 }
        }
    }
    Window {
        id: overlay; objectName: "companionOverlay"; visible: false; width: 350; height: 150; color: "transparent"
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        x: win.x + win.width - width - 30; y: win.y + win.height - height - 70
        Rectangle { anchors.fill: parent; anchors.margins: 4; radius: 18; color: "#F9FCFF"; border.color: "#BFD6F3"; border.width: 2
            Column { x: 20; y: 17; width: parent.width - 60; spacing: 8
                Text { text: "BiliClass · lớp nổi thử nghiệm"; color: win.blue; font.pixelSize: 11; font.weight: Font.Bold }
                Text { width: parent.width; text: "Please explain your answer.\nHãy giải thích câu trả lời của em."; wrapMode: Text.WordWrap; color: win.ink; font.pixelSize: 15; lineHeight: 1.4 }
                Text { text: "Kéo để di chuyển"; color: win.muted; font.pixelSize: 10 }
            }
            DragHandler { target: null; onActiveChanged: if (active) overlay.startSystemMove() }
            Button { text: "×"; width: 28; height: 28; anchors.right: parent.right; anchors.rightMargin: 8; y: 7; onClicked: overlay.visible = false }
        }
    }
}
