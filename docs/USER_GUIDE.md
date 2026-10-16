# BiliClass — Trợ lý dạy học song ngữ

Hướng dẫn RC50, ngày 16/10/2026. Bài giảng, giọng đọc và thư viện cá nhân lưu
trên máy. Chuyển đổi hiện dùng Google Cloud Translation cho phần chữ và dựng
PowerPoint tại máy; Browser ChatGPT/Gemini tạm ẩn.

## Cài và cập nhật

1. Tải **BiliClass-RC50-Windows.zip** tại
   [Release RC50](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc50).
2. Giải nén toàn bộ; không chạy trong cửa sổ ZIP. Chạy **Setup.cmd**.
3. Bộ cài kiểm tra checksum và cài vào
   `%LOCALAPPDATA%/Programs/BiliClass/1.0.0rc50`, không cần quyền quản trị.
4. Mở BiliClass từ Desktop hoặc Start menu. Bản cài có model giọng, OCR và
   template; không cần thư mục runtime của máy phát triển.

Máy đang dùng RC34: vào **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật**,
chọn Cập nhật khi thấy RC50. Nếu chưa kiểm tra được mạng, tải ZIP và chạy
Setup.cmd như trên. Các bản cài nằm cạnh nhau; thư viện ở
`%LOCALAPPDATA%/BiliClass` được giữ nguyên. Không xóa thư mục dữ liệu này.
Thư viện cá nhân không đưa lên GitHub. Key có thể nhận riêng như hướng dẫn dưới.

## Tạo bài giảng

1. Chọn **Bài học mới**, đưa tài liệu vào hoặc dán nội dung.
2. Chọn môn, cấp/khối và **Song ngữ Việt–Anh** hoặc **Tiếng Anh 100%**.
3. Chọn giữ thiết kế PowerPoint gốc, hoặc tạo theo mẫu BiliClass/PowerPoint
   riêng. Mẫu Universal 2026 có ba phong cách; chọn xem mẫu để kiểm tra trước.
4. Cấu hình key ở **Cài đặt → Google Dịch**, lưu rồi chuyển đổi.
   Dịch chỉ gửi phần chữ; nội dung trong ảnh được OCR nếu nhận diện được.
5. Xem lại bài đã lưu. Công thức, chữ trong ảnh, hiệu ứng phức tạp và slide
   dày chữ vẫn cần đối chiếu. Bài còn lỗi chưa được coi là đã duyệt để dạy.

Key được lưu mã hóa theo tài khoản Windows. Nhiều key có thể dùng theo cấu
hình nhóm/hạn mức, nhưng 500.000 ký tự không phải số dư riêng được BiliClass
đọc từ mỗi key. Kiểm soát hạn mức và chi phí trong Google Cloud của dự án.

Máy thứ hai có thể vào **Cài đặt → Google Dịch → Nhận key từ GitHub**.
Cần Git for Windows và đăng nhập GitHub bằng Git Credential Manager, với quyền
truy cập kho riêng tư `whitelotus-web/BiliClass-Private-Config`. Không có mật
khẩu BiliClass bổ sung. Key được chuyển qua HTTPS rồi mã hóa bằng Windows
trên máy nhận, không chứa trong bộ cài hay repo mã nguồn công khai.
**Đồng bộ key lên GitHub** lưu/gộp cấu hình khi bấm; không chạy nền tự động.
Bộ đếm đã ghi nhận được giữ theo giá trị lớn hơn, nhưng hai máy sau đó vẫn
đếm riêng; không coi đây là đồng bộ trực tiếp quota. Đặt quota trong Google.

## Tạo giọng và bước tiếp theo

Giọng là bước tùy chọn sau khi bài đã lưu. Chọn một trong sáu giọng, nghe
thử, chọn tốc độ và tiếng Anh / tiếng Việt / Việt + Anh. Chọn ở đây không
thay cấu hình mặc định trong Cài đặt. Giọng chạy ngoại tuyến trên máy.

- Mỗi bản được phân biệt bằng nội dung, ngôn ngữ, giọng và tốc độ. Các bản
  đã tạo được giữ lại. Bản đã đủ hiện **Đã tạo**, khóa nút tạo trùng nhưng
  vẫn cho chọn để dùng/tải. Bản thiếu hiện **Tiếp tục tạo giọng**.
- Đổi giọng/tốc độ mở tạo bản mới. Nếu WAV bị thiếu/hỏng, tạo tiếp sẽ bổ sung
  phần thiếu. Bộ đếm thời gian chạy trong lượt tạo; không tự mở trình chiếu.
- Khi sẵn sàng, chọn **Tiếp tục: chuẩn bị dạy** ngay dưới phần giọng. Chọn
  đúng bản ở màn chuẩn bị rồi **Bắt đầu dạy**, hoặc tải PowerPoint.
- Bản Việt–Anh mới có ba nút EN, VI và VI+EN trên cùng slide khi nhúng được
  lời đọc tĩnh đã xác minh. Nút chung dùng lại WAV, không tổng hợp lần thứ ba.
  File đã nhúng phát được bằng PowerPoint mà không cần BiliClass.
- Đáp án ẩn và hiệu ứng chưa xác định không được đưa vào lời đọc cả slide.
  Trang không đủ khoảng trống/không có lời đọc tĩnh có thể không nhúng được;
  dùng BiliClass hoặc tải bản không kèm giọng trong trường hợp đó.

## Dạy và mascot

Chọn **Dùng để dạy** hoặc **Tiếp tục: chuẩn bị dạy**, kiểm tra bản giọng,
xác nhận nội dung rồi Bắt đầu dạy. Trình chiếu dùng Microsoft PowerPoint
cài trên máy. Giọng chỉ phát khi bấm đọc; đóng/đổi slide sẽ dừng hàng đợi.

Mascot có nút mở bài và đọc Việt/Anh/chung. Các nút đọc trên mascot chỉ bật
khi có phiên trình chiếu đúng bài. Trong Cài đặt Mascot, chọn tự theo môn của
bài hoặc môn cố định rồi Lưu để áp dụng cho mascot nổi.

## Thư viện, lớp học và báo cáo

Trang chủ hiển thị việc đang làm và ba bài vừa cập nhật. **Bài giảng** là
thư viện đầy đủ: tìm không dấu, lọc môn/khối/trạng thái/giọng, sắp xếp và
phân trang. Mở bài để chọn bản giọng rồi tải hoặc dạy. Xóa đưa vào Thùng rác,
có thể khôi phục.

**Lớp học** dùng khi muốn học sinh trả lời câu hỏi qua QR/địa chỉ mạng nội bộ.
Chọn bài và câu hỏi đã duyệt, mở lớp, cho học sinh vào cùng mạng rồi mở câu
hỏi. **Báo cáo** xem kết quả theo tiết; chỉ chuyển bài/tạo giọng chưa tạo ra
kết quả học sinh. **Dữ liệu trợ giảng** quản lý thuật ngữ và kiến thức tham
khảo; khác với mascot nổi.

## Chuyển dữ liệu giữa máy

Tải PowerPoint cho người chỉ cần trình chiếu. Gói `.biliclass` phục vụ chia
sẻ bài/nội dung trợ giảng tùy chọn, có giới hạn kích thước và yêu cầu duyệt
lại trên máy nhận. Dùng Sao lưu / Khôi phục thư viện để chuyển dữ liệu cá
nhân; khôi phục tạo thư mục mới. Ứng dụng/model cài riêng, key nhập riêng.
Không đưa thư viện, câu trả lời học sinh hoặc API key lên GitHub.
