# RC124 — Cân đối cấu hình tạo giọng đọc

Chia hàng ngôn ngữ/vị trí loa thành hai nửa bằng nhau. Ba lựa chọn
Tiếng Anh, Tiếng Việt, Cả Anh và Việt dùng ô cùng kiểu với cấu hình
Chuyển đổi, có mô tả ngắn và trạng thái chọn. Nhóm này căn giữa nửa
trái; vị trí loa và dòng hướng dẫn căn giữa nửa phải. Màn hẹp xếp hai
nhóm thành hai hàng. Giữ ba lựa chọn trong một hàng và đủ chữ mô tả.

Ẩn phần thông tin bài trống khi chưa chọn bài. Khung cấu hình tiến lên
gần bộ chọn bài, tăng đệm trong khung và giãn các hàng. Ở 1366×850,
tiêu đề lên khoảng 24 px và khung có mô tả cao khoảng 270 px. Màn nhỏ
dùng khoảng trống phía trên ngắn hơn; có thể cuộn tới các điều khiển.

Không thay tạo/cache giọng hoặc lưu lựa chọn. Quy tắc bật/tắt theo lời
Anh/Việt có sẵn và trạng thái đang xử lý được giữ trên các ô mới.

Kiểm bằng `.venv`: 15 pytest cấu hình/lời đọc đạt. Qt thật kiểm sáng/tối,
1080/1366/1920, có/chưa chọn bài, hiển thị 100% và 150%; hai nửa bằng
nhau, từng nhóm căn giữa, mô tả hiện đủ, các hàng không đè nhau. Bấm
đổi cả ba chế độ và sáu vị trí loa vẫn cập nhật tức thì, không tải lại
ảnh slide hay chạy tác vụ tạo giọng. Không có cảnh báo QML. Ảnh fixture,
thư viện thử và báo cáo giữ ngoài Git.

Nguồn `1.0.0rc124`. Dựng một lần sau commit đã kiểm, dùng runtime RC123
có manifest SHA256. Thông tin gói/cài đặt bổ sung sau xác minh.
