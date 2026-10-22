# RC155 — Bố cục đầu vào thống nhất, hướng dẫn phím và chuột

Chuyển đổi và Tạo giọng dùng chung lề trang, cỡ tiêu đề, khoảng cách,
vị trí thông tin bài/trạng thái, Mở PowerPoint, xem trước và cấu hình.
Kiểm tra cả khi chưa tải file, một bài và nhiều bài; giữ các thông tin
riêng của từng công cụ. Khung tải lên, hình minh họa và nút chọn file
cùng kích thước/vị trí. Bộ chọn thư viện vẫn ở màn Tạo giọng.

Đầu vào nhiều bài bỏ tiêu đề “Hàng đợi · … bài”; lời nhắc chọn bài
để xem trước/dùng cấu hình chung nằm dưới danh sách. Chọn bài, mở/bỏ
từng file, cuộn, xem trước và chuyển slide vẫn dùng luồng hiện có.
Thanh tiến độ của lượt đang xử lý vẫn có số bài để theo dõi.

Khi Mascot đang gắn bài và trình chiếu, lăn lên/lăn xuống ngoài vùng
âm lượng trong bảng trợ giảng gọi Trước/Sau theo hiệu ứng rồi slide.
Lăn ở cả hàng Âm lượng (chữ, thanh kéo, phần trăm) tăng/giảm 5% mỗi
nấc, không đổi slide; cử chỉ nhỏ được tích lũy. Khi đang chọn bài hoặc
chưa trình chiếu, bảng vẫn cuộn bình thường. Giữ nguyên cơ chế lăn
chuột sẵn có của PowerPoint trên vùng trình chiếu, không chặn thêm.

Bảng trợ giúp đổi thành “Hướng dẫn phím và chuột”, thêm hình chuột,
mũi tên và hai chỉ dẫn riêng cho chuyển hiệu ứng/slide và âm lượng.
Bảng nằm trong màn hình, tránh che bảng điều khiển; không làm bảng
trợ giảng nhảy kích thước khi rê chuột.

Kiểm chứng nguồn:

- 125 pytest liên quan đầu vào, hàng đợi, workspace tạo giọng,
  phím trình chiếu và PowerPoint đạt.
- Qt đo trực tiếp vị trí/kích thước chung của hai công cụ ở ba trạng
  thái, sáng/tối, 1080×700 và 1366×850. Ảnh trả về trễ không lấn bài
  đang chọn; mở/bỏ từng bài và hủy cả đầu vào giữ nguyên nguồn.
- Qt bố cục Chuyển đổi 1080–1920 px, template/môn riêng đạt; cấu hình,
  cuộn và thanh nút dưới cùng vẫn truy cập được.
- Qt hàng đợi xử lý lần lượt, dừng/tiếp tục/thử lại và tự ẩn sau khi
  hoàn tất đạt. Qt tạo giọng đã hoàn tất: mở lại đúng bài, ảnh xem
  trước, nghe/dừng và nút tải đạt ở 1080–1920 px, dùng WAV thử.
- Qt bảng trợ giảng kiểm tra wheel trên thanh/chữ/phần trăm và ngoài
  âm lượng, delta nhỏ/pixel, cuộn khi chọn bài, tooltip có hình chuột,
  vị trí ở mép màn hình và giữ trạng thái cài đặt. Âm lượng Windows
  được thay bằng backend thử, không đổi âm lượng của giáo viên.
- PowerPoint thật với bài thử hai slide/một hiệu ứng: lăn xuống hiện
  hiệu ứng, lên thu hiệu ứng, xuống tiếp sang slide sau, lên quay về
  hiệu ứng cuối slide trước. Chỉ gửi sự kiện vào cửa sổ bài thử.
- Ruff, compileall; không có cảnh báo QML trong smoke đầu vào/bảng trợ giảng.

Không thay bộ dịch, OCR, TTS, nguồn/file thư viện hoặc các tab Cài đặt.
Không đánh giá lại nội dung dịch/TTS trong chỉnh sửa giao diện này.

Đã phát hành từ `fe69c0e8fd5957d0f9e56b7b87bc20b5715db6ef`;
[Source checks](https://github.com/whitelotus-web/BiliClass/actions/runs/39816791521) đạt cho đúng commit gói.
[Gói RC155](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc155): 1,258,165,712 byte, SHA-256
`c52d2eef3f57ebf646e4b84ab32490639790705fc6689ebf54aa902537f37207`. 62 tệp QML/qmldir và bytecode
khớp nguồn; ZIP/digest/tag và updater công khai đạt. Cài/mở Trang chủ
từ Explorer, Mascot mặc định ẩn; hồ sơ/key, bài và
1752 WAV tham chiếu giữ nguyên.
