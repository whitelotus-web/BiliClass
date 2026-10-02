import QtQuick
import QtQuick.Controls

Item {
    id: view
    property var plan: ({})
    readonly property real factor: Math.min(width / 1280, height / 720)
    implicitWidth: 1280
    implicitHeight: 720
    Rectangle {
        width: 1280; height: 720
        anchors.centerIn: parent
        scale: view.factor
        color: view.plan.background || "#f7f9fd"
        clip: true
        Image {
            source: view.plan.image || ""
            x: (view.plan.image_box || {}).x || 0
            y: (view.plan.image_box || {}).y || 0
            width: (view.plan.image_box || {}).width || 0
            height: (view.plan.image_box || {}).height || 0
            fillMode: Image.PreserveAspectFit
        }
        Repeater {
            model: view.plan.elements || []
            Label {
                required property var modelData
                x: modelData.x; y: modelData.y; width: modelData.width; height: modelData.height
                text: modelData.text
                color: modelData.color
                font.family: view.plan.font || "Arial"
                font.pixelSize: modelData.size
                font.bold: modelData.bold
                font.italic: modelData.italic
                wrapMode: Text.WordWrap
                textFormat: Text.PlainText
                horizontalAlignment: modelData.align === "center" ? Text.AlignHCenter : Text.AlignLeft
                clip: true
            }
        }
        Label {
            visible: !!view.plan.overflow
            x: 64; y: 632; width: 1152; height: 30
            text: "Ý này quá dài cho khung mẫu. Tách đoạn và duyệt lại trước khi xuất."
            color: "#ad651d"; font.pixelSize: 20; textFormat: Text.PlainText
        }
    }
}
