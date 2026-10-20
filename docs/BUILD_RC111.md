# RC111 — Gọn menu Thao tác khác

Bỏ các mục Gửi gói bài cho giáo viên khác, Mở trong PowerPoint và Kiểm
tra và xác nhận khỏi menu Thao tác khác. Nút Mở PowerPoint chính vẫn ở
ngoài. Mục xác nhận toàn bài phục vụ duyệt nội dung cho Lớp học; không
trùng với chỉnh lời đọc, nhưng không cần đặt ở menu này.

Bỏ menu con Bài giảng, đưa các mục còn dùng ra một cấp. Giữ Kiểm tra /
sửa lời đọc, Sửa thông tin bài và Sửa nội dung bài giảng (bài chuyển ngữ).
Trang voice hoàn tất vẫn có Tải PowerPoint không giọng. Đổi tên cũ Sửa
nội dung trợ giảng để khớp công việc thực tế và cập nhật lời hướng dẫn.
Không xóa chức năng duyệt toàn bài hay chia sẻ ở các luồng khác.

Kiểm tra Qt trên thư viện tạm: menu ba mục trực tiếp cho bài chuyển ngữ,
hai mục cho bài chỉ tạo voice; các mục đã bỏ không còn tồn tại; mở được
hộp sửa lời đọc và sửa thông tin bài. Không có cảnh báo QML. 15 ca liên
quan đến duyệt bài/lời đọc và Ruff cho các smoke đã cập nhật đều đạt.

Gói RC111 được dựng từ commit `9d3770dc2b30308493cb89330f401649e0f4fe17`,
ZIP 1.249.943.735 byte, SHA-256
`60fa86bba96c14f6dd55cb53704d12a1704771a22bdc2b7a15bd57aef70d09a6`.
Đã xác minh manifest, ZIP và QML khớp nguồn đã kiểm tra; digest của tài
sản trên GitHub khớp SHA-256 này. Phát hành: `v1.0.0rc111`.

Đã cài RC111 và mở trang bài giảng qua Explorer độc lập với Codex.
Cửa sổ chính và Mascot hiển thị, shortcut/taskbar đúng phiên bản. Khi
khởi động có bốn lần thăm dò phản hồi quá 500 ms; sau đó cả hai cửa sổ
đạt ba lần phản hồi liên tiếp trong ngưỡng. Đối chiếu trước/sau: nguồn
bài, revision, 1.224 WAV được tham chiếu, lựa chọn giọng và khóa dịch
mã hóa đều giữ nguyên. Không đóng các PowerPoint độc lập của người dùng.
