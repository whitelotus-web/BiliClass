import QtQuick
import QtQuick.Controls

Item {
    id: mascot
    property string character: "Milo"
    property string expression: "idle"
    property string subject: ""
    property bool accessories: true
    property bool reducedMotion: false
    implicitWidth: 110; implicitHeight: 125
    Accessible.name: character + " · " + expression
    readonly property int frame: expression === "speaking" ? 1 : expression === "thinking" ? 2 : expression === "celebrate" ? 3 : 0
    Item {
        width: parent.width; height: parent.width; anchors.centerIn: parent; clip: true
        transform: Translate {
            id: mascotFloat
            SequentialAnimation on y {
                running: mascot.visible && !mascot.reducedMotion
                loops: Animation.Infinite
                NumberAnimation { to: -4; duration: 1450; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0; duration: 1450; easing.type: Easing.InOutSine }
                onStopped: mascotFloat.y = 0
            }
        }
        SequentialAnimation on scale {
            running: mascot.visible && !mascot.reducedMotion
            loops: Animation.Infinite
            NumberAnimation { to: 1.025; duration: 1100; easing.type: Easing.InOutSine }
            NumberAnimation { to: 1; duration: 1100; easing.type: Easing.InOutSine }
            onStopped: scale = 1
        }
        Image {
            source: "../assets/mascot-states.png"
            width: parent.width * 4; height: parent.height * 2
            x: -mascot.frame * parent.width
            // Skip a few transparent/border pixels at the atlas row boundary.
            y: mascot.character === "Lumi" ? -parent.height - 3 : 0
            smooth: true
        }
        SequentialAnimation on opacity {
            running: mascot.visible && !mascot.reducedMotion && mascot.expression === "thinking"
            loops: Animation.Infinite
            NumberAnimation { to: .6; duration: 500 }
            NumberAnimation { to: 1; duration: 500 }
            onStopped: opacity = 1
        }
    }
    Rectangle {
        visible: mascot.accessories && !!mascot.subject
        anchors.right: parent.right; anchors.bottom: parent.bottom
        width: badge.implicitWidth + 14; height: 24; radius: 12; color: "#eaf3ff"; border.color: "#bcd8fc"
        Label { id: badge; anchors.centerIn: parent; text: mascot.subject.slice(0, 16); font.pixelSize: 10; color: "#0869f9"; textFormat: Text.PlainText }
    }
}
