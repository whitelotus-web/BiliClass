# RC54 — thư viện Danh sách / Thẻ lớn, 16/10/2026

Mốc nguồn đã kiểm tra, đang chuẩn bị bộ cài riêng.

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

46 kiểm thử liên quan qua. Qt dùng 24 bài thử kiểm tra chọn/tải/xóa,
thùng rác, lớp học/báo cáo/thuật ngữ và toolbar một hàng ở 2 kích thước.
Qt riêng cho kiểu xem xuất ảnh bằng PowerPoint thật của 3 bài dùng thử;
xác minh 16:9, 2/3 cột, vị trí nút sau Sắp xếp, lưu lựa chọn, giữ các ID
đã chọn khi chuyển kiểu và đúng ID khi tải. Không QML warning.

Runtime/model không đổi từ bộ đã kiểm tra ở RC51. Không chạy lại
inference giọng/OCR cho thay đổi thư viện này. Không gửi thư viện,
bài giảng cá nhân hoặc key lên repo mã nguồn.
