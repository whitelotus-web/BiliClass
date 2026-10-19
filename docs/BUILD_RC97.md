# RC97 — Thêm Trúc Ly, Đoan Trang, Phạm Tuyên và Bella

Thêm ba cặp gợi ý: Trúc Ly + Bella, Đoan Trang + Heart, Phạm Tuyên + Michael.
Sáu cặp cũ giữ nguyên ID và thứ tự hai hàng nữ/nam Bắc–Trung–Nam. Ba cặp
bổ sung ở hàng thứ ba, ghi tên và giọng Mỹ đi kèm để dễ phân biệt.

Hai bộ chọn riêng có 9 giọng Việt và 3 giọng Mỹ, tự ghép được 27 tổ hợp.
Bella là giọng nữ Mỹ `af_bella`, speaker index 2 của bộ Kokoro đã đóng gói.
Ba giọng Việt dùng preset có sẵn trong VieNeu v3 turbo. Không đổi mô hình,
không thêm dịch vụ mạng hoặc API. Các cặp tự ghép cũ giữ ID.

Nút nghe từng ngôn ngữ đặt cạnh bộ chọn, giữ hai đoạn mẫu dài sửa được.
Các mẫu mặc định mới được tạo bằng engine local và kiểm checksum, nội dung,
người đọc, phiên bản engine. Chỉ chép WAV công khai cuối cùng vào tài nguyên;
cache trung gian ở reports và không vào Git. Bài và WAV cá nhân không tạo lại.

## Kiểm chứng

- Ruff và compileall đạt; 1.011 kiểm thử lõi đạt trong 157,44 giây. Bỏ
  sáu nhóm trình duyệt cũ như RC96; một cảnh báo Starlette/httpx không liên quan.
- Bao phủ 27 cặp × ba chế độ tạo, ánh xạ speaker Bella/Heart/Michael,
  thứ tự sáu cặp cũ, xuất hai loa và dùng lại cache đúng người đọc.
- Qt nghe cả chín cặp và hai ngôn ngữ riêng, lưu cặp tự ghép, tạo đủ ba
  sản phẩm, giữ nguồn và WAV cũ: đạt; không cảnh báo QML.
- Đã xem ảnh Settings 1366 × 850 và 1080 × 700. Hai cột cân nhau; cửa
  sổ thấp cuộn nội dung, nghe cả cặp/dừng/lưu luôn hiện ngoài vùng cuộn.
- Kiểm tra Qt mẫu sẵn bắt đầu trong 24–39 ms; lưu lúc đang chuẩn bị
  trong 28 ms; khoảng ngắt giao diện lớn nhất 107 ms. Hủy không phát
  muộn, không nạp mô hình hoặc gọi API, không cảnh báo QML.
- Xác minh đủ 30 WAV công khai với manifest: chín mẫu cũ, chín mẫu cặp,
  12 mẫu ngôn ngữ; PCM mono 16 bit 48 kHz. Không có tệp trung gian.

Bằng chứng ở `reports/rc97-core-tests.log`, `reports/rc97/voice-pairs-ui`
và `reports/rc97/source-voice-ui.json` (đều không đưa vào Git).

## Đóng gói

Phiên bản `1.0.0rc97`, dựng một lần từ nguồn đã kiểm thử:

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc96-selection-ui --output dist/rc97-extra-voices
```

- Commit ứng dụng: `7a56fc732954dcad82d037d248f2bffdd0ee09e5`.
- ZIP `BiliClass-RC97-Windows.zip`: 1.246.809.377 byte, 4.631 tệp ứng
  dụng (4.635 mục ZIP). Đối chiếu toàn bộ nội dung ZIP với manifest đạt.
- SHA256: `c0915721e1158c2d5288f5019074e53b99863d794128211bf35f8943ef126022`.
- Runtime và mô hình RC96 được kiểm đủ checksum trước khi dùng lại;
  toàn bộ module ứng dụng được dựng lại. Không thêm model vào Git.

Kiểm tra bản cài độc lập đạt tại
`reports/release/1.0.0rc97-b7909efb/installer.json`: đường dẫn Unicode,
Windows Details, shortcut tạm, trang Qt, template, hai engine thật,
tiến trình lớp học, sao lưu và gỡ bản thử vẫn giữ thư viện riêng.
Qt chuyển từ kết quả sang tạo hai giọng thật hoàn tất trong 17,47 giây,
giữ nguồn và không cảnh báo QML; không dùng API hoặc cache phát triển.

Kiểm tra mẫu trong bản đóng gói đạt: chín cặp bắt đầu trong 24–168 ms,
lưu lúc đang chuẩn bị trong 23 ms; khoảng ngắt giao diện lớn nhất 130 ms.
Không nạp mô hình, không phát muộn sau khi hủy, không cảnh báo QML.
Bằng chứng `reports/rc97/frozen-voice-ui.json`.

Đã công bố tại https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc97 .
Digest asset GitHub khớp SHA256 ở trên.

Đã cài tại `F:/Applications/BiliClass/1.0.0rc97`, đóng RC96 bình thường
và mở RC97 qua Explorer vào Cài đặt. Cửa sổ chính và Mascot đáp ứng,
không thu nhỏ; tiến trình chạy độc lập với Codex. Icon nhỏ/lớn,
AppUserModelID và shortcut Desktop/Start menu đều đúng.
Nguồn, revision, môn đã chọn, cấu hình giọng, khóa API và toàn bộ 134
WAV tham chiếu của bài đang dùng giữ nguyên. Bằng chứng
`reports/rc97/installed-verification.json`.

Kế hoạch đọc liên tục có khoảng nghỉ và đọc từng nhóm nội dung nằm tại
`docs/PLAN_SEGMENT_PLAYBACK.md`; chưa thay đổi cơ chế trình chiếu trong RC97.
