# RC56 — Trang chủ và chuyển đổi, 17/10/2026

[GitHub Release RC56](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc56).

- Nguồn: `f79ef2e212a1d020b6ecbd8f9a58ae27f31970a7`.
- ZIP: `BiliClass-RC56-Windows.zip`, 837269246 byte, 4167 tệp.
- ZIP SHA-256: `a5420dc3581e24b1885b4ccce8c76061a0d7f4add6b5fe1cc56dcfb83c4192d6`.
- EXE SHA-256: `262bb1f81e1c68b43c41d63af652f633114040e439da4e2bc9c21c5d14282814`.

Trang chủ mới, slogan, mục Chuyển đổi bài giảng riêng, mẫu chứa văn bản/công
thức hiện đại và thuật ngữ theo môn được mô tả trong
[ghi nhận tối ưu RC56](OPTIMIZATION_RC56.md).

172 test liên quan qua. Các Qt Trang chủ, thư viện, chuyển đổi Google bằng
fixture và xem mẫu sáu tổ hợp không có QML warning. Bài Vật lý thực được
dựng thành 67 trang từ 48 trang gốc, render 67/67 bằng PowerPoint, không còn
lỗi tràn khung. Bài giữ trạng thái cần rà soát, không tự duyệt nội dung.

Đã kiểm SHA-256/CRC mọi tệp trong ZIP và digest phía GitHub. Cài thực vào thư
mục ứng dụng của người dùng, chạy EXE không có PYTHONPATH nguồn: Trang chủ,
Chuyển đổi, Cài đặt, thư viện Danh sách/Thẻ đều qua; không QML warning.
EXE dựng được sáu bộ mẫu trong kiểm tra ngoại tuyến. Archive có đủ các module
mới, gồm PIL.ImageStat. Runtime/model giữ từ mốc trước, không chạy lại toàn bộ
inference giọng/OCR hoặc chứng nhận Windows sạch trong đợt này.

Đã mở RC56 ở Trang chủ qua desktop Explorer, ngoài job của launcher; vẫn
sống sau khi đóng launcher và qua 10 kiểm tra phản hồi. Shortcut Desktop/
Start menu trỏ RC56. 17 bản ghi bài học, 992 WAV và cấu hình giọng/mascot giữ
nguyên; không tự tạo lại giọng. Trình cập nhật công khai từ RC34 và RC55 nhận
đúng RC56, dung lượng và SHA-256; RC56 không tự báo lại chính nó.

Thư viện, giọng, key, bản dựng và báo cáo riêng không nằm trong commit. Bộ
cài là tệp Release riêng. Commit sau mốc nguồn ở trên chỉ bổ sung tài liệu
phát hành, không thay EXE.
