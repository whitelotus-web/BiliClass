# RC58 — Rà soát toàn bộ và giảm chờ giao diện, 17/10/2026

[GitHub Release RC58](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc58).

- Nguồn: `8c1d89fead466350b6caad58ecbe7b000d283c10`.
- ZIP: `BiliClass-RC58-Windows.zip`, 837276320 byte, 4167 tệp.
- ZIP SHA-256: `af428db0a34d99808dc1d9b482789d4ddd6938c69eb915b3d6af5c198e33a4a1`.
- EXE SHA-256: `3df7135ffed80d1cf69318acb592a4db4061316fe4c32bae59ce9a07d902f333`.

## Nội dung và kiểm chứng

[Báo cáo rà soát](AUDIT_RC58.md) ghi thay đổi, số đo trước/sau, ma trận chức
năng và kế hoạch tiếp theo. [Hướng dẫn sử dụng](USER_GUIDE.md) đã cập nhật.

890 kiểm thử toàn bộ qua trong 493,19 giây. Nhóm 20 kiểm thử updater,
package/catalog sau điều chỉnh cuối cũng qua. Ruff và biên dịch toàn bộ mã
nguồn không lỗi. Cảnh báo test client FastAPI/Starlette với httpx còn được ghi
nhận; không thay runtime nhị phân chỉ để ẩn cảnh báo.

Qt thật kiểm tra chuyển đổi Google bằng API fixture, ba mẫu × hai chế độ,
cache slide, các bản giọng, bước chuẩn bị dạy, mascot, quản lý 24 bài/thùng
rác, Trang chủ và Lớp học đến WebSocket/kết quả/CSV. PowerPoint thật chuyển
đủ ba slide và giữ nguyên tệp nguồn. 50 kết nối loopback nhận đủ phản hồi,
không nhân đáp án khi gửi trùng/kết nối lại, giữ dữ liệu sau khởi động lại.

## Bộ cài và bản EXE

Biên dịch lại 113 module app bằng PyInstaller; dùng lại runtime/model đã kiểm
chứng từ RC57. Mỗi tệp trong ZIP được kiểm SHA-256/CRC. Source và bộ cài có
cùng phiên bản/commit; không có key, thư viện giáo viên hay phản hồi học sinh
trong commit nguồn/bộ cài.

Bản đã cài kiểm tra bảy màn hình Qt (Trang chủ, chuyển đổi, thư viện danh
sách/thẻ, cài đặt, lớp học, báo cáo), không có cảnh báo QML. Sáu mẫu giọng
không tải model, bắt đầu phát sau 15–47 ms; lưu trong lúc chuẩn bị nghe thử
khoảng 22 ms, Dừng không phát muộn. Đây là mẫu có sẵn, không phải tốc độ suy
luận câu nhập mới.

EXE đã qua self-test ngoại tuyến bằng model đi kèm: DOCX/PPTX, gói bài và lịch
sử SQLite, tổng hợp WAV Anh/Việt/trộn cùng một giọng, đổi tốc độ và dùng lại
cache. Máy chủ lớp spawn từ EXE, trang học sinh, WebSocket xác thực, ACK,
kết quả và sao lưu/khôi phục đều qua. Tất cả lượt thử dùng dữ liệu riêng.

Trên máy phát triển, RC58 cài tại `F:/Applications/BiliClass/1.0.0rc58` vì ổ C
ít chỗ trống. Thư viện ở `%LOCALAPPDATA%/BiliClass` không chuyển. Mở bằng
Explorer; ứng dụng vẫn sống ngoài job của launcher sau khi launcher bị đóng.
Mười lần kiểm tra phản hồi qua. Shortcut Desktop/Start menu trỏ RC58.
17 bản ghi, 992 WAV và cấu hình giữ nguyên; tác vụ đã xong 354/354 không tự
khởi động lại. Các bản cài cũ được giữ lại.

## Máy khác cập nhật

Vào **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật** hoặc tải ZIP RC58,
giải nén toàn bộ và chạy **Setup.cmd**. Cơ chế chọn phiên bản với đầu vào
RC34/RC57 đã nhận đúng metadata công khai RC58, dung lượng và SHA-256; RC58
không tự báo lại chính nó. Đây chưa phải thử nâng cấp trên chính máy thứ hai.

RC58 giữ thư mục cài tùy chọn đã xác minh khi tự nâng cấp; nếu ổ dữ liệu
thiếu chỗ tải, có thể dùng thư mục cập nhật trên ổ cài còn đủ dung lượng.
Không chuyển hoặc xóa dữ liệu giáo viên. Kiểm chứng trên Windows hiện tại;
chưa chứng nhận Windows sạch, máy chiếu, mọi PowerPoint hoặc Wi-Fi trường.
