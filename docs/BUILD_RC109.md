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
