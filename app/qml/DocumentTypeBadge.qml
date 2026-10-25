import QtQuick
import QtQuick.Controls

Row {
    property bool word: false
    property bool iconOnly: false
    spacing: 5
    height: iconOnly ? 36 : 22
    Image {
        width: parent.iconOnly ? 32 : 20; height: parent.iconOnly ? 36 : 22
        source: parent.word ? "../assets/actions/document-word.svg" : "../assets/actions/document-powerpoint.svg"
        sourceSize.width: 96; sourceSize.height: 108; fillMode: Image.PreserveAspectFit
        Accessible.ignored: true
    }
    Label {
        visible: !parent.iconOnly; text: parent.word ? "Word" : "PowerPoint"
        color: AppTheme.muted; font.pixelSize: 10; font.weight: Font.DemiBold
        height: parent.height; verticalAlignment: Text.AlignVCenter
    }
    Accessible.role: Accessible.StaticText
    Accessible.name: word ? "Tài liệu Word" : "Bài giảng PowerPoint"
}
