import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: guide
    modal: true
    title: "Bắt đầu với BiliClass"
    width: Math.min(parent.width - 40, 760)
    height: Math.min(parent.height - 50, 660)
    anchors.centerIn: parent
    standardButtons: Dialog.Close
    contentItem: ScrollView {
        clip: true; contentWidth: availableWidth
        ColumnLayout { width: parent.width; spacing: 18
            Repeater {
                model: [
                    {title:"1 · Tài liệu và kiểu chuyển đổi",body:"Kéo thả hoặc chọn PPTX (tối đa 200 MB), DOCX, PDF, TXT, PNG/JPG (tối đa 50 MB); cũng có thể dán nội dung. Tên tệp và Đã nhận tệp hiện sau khi chọn. Điền tên bài, môn và cấp học; khối lớp chỉ hiện theo cấp đã chọn. Tích một trong bốn kiểu và Xem mẫu bố cục. Giữ thiết kế PowerPoint gốc hoặc tạo theo mẫu mới; tài liệu khác dùng mẫu mới. Ghi chú thêm cho ChatGPT không bắt buộc và được ghép vào prompt. Có thể Hiện/Ẩn prompt để xem kịch bản sẽ gửi."},
                    {title:"2 · Đăng nhập ChatGPT và chuyển đổi",body:"Cài đặt → Browser AI → Thêm tài khoản. Đăng nhập Free/Plus trong Chrome riêng rồi kiểm tra và lưu. Bấm Chuyển đổi bài giảng: app tự gửi prompt và tài liệu, nhận PowerPoint rồi chuẩn bị giọng đọc Việt–Anh theo cài đặt đã lưu. Bài mới ưu tiên Plus còn dùng được rồi Free; bài đã gửi giữ tài khoản/cuộc trò chuyện để tránh gửi trùng. Mất phiên/cần xác minh thì xử lý trong Browser AI; hết lượt thì chờ."},
                    {title:"3 · Xem kết quả rồi Dùng để dạy",body:"Xem từng slide hoặc mở toàn bộ bài. Kiểm tra ý nghĩa, thuật ngữ, số liệu, công thức và bố cục. Bấm Dùng để dạy rồi xác nhận đã kiểm tra cả bài một lần để mở trình chiếu; không phải duyệt từng đoạn. Chỉnh sửa chi tiết vẫn có sửa/tách đoạn, khóa, trợ giảng, quiz và lịch sử. Sửa bài xong cần chuyển đổi và xác nhận lại."},
                    {title:"4 · Dạy bằng PowerPoint và mascot",body:"Nguồn được giữ riêng. Prompt yêu cầu giữ đúng số lượng/thứ tự slide PPTX; slide quá kín phải báo hạn chế. Dùng để dạy mở PowerPoint toàn màn hình và mascot trong suốt, kéo tự do; bấm mascot để dùng các thao tác. Voice bám slide thực tế, dừng khi đổi/đóng slide. Tiếng Anh 100% chỉ có Anh trên slide, lời đọc Việt lưu riêng trong ghi chú. Giọng đọc offline cần model hoặc cache phù hợp."},
                    {title:"5 · Câu hỏi hiểu bài",body:"Câu hỏi trong ghi chú PPTX được nhập vào đúng slide ở trạng thái nháp. Thầy cô xem và duyệt riêng trong Trợ giảng & Quiz; xác nhận PowerPoint không tự duyệt đáp án. Câu hỏi không thêm slide và không được đọc lẫn vào voice. Khi dùng lớp học, học sinh cùng Wi-Fi quét QR, không cần tài khoản; đóng câu trước khi công bố đáp án."},
                    {title:"6 · Kết quả và dùng lại bài",body:"Báo cáo luôn ghi số câu trả lời và mẫu số; khảo sát không chấm điểm. Gợi ý level cần cặp câu tương đương được thầy cô gắn nhãn. Xuất gói bài để chuyển máy; máy nhận cần kiểm tra lại. Trong Chỉnh sửa chi tiết, xuất PPTX giữ thiết kế nguồn hoặc dùng mẫu theo cách đã chọn. Hiệu ứng của slide nguồn được giữ ở chế độ giữ thiết kế gốc."},
                    {title:"Khi cần khôi phục hoặc đổi máy",body:"Cài đặt → Sao lưu thư viện. Tự sao lưu mỗi ngày khi mở ứng dụng, giữ tối đa 14 bản tự động. Khôi phục luôn vào thư mục mới, sau đó chọn Mở thư viện. Gỡ ứng dụng giữ dữ liệu trong thư mục BiliClass của tài khoản Windows. Model dịch được cài từ gói .bclanguage trên máy/USB; không tự tải Internet."},
                    {title:"Khi điện thoại không vào được lớp",body:"Chọn đúng địa chỉ Wi-Fi/Ethernet, không chọn 127.0.0.1 cho điện thoại. Cho phép BiliClass trên mạng riêng trong Windows Firewall nếu Windows hỏi. Kiểm tra hai máy cùng mạng và router không bật cô lập thiết bị. Khi đổi mạng, ngắt máy chủ rồi mở lại phiên trong Báo cáo; phát lại QR mới. Mất kết nối vẫn giữ câu trả lời đã được xác nhận."}
                ]
                ColumnLayout { required property var modelData; Layout.fillWidth: true; spacing: 5
                    Label { text: modelData.title; font.pixelSize: 17; font.bold: true; color: "#112650"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                    Label { text: modelData.body; font.pixelSize: 13; color: "#667997"; Layout.fillWidth: true; wrapMode: Text.WordWrap; lineHeight: 1.3 }
                }
            }
        }
    }
}
