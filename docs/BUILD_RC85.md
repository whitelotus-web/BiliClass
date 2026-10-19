# RC85 — Bố cục chuyển đổi, hoàn tất bài và chia trang dài

Khi có bài chuyển đổi đang chuẩn bị, phần bên trái footer chỉ còn nút
Tiếp tục bài đang chuẩn bị. Giới hạn chiều rộng suy ra từ layout con làm
phần này không giãn hết chỗ trống, khiến nút Chuyển đổi bài giảng bị đặt
vào giữa thanh dưới.

Cho phần trái giãn tới hết chiều rộng còn lại. Nút chuyển đổi giữ lề phải
28 px khi có/không có bài đang chuẩn bị, ở các kích thước cửa sổ. Footer
tạo giọng dùng chung cũng được kiểm tra. Không thay đổi luồng chuyển đổi.

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
đã tồn tại. Kết quả bộ cài được bổ sung sau khi hoàn tất.
