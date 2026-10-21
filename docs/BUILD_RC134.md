# RC134 — Thu gọn icon trạng thái giọng

Theo yêu cầu thu nhỏ sau RC133, icon loa VI/EN trong thư viện còn
24 × 22 px, loa gạch chéo xám 18 × 18 px. Nhãn cao 28 px, hai icon
cách nhau 4 px; giữ vùng bấm ngang và tooltip đầy đủ. Tiếp tục dùng
đúng hai ảnh đã gửi, EN xanh dương và VI tím trên cả nền sáng/tối.

RC133 đã đóng gói nhưng chưa cài; bản RC134 là bản mở để kiểm tra.

Xác minh bằng `.venv`: 14 pytest thư viện/giao diện đạt. Qt smoke
thư viện đạt ở 1080/1366/1920, dạng thẻ/danh sách, không cảnh báo
QML. Đã xem icon nhỏ trên nền sáng/tối, gồm VI, EN và cả hai.
