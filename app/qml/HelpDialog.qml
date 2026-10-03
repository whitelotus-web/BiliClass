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
                    {title:"2 · Tài khoản Browser AI và chuyển đổi",body:"Thiết lập một lần trong Cài đặt → Browser AI: Thêm tài khoản, bấm Đăng nhập/Kiểm tra, đăng nhập trực tiếp trên web rồi bấm Đã đăng nhập · Kiểm tra trong app. Khi nhập bài, chọn Browser AI · ChatGPT và bấm Chuyển đổi bằng ChatGPT: app gửi prompt cùng tài liệu qua tài khoản đã chọn, chờ tải PPTX và chuẩn bị giọng đọc/mascot. Không dùng API. Nếu web yêu cầu xác minh hoặc phiên hết hạn, đăng nhập/kiểm tra rồi tiếp tục cùng yêu cầu. Chạy ngầm còn phụ thuộc web ChatGPT; đây là tính năng thử nghiệm. Tắt Tự gửi tài liệu trong Browser AI để gửi/tải thủ công; BiliClass ngoại tuyến vẫn dùng model trên máy."},
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
