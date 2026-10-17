import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: home
    required property var bridge
    property string inputError: ""
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
                    text: "Chuyển PowerPoint thành bài giảng Việt–Anh hoặc tiếng Anh, kèm giọng đọc và mascot đồng hành khi dạy."
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

    ColumnLayout {
        objectName: "homeWorkflow"; Layout.fillWidth: true; spacing: 12
        Label { objectName: "homeWorkflowHeading"; text: "Quy trình đơn giản"; color: "#16314f"; font.pixelSize: 19; font.weight: Font.DemiBold }
        RowLayout {
            Layout.fillWidth: true; spacing: home.width > 1000 ? 12 : 8
            Repeater {
                model: [
                    {title: "Tải bài giảng", detail: "Chọn file PowerPoint\ntiếng Việt", icon: "upload", box: Qt.rect(332,282,616,719), number: Qt.rect(469,473,316,315)},
                    {title: "Chuyển ngữ", detail: "Chọn song ngữ hoặc\ntiếng Anh 100%", icon: "translate", box: Qt.rect(304,330,654,603), number: Qt.rect(412,428,430,431)},
                    {title: "Nhận bài giảng mới", detail: "Xem lại nội dung\nvà tải PowerPoint", icon: "slides", box: Qt.rect(308,392,639,483), number: Qt.rect(449,450,355,355)},
                    {title: "Dạy cùng Mascot", detail: "Chọn giọng đọc\nkhi trình chiếu", icon: "voice", box: Qt.rect(372,423,540,452), number: Qt.rect(474,474,306,306)}
                ]
                RowLayout {
                    required property var modelData
                    required property int index
                    Layout.fillWidth: true; Layout.preferredWidth: 1; spacing: home.width > 1000 ? 12 : 8
                    Button {
                        id: step
                        objectName: "homeWorkflowStep" + index
                        Layout.fillWidth: true; Layout.preferredWidth: 1; implicitHeight: 178; padding: 13
                        enabled: !home.bridge.busy
                        Accessible.name: (index + 1) + ". " + modelData.title + ". " + modelData.detail
                        background: Rectangle { radius: 14; color: step.hovered ? "#f8fbff" : "white"; border.color: step.visualFocus ? "#0869f9" : "#dce7f5" }
                        onClicked: { if (index === 0) home.chooseDocument(); else if (index === 1) home.continueWork(); else home.openLibrary() }
                        contentItem: Item {
                            Image { objectName: "homeWorkflowNumber" + index; x: -3; y: -3; width: 34; height: 34; source: "../assets/workflow/number-" + (index + 1) + ".png"; sourceClipRect: modelData.number; fillMode: Image.PreserveAspectFit; mipmap: true; Accessible.ignored: true }
                            ColumnLayout {
                                anchors.fill: parent; anchors.topMargin: 3; spacing: 8
                                Image { objectName: "homeWorkflowIcon" + index; source: "../assets/workflow/" + modelData.icon + ".png"; sourceClipRect: modelData.box; Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: 54; Layout.preferredHeight: 54; fillMode: Image.PreserveAspectFit; mipmap: true; Accessible.ignored: true }
                                Label { text: modelData.title; color: "#16314f"; font.pixelSize: home.width > 1000 ? 16 : 14; font.weight: Font.DemiBold; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap }
                                Copy { text: modelData.detail; font.pixelSize: home.width > 1000 ? 14 : 12; Layout.fillHeight: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignTop }
                            }
                        }
                    }
                    Image { visible: index < 3; source: "../assets/workflow/arrow.png"; sourceClipRect: Qt.rect(396,481,463,338); Layout.preferredWidth: home.width > 1000 ? 24 : 18; Layout.preferredHeight: 24; fillMode: Image.PreserveAspectFit; mipmap: true; Accessible.ignored: true }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 80; color: "white"; radius: 14
            RowLayout {
                anchors.fill: parent; anchors.margins: 16; spacing: 16
                Repeater {
                    model: [
                        {title: "2 kiểu chuyển ngữ", detail: "Song ngữ Việt–Anh · Tiếng Anh 100%", icon: "bilingual", box: Qt.rect(222,305,821,719)},
                        {title: "3 phong cách thiết kế", detail: "Chuẩn lớp học · Trực quan · Luyện tập", icon: "palette", box: Qt.rect(151,195,950,914)},
                        {title: "Giọng đọc & mascot", detail: "Đọc theo slide khi thầy cô yêu cầu", icon: "assistant", box: Qt.rect(189,241,876,807)}
                    ]
                    RowLayout {
                        required property var modelData
                        required property int index
                        Layout.fillWidth: true; Layout.preferredWidth: 1; spacing: 12
                        Rectangle { visible: index > 0; width: 1; Layout.fillHeight: true; color: "#e5edf7"; Layout.rightMargin: 4 }
                        Image { source: "../assets/workflow/" + modelData.icon + ".png"; sourceClipRect: modelData.box; Layout.preferredWidth: 34; Layout.preferredHeight: 34; fillMode: Image.PreserveAspectFit; mipmap: true; Accessible.ignored: true }
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 4
                            Label { text: modelData.title; color: "#16314f"; font.pixelSize: home.width > 1000 ? 14 : 12; font.weight: Font.DemiBold; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                            Copy { text: modelData.detail; font.pixelSize: 11 }
                        }
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
