# RC112 — Căn giữa số slide, gọn trang bài giảng

Căn giữa cụm Trước – số slide – Sau dưới bản xem trước của trang bài
giảng. Bỏ dòng lặp số slide, trạng thái lưu và trạng thái giọng đọc.
Các nút Mở PowerPoint, Tải PowerPoint và Tạo giọng đọc vẫn ở phía trên.
Hàng nghe giọng đã tạo trên trang voice giữ bố cục hiện có.

Qt smoke dùng thư viện tạm tại 1080×700, 1366×850 và 1680×980: tâm số
slide khớp tâm bản xem trước, sai lệch 0 pixel; dòng thừa không còn;
các nút đầy đủ, không có cảnh báo QML. Đã xem ảnh chụp giao diện.
Sáu ca xem trước và Ruff đạt. Hai kỳ vọng cũ trong test đã được cập nhật
theo hành vi có từ trước: xem trước vẫn dùng được khi Office đang mở
trình chiếu và không ngắt âm thanh của trình chiếu đang chạy. Không sửa
logic xem trước hay âm thanh trong bản này.

Bốn icon đầu bảng Mascot chuyển từ PNG thu nhỏ sang SVG cùng biểu tượng:
mũi tên thu gọn, dấu hỏi/bàn phím, bánh răng và mắt gạch chéo. Nét dày
2–2,2 đơn vị trên khung 24, đầu nét và góc bo tròn, màu thống nhất.
Ảnh vector được raster hóa theo DPI ở độ phân giải gấp đôi và lọc mipmap.
Menu chuột phải dùng chung SVG; ảnh PNG nguồn vẫn được giữ nguyên.
Qt context smoke đạt ở tỉ lệ 100% và 150%: bấm, mở Cài đặt, ẩn/mở lại,
ba cỡ Mascot và khoảng cách nút đều đúng, không cảnh báo QML. Đã xem
ảnh đầu bảng và menu ở kích thước thực.

Gói phát hành dựng từ commit `578c1d931393c199140af5acf88f93c19a44c7e0`,
ZIP 1.249.945.407 byte, SHA-256
`6815a8ad5cd1e8491d02233c5a657660213f2573baf561984dcaf6bbb73917a8`.
Manifest và ZIP được xác minh; bốn QML và bốn SVG trong gói khớp nguồn
đã kiểm tra. GitHub xác nhận digest khớp; tag `v1.0.0rc112` đã phát hành.

Đã cài và mở bản RC112 qua Explorer tại trang bài giảng; cửa sổ chính,
Mascot, shortcut và biểu tượng taskbar đúng. Khởi động có ba lần thăm
dò quá 500 ms rồi đạt ba lần phản hồi liên tiếp trong ngưỡng. Hash nguồn,
revision bài, 1.224 WAV được tham chiếu, lựa chọn giọng và khóa dịch mã
hóa khớp trước/sau. PowerPoint độc lập của người dùng được giữ nguyên.

Đã tìm nguyên nhân của câu hỏi về tiêu đề lặp: ở ví dụ Warm-up, dòng
tiêu đề được trích xuất với kind=body. ReadingProgress hiện chỉ bỏ tiêu
đề đã nghe ở trang liền trước trong chế độ tự động của Mascot, còn âm
thanh xuất theo slide giữ đầy đủ nội dung. RC112 chưa thay đổi chính
sách này; hướng đề xuất là nhận diện tiêu đề chắc chắn hơn và tránh
đọc lặp khi đọc nối tiếp, vẫn giữ ngữ cảnh khi mở thẳng hoặc quay lại.
