# RC73 — Khôi phục, giọng đọc và giao diện

Ngày 18/10/2026. Source đang hoàn thiện theo phản hồi thử trực tiếp của
giáo viên. Bộ cài RC72 đang mở không bị dừng khi sửa source RC73.

## Đã kiểm chứng ở mốc source đầu

- 972 ca kiểm thử đạt theo ba tiến trình: 854 core, 104 browser AI, 14
  browser translation. Lượt monolithic bị treo trong Playwright/Chrome sau
  nhiều phiên; ca bị treo chạy riêng đạt, ba nhóm chạy riêng đạt. Lệnh kiểm
  chuẩn đã tách nhóm; chưa kết luận nguyên nhân treo monolithic đã hết.
- Hai lỗi đầu vòng core đã xử lý: thông báo cấu hình có sẵn và fallback
  tên voice trong popup. Nhóm 55 ca liên quan chạy lại đạt trước vòng cuối.
- Qt giọng/diễn giải chuyển đổi, popup tạo lại và bảo toàn nguồn đạt; mặc
  định lần đầu là Tiếng Anh theo yêu cầu mới nhất, nhớ lần chọn gần nhất.
- Sao lưu thư viện thật 8.040.765.784 byte rồi restore 20 bài; restore gói
  cũ 2.231.885.510 byte được 17 bài, integrity SQLite đạt. Tệp giữ tại máy,
  không ở Git. Không bao gồm model, key hoặc phiên đăng nhập trong gói này.
- 8 corpus tự tạo đã render bằng PowerPoint qua worker riêng: 9 slide đầu
  ra, không còn FAIL kỹ thuật; CHECK vẫn giữ cho hình/hiệu ứng/phần cần
  người xem. Group nguồn có 2 vùng overflow, đầu ra không còn overflow.
  Sau kiểm ảnh bảng, sửa lượng có đơn vị như `12 kg` để không nhân đôi
  trong cặp ngôn ngữ; 41 ca và native bảng sau sửa đạt.
- 6 voice có VI/EN/xen kẽ/công thức và bộ WAV để nghe tay. Có mẫu dùng
  cache; không phải chứng nhận phát âm/thuật ngữ bởi giáo viên.

Chi tiết triển khai và phần còn chạy: [IMPLEMENTATION_RC73](IMPLEMENTATION_RC73.md).
Nghiệm thu điện thoại, máy chiếu, Windows sạch và nghe tay:
[ACCEPTANCE_FIELD](ACCEPTANCE_FIELD.md). Kênh nguồn/phát hành:
[RELEASE_CHANNEL](RELEASE_CHANNEL.md).

## Còn cập nhật trước khi chốt gói

Phản hồi mới về màn hoàn tất và mở thẳng PowerPoint, các luồng Qt còn lại,
DPI, lint script/test, đo phiên dài, bản dựng/frozen/installer và commit/hash
gói. Không coi mục chưa có bằng chứng là đã đạt.
