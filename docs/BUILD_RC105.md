# RC105 — Loading gọn và mượt hơn

Bỏ dãy ba vòng tròn/đường nối cuối màn hình; chỉ giữ trạng thái đang làm
và thanh loading mảnh, cân lại khoảng cách với logo. Thanh chạy bằng
XAnimator của Qt trên luồng kết xuất, chu kỳ 1,15 giây thay 1,55 giây.
Khi cửa sổ chính vẽ xong, loading mờ ra trong 110 ms rồi đóng; khoảng
đóng giảm từ 180 xuống 120 ms. Không thêm thời gian chờ để trình diễn.

Tôn trọng lựa chọn tắt chuyển động của Windows: dùng thanh tĩnh và đóng
ngay khi sẵn sàng. Ảnh gốc, các bước nội bộ và việc tách tiến trình giữ
nguyên. Không sửa luồng thư viện, chuyển đổi, giọng đọc hay Mascot.

Phạm vi cải thiện là cách hiển thị và chuyển tiếp loading. Thời gian
chuẩn bị giao diện chính vẫn phụ thuộc máy/thư viện; không coi tốc độ
thanh chuyển động là phần trăm công việc hay số đo tốc độ khởi động.

Kiểm tra trước đóng gói: 5 kiểm thử vòng đời qua; Qt Windows dùng thư
viện tạm xác nhận ảnh/bước thật, chuyển động độc lập, ready/EOF đóng
tiến trình và cửa sổ chính tiếp quản. Ảnh thực tế đã kiểm tra bố cục.
Ruff và kiểm tra khoảng trắng qua. Không chạy lại các bộ chuyển đổi,
giọng đọc hay thư viện vì mã các luồng đó không đổi.

## Bộ cài đã kiểm chứng

- Mã nguồn: `235aac5c1740c6e578abf0d696761380a4ebaca2`.
- ZIP: 1.248.157.026 byte; SHA256
  `487cbbec6ff9683fb682426814b1157cc4eaf3290d9549b556dc94ffd0fb035c`.
- Nội dung ZIP khớp manifest; digest GitHub khớp checksum.
- Qt thật trên executable đóng gói qua: ảnh/bước, chuyển động, pipe,
  ready/EOF và giao diện chính tiếp quản. Lựa chọn Windows hiện tại bật
  chuyển động; không thay thiết lập hệ thống của người dùng để thử.
- RC105 đã cài riêng, executable/QML thay đổi khớp bộ đã thử; mở độc lập
  qua Explorer, biểu tượng và shortcut đúng. Một lần kiểm tra cửa sổ hết
  hạn 500 ms lúc khởi động, tiếp đó ba lần phản hồi 0,110 / 0,016 / 0 giây.
- Đối chiếu nguồn bài, phiên bản chỉnh sửa, 940 WAV tham chiếu, cặp/tốc độ
  và checksum key giữ nguyên. RC104 đóng bình thường và còn làm dự phòng.

[Bản phát hành RC105](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc105).
