# RC98 — Hiển thị tên cặp giọng trước

Chín cặp gợi ý dùng cùng một cách ghi: tên Việt – tên Mỹ in đậm ở dòng
trên, ví dụ **Mai Anh – Heart**; dòng chú thích nhỏ, màu dịu ghi **Nữ Bắc – Mỹ**.
Trúc Ly – Bella, Đoan Trang – Heart, Phạm Tuyên – Michael cũng theo định
dạng này. Giữ thứ tự các cặp và bố cục ba cột hiện có.

Chỉ đổi nhãn hiển thị, giữ ID cặp/giọng, speaker, engine, cache, cấu hình
đã lưu và hành vi phát. Không tạo lại giọng bài cũ hoặc tải thêm mô hình.
Các tổ hợp tự ghép cũng có nhãn đúng hai người đọc được chọn.

## Kiểm chứng và đóng gói

- Ruff và compileall đạt; 97 kiểm thử liên quan tới cặp giọng, mẫu nghe,
  cache và mức sẵn sàng của engine đạt trong 18,67 giây.
- Qt nghe chín cặp và hai ngôn ngữ riêng, lưu cặp tự ghép, tạo đủ ba sản
  phẩm, dùng lại giọng cũ và giữ nguồn đạt; không cảnh báo QML.
- Đã xem ảnh Settings 1080 × 700 và 1366 × 850: cả chín tên cặp vừa ô,
  ghi chú đồng nhất và nền chọn nhạt. Không đổi kích thước/bố cục nút.

Bằng chứng Qt ở `reports/rc98/voice-pairs-ui` (không đưa vào Git).

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc97-extra-voices --output dist/rc98-pair-labels
```

- Commit ứng dụng: `bc2fd73051c2ee8032af47f608ccc48e0c1e02d5`.
- Dựng một lần; kiểm checksum đầy đủ runtime/mô hình RC97 trước khi dùng lại.
  Toàn bộ module ứng dụng được dựng lại. Không thêm model hoặc mẫu âm thanh mới.
- ZIP `BiliClass-RC98-Windows.zip`: SHA256
  `0a905c9d74be53441b6f52b3d7fadcf36864bda380d23723ce50ed85495184e4`.
  Đối chiếu toàn bộ nội dung ZIP với manifest đạt.
- Qt bản đóng gói nghe đủ chín cặp trong 23–33 ms, lưu lúc đang chuẩn bị
  trong 24 ms; khoảng ngắt giao diện lớn nhất 107 ms. Hủy không phát muộn,
  không nạp mô hình hoặc gọi API, không cảnh báo QML.
  Bằng chứng `reports/rc98/frozen-voice-ui.json`.

Đã công bố tại https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc98 .
Digest asset GitHub khớp SHA256. Đã cài và mở qua Explorer tại
`F:/Applications/BiliClass/1.0.0rc98`, đóng RC97 bình thường. Icon và hai
shortcut đúng; nguồn, cấu hình, revision, môn, khóa API và 134 WAV giữ
nguyên (`reports/rc98/installed-verification.json`).

Yêu cầu bỏ thêm nút 100% đến lúc RC98 đang cài/tải lên; phần này nằm ở
RC99, tiếp tục giữ toàn bộ thay đổi tên cặp ở trên.
