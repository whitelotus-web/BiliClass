# RC152 — Tab hồ sơ và vị trí file bài giảng

Tab đang chọn trong Thư viện dùng cùng nền xanh với nút Mở PowerPoint,
chữ/icon trắng; các tab cao 40 px, chữ 13 px, icon 22 px, vát phải,
chồng nhẹ 10 px và có bóng mỏng. Tab đang chọn nằm trên các tab kề.
Tất cả dùng hình hồ sơ có tài liệu do người dùng cung cấp.

Chưa có giọng dùng loa gạch chéo dạng đặc ở tab và bài trong cả
chế độ danh sách/thẻ. Mẫu loa có sóng dạng đặc chỉ thay ở tab Đã có
giọng. Giữ nguyên các loa Việt/Anh màu xanh trên bài có giọng và
loa nhúng PowerPoint. Các mẫu được chuyển sang SVG nền trong suốt,
nhận màu theo sáng/tối/trạng thái chọn; ảnh tham chiếu gốc không sửa.

Nút tùy chọn góc phải dùng ba chấm tròn lớn hơn. Menu ba chấm của
mỗi bài thêm Mở trong Explorer: chọn file PowerPoint đã lưu tương
ứng với bản giọng đang chọn, hoặc file nguồn do thư viện quản lý
nếu bản xuất không còn. Không tạo lại file, tổng hợp giọng, mở
PowerPoint hay đổi nội dung/thứ tự/chọn bài. Có thông báo rõ nếu
không còn file. Windows Shell nhận đường dẫn Unicode trực tiếp,
kể cả dấu phẩy; nếu Shell không chọn được thì thử mở thư mục cha.

Kiểm chứng nguồn:

- 17 pytest cho vị trí file, bản xuất hoàn tất và thao tác thư viện.
- Qt smoke trên thư viện riêng: sáng/tối, ba tab, chọn/lọc bài,
  vùng bấm/trạng thái loa ở danh sách và thẻ; menu Explorer ở cả
  hai chế độ, không đổi lựa chọn; nút Tạo giọng đã chọn đúng hàng.
- Windows Explorer thật chọn đúng file thử có dấu Việt, dấu phẩy
  và ký tự #. Không dùng bài giảng của giáo viên để thử.
- Ruff, compileall; Qt không có cảnh báo QML. Các luồng chuyển đổi,
  tổng hợp giọng và điều khiển PowerPoint không thay trong mốc này.

Đã phát hành từ `b695a72c3f8bb159e89130e06100222c7830c522`;
[Source checks](https://github.com/whitelotus-web/BiliClass/actions/runs/39798542458) đạt cho đúng commit gói.
[Gói RC152](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc152): 1,258,154,981 byte, SHA-256
`35d60f615aab63315f4dcd3dd9a52ea7f20cb4d10ee28e34ab1941c41d462801`. 60 tệp QML/qmldir và bytecode
khớp nguồn; ZIP/digest/tag và updater công khai đạt. Cài/mở Trang chủ
từ Explorer, Mascot mặc định ẩn; hồ sơ/key, bài và
1752 WAV tham chiếu giữ nguyên.
