# RC121 — Tab Mascot giãn theo cửa sổ

Bỏ giới hạn 1180 px và căn giữa riêng của nội dung tab Mascot. Nội dung
giờ chiếm toàn bộ chiều rộng vùng Cài đặt, giữ cùng lề với các tab khác.
Ba thẻ chọn/xem trước và các ô cấu hình giãn cùng nhau; bố cục màn hẹp
và lựa chọn đã lưu giữ nguyên.

Kiểm bằng `.venv`: 11 pytest về giao diện/cài đặt đồng hành đạt.
Qt thật kiểm sáng/tối tại 1080/1366/1920, phóng to cửa sổ rồi thu về
1080, cả cỡ hiển thị 100% và 150%. Nội dung không còn dải trống do
giới hạn chiều rộng, không tràn ngang; nút và cuộn vẫn dùng được,
không có cảnh báo QML.

Nguồn `1.0.0rc121`; dựng một lần từ commit đã kiểm, dùng runtime/model
RC120 với manifest SHA256. Commit được ghi trong BUILD_INFO.json.
Gói, dữ liệu cá nhân và báo cáo thử không đưa vào Git. Thông tin gói và
đối chiếu dữ liệu sau cài đặt được bổ sung sau khi xác minh.
