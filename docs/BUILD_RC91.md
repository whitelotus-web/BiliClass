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

## Bản đóng gói

- Phiên bản: `1.0.0rc91`.
- Commit ứng dụng: `626a261eb3fc1b1efdf1e8b6db48a5095b7efb25`.
- CI Source checks đạt:
  https://github.com/whitelotus-web/BiliClass/actions/runs/39243619942
- Dựng lại toàn bộ mã ứng dụng; tái sử dụng runtime/mô hình RC90 đã kiểm
  checksum. Python 3.12.7, PyInstaller 6.22.3, Qt/PySide6 6.11.2.
- `BiliClass-RC91-Windows.zip`: 871.281.549 byte; 4.215 tệp ứng dụng.
- SHA256: `cb22b80af158bfdafb8b78de73a2c7ac78e04426a311d71db40f9f74f41ffe72`.
- ZIP đã đối chiếu đủ manifest và checksum sau đóng gói.

## Bản cài và khởi chạy

- Các bước xác minh trên bản cài Unicode đạt: Windows Details, CLI đăng ký
  shortcut, trang chuyển đổi/cấu hình, template, mô hình giọng Việt/Anh,
  tiến trình lớp học và sao lưu thư viện. Fixture shortcut đặt trong thư mục
  local vì WScript.Shell trên máy này chuyển đường dẫn sang ANSI; không chạy
  chương trình đích của shortcut, không thay shortcut cá nhân trong kiểm tra.
- Tiếp tục kiểm tra trên bản cài đã xác minh sau khi chỉnh fixture WScript;
  kiểm tra gỡ bản cài tạm được hoàn tất riêng và giữ thư viện tạm. Bằng chứng:
  `reports/release/1.0.0rc91-aa342d58/installer.json`.
- Qt hoàn tất chuyển đổi → tạo giọng Việt/Anh thật: 2/2 đoạn trong 9,53 giây,
  444 nhịp giao diện, khoảng ngắt lớn nhất 344 ms; watchdog bật, không cảnh
  báo QML, giữ nguyên nguồn. Không gọi API hoặc phát tiếng trong kiểm tra.
- Phát hành: https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc91
  Digest asset trên GitHub khớp SHA256 ở trên.
- Cài tại `F:/Applications/BiliClass/1.0.0rc91`. Đóng RC90 bằng thông điệp
  đóng cửa sổ bình thường; không buộc dừng tiến trình. Mở RC91 bằng Explorer
  vào màn xem bài 4; cửa sổ chính và Mascot hiện, đáp ứng; tiến trình độc lập
  với Codex. Icon nhỏ/lớn, ID cửa sổ và cả hai shortcut đều hợp lệ.
- Bản gốc, revision, môn đã chọn, khóa API và toàn bộ 134 WAV của bài đang
  thử được đối chiếu giữ nguyên. Không tự đổi môn của bài cũ.
