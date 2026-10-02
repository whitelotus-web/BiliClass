# Dùng thử BiliClass 1.0 RC10

Trong bản mã nguồn mới: chọn `.pptx` tại **Tạo bài học mới**, dịch và duyệt, rồi bấm **Xem bài song ngữ**. Mỗi slide Việt đi kèm bản Anh cùng thiết kế gốc; không cần chọn template. **PPTX** lưu bản mới; **Trình chiếu song ngữ** mở và điều khiển bằng PowerPoint. Chi tiết: [SOURCE_POWERPOINT.md](SOURCE_POWERPOINT.md). Văn bản/tài liệu khác tiếp tục dùng [bộ mẫu BiliClass](TEMPLATES.md).

Đóng BiliClass đang mở, rồi chạy `dist/rc10/BiliClass/BiliClass.exe`. Trong **Cài đặt → Chung**, nhập tên/trường/nhiều bộ môn, tải logo ngay bên dưới và bấm **Lưu thông tin**; ô xem trước phản ánh hồ sơ đã lưu. Tab **Song ngữ** giải thích các level cùng bốn kiểu hiển thị, không lưu một mức chung. Trong **Giọng đọc**, nghe thử giọng English Kokoro và giọng Việt VieNeu, hoặc chọn nhanh một bộ giọng Việt–Anh. VieNeu có thể mất khoảng nửa phút để nạp lần đầu; nên dùng **Chuẩn bị âm thanh** trước giờ dạy. Ở tab **Mascot**, bấm **Lưu cài đặt Mascot** khi bật **Hiện khi dạy** để thấy ngay nhân vật nổi không khung; nhấp mascot để mở nút trợ giảng, nhấp lại để thu gọn. Nút mascot ở thanh bên mở lại nếu đã ẩn. Ở **Bài giảng mới**, chọn môn bất kỳ, khối 10–12, L0–L4 và kiểu trình bày cho chính bài đó; dán đoạn tiếng Việt hoặc chọn tài liệu. Dịch, sửa rồi duyệt cặp Việt–Anh. Dùng **Chuẩn bị lên lớp** và **Xem trước** để thử bố cục, âm thanh và trợ giảng. Tên lớp chỉ nhập khi bắt đầu tiết.

Muốn thử tương tác: soạn/duyệt câu hỏi trong **Trợ giảng & Quiz**, mở **Lớp học**, chọn đúng địa chỉ LAN và quét QR bằng điện thoại cùng mạng. Xem **Báo cáo** sau khi kết thúc.

Hướng dẫn đầy đủ về cài đặt, OCR, PowerPoint, gói bài, gói dịch và khôi phục: [USER_GUIDE.md](USER_GUIDE.md). Trong app nhấn F1. Không cần nhập bài ví dụ cụ thể hoặc tạo tài khoản học sinh.

Để thử tính năng đang phát triển (kéo mascot tự do), đóng RC10 rồi chạy `powershell -ExecutionPolicy Bypass -File scripts/run.ps1 --page settings` từ thư mục dự án. Cửa sổ sẽ ghi **Bản phát triển từ mã nguồn**. Kéo mascot rồi thả để lưu vị trí, nhấp nhanh để mở nút; **Về góc** đặt lại vị trí. Sau khi sửa mã, đóng cửa sổ và chạy lại lệnh. Tính năng mới chỉ có ở bản mã nguồn cho đến khi đóng gói `.exe` tiếp theo.

Nếu mã nguồn và `.venv` nằm trên ổ cứng chậm, chuẩn bị thư viện khởi động trên ổ hệ thống một lần:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/prepare-dev-runtime.ps1
```

Sau đó `scripts/run.ps1` tự dùng cache trong `%LOCALAPPDATA%\BiliClass\dev-runtime`. Mã nguồn vẫn được đọc từ dự án; sửa mã chỉ cần đóng và mở lại app, không tạo lại `.exe`. Cache không chứa bài giảng, phản hồi học sinh hay model. Khi thay đổi bộ thư viện Python, chạy lại lệnh chuẩn bị; cache không khớp hoặc chưa hoàn tất sẽ không được sử dụng.

Để thử kho kiến thức đang phát triển trên thư viện riêng, không nâng cấp thư viện cá nhân đang dùng với RC12:

```powershell
$env:BILICLASS_DATA = Join-Path (Get-Location) '.runtime\knowledge-test'
powershell -ExecutionPolicy Bypass -File scripts/run.ps1 --page knowledge
```
