import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property string formatLabel: ""
    property string formatId: "parallel_columns"
    property bool keepSource: true
    property string templateName: ""
    property string subject: ""
    property string education: ""
    property string grade: ""
    radius: 9; color: AppTheme.adapt("#f5f8fd"); border.color: AppTheme.adapt("#e0e8f3")
    implicitHeight: content.implicitHeight + 24
    ColumnLayout {
        id: content
        anchors.fill: parent; anchors.margins: 12; spacing: 5
        Label {
            objectName: "conversionConfigurationTitle"
            text: "Cấu hình đã chọn · " + card.formatLabel + " · " +
                (card.keepSource ? "Giữ thiết kế gốc" : card.templateName || "Mẫu BiliClass")
            color: AppTheme.adapt("#112650"); font.pixelSize: 13; font.weight: Font.DemiBold
            Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            objectName: "conversionConfigurationExplanation"
            text: (card.formatId === "english_only" ? "Nội dung trên slide chuyển sang tiếng Anh; lời Việt lưu riêng cho trợ lý. "
                   : card.formatId === "integrated_keywords" ? "Giữ câu tiếng Việt và tích hợp các thuật ngữ tiếng Anh đã chọn. "
                   : card.formatId === "sentence_pairs" ? "Mỗi ý tiếng Việt có bản tiếng Anh ngay dưới để đối chiếu khi dạy. "
                   : "Mỗi trang có nội dung Việt và Anh để đối chiếu khi dạy. ") +
                (card.keepSource ? "Giữ nền, hình và công thức; vùng chật có thể thêm trang tiếp nối. Chữ trong ảnh và hiệu ứng cần kiểm tra."
                                 : "Dàn lại nội dung theo mẫu đã chọn, tự chia trang khi dài. Hiệu ứng của bản gốc không được tái dựng.")
            color: AppTheme.adapt("#667997"); font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
        Label {
            objectName: "conversionConfigurationNextStep"
            text: [card.subject || "Chưa chọn môn học", card.education, card.grade ? "Lớp " + card.grade : ""].filter(function(value) { return !!value }).join(" · ") +
                ". Sau chuyển đổi, kiểm tra bài và sang Tạo giọng đọc nếu cần nút loa Việt, Anh hoặc cả hai."
            color: AppTheme.adapt("#667997"); font.pixelSize: 12; Layout.fillWidth: true; wrapMode: Text.WordWrap
        }
    }
}
