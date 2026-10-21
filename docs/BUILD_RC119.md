# RC119 — Mở PowerPoint có gắn Mascot và chọn vị trí loa tức thời

## Thay đổi

- Nút Mở PowerPoint ở màn Chuyển đổi mở đúng tệp đã chọn, gắn với Mascot
  và giữ nguyên màn cấu hình. Mở file từ Mascot vẫn chuyển về Bài giảng.
  Các đường mở PowerPoint cũ cũng dùng phiên được quản lý, bản sao riêng
  và trạng thái sẵn sàng; bấm Trình chiếu/F5 mới bắt đầu chiếu.
- Phân biệt bản nguồn và bản đã chuyển đổi khi mở lại cùng bài. Bản nguồn
  không mượn lời đọc/giọng của sản phẩm chuyển đổi. Chỉ đóng đúng phiên
  cũ khi bài mới đã chuẩn bị thành công; hủy chọn file không đổi phiên.
- Đổi vị trí loa cập nhật minh họa ngay và lưu bằng hàng đợi nền riêng,
  không bật busy toàn ứng dụng, tải lại bài, tạo lại WAV hay render ảnh.
  Các lần chọn liên tiếp được gộp; chỉ cập nhật trường vị trí trong JSON,
  không ghi đè sửa đổi nội dung diễn ra trong lúc chờ lưu.
- Sáu vị trí xếp theo lưới ba cột, hai hàng: trái/giữa/phải trên và dưới.
  Minh họa, thông tin bài, vị trí loa trong PowerPoint xuất ra dùng cùng
  quy ước. Lựa chọn cũ Phải dưới vẫn giữ nguyên.
- Ô tên bài tự hiển thị từ đầu khi nạp file hoặc rời ô nhập; sửa chữ khi
  đang nhập vẫn bình thường. Tên dài có tooltip và không mất dữ liệu.
- Nội dung hai ô tổng hợp cấu hình được căn giữa từng hàng, tiêu đề giữ
  bên trái. Nút Hủy chuyển đổi nằm phải; kết quả mới có nút màu cam.
- Cảnh báo thiếu lời xuất hiện cả khi chỉ chọn một ngôn ngữ. Vẫn khóa
  lựa chọn không có lời trên toàn bài; một số slide thiếu không khóa
  những slide có lời còn lại.
- Tiếng Anh 100% dịch cả chữ trong hộp nằm ngoài slide: PowerPoint có
  thể vẽ phần chữ tràn vào khung dù tọa độ hộp ở ngoài. Giữ tọa độ nguồn.
  Cảnh báo ảnh tính cả những slide OCR có chữ, liệt kê slide nguồn và nói
  rõ phần đã tự xử lý/phần còn cần đối chiếu. Không coi công thức hoặc
  vùng OCR chưa chắc chắn là đã dịch hoàn tất. Bài cũ không bị sửa ngầm;
  cần chuyển đổi lại từ nguồn để nhận thay đổi này.
- Bao gồm các chỉnh giao diện sau RC118: bỏ tên file lặp, nút ⋯ cạnh
  Xem trước slide, thông tin phiên bản trên bản quyền và số liên hệ tác giả.

## Kiểm tra nguồn

155 kiểm thử liên quan đạt trong môi trường .venv: phiên dạy/đổi bài,
nguồn và preview, giọng, vị trí loa/lưu nền, chuyển đổi/OCR và xuất audio.
Qt thật đã kiểm giao diện sáng/tối, bố cục 1080/1366/1920, cỡ chữ 150%,
click menu sáu vị trí, loa Anh/Việt/cả hai, giữ ảnh preview và không busy.
48 trường hợp bố cục chuyển đổi đạt, không có cảnh báo QML.

Qt với PowerPoint thật kiểm mở/chiếu/kết thúc/đổi/hủy, các nút mở từ
thư viện/Mascot/công cụ, giữ cấu hình khi mở tệp đầu vào và byte nguồn.
Một bản sao riêng của slide nguồn thực tế cũng đã được dựng bằng Office
để kiểm phần tiêu đề tiếng Việt nằm ngoài khung không còn xuất hiện sau
khi xử lý; không sửa bài/thư viện cá nhân hoặc gọi API dịch khi kiểm.

Chưa coi các phép thử trên là chứng nhận máy chiếu/nhiều màn hình hoặc
xác nhận dịch hết mọi chữ/công thức nằm trong ảnh.

## Gói

Dựng một lần từ commit đã kiểm tra, dùng runtime/model RC118 có manifest
SHA256. Commit, phiên bản và baseline ghi trong BUILD_INFO.json của gói.
Dữ liệu thư viện, audio, khóa, model tải riêng và executable không đưa
vào commit nguồn.

Gói đã dựng từ `be06b943ceaa860974e36a564f12be6be8942bc2`, phiên bản
`1.0.0rc119`. ZIP có 1.249.986.372 byte, SHA256
`e007af5e2ab74e8860e43eca22aaddfea3ac844c6b31b02eccb28421a5a620c9`.
4662 tệp ứng dụng và 54 tệp QML/qmldir đã được đối chiếu với manifest/commit.
Gói đã chạy kiểm tra Qt riêng, cài vào `F:/Applications/BiliClass/1.0.0rc119`
và mở qua Explorer. Cửa sổ chính/Mascot phản hồi; icon, taskbar và shortcut
đúng phiên bản. So sánh trước/sau cài xác nhận nguồn, nội dung thư viện,
1066 WAV được tham chiếu, logo, khóa mã hóa và tùy chọn giọng giữ nguyên.
Gói RC119 được dùng để test tại máy, chưa phát hành GitHub Release.
