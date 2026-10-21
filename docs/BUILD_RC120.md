# RC120 — Mở lại bài nhanh hơn và hoàn thiện cấu hình giọng/Mascot

## Hành vi

- Sau khi tạo giọng thành công, nút cam **Mở bài vừa tạo giọng** ở chân
  công cụ mở đúng bài và đúng bản giọng vừa hoàn tất. Nút vẫn dùng được
  sau khi đổi cấu hình, đổi tab hoặc bỏ chọn bài. Tác vụ bị hủy không ghi
  đè kết quả thành công trước đó. Bản giọng bị xóa/thiếu WAV được báo lỗi,
  không chuyển sang màn kết quả sai và không tạo giọng lại khi mở.
- Các nhóm nút Mở PowerPoint/Tải PowerPoint/Tải audio và nhóm trong ô
  hoàn tất được căn giữa. Tổng hợp cấu hình của màn tạo giọng vẫn nằm
  ở chân trang sau khi trở về cấu hình từ kết quả.
- Trạng thái thư viện dùng màu xanh lá khi có giọng, vàng khi chưa đủ,
  xám khi chưa có và xanh lam khi đang kiểm tra. Cả danh sách/thẻ dùng
  chung trạng thái và màu. Ngày tạo luôn nằm phải ở chế độ thẻ.
- Luồng thông thường không hiện nhắc kiểm tra bố cục/xác nhận thủ công
  chung chung. Hoàn thiện tự động khi chuyển đổi/mở/tải vẫn chạy; menu
  sửa nội dung vẫn có. Dấu phiên bản/hash ngăn lặp lại toàn bộ lần sửa
  đã thực hiện khi mở trang chi tiết. Các phát hiện chưa giải quyết vẫn
  được giữ trong dữ liệu, không bị đổi thành PASS hay tự phê duyệt.
- Cài đặt **Cấu hình cho Mascot** bỏ lựa chọn Giảm chuyển động và luôn
  dùng chuyển động bình thường, kể cả nếu cài đặt cũ từng bật giảm.
  **Hiện phụ kiện theo môn** vừa bật phụ kiện vừa hiện danh sách môn;
  tắt sẽ ẩn/khóa danh sách và tắt phụ kiện. Môn đã chọn được giữ để dùng
  lại khi bật. Bố cục ba phần trên màn rộng, xếp dọc trên màn hẹp.
  Giữ nguyên các tab Cài đặt.
- Sửa điều kiện tooltip tên bài dài dùng chiều rộng thực của TextField;
  tên vẫn hiển thị từ đầu và không làm mất vị trí con trỏ khi đang nhập.

## Chuẩn bị mở bài

PPTX có giọng đã được xác minh được lưu tạm để mở lại. Mỗi phiên Office
vẫn nhận một bản sao riêng; đóng/xóa bản sao phiên không ảnh hưởng nguồn
hoặc bộ nhớ đệm. Khóa gồm phiên bản ứng dụng, bài/revision, SHA nguồn,
bản giọng, vị trí loa và kích thước/thời gian sửa của từng WAV. Trước mỗi
lần dùng vẫn kiểm tra giọng còn hợp lệ và SHA256 của PPTX lưu tạm.
Đổi nguồn/giọng/vị trí/WAV hoặc làm hỏng PPTX sẽ không dùng lại bản cũ.
Không tải model hay tổng hợp giọng khi mở. Lỗi ghi bộ nhớ đệm không chặn
phiên hiện tại đã chuẩn bị thành công. Ảnh/video vốn đã nén không bị nén
ZIP lần nữa; XML và WAV vẫn nén. Nội dung resource nguồn giữ nguyên byte.

Đo trên bản sao riêng của bài thực tế 79 slide/214 đoạn, cùng máy và
cProfile: RC119 mất 17,656 giây; RC120 lần đầu 10,593 giây, lần mở lại
1,328 giây và chỉ nhúng audio một lần trong hai lần mở. Đây là thời gian
chuẩn bị, không bao gồm khởi động/giao diện PowerPoint. Không coi số đo
một bài là cam kết cho mọi tài liệu. Dữ liệu đo không đưa vào Git.

## Xác minh

- 147 kiểm thử pytest liên quan đạt bằng `.venv`: phiên dạy/đổi bài,
  giọng, vị trí/lưu nền, hoàn thiện, xuất âm thanh, cache và mở lại kết quả.
  Có kiểm cache hỏng, WAV thiếu, thay đổi vị trí, giữ sửa lời đọc,
  hủy tác vụ và chống lặp sửa bố cục đã có dấu phiên bản.
- Qt thật kiểm màn kết quả giọng, nút mở lại chính xác sau thay cấu hình
  hoặc bỏ chọn, căn giữa các nhóm nút, Cài đặt sáng/tối và phụ kiện ẩn/hiện.
  Theme đã kiểm ở 100% và 150%, menu sáu vị trí loa và tổng hợp cấu hình.
  Mascot đã kiểm các cỡ, kéo/thu bảng, click điều khiển, cuộn âm lượng
  và lưu tùy chọn khi SQLite bận; không chỉnh âm lượng thật của máy.
- Qt thư viện dùng PowerPoint thật dựng bìa, kiểm list/thẻ, chọn bài/menu,
  ngày căn phải ở 1080/1366/1920, mở bài giữ tab Bài giảng và nút riêng
  tạo giọng chỉ mở cấu hình. Không có cảnh báo QML.
- Kiểm với bản sao bài thực tế: PowerPoint dựng slide 1 và 57 từ PPTX
  dùng cache thành công, 355 ảnh dùng ZIP_STORED, nguồn và WAV giữ nguyên.
  Không mở/đóng bài cá nhân đang trình chiếu và không gọi API dịch/TTS.

Kiểm tra tại máy không chứng nhận máy chiếu/nhiều màn hình hoặc khẳng
định đã dịch đủ công thức/chữ không rõ nằm trong ảnh. RC119 đã sửa chữ
ngoài khung; bài chuyển đổi cũ cần chạy lại từ nguồn để nhận thay đổi đó.

## Gói

Phiên bản nguồn `1.0.0rc120`. Dựng một lần sau khi commit nguồn đã kiểm,
dùng runtime/model RC119 với manifest SHA256. Commit được ghi trong
BUILD_INFO.json; dữ liệu, audio, khóa, model tải và executable không
đưa vào commit.

Gói đã dựng từ `ce70f40c53d65ac2098ac2a51496a1dccc8fbd55`, ZIP
1.249.991.815 byte, SHA256
`cc967cdaab1438cd54a831a1f66e76a703e2a20f53091f8ea3655291363309a7`.
4662 tệp ứng dụng và 54 QML/qmldir đã đối chiếu manifest/commit;
PYZ có module cache mới. EXE thực chạy smoke Voice 1366×850, không có
cảnh báo QML. Cài vào `F:/Applications/BiliClass/1.0.0rc120` và mở qua
Explorer; cửa sổ chính/Mascot phản hồi, shortcut/taskbar/icon đúng bản.
RC119 đã đóng bình thường, không đóng PowerPoint hoặc phiên khác.
So sánh trước/sau cài xác nhận nội dung/nguồn bài, 1066 WAV được tham
chiếu, logo, khóa mã hóa và tùy chọn giọng không thay đổi. Gói phục vụ
test tại máy, chưa phát hành GitHub Release.
