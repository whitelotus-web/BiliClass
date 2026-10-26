# BiliClass 1.0.0rc169

Mốc phát hành ngày 26/10/2026, giữ bản phát hành/tag RC167 trước đó.

- Bốn dịch vụ dịch có cấu hình độc lập, thuật ngữ dùng chung và dự phòng có
  giới hạn. Không đóng gói key, thư viện hay dữ liệu cá nhân của người dùng.
- Word `.docx` chọn đoạn/câu hoặc bôi đen nhiều vùng; xác nhận sau khi nhả
  chuột. Bốn kiểu chuyển đổi, xem/sửa Anh và từ khóa; tự lưu cạnh nguồn với
  hậu tố `(Song ngu VI-EN)`, giữ checkpoint khi dừng/lỗi. Thư viện dùng chung
  phân biệt Word/PowerPoint, giọng đọc chỉ áp dụng cho PowerPoint.
- Tên bài học, màu/phông gốc hoặc tùy chọn, nghiêng/đậm; nhớ lựa chọn định
  dạng mới nhất cho bài mới, giữ cấu hình của bài cũ khi mở lại.
- Tốc độ Việt/Anh riêng; lần đầu 100%, nhớ khi bấm Lưu. Thêm 75%, 70%, 60%;
  giữ cao độ bằng WSOLA. Tốc độ rất chậm có thể nghe kéo dài âm tiết. Mã tốc
  độ RC167 và cache âm thanh cũ giữ nguyên ý nghĩa; bản mới ghi tốc độ từng
  ngôn ngữ trong plan/cache/export và mascot phát đúng bản đã tạo.
- Hai biểu tượng P/W dùng ảnh do giáo viên cung cấp; F1 và hướng dẫn cập nhật.

Nguồn được kiểm tra với môi trường `.venv`: kiểm thử giọng đọc/caching,
ngôn ngữ riêng, tạo/tiếp tục/tạo lại, Word và kiểu chữ, bốn dịch vụ dịch,
installer/updater. Qt Word, chọn bài tạo giọng và Cài đặt đã chạy bằng dữ
liệu tạm ở nhiều kích thước, sáng/tối; không cảnh báo QML. Kiểm cao độ bằng
tín hiệu thử chứng minh không hạ cao độ theo tốc độ, không chứng nhận mọi
câu/giọng đều tự nhiên ở mức 60%.

Kiểm thử bộ cài Windows RC167 → RC169 vào cùng thư mục được quản lý giữ
nguyên thư mục phiên bản cũ, thư viện, byte dữ liệu/key/cài đặt. Bản gói
phải được kiểm manifest, SHA-256, Qt và pipeline trong runtime đã cài trước
khi công bố. Tái dùng runtime/model RC167 chỉ sau kiểm toàn bộ hash; biên
dịch lại toàn bộ module ứng dụng, QML/assets từ commit nguồn mới. Không có
thay đổi dependency hay model trong mốc này.

Đây là kiểm chứng trên máy phát triển; trước khi dùng để dạy nên sao lưu
thư viện và đối chiếu kết quả trên máy đích. Không khẳng định tương thích
tuyệt đối với mọi Windows/Office hoặc mọi tài liệu.
