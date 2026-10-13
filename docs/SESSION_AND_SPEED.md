# Giữ phiên Chrome và mở bài nhanh hơn — RC19

Chrome riêng của từng tài khoản dùng chế độ khôi phục phiên khi mở lại. Tool
chỉ sửa tùy chọn startup trong profile riêng khi Chrome đã đóng; giữ nguyên
các tùy chọn khác và không sửa/nhập cookie hoặc token. Profile đang được dùng
không bị mở lần hai hoặc xóa. Cấu hình hỏng không bị ghi đè. Cơ chế cookie
khôi phục dựa trên [mã nguồn Chromium](https://github.com/chromium/chromium/blob/main/chrome/browser/profiles/profile_impl.cc).

Trước thay đổi, thử Chrome nền thật với cookie phiên không có thời hạn lưu
cho thấy cookie mất sau đóng/mở. Sau thay đổi, cookie và local storage được
giữ trong đúng profile, không xuất hiện ở profile thứ hai. Đăng nhập bằng
Chrome thường được kiểm tra riêng với cookie có thời hạn. Chrome có thể xóa
cookie chỉ dùng trong phiên khi người dùng đóng cửa sổ đăng nhập; tool chỉ
báo thành công sau khi mở lại và kiểm tra được tài khoản. Không cam kết giữ
phiên mà web đã thu hồi hoặc hết hạn. Hai tài khoản Free đã lưu trên máy kiểm
tra lại thành công trong 8,53 và 7,42 giây; không gửi prompt/tài liệu mới.

PowerPoint nhận xong vẫn được kiểm tra slide và lưu bản nháp trước. Đến đó,
tiến trình chuyển đổi đạt 100% và mở bài để xem. Không còn chờ tạo toàn bộ WAV
trước khi lưu/mở bài. Trạng thái giọng đọc hiển thị riêng ở màn bài giảng;
âm thanh Việt/Anh xen kẽ được chuẩn bị ở nền, dùng đúng giọng và tốc độ đang
chọn. Khi cần đọc, reader tự lấy cache hoặc tạo đoạn cần đọc; không có thêm
bước gửi/nhận hoặc nút xác nhận để chạy âm thanh nền.

Giọng đọc dùng một engine duy nhất. Yêu cầu nghe thật được ưu tiên lượt kế
tiếp; nền tạm nghỉ khi chuyển đổi/xem slide/đọc đang hoạt động. Hai yêu cầu
cùng đoạn/giọng/tốc độ chỉ tạo WAV một lần, kiểm tra cache lại sau khi chờ.
Dừng nền giữ các WAV đã tạo. Lỗi giọng không hủy PowerPoint; ba lỗi engine
liên tiếp dừng warmup thay vì lỗi lặp từng slide. Khi mở lại tool, bài đã lưu
tiếp tục chuẩn bị âm thanh từ cache, không gửi lại lên ChatGPT. Lưu cấu hình
giọng mới hủy warmup cũ. Tắt tool hoàn tất lần gọi CPU đang chạy rồi dừng,
không terminate engine giữa chừng.

Một bài thực tế trước đó có 79 slide và 238 đoạn cần tạo, tổng tiến trình lưu
ghi 1.552 giây. Việc tạo đủ âm thanh trước khi lưu đã làm người dùng phải chờ.
RC19 loại bước chờ đó khỏi đường chuyển đổi. Không diễn giải thành số phút
tăng tốc ChatGPT: thời gian AI tạo/sửa PowerPoint vẫn do web, mạng và quyền
tài khoản quyết định. Nhật ký tiến trình mới có `stageSeconds` cho từng bước
của lượt chạy hiện tại để phân biệt thời gian tải tệp, AI chờ và xử lý máy.

Qt smoke dùng engine cố tình bị chặn/lỗi: thư viện đã có bài, màn kết quả có
PPTX và 100% trong khi giọng chưa xong; giao diện vẫn nhận sự kiện, lỗi giọng
không làm mất bài hoặc duyệt bản nháp. Kiểm tra riêng lượt ưu tiên, chống tạo
trùng WAV, hủy và lỗi engine. Không dùng fixture làm bằng chứng một bài mới
đã chuyển đổi thật qua ChatGPT. Quy tắc khôi phục/không gửi trùng và kiểm tra
FAIL/CHECK vẫn theo [Browser recovery](BROWSER_RECOVERY.md).
