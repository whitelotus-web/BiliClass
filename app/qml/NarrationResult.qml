import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ContentScrollView {
    id: result
    required property var bridge
    property var record: ({})
    property var coverage: ({})
    signal requestLibrary()
    signal requestConfiguration()
    signal requestPowerPoint()
    signal requestDownload()
    signal requestAudio()
    objectName: "narrationResultPage"
    outerGutter: true; contentWidth: availableWidth
    ColumnLayout {
        width: result.availableWidth; spacing: 16
        RowLayout { Layout.fillWidth: true
            Label { objectName: "narrationResultHeading"; text: "Đã tạo giọng đọc bài giảng"; color: AppTheme.ink; font.pixelSize: 27; font.weight: Font.Bold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            ActionButton { objectName: "narrationResultChange"; text: "Đổi cấu hình giọng"; onClicked: result.requestConfiguration() }
            ActionButton { objectName: "narrationResultLibrary"; text: "Trở lại thư viện"; onClicked: result.requestLibrary() }
        }
        Label { text: result.bridge.lesson.title || ""; color: AppTheme.ink; font.pixelSize: 20; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Frame {
            Layout.fillWidth: true; padding: 16
            background: Rectangle { radius: 12; color: AppTheme.adapt("#eef8f4"); border.color: AppTheme.adapt("#d2eade") }
            ColumnLayout { width: parent.width; spacing: 7
                Label { text: "✓ Giọng đọc đã hoàn tất và lưu cùng bài giảng"; color: AppTheme.success; font.pixelSize: 14; font.weight: Font.DemiBold; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Label { text: (result.record.title || "") + " · " + (result.record.complete || result.record.total || 0) + "/" + (result.record.total || 0) + " đoạn sẵn sàng"; color: AppTheme.ink; font.pixelSize: 13; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                Label { text: (result.coverage.total || 0) + " slide · " + (result.coverage.readable || 0) + " slide có lời đọc" + ((result.coverage.total || 0) > (result.coverage.readable || 0) ? " · Slide không có lời giữ im lặng" : ""); color: AppTheme.muted; font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            }
        }
        Flow { objectName: "narrationResultActions"; Layout.alignment: Qt.AlignHCenter; Layout.minimumWidth: 0; Layout.maximumWidth: result.availableWidth
            Layout.preferredWidth: openButton.implicitWidth + downloadButton.implicitWidth + audioButton.implicitWidth + 20; spacing: 10
            ActionButton { id: openButton; objectName: "narrationResultOpen"; text: "Mở PowerPoint"; primary: true; enabled: !result.bridge.busy && !result.bridge.narrationBusy && !result.bridge.teachingTransitioning; onClicked: result.requestPowerPoint() }
            ActionButton { id: downloadButton; objectName: "narrationResultDownload"; text: "Tải PowerPoint có giọng"; iconName: "download"; enabled: !result.bridge.busy; onClicked: result.requestDownload() }
            ActionButton { id: audioButton; objectName: "narrationResultAudio"; text: "Tải audio (.zip)"; enabled: !result.bridge.busy; onClicked: result.requestAudio() }
        }
        Rectangle {
            objectName: "narrationResultPreview"; Layout.fillWidth: true
            implicitHeight: Math.max(260, Math.min(500, result.height * .56)); radius: 12
            color: AppTheme.adapt("#e9eef5"); border.color: AppTheme.line
            Image { objectName: "narrationResultSlideImage"; anchors.fill: parent; anchors.margins: 5; source: result.bridge.quickResult.image || ""; fillMode: Image.PreserveAspectFit; asynchronous: true; sourceSize.width: 1600; cache: true }
            BusyIndicator { anchors.centerIn: parent; running: result.bridge.previewBusy; visible: running }
            Label { anchors.centerIn: parent; visible: !result.bridge.quickResult.image && !result.bridge.previewBusy; text: "Xem trước slide"; color: AppTheme.muted }
        }
        RowLayout { Layout.alignment: Qt.AlignHCenter; spacing: 8
            ActionButton { objectName: "narrationResultPrevious"; text: "‹"; implicitHeight: 34; enabled: !result.bridge.busy && (result.bridge.quickResult.slide || 1) > 1; onClicked: result.bridge.previewConvertedSlide(result.bridge.quickResult.slide - 1) }
            Label { objectName: "narrationResultCounter"; text: "Slide " + (result.bridge.quickResult.slide || 1) + " / " + (result.bridge.quickResult.total || 0); color: AppTheme.ink; font.pixelSize: 13 }
            ActionButton { objectName: "narrationResultNext"; text: "›"; implicitHeight: 34; enabled: !result.bridge.busy && (result.bridge.quickResult.slide || 1) < result.bridge.quickResult.total; onClicked: result.bridge.previewConvertedSlide(result.bridge.quickResult.slide + 1) }
        }
        Flow { objectName: "narrationResultListening"; Layout.fillWidth: false; Layout.alignment: Qt.AlignHCenter; Layout.minimumWidth: 0; Layout.maximumWidth: result.availableWidth; spacing: 10
            Layout.preferredWidth: (listenEnglish.visible ? listenEnglish.implicitWidth : 0) + (listenVietnamese.visible ? listenVietnamese.implicitWidth : 0) + (listenEnglish.visible && listenVietnamese.visible ? spacing : 0)
            CreatedNarrationButton { id: listenEnglish; objectName: "narrationResultListenEnglish"; appBridge: result.bridge; language: "en"; slideNumber: result.bridge.quickResult.slide || 1; recordId: result.record.id || ""; visible: result.record.mode !== "vi" }
            CreatedNarrationButton { id: listenVietnamese; objectName: "narrationResultListenVietnamese"; appBridge: result.bridge; language: "vi"; slideNumber: result.bridge.quickResult.slide || 1; recordId: result.record.id || ""; visible: result.record.mode !== "en" }
        }
    }
}
