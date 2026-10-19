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
