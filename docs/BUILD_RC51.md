# RC51 — bộ cài Windows đã phát hành, 16/10/2026

[GitHub Release RC51](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc51)

- Phiên bản: `1.0.0rc51`.
- Commit nguồn của bộ cài: `1200d1f5ae5e2d80b86aaa2925aae11d13326d40`.
- ZIP: `BiliClass-RC51-Windows.zip`, 837.224.493 byte, 4.165 tệp.
- ZIP SHA-256: `078d731af3f7e7d4fdeb1c8964570716c6872dc2b8f34664dfa9a59edc0f9c24`.
- EXE SHA-256: `92e2cb1347b397f0a961e49f489244a1c30c64c8003ec9ce5e7ffe232d59af3b`.
- Giải nén khoảng 1,65 GB; có runtime, VieNeu, hai bộ OCR và template.

Nguồn đã commit/push trước khi đóng gói. Đã sửa định dạng ngày qua Qt và
manifest phải chứa cả models nằm trong package rapidocr trước khi chốt bộ
cài; executable cuối và manifest cùng commit nêu trên. Tái dùng các native
dependency không đổi đã xác minh từ RC34, biên dịch 108 module ứng dụng,
nhưng ZIP cuối chứa **tệp vật lý đầy đủ**, không có junction đến máy này.
Giữ bản EXE/model ngoài commit nguồn. GitHub kiểm tra digest của cả ZIP và
tệp sha256 trước khi chuyển release từ draft sang published.

Kiểm chứng:

- 111 kiểm thử liên quan qua; Qt result, chọn nhiều bài, bộ lọc, xóa/khôi
  phục, báo cáo, thuật ngữ và mascot ở 1080×700 / 1366×850 không QML warning.
- Trình chiếu PowerPoint thật: bước xác nhận, mascot, đọc cache, đổi slide,
  trang trống, đóng/mở lại; nguồn không đổi.
- Cài từ manifest vào đường dẫn Unicode riêng; chạy Qt từ bộ đã cài khi
  bỏ PYTHONPATH/PYTHONHOME và biến model của máy phát triển.
- Self-test bộ cài: DOCX/PPTX, template, SQLite, giọng VieNeu Việt/Anh/xen
  ngôn ngữ và tốc độ, cache, server lớp học riêng, điện thoại mô phỏng nhận
  ACK qua WebSocket, lưu báo cáo, xuất PowerPoint và sao lưu/khôi phục.
- Gỡ bản cài thử giữ lại thư viện thử riêng. Không tác động thư viện thật.
- Universal 2026 chạy sáu cặp phong cách/ngôn ngữ từ gói đầy đủ.
- OCR từ executable đầy đủ đọc được hai dòng của ảnh thử; dòng Anh đúng,
  dấu Việt chưa khớp kiểm tra độc lập nên giữ ảnh để đối chiếu, không tự che.
  Đây là kiểm tra tải engine/bảo vệ vùng chưa chắc, không chứng nhận OCR Việt.
- Trình cập nhật RC34 qua API GitHub công khai nhận đúng RC51, kích thước,
  digest và tag trỏ đúng commit của bộ cài.

Đã cài RC51 vào `%LOCALAPPDATA%/Programs/BiliClass/1.0.0rc51`, cập nhật
shortcut Desktop/Start menu. Đóng RC49 nhẹ nhàng khi giọng đã đủ 354/354.
Mở lại bài đang xem qua Explorer; app nằm ngoài Windows job của launcher
và sống sau khi launcher bị đóng. Mười phép kiểm tra phản hồi cửa sổ qua.
16 bản ghi bài (9 đang dùng), 992 WAV, nội dung bài và tùy chọn cá nhân giữ
nguyên; không khởi động lại lượt tạo giọng.

Theo yêu cầu chủ máy, hai API key được gửi riêng vào kho GitHub private
`whitelotus-web/BiliClass-Private-Config`; truy cập ẩn danh nhận 404. Nhận
vào thư viện thử mã hóa DPAPI và giữ bộ đếm thành công. Không có mật khẩu
BiliClass bổ sung; máy khác cần Git for Windows và đăng nhập GitHub có quyền.
Key, dữ liệu cá nhân và token GitHub không chứa trong repo/bộ cài công khai.

Phạm vi: Windows/Office hiện tại, dữ liệu thử cho kiểm chứng. Chưa phải
chứng nhận clean Windows, mọi bố cục bài hay mọi hiệu ứng. Nội dung dịch,
chữ trong ảnh và đáp án quiz vẫn cần thầy cô đối chiếu/duyệt.
