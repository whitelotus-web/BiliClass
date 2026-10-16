# Bản giọng, thư viện và mascot — RC49

Ngày 16/10/2026. Dòng tiêu đề chung đổi thành **Trợ lý dạy học song ngữ** theo
lựa chọn của người dùng. Giữ các tab Cài đặt và thư viện cá nhân hiện có.

## Bản giọng của từng bài

Một bài có thể giữ nhiều bản giọng, phân biệt theo nội dung, ngôn ngữ, giọng,
tốc độ và kiểu nút loa. Tạo bản mới không thay mất metadata của các bản cũ;
không tạo bản sao cả bài giảng. Bản đã tạo ở phiên bản trước vẫn được nhận diện.

Ở màn bài giảng:

1. Chọn một trong sáu giọng và nghe thử mẫu đóng sẵn ngay tại đây; chọn tốc độ
   nếu cần. Việc này không đổi giọng mặc định trong Cài đặt.
2. Chọn tiếng Anh, tiếng Việt hoặc Việt + Anh rồi Tạo / tiếp tục giọng.
   WAV hợp lệ được dùng lại. Bản Việt–Anh không phải tổng hợp thêm lần thứ ba
   để có giọng đọc chung.
3. Chọn **Bản dùng để dạy / tải PowerPoint**. Tên bản có ngôn ngữ, giọng và
   tốc độ, kèm trạng thái đã đủ hay cần tạo tiếp. Có lựa chọn Không kèm giọng.
4. Tải PowerPoint với bản giọng đã chọn hoặc Dùng để dạy. Bản chưa đủ âm thanh
   không được âm thầm thay bằng giọng mặc định hoặc coi là bản hoàn tất.

Bản Việt–Anh mới nhúng ba nút trên cùng slide: **EN**, **VI**, **VI+EN**.
Nút chung ghép các WAV đã có: Việt rồi Anh theo từng cặp nội dung xác định
được, sau đó giữ phần nội dung hiện rõ còn lại. PowerPoint tải về phát âm thanh
nhúng mà không cần BiliClass. Tên file gợi ý chứa loại giọng để dễ phân biệt.
Các bản Việt + Anh cũ giữ hai loa và được ghi rõ; chọn tạo bản Việt–Anh mới
để có ba nút, dùng lại cache của cùng giọng/tốc độ.

Việc nhúng chỉ dùng nội dung đã xác minh đang hiện trên slide. Không đưa lời
đọc của đáp án ẩn vào nút phát cả slide. Trang có hiệu ứng chưa xác định hoặc
không có vùng đặt loa trống vẫn có thể cần dùng trình chiếu trong BiliClass /
tải bản không giọng; không khẳng định mọi trang đều nhúng được cả ba loa.
Giọng Việt chỉ được giữ trên trang có timing khi đối chiếu được chữ Việt
đang hiện tĩnh, ngoài các đối tượng bị timing tác động.

## Thư viện và Trang chủ

- Thư viện có tìm kiếm không dấu, lọc môn, khối/cấp học, trạng thái và bản
  giọng Anh/Việt/Việt–Anh, chưa tạo hoặc chưa hoàn tất. Bộ lọc kết hợp được;
  có số kết quả và trạng thái không tìm thấy.
- Sắp xếp theo ngày tạo mới/cũ, cập nhật hoặc tên A–Z. Danh sách hiển thị
  tối đa 20 bài mỗi trang. Việc tìm/lọc chỉ dùng catalog trong bộ nhớ, không
  quét WAV trên luồng Qt khi gõ. Kiểm tra audio vẫn ở worker của catalog.
- Trang chủ hiển thị việc đang xử lý, số bài thực tế và tối đa ba bài vừa cập
  nhật. Có lối vào thư viện/lớp học; không lặp lại bộ lọc và danh sách đầy đủ.
- Không xóa/gộp/đổi tên tự động các bài demo của người dùng.

## Mascot

Phụ kiện có hai chế độ: Tự theo bài đang dạy / Dùng môn đã chọn. Đổi môn trong
dropdown tự chọn chế độ cố định; bấm Lưu cập nhật ngay mascot nổi và các màn
hiển thị. Có thể trở lại chế độ tự động, không đổi môn của bài giảng.

Mascot có nút Mở bài để dạy, đưa giáo viên về màn bài để chọn Dùng để dạy.
Các nút đọc Việt/Anh/chung và đọc lại chỉ bật trong phiên PowerPoint đang mở
đúng bài. Backend kiểm tra lại điều kiện khi bấm; đóng/đổi slide hoặc đổi bài
dừng hàng đợi hiện tại. Nghe thử ở Cài đặt/màn tạo giọng vẫn là thao tác riêng.

## Kiểm chứng

- 131 kiểm thử liên quan qua: thư viện/catalog/tìm lọc, các bản giọng và cache,
  xuất audio, PowerPoint, gói bài, điều khiển giọng, lời đọc và lớp học.
- Qt result: cả 1080×700 / 1366×850, sáu mẫu nghe thử, không đổi mặc định,
  chọn bản Việt dùng đúng giọng, giữ đồng hồ và bố cục RC48; lưu môn cố định
  đổi mascot nổi, nút đọc bị khóa khi chưa trình chiếu; không QML warning.
- Qt thư viện: tìm không dấu, kết hợp bộ lọc, xóa lọc, Trang chủ khác thư viện;
  sửa/xóa/khôi phục/mở bài/tải đúng file và Office preview; không QML warning.
- Qt giọng Cài đặt: sáu mẫu, lưu trong lúc nghe, hủy không phát muộn và theme
  môn học; không nạp model hoặc gọi Google trong fixture.
- PowerPoint thật mở file thử và nhận ba audio media với click action 12;
  độ dài hai loa riêng 280 ms và loa chung 560 ms. Đã render để đối chiếu
  vị trí/nhãn. Âm thanh kiểm tra là WAV ngắn có kiểm soát, không phải chứng nhận
  chất lượng đọc hoặc hiệu ứng cho toàn bộ bài thật.

Bằng chứng riêng: `reports/rc49` và `reports/lesson-management`. Báo cáo, bài
cá nhân, WAV, API key, model và EXE không đưa vào Git.

[Bản EXE RC49 và kiểm tra mở độc lập](BUILD_RC49.md). Bài hiện tại đã được
đăng ký bản Anh / Việt / Việt–Anh từ đủ 354 đoạn cache sẵn có, không tổng hợp
lại; không thay nội dung hay duyệt lại bài tự động.
