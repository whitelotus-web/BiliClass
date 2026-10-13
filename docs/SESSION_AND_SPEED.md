# Giữ phiên Chrome và mở bài nhanh hơn

## RC23: giao diện gọn và giọng đọc nhanh hơn

Báo cáo slide/lời đọc được thu gọn mặc định vào **Xem chi tiết**. Màn kết
quả vẫn báo rõ số slide cần sửa hoặc cần rà soát, không tự duyệt bài hay
câu hỏi. Âm thanh chuẩn bị ở nền; số đoạn nằm trong chi tiết. Một lỗi âm
thanh không làm mất PowerPoint đã lưu. Không dùng loading để che lỗi.

Nút **Kiểm tra cập nhật** hiện ở cả bản nguồn lẫn bản Windows. Thanh điều
hướng cuộn riêng khi cửa sổ thấp để giữ nút cập nhật và phiên bản trên màn
hình. Kiểm tra bằng tay có hộp cập nhật ngay tại trang đang mở. Bản nguồn
có thể cài gói Windows cùng phiên bản; cơ chế này không kéo Git/ghi đè
checkout, không hạ phiên bản và vẫn kiểm tra checksum/manifest của gói.

VieNeu vẫn dùng model FP32, cùng giọng/tốc độ, một engine và quyền ưu tiên
lượt đọc đang được yêu cầu. NumPy/BLAS chỉ dùng một luồng trong lúc model
suy luận, tránh tranh CPU với bốn luồng ONNX; khôi phục cấu hình BLAS khi
ra khỏi lượt gọi, kể cả khi lỗi. Không đổi khóa cache hay tạo lại âm thanh
đã có. Tăng số worker dùng chung engine không an toàn với trạng thái model,
nên không gọi đồng thời nhiều lượt trên cùng engine.

Đo bốn câu Việt/Anh tổng 21,28 giây âm thanh trên i7-8700 (6 nhân/12 luồng):
4 luồng ONNX + BLAS mặc định 12 luồng mất 17,766 giây; 4 ONNX + 1 BLAS mất
14,734 giây (giảm khoảng 17%); 2 ONNX + 1 BLAS mất 15,812 giây. Cùng model,
speaker và seed; mỗi cấu hình có lượt làm nóng. Đây là mẫu thử trên máy
này, không phải cam kết tăng tốc tương đương trên mọi bài/máy. Không dùng
thời gian nạp model để so sánh vì cache hệ điều hành đã ấm.

Trước warmup, chỉ xếp đoạn còn thiếu hoặc WAV hỏng vào hàng đợi. Bài đã có
đủ âm thanh không khởi động QThread/nạp model và không đặt tiến độ về 0.
Kiểm tra chỉ đọc bài đã lưu 48 slide: 137/137 WAV hợp lệ, lập kế hoạch cache
mất 0,032 giây, không phát âm thanh, không gửi lại bài hoặc thay đổi dữ liệu
giáo viên. Tiến độ âm thanh có tín hiệu Qt riêng, không dựng lại toàn bộ
giao diện/preview sau mỗi đoạn; checkpoint lưu tối đa một lần/giây và luôn
lưu lúc kết thúc/dừng. Khi đổi giọng hoặc tốc độ, kiểm tra đúng khóa mới.

Chế độ chuyển đổi tự động không nén thêm ZIP tài liệu vốn không được dùng:
gửi đúng tệp nguồn/mẫu đã lưu và xác minh hash. Các gói thủ công cũ vẫn mở
được. Không giảm bước kiểm tra slide, chất lượng model hay xử lý xác minh.
Thời gian web tạo/sửa PowerPoint vẫn phụ thuộc tài khoản, mạng và dịch vụ;
những thay đổi trên tăng tốc phần việc tại máy, không bảo đảm toàn bộ bài
hoàn thành trong một thời gian cố định.

137 ca kiểm tra liên quan qua. Smoke Qt toàn luồng qua với Office preview
thật, web/voice fixture, không QML warning: báo cáo thu gọn/mở chi tiết,
nút cập nhật ở 1080×700, kiểm tra từ Cài đặt, quyền duyệt cả bài/quiz và
thông báo tiến độ âm thanh không kích hoạt dựng lại mọi view.

## Cơ chế giữ phiên và âm thanh nền từ RC19

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
