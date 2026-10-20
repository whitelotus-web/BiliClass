# RC110 — Chỉ hiện bản giọng hoàn tất trong thông tin bài giảng

Mục Giọng đọc trên trang thông tin bài chỉ liệt kê bản đã kiểm tra và sẵn
sàng. Không hiện bản đang tạo, chưa đủ, cũ hoặc đang kiểm tra. Nếu chưa
có bản hoàn tất, hiện một dòng “Chưa có giọng đọc hoàn tất”.

Chỉ lọc phần hiển thị tại LessonInformation; giữ các bản đang làm để có
thể tạo tiếp trong trang Tạo giọng đọc. Không xóa bản ghi hay WAV.

Kiểm tra Qt: chỉ bản sẵn sàng được hiện, bỏ lựa chọn Không kèm giọng,
ẩn bản cũ/chưa đủ/đang kiểm tra, xử lý danh sách trống và giữ nhiều bản
hoàn tất khác nhau. Không có cảnh báo QML. Ba ca Final Narration đạt.

## Bản đã phát hành và mở trên máy

- Commit đóng gói: `cd325562a774ebe904d19194b457f2c1de362472`.
- ZIP: 1.249.943.922 byte; SHA256
  `28467e71154ca1d5d607aa0b75d6caca4660dd9fb1e295e9ee1454a8bd2cf98a`.
- Manifest/ZIP đã kiểm tra; QML trong gói khớp nguồn đã kiểm tra.
  Digest asset GitHub khớp checksum.
- RC110 cài riêng và mở qua Explorer vào trang thông tin bài; cửa sổ
  chính/Mascot hiện, shortcut và biểu tượng đúng. Sau khi tải bài, ba
  lượt kiểm tra phản hồi liên tiếp đạt; có bốn lượt hết hạn 500 ms lúc
  đang tải bài, không coi đây là kiểm tra hiệu năng toàn ứng dụng.
- Đối chiếu trước/sau cài: nguồn/phiên bản bài, 1.224 WAV tham chiếu,
  cặp/tốc độ và checksum Key giữ nguyên.

[Bản phát hành RC110](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc110).
