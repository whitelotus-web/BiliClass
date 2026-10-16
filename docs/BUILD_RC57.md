# RC57 — Lớp học, kết quả và mascot, 17/10/2026

[GitHub Release RC57](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc57).

- Nguồn: `19131a32ac56b28283209c0e74e443bffe8ff12f`.
- ZIP: `BiliClass-RC57-Windows.zip`, 837273703 byte, 4167 tệp.
- ZIP SHA-256: `26ebdec8c3ab42516f61a6e9959fa10ddc4cc860d24e3ac57453d56ea47ef944`.
- EXE SHA-256: `6cbb58eb5a1aa42afcece3eedc91755a5b8bfda746cdb9abb10857f83bc1e98a`.

[Hướng dẫn và báo cáo chức năng](CLASSROOM_MASCOT_RC57.md) ghi rõ cơ chế lớp,
câu hỏi, mạng, khôi phục, kết quả và các giới hạn mascot. Trang chủ chuyển
sang bảng làm việc gọn. Báo cáo nằm trong Lớp học, kho thuật ngữ nằm trong
Cài đặt → Dữ liệu; dữ liệu và cơ chế thuật ngữ khi dịch được giữ lại.

59 kiểm thử liên quan qua. Qt thật kiểm tra mở lớp đến học sinh WebSocket,
đếm ngược, giữ câu đang chọn qua poll, đóng/công bố, ngắt/mở lại giữ phản hồi,
kết thúc và CSV. Các Qt Trang chủ/thư viện/kho nâng cao/mascot không có cảnh
báo QML. Lượt PowerPoint thật với 3 slide và giọng Anh tại máy qua. 50 kết nối
loopback nhận đủ 50 phản hồi, giữ đúng khi gửi trùng/kết nối lại và khởi động
lại; đây chưa phải thử Wi-Fi trường, 200 thiết bị hoặc Windows sạch.

Bộ cài dùng runtime/model đã có ở RC56, biên dịch lại toàn bộ module app và
đóng gói các QML đã thay đổi. Mỗi tệp ZIP đã kiểm SHA-256/CRC; file thực thi, model,
dữ liệu giáo viên, giọng, key và báo cáo riêng không nằm trong commit nguồn.

Bản EXE đã cài chạy ngoại tuyến qua DOCX/PPTX, kho SQLite/lịch sử/gói bài,
tổng hợp WAV Việt/Anh/trộn bằng cùng giọng VieNeu, thay tốc độ và dùng cache.
Máy chủ lớp học spawn từ EXE, trang học sinh đi kèm, WebSocket xác thực/ACK,
kết quả lưu và sao lưu/khôi phục đều qua. Mọi dữ liệu của lượt thử nằm trong
thư mục dùng thử riêng; không dùng key Google hoặc thư viện giáo viên.

RC57 đã mở qua Explorer, ngoài job của launcher và vẫn chạy sau khi launcher
bị đóng; 10 lần kiểm tra phản hồi qua. Shortcut Desktop/Start menu trỏ RC57.
17 bản ghi bài giảng, 992 WAV và cấu hình hiện có giữ nguyên, không tự tạo lại
giọng. Trình cập nhật công khai từ RC34/RC56 nhận đúng RC57, dung lượng và
SHA-256; bản RC57 không tự báo lại chính nó.
