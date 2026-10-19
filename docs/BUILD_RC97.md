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
