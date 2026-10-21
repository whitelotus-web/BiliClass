# RC137 — Hủy bài sạch trạng thái và Mascot theo lúc dạy

Bao gồm toàn bộ sửa thuật ngữ Hóa, lời đọc và nhãn số Toán của
RC136. Sau Hủy bài đang chọn trong màn chuyển đổi Google, tool
bỏ yêu cầu tạm dừng/lỗi khỏi tác vụ hiện tại, đặt tiến độ và đồng hồ
về 0, xóa thông báo lỗi và ẩn nút Tiếp tục cũ. Đổi sang một tệp hợp
lệ khác cũng bỏ tác vụ cũ; chọn lại luôn bắt đầu từ cấu hình mới.
Không xóa tệp nguồn, cache bản dịch, khóa API, hạn mức, bài đã lưu
hay WAV. Yêu cầu chưa lưu bị đánh dấu không tự tiếp tục khi mở app.
Nút Dừng trong lúc chạy vẫn giữ tác vụ để tiếp tục như trước.

Đối chiếu bên Tạo giọng: Hủy bài sau khi lỗi/dừng đưa phần chọn bài
về trạng thái rỗng, phát đủ tín hiệu cập nhật lời đọc và bản xem trước,
không giữ thông báo lỗi của bài trước. Giữ bài/plan/âm thanh trong
thư viện. Nếu đang tạo giọng, chờ dừng đoạn hiện tại rồi mới bỏ chọn.

Theo lựa chọn của người dùng, Mascot ẩn lúc khởi động. Lần đầu mở
bài giảng từ tool tự hiện; đã từng hiện hoặc chủ động mở trong phiên
thì các lần đổi/mở bài sau không tự bật lại. Nút Mở trợ giảng nổi
vẫn mở bất cứ lúc nào. Vị trí, kích thước và các tab Cài đặt giữ nguyên.

Xác minh trong `.venv`: 189 pytest đạt, gồm lưu/hủy tác vụ ở trạng thái dở và đã lưu,
Qt chuyển đổi chạy/dừng/tiếp tục rồi hủy/chọn lại, Qt tạo giọng lỗi rồi
hủy, Qt vòng đời Mascot và luồng Office thật. Kiểm tra dùng dữ liệu
thử; không xóa bài hay âm thanh của thầy cô.
