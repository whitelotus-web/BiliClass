import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: guide
    required property var bridge
    property int step: 0
    property string resultMessage: ""
    readonly property bool working: bridge.busy
    readonly property var headings: ["Dán mã đã chuẩn bị", "Triển khai trên Google", "Dán đường dẫn về tool", "Sẵn sàng sử dụng"]
    objectName: "languageappGuide"
    title: "Thiết lập Apps Script · chỉ làm một lần"
    modal: true
    anchors.centerIn: parent
    width: Math.min(700, parent.width - 24)
    height: Math.min(650, parent.height - 20)
    closePolicy: working ? Popup.NoAutoClose : Popup.CloseOnEscape
    background: Rectangle { color: AppTheme.surface; radius: 14; border.color: AppTheme.line }
    onAboutToShow: {
        // A prior successful test must not look like a fresh test after editing settings.
        if (step === 3) { step = 0; resultMessage = "" }
    }

    Connections {
        target: guide.bridge.googleSettings
        function onLanguageSetupChecked(success, message) {
            guide.resultMessage = message
            if (success) guide.step = 3
        }
    }

    component HelpText: Label {
        Layout.fillWidth: true
        wrapMode: Text.WordWrap
        textFormat: Text.PlainText
        color: AppTheme.muted
        font.pixelSize: 13
    }
    component Action: Button {
        id: action
        property bool primary: false
        implicitHeight: 42
        leftPadding: 14; rightPadding: 14
        font.pixelSize: 13
        font.weight: Font.DemiBold
        contentItem: Label {
            text: action.text; font: action.font
            color: !action.enabled ? AppTheme.disabled : action.primary ? AppTheme.accentText : AppTheme.blue
            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            radius: 9
            color: !action.enabled ? AppTheme.disabledSurface : action.primary ? AppTheme.accent : action.hovered ? AppTheme.hover : AppTheme.surface
            border.color: action.activeFocus || action.primary ? AppTheme.accent : AppTheme.line
            border.width: action.activeFocus ? 2 : 1
        }
    }

    contentItem: ColumnLayout {
        spacing: 16
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            Repeater {
                model: ["Dán mã", "Triển khai", "Kết nối"]
                Label {
                    required property int index
                    required property string modelData
                    Layout.fillWidth: true
                    text: (index + 1) + ". " + modelData
                    color: guide.step >= index ? AppTheme.blue : AppTheme.muted
                    font.pixelSize: 13; font.weight: guide.step === index ? Font.Bold : Font.Normal
                    wrapMode: Text.WordWrap
                }
            }
        }
        Label {
            objectName: "languageappSetupHeading"
            text: guide.headings[guide.step]
            color: AppTheme.ink; font.pixelSize: 21; font.weight: Font.Bold
            Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        ContentScrollView {
            id: scroll
            objectName: "languageappSetupScroll"
            Layout.fillWidth: true; Layout.fillHeight: true
            contentWidth: availableWidth
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ColumnLayout {
                width: scroll.availableWidth; spacing: 16
                ColumnLayout {
                    visible: guide.step === 0; Layout.fillWidth: true; spacing: 14
                    HelpText { text: "Không cần thẻ hoặc key Google Cloud. BiliClass đã chuẩn bị mã chương trình và tự tạo mã truy cập riêng cho thầy cô." }
                    HelpText {
                        visible: guide.bridge.googleSettings.state.alternatives.languageapp.configured
                        text: "Máy này đã có cấu hình. Nếu đang dịch được, chỉ cần đóng hướng dẫn để dùng tiếp. Các bước dưới dành cho thiết lập lại dịch vụ."
                    }
                    Action {
                        objectName: "languageappCopySetup"
                        primary: true
                        text: guide.bridge.googleSettings.languageSetupReady ? "Sao chép lại cùng mã" : "1. Sao chép mã đã chuẩn bị"
                        enabled: !guide.working
                        onClicked: guide.bridge.googleSettings.copyLanguageScript()
                    }
                    HelpText {
                        objectName: "languageappCopyStatus"
                        visible: guide.bridge.googleSettings.languageSetupReady
                        text: "✓ Đã sao chép. Mã có sẵn doPost; không cần tự viết hay tự đặt mã truy cập."
                        color: AppTheme.adapt("#168567")
                    }
                    Action {
                        objectName: "languageappOpenScript"
                        text: "2. Mở trang tạo Apps Script"
                        enabled: guide.bridge.googleSettings.languageSetupReady && !guide.working
                        onClicked: Qt.openUrlExternally("https://script.google.com/home/start")
                    }
                    HelpText { text: "Trên trang Google:\n• Đăng nhập tài khoản Google của thầy cô.\n• Chọn Dự án mới nếu chưa có vùng soạn mã.\n• Bấm vào vùng mã trong Code.gs → Ctrl+A → Ctrl+V → Ctrl+S.\n\nDán thay toàn bộ mã cũ, kể cả myFunction; không dán vào bên trong hàm cũ." }
                    HelpText { text: "Đoạn mã vừa sao chép chứa mã truy cập riêng. Chỉ dán vào dự án của thầy cô, không đăng công khai. Không cần vào Thuộc tính tập lệnh." }
                }
                ColumnLayout {
                    visible: guide.step === 1; Layout.fillWidth: true; spacing: 14
                    HelpText { text: "Ở góc phải trang Apps Script, chọn:\nTriển khai → Bản triển khai mới → bánh răng → Ứng dụng web." }
                    Frame {
                        Layout.fillWidth: true; padding: 14
                        background: Rectangle { radius: 10; color: AppTheme.adapt("#edf5ff"); border.color: AppTheme.line }
                        ColumnLayout {
                            width: parent.width; spacing: 10
                            HelpText { text: "Thực thi bằng:  Tôi"; color: AppTheme.ink; font.bold: true }
                            HelpText { text: "Ai có quyền truy cập:  Mọi người"; color: AppTheme.ink; font.bold: true }
                        }
                    }
                    HelpText { text: "Bấm Triển khai và làm theo trang cấp quyền của Google cho chính dự án vừa tạo. Kiểm tra đúng tài khoản, đúng mã do thầy cô vừa dán.\n\nKhi hiện kết quả, sao chép URL ứng dụng web, có đuôi /exec. Quay lại BiliClass và bấm Tiếp theo." }
                    HelpText { text: "Không cần bấm Chạy hoặc chọn doPost. BiliClass tự gọi doPost khi thử kết nối và khi dịch bài." }
                    HelpText { text: "Nếu cập nhật một dự án cũ: Triển khai → Quản lý bản triển khai → bút chỉnh sửa → Phiên bản mới → Triển khai. Chỉ lưu mã chưa cập nhật dịch vụ.\n\nNếu tài khoản trường học không có lựa chọn Mọi người, hãy dùng tài khoản cá nhân được phép triển khai hoặc chọn dịch vụ dịch khác." }
                }
                ColumnLayout {
                    visible: guide.step === 2; Layout.fillWidth: true; spacing: 14
                    HelpText { text: "Dán URL ứng dụng web vừa sao chép từ Google vào đây. Không dán đường dẫn trang soạn mã hoặc đường dẫn /dev." }
                    TextField {
                        id: endpoint; objectName: "languageappSetupUrl"
                        Layout.fillWidth: true; implicitHeight: 46
                        selectByMouse: true; maximumLength: 320; readOnly: guide.working
                        placeholderText: "https://script.google.com/macros/s/…/exec"
                        color: AppTheme.ink
                        background: Rectangle { radius: 9; color: AppTheme.field; border.color: endpoint.activeFocus ? AppTheme.blue : AppTheme.line }
                        Accessible.name: "Đường dẫn ứng dụng web Apps Script kết thúc bằng /exec"
                    }
                    HelpText { text: "Mã truy cập sẽ được ghép tự động với đoạn mã ở bước 1. Thầy cô không cần nhập lại mã riêng." }
                    HelpText { text: "Bấm Lưu và thử kết nối. Tool gửi một câu ngắn để kiểm tra dịch vụ thật; chỉ lưu được cấu hình chưa chứng minh đã dịch được." }
                    HelpText {
                        objectName: "languageappSetupResult"
                        visible: !!guide.resultMessage; text: guide.resultMessage
                        color: AppTheme.adapt("#ba581a")
                    }
                    HelpText { text: "Nếu báo thiếu doPost: quay lại bước 1, dán thay toàn bộ Code.gs, rồi cập nhật Phiên bản mới ở bước 2. Bấm Sao chép lại sẽ giữ cùng mã truy cập trong lần thiết lập này." }
                }
                ColumnLayout {
                    visible: guide.step === 3; Layout.fillWidth: true; spacing: 14
                    HelpText { objectName: "languageappSetupSuccess"; text: guide.resultMessage; color: AppTheme.adapt("#168567"); font.bold: true }
                    HelpText { text: "Bây giờ thầy cô có thể sang Chuyển đổi bài giảng để dùng Apps Script.\n\n• Mở lại tool, khởi động lại máy hoặc dịch bài mới: dùng tiếp, không thiết lập lại.\n• Ô mã truy cập trống: tool đã lưu và ẩn mã, không phải bị mất.\n• Chỉ khi sửa mã trên Google mới cần cập nhật bản triển khai.\n\nCác máy dùng cùng dịch vụ chia sẻ hạn mức của tài khoản Google triển khai. Kết nối thành công chưa chứng nhận chất lượng từng bài dịch." }
                }
            }
        }
    }
    onStepChanged: {
        if (scroll.contentItem && scroll.contentItem.contentY !== undefined) scroll.contentItem.contentY = 0
    }
    footer: Frame {
        padding: 12
        background: Rectangle { color: "transparent" }
        contentItem: RowLayout {
          spacing: 10
          Action {
            objectName: "languageappSetupClose"; text: guide.step === 3 ? "Hoàn tất" : "Để sau"
            enabled: !guide.working
            onClicked: guide.close()
          }
          Item { Layout.fillWidth: true }
          Action {
            objectName: "languageappSetupBack"; text: "Quay lại"; visible: guide.step > 0 && guide.step < 3
            enabled: !guide.working
            onClicked: { guide.resultMessage = ""; guide.step-- }
          }
          Action {
            objectName: "languageappSetupNext"
            primary: true
            text: guide.step === 0 ? "Đã dán mã · Tiếp theo" : guide.step === 1 ? "Đã triển khai · Tiếp theo" : guide.working ? "Đang kiểm tra…" : "Lưu và thử kết nối"
            visible: guide.step < 3
            enabled: !guide.working && guide.bridge.googleSettings.languageSetupReady && (guide.step !== 2 || !!endpoint.text.trim())
            onClicked: {
                guide.resultMessage = ""
                if (guide.step < 2) guide.step++
                else guide.bridge.googleSettings.saveLanguageSetup(endpoint.text)
            }
          }
        }
    }
}
