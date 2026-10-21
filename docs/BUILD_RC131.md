# RC131 — Thu gọn khoảng cách cấu hình giọng đọc

Bỏ lề trên bổ sung 16/48 px của khung Cấu hình tạo giọng đọc khi chưa
chọn bài. Khung dùng khoảng cách chung 18 px ngay dưới hàng chọn bài
trong thư viện, giống các phần còn lại. Giữ chiều cao, nội dung khung
và hành vi sau khi đã chọn bài.

Xác minh bằng `.venv`: 8 pytest giao diện đạt; Qt smoke Chuyển đổi/
Tạo giọng ở 1080×700, 1366×768, 1366×850 và 1920×1080 đạt, không
cảnh báo QML. Đã xem ảnh bố cục Tạo giọng với khoảng cách mới.
