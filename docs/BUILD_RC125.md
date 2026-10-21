# RC125 — Căn giữa nghe giọng và tách kết quả theo tab

Căn giữa nhóm Nghe giọng Anh/Việt và Dừng nghe dưới slide kết quả.
Chiều rộng chỉ tính những nút hiện theo ngôn ngữ của bản giọng, nên
bản Anh, Việt và cả hai đều căn giữa. Nút tải ở trang kết quả và khung
giọng đã hoàn tất ghi rõ “Tải PowerPoint có giọng”. Giữ luồng xuất có
nhúng giọng hiện có.

Nút cam “Mở bài vừa tạo giọng” chỉ hiện tại tab Tạo giọng đọc khi có
kết quả giọng. Tab Chuyển đổi giữ nút kết quả chuyển đổi riêng, không
hiện nút kết quả giọng. Hai kết quả được giữ riêng khi chuyển qua lại
hai tab. Bản này gồm cả bố cục và mô tả cấu hình tạo giọng của RC124.

Kiểm bằng `.venv`: 6 pytest cấu hình/kết quả giọng gần nhất đạt.
Qt thật dùng thư viện tạm, slide và WAV fixture, không tạo giọng qua
dịch vụ. Kiểm căn giữa cả ba tổ hợp nút nghe ở 1080/1366/1920, giao
diện sáng/tối và tỷ lệ hiển thị 100%/150%. Kiểm chưa có kết quả,
chỉ có kết quả giọng và có hai kết quả khác bài; mỗi tab mở lại đúng
bài tương ứng, giữ đúng biến thể giọng. Không có cảnh báo QML.

Nguồn `1.0.0rc125`. Dựng một lần sau commit đã kiểm, dùng runtime
RC124 có manifest SHA256. Thông tin gói/cài đặt bổ sung sau xác minh.
