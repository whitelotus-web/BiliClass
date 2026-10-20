# RC109 — Loa nhỏ hơn, không sửa hình trên slide đang chiếu

Bao gồm bộ icon Mascot của RC108. RC108 đã đóng gói nhưng chưa cài/mở
cho người dùng khi nhận thêm báo lỗi loa trên slide 6 của bài gần nhất.

Loa slide giảm từ 36 xuống 28 pt; hai loa vẫn có khoảng cách riêng.
Trong phiên gắn Mascot, hình loa/Pause được vẽ ở các cửa sổ trong suốt
nhỏ, thuộc đúng cửa sổ trình chiếu, không nhận chuột hay lấy tiêu điểm.
Chỉ ẩn hình trong bản sao phiên dạy trước khi trình chiếu. Việc đổi trạng
thái phát/dừng không còn sửa Visible của hình trên slide đang chiếu,
tránh xung đột với hiệu ứng và việc làm mới nội dung slide. Khi không
khởi tạo được lớp hình này, chuột dùng nút PowerPoint gốc.

Giữ nguyên cơ chế phát/kiểm tra âm thanh, phạm vi đọc và hiệu ứng nguồn.
Nút vẫn tạm dừng được phần đang đọc khi chế độ Tự động vừa đánh dấu hết
lời mới. Bản PowerPoint tải về vẫn có loa và Pause riêng chạy trực tiếp
trong PowerPoint.

Bảng Mascot giữ cố định một dòng trạng thái, tránh thay chiều cao và vị
trí khi chuyển Phát/Pause/hết lời đọc. Hàng loa nằm dưới Âm lượng; hàng
Trước–Sau nằm cuối bảng. Tự động vẫn ưu tiên phần mới trên mỗi bước;
khi đã đọc hết, bấm lại loa sẽ nghe lại phần đang hiện. Các nút không
bị vô hiệu hóa chỉ vì phần này đã đọc xong.

Kiểm tra: 108 ca liên quan đến giọng đọc, loa, phím đọc và phạm vi đọc
đạt; Ruff đạt. Qt kiểm tra ba cỡ bảng, thứ tự nút và tọa độ không đổi
qua Chuẩn bị/Phát/Pause/Dừng; không có cảnh báo QML.

Trên bản sao riêng của slide 6, PowerPoint thật giữ nguyên bước hiệu ứng
4 qua Phát/Pause/Tiếp tục/đổi Anh–Việt/Dừng; không có hai player cùng
phát trong lượt này. Thư viện hiện có đủ 14 đoạn Anh và 5 đoạn Việt cho
phần đã mở, và chọn lại đủ số đoạn khi nghe lại. Đây là kiểm tra điều
khiển Office và chọn lời đọc; chưa thay thế thao tác bấm chuột thực của
người dùng trên từng slide. Tệp nguồn và WAV cá nhân không được sửa.

## Bản đã phát hành và mở trên máy

- Commit đóng gói: `dc646c881f3fa804aaebeacba9981362541c466e`.
- ZIP: 1.249.943.910 byte; SHA256
  `8e84119d4c5aa6f5aeffd40cd209ccd3dc0562e346d10681d5a42e191afe44fa`.
- ZIP khớp manifest; digest asset trên GitHub khớp checksum. Executable
  vượt qua smoke khởi động; QML/icon trong gói khớp nguồn đã kiểm tra.
- Cài riêng RC109 và mở qua Explorer; cửa sổ chính/Mascot hiện, shortcut
  và biểu tượng đúng. Khi mở bài có năm lượt hết hạn kiểm tra 500 ms;
  sau đó ba lượt phản hồi liên tiếp 0,140 / 0,016 / 0,031 giây.
- So với trạng thái trước cài: nguồn/phiên bản bài, 1.224 WAV tham chiếu,
  cặp/tốc độ và checksum Key giữ nguyên.

[Bản phát hành RC109](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc109).
