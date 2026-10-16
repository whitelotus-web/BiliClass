# RC54 — thư viện Danh sách / Thẻ lớn, 16/10/2026

[GitHub Release RC54](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc54).

- Nguồn: `9be4dde2484f92d7f9f554f778877440575e7484`.
- ZIP: `BiliClass-RC54-Windows.zip`, 837234412 byte, 4165 tệp.
- ZIP SHA-256: `1395e3b2e05a35625234e6ac397a3909d95dd21c14a56ec72da1e134050e90ee`.
- EXE SHA-256: `a214702549174118a598b5b305b143ea234742222144f7170e32f234832428c1`.

Thêm hai nút ngay bên phải Sắp xếp. Thẻ lớn hiển thị trang đầu thực của
bài giảng trong khung 16:9; giữ trọn slide 4:3 bằng khoảng đệm hai bên.
Tự chia 2/3 cột ở cửa sổ 1080/1366; lưu lựa chọn ở thư viện cá nhân.
Hai kiểu xem dùng chung tìm/lọc/phân trang, ô chọn và tải/xóa nhiều bài.

Ảnh được nạp ở luồng nền, ưu tiên ảnh đã xác minh trong cache. Khi cần
vẽ mới chỉ xuất trang đầu; các tác vụ preview dùng chung khóa Office.
Ảnh nhỏ 640×360 được lưu theo dấu vân tay của ảnh gốc. Đổi trang/bộ lọc
hủy hàng chờ cũ; không mở/chọn bài hay sửa nội dung bài khi tải ảnh.
Không có PowerPoint hoặc chưa tạo được bản trình chiếu thì hiện trạng
thái chưa có ảnh; bài vẫn có thể mở từ thẻ.

47 kiểm thử liên quan qua. Qt dùng 24 bài thử kiểm tra chọn/tải/xóa,
thùng rác, lớp học/báo cáo/thuật ngữ và toolbar một hàng ở 2 kích thước.
Qt riêng cho kiểu xem xuất ảnh bằng PowerPoint thật của 3 bài dùng thử;
xác minh 16:9, 2/3 cột, vị trí nút sau Sắp xếp, lưu lựa chọn, giữ các ID
đã chọn khi chuyển kiểu và đúng ID khi tải. Không QML warning.

Runtime/model không đổi từ bộ đã kiểm tra ở RC51. Không chạy lại
inference giọng/OCR cho thay đổi thư viện này. Không gửi thư viện,
bài giảng cá nhân hoặc key lên repo mã nguồn.

Kiểm tra bộ cài phát hiện metadata NTFS có thể đổi khi PowerPoint mở
lần đầu. Ảnh thư viện tự kiểm tra lại hash nguồn và ảnh cache một lần;
không mở Office lần nữa và vẫn từ chối khi byte nguồn không khớp.

Bộ cài đầy đủ đã kiểm tra SHA-256/CRC mọi entry ZIP và digest GitHub,
manifest khi cài. EXE đã cài được thử Danh sách, Thẻ lớn với ảnh native
của bài dùng thử và Cài đặt; dữ liệu riêng, không có PYTHONPATH nguồn.
Ba ảnh bìa từ thư viện cá nhân cũng tải được; so sánh nội dung bài
trước/sau giữ nguyên. Đây là kiểm tra xem trước, không duyệt chất lượng
nội dung hoặc hiệu ứng của toàn bộ bài giảng.

Đã mở RC54 qua desktop Explorer, ngoài job của launcher. Sau khi đóng job,
app vẫn sống và qua 10 phép kiểm tra phản hồi. Toàn bộ 16 bản ghi bài,
992 WAV và tùy chọn cá nhân giữ nguyên; không tự tạo lại lượt voice 354
đoạn đã hoàn tất. Shortcut Desktop/Start menu đã trỏ RC54.
Updater công khai từ RC34 và RC53 nhận đúng RC54, kích thước và SHA-256.
Nguồn/tài liệu đã commit và push; runtime, model và bài cá nhân ở ngoài Git.
