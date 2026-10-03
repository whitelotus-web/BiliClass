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
                    {title:"1 · Tài liệu, level và cách trình bày",body:"Chọn PPTX, DOCX, PDF, TXT, ảnh PNG/JPG hoặc dán nội dung. Điền tên bài, môn, khối, chọn L0–L4 và cách sắp xếp Việt–Anh. PowerPoint có thể giữ thiết kế gốc hoặc dùng mẫu BiliClass. Tài liệu khác dùng mẫu. Bấm Xem slide mẫu để xem hình minh họa và từng loại slide."},
                    {title:"2 · Chuyển đổi bằng ChatGPT trong browser",body:"Chọn ChatGPT trong browser, bấm Chuẩn bị & mở ChatGPT. BiliClass tạo prompt và gói tài liệu tại máy. Sao chép prompt, mở thư mục tài liệu, đính kèm tệp trong ChatGPT bằng tài khoản của thầy cô rồi gửi. Tải file .pptx kết quả và bấm Nhận PowerPoint từ ChatGPT. Không dùng API; tài liệu chỉ gửi lên ChatGPT khi thầy cô thao tác trong browser. Có thể chọn BiliClass ngoại tuyến nếu muốn dùng model đã cài trên máy."},
                    {title:"3 · Xem kết quả rồi Dùng để dạy",body:"Xem từng slide hoặc mở toàn bộ bài. Kiểm tra ý nghĩa, thuật ngữ, số liệu, công thức và bố cục. Bấm Dùng để dạy rồi xác nhận đã kiểm tra cả bài một lần để mở trình chiếu; không phải duyệt từng đoạn. Chỉnh sửa chi tiết vẫn có sửa/tách đoạn, khóa, trợ giảng, quiz và lịch sử. Sửa bài xong cần chuyển đổi và xác nhận lại."},
                    {title:"4 · Dạy với PowerPoint đã nhận",body:"BiliClass giữ nguyên PowerPoint nhận từ ChatGPT và trình chiếu bằng Office sau khi thầy cô xác nhận. Mascot đọc cặp Việt–Anh nhận diện được từ chữ/ghi chú slide; slide chưa có cặp rõ ràng vẫn chiếu được nhưng chưa có giọng đọc song ngữ. Sau khi nhận file, không cần Internet để chiếu; giọng đọc cần gói model trên máy. Không cần tạo quiz hay audio trước. Trợ giảng nổi có thể thu gọn hoặc đóng bằng Escape."},
                    {title:"5 · PowerPoint và câu hỏi",body:"Tệp PPTX có thể mở bằng PowerPoint đã cài, chỉ đọc. Tiến/lùi giữ xử lý animation của Office. Theo slide hiện tại đồng bộ đoạn; thầy cô đang sửa nội dung thì không tự chuyển. Học sinh dùng cùng mạng Wi-Fi, quét QR, không cần tài khoản. Đóng câu trước khi công bố đáp án. Kiểm tra lại tạo lượt riêng."},
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
