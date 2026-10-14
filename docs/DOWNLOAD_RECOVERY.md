# Nhận tệp PowerPoint và giới hạn kiểm chứng — RC33

Một tác vụ cũ có thể giữ mốc 55% dù đã có câu trả lời: mốc này bắt đầu bước
nhận tệp, không chứng minh tệp đã có trên máy. Nhật ký của bài thử ghi nhận
khoảng 44 phút chờ kết quả và 6 phút ở các lượt nhận tệp. Không nên giải thích
thời gian đó là thời gian tạo voice; voice chưa được yêu cầu.

## Thay đổi

- Ưu tiên liên kết tải thuộc câu trả lời mới nhất trước thẻ mở xem trước.
- Hiểu nhãn `Open preview of`, `Download`, `Download file` và nhãn có biểu
  tượng/ngôn ngữ Việt. Chỉ lấy nút tải trong thẻ/khung có đúng tên tệp;
  không lấy tài liệu nguồn hoặc tệp khác trong câu trả lời.
- Theo dõi phản hồi tải do giao diện phát sinh, đối chiếu tên trong
  Content-Disposition rồi phát hiện request lỗi. Không đọc token, gọi URL
  nội bộ, sửa CSP hay bỏ qua xác minh web. Không coi ERR_ABORTED khi chuyển
  trang/bắt đầu tải thông thường là bằng chứng tệp hỏng.
- Lỗi `file_transfer` chỉ thử nhận lại một lần trên tài khoản/cuộc trò chuyện
  cũ; sau đó tạm dừng. Không tự gửi lại bài hoặc khởi động lại vô hạn khi mở app.
  Trạng thái đăng nhập tài khoản được giữ độc lập với lỗi truyền tệp.
- Cho giao diện web thêm tối đa hai lượt đọc lại cấu hình model/suy luận
  khi nút chưa xuất hiện cùng ô soạn thảo. Vẫn chặn gửi nếu không xác nhận
  được lựa chọn; không tự hạ cấu hình.

## Kiểm chứng và tình trạng bài thật

66 ca liên quan, trong đó có Chrome thật với giao diện mô phỏng và máy chủ
HTTP cố ý ngắt thân tệp, đều qua. Kiểm tra Qt startup/resume và ảnh giao diện
1366×850 qua, không warning. Đây không phải chứng nhận một lượt chuyển đổi
web thật đã thành công.

Đối với bài 65 slide đang dở, tài khoản vào được màn chat. Tệp đầy đủ, một
bản sao và một gói trung gian nhẹ đều có thẻ tệp nhưng thao tác tải web bị
ngắt. Khung xem tệp cũng báo “Couldn't load this file”. Bản sửa phát hiện
lỗi sau 3,95 giây trong phép thử thật; không thêm yêu cầu chuyển đổi khi
kiểm tra lỗi này. Xóa HTTP cache riêng không giải quyết được; cookies và
đăng nhập được giữ nguyên. Chưa chứng minh nguyên nhân bên trong dịch vụ.

Không nhập gói trung gian có media rỗng, không đánh dấu PASS hoặc 100%, không
phát sinh bài mới/voice từ các kết quả chưa nhận được. Bản ghi của bài đang dở
đã được giữ để trỏ đúng câu trả lời chứa tệp đầy đủ, bỏ qua các bản xuất chẩn
đoán. Thư viện riêng, media, báo cáo và profile không thuộc Git.
