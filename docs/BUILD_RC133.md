# RC133 — Icon loa Việt/Anh do thầy cô cung cấp

Thay ký hiệu loa nhỏ kèm chữ rời trong thư viện bằng đúng hai PNG
VI/EN người dùng gửi ngày 21/10. Giữ nguyên byte và kênh alpha nguồn;
QML chỉ cắt lề trống để phần loa/chữ sẵn trong ảnh đủ lớn. EN dùng
xanh dương, VI dùng tím trên cả nền sáng/tối. Có cả hai giọng hiện hai
icon cạnh nhau trên nền xanh lá nhạt; chưa có giọng dùng loa gạch
chéo xám. Tooltip/tên trợ năng giữ ý nghĩa đầy đủ. Chỉ các bản giọng
đã hoàn tất được hiện icon tương ứng; không đổi cách xác định giọng.

ThemedImage thêm tùy chọn tô màu từ alpha, mặc định giữ hành vi cũ
(chỉ tô màu khi nền tối). Nhãn giọng bật tùy chọn để màu EN/VI nhất
quán cả hai giao diện. Nút trạng thái cao 36 px, giữ vùng bấm 96 px
và thao tác mở cấu hình giọng.

Xác minh bằng `.venv`: 14 pytest thư viện/giao diện đạt. Qt danh sách
và thẻ, chọn/kéo chọn, bộ lọc, tải đúng bài và điều hướng đạt tại
1080/1366/1920, không cảnh báo QML. Đã xem cả bốn trạng thái trên
nền sáng/tối; icon VI/EN đúng ảnh, không có chữ bên ngoài lặp lại.
