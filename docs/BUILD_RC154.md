# RC154 — Chuyển slide dưới ảnh thu nhỏ, hàng đợi nhẹ hơn

Cả Chuyển đổi và Tạo giọng đọc đều có nút trước/sau và số slide
ngay dưới ảnh thu nhỏ khi chọn một hoặc nhiều bài, không cần bấm
Xem trước slide. Khi phóng to, dùng điều khiển bên dưới ảnh lớn;
không hiện hai bộ điều khiển cùng lúc. Các nút gọi đúng cơ chế
xem trước đang có, chặn khi đang tải ảnh và chặn đầu/cuối bài.

Đầu vào nhiều bài bỏ khung/nền trắng bao toàn hàng đợi. Các dòng
chưa chọn trong suốt theo nền trang; dòng đang chọn dùng nền xanh
nhẹ, viền và thanh cuộn vẫn rõ trong sáng/tối. Các nút mở file/bỏ
bài, thông tin file và xử lý lần lượt giữ nguyên. Xem trước slide
ở nhiều bài dùng chữ xanh 13 px, nền trong suốt/không viền, cùng
kiểu với một bài; bấm ẩn/hiện và bấm ảnh để phóng to như trước.

Không đổi bộ dịch, OCR, âm thanh, file gốc, lưu tự động hay dữ liệu
thư viện. Các thay đổi chỉ ở thành phần QML và smoke UI liên quan.

Kiểm chứng nguồn:

- Qt đầu vào một/nhiều bài ở cả Chuyển đổi và Tạo giọng: hình thu
  nhỏ và nút chuyển hiện cùng lúc; vị trí giữa nút chuyển và ảnh
  được đo trực tiếp; bấm chuyển slide không làm phóng to ảnh.
- Danh sách bốn bài có cuộn: chọn bài cuối, đổi nhanh hai bài,
  bỏ bài đang xem, mở đúng file từng dòng và hủy đầu vào đạt;
  kết quả ảnh cũ không lấn ảnh đang chọn, nguồn giữ nguyên.
- Sáng/tối ở 1080×700 và 1366×850: ảnh không méo, hàng đợi và nút
  xem trước rõ. Bố cục một bài 1080–1920 px vẫn đạt.
- Qt hàng đợi xử lý tuần tự chuyển đổi/tạo giọng, dừng/tiếp tục,
  thử lại và tự ẩn khi hoàn tất đạt; dùng file/WAV thử riêng.
- Ruff, compileall và các smoke không có cảnh báo QML.
  Không đánh giá lại nội dung dịch/TTS trong chỉnh sửa giao diện này.

[Trạng thái phát hành RC154: đang kiểm tra.]
