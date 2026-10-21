# RC128 — Nút lưu hồ sơ theo thay đổi chưa lưu

Nút Lưu thông tin chỉ bật khi tên thầy/cô, trường hoặc bộ môn khác
giá trị đã lưu. Sau lưu thành công, nút tự tắt. Sửa rồi hoàn nguyên
giá trị cũng tắt nút. So sánh theo cùng quy tắc loại khoảng trắng và
tên mặc định với backend. Môn Khác để trống vẫn không được lưu.
Logo tự lưu riêng nên không làm nút hồ sơ bật lại. Các nút Lưu trong
Cài đặt dùng màu nền/chữ vô hiệu hóa rõ ràng, giữ nguyên vị trí nút.

Kiểm bằng `.venv`: pytest danh mục môn đạt. Qt thật kiểm gõ phím
vào tên, sửa trường/bộ môn, hoàn nguyên, lưu và trạng thái tắt ngay
sau lưu. Kiểm logo tự lưu, môn tùy chọn gồm dấu phẩy và khôi phục
giá trị sau mở lại. Luồng bố cục Cài đặt sáng/tối ở 1080/1366/1920,
sao lưu/khôi phục thư viện thử và các tab hiện có đều đạt, không cảnh
báo QML. Dữ liệu/ảnh thử giữ ngoài Git.

Bản này gồm các sửa Mascot và cấu hình giọng đã kiểm ở RC127.
Nguồn `1.0.0rc128`. Dựng một lần sau commit đã kiểm, dùng runtime
RC127 có manifest SHA256. Thông tin gói/cài đặt bổ sung sau xác minh.
