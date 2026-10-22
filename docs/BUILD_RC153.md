# RC153 — Hàng đợi đầu vào và xem trước từng bài

Chọn nhiều bài ở Chuyển đổi hoặc Tạo giọng đọc dùng chung phần
đầu vào: hàng đợi nằm trên cấu hình, bên trái là các bài đã chọn,
bên phải là ảnh xem trước. Mặc định chọn bài đầu tiên; bấm bài khác
để đổi ảnh. Mỗi dòng có tên, số slide, dung lượng, Mở PowerPoint và
nút bỏ riêng. Chọn bài khác/Hủy các bài đang chọn vẫn ở đầu trang.
Có phóng to và chuyển slide của bài đang xem, không nhập bản trùng
vào thư viện chỉ để xem trước. Chọn nhiều bài trong thư viện dùng
cùng phần đầu vào này.

Thông tin file đọc ở luồng nền, không mở PowerPoint để đếm slide.
Ảnh dùng cơ chế xem trước/cached-render hiện có của một bài; chỉ
chuẩn bị ảnh bài đang chọn. Thay bài nhanh, bỏ bài đang xem, đổi
công cụ hoặc hủy đầu vào bỏ qua kết quả ảnh cũ. File nguồn và bài
đã lưu không bị xóa/sửa. Thư viện không tự được thêm bài khi chọn
đầu vào hoặc xem trước. Khi bắt đầu, dừng phần xem trước và dùng
nguyên hàng đợi xử lý lần lượt, thời gian, dừng/tiếp tục/thử lại;
loading vẫn ở vùng cấu hình. Hàng đợi hoàn tất vẫn tự ẩn.

Vùng tải bài ở cả hai màn ghi rõ có thể chọn/kéo thả nhiều file
cùng lúc và xử lý lần lượt. Tab thư viện: icon 18 px, tab bên trái
đè tab sau, tab được chọn nổi trên cả hai bên. Màn khởi động thu
từ 1000×563 xuống 860×484, giữ tỷ lệ, hình, tiến độ và tùy chọn
Windows tắt chuyển động.

Kiểm chứng nguồn:

- 54 pytest cho thông tin đầu vào, hàng đợi, vị trí/bản xuất, workspace
  và chuẩn bị giọng; hai kiểm tra metadata chạy lại sau chỉnh thông báo.
- Qt đầu vào: file PPTX thật để đếm slide; ảnh fixture để ép cuộc đua
  trả ảnh cũ, chọn nhanh/bỏ bài hiện tại/chuyển slide/phóng to; mở đúng
  file từng dòng không đổi lựa chọn. Hủy không thêm/xóa bài trong thư
  viện hay sửa nguồn. Sáng/tối, cửa sổ 1080×700 và 1366×850 đạt.
- Render một slide PPTX thử bằng PowerPoint thật qua đúng pipeline
  xem trước đang dùng; số slide đúng và hash nguồn giữ nguyên.
- Qt hàng đợi: chuyển đổi và tạo giọng lần lượt, tổng thời gian,
  dừng/tiếp tục/thử lại, 25 bài tự cuộn theo bài đang chạy, toàn bộ
  lượt hoàn tất tự ẩn và vẫn ẩn khi mở lại; bản xuất có WAV fixture.
- Qt chọn một bài, chọn nhiều bài trong thư viện, icon và thao tác
  thư viện; layout một bài 1080–1920 px vẫn đạt. Không có cảnh báo QML.
- Smoke khởi động thật đo được 860×484, hình/tiến độ và các giai đoạn
  hiển thị; splash đóng sau khung hình đầu của cửa sổ chính.
- Ruff và compileall đạt. Không đánh giá lại chất lượng dịch hoặc
  giọng TTS trong thay đổi giao diện này.

[Trạng thái phát hành RC153: đang kiểm tra.]
