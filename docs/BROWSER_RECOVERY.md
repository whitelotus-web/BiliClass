# Khôi phục chuyển đổi Browser AI — RC18

## Bổ sung RC29 — 14/10/2026

Ngân sách chờ mặc định 900 giây được lưu theo hash prompt đã gửi, tính tổng
thời gian chờ thực trong các lần nối lại. Đóng/mở lại hoặc retry không cấp
thêm 900 giây cho cùng lượt; thời gian app tạm dừng không bị cộng. Yêu cầu
xuất/sửa tiếp theo có hash mới được theo dõi riêng. Đã hết ngân sách thì
vẫn kiểm tra và nhận file sẵn có trước khi báo hết chờ, nhưng không tiếp
tục vòng đợi hoặc tự khởi động lại. Đây là giới hạn chờ mỗi lượt, không phải
cam kết toàn bộ bài sẽ xong trong 15 phút.

Nếu cuộc trò chuyện chỉ còn bản tóm tắt hoạt động xử lý, không có câu trả
lời cuối và không có điều khiển đang tạo, theo dõi thêm 60 giây không đổi.
Chỉ gửi một yêu cầu hoàn tất tệp khi so khớp toàn bộ prompt trong lượt người
dùng cuối cùng. Không đoán rằng tóm tắt hoạt động là kết quả; không tải lại
bài gốc. Lượt xuất cũng không có tệp thì giữ cuộc trò chuyện và báo cần kiểm
tra thay vì tiếp tục gửi vô hạn. Đây là khôi phục có giới hạn, không bảo đảm
dịch vụ có thể xuất PPTX cho mọi tài khoản/tài liệu.

Màn chuyển đổi có HH:MM:SS cập nhật mỗi giây, phân biệt đang chạy, tạm dừng
và hoàn tất. Thời gian dừng không làm đồng hồ tăng; mở lại đọc checkpoint.
Phần trăm vẫn theo mốc công việc thật, không có countdown giả. Nhật ký và
tệp cá nhân không đưa vào Git. Định hướng tăng tốc tiếp theo:
[dịch theo cụm và xử lý PPTX cục bộ](CONVERSION_SPEED_PLAN.md).

## Cơ chế trước RC29

Ngày 13/10/2026, nhật ký một bài đang chuyển đổi dừng ở `submitting`, chưa lưu
được URL, với `TimeoutError` ở bước gửi. Kiểm tra trên cùng profile tìm thấy
nguyên văn prompt trong cuộc trò chuyện và nhận được PPTX 75.246.124 byte.
Đây là lỗi xác nhận thao tác gửi, không phải bằng chứng mất đăng nhập. Không
đưa bài, prompt, profile hay tệp tải về của giáo viên vào Git.

- Nút Gửi được kích hoạt bằng bàn phím sau khi xác nhận prompt và toàn bộ tệp.
  Focus xảy ra trước ghi ý định gửi; ý định và SHA-256 lưu trước kích hoạt.
  Timeout sau kích hoạt chuyển sang quan sát xác nhận, không bấm lại.
- Lỗi mạng/browser/tải kết quả/xác nhận gửi được khôi phục có giới hạn, với
  khoảng nghỉ 2, 5, 10 giây. Chờ có thể hủy. Khôi phục xác nhận chỉ kiểm tra
  profile đã gửi, các tab được khôi phục và tối đa 10 chat gần đây trên giao
  diện. Cần tìm duy nhất một chat có toàn bộ prompt ở thông điệp người dùng.
  Không dùng tiêu đề, tên tệp, lời đáp của AI hay việc còn đăng nhập làm bằng
  chứng bài đã gửi. Yêu cầu cũ được đọc tương thích, không tự xóa trạng thái gửi.
- Khi tìm được xác nhận, tiếp tục chờ/nhận kết quả, nhập thư viện và chuẩn bị
  lời đọc. Giữ việc kiểm tra bản nháp, báo cáo slide và quyền duyệt của giáo viên.
  Tác vụ tự động đã được lưu có thể tiếp tục sau khi khởi động lại, gồm cả
  PowerPoint đã tải nhưng chưa nhập xong. Dấu Dừng của người dùng được lưu riêng
  để worker ghi nhật ký không làm mất lựa chọn đó; tác vụ đã lưu vào thư viện
  không tự mở lại hoặc chạy lại. Yêu cầu cũ chưa có cờ cho phép không tự khởi chạy.
- Trước khi gửi, chọn tài khoản còn kết nối/còn quyền theo ưu tiên đang có;
  sau khi bắt đầu gửi, giữ tài khoản và chat đó. Một tài khoản thứ hai đã đăng
  nhập không thể thay thế cuộc trò chuyện của tài khoản trước.
- Lỗi của bài (upload, thiếu PPTX, chưa rõ xác nhận) nằm ở trang chuyển đổi.
  Browser AI chỉ ghi lỗi phiên/hạn mức ở đúng profile; bỏ thông báo lỗi phiên
  chung bị lặp dưới các tài khoản khác.

Nếu hết lượt, cần đăng nhập/xác minh, không tìm thấy xác nhận sau các lần thử,
hoặc nhiều chat trùng prompt, tool dừng và giữ bài. Không gửi mù, không đổi tài
khoản sau gửi, không tự vượt xác minh hoặc tạo quyền model/hạn mức không có.
Không cam kết tự sửa mọi thay đổi giao diện hoặc mọi lỗi phía ChatGPT.

Kiểm tra: Chrome thật với trang fixture cho tình huống lớp phủ chặn chuột,
timeout sau khi phím gửi đã tới web, mất xác nhận trước khi lưu URL, tiếp tục
yêu cầu cũ, prompt khác/trùng/đã sửa; xác nhận không gửi trùng. Qt smoke kiểm
tra tự khôi phục, trạng thái hai profile độc lập và xem bài bằng PowerPoint.
Việc nhận lại bài thật đã kiểm tra riêng, không thay thế bằng chứng fixture.
