# Hai giáo viên thử BiliClass trên hai máy

## Chia sẻ đúng thứ cần thử

Kho GitHub riêng tư giữ mã nguồn, tài liệu và kiểm thử. Mỗi giáo viên cần quyền truy cập kho nếu muốn xem mã hoặc gửi lỗi qua Issues. Để **chạy ứng dụng** trên máy không có môi trường phát triển, chia sẻ **bản portable hoặc bộ cài cùng các gói model** của đúng mốc phát hành; tải mã GitHub về không tự tạo ra `.exe` mới. Bản RC10 trong `dist/rc10` có trước các thay đổi trong mã nguồn ngày 02/10/2026.

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
