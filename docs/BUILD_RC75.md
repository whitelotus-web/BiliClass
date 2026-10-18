# RC75 — Loa gọn với nhãn ngôn ngữ ở góc

Ngày 18/10/2026. Phản hồi tiếp theo của giáo viên sau mốc RC74 đã đóng gói.

- Icon loa/Ⅱ và nhãn VI/EN/VI+EN cùng một ảnh, cùng vùng bấm. Nhãn không
  trôi hoặc cần bấm riêng; trạng thái phát giữ đúng nhãn ngôn ngữ.
- Dạng thường 36 × 36 pt, nhãn khoảng 8 pt; dạng hẹp 50 × 20 pt, nhãn
  khoảng 7,5 pt. Không tăng chiều cao header 20 pt đã kiểm chứng ở RC73.
- Hàng loa dùng vùng 44 × 42 pt thay cho 62 × 42 pt; tiếp tục thử hàng,
  cột, vùng rời và header. Không nới điều kiện đè lên nội dung gốc.
- Ảnh PNG dựng từ SVG bằng mã trong `scripts/build_speaker_icon.py`;
  không cần font ngoài hay truy cập mạng khi sử dụng.
- 49 ca liên quan xuất audio, binding, phím và cache render đạt ở lượt cuối. Toàn bộ
  media/timing giữ cùng cơ chế RC74; không thử lại desktop input sau khi
  giáo viên bấm Escape dừng Computer Use.
- Đã xuất bài thật thành bản **Nút loa gọn**, đủ 86 slide / 258 loa;
  không đổi bài lưu hoặc source. Chứng cứ riêng tại `reports/rc75`.
- Phạm vi phím và badge động vẫn theo [RC74](BUILD_RC74.md): cần phiên
  PowerPoint gắn với BiliClass; mở PPTX độc lập dùng player native.

Qt workspace chạy offscreen đạt, không QML warning. Đã render native các
slide 1/3/4/60; kiểu thường và kiểu header nhìn rõ. Phát hiện Office trả
bitmap đầu thiếu cả master/header và poster trên slide 4 dù shape Visible
đang bật. Lượt xuất tiếp đầy đủ; renderer nay prime một lượt trước khi
ghi cache để tránh ảnh xem trước thiếu thành phần trong tình huống này.

## Gói cài đã kiểm

- Dựng một lần từ `073cb3c4de294ac3035c07af1735a4d174562c5f`; CI commit
  này đạt. Runtime RC74 được xác minh trước khi tái dùng; mã app dựng lại.
- Gói `dist/rc75-speaker-badges/BiliClass-RC75-Windows.zip`: 871.094.765
  byte, 4.209 entry; đối chiếu SHA từng file trong archive đạt.
- EXE SHA256: `b1004f3d56c06fbc4da5f5b815afa775c3512a8075b6e483479a6188107b9a15`.
- ZIP SHA256: `c73bd2a7fbc93334638c820b8cb5877b32b6589294d57725ffc4986c77add1b1`.
- Cài vào đường dẫn Unicode riêng, kiểm Qt hai trang, VieNeu Việt/Anh,
  template, lớp học process, backup và gỡ giữ thư viện đạt. Qt chạy
  offscreen, không thao tác desktop sau Escape. Trang Cài đặt EXE cũng
  có smoke offscreen riêng đạt. Báo cáo tại
  `reports/release/1.0.0rc75-571c4571` và `reports/rc75/frozen-settings.png`.
- Chưa thay bộ cài/shortcut RC73 đang dùng hoặc kiểm lại F5 bằng desktop
  input trên EXE RC75. Phiên test RC74 khởi động riêng dùng fixture,
  không dùng thư viện thật; đã kết thúc khi hoàn tất kiểm tra.
