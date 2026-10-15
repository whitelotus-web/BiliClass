import QtQuick
import QtQuick.Controls
import QtQuick.Window
import "SubjectTheme.js" as Subjects

Item {
    id: mascot
    property string character: "Milo"
    property string expression: "idle"
    property string subject: ""
    property bool accessories: true
    property bool reducedMotion: false
    property bool inViewport: true
    property real blinkProgress: 0
    property int gestureFrame: 0
    readonly property var theme: Subjects.forSubject(subject)
    readonly property bool themed: accessories && subject.trim().length > 0
    readonly property bool windowActive: visible && !!Window.window && Window.window.visible && Window.window.visibility !== Window.Minimized
    readonly property bool motionActive: windowActive && inViewport && !reducedMotion
    readonly property int frame: expression === "thinking" ? 2 : expression === "celebrate" ? 3 : gestureFrame
    implicitWidth: 110; implicitHeight: 138
    Accessible.name: character + " · " + expression + (themed ? " · " + subject : "")
    function updateViewport() {
        let point = mapToItem(null, 0, 0)
        let available = !!Window.window && point.y + height > 0 && point.y < Window.window.height && point.x + width > 0 && point.x < Window.window.width
        let ancestor = parent
        while (ancestor && available) {
            if (ancestor.clip) {
                let local = mapToItem(ancestor, 0, 0)
                available = local.x + width > 0 && local.y + height > 0 && local.x < ancestor.width && local.y < ancestor.height
            }
            ancestor = ancestor.parent
        }
        inViewport = available
    }
    onMotionActiveChanged: if (!motionActive) { blink.stop(); blinkProgress = 0; gestureFrame = 0 }
    onBlinkProgressChanged: eyes.requestPaint()
    Timer { interval: 400; repeat: true; running: mascot.windowActive && !mascot.reducedMotion; triggeredOnStart: true; onTriggered: mascot.updateViewport() }
    Timer { interval: 4300; repeat: true; running: mascot.motionActive && mascot.frame === 0; onTriggered: { blink.restart(); interval = 3600 + Math.round(Math.random() * 2600) } }
    SequentialAnimation {
        id: blink
        NumberAnimation { target: mascot; property: "blinkProgress"; to: 1; duration: 85; easing.type: Easing.InOutSine }
        PauseAnimation { duration: 45 }
        NumberAnimation { target: mascot; property: "blinkProgress"; to: 0; duration: 130; easing.type: Easing.OutSine }
    }
    Timer { interval: 12000; repeat: true; running: mascot.motionActive && mascot.expression !== "thinking" && mascot.expression !== "celebrate"; onTriggered: { mascot.gestureFrame = 1; waveRest.restart(); interval = 12000 + Math.round(Math.random() * 6000) } }
    Timer { id: waveRest; interval: 850; onTriggered: mascot.gestureFrame = 0 }
    Item {
        id: art; objectName: "mascotArt"
        width: Math.min(mascot.width, mascot.height - (mascot.themed ? 25 : 0)); height: width
        anchors.horizontalCenter: parent.horizontalCenter; anchors.top: parent.top
        transformOrigin: Item.Bottom
        SequentialAnimation on rotation {
            running: mascot.motionActive; loops: Animation.Infinite
            NumberAnimation { to: -.65; duration: 1700; easing.type: Easing.InOutSine }
            NumberAnimation { to: .65; duration: 1700; easing.type: Easing.InOutSine }
            onStopped: art.rotation = 0
        }
        Repeater {
            model: 4
            Item {
                required property int index
                width: art.width; height: art.height; clip: true
                opacity: mascot.frame === index ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: mascot.reducedMotion ? 0 : 95 } }
                Image { source: "../assets/mascot-states.png"; width: parent.width * 4; height: parent.height * 2; x: -parent.index * parent.width; y: mascot.character === "Lumi" ? -parent.height * (1 + 12/448) : 0; smooth: true }
            }
        }
        Canvas {
            id: eyes; objectName: "mascotBlink"
            anchors.fill: parent; visible: mascot.frame === 0 && mascot.blinkProgress > 0
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset(); ctx.scale(width / 448, height / 448)
                const lumi = mascot.character === "Lumi"
                const positions = lumi ? [[188, 138, 31, 39], [295, 104, 27, 36]] : [[224, 194, 27, 31], [326, 175, 24, 30]]
                for (let eye of positions) {
                    ctx.save(); ctx.translate(eye[0], eye[1]); ctx.rotate(-.15)
                    ctx.beginPath(); ctx.moveTo(-eye[2], 0)
                    ctx.bezierCurveTo(-eye[2], -eye[3]*1.35, eye[2], -eye[3]*1.35, eye[2], 0)
                    ctx.bezierCurveTo(eye[2], eye[3]*1.35, -eye[2], eye[3]*1.35, -eye[2], 0)
                    ctx.clip()
                    const lid = ctx.createLinearGradient(0, -eye[3], 0, eye[3])
                    lid.addColorStop(0, lumi ? "#ffe5c6" : "#ffa133")
                    lid.addColorStop(.5, lumi ? "#ffe8cd" : "#ffb95e")
                    lid.addColorStop(1, lumi ? "#ffedda" : "#fff0dd")
                    ctx.fillStyle = lid
                    ctx.fillRect(-eye[2]-2, -eye[3]-3, eye[2]*2+4, (eye[3]*2+6)*mascot.blinkProgress)
                    if (mascot.blinkProgress > .75) {
                        ctx.globalAlpha = (mascot.blinkProgress-.75)*4
                        ctx.strokeStyle = "#48291e"; ctx.lineWidth = 4; ctx.lineCap = "round"
                        ctx.beginPath(); ctx.moveTo(-eye[2]*.8, 0)
                        ctx.quadraticCurveTo(0, eye[3]*.45, eye[2]*.8, 0); ctx.stroke()
                    }
                    ctx.restore()
                }
            }
        }
        Rectangle {
            objectName: "mascotSubjectProp"; visible: mascot.themed
            x: art.width * .61; y: art.height * .66; width: art.width * .22; height: art.height * .21; radius: 4
            color: mascot.theme.paper; border.color: mascot.theme.color; rotation: -8
            Label { anchors.centerIn: parent; text: mascot.theme.symbol; font.pixelSize: Math.max(9, parent.width*.44); font.bold: true; color: mascot.theme.color; textFormat: Text.PlainText }
        }
    }
    Rectangle {
        objectName: "mascotSubjectBadge"; visible: mascot.themed
        anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom
        width: Math.min(parent.width, badge.implicitWidth + 16); height: Math.max(22, badge.implicitHeight + 7)
        radius: 10; color: mascot.theme.paper; border.color: mascot.theme.color
        Label { id: badge; anchors.centerIn: parent; width: Math.min(implicitWidth, mascot.width - 12); text: mascot.subject; wrapMode: Text.Wrap; font.pixelSize: 10; color: mascot.theme.color; textFormat: Text.PlainText; horizontalAlignment: Text.AlignHCenter }
    }
}
