import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: navigation
    property int number: 1
    property int total: 0
    property bool working: false
    property string previousObjectName: ""
    property string counterObjectName: ""
    property string nextObjectName: ""
    signal requested(int number)
    spacing: 8
    Item { Layout.fillWidth: true }
    ActionButton {
        objectName: navigation.previousObjectName; text: "‹"; implicitWidth: 42; implicitHeight: 34
        enabled: !navigation.working && navigation.number > 1
        Accessible.name: "Slide trước"
        onClicked: navigation.requested(navigation.number - 1)
    }
    Label {
        objectName: navigation.counterObjectName
        text: "Slide " + navigation.number + " / " + navigation.total
        color: AppTheme.ink; font.pixelSize: 13
    }
    ActionButton {
        objectName: navigation.nextObjectName; text: "›"; implicitWidth: 42; implicitHeight: 34
        enabled: !navigation.working && navigation.number < navigation.total
        Accessible.name: "Slide sau"
        onClicked: navigation.requested(navigation.number + 1)
    }
    Item { Layout.fillWidth: true }
}
