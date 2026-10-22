import QtQuick
import QtQuick.Window

Window {
    id: splash
    objectName: "startupSplashWindow"
    title: "BiliClass · " + (stage === "ready" ? "Đã sẵn sàng" : stage === "interface" ? "Đang tải giao diện" : stage === "library" ? "Đang mở thư viện" : "Đang khởi động")
    flags: Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
    color: "#edf7ff"
    width: 860; height: 484
    readonly property string stage: splashState.stage
    opacity: stage === "ready" ? 0 : 1
    Behavior on opacity { NumberAnimation { duration: splashState.reducedMotion ? 0 : 110; easing.type: Easing.OutCubic } }
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
            x: 172; y: 574; width: 610
            text: splash.stage === "ready" ? "BiliClass đã sẵn sàng!" : "Đang khởi động BiliClass…"
            font.family: "Be Vietnam Pro"; font.pixelSize: 33; font.weight: Font.Bold; color: "#112650"
        }
        Text {
            x: 172; y: 628; width: 610
            text: splash.stage === "ready" ? "Chào mừng thầy cô!" : splash.stage === "interface" ? "Đang tải giao diện bài giảng…" : splash.stage === "library" ? "Đang mở thư viện bài giảng…" : "Chuẩn bị trợ lý dạy học song ngữ"
            font.family: "Be Vietnam Pro"; font.pixelSize: 25; font.weight: Font.Medium; color: "#6680a6"
        }
        Rectangle {
            id: track; objectName: "startupProgressTrack"
            x: 172; y: 687; width: 574; height: 18; radius: 9; color: "#dce8f6"; clip: true
            Rectangle {
                id: moving; width: splashState.reducedMotion ? track.width * .45 : 196; height: track.height; radius: 9
                x: splashState.reducedMotion ? 0 : -196
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0; color: "#69b3ff" }
                    GradientStop { position: .5; color: "#2589ff" }
                    GradientStop { position: 1; color: "#69b3ff" }
                }
                XAnimator on x {
                    from: -196; to: track.width; duration: 1150; easing.type: Easing.InOutSine
                    loops: Animation.Infinite
                    running: splash.visible && splash.stage !== "ready" && !splashState.reducedMotion
                }
            }
        }
    }
}
