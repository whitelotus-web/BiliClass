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
                model: bridge.googleTranslation ? [
                    {title:"1 · Cấu hình Google Dịch", body:"Mở Cài đặt → Google Dịch. Bật Cloud Translation API và thanh toán trên Google Cloud, nhập key rồi Lưu cấu hình. Mỗi dòng một key; có thể dùng Tên dự án | key để nhóm các key cùng dự án. Key được mã hóa trên tài khoản Windows, không đi cùng bản sao lưu."},
                    {title:"2 · Chọn tài liệu và bố cục", body:"Chọn PPTX có chữ chỉnh sửa được, DOCX, PDF có chữ, TXT hoặc dán nội dung. Điền tên bài, môn, cấp và khối lớp. Chọn Song ngữ Việt–Anh để tự căn từng vùng, hoặc Tiếng Anh 100% để thay chữ tại vị trí gốc. Giữ thiết kế PowerPoint gốc hoặc chọn một trong ba mẫu mới. Vùng song ngữ quá chật có thể dùng trang tiếp nối; chữ trong ảnh và hiệu ứng phức tạp cần đối chiếu."},
                    {title:"3 · Chuyển đổi và tải về", body:"Bấm Chuyển đổi bài giảng. BiliClass tự dịch chữ, sắp xếp và lưu PowerPoint tại máy. Màn hình có phần trăm và thời gian; phần đã dịch được lưu để tiếp tục nếu lỗi mạng. Khi xong có thể Tải PowerPoint ngay, không cần tạo voice. Chữ trong ảnh, biểu đồ, công thức và hiệu ứng chưa kiểm chứng vẫn cần đối chiếu."},
                    {title:"4 · Tạo giọng đọc khi cần", body:"Chọn Tiếng Anh, Tiếng Việt hoặc Việt + Anh rồi bấm Tạo giọng đọc. VieNeu chạy tại máy bằng giọng và tốc độ đã lưu. Khi đủ giọng, tích Kèm giọng đọc khi tải PowerPoint: file có nút loa VI/EN trên slide, dùng được độc lập với BiliClass. Chỉ nhúng lời đọc tĩnh; lời đọc ẩn theo hiệu ứng vẫn dùng trong BiliClass. Bỏ tích để tải bản không voice."},
                    {title:"5 · Xem và dùng để dạy", body:"Xem lại bản trình chiếu, nội dung, thuật ngữ và các phần cần rà soát. Xác nhận bài trước khi Dùng để dạy. PowerPoint mở toàn màn hình; mascot điều khiển slide và đọc phần đã chuẩn bị. Quiz và đáp án vẫn cần duyệt riêng."},
                    {title:"6 · Hạn mức và dữ liệu", body:"500.000 ký tự/tháng là tín dụng theo điều kiện Google, không phải hạn mức riêng mỗi key. BiliClass chỉ đếm lượng dùng cục bộ theo nhóm, không thấy số dư hay lượt dùng ở ứng dụng/máy khác. Đặt thêm quota trong Google Cloud để kiểm soát chi phí. Bài học lưu trên máy; sao lưu hoặc xuất gói bài để chuyển máy. Key cần nhập lại ở máy mới. Kiểm tra cập nhật tại Cài đặt → Thông tin BiliClass."}
                ] : [
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
