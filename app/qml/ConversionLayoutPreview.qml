import QtQuick

Item {
    id: view
    required property var bridge
    property string conversionFormat: "parallel_columns"
    property string preset: "standard"
    implicitWidth: 960; implicitHeight: 540
    Image {
        objectName: "conversionReferenceImage"
        anchors.fill: parent
        source: view.bridge.templatePreviewImage(view.preset, "language", view.conversionFormat)
        fillMode: Image.PreserveAspectFit; mipmap: true
    }
}