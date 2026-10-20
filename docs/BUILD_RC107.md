# RC107 — Chốt tự hiện slide sau khi tạo giọng

Bao gồm thay đổi giọng đọc, icon và xem trước của RC106. Kiểm tra executable
RC106 phát hiện trường hợp job tạo xong một cặp/ngôn ngữ khác với cấu hình
đang chọn trên màn hình: ảnh đã tải nhưng khung vẫn có thể ẩn. RC106 chưa
được mở cho người dùng hay phát hành trên GitHub.

QML theo dõi một lần chuyển từ job đang chạy sang hoàn tất của đúng bài,
tự mở xem trước khi thành công. Không phụ thuộc cấu hình nháp đang chọn.
Các thông báo sau đó không mở lại khi giáo viên đã chủ động ẩn khung.
Giọng chưa hoàn tất, bị hủy hay của bài khác không kích hoạt hành vi này.

Kiểm tra Qt riêng bổ sung cả trường hợp đổi cặp đang chọn và ẩn thủ công.
Bản giọng và nguồn bài cá nhân đã sửa trước đó giữ nguyên; không tạo lại
âm thanh vì thay đổi này chỉ ở giao diện.
