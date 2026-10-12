# Hai giáo viên dùng BiliClass trên hai máy

Gửi [link Release RC14](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc14) cho người dùng thử. Người nhận tải **BiliClass-RC14-Windows.zip** trong Assets, giải nén toàn bộ, chạy **Setup.cmd**, rồi mở BiliClass từ Start menu. Không cần tài khoản GitHub hoặc Python. Không chọn Source code nếu chỉ muốn dùng.

Mỗi máy cần Windows 10/11 64-bit, Google Chrome, PowerPoint desktop và Internet khi chuyển đổi. Sau khi cài, đăng nhập ChatGPT riêng tại **Cài đặt → Browser AI → Thêm tài khoản**. Bộ cài chứa giọng Anh/Việt, mẫu và ảnh xem trước; không mang tài khoản hoặc thư viện của máy phát triển sang.

## Thử một bài

1. Đưa vào một PPTX quen thuộc, kiểm tra tên tệp đã hiện.
2. Chọn môn/cấp/khối, một trong bốn kiểu chuyển đổi; xem ví dụ bố cục.
3. Chọn giữ đúng PPTX gốc hoặc tạo theo mẫu mới, thêm lưu ý nếu cần.
4. Bấm Chuyển đổi bài giảng, chờ tool nhận kết quả và chuẩn bị âm thanh.
5. Đối chiếu slide, hình, công thức, ngôn ngữ rồi Dùng để dạy. Thử đọc Anh/Việt và kéo mascot/đổi slide.
6. Nếu thử quiz, duyệt câu hỏi trước, cho một điện thoại cùng Wi-Fi quét QR; kết thúc tiết và kiểm tra báo cáo.

Free/Plus có hạn mức riêng. Cần tự xử lý nếu web yêu cầu đăng nhập/xác minh hoặc hết lượt. Một yêu cầu thành công không chứng minh mọi môn/bài/hiệu ứng đều đúng.

## Cập nhật và gửi góp ý

Bản Windows tự kiểm tra GitHub khi mở. Khi có bản mới, bấm **Cập nhật**; tool tải/xác minh, cài và mở lại, giữ thư viện bài học. Không cần tự cài lại từ đầu. Bản chạy từ mã nguồn cập nhật bằng Git, không dùng cơ chế cập nhật `.exe`.

Ghi phiên bản (hoặc commit trong `BiliClass/BUILD_INFO.json`), Windows, loại/tên tệp, bước thao tác, kết quả mong đợi và kết quả thực tế. Ảnh/tệp gửi góp ý cần bỏ thông tin học sinh hoặc dữ liệu riêng không muốn chia sẻ.

## Chia sẻ đúng dữ liệu

GitHub giữ code/tài liệu/tài nguyên chung; gói `.exe` và model nằm ở Releases. Mỗi máy giữ thư viện trong `%LOCALAPPDATA%/BiliClass`, không mở chung thư mục database qua mạng.

Chia sẻ bài bằng `.biliclass` hoặc bản sao PPTX đã kiểm tra. Không tự đồng bộ hồ sơ ChatGPT, dữ liệu học sinh hoặc báo cáo lên GitHub. Nếu cùng sửa code, pull bản mới trước khi sửa rồi kiểm tra/commit/push; không force-push ghi đè người còn lại.
