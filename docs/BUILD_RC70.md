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

- Phiên bản `1.0.0rc70`, nguồn `5e03483524ebe61bebedea4ac0affd4a936d6055`.
- Biên dịch lại 121 module app; giữ runtime/model đã kiểm của RC69.
- ZIP `BiliClass-RC70-Windows.zip`: 840.280.245 byte, 4.187 mục;
  kiểm SHA-256/CRC toàn bộ mục và đối chiếu digest trên GitHub.
- SHA-256 ZIP: `e8afa221456dcbffe0135174397838ef45489f4ffe31d3ab0136d9df403cf91b`.
- SHA-256 EXE: `e5f647ec2de55924334fe11edba55ad651a307f618915346e3f6383b746d1933`.
- Đã cài tại `F:/Applications/BiliClass/1.0.0rc70`. Bốn cấu hình Qt frozen
  của Chuyển đổi/Tạo giọng ở 1080×700 và 1366×850 đạt, không dùng PYTHONPATH
  nguồn, không có cảnh báo QML; các tệp QML khớp nguồn.
- Đã mở ứng dụng từ Explorer, ngoài job của trình kiểm thử, phản hồi đủ 10
  lần kiểm tra. Shortcut Desktop/Start trỏ RC70; mở sẵn trang Chuyển đổi.
- Trước/sau mở bản cài giữ nguyên 19 bản ghi bài giảng, 1.096 WAV và cấu
  hình hồ sơ/giọng/Mascot. Key mã hóa, tên key, bộ đếm và lịch sử không đổi;
  không tự chạy lại tác vụ giọng đã hoàn tất.
- [Phát hành RC70](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc70).
  Bộ chọn cập nhật công khai kiểm RC68/RC69 nhận RC70 cùng kích thước/digest;
  RC70 không nhận bản cũ.

Báo cáo `reports/rc70/`, `reports/rc70-installed/` và các gói cài ở ngoài Git.
Phạm vi kiểm là máy Windows hiện tại; không chạy suy luận giọng mới hoặc
kiểm trên máy vật lý thứ hai trong bản sửa giao diện này.
