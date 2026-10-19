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
    contentItem: ContentScrollView {
        contentWidth: availableWidth
        ColumnLayout { width: parent.width; spacing: 18
            Repeater {
                model: !bridge.experimentalTeaching ? [
                    {title:"1 · Chuyển đổi bài giảng", body:"Chọn file PowerPoint, kiểu chuyển đổi và thiết kế. BiliClass dịch và lưu bản trình chiếu trên máy. Có thể giữ thiết kế gốc hoặc dùng mẫu BiliClass. Xem trước kết quả để đối chiếu nội dung, số liệu và công thức; chữ trong ảnh vẫn có thể cần kiểm tra."},
                    {title:"2 · Tạo giọng đọc local", body:"Chọn cặp Việt–Mỹ, tốc độ và tiếng Anh, tiếng Việt hoặc cả hai. Tiếng Việt dùng VieNeu, tiếng Anh dùng giọng Mỹ Kokoro, chạy trên máy. Chọn cả hai tạo hai loa độc lập. Nghe thử dùng mẫu dài theo ngôn ngữ đang chọn; cặp và tốc độ gần nhất được nhớ cho lần tạo mới."},
                    {title:"3 · Dạy bằng PowerPoint và Mascot", body:"Mở bài từ thư viện hoặc chọn trên Mascot, rồi bấm F5 để trình chiếu. Dùng Trước/Sau, loa Anh/Việt và âm lượng. Chuột trái lên Mascot để mở/thu bảng; chuột phải mở Cài đặt hoặc Ẩn mini. Mở lại Mascot từ thanh bên khi cần."},
                    {title:"4 · Tìm và tải bài", body:"Thư viện có tìm kiếm, bộ lọc, xem thẻ hoặc danh sách. Shift chọn theo dải; kéo chuột qua các bài để chọn nhiều. Thanh tìm kiếm và tác vụ giữ cố định khi cuộn. Tệp tải lấy theo tên bài và ghi rõ ngôn ngữ cùng giọng đọc đã tạo."},
                    {title:"5 · Lưu và khôi phục dữ liệu", body:"Bài giảng được lưu trên máy. Trong Cài đặt → Dữ liệu, dùng Sao lưu dữ liệu, Khôi phục bản sao hoặc Đổi nơi lưu. Khôi phục vào thư mục mới, kiểm tra rồi mở lại; thư viện trước vẫn được giữ. Kiểm tra cập nhật trong Thông tin BiliClass."}
                ] : bridge.googleTranslation ? [
                    {title:"1 · Cấu hình Google Dịch", body:"Mở Cài đặt → Google Dịch. Bật Cloud Translation API và thanh toán trên Google Cloud, nhập key rồi Lưu cấu hình. Mỗi dòng một key; có thể dùng Tên dự án | key để nhóm các key cùng dự án. Key được mã hóa trên tài khoản Windows, không đi cùng bản sao lưu."},
                    {title:"2 · Chọn tài liệu và bố cục", body:"Chọn PPTX có chữ chỉnh sửa được, DOCX, PDF có chữ, TXT hoặc dán nội dung. Điền tên bài, môn, cấp và khối lớp. Chọn Song ngữ Việt–Anh để tự căn từng vùng, hoặc Tiếng Anh 100% để thay chữ tại vị trí gốc. Giữ thiết kế PowerPoint gốc hoặc chọn một trong ba mẫu mới. Vùng song ngữ quá chật có thể dùng trang tiếp nối; chữ trong ảnh và hiệu ứng phức tạp cần đối chiếu."},
                    {title:"3 · Chuyển đổi và tải về", body:"Bấm Chuyển đổi bài giảng. BiliClass tự dịch chữ, sắp xếp và lưu PowerPoint tại máy. Màn hình có phần trăm và thời gian; phần đã dịch được lưu để tiếp tục nếu lỗi mạng. Khi xong tự sang Tạo giọng đọc bài giảng, nạp sẵn bài vừa chuyển. Có thể tải PowerPoint không giọng ngay hoặc cấu hình tạo giọng. Chữ trong ảnh, biểu đồ, công thức và hiệu ứng chưa kiểm chứng vẫn cần đối chiếu."},
                    {title:"4 · Tạo giọng đọc khi cần", body:"Chọn Tiếng Anh, Tiếng Việt hoặc Việt + Anh rồi bấm Tạo giọng đọc. VieNeu chạy tại máy bằng giọng và tốc độ đã lưu. Khi đủ giọng, tích Kèm giọng đọc khi tải PowerPoint: file có nút loa VI/EN trên slide, dùng được độc lập với BiliClass. Chỉ nhúng lời đọc tĩnh; lời đọc ẩn theo hiệu ứng vẫn dùng trong BiliClass. Bỏ tích để tải bản không voice."},
                    {title:"5 · Xem và dùng để dạy", body:"Xem lại bản trình chiếu, nội dung, thuật ngữ và các phần cần rà soát. Bấm Mở bài giảng để dạy và xác nhận nội dung. PowerPoint mở ở trạng thái sẵn sàng, Mascot gắn với đúng bài và bản giọng. Bấm Trình chiếu (F5) trên Mascot. Thu nhỏ BiliClass vẫn dùng được; chọn/đổi bài ngay trên Mascot hoặc từ thư viện. Quiz và đáp án vẫn cần duyệt riêng."},
                    {title:"6 · Hạn mức và dữ liệu", body:"500.000 ký tự/tháng là tín dụng theo điều kiện Google, không phải hạn mức riêng mỗi key. BiliClass chỉ đếm lượng dùng cục bộ theo nhóm, không thấy số dư hay lượt dùng ở ứng dụng/máy khác. Đặt thêm quota trong Google Cloud để kiểm soát chi phí. Bài học lưu trên máy; sao lưu hoặc xuất gói bài để chuyển máy. Key cần nhập lại ở máy mới. Kiểm tra cập nhật tại Cài đặt → Thông tin BiliClass."}
                ] : [
                    {title:"1 · Tài liệu và kiểu chuyển đổi",body:"Kéo thả hoặc chọn PPTX (tối đa 200 MB), DOCX, PDF, TXT, PNG/JPG (tối đa 50 MB); cũng có thể dán nội dung. Tên tệp và Đã nhận tệp hiện sau khi chọn. Điền tên bài, môn và cấp học; khối lớp chỉ hiện theo cấp đã chọn. Tích một trong bốn kiểu và Xem mẫu bố cục. Giữ thiết kế PowerPoint gốc hoặc tạo theo mẫu mới; tài liệu khác dùng mẫu mới. Ghi chú thêm cho ChatGPT không bắt buộc và được ghép vào prompt. Có thể Hiện/Ẩn prompt để xem kịch bản sẽ gửi."},
                    {title:"2 · Đăng nhập ChatGPT và chuyển đổi",body:"Cài đặt → Browser AI → Thêm tài khoản. Đăng nhập Free/Plus trong Chrome riêng rồi kiểm tra và lưu. Bấm Chuyển đổi bài giảng: app tự gửi prompt và tài liệu, nhận PowerPoint rồi chuẩn bị giọng đọc Việt–Anh theo cài đặt đã lưu. Bài mới ưu tiên Plus còn dùng được rồi Free; bài đã gửi giữ tài khoản/cuộc trò chuyện để tránh gửi trùng. Mất phiên/cần xác minh thì xử lý trong Browser AI; hết lượt thì chờ."},
                    {title:"3 · Xem kết quả rồi Dùng để dạy",body:"Xem từng slide hoặc mở toàn bộ bài. Kiểm tra ý nghĩa, thuật ngữ, số liệu, công thức và bố cục. Bấm Dùng để dạy rồi xác nhận đã kiểm tra cả bài một lần để mở trình chiếu; không phải duyệt từng đoạn. Chỉnh sửa chi tiết vẫn có sửa/tách đoạn, khóa, trợ giảng, quiz và lịch sử. Sửa bài xong cần chuyển đổi và xác nhận lại."},
                    {title:"4 · Dạy bằng PowerPoint và mascot",body:"Nguồn được giữ riêng. Prompt yêu cầu giữ đúng số lượng/thứ tự slide PPTX; slide quá kín phải báo hạn chế. Mở bài giảng để dạy gắn PowerPoint với Mascot; bấm Trình chiếu (F5) khi sẵn sàng. Mascot trong suốt, kéo tự do; bấm mascot để dùng các thao tác hoặc chọn bài khác. Voice bám slide thực tế, dừng khi đổi/đóng slide. Tiếng Anh 100% chỉ có Anh trên slide, lời đọc Việt lưu riêng trong ghi chú. Giọng đọc offline cần model hoặc cache phù hợp."},
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
