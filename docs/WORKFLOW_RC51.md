# Thư viện và dạy học tương tác — RC51

Một bài lưu nhiều bản giọng, phân biệt ngôn ngữ/người đọc/tốc độ. Thư viện
chỉ tóm tắt ngôn ngữ có sẵn, không lặp bản ghi cũ hoặc liệt kê người đọc.
Mở bài để chọn bản dạy/tải; không nhân bản bài trong thư viện.

Thư viện có chọn từng bài, chọn tất cả kết quả đang lọc qua nhiều trang,
bỏ chọn, tải và xóa đã chọn. Đổi bộ lọc bỏ chọn để tránh tác động bài ẩn.
Xóa xác nhận một lần, kiểm tra toàn bộ ID và tiết chưa kết thúc trước khi
ghi một transaction; đưa vào thùng rác, giữ source/WAV/báo cáo để khôi phục.
Chặn xóa khi chuyển đổi, tạo giọng, trình chiếu hoặc lớp học đang chạy.

Tải từng bài là PPTX; nhiều bài là ZIP chứa tên duy nhất, loại giọng và
hướng dẫn. Kiểm tra bản trình chiếu và WAV ở worker. Tùy chọn kèm giọng dùng
bản đang chọn chỉ khi đã đủ; bản thiếu xuất không âm thanh. Không tự tạo
voice. Không thay bản giọng hay duyệt bài trong thư viện khi tải. Tệp đích
chỉ thay sau khi tất cả bài xuất thành công; lỗi/hủy giữ tệp đích cũ.

Lớp học giải thích mục đích tương tác, chỉ rõ ba bước và có đường đi đến
chuẩn bị bài/câu hỏi/báo cáo. Nút mở lớp chặn bài chưa chốt, tên trống và
mạng chưa chọn. Báo cáo tìm không dấu theo lớp/bài/môn, lọc đang mở/đã kết
thúc, hiển thị ngày và số phản hồi. Giữ snapshot và điều kiện mẫu đủ của
analytics; không đánh giá mức hiểu bài từ số lượt nghe/xem.

Tên Thuật ngữ & kiến thức thay Dữ liệu trợ giảng. Tìm thuật ngữ không dấu,
lọc môn có thật trong kho và phân trang 20 mục; tìm kiến thức chờ gõ xong
220 ms, không truy vấn lặp cho cùng danh sách và trạng thái rỗng.
Phụ kiện mascot nhỏ hơn, bỏ nền trắng bao ngoài, gắn lên sách/tablet và
ẩn ở tư thế không phù hợp. Chuyển động, nháy mắt và giảm chuyển động giữ lại.

Kiểm chứng: 111 kiểm thử liên quan; Qt thư viện với 24 bài qua hai trang,
hủy/xóa/khôi phục trong thư viện thử, tìm/lọc và điều hướng ba màn, hai cỡ
1080×700 và 1366×850 không QML warning. Qt result và trình chiếu PowerPoint
thật kiểm tra lại bước sau tạo giọng, đọc cache, mascot và đổi/đóng slide.
Mẫu ít/slide phức tạp vẫn cần thầy cô kiểm tra; không chứng nhận mọi bộ PPTX.

RC51 bao gồm luồng sau tạo giọng và chuyển key bằng đăng nhập GitHub ở RC50.
Hai API key được gửi riêng vào kho GitHub private theo yêu cầu chủ máy,
không nằm trong commit/bộ cài công khai. Kiểm chứng nhập snapshot vào thư viện
thử giữ bộ đếm và mã hóa Windows; đây không phải bộ đếm quota liên máy.
