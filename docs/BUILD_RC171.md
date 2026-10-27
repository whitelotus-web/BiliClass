# BiliClass 1.0.0rc171

Mốc cập nhật Word ngày 27/10/2026, nhánh `codex/word-format-preview-rc171`.
Giữ nguyên các tag/bộ cài RC167, RC169 và RC170.

- Mẫu song ngữ gọn, chỉ hiện sau khi tải Word, phản ánh bốn kiểu bố cục
  và định dạng đang chọn. Bảng màu đánh dấu màu hiện tại, có mẫu màu/HEX
  cho màu tùy chọn; vạch dưới A theo màu chữ.
- Dịch toàn bộ làm mờ và khóa hai khung chọn riêng; bỏ tích khôi phục
  vùng thủ công. Chọn hụt từ tự nới đủ từ trước khi xác nhận.
- Bôi qua dòng trống Word không còn báo nhầm bố cục đã đổi. Popup Chọn/Hủy
  nhỏ gọn nằm trong phần nguồn đang nhìn thấy. Hai nút Chọn tất cả/Bỏ chọn
  ở nguồn được bỏ; Bỏ tất cả vẫn ở bên phải.
- Nhãn nhóm là #1, #2…; dấu × cân giữa theo thẻ. Bấm nhóm đưa nội dung
  tương ứng vào giữa khung nguồn khi vừa chiều cao, giữ nguyên chế độ
  bôi đen/tích chọn. Bỏ tất cả hoặc bỏ nhóm cuối không đổi chế độ chọn.
- Không ghi đè nguồn Word, không thay thư viện/key. Bản xuất vẫn dùng hậu
  tố `(Song ngu VI-EN)`. Kiểm thử xuất giữ nguyên nội dung/định dạng phần
  ngoài vùng chọn. Bản xem là bề mặt chọn chữ, không thay Microsoft Word.

Kiểm nguồn bằng môi trường `.venv`: bộ kiểm thử Word và Qt toàn luồng,
kiểm trên tài liệu dài cục bộ bằng thư viện thử riêng, không gọi API dịch
thật. Tài liệu cá nhân, key và ảnh báo cáo không vào Git hoặc bộ cài.

Bộ dựng kiểm hash baseline RC170, biên dịch lại toàn bộ module app và dùng
QML/tài nguyên hiện tại; không đổi dependency/model. Trước công bố, kiểm
manifest/hash ZIP, cài vào thư mục thử riêng, pipeline giọng Việt–Anh,
Qt Word từ runtime đóng gói, gỡ cài giữ dữ liệu và updater từ bản cũ.
Commit/version/hash được ghi ở BUILD_INFO/SHA256 của thư mục bộ cài.
