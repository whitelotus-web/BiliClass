# RC91 — Lời đọc theo nội dung đã hiện và âm lượng Windows

Bao gồm toàn bộ thay đổi [RC90](BUILD_RC90.md).

Loa ở chế độ tự động ghi nhớ từng đoạn đã đọc xong trong slide. Lần bấm
đầu đọc tất cả nội dung đang hiện; lần sau đọc phần chưa đọc, kể cả khi
thầy cô đã mở nhiều hiệu ứng trước khi bấm loa. Khi đã đọc hết phần đang
hiện, bấm loa để đọc lại phần đó. Không đọc chữ còn ẩn. Đoạn bị ngắt giữa
chừng vẫn nằm trong phần chưa đọc; chuyển slide bắt đầu lại. Đang đọc thì
bấm loa để tạm dừng/đọc tiếp. Lựa chọn đọc được đặt thành một dòng rõ ràng
ngay dưới loa, thay cho dấu ba chấm.

Hiệu ứng chứa cả ô gốc và ô dịch được nhận diện là một bước chung, thay
vì bị coi là chưa xác định chỉ vì có nhiều đối tượng. Giữ kiểm tra thời gian
hiệu ứng, trigger và chữ còn ẩn. Không sửa tệp gốc hay tổng hợp lại giọng
khi mở bài để dạy.

Thanh âm lượng nhận lăn chuột mỗi nấc 5%, đồng bộ hai chiều với thiết bị
phát mặc định Windows, kể cả khi đổi loa/tai nghe. Giữ hai đường phát
PowerPoint và WAV ở mức phần mềm 100% để không giảm tiếng hai lần.
Đọc/ghi thiết bị chạy ngoài luồng giao diện; không thay mức loa khi khởi
động. Khi Windows chưa có thiết bị, dùng điều chỉnh lời đọc cục bộ và tự
kết nối lại khi thiết bị sẵn sàng.

Khôi phục “Trợ lý dạy học song ngữ” trong tiêu đề. Hai nhãn ANH ↔ VIỆT
màu xanh, Lưu trên máy màu xanh ngọc nằm trên cùng thanh tiêu đề; dùng
vùng nội dung mở rộng của Qt, giữ các nút cửa sổ Windows. Không thêm lại
hàng đầu trang cũ. Nút Trước/Sau không còn tooltip.

Đăng ký cùng AppUserModelID trên tiến trình, cửa sổ và shortcut. Cửa sổ
đăng ký tài nguyên icon/lệnh mở lại trước ID để Explorer làm mới đúng
nhóm icon khi đường dẫn cài đặt thay đổi theo phiên bản. Không xóa cache
Windows hoặc khởi động lại Explorer. CLI đăng ký shortcut không mở giao
diện, thư viện hoặc mô hình; bộ kiểm tra bản cài thử trên shortcut tạm.

## Kiểm tra trước đóng gói

- Ruff đạt; 913 kiểm thử lõi đạt (123,10 giây), bao gồm nguồn âm thanh,
  tiến độ từng đoạn, hiệu ứng song ngữ, phiên dạy, phím, Core Audio và
  metadata shortcut. Loại sáu nhóm kiểm thử trình duyệt cũ như RC90;
  một cảnh báo Starlette/httpx không liên quan thay đổi này.
- Qt: Trang chủ, bảng Mascot, ba cỡ bảng/cửa sổ, menu cách đọc, lăn chuột
  5%, cập nhật âm lượng ngược, không cuộn bảng; tiêu đề và màu nhãn;
  icon native, metadata, phóng to/thu nhỏ/khôi phục. Không cảnh báo QML.
- Bản sao slide 4 thực tế trong PowerPoint: click 0/1/2/3, đọc đầu rồi đọc
  tiếp, hiện hết trước khi đọc, hiện nhiều bước rồi đọc, đọc lại, giữ đoạn
  chưa đọc hết sau khi chuyển bước. Tệp gốc giữ nguyên, dùng WAV đã lưu.
- Core Audio native: đọc → thay một nấc nhỏ → đọc lại → khôi phục đúng mức
  ban đầu, hoàn tất trong 16 ms. Không thay đổi trạng thái loa sau kiểm tra.
- Điều khiển Office native: chuột/phím, đọc/tạm dừng/đọc tiếp, loa trên
  slide và Mascot, F5, hiệu ứng tiến/lùi, WASD và kéo bảng đều đạt;
  16 lần điều hướng trung bình 29 ms, cao nhất 47 ms; khoảng ngắt giao diện
  cao nhất 63 ms; không cảnh báo QML. Kiểm tra dùng âm thanh im lặng và
  thiết bị giả cho các thao tác phím âm lượng, không đổi loa của thầy cô.

Commit nguồn và kết quả bản đóng gói được ghi sau khi xác minh.
