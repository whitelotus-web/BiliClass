# RC99 — Tên cặp giọng và tốc độ đọc gọn hơn

Giữ cách ghi tên cặp của RC98: dòng chính in đậm tên Việt – tên Mỹ,
dòng dưới chú thích nhỏ như Nữ Bắc – Mỹ. Bỏ nút 100% đặt lại nhanh bên
phải thanh tốc độ theo yêu cầu bổ sung; giữ thanh kéo và một nhãn phần
trăm hiển thị tốc độ hiện tại. Thanh kéo nhận phần chiều rộng còn lại.

Giữ nguyên lựa chọn cặp, người đọc, tốc độ đã lưu, cache và WAV cũ.
Không đổi engine, model, nội dung mẫu nghe hoặc hành vi trình chiếu.

## Kiểm chứng và đóng gói

- Ruff và compileall đạt. 97 kiểm thử giọng của RC98 vẫn áp dụng cho
  backend không đổi; RC99 chỉ bỏ một nút QML và cập nhật phiên bản.
- Qt chọn/nghe đủ chín cặp, nghe từng ngôn ngữ, lưu cặp tự ghép, ba chế
  độ tạo và giữ nguồn/WAV cũ đạt; không cảnh báo QML.
- Qt giọng/tốc độ: chín mẫu phát trong 25–33 ms, lưu tốc độ khi đang
  chuẩn bị trong 27 ms; hủy không phát muộn, không gọi API/nạp mô hình.
- Đã xem ảnh Settings: chỉ còn một nhãn phần trăm và thanh kéo kéo dài
  cân đối; tên cặp vẫn in đậm, chú thích nhỏ đồng nhất.

Bằng chứng ở `reports/rc99/voice-pairs-ui` và
`reports/rc99/source-voice-ui.json` (không đưa vào Git).

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc98-pair-labels --output dist/rc99-voice-speed-ui
```

- Commit ứng dụng: `0f9430cd1d4f920776dd8dcdecc70c27f5668162`.
- Dựng một lần từ nguồn đã kiểm thử; runtime/mô hình RC98 được kiểm
  đầy đủ checksum. Toàn bộ module ứng dụng được dựng lại.
- ZIP `BiliClass-RC99-Windows.zip`: 1.246.809.129 byte, 4.631 tệp ứng
  dụng, 4.635 mục ZIP. Toàn bộ nội dung ZIP đối chiếu manifest đạt.
- SHA256: `5515a3436bd437df54607fa44f2c6b98db0fb78ec95eadf49cb967476a01ec65`.
- Qt trong bản đóng gói đạt: chín mẫu bắt đầu trong 22–32 ms, lưu tốc độ
  trong 24 ms khi đang chuẩn bị; khoảng ngắt giao diện lớn nhất 104 ms.
  Không nạp mô hình, gọi API, phát muộn sau khi hủy hoặc cảnh báo QML.
  Bằng chứng `reports/rc99/frozen-voice-ui.json`.

Đã cài và mở tại `F:/Applications/BiliClass/1.0.0rc99` qua Explorer,
đóng RC98 bình thường. Cửa sổ chính và Mascot đáp ứng, không thu nhỏ;
icon nhỏ/lớn, AppUserModelID và shortcut Desktop/Start menu đúng.
Nguồn, revision, môn, cấu hình giọng, khóa API và 134 WAV tham chiếu
giữ nguyên (`reports/rc99/installed-verification.json`).

Đã công bố tại https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc99 .
Digest asset GitHub khớp SHA256 ở trên.
