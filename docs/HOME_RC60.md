# Trang chủ RC60 — mascot lớn, 17/10/2026

Trang chủ chuyển sang bố cục gần ảnh tham khảo đã chọn: lời chào lớn bên
trái, mascot lớn cùng ô thoại bên phải, nền xanh nhạt và vùng chọn tài liệu
rộng bên dưới. Dùng lại nhân vật Milo/Lumi đang chọn; không đổi cài đặt mascot.

- Chọn tài liệu hoặc kéo thả để vào cùng luồng Chuyển đổi bài giảng hiện có.
  Luồng chính nhận .pptx tối đa 200 MB; chọn hoặc thả tệp sai định dạng sẽ báo lỗi.
- Bốn bước ngắn: chọn tài liệu → chọn cách dịch → xem bài/tạo giọng → dạy.
  Không hứa giữ mọi hiệu ứng khi dùng mẫu mới; vẫn cần kiểm tra bài trước dạy.
- Khi có tác vụ, nút chính đổi thành Xem tiến độ; không nhận thêm tệp ở vùng
  thả. Bài đang mở/bài gần đây, vào lớp và tình trạng ứng dụng vẫn còn phía dưới.
- Giữ phần tìm/lọc/chọn nhiều bài trong Thư viện, không đưa lên đầu Trang chủ.

Kiểm tra Qt thật ở 1080×700, 1366×850 và 1680×960: lời chào/mascot/nút chọn
và vùng tải nằm trong khung nhìn ban đầu. Ở cửa sổ nhỏ cần cuộn để xem đủ bốn
bước và phần dưới. Kiểm tra cả Milo/Lumi, chọn/kéo thả, chặn quá 200 MB, giữ cấu hình khi chuyển
tab, mở bài đã lưu, nút tiến độ và phần tình trạng; không có cảnh báo QML.
Nhóm kiểm thử liên quan qua, cùng các Qt quản lý thư viện/lớp và danh sách/thẻ.

Ảnh nhân vật dùng tài nguyên có sẵn, giới hạn kích thước giải mã. Nền sóng
và biểu tượng tải vẽ bằng QML Canvas, chỉ vẽ lại khi kích thước/trạng thái
thay đổi; không có vòng lặp hoạt ảnh hoặc thư viện mới.

Bộ cài, commit và checksum: [BUILD_RC60.md](BUILD_RC60.md).

Ô tải lên dùng chung ở Trang chủ và Chuyển đổi: bốn dòng căn giữa đúng nội
dung được chọn, icon tải màu trắng trên nút xanh. Bỏ số 01/02 và nút quay về
Thư viện ở màn Chuyển đổi. Tên tệp, đổi/bỏ tệp và lỗi hiển thị trong cùng ô.

Hướng phát triển: ổn định chuyển ngữ PowerPoint trước. Word/PDF/ảnh nên thành
luồng riêng Tạo bài giảng từ tài liệu với bước trích nội dung, lập dàn ý, chọn
ảnh/công thức, chia slide và giáo viên duyệt. Các bộ đọc định dạng và API nhập
nội dung cũ trong mã nguồn được giữ lại; giao diện chính hiện chỉ nhận PPTX.

Thư viện: Chia sẻ & quản lý chuyển ngang dòng mô tả; bỏ hàng Tất cả bài
giảng thừa. Tìm kiếm nằm ngay dưới mô tả; bộ đếm số bài chuyển cạnh Xóa đã
chọn, cùng hàng bộ lọc/thao tác. Các kiểm tra Qt xác nhận cùng hàng ở 1080
và 1366, số bài vẫn theo kết quả lọc.
