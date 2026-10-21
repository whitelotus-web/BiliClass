import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Frame {
    id: preview
    required property var bridge
    property string lessonId: ""
    property real previewHeight: 360
    readonly property bool current: !!lessonId && bridge.lesson.id === lessonId && bridge.quickResult.lesson_id === lessonId
    readonly property var result: current ? bridge.quickResult : ({})
    readonly property bool loading: visible && (!current || bridge.previewBusy)
    padding: 12
    background: Rectangle { radius: 12; color: AppTheme.adapt("#f7faff"); border.color: AppTheme.adapt("#dce8f8") }
    contentItem: ColumnLayout {
        spacing: 10
        LessonChecks {
            objectName: "completionChecks"; Layout.fillWidth: true
            bridge: preview.bridge; visible: preview.current && (!!report.remaining || !!report.image_note)
            onViewRequested: function(slide) { preview.bridge.previewConvertedSlide(slide) }
        }
        Item {
            Layout.fillWidth: true; implicitHeight: preview.previewHeight
            Image {
                objectName: "conversionCompletionImage"
                anchors.fill: parent; source: preview.result.image || ""
                fillMode: Image.PreserveAspectFit; asynchronous: true; cache: true; sourceSize.width: 1600
                opacity: preview.loading ? .6 : 1
                Accessible.name: "Slide vừa tạo"
            }
            BusyIndicator { anchors.centerIn: parent; running: preview.loading; visible: running }
            Label {
                objectName: "conversionCompletionPreviewNote"
                anchors.centerIn: parent; width: parent.width - 40
                visible: !preview.loading && !preview.result.image
                text: preview.result.preview_note || "Chưa có ảnh xem trước. Bấm Thử lại để nạp slide."
                font.pixelSize: 13; color: AppTheme.adapt("#667997"); wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter
            }
        }
        RowLayout {
            objectName: "conversionCompletionNavigation"; Layout.fillWidth: true; spacing: 12
            Item { Layout.fillWidth: true }
            ActionButton {
                objectName: "conversionCompletionPrevious"; text: "Trước"; implicitHeight: 34; Layout.preferredWidth: 84
                enabled: preview.current && !preview.bridge.busy && !preview.bridge.powerpointState.active && !preview.bridge.powerpointState.starting && (preview.result.slide || 1) > 1
                onClicked: preview.bridge.previewConvertedSlide(preview.result.slide - 1)
            }
            Label {
                objectName: "conversionCompletionCounter"
                text: preview.current ? "Slide " + (preview.result.slide || 1) + " / " + (preview.result.total || 0) : "Đang nạp bài giảng…"
                color: AppTheme.adapt("#112650"); font.pixelSize: 13
            }
            ActionButton {
                objectName: "conversionCompletionNext"; text: "Sau"; implicitHeight: 34; Layout.preferredWidth: 84
                enabled: preview.current && !preview.bridge.busy && !preview.bridge.powerpointState.active && !preview.bridge.powerpointState.starting && (preview.result.slide || 1) < (preview.result.total || 0)
                onClicked: preview.bridge.previewConvertedSlide((preview.result.slide || 1) + 1)
            }
            ActionButton {
                objectName: "conversionCompletionRetry"; text: "Thử lại"; implicitHeight: 34
                visible: preview.current && !preview.loading && !preview.result.image
                enabled: !preview.bridge.busy && !preview.bridge.powerpointState.active && !preview.bridge.powerpointState.starting
                onClicked: preview.bridge.previewConvertedSlide(preview.result.slide || 1)
            }
            Item { Layout.fillWidth: true }
        }
    }
}
