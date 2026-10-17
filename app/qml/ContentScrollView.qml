import QtQuick
import QtQuick.Controls

ScrollView {
    id: view
    // Pages already have a margin; compact editors/dialogs reserve space inside.
    property bool outerGutter: false
    property real scrollBarGap: 6
    property string barObjectName: objectName ? objectName + "Bar" : ""
    // Clip the viewport, not the control: an outer thumb can then sit in the
    // page margin without becoming an extra child of the surrounding Layout.
    clip: !outerGutter
    Binding { target: view.contentItem; property: "clip"; value: true }
    rightPadding: outerGutter ? 0 : 24
    bottomPadding: horizontalBar.visible ? 18 : 0
    ScrollBar.vertical: SlimScrollBar {
        id: verticalBar
        objectName: view.barObjectName
        parent: view
        x: view.outerGutter ? view.width + view.scrollBarGap : view.width - width
        y: 0
        height: view.height - view.bottomPadding
        width: 18
        visible: view.visible && size < 1 && policy !== ScrollBar.AlwaysOff
    }
    ScrollBar.horizontal: SlimScrollBar {
        id: horizontalBar
        objectName: view.barObjectName ? view.barObjectName + "Horizontal" : ""
        parent: view
        x: view.leftPadding
        y: view.height - height
        width: view.availableWidth
        height: 18
        visible: view.visible && size < 1 && policy !== ScrollBar.AlwaysOff
    }
}
