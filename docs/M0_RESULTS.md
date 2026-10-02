# M0 — kết quả kỹ thuật và quyết định đi tiếp

29/09/2026. Máy phát triển: Windows 10 x64, Intel i7-8700, RAM 32 GB, PowerPoint 16.0. Đây không phải máy tham chiếu 8 GB. Mã thử nằm riêng trong biliclass_m0; dữ liệu đo gốc tại reports/m0 và .runtime/reports.

| Spike | Đã kiểm chứng | Còn mở |
|---|---|---|
| PowerPoint | Tạo deck kỹ thuật riêng; COM đọc đúng chuỗi slide 1→2→3→1; stable IDs và hash nguồn không đổi | Animation/video, full-screen overlay, projector, Presenter View, DPI/rút màn hình |
| Dịch/TTS CPU | 60 ca/30 cặp song ngữ bằng Argos 1.9/CT2 INT8, khoảng 268 MB peak RSS ở lần đo gần nhất; SAPI tạo WAV EN local | Chất lượng bản dịch cần giáo viên chấm; chưa có voice VI trong SAPI; máy 8 GB; kiểm thử Internet bị chặn cấp OS |
| Classroom transport | 50 WebSocket client loopback đồng thời; retry không đếm trùng, reconnect giữ participant, không lộ đáp án; p95 ACK khoảng 17 ms ở lượt đo | Điện thoại/router/firewall thật; dashboard broadcast và lưu bền session thuộc M5 |
| Qt/Windows package | Qt Quick UI chạy 1366×768; screenshot không warning QML; PyInstaller onedir .exe chạy và thoát mã 0 | Windows sạch, DPI và nhiều màn hình thực địa; kích thước/tốc độ package chưa tối ưu |

Benchmark dịch gần nhất: VI→EN p50 khoảng 72 ms, p95 867 ms; EN→VI p50 khoảng 79 ms, p95 143 ms. Có tải build chạy cùng nên đây là baseline thăm dò, không phải SLA. Hai cờ số là trường hợp “3” thành “three”, không kết luận sai nghĩa tự động. CSV lưu nguồn/đích/tham chiếu và cột chấm chất lượng trống.

## Lỗi đã tìm và xử lý

- Native SentencePiece loader không đọc được đường dẫn tiếng Việt: nạp model bằng bytes do Python đọc; CT2 dùng file mapping in-memory.
- Tokenizer của gói Argos có ký hiệu khoảng trắng còn sót: xử lý U+2581 sau decode, giữ underscore thông thường để tránh phá code.
- Native style Windows của Qt không nhận tùy biến component: dùng Basic style.
- PyInstaller thu nhầm `icuuc.dll` từ Poppler có trên PATH, thiếu API Windows ICU mà Qt cần. Loại DLL ngoại lai trong thư mục build, dùng ICU hệ điều hành; không sửa DLL hệ thống. Đồng bộ VC runtime đi kèm Qt trong app bundle.
- PowerPoint slideshow bắt đầu ở cửa sổ maximize; phép resize không phù hợp và không cần cho phép thử đồng bộ, đã bỏ.

## Gate

GO có điều kiện cho M1 nền tảng: bốn spike đều đã có kết quả, không còn lỗi local chặn mở Qt/COM/dịch/transport. Không đánh dấu M0 nghiệm thu thực địa hoàn toàn. Việc lưu thư viện, settings, review drafts có thể xây độc lập các kiểm tra projector/điện thoại còn thiếu. Các phần chưa kiểm chứng phải giữ trạng thái experimental, không quảng bá V1 đã sẵn sàng triển khai trường học.

Model hiện tại chỉ là ứng viên; không phê duyệt chất lượng dịch tự động. Không bắt buộc voice VI để xây M1; Rescue chữ vẫn là phương án có thật. Không triển khai BiliCard trong lượt này.

## Kiểm tra tự động đã có

26 tests đạt cho level policies, grade/subject mở, retrieval không bịa nội dung, readiness không đòi mạng nếu không quiz, ResponseProvider, idempotency, stale/closed round, DTO không lộ đáp án và auth join. Lint đạt sau chỉnh import. Một cảnh báo dependency về httpx test client được ghi nhận; không ảnh hưởng kết quả transport socket thật.
