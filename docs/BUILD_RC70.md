# RC70 — Khôi phục giao diện tải PowerPoint

Ngày 17/10/2026. Chỉ đổi vùng tải trong Chuyển đổi sang cùng biến thể
`PowerPointUpload` đang dùng ở Tạo giọng đọc: ảnh lớn bên trái; tiêu đề,
hướng dẫn, nút chọn tệp có icon và dòng giới hạn căn giữa bên phải.

Giữ cấu hình chuyển đổi gọn của RC69, chọn/đổi/bỏ tệp, kéo thả và toàn bộ
luồng tạo giọng/Mascot/key. Không đổi engine hoặc dữ liệu người dùng.

Khung tải giữ kích thước như mẫu người dùng yêu cầu. Khi cửa sổ thấp và
có thêm tên tệp/môn Khác/tùy chọn mẫu, phần cấu hình có thể cần cuộn; kiểm
các trường vẫn truy cập được và nút chuyển đổi ở footer cố định.

## Kiểm chứng

- 36 kiểm thử cấu hình đầu vào/chọn tệp và đóng gói đạt bằng `.venv`.
- Qt kiểm 32 cấu hình ở 1080×700, 1366×768, 1366×850 và 1920×1080,
  trước/sau chọn tệp, giữ gốc/mẫu mới, môn thường/Khác; kiểm các trường
  cuối vẫn truy cập được khi cần cuộn. So chiều cao và biến thể của khung
  tải với Tạo giọng ở cả bốn kích thước, không có cảnh báo QML.

## Đóng gói

Thông tin commit, checksum và kiểm bản cài sẽ bổ sung sau đóng gói.
