# RC104 — Màn hình khởi động và hướng dẫn F1

Màn hình khởi động dùng ảnh nền do người dùng cung cấp, giữ logo/màu/chữ
thật của BiliClass. Chuyển động chạy trong một tiến trình Qt nhỏ riêng,
nên không dừng theo lúc cửa sổ chính dựng QML. Các bước cập nhật theo
khởi tạo, mở thư viện và tải giao diện; thanh chuyển động biểu thị đang
làm việc, không hiển thị phần trăm ước lượng. Tự đóng sau khung hình đầu
của cửa sổ chính. Không thêm thời gian chờ để giữ màn hình loading.

Thông điệp nội bộ chỉ chứa tên bước. Màn hình này không mở thư viện,
key, mô hình hay giọng đọc. EOF đóng màn hình nếu ứng dụng mẹ thoát/lỗi;
không chờ tiến trình phụ trên luồng giao diện. Worker Office, các chế độ
chẩn đoán và smoke không mở màn hình khởi động.

F1 là hướng dẫn đọc, không có nút chuyển màn hình hay thay cấu hình.
Mục đầu giải thích Chung → Google Dịch → Giọng đọc → Mascot; sau đó là
chuyển đổi, tạo giọng, dạy bài, tìm/tải và sao lưu. Có mục lục, bước ngắn,
Trước/Tiếp/Đóng; nhớ mục đã đọc trong phiên. Không nêu tên bộ máy giọng.

Mascot bỏ dòng giải thích nút sáng và thay menu cách đọc bằng ba ô trên
một hàng: Tự động / Đang hiện / Toàn slide. Chỉ chọn một chế độ, có tooltip
ngắn; dùng cùng logic đọc đã có, chọn chế độ không tự phát âm thanh.

## Kiểm tra đúng phạm vi

- 29 kiểm thử khởi động/phiên dạy qua, gồm tắt trong smoke/worker, lỗi tiến trình
  tùy chọn không chặn desktop, đóng không chờ trên luồng giao diện.
- Qt thật: ảnh nền và các bước, chuyển động vẫn chạy khi tiến trình gọi
  ngủ, ready/EOF đóng cửa sổ và khởi động desktop kết thúc loading qua.
- Qt F1: bốn cài đặt đứng đầu, sáu mục, không tên bộ máy, sidebar/F1 cùng
  hướng dẫn, nhớ mục và giữ nguyên màn hình làm việc; hai kích thước qua.
- Ruff qua; không cảnh báo QML trong lượt F1 cuối.
- Qt Mascot: ba ô cùng hàng, chọn đúng chế độ và không bỏ chọn hết, không
  tràn chữ ở ba kích thước. Loa, âm lượng, kéo bảng và mở cài đặt qua;
  không cảnh báo QML. Thử bằng lệnh chặn, không điều khiển Office cá nhân.

Không chạy lại toàn bộ bộ kiểm thử 1.111 của RC103: các luồng chuyển đổi,
giọng và lưu dữ liệu không đổi. Bản đóng gói sẽ kiểm tra riêng đúng các
thay đổi khởi động/F1/Mascot và tính toàn vẹn bộ cài.

## Bộ cài và lần mở trên máy này

- Mã nguồn đóng gói: `9bd11dbf02e8479fb1e8fb1ea4188605c767d20d`.
- `BiliClass-RC104-Windows.zip`: 1.248.157.157 byte.
- SHA256: `ec7442b04f42481cbfa88161f0d1468b4feba48cc90f97b7cbb2f64446938944`.
- Toàn bộ nội dung ZIP khớp manifest; digest tài sản GitHub khớp SHA256.
- Thử executable đóng gói với thư viện tạm: ảnh và bước thật hiển thị,
  chuyển động độc lập, pipe hoạt động trong bản không console, loading
  tự đóng sau khung hình đầu; tiến trình phụ thoát sạch.
- Đã cài RC104 vào thư mục phiên bản riêng bằng bộ cài kiểm tra manifest.
  Executable, ảnh nền và ba QML thay đổi ở nơi cài khớp bộ đã thử.
- RC104 đã mở độc lập qua Explorer, có Mascot, biểu tượng và shortcut đúng.
  Đối chiếu nguồn bài, phiên bản chỉnh sửa, 940 WAV được tham chiếu,
  cặp/tốc độ và checksum key đều giữ nguyên. RC103 đã đóng bình thường.

Lần mở thư viện thật vẫn ghi nạp QML khoảng 5,03 giây. Kiểm tra cửa sổ
ghi nhận năm lần hết hạn 500 ms trong giai đoạn khởi động, sau đó ba lần
liên tiếp phản hồi (0,047 / 0,031 / 0,359 giây). Loading không làm khởi
động nhanh hơn; nó cung cấp phản hồi trong lúc chuẩn bị. Không đổi ngưỡng
hay xóa nhật ký để che khoảng nạp này. Đây là kiểm tra trên máy hiện tại.

[Bản phát hành RC104](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc104).
