# Trang chủ RC59 — mascot lớn, 17/10/2026

Trang chủ chuyển sang bố cục gần ảnh tham khảo đã chọn: lời chào lớn bên
trái, mascot lớn cùng ô thoại bên phải, nền xanh nhạt và vùng chọn tài liệu
rộng bên dưới. Dùng lại nhân vật Milo/Lumi đang chọn; không đổi cài đặt mascot.

- Chọn tài liệu hoặc kéo thả để vào cùng luồng Chuyển đổi bài giảng hiện có.
  Vẫn nhận PowerPoint, Word, PDF, văn bản và ảnh.
- Bốn bước ngắn: chọn tài liệu → chọn cách dịch → xem bài/tạo giọng → dạy.
  Không hứa giữ mọi hiệu ứng khi dùng mẫu mới; vẫn cần kiểm tra bài trước dạy.
- Khi có tác vụ, nút chính đổi thành Xem tiến độ; không nhận thêm tệp ở vùng
  thả. Bài đang mở/bài gần đây, vào lớp và tình trạng ứng dụng vẫn còn phía dưới.
- Giữ phần tìm/lọc/chọn nhiều bài trong Thư viện, không đưa lên đầu Trang chủ.

Kiểm tra Qt thật ở 1080×700, 1366×850 và 1680×960: lời chào/mascot/nút chọn
và vùng tải nằm trong khung nhìn ban đầu. Ở cửa sổ nhỏ cần cuộn để xem đủ bốn
bước và phần dưới. Kiểm tra cả Milo/Lumi, chọn/kéo thả, giữ cấu hình khi chuyển
tab, mở bài đã lưu, nút tiến độ và phần tình trạng; không có cảnh báo QML.
Nhóm 34 kiểm thử liên quan qua, cùng các Qt quản lý thư viện/lớp và danh sách/thẻ.

Ảnh nhân vật dùng tài nguyên có sẵn, giới hạn kích thước giải mã. Nền sóng
và biểu tượng tải vẽ bằng QML Canvas, chỉ vẽ lại khi kích thước/trạng thái
thay đổi; không có vòng lặp hoạt ảnh hoặc thư viện mới.

Bộ cài, commit và checksum: [BUILD_RC59.md](BUILD_RC59.md).
