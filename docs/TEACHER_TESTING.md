# Hai giáo viên thử BiliClass trên hai máy

## Chia sẻ đúng thứ cần thử

Kho GitHub riêng tư giữ mã nguồn, tài liệu và kiểm thử. Mỗi giáo viên cần quyền truy cập kho để tải [bản RC11](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc11) hoặc gửi lỗi qua Issues. Tải `BiliClass-RC11-Windows.zip`, giải nén rồi chạy `BiliClass/BiliClass.exe` để dùng ngay, hoặc `Setup.cmd` để cài vào tài khoản Windows. Nếu cài đặt, tải thêm hai gói `.bclanguage` ở cùng trang phát hành và nạp trong Cài đặt. Chỉ tải mã GitHub về sẽ không tự tạo ra `.exe` mới. Bản RC11 trên máy phát triển nằm trong `dist/rc11`, đã qua tự kiểm tra đóng gói tại đây nhưng cần thử trên máy giáo viên thứ hai.

Chỉ đóng gói sau khi kiểm thử từ mã nguồn qua một mốc. Mỗi bản phát hành ghi mã commit, ngày, thay đổi, các gói model đi kèm và kết quả kiểm thử. Vì gói app và model lớn, để tệp phát hành ngoài lịch sử Git; có thể dùng GitHub Release riêng tư nếu từng tệp đủ nhỏ, hoặc thư mục đám mây được chia sẻ riêng cho hai giáo viên. Không đưa `models/`, `dist/` hoặc bản sao thư viện lên Git.

## Mỗi máy giữ dữ liệu riêng

- Máy của giáo viên dùng thư viện trong `%LOCALAPPDATA%/BiliClass`; không mở cùng một thư mục dữ liệu qua mạng.
- Chia sẻ một bài đã kiểm tra bằng gói `.biliclass`. Máy nhận nhập thành bài riêng và duyệt lại nội dung trước khi dạy. Không tự đồng bộ dữ liệu học sinh hay báo cáo qua GitHub.
- Nếu cùng sửa một bài, chọn một bản gốc để biên tập, gửi gói bài mới và đối chiếu thay đổi thủ công. Git dùng cho mã ứng dụng, không thay thế hệ đồng biên tập bài giảng.
- Góp ý theo mẫu: phiên bản app/commit, Windows, loại tài liệu đầu vào, bước thao tác, kết quả mong đợi, kết quả thực tế. Chỉ đính kèm bài giảng hoặc ảnh có tên học sinh khi đã chủ động loại dữ liệu riêng tư.

## Luồng thử ngắn

1. Trên máy phát triển, chạy `powershell -ExecutionPolicy Bypass -File scripts/run.ps1` để thử thay đổi nhanh. Không cần build `.exe` sau mỗi lần sửa.
2. Nhập một PPTX hoặc DOCX mẫu, đối chiếu nội dung nguồn; dịch/sửa và duyệt từng đoạn.
3. Mở **Chuẩn bị bài giảng**, kiểm tra nguồn và mức sẵn sàng, bấm **Chốt bản chuẩn bị**.
4. Dạy thử bằng chữ; nếu dùng quiz, cho một điện thoại cùng Wi-Fi quét QR. Mở báo cáo và quay về bài gốc.
5. Khi luồng trên ổn, đóng gói một lần, chạy bản đóng gói trên máy thứ hai rồi ghi lỗi theo đúng phiên bản đó.

Giới hạn hiện tại: bản xuất PPTX mới giữ văn bản đã duyệt và ảnh thường; công thức dạng đối tượng, biểu đồ, video và hiệu ứng cần đối chiếu bản gốc. Chưa gọi đây là bản sao tương đương tuyệt đối của PPTX giáo viên đưa vào.
