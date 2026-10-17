import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: upload
    property string fileName: ""
    property string errorText: ""
    property bool busy: false
    property bool working: false
    property bool illustrated: false
    property bool compact: false
    property string chooseObjectName: ""
    property string dropObjectName: ""
    property string filenameObjectName: ""
    property string errorObjectName: ""
    property string removeObjectName: ""
    signal chooseFile()
    signal filesDropped(var urls)
    signal removeFile()
    signal showProgress()
    implicitHeight: uploadRow.implicitHeight + (compact ? 28 : 44)
    radius: 16; color: drop.containsDrag ? "#edf5ff" : "white"
    border.color: drop.containsDrag ? "#0869f9" : "#cbdcf4"
    border.width: drop.containsDrag ? 2 : 1

    RowLayout {
        id: uploadRow
        anchors.horizontalCenter: parent.horizontalCenter; anchors.top: parent.top; anchors.topMargin: upload.compact ? 14 : 22
        width: upload.illustrated ? Math.min(parent.width - 44, 840) : parent.width - 44
        spacing: upload.illustrated ? 24 : 0
        Image {
            objectName: upload.chooseObjectName + "Illustration"
            visible: upload.illustrated
            source: "../assets/powerpoint-upload.png"
            // Trim transparent canvas margins for optical balance; retain the original asset.
            sourceClipRect: Qt.rect(248, 120, 1040, 830)
            fillMode: Image.PreserveAspectFit; smooth: true; mipmap: true
            Layout.preferredWidth: upload.compact ? 140 : upload.width >= 1000 ? 200 : 160
            Layout.preferredHeight: upload.compact ? 110 : upload.width >= 1000 ? 160 : 128
            Layout.alignment: Qt.AlignVCenter
            Accessible.ignored: true
        }
        ColumnLayout {
            id: content
            Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: upload.compact ? 7 : 10
            Label {
                objectName: "powerpointUploadHeading"
                text: upload.working ? "Bài giảng đang được chuẩn bị" : "Tải lên bài giảng PowerPoint (.pptx)"
                color: "#0869f9"; font.pixelSize: upload.compact ? 19 : 22; font.weight: Font.Bold
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
            }
            Label {
                text: upload.working ? "Theo dõi tiến độ; các phần đã xong được lưu lại." : "Kéo thả tệp vào đây hoặc bấm nút bên dưới để chọn file"
                color: "#687e9b"; font.pixelSize: 13; Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
            }
            ActionButton {
                id: choose
                objectName: upload.chooseObjectName
                text: upload.working ? "Xem tiến độ" : upload.fileName ? "Đổi file PowerPoint" : "Chọn file PowerPoint"
                primary: true; font.pixelSize: 14; implicitHeight: 44
                Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: 258
                enabled: upload.working || !upload.busy
                onClicked: upload.working ? upload.showProgress() : upload.chooseFile()
                contentItem: RowLayout {
                    spacing: 9
                    Item { Layout.fillWidth: true }
                    Canvas {
                        Layout.preferredWidth: 20; Layout.preferredHeight: 20
                        property bool active: choose.enabled
                        onActiveChanged: requestPaint()
                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            ctx.strokeStyle = active ? "white" : "#96a6bc"
                            ctx.lineWidth = 1.7; ctx.lineJoin = "round"; ctx.lineCap = "round"
                            ctx.beginPath(); ctx.moveTo(10, 13); ctx.lineTo(10, 3)
                            ctx.moveTo(6, 7); ctx.lineTo(10, 3); ctx.lineTo(14, 7)
                            ctx.moveTo(4, 12); ctx.lineTo(4, 17); ctx.lineTo(16, 17); ctx.lineTo(16, 12); ctx.stroke()
                        }
                    }
                    Label { text: choose.text; font: choose.font; color: choose.enabled ? "white" : "#96a6bc" }
                    Item { Layout.fillWidth: true }
                }
            }
            Label {
                text: "Chỉ hỗ trợ tệp .pptx tối đa 200 MB"; color: "#687e9b"; font.pixelSize: 12
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
            }
            RowLayout {
                visible: !!upload.fileName; Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: false
                Layout.preferredWidth: Math.min(content.width, selectedName.implicitWidth + removeSelected.implicitWidth + 9)
                Layout.maximumWidth: content.width; spacing: 9
                Label {
                    id: selectedName
                    objectName: upload.filenameObjectName
                    text: upload.fileName; textFormat: Text.PlainText; elide: Text.ElideMiddle
                    color: "#16314f"; font.pixelSize: 12; Layout.fillWidth: true
                }
                ActionButton {
                    id: removeSelected
                    objectName: upload.removeObjectName; text: "Bỏ tệp"; implicitHeight: 30
                    enabled: !upload.busy && !upload.working; onClicked: upload.removeFile()
                }
            }
            Label {
                objectName: upload.errorObjectName
                visible: !!upload.errorText; text: upload.errorText; textFormat: Text.PlainText
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                color: "#ab5b20"; font.pixelSize: 12
            }
        }
    }
    DropArea {
        id: drop; objectName: upload.dropObjectName
        anchors.fill: parent; enabled: !upload.working && !upload.busy
        onEntered: function(drag) { drag.accepted = drag.hasUrls && drag.urls.length === 1 }
        onDropped: function(event) {
            var urls = []
            for (var i = 0; i < event.urls.length; i++) urls.push(event.urls[i].toString())
            if (urls.length) { upload.filesDropped(urls); event.acceptProposedAction() }
        }
    }
}
