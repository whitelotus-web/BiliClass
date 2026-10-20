import QtQuick
import QtQuick.Window

Window {
    id: splash
    objectName: "startupSplashWindow"
    title: "BiliClass · " + (stage === "ready" ? "Đã sẵn sàng" : stage === "interface" ? "Đang tải giao diện" : stage === "library" ? "Đang mở thư viện" : "Đang khởi động")
    flags: Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
    color: "#edf7ff"
    width: 1000; height: 563
    readonly property string stage: splashState.stage
    readonly property int step: stage === "ready" ? 2 : stage === "interface" ? 1 : 0
    Item {
        width: 1672; height: 941
        transform: Scale { xScale: splash.width / 1672; yScale: splash.height / 941 }
        Image { anchors.fill: parent; source: "../assets/brand/startup-background.png"; fillMode: Image.Stretch }
        Image { x: 138; y: 206; width: 195; height: 170; source: "book.svg"; fillMode: Image.PreserveAspectFit; sourceSize.width: 390; sourceSize.height: 340 }
        Text {
            x: 343; y: 228; width: 450; height: 140
            text: "Bili<span style='color:#ff7d2b'>Class</span>"; textFormat: Text.RichText
            font.family: "Be Vietnam Pro"; font.pixelSize: 100; font.weight: Font.Bold; color: "#112650"
        }
        Text {
            x: 158; y: 385; width: 620
            text: "CHUYỂN NGỮ THÔNG MINH\nNÂNG TẦM BÀI GIẢNG"
            horizontalAlignment: Text.AlignHCenter; lineHeight: 1.18
            font.family: "Be Vietnam Pro"; font.pixelSize: 34; font.weight: Font.DemiBold
            font.letterSpacing: 1; color: "#5e789f"
        }
        Text {
            x: 172; y: 545; width: 610
            text: splash.stage === "ready" ? "BiliClass đã sẵn sàng!" : "Đang khởi động BiliClass…"
            font.family: "Be Vietnam Pro"; font.pixelSize: 33; font.weight: Font.Bold; color: "#112650"
        }
        Text {
            x: 172; y: 599; width: 610
            text: splash.stage === "ready" ? "Chào mừng thầy cô!" : splash.stage === "interface" ? "Đang tải giao diện bài giảng…" : splash.stage === "library" ? "Đang mở thư viện bài giảng…" : "Chuẩn bị trợ lý dạy học song ngữ"
            font.family: "Be Vietnam Pro"; font.pixelSize: 25; font.weight: Font.Medium; color: "#6680a6"
        }
        Rectangle {
            id: track; x: 172; y: 657; width: 574; height: 24; radius: 12; color: "#d8e4f3"; clip: true
            Rectangle {
                id: moving; width: splash.stage === "ready" ? track.width : 175; height: track.height; radius: 12
                color: "#2589ff"
                x: splash.stage === "ready" ? 0 : -width
                NumberAnimation on x { from: -175; to: track.width; duration: 1550; loops: Animation.Infinite; running: splash.stage !== "ready" }
            }
        }
        Repeater {
            model: ["Mở thư viện", "Tải giao diện", "Sẵn sàng"]
            delegate: Item {
                id: milestone
                required property int index
                required property string modelData
                x: 162 + index * 202; y: 721; width: 180; height: 112
                readonly property bool complete: splash.stage === "ready" || index < splash.step
                readonly property bool active: !complete && index === splash.step
                Rectangle {
                    visible: milestone.index < 2; x: 133; y: 29; width: 100; height: 2
                    color: milestone.complete ? "#82b7ff" : "#d5e3f5"
                }
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter; width: 58; height: 58; radius: 29
                    color: milestone.complete ? "#2487ff" : milestone.active ? "#f5fbff" : "#e7edf7"
                    border.width: 3; border.color: milestone.complete || milestone.active ? "#b5d8ff" : "#e3eaf4"
                    Text { anchors.centerIn: parent; visible: milestone.complete; text: "✓"; font.pixelSize: 37; font.bold: true; color: "white" }
                    Rectangle { anchors.centerIn: parent; width: 31; height: 31; radius: 16; visible: !milestone.complete && !milestone.active; color: "#c4d0e3" }
                    Canvas {
                        anchors.fill: parent; anchors.margins: 12; visible: milestone.active
                        onPaint: { let ctx = getContext("2d"); ctx.clearRect(0,0,width,height); ctx.lineWidth = 7; ctx.lineCap = "round"; ctx.strokeStyle = "#2487ff"; ctx.beginPath(); ctx.arc(width/2,height/2,width/2-4,-Math.PI*.7,Math.PI*.7); ctx.stroke() }
                        RotationAnimator on rotation { from: 0; to: 360; duration: 1000; loops: Animation.Infinite; running: milestone.active }
                    }
                }
                Text { y: 76; width: parent.width; horizontalAlignment: Text.AlignHCenter; text: milestone.modelData; font.family: "Be Vietnam Pro"; font.pixelSize: 22; font.weight: Font.DemiBold; color: milestone.complete || milestone.active ? "#5e789f" : "#889dbc" }
            }
        }
    }
}
