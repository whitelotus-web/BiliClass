# RC114 — Giao diện sáng/tối và hoàn tất giọng đọc

Cài đặt → Chung có hai lựa chọn Sáng/Tối, lưu ngay trên máy. Bảng màu
dùng chung cho trang chính, điều khiển, hộp thoại, menu và Mascot. Icon
giao diện dùng màu theo chế độ; hình bài chiếu, logo và nhân vật giữ màu
gốc. Giữ nguyên các tab Cài đặt. Hộp chọn tệp dùng giao diện Qt ở chế độ
tối để đi cùng bảng màu ứng dụng.

Trang tạo giọng có ô xem trước 16:9 khi thu gọn. Phóng to rồi ẩn sẽ trở
về ô nhỏ, dùng lại ảnh đã tải. Tạo giọng hoàn tất chuyển sang màn riêng
“Đã tạo giọng đọc bài giảng”, có bản xem trước, nghe, mở PowerPoint,
tải và trở lại Thư viện. Mở cấu hình là hành động riêng; thông báo đến
sau không được mở lại phần người dùng vừa thu gọn.

Thông báo tác vụ ở chân trang là chữ thường khi đang ở đúng màn hình.
Ở màn khác, riêng thông báo trở thành nút quay lại tác vụ. Giữ đúng
tab Cài đặt của công việc và bảo vệ nội dung đang sửa chưa lưu. Nút
dừng vẫn độc lập với nút quay lại.

Menu chuột phải Mascot vừa hai dòng. Hàng Tự động/Đang hiện/Toàn slide
căn giữa, bỏ câu nhắc nghe lại và các thông báo phát âm thanh thông
thường gây đổi chiều cao. Mascot 60–65 px có bảng rộng 280 px, nút cao
30 px và khoảng cách 5 px; cỡ 80 px vẫn dùng bảng 320 px. Các trạng thái
lỗi hoặc không có giọng vẫn được thông báo.

Slide trống trong bài chuyển đổi không còn tính là thiếu bản dịch.
Trạng thái duyệt cho lớp học chỉ hiện khi tính năng lớp học được bật.
Lời đọc tự bỏ hai dấu nguồn đã nhận diện (19wx568/19lt568), giữ câu có
nghĩa, bỏ dòng ghi công Gemini Notebook chỉ khi đi cùng dấu nguồn.
Văn bản PowerPoint không bị sửa bởi bước lọc lời đọc. Cache của phần
không đổi được giữ nguyên. Job thử lại một lần khi tạo một đoạn bị lỗi,
vẫn dừng sau ba đoạn lỗi liên tiếp và hỗ trợ hủy.

Khi mở trang voice của bản cũ đã chạy xong nhưng bỏ sót chỉ vì các dấu
nguồn này, ứng dụng tự tạo tiếp tối đa tám đoạn mới, một lần mỗi phiên.
Không tự tổng hợp khi chỉ duyệt Thư viện. File WAV vẫn được kiểm tra;
ghi âm hỏng, nội dung lạ hoặc job chưa xong không được báo hoàn tất.
Thư viện tiếp tục giữ một mục cho bài: tạo song ngữ lưu ngay, tạo giọng
cập nhật chính mục đó; bản nguồn không bị ghi đè bằng file gắn âm thanh.

Căn chữ tràn chuyển giãn dòng cố định sang tỉ lệ theo font, để co font
không để lại dòng quá cao. Giữ giới hạn số lượt sửa và chỉ nhận trang
đã render, không có lỗi mới. Kiểm tra trên bản sao Bài 6 giảm số trang
bị đo tràn từ 13 xuống 11; chưa thể tuyên bố mọi bố cục nguồn đạt chuẩn.
Không xóa lỗi thật hoặc tự duyệt tính đúng đắn của nội dung giảng dạy.

Kiểm tra bằng virtual environment: 133 ca về giao diện lưu trữ, lời đọc,
WAV/cache, workspace, kiểm tra bài và căn chữ đạt; Ruff đạt. Qt smoke
kiểm tra sáng/tối qua các trang và tab Cài đặt, hộp thoại, xem trước,
nút tác vụ, bảo vệ bản sửa, bảng Mascot 60/80/110/150 px. Kiểm tra màn
voice hoàn tất dùng bản xem trước PowerPoint thật ở 1080×700 và
1366×850. Qt menu và giao diện cũng đạt tại DPI 150%; không cảnh báo
QML. Đã xem ảnh sáng/tối, màn hoàn tất, bảng nhỏ và menu.

Gói phát hành từ commit `a159f5790b6274a0f84493735dfa26792a97ec23`,
ZIP 1.249.962.134 byte, SHA-256
`8c7be5cfedc672e1b6d46c6d731cc4dcb9f6134b7571c0e348199260bb50c2b0`.
Manifest/ZIP đã xác minh; 50 QML/qmldir trong gói khớp nguồn đã kiểm
tra. Bản đóng gói chạy smoke giao diện tối với thư viện tạm, thoát mã 0.
GitHub xác nhận digest khớp và đã phát hành tag `v1.0.0rc114`.

Đã cài, mở RC114 qua Explorer tại trang Cài đặt, kiểm tra cửa sổ chính,
Mascot, shortcut và biểu tượng native. Khởi động có một lần thăm dò
quá 500 ms rồi đạt ba lần phản hồi liên tiếp. Sau cài, hash nguồn và
revision của 18 bản ghi bài (kể cả bài trong thùng rác), 1.658 WAV được
tham chiếu, lựa chọn giọng và khóa dịch mã hóa khớp trước cài. PowerPoint
độc lập và ứng dụng RC80 được giữ nguyên. Bài Bài 6 hiện có 436 đoạn
cache được bảo toàn; kế hoạch phục hồi chỉ bổ sung hai đoạn thành 438,
không ghi lại các đoạn đã hợp lệ. Phục hồi bắt đầu khi mở trang voice.
