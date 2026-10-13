# Khôi phục chuyển đổi Browser AI — RC18

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
