# RC37 — sửa cửa sổ đứng khi cập nhật tiến độ

Ngày 15/10/2026. Chẩn đoán từ chính tiến trình RC36 đang báo Not Responding;
không suy luận nguyên nhân chỉ từ phần trăm hoặc ảnh chụp.

## Nguyên nhân đã xác định

Luồng chuyển đổi vẫn ghi checkpoint ở nền trong khi đồng hồ trên cửa sổ dừng.
Stack của luồng Qt chính cho thấy chuỗi:

`_on_conversion_progress → inform → changed → trashedLessons → list_lessons
→ audio_status → valid_key → pathlib.resolve / ntpath.realpath`.

Mỗi thông báo tiến độ phát lại tín hiệu thay đổi toàn màn hình. Các binding
danh sách bài/thùng rác đọc thuộc tính nhiều lần, mỗi lần lại kiểm tra nhiều
WAV. Trạng thái âm thanh còn đếm lại cùng khóa khi tính từng ngôn ngữ và tổng
số đoạn. Những lần kiểm tra dồn vào hàng đợi Qt làm cửa sổ không phản hồi.
Đây là nguyên nhân quan sát được của lần treo này; không quy thành lỗi mạng.

Thư viện lúc chẩn đoán có bảy bài, gồm bốn bài trong thùng rác. Một lần duyệt
trạng thái giọng của cả bảy bài bằng mã cũ mất khoảng 0,57 s trên máy này.
Con số đơn lẻ chịu ảnh hưởng cache của Windows; không dùng làm benchmark
thời gian chuyển đổi bài giảng hoặc kết luận tốc độ dịch vụ AI.

## Sửa đổi

- Tiến độ dùng `browserStateChanged` và `statusChanged`; không phát lại tín
  hiệu cập nhật toàn bộ bài học cho mỗi thông báo loading. Đồng hồ giữ tín
  hiệu riêng như trước.
- QML lấy danh sách/thùng rác từ snapshot trong bộ nhớ. Getter không quét
  WAV, đọc nội dung bài hoặc truy vấn lại danh sách từ SQLite.
- Worker công bố metadata trước, sau đó kiểm tra giọng cho bài đang dùng.
  Không quét WAV của bài trong thùng rác. Trong lúc chưa kiểm tra, nhãn giọng
  không khẳng định đã sẵn sàng.
- Worker có kết nối SQLite riêng **chỉ đọc**, tránh migration/ghi phiên bản
  dữ liệu làm cache tự mất hiệu lực. Thay đổi bài, nhập từ worker, sắp xếp,
  metadata giọng và chuyển thư viện đều cập nhật snapshot đúng phiên.
- Chỉ chạy một lượt quét và gộp các yêu cầu làm mới đến trong lúc đang chạy.
  Kết quả cũ bị bỏ nếu có chỉnh sửa mới; đóng/chuyển thư viện hủy worker.
- Mỗi khóa WAV chỉ kiểm tra một lần trong mỗi phép tính trạng thái. Giữ kiểm
  tra định dạng, kích thước/mtime và nội dung WAV; bỏ bước resolve đường dẫn
  lặp lại trên từng khóa hex đã kiểm tra. Kiểm tra hỗ trợ hủy giữa các khóa.

Theo yêu cầu người dùng, đã dừng lượt chuyển đổi bị treo và đặt dấu dừng để
không tự tiếp tục khi mở ứng dụng. Giữ các bài đã lưu và profile tài khoản;
không gửi lại yêu cầu ChatGPT để kiểm tra lỗi giao diện.

## Kiểm chứng

- 39 kiểm thử liên quan qua: snapshot chỉ đọc, cache, sửa/khôi phục/chuyển
  thư viện, metadata giọng, hủy, WAV hỏng/thiếu và các hồi quy nhập bài.
- Qt Settings tám kiểm tra qua ở cả cửa sổ lớn và nhỏ, không warning.
- Qt thật với 12 bài (tám bài hoạt động, bốn bài trong thùng rác): cố tình
  giữ bước kiểm tra âm thanh ở nền, gửi 200 thông báo tiến độ. Cả 200 thông
  báo được xử lý, **không** có lượt làm mới toàn màn hình do tiến độ, không
  kiểm tra WAV trên luồng Qt. Khoảng ngắt nhịp giao diện lớn nhất khoảng
  **0,047 s**; nút Dừng nhận và đặt cờ hủy trong khoảng **0,359 s**.
- Test vẫn kiểm tra nhãn giọng sau tạo VI/EN/cả hai, chỉ đợi snapshot bất
  đồng bộ bằng khoảng chờ có giới hạn; không bỏ assertion về nội dung nhãn.

Các phép thử phản hồi dùng tiến độ/tác vụ âm thanh mô phỏng và dữ liệu riêng.
Chúng xác nhận sửa nghẽn giao diện, không phải chứng nhận mọi bản dịch, mọi
slide hoặc browser của mọi tài khoản. RC37 chưa thay bản RC34 trên kênh cập
nhật tự động. Mã nguồn vào Git; stack chẩn đoán, dữ liệu giáo viên, báo cáo,
model và EXE ở ngoài Git.
