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
    readonly property bool working: bridge.narrationBusy || !!bridge.browserState.running
    readonly property var recent: bridge.recentLessons.length ? bridge.recentLessons[0] : ({})
    readonly property var featured: bridge.lesson.id ? bridge.lesson : recent
    readonly property bool wide: width >= 1000
    spacing: 18

    component Copy: Label {
        color: "#687e9b"; font.pixelSize: 12; wrapMode: Text.WordWrap
        textFormat: Text.PlainText; Layout.fillWidth: true
    }

    Rectangle {
        objectName: "homeWelcomeHero"
        Layout.fillWidth: true
        implicitHeight: home.wide ? 280 : 244
        radius: 22; clip: true; color: "#f2f8ff"
        Canvas {
            anchors.fill: parent
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle = "#e7f2ff"
                ctx.beginPath(); ctx.moveTo(0, height)
                ctx.bezierCurveTo(width * 0.18, height * 0.76, width * 0.4, height * 0.98, width * 0.56, height * 0.3)
                ctx.bezierCurveTo(width * 0.75, -height * 0.3, width * 0.82, height * 0.24, width, 0)
                ctx.lineTo(width, height); ctx.closePath(); ctx.fill()
                ctx.fillStyle = "#dcecff"
                ctx.beginPath(); ctx.moveTo(width * 0.62, height)
                ctx.bezierCurveTo(width * 0.83, height * 0.72, width * 0.8, height * 0.87, width, height * 0.58)
                ctx.lineTo(width, height); ctx.closePath(); ctx.fill()
            }
        }
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: home.wide ? 32 : 24
            anchors.rightMargin: 14; spacing: 6
            ColumnLayout {
                Layout.fillWidth: true; spacing: 14
                Label {
                    objectName: "homeHeroTitle"
                    text: "Chào Thầy cô!"; color: "#102c56"
                    font.pixelSize: home.wide ? 43 : 35; font.weight: Font.Bold
                    font.letterSpacing: -1; Layout.fillWidth: true
                }
                Rectangle { width: 46; height: 4; radius: 2; color: "#ff891c" }
                Copy {
                    text: "Chuyển tài liệu thành bài giảng Việt–Anh hoặc tiếng Anh, kèm giọng đọc và mascot đồng hành khi dạy."
                    color: "#355478"; font.pixelSize: home.wide ? 17 : 15
                    lineHeight: 1.35; Layout.maximumWidth: 600
                }
            }
            Item {
                id: heroArt
                Layout.preferredWidth: Math.max(280, Math.min(410, home.width * 0.38))
                Layout.fillHeight: true
                Rectangle {
                    objectName: "homeMascotSpeech"
                    x: -20; y: home.wide ? 36 : 24
                    width: Math.min(166, heroArt.width * 0.47); height: home.wide ? 100 : 88
                    radius: 20; color: "#ffffff"; border.color: "#ccdef7"; border.width: 2
                    rotation: -5
                    Label {
                        anchors.fill: parent; anchors.margins: 11
                        text: "Cùng thầy cô\nbiến mỗi bài giảng\nthành trải nghiệm\nsong ngữ thú vị."
                        font.pixelSize: home.wide ? 14 : 12; font.weight: Font.DemiBold
                        color: "#0869f9"; horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter; lineHeight: 1.2
                    }
                }
                Image {
                    objectName: "homeHeroMascot"
                    anchors.right: parent.right; anchors.rightMargin: 4
                    anchors.bottom: parent.bottom; anchors.bottomMargin: 4
                    width: heroArt.width * 0.68; height: parent.height - 16
                    source: home.bridge.settings.mascot === "Lumi" ? "../assets/lumi-welcome.png" : "../assets/milo-welcome.png"
                    sourceSize.width: 700; fillMode: Image.PreserveAspectFit
                    Accessible.name: home.bridge.settings.mascot + " chào thầy cô"
                }
            }
        }
    }

    Rectangle {
        id: upload
        objectName: "homeUploadZone"
        Layout.fillWidth: true; implicitHeight: home.wide ? 184 : 170
        radius: 16; color: uploadDrop.containsDrag ? "#eaf3ff" : "white"
        border.width: uploadDrop.containsDrag ? 2 : 1
        border.color: uploadDrop.containsDrag ? "#0869f9" : "#bed6fa"
        RowLayout {
            anchors.centerIn: parent; width: Math.min(parent.width - 48, 780); spacing: home.wide ? 32 : 24
            Item {
                Layout.preferredWidth: home.wide ? 120 : 96; Layout.preferredHeight: 112
                Rectangle { x: 18; y: 8; width: 78; height: 98; radius: 9; color: "#e7f0ff"; rotation: 9 }
                Rectangle {
                    x: 8; y: 2; width: 78; height: 98; radius: 8
                    color: "#fffdfb"; border.color: "#e4eaf4"; rotation: -7
                    Rectangle { x: 18; y: 68; width: 42; height: 3; radius: 1; color: "#dee6f1" }
                    Rectangle { x: 18; y: 77; width: 32; height: 3; radius: 1; color: "#dee6f1" }
                    Rectangle {
                        x: -8; y: 25; width: 70; height: 34; radius: 6; color: "#f47b28"
                        Label { anchors.centerIn: parent; text: "PPTX"; color: "white"; font.pixelSize: 19; font.weight: Font.Bold }
                    }
                }
            }
            ColumnLayout {
                Layout.fillWidth: true; spacing: 9
                Label {
                    text: home.working ? "Bài giảng đang được chuẩn bị" : "Đưa bài giảng vào BiliClass"; color: "#0869f9"
                    font.pixelSize: home.wide ? 23 : 20; font.weight: Font.Bold
                    Layout.fillWidth: true; wrapMode: Text.WordWrap
                }
                Copy { text: home.working ? "Theo dõi tiến độ; các phần đã xong được lưu lại." : "Kéo thả tài liệu vào đây hoặc bấm để chọn tệp."; font.pixelSize: 13 }
                ActionButton {
                    id: uploadAction
                    objectName: "homeChooseDocument"; text: home.working ? "Xem tiến độ" : "Chọn tài liệu"
                    primary: true; implicitHeight: 44; Layout.preferredWidth: 224; font.pixelSize: 14
                    enabled: home.working || !home.bridge.busy
                    onClicked: home.working ? home.continueWork() : home.chooseDocument()
                    contentItem: RowLayout {
                        spacing: 9
                        Item { Layout.fillWidth: true }
                        Canvas {
                            Layout.preferredWidth: 20; Layout.preferredHeight: 20
                            property bool active: uploadAction.enabled
                            onActiveChanged: requestPaint()
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.clearRect(0, 0, width, height)
                                ctx.strokeStyle = active ? "white" : "#96a6bc"
                                ctx.lineWidth = 1.7; ctx.lineJoin = "round"; ctx.lineCap = "round"
                                ctx.beginPath(); ctx.moveTo(10, 13); ctx.lineTo(10, 3)
                                ctx.moveTo(6, 7); ctx.lineTo(10, 3); ctx.lineTo(14, 7)
                                ctx.moveTo(4, 12); ctx.lineTo(4, 17); ctx.lineTo(16, 17); ctx.lineTo(16, 12)
                                ctx.stroke()
                            }
                        }
                        Label { text: uploadAction.text; font: uploadAction.font; color: uploadAction.enabled ? "white" : "#96a6bc" }
                        Item { Layout.fillWidth: true }
                    }
                }
                Copy { text: "PowerPoint · Word · PDF · Văn bản · Ảnh"; font.pixelSize: 11 }
            }
        }
        DropArea {
            id: uploadDrop; objectName: "homeUploadDrop"
            anchors.fill: parent; enabled: !home.working && !home.bridge.busy
            onDropped: function(drop) {
                if (drop.hasUrls) { home.documentDropped(drop.urls); drop.acceptProposedAction() }
            }
        }
    }

    ColumnLayout {
        objectName: "homeWorkflow"; Layout.fillWidth: true; spacing: 12
        Label { text: "Từ tài liệu đến tiết dạy"; color: "#16314f"; font.pixelSize: 17; font.weight: Font.DemiBold }
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    {title: "Chọn tài liệu", detail: "PowerPoint, Word, PDF hoặc ảnh", icon: "upload"},
                    {title: "Chọn cách dịch", detail: "Việt–Anh hoặc tiếng Anh", icon: "refresh"},
                    {title: "Xem & tạo giọng", detail: "Kiểm tra bài, giọng tùy chọn", icon: "view"},
                    {title: "Sẵn sàng dạy", detail: "Mở PowerPoint cùng mascot", icon: "play"}
                ]
                Rectangle {
                    required property var modelData
                    required property int index
                    Layout.fillWidth: true; Layout.preferredWidth: 1
                    implicitHeight: 128; radius: 12; color: "white"; border.color: "#dce7f5"
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 13; spacing: 7
                        RowLayout {
                            Layout.fillWidth: true
                            Rectangle {
                                width: 24; height: 24; radius: 12; color: "#eaf3ff"
                                Label { anchors.centerIn: parent; text: index + 1; color: "#0869f9"; font.weight: Font.DemiBold; font.pixelSize: 12 }
                            }
                            Item { Layout.fillWidth: true }
                            Image { source: "../assets/actions/" + modelData.icon + ".png"; sourceSize.width: 64; Layout.preferredWidth: 26; Layout.preferredHeight: 26; fillMode: Image.PreserveAspectFit }
                        }
                        Label { text: modelData.title; color: "#16314f"; font.pixelSize: 14; font.weight: Font.DemiBold; Layout.fillWidth: true }
                        Copy { text: modelData.detail; font.pixelSize: 12; Layout.fillHeight: true; verticalAlignment: Text.AlignTop }
                    }
                }
            }
        }
    }

    Rectangle {
        objectName: "homeWorkPanel"; visible: home.working || !!home.featured.id
        Layout.fillWidth: true; implicitHeight: Math.max(94, focusContent.implicitHeight + 30)
        radius: 13; color: "#edf4fd"
        RowLayout {
            id: focusContent; anchors.fill: parent; anchors.margins: 15; spacing: 14
            ColumnLayout {
                Layout.fillWidth: true; spacing: 5
                Label { text: home.working ? "ĐANG XỬ LÝ" : "TIẾP TỤC CHUẨN BỊ"; color: "#687e9b"; font.pixelSize: 10; font.letterSpacing: .5; font.weight: Font.DemiBold }
                Label {
                    objectName: "homeFeaturedTitle"
                    text: home.working ? (home.bridge.narrationBusy ? "Giọng đọc đang được chuẩn bị" : "Bài giảng đang chuyển ngữ") : home.featured.title || "Bài giảng đang mở"
                    color: "#16314f"; font.pixelSize: 17; font.weight: Font.DemiBold
                    Layout.fillWidth: true; elide: Text.ElideRight; textFormat: Text.PlainText
                }
                Copy { text: home.working ? "Các phần đã xong được lưu lại." : [home.featured.subject, home.featured.grade ? "Khối " + home.featured.grade : ""].filter(function(s) { return !!s }).join(" · "); font.pixelSize: 11 }
            }
            ActionButton {
                objectName: "homeContinueWork"; text: home.working ? "Xem tiến độ" : "Mở bài giảng"; primary: true
                enabled: home.working || !home.bridge.busy
                onClicked: { if (home.working) home.continueWork(); else home.bridge.openLesson(home.featured.id) }
            }
            ActionButton { objectName: "homeLibraryButton"; text: "Thư viện"; onClicked: home.openLibrary() }
            ActionButton { objectName: "homeClassroomButton"; text: home.bridge.classroomContext.running ? "Lớp đang mở" : "Vào lớp"; onClicked: home.openClassroom() }
        }
    }
    RowLayout {
        objectName: "homeLibrarySummary"; Layout.fillWidth: true; spacing: 18
        Copy { text: home.bridge.librarySummary.total + " bài giảng" }
        Copy { text: home.bridge.librarySummary.ready + " bài đã duyệt" }
        Copy { text: home.bridge.librarySummary.voiced + " bài có giọng" }
    }
}
