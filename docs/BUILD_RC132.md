# RC132 — Thư viện gọn hơn và điều khiển bài từ Mascot

Thư viện dùng biểu tượng loa với VI/EN/VI + EN; chưa có giọng dùng
loa gạch chéo. Tooltip và tên trợ năng giữ trạng thái đầy đủ, thao tác
vẫn mở cấu hình giọng. Nút tải từng bài dùng icon chung cho danh sách
và thẻ. Bộ lọc giãn ngang theo cửa sổ. Ngày tạo thêm thứ tiếng Việt;
ở danh sách nằm bên trái dưới môn học với khoảng cách riêng. Thẻ bỏ
chiều cao tiêu đề dư và đặt môn/khối/số slide cùng hàng với ngày tạo.

Cài đặt Mascot xếp Luôn nổi trên cùng trước Hiện phụ kiện theo môn.
Ô môn luôn hiện, khóa khi bỏ tích phụ kiện và giữ lựa chọn cũ. Độ rộng
đo theo tên môn dài nhất, tính cả lề chữ/mũi tên để không cắt tên môn.

Tooltip phím khớp chiều ngang và mép trái bảng trợ giảng khi hiện phía
trên; giữ cách tránh che bảng khi gần mép màn hình. Căn giữa thông báo
chưa gắn bài, hướng dẫn chọn bài và trạng thái giọng. Bỏ nhắc Bấm Trình
chiếu để đọc giọng; dùng Trình chiếu · F5 cả ở bảng nhỏ.

Thêm nút đóng bài bên phải môn học trong bảng Mascot, dùng luồng đóng
bản sao quản lý có sẵn: dừng giọng/trình chiếu, đóng đúng bản đang gắn
và gỡ liên kết. Không xóa bài lưu hoặc đóng cửa sổ PowerPoint khác.
Đổi bài chuẩn bị B trước; nếu chuẩn bị thất bại A tiếp tục. Khi B đã
sẵn sàng, chờ phiên A đóng xong rồi mở B ở trạng thái sẵn sàng/F5.
Bảng hiện tiến trình chuẩn bị/mở/đóng để tránh tưởng thao tác chưa nhận.

Chuẩn bị bài đọc danh sách loa từ XML theo thứ tự slide, giữ slide im
lặng và chỉ nhận audio thật, thay vì giải nén ảnh/âm thanh bằng python-pptx
lần nữa. Trên ba bản sao bài 20/70/79 slide, kết quả giống cách cũ;
khâu này nhanh hơn khoảng 4–6 lần, không phải toàn bộ thời gian mở Office.
Cache bài có giọng phụ thuộc phiên bản định dạng riêng cùng nội dung,
giọng, vị trí loa và dấu thời gian WAV; đổi phiên bản giao diện không
buộc nhúng âm thanh lại. Cần tăng FORMAT_VERSION khi đổi cách nhúng loa.

Xác minh bằng `.venv`:

- 63 pytest luồng dạy/đóng/đổi bài, cache, XML loa, thư viện và Mascot đạt.
- Qt danh sách/thẻ, bộ lọc, chọn/kéo chọn, nút tải và điều hướng đạt ở
  1080/1366/1920; đã xem ảnh, không cảnh báo QML.
- Qt bảng Mascot ba cỡ, tooltip native cùng chiều ngang/mép trái,
  fallback gần mép màn hình, khóa ô môn mà giữ lựa chọn, thao tác đóng
  đúng phiên đạt. Tên môn dài nhất vừa khung sau khi tính lề chữ.
- PowerPoint thật với bài/âm thanh im lặng dùng một lần: đổi A đang
  chiếu sang B, xác minh HWND trình chiếu A đóng và bản sao A được
  giải phóng; B sẵn sàng, chưa tự chiếu. Thử nút đóng mới và nguồn giữ
  nguyên. Lượt đổi bài thử mất khoảng 5,1 giây; không đại diện mọi máy/bài.
- WAV, ảnh, tệp PowerPoint thử và báo cáo chỉ ở thư mục ngoài Git.
