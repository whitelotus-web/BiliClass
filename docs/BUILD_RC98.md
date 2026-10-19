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
