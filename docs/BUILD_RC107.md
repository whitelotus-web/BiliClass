# RC107 — Chốt tự hiện slide sau khi tạo giọng

Bao gồm thay đổi giọng đọc, icon và xem trước của RC106. Kiểm tra executable
RC106 phát hiện trường hợp job tạo xong một cặp/ngôn ngữ khác với cấu hình
đang chọn trên màn hình: ảnh đã tải nhưng khung vẫn có thể ẩn. RC106 chưa
được mở cho người dùng hay phát hành trên GitHub.

QML theo dõi một lần chuyển từ job đang chạy sang hoàn tất của đúng bài,
tự mở xem trước khi thành công. Không phụ thuộc cấu hình nháp đang chọn.
Các thông báo sau đó không mở lại khi giáo viên đã chủ động ẩn khung.
Giọng chưa hoàn tất, bị hủy hay của bài khác không kích hoạt hành vi này.

Kiểm tra Qt riêng bổ sung cả trường hợp đổi cặp đang chọn và ẩn thủ công.
Bản giọng và nguồn bài cá nhân đã sửa trước đó giữ nguyên; không tạo lại
âm thanh vì thay đổi này chỉ ở giao diện.

## Bộ cài đã kiểm chứng

- Commit đóng gói: `aea1479755ecf219709fa2900547a0041a070c85`.
- ZIP: 1.249.733.257 byte; SHA256
  `fc6e169561f6f9187553350d2b564ccd547bbdb8c64eade9a45384f164f87e4c`.
- ZIP khớp manifest; digest của asset GitHub khớp checksum.
- Executable thực tạo đủ hai giọng Việt–Anh trên thư viện tạm và tự hiện
  ảnh slide; không cảnh báo QML. Nhịp giao diện lớn nhất đo được 0,843 s
  trong lượt kiểm tra; không suy ra mọi bài/mọi máy đều có cùng tốc độ.
- RC107 cài riêng và mở độc lập qua Explorer; cửa sổ chính/Mascot hiện,
  biểu tượng và shortcut đúng. Có bốn lần hết hạn kiểm tra 500 ms khi
  đang mở bài, sau đó ba lượt phản hồi liên tiếp 0,187 / 0,172 / 0 giây.
- Đối chiếu sau cài với trạng thái trước cài (đã bao gồm phần sửa bài có
  chủ đích): nguồn/phiên bản bài, 1.224 WAV tham chiếu, cặp/tốc độ và
  checksum Key giữ nguyên.
- Bản thử RC106 chưa phát hành được giữ nguyên: bước dọn thư mục bị
  duyệt tự động chặn theo chính sách. RC105 dự phòng và RC107 còn đủ.

[Bản phát hành RC107](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc107).
