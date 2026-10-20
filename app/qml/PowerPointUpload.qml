import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: upload
    property string fileName: ""
    property string errorText: ""
    property bool busy: false
    property bool working: false
    property string workingTitle: "Bài giảng đang được chuẩn bị"
    property string workingDetail: "Theo dõi tiến độ; các phần đã xong được lưu lại."
    property string progressLabel: "Xem tiến độ"
    property bool illustrated: false
    property bool compact: false
    property bool condensed: false
    property bool previewEnabled: false
    property url previewImage
    property bool previewBusy: false
    property int slideCount: 0
    property string previewError: ""
    property string chooseObjectName: ""
    property string dropObjectName: ""
    property string filenameObjectName: ""
    property string errorObjectName: ""
    property string removeObjectName: ""
    signal chooseFile()
    signal filesDropped(var urls)
    signal removeFile()
    signal showProgress()
    signal previewRequested()
    signal previewRetryRequested()
    implicitHeight: condensed ? condensedRow.implicitHeight + 20 : uploadRow.implicitHeight + (compact ? 28 : 44)
    radius: 16; color: drop.containsDrag ? AppTheme.adapt("#edf5ff") : AppTheme.surface
    border.color: drop.containsDrag ? AppTheme.adapt("#0869f9") : AppTheme.adapt("#cbdcf4")
    border.width: drop.containsDrag ? 2 : 1

    RowLayout {
        id: uploadRow
        visible: !upload.condensed
        anchors.horizontalCenter: parent.horizontalCenter; anchors.top: parent.top; anchors.topMargin: upload.compact ? 14 : 22
        width: upload.illustrated ? Math.min(parent.width - 44, 840) : parent.width - 44
        spacing: upload.illustrated ? 24 : 0
        Image {
            objectName: upload.condensed ? "" : upload.chooseObjectName + "Illustration"
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
                objectName: upload.condensed ? "" : "powerpointUploadHeading"
                text: upload.working ? upload.workingTitle : "Tải lên bài giảng PowerPoint (.pptx)"
                color: AppTheme.adapt("#0869f9"); font.pixelSize: upload.compact ? 19 : 22; font.weight: Font.Bold
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
            }
            Label {
                text: upload.working ? upload.workingDetail : "Kéo thả tệp vào đây hoặc bấm nút bên dưới để chọn file"
                color: AppTheme.adapt("#687e9b"); font.pixelSize: 13; Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
            }
            ActionButton {
                id: choose
                objectName: upload.condensed ? "" : upload.chooseObjectName
                text: upload.working ? upload.progressLabel : upload.fileName ? "Đổi file PowerPoint" : "Chọn file PowerPoint"
                primary: true; font.pixelSize: 14; implicitHeight: 44
                Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: 258
                enabled: upload.working || !upload.busy
                onClicked: upload.working ? upload.showProgress() : upload.chooseFile()
                contentItem: RowLayout {
                    spacing: 9
                    Item { Layout.fillWidth: true }
                    Canvas {
        property bool applicationDark: AppTheme.dark
        onApplicationDarkChanged: requestPaint()
                        Layout.preferredWidth: 20; Layout.preferredHeight: 20
                        property bool active: choose.enabled
                        property bool progress: upload.working
                        onActiveChanged: requestPaint()
                        onProgressChanged: requestPaint()
                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            ctx.strokeStyle = active ? AppTheme.accentText : AppTheme.adapt("#96a6bc")
                            ctx.lineWidth = 1.7; ctx.lineJoin = "round"; ctx.lineCap = "round"
                            ctx.beginPath()
                            if (progress) {
                                ctx.arc(10, 10, 7, 0, 2 * Math.PI)
                                ctx.moveTo(10, 5); ctx.lineTo(10, 10); ctx.lineTo(14, 12)
                            } else {
                                ctx.moveTo(10, 13); ctx.lineTo(10, 3)
                                ctx.moveTo(6, 7); ctx.lineTo(10, 3); ctx.lineTo(14, 7)
                                ctx.moveTo(4, 12); ctx.lineTo(4, 17); ctx.lineTo(16, 17); ctx.lineTo(16, 12)
                            }
                            ctx.stroke()
                        }
                    }
                    Label { text: choose.text; font: choose.font; color: choose.enabled ? AppTheme.accentText : AppTheme.adapt("#96a6bc") }
                    Item { Layout.fillWidth: true }
                }
            }
            Label {
                text: "Chỉ hỗ trợ tệp .pptx tối đa 200 MB"; color: AppTheme.adapt("#687e9b"); font.pixelSize: 12
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
            }
            RowLayout {
                visible: !!upload.fileName; Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: false
                Layout.preferredWidth: Math.min(content.width, selectedName.implicitWidth + removeSelected.implicitWidth + 9)
                Layout.maximumWidth: content.width; spacing: 9
                Label {
                    id: selectedName
                    objectName: upload.condensed ? "" : upload.filenameObjectName
                    text: upload.fileName; textFormat: Text.PlainText; elide: Text.ElideMiddle
                    color: AppTheme.adapt("#16314f"); font.pixelSize: 12; Layout.fillWidth: true
                }
                ActionButton {
                    id: removeSelected
                    objectName: upload.condensed ? "" : upload.removeObjectName; text: "Bỏ tệp"; implicitHeight: 30
                    enabled: !upload.busy && !upload.working; onClicked: upload.removeFile()
                }
            }
            Label {
                objectName: upload.condensed ? "" : upload.errorObjectName
                visible: !!upload.errorText; text: upload.errorText; textFormat: Text.PlainText
                Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                color: AppTheme.adapt("#ab5b20"); font.pixelSize: 12
            }
        }
    }
    RowLayout {
        id: condensedRow
        visible: upload.condensed
        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
        anchors.margins: 10; spacing: 14
        Image {
            objectName: upload.condensed ? upload.chooseObjectName + "Illustration" : ""
            visible: upload.illustrated && !upload.previewEnabled; source: "../assets/powerpoint-upload.png"
            sourceClipRect: Qt.rect(248, 120, 1040, 830)
            fillMode: Image.PreserveAspectFit; smooth: true; mipmap: true
            Layout.preferredWidth: 80; Layout.preferredHeight: 64
            Accessible.ignored: true
        }
        ColumnLayout {
            Layout.fillWidth: true; Layout.minimumWidth: 0; spacing: 4
            Label {
                objectName: upload.condensed ? "powerpointUploadHeading" : ""
                text: upload.working ? upload.workingTitle : upload.fileName ? "Đã chọn PowerPoint" : "Tải lên bài giảng PowerPoint (.pptx)"
                color: AppTheme.adapt("#0869f9"); font.pixelSize: 17; font.weight: Font.Bold
                Layout.fillWidth: true; wrapMode: Text.WordWrap
            }
            Label {
                visible: !upload.fileName && !upload.errorText
                text: upload.working ? upload.workingDetail : "Kéo thả tệp .pptx vào đây · Tối đa 200 MB"
                color: AppTheme.adapt("#687e9b"); font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
            }
            RowLayout {
                visible: !!upload.fileName; Layout.fillWidth: true; spacing: 8
                Label { objectName: upload.condensed ? upload.filenameObjectName : ""; text: upload.fileName; textFormat: Text.PlainText; elide: Text.ElideMiddle; color: AppTheme.adapt("#16314f"); font.pixelSize: 12; Layout.fillWidth: true; Layout.minimumWidth: 0 }
                ActionButton { objectName: upload.condensed ? upload.removeObjectName : ""; text: "Bỏ tệp"; implicitHeight: 26; font.pixelSize: 11; enabled: !upload.busy && !upload.working; onClicked: upload.removeFile() }
            }
            Label { visible: upload.slideCount > 0; text: upload.slideCount + " slide · Chọn cấu hình chuyển đổi ở bên dưới"; color: AppTheme.muted; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            Label { objectName: upload.condensed ? upload.errorObjectName : ""; visible: !!upload.errorText; text: upload.errorText; textFormat: Text.PlainText; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: 1; elide: Text.ElideRight; color: AppTheme.adapt("#ab5b20"); font.pixelSize: 12; HoverHandler { id: uploadErrorHover } ToolTip.visible: uploadErrorHover.hovered; ToolTip.text: upload.errorText }
        }
        ActionButton {
            objectName: upload.condensed ? upload.chooseObjectName : ""
            text: upload.working ? upload.progressLabel : upload.fileName ? "Chọn bài khác" : "Chọn file PowerPoint"
            primary: true; implicitHeight: 38; font.pixelSize: 13
            Layout.preferredWidth: upload.fileName ? 156 : 220; enabled: upload.working || !upload.busy
            onClicked: upload.working ? upload.showProgress() : upload.chooseFile()
        }
        Rectangle {
            objectName: upload.previewEnabled ? "creationSelectedSlidePreview" : ""
            visible: upload.previewEnabled
            Layout.preferredWidth: upload.width >= 1000 ? 304 : 240
            Layout.preferredHeight: width * 9 / 16
            radius: 8; color: AppTheme.field; border.color: AppTheme.line
            Image { objectName: upload.previewEnabled ? "creationSelectedSlideImage" : ""; anchors.fill: parent; anchors.margins: 3; source: upload.previewImage; fillMode: Image.PreserveAspectFit; asynchronous: true; smooth: true }
            BusyIndicator { anchors.centerIn: parent; running: upload.previewBusy; visible: running }
            Label { visible: !upload.previewBusy && !upload.previewImage; anchors.centerIn: parent; text: upload.previewError ? "Bấm để tải lại ảnh slide" : "Xem trước slide"; color: AppTheme.muted; font.pixelSize: 12 }
            TapHandler { onTapped: upload.previewImage ? upload.previewRequested() : upload.previewRetryRequested() }
            HoverHandler { id: previewHover; cursorShape: Qt.PointingHandCursor }
            ToolTip.visible: previewHover.hovered; ToolTip.text: upload.previewImage ? "Phóng to slide gốc" : upload.previewError || "Đang chuẩn bị ảnh slide gốc"
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
