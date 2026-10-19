# RC85 — Bố cục chuyển đổi, hoàn tất bài và chia trang dài

Khi có bài chuyển đổi đang chuẩn bị, phần bên trái footer chỉ còn nút
Tiếp tục bài đang chuẩn bị. Giới hạn chiều rộng suy ra từ layout con làm
phần này không giãn hết chỗ trống, khiến nút Chuyển đổi bài giảng bị đặt
vào giữa thanh dưới.

Cho phần trái giãn tới hết chiều rộng còn lại. Nút chuyển đổi giữ lề phải
28 px khi có/không có bài đang chuẩn bị, ở các kích thước cửa sổ. Footer
tạo giọng dùng chung cũng được kiểm tra.

Sau khi chuyển đổi, giữ ở màn hình Đã tạo bài giảng. Tạo giọng đọc là
nút chính; có Tải bài giảng, Mở PowerPoint và Về Bài giảng. Không tự
chuyển sang bước giọng đọc hoặc chạy thêm preview/sửa bài sau khi báo
hoàn tất. Khi quay lại kết quả sau khi duyệt bài khác, nạp đúng bài đã
chuyển đổi trước khi cho tải hoặc mở. Ghi chú bố cục còn lại tách khỏi
thông báo lỗi của tác vụ.

Sửa chia trang: một đoạn dài hơn chiều cao dự kiến không được làm bỏ
qua cả khung nhiều đoạn. Từng cặp Việt–Anh chỉ xuất hiện ở đúng trang
tiếp nối của nó. Giữ nguyên đoạn, công thức, ảnh và hiệu ứng gốc.

Kiểm tra cục bộ trên bài gặp vấn đề: dùng lại bản dịch lưu trong cache,
không gọi API, từ 21 slide/2 lỗi tràn thành 22 slide/0 lỗi tràn đo bởi
Office. Vẫn giữ các ghi chú cần đối chiếu hình/hiệu ứng; không coi kiểm
tra hình học là chứng nhận chính xác mọi nội dung.

942 test core đạt, gồm hồi quy chia trang; lint/compile đạt. Các luồng Qt
chuyển đổi, chọn file và bố cục 4 kích thước đạt, không warning QML.
Office thật: mở từ màn hình hoàn tất gắn đúng Mascot, trước/sau tạo giọng,
đổi bài, F5 và loa native đạt. Thử chuyển đổi dùng API fixture, không
dùng key thật hoặc gửi nội dung cá nhân. Có một warning Starlette/httpx
đã tồn tại.

## Bản phát hành đã kiểm chứng

- Nguồn `9bcd8219bc13e75803485bb3c81c967e1763936b`;
  [CI đạt](https://github.com/whitelotus-web/BiliClass/actions/runs/39202690081).
- [Release RC85](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc85):
  ZIP 871.228.386 byte, 4.215 mục. Digest GitHub khớp
  `e24a57a5e75070617eec5a9cfc1690abef1c3cf1d17833cad374609338acb4d5`.
  Dựng đúng một lần từ runtime RC84 đã đối chiếu, biên dịch lại mọi module
  ứng dụng; EXE/model không nằm trong commit.
- Kiểm tra bản cài ở đường dẫn Unicode đạt: Properties sản phẩm/phiên
  bản/copyright, trang Chuyển đổi và Browser AI, template, VieNeu Việt/Anh
  cùng giọng, process lớp học, backup. Gỡ bản thử vẫn giữ thư viện riêng.
  Báo cáo cục bộ `reports/release/1.0.0rc85-d529fdd1/installer.json`.
- Cài chính tại `F:/Applications/BiliClass/1.0.0rc85`; mở trang Chuyển đổi
  từ Explorer, xác nhận đúng main window RC85 và Mascot, có phản hồi,
  parent `explorer.exe`, độc lập Codex. Lần khởi động đầu có chờ nạp DLL
  và dựng Qt khi máy đồng thời sao chép/đóng gói; không coi lần mở này
  là chứng minh mọi nguyên nhân chậm/treo đã được giải quyết.
- Bản thử chia trang được dựng ở reports, không thay thế bài cá nhân đã
  lưu. Chuyển đổi lại nguồn để áp dụng cách chia trang mới. Không đưa
  bài cá nhân, key hoặc báo cáo chẩn đoán vào Git/gói phát hành.
