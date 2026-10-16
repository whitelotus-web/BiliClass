# RC53 — chọn bài trực tiếp, 16/10/2026

[GitHub Release RC53](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc53).

- Nguồn: `a063abd82f266ead2a82417d024cc9f3aad6f456`.
- ZIP: `BiliClass-RC53-Windows.zip`, 837227901 byte, 4165 tệp.
- ZIP SHA-256: `8b9b3a51571b8d1db92e4b5dc2e544a37a86e1d3119a8d9cb61fadd41925b99e`.
- EXE SHA-256: `e5ddf1146a8876e8624e0ac3e9f8c2ffdf062373414f8ba4744a1aacda6820a2`.

Bỏ nút Chọn bài/Xong và cờ chế độ chọn. Ô chọn từng bài cùng Chọn tất cả /
Bỏ chọn / Tải đã chọn / Xóa đã chọn luôn hiện trong Thư viện; giữ thanh
công cụ một hàng và ô tích 16 px. Trang chủ giữ danh sách ngắn như cũ.

17 kiểm thử liên quan qua. Qt dùng 24 bài thử kiểm tra ô chọn hiện ngay,
không còn nút chuyển chế độ; chọn/tải/xóa, thùng rác và bố cục 1080×700 /
1366×850 không QML warning. Cài bằng manifest/checksum rồi mở Thư viện và
Cài đặt từ EXE đã cài với dữ liệu riêng, không có đường dẫn Python nguồn.
Runtime/model không đổi; không chạy lại inference giọng/OCR cho sửa UI này.

Nguồn commit/push trước khi build một lần. ZIP chứa toàn bộ runtime/model,
đã kiểm tra SHA-256/CRC mọi tệp và digest GitHub trước khi published.
Updater công khai từ RC34 và RC52 nhận đúng RC53 và checksum.

Đã mở độc lập qua Explorer tại `%LOCALAPPDATA%/Programs/BiliClass/1.0.0rc53`.
App sống sau khi launcher bị đóng; 10 phép kiểm tra phản hồi qua. Toàn bộ
16 bản ghi bài, 992 WAV và tùy chọn cá nhân giữ nguyên.
Desktop/Start menu trỏ RC53; không tự chạy lại lượt tạo giọng đã hoàn tất.
