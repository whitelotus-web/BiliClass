# Hai giáo viên thử BiliClass trên hai máy

## Chia sẻ đúng thứ cần thử

Kho GitHub công khai giữ mã nguồn, tài liệu và kiểm thử. Giáo viên có thể tải [bản RC12](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc12) mà không cần tài khoản GitHub. Tải `BiliClass-RC12-Windows.zip`, giải nén toàn bộ rồi chạy `Setup.cmd` để cài lần đầu; hoặc chạy `BiliClass/BiliClass.exe` để dùng portable. Sau khi mở app, RC12 tự kiểm tra bản mới và có nút **Kiểm tra cập nhật**. Khi có bản mới, bấm **Cập nhật**; app tải và xác minh gói, tự đóng/mở lại, còn thư viện bài học trong `%LOCALAPPDATA%/BiliClass` được giữ nguyên. Nếu dùng bộ cài, hai gói `.bclanguage` vẫn nằm ở cùng trang phát hành để nạp thủ công khi cần. Tải mã GitHub về sẽ không tự tạo ra `.exe` mới.

Chỉ phát hành sau khi kiểm thử từ mã nguồn qua một mốc. Mỗi bản phát hành ghi mã commit, ngày, thay đổi, gói model đi kèm và kết quả kiểm thử. Vì gói app và model lớn, để tệp phát hành ngoài lịch sử Git; không đưa `models/`, `dist/` hoặc bản sao thư viện lên Git.

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

Giới hạn hiện tại: bản xuất PPTX mới giữ văn bản đã duyệt và ảnh thường; công thức dạng đối tượng, biểu đồ, video và hiệu ứng cần đối chiếu bản gốc. Cập nhật tự động chỉ áp dụng cho bản Windows đóng gói; bản chạy từ mã nguồn vẫn cập nhật bằng Git và lệnh chạy phát triển. Chưa gọi đây là bản sao tương đương tuyệt đối của PPTX giáo viên đưa vào.
