# Sau tạo giọng — RC50

Ngày 16/10/2026. Bản giọng đã đủ âm thanh vẫn chọn được để dạy/tải, nhưng
nút tạo trùng của đúng nội dung/ngôn ngữ/giọng/tốc độ bị khóa. Các lựa chọn
Anh / Việt / Việt–Anh hiện Chưa tạo, Đã tạo, Cần tạo tiếp hoặc Đang kiểm tra.
Đổi giọng/tốc độ được tạo bản mới. WAV thiếu/hỏng mở lại khả năng tạo tiếp;
backend kiểm tra thật trước khi từ chối yêu cầu, không chỉ khóa giao diện.
Yêu cầu trùng không ghi lại metadata, khởi động worker hoặc reset đồng hồ.

Ngay khi bản giọng đủ, khung Bước tiếp theo có Tiếp tục: chuẩn bị dạy và
Tải PowerPoint. Hoàn thành không tự chuyển màn hình hoặc phát âm thanh.
Bước chuẩn bị cho chọn bản giọng, xem tên bài/số slide, xác nhận kiểm tra
nội dung rồi Bắt đầu dạy. Giữ chặn bản giọng thiếu và slide còn FAIL.
Nút Dùng để dạy phía trên cũng đi qua cùng bước này, kể cả khi mở lại bài.
Không thêm một bản sao bài hay yêu cầu phải tạo giọng mới được dạy.

Các trạng thái chưa chọn dùng dữ liệu catalog đã kiểm tra ở worker; không
thêm quét filesystem cho mỗi nút radio hoặc mỗi giây đồng hồ. Giữ các bản
giọng đã lưu và cơ chế tạo phần thiếu của RC49.

Kiểm chứng: 83 kiểm thử liên quan (gồm đồng bộ key) qua; Qt result ở 1080×700 và 1366×850
kiểm tra khóa tạo trùng nhưng chọn được, đổi tốc độ mở tạo, bước tiếp theo
chỉ mở khi bấm và không tự duyệt slide lỗi. Có kiểm tra trình chiếu PowerPoint
thật cho luồng xác nhận, phát cache, mascot theo slide, đóng và mở lại.
Phạm vi đóng gói/cập nhật ghi riêng khi hoàn tất bộ cài.

Theo yêu cầu đồng bộ key không có mật khẩu bổ sung: Cài đặt Google Dịch có
nút gửi/nhận qua kho GitHub riêng tư, dùng đăng nhập Git Credential Manager.
Kiểm tra kho còn private trước mọi lượt; chặn kho công khai, giữ nhóm key và
không reset bộ đếm khi nhập lại. Key nhận được chỉ lưu DPAPI ở máy đó.
Đây là snapshot khi bấm, không phải đồng bộ quota trực tiếp giữa các máy.
