# RC100 — Thư viện gọn hơn, xem trước và tải bài đúng tên

- Danh sách gọn hơn, nút 34px; giữ tên, môn/khối, số slide, ngày tạo
  và giọng đọc. Nút thùng rác đỏ cho từng bài; xóa nhiều bài trên
  thanh cố định. Biểu tượng loa + VI/EN chỉ hiện cho bản giọng đã đủ.
- Tiêu đề, tìm kiếm, bộ lọc và thao tác cố định khi cuộn; dấu × xóa
  nhanh từ khóa và giữ bộ lọc khác. Thẻ ít kết quả giữ kích thước và
  căn trái. Kéo chọn có tự cuộn; Shift chọn theo dải đã lọc/sắp xếp.
- Chuột Back và Backspace trở về thư viện qua cùng luồng bảo vệ thay
  đổi chưa lưu; Backspace trong ô nhập vẫn xóa chữ.
- Hướng dẫn nhanh ngay dưới tiêu đề Chuyển đổi và Tạo giọng đọc;
  bỏ dòng hướng dẫn tạo giọng lặp ở chân trang.
- Bỏ dòng ghi chú mặc định dưới nút lưu trong Cài đặt giọng đọc;
  chỉ hiện trạng thái khi đang sửa, lưu hoặc có kết quả lưu.
- Cặp/tốc độ chọn gần nhất ở Tạo giọng được lưu làm mặc định chung;
  Cài đặt cập nhật cùng lựa chọn. Đổi nhanh liên tiếp và thoát ngay
  vẫn giữ lựa chọn cuối. Nghe thử dùng mẫu dài cùng Cài đặt, theo
  tiếng Anh/Việt/cả hai đang chọn; không thay giọng đã tạo của bài cũ.
- Dọn các ghi chú hồ sơ được yêu cầu bỏ ở Cài đặt chung; rút gọn
  tiêu đề thành “Xem trước hồ sơ”, giữ các trường và thao tác lưu.
- Căn giữa cụm thương hiệu, phiên bản và bản quyền trong Thông tin
  BiliClass. Tab Dữ liệu chỉ hiện ba tác vụ chính; mục hỗ trợ và quản
  lý nâng cao nằm trong Tùy chọn khác. Khôi phục thành công mở lại
  với dữ liệu vừa khôi phục, giữ nguyên thư viện trước đó.
- Chuột phải lên người Mascot mở Cài đặt (bánh răng) và Ẩn mini
  (mắt gạch chéo). Nút ẩn trên bảng dùng cùng icon mắt gạch chéo.
  Menu riêng vẫn hiện đủ sát mép màn hình, không làm mở bảng/di
  chuyển Mascot; chuột trái và mở lại từ thanh bên giữ nguyên.
- Hiện slide ngay trong bước chuyển đổi hoàn tất, có Trước/Sau và
  bốn nút cân đối. Xem trước ở Tạo giọng không bị worker Office đã
  ngừng trình chiếu chặn. Không tự xác nhận nội dung hay tạo giọng.
- Tên tải lấy lại bài đang chọn mỗi lần mở hộp lưu: tên bài + Song
  ngữ VI-EN, thêm Voice VI/EN/VI-EN theo bản giọng đã lưu đầy đủ.
- Mở bài chuyển giao diện trước khi worker chuẩn bị xong; ghi nhớ
  kiểm tra không có nhãn OCR để tránh phân tích lại cả tệp mỗi lần.
- Sẵn sàng trình chiếu tách khỏi duyệt nội dung dành cho lớp học.
  Bản thiếu nội dung hoặc còn lỗi không được đổi nhãn thành sẵn sàng.
- Sửa OCR bỏ qua ảnh có hiệu ứng ở chế độ mẫu mới, nhãn OCR làm tiêu
  đề và ảnh nhỏ chứa nội dung bị tách khỏi vị trí nguồn. Giữ kiểm tra
  chéo, công thức, bản gốc và dữ liệu cá nhân.

Giới hạn quan trọng: chưa tự đọc/tái dựng đầy đủ mọi bài chỉ có ảnh.
Chi tiết ở `PLAN_CONTENT_COMPLETION.md` và `VOICE_REVIEW_RC100.md`.

## Kiểm chứng

Bằng chứng chi tiết trong `reports/rc100` không đưa vào Git:

- Ruff và compileall qua; 1.094 kiểm thử pytest qua trong 159,84 giây.
  Hai nhóm browser-ai/browser-translation không chạy trong bộ này;
  không thay đổi chúng. Có một cảnh báo deprecation từ dependency.
- Qt Windows: thư viện dạng thẻ/danh sách, kéo chọn/Shift, thanh cố
  định, Back/Backspace, ba kích thước 1080/1366/1920 và không có
  cảnh báo QML. Dạng danh sách 1366×850 hiện năm dòng đầy đủ.
- Qt chuyển đổi với PowerPoint thật: xem trước ở bước hoàn tất,
  chuyển slide, khôi phục đúng bài và mở xem trước trong Tạo giọng.
- Hộp lưu Windows: nạp mới tên tệp cho không giọng, VI, EN, VI-EN.
- Qt cặp giọng và phiên dạy với PowerPoint: nghe thử, lưu tự ghép,
  ba lựa chọn tạo, hai loa riêng, phát/tạm dừng/tiếp tục và đổi slide.
  Fixture âm thanh im lặng kiểm chứng vận hành; gói cài được kiểm
  tra thêm với engine local thật. Chưa chứng nhận click loa vật lý
  trên mọi máy hoặc màn chiếu thứ hai.
- Đợt chỉnh Cài đặt/thùng rác bổ sung: 33 kiểm thử sao lưu, vị trí
  thư viện, xem trước và voice controls qua; Qt thư viện và kéo chọn
  chạy lại qua. Qt Cài đặt xác minh căn giữa ở ba kích thước, ẩn/hiện
  tùy chọn nâng cao, sao lưu/khôi phục dữ liệu thật trong thư viện
  dùng thử; bản hỏng không chuyển thư viện hay yêu cầu mở lại.
- Luồng nhớ cặp giọng bổ sung: 97 kiểm thử voice controls, mẫu nghe
  và cặp giọng qua. Qt xác minh mặc định qua khởi động lại, đúng mẫu
  dài/người đọc/tốc độ cho ba ngôn ngữ và WAV cũ còn nguyên. Qt cặp
  giọng/Cài đặt chạy lại qua; không có cảnh báo QML.
- Qt menu Mascot: chuột phải thật trong cửa sổ thử, hai hành động,
  icon, mở đúng tab Cài đặt, ẩn và mở lại, menu trong màn hình,
  nút ẩn trên bảng và click trái qua; không có cảnh báo QML.

Kết quả đóng gói/cài đặt được ghi sau khi hoàn tất.

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc99-voice-speed-ui --output dist/rc100-mascot-menu
```
