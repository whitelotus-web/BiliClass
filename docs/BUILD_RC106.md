# RC106 — Giọng đọc, loa PowerPoint và xem trước

Sau khi tạo giọng xong, trang Tạo giọng đọc tự hiện ảnh slide. Chuyển slide
và nghe Anh/Việt nằm cùng một hàng; bỏ nút Kiểm tra slide và giọng cùng
thanh nút Đã có giọng đọc ở cuối. Khối hoàn tất giữ Mở PowerPoint, tải PPTX,
tải audio và xem trong thư viện. Tải file và xem trước vẫn dùng được khi
PowerPoint đang mở. Lỗi xem trước có thông báo và nút tải lại.

Bảng Mascot dùng bốn PNG do người dùng cung cấp: thu gọn, trợ giúp bàn
phím, cài đặt và ẩn. Menu chuột phải dùng cùng icon cài đặt/ẩn. QML chỉ
chọn vùng hiển thị để bỏ khoảng trong suốt; PNG gốc giữ nguyên byte.
Loa VI/EN và nút tạm dừng trên slide dùng bốn PNG người dùng cung cấp,
cắt vùng hiển thị bằng thuộc tính ảnh gốc của PowerPoint. Dùng ô vuông
36 pt để chữ VI/EN đọc được và không kéo méo ảnh; vị trí đồng nhất giữa
các slide. Không cần tạo lại WAV khi đổi biểu tượng.

Ảnh xem trước dựng trên bản sao riêng, chỉ đóng bản sao đó. Không mở rồi
đóng đường dẫn đang dùng trong trình chiếu của giáo viên.

## Nội dung và âm thanh

- Giữ số/dấu câu nằm ở run riêng trong đoạn tiếng Anh có bằng chứng ngôn
  ngữ; không đưa số/công thức tiếng Việt vào lời Anh chỉ vì có ký tự Latin.
- Đọc nhãn mục 1., I/, II. thành Section tương ứng; không sửa số thập phân,
  phân số hay đại từ I. Cache chỉ đổi cho những nhãn được chuẩn hóa.
- Dịch Bài 4 thành Lesson 4, Chương II thành Chapter II trước API/cache.
  Bài hát không bị áp dụng quy tắc này. Có bộ thuật ngữ cơ bản theo môn,
  chuẩn hóa tên môn có dấu/biến thể; thuật ngữ giáo viên khóa được ưu tiên.
  Từ ngắn nhiều nghĩa của bộ mặc định chỉ thay khi là toàn cụm.
- Giữ ngắt đoạn thay vì gộp toàn slide thành một câu; thêm 450 ms nghỉ giữa
  các đoạn trong hàng đợi phát và trong WAV nhúng/xuất. Cache WAV cũ vẫn
  còn; đoạn có cách chia mới cần tạo tiếp trước khi dùng bản có giọng mới.
- Tự động chỉ chọn phần chưa đọc xong, không phát lại toàn bộ phần đang
  hiện khi không có nội dung mới. Đọc phần đang hiện/Toàn slide vẫn đọc lại
  theo lựa chọn rõ ràng của giáo viên. Đoạn Việt được ghép theo đoạn Anh khi
  có đối chiếu đủ; không coi mọi lời ghi chú là đang hiện theo hiệu ứng.
- Chỉ bỏ tiêu đề lặp khi nhận diện rõ là tiêu đề, đã đọc ở slide ngay trước
  và đang đi tiếp từng slide. Đi lùi/nhảy trang hoặc đọc toàn slide không bỏ.
  Không đoán tiêu đề từ nội dung thân bài hay cam kết hiểu mọi hiệu ứng.

## Loa và tốc độ

Office có thể đổi vị trí đối tượng khi xử lý AlternateContent/công thức.
Tìm loa/nút bằng tên ổn định và kiểm tra ID media, rồi mới dự phòng vị trí.
Đã kiểm tra bản sao bài thực: bốn vị trí khác XML; cách mới tìm đúng 60
player và 60 cặp biểu tượng, không cảnh báo. File mở qua Mascot cũng giữ
trigger âm thanh trực tiếp của PowerPoint; hook nhận cú bấm thì chặn sự
kiện trước khi Office xử lý, tránh hai đường phát cùng lúc.

Khởi tạo giọng Anh bỏ đọc/ghi và phân tích từ điển không được dùng trên
đường đọc đã chọn. Hai lượt đo nóng: trung bình 1,930 s xuống 1,399 s cho
bước khởi tạo, không phải toàn bộ thời gian tạo bài. 12 chuỗi token ngữ âm
mỗi lượt giống nhau trên ba giọng, gồm Lesson 4, số 12, mục 2 và số 3.5.
Âm thanh có dao động nhỏ giữa các lần suy luận, không so hash WAV để kết
luận phát âm. Không tải model mới hay gửi nội dung lên dịch vụ đọc ngoài.

Kiểm tra trước đóng gói: 138 kiểm thử luồng đọc/loa/xem trước và 288 kiểm
thử giọng/chuyển đổi qua; sau thay ảnh loa, 46 kiểm thử nhúng/điều khiển
và tiến độ đọc qua. Kiểm thử nhận số của bản dịch chấp nhận khoảng trắng
không ngắt giữa số và đơn vị, vẫn yêu cầu đủ giá trị và đơn vị.
Qt Windows với thư
viện tạm/Office thật qua ở 1080×700 và 1366×850, không cảnh báo QML. Xác
nhận tự hiện ảnh, xem khi PowerPoint đang mở không dừng tiếng, nghe/tải
không tràn hàng. Kiểm tra chuột vật lý trong phiên Mascot thực tế còn cần
người dùng thử; kiểm tra cấu trúc/COM không thay cho kết luận đó. Quét
thêm toàn bộ dự án dừng ở phần trình duyệt không thuộc thay đổi; không
ghi nhận quét đó là đã qua toàn bộ hệ thống.

Nguồn bài cá nhân, ảnh, WAV, kết quả đo và executable không nằm trong Git.
