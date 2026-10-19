# RC90 — Mascot gọn hơn và điều khiển đồng bộ

Bao gồm toàn bộ thay đổi [RC89](BUILD_RC89.md) và [RC88](BUILD_RC88.md).

Bảng trợ giảng dùng ba cỡ rộng 320/356/400 px; nút cao 34/38/44 px và chữ
12/13/14 px. Giảm khoảng trống, giữ vùng bấm đầy đủ. Nút Kết thúc có chữ,
viền và nền đỏ nhạt; Trình chiếu dùng icon màn hình trắng trên nền xanh.
Mũi tên xuống thu bảng về Mascot; nhấp đúp bảng không còn thu bảng.

Cách đọc mặc định là Tự động theo slide: slide tĩnh đọc toàn bộ, slide có
hiệu ứng đọc các phần xác định đã hiện. Hai lựa chọn thủ công nằm trong
menu ⋯ cạnh âm lượng. Sau thời gian hiệu ứng hoàn tất, một timer đơn lẻ
cập nhật các nút đọc. Nhận diện thêm hiệu ứng cùng lần bấm với hiệu ứng
chính; không suy đoán chữ đang hiện với trigger/chuỗi chưa giải được.
Nút Trước/Sau và phím điều hướng lùi/tiến hiệu ứng trước khi đổi slide.

Phím tiến/lùi và tăng/giảm âm lượng đổi được ngay trên bốn nút bố trí
mũi tên trong Cài đặt → Mascot. Lưu áp dụng cho phiên đang mở; hướng dẫn
ở dấu ? cập nhật từ cùng dữ liệu đã lưu. Giữ cấu hình ba phím đọc của bản
cũ khi nâng cấp, thêm bốn phím mặc định; kiểm tra trùng phím. F5 và Esc
vẫn dành cho PowerPoint, phím ở ứng dụng khác không bị chặn.

Bản mở cùng Mascot dùng một bộ điều khiển cho loa trên slide và bảng:
không để animation của nút loa chạy song song với trạng thái COM. Giọng
đã lưu theo phần đang hiện cũng đồng bộ icon phát/tạm dừng trên slide.
Poster media trong suốt 1 pt nằm dưới nút, không còn icon thừa ngoài rìa.
Bản tải độc lập giữ các lệnh tương tác native của PowerPoint. Lệnh dừng
cũ không được xóa yêu cầu đọc mới đang chờ; handler Office tách tên khỏi
QObject.event để timer con không đi vào handler dữ liệu Office.

Môn chuyển đổi lần đầu theo môn giảng dạy trong Chung, sau đó lưu riêng
môn chọn gần nhất, gồm tên môn riêng. Phụ kiện mặc định theo Chung; khi
người dùng đổi môn phụ kiện và lưu thì giữ lựa chọn riêng. Không sửa lại
môn của bài cũ. Kiểm tra luồng Qt từ chọn tệp, kiểu chuyển ngữ, thiết kế,
nút chuyển đổi đến cấu hình tác vụ và dữ liệu bài, rồi đóng/mở lại.

Bỏ thông báo số slide cần xem lại bố cục ở Mascot, hoàn tất chuyển đổi,
giọng và màn xem. Giữ xử lý tự căn chỉnh, render và kiểm tra nội bộ trước
khi chọn bản sửa. Không xóa các kiểm tra kỹ thuật hoặc tự xác nhận bản
dịch. Việc tự cân đối được kiểm chứng trên bộ thử cụ thể, không phải bảo
đảm thẩm mỹ hoặc nội dung đúng cho mọi tệp PowerPoint/trigger/công thức.

Thanh dưới hiện “BiliClass sẵn sàng” khi rảnh; chỉ hiện vòng xoay và tiến
độ khi có tác vụ thật. Tạo giọng khi sang tab khác vẫn có nút dừng. Lỗi
thao tác thật nằm ở thông báo riêng có nút đóng, không phủ nút hủy trong
khi tác vụ đang chạy.

## Kiểm tra nguồn và runtime

- Ruff: đạt trên app và các script/test thay đổi.
- Kiểm thử lõi loại trừ sáu nhóm browser cũ không liên quan: 904 test đạt, cộng 89 test luồng/race/Office sau thay đổi cuối.
- Qt: Trang chủ ba cỡ, màn xem ba cỡ, cấu hình/chuyển đổi bốn cỡ, tạo
  giọng/dừng/tiếp tục/hủy bài, ba cỡ Mascot, thu bằng nút xuống và menu
  cách đọc, đổi phím WASD và tooltip, lưu môn độc lập qua mở lại.
- PowerPoint thật: click loa từ cửa sổ fixture khác, phát/tạm dừng/đổi
  ngôn ngữ, cached WAV không chồng native player, icon giữ được, F5,
  Trước/Sau theo bước, 12 lần kéo bảng. Lần đo fixture: trung bình 24 ms,
  cao nhất 32 ms cho 16 lần đổi slide (gồm A/D tùy chọn); khoảng cách UI tick lớn nhất 63 ms.
  Đây là phép đo trên fixture im lặng ở máy kiểm tra, không phải cam kết
  thời gian với mọi tài liệu hoặc máy chiếu.
- Export native: Office nhận đủ chuỗi tương tác [6, 0, 2], giữ lệnh qua
  roundtrip; media trong suốt phát/tạm dừng/tiếp tục, không tự phát.

Gói RC89 từ `35a99fc` đã build cục bộ đúng manifest/hash ZIP làm baseline.
Chỉ công bố/cài RC90 sau kiểm gói độc lập, model thật và luồng Qt từ hoàn
tất bài sang tạo giọng. Dữ liệu giáo viên, khóa, báo cáo/ảnh thử, WAV,
model và executable ở ngoài Git.

## Gói phát hành đã kiểm chứng

- Nguồn build: `0a3645696cebb5fdd6ad00ad0c438eb636f36b70`.
- CI [Source checks](https://github.com/whitelotus-web/BiliClass/actions/runs/39235831288): success.
- 4.215 file ứng dụng; ZIP 871.266.004 byte, đã đọc lại từng entry và
  đối chiếu manifest. SHA-256:
  `e51045b3ecf8773ba61e2f3e87f06104c064331fbe5bff252a102e3a04d84aee`.
- Cài/gỡ trong đường dẫn Unicode tách biệt: đạt; Windows Properties,
  hai màn Qt, template, bộ giọng VieNeu Việt/Anh, lớp học và backup đạt.
- Qt từ hoàn tất bài sang tạo giọng thật: đủ 2/2 đoạn Việt–Anh, 9,66 giây,
  469 nhịp giao diện, khoảng cách lớn nhất 94 ms, không cảnh báo QML,
  bộ ghi kẹt giao diện bật và nguồn giữ nguyên.
- [Phát hành RC90](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc90): ZIP và checksum đã tải lên, digest GitHub khớp.
- Đã cài tại `F:/Applications/BiliClass/1.0.0rc90` và mở qua Explorer,
  parent `explorer.exe`; main và Mascot đều hiện và trả WM_NULL trong 1 giây.
  RC86 đóng bằng WM_CLOSE thông thường, không cưỡng bức. Kiểm tra sau mở
  xác nhận khóa API, môn đã lưu và nguồn bài đang kiểm tra được giữ nguyên.
