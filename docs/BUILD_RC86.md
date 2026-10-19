# RC86 — Chống crash và giữ phản hồi khi tạo giọng đọc

Windows ghi nhận ba lần access violation của RC83–85 đúng lúc watchdog
đang ghi stack; log bị cắt giữa tên file/frame. Các offset trong DLL Python
3.12.7 trỏ vào `PyCode_Addr2Line` và vùng `_Py_DumpTraceback`. Vì vậy bỏ
`faulthandler.dump_traceback_later()` khỏi watchdog. Luồng Python lấy tham
chiếu frame/code trong GIL, chỉ ghi tên file/hàm/dòng, không lấy nội dung
bài hay biến cục bộ. File log do luồng đó tự mở/đóng; lỗi ghi log không
làm tắt ứng dụng. Nếu chính GIL bị giữ lâu, chấp nhận ghi chậm thay vì
đọc frame thiếu an toàn. Có [báo cáo upstream về cùng cơ chế đọc metadata
đang được giải phóng](https://github.com/python/cpython/issues/158200);
không coi báo cáo trên nhánh main là chứng nhận mọi bản Python 3.12.

Việc kiểm tra WAV của bản giọng đang chọn chạy trên worker, có hủy và
loại bỏ kết quả cũ khi đổi bài. Getter QML chỉ đọc trạng thái đã công bố.
Lập kế hoạch, kiểm tra bản giọng có sẵn và lưu metadata trước khi tạo cũng
chuyển ra khỏi GUI. Nút mở bản có giọng vẫn kiểm tra lại tệp trong worker
trước khi mở PowerPoint.

Giao diện dùng một snapshot bài giảng thay cho 69 lần chuyển cả bản đồ
Python sang QML; nhận diện ngôn ngữ thuần túy dùng cache có giới hạn.

Phép thử model thật còn phát hiện nạp thư viện/model có thể giữ GIL lâu
trong lần đầu, dù gọi từ QThread. Desktop nay tạo giọng bằng tiến trình
riêng, giữ model để dùng lại, vẫn chung khóa/cache và thứ tự ưu tiên đọc.
Nếu helper lỗi, GUI báo lỗi và giữ bài; lần thử kế tiếp có thể khởi tạo
lại. Helper tự thoát khi ứng dụng chủ mất, và được đóng khi thoát tool.
Model, giọng, tốc độ, tên/cache WAV và cách gắn PowerPoint giữ nguyên.

Kiểm thử nguồn trên máy này:

- 946 test core đạt; lint và compile đạt. Còn một warning Starlette/httpx
  đã tồn tại, không có lỗi test.
- Qt: cố ý giữ GUI hơn 6 giây khi luồng khác tạo/hủy code; watchdog ghi
  được log và ứng dụng tiếp tục chạy.
- 51 slide, giả lập mỗi kiểm tra WAV mất 120 ms, 40 lần chuyển màn hình:
  không kiểm tra WAV trên GUI, không warning QML; khoảng ngắt heartbeat
  lớn nhất 0,407 giây trong phép thử.
- Qt chuyển đổi hoàn tất → tạo giọng Việt–Anh bằng model thật, watchdog
  bật, dữ liệu riêng: 2 đoạn hoàn tất trong 9,41 giây, heartbeat lớn nhất
  0,313 giây. Đây là đo cục bộ, không phải cam kết cho mọi máy/ổ đĩa.
- Các luồng Qt tạo/hủy/tạo tiếp giọng, dùng/tạo lại bản có sẵn, bố cục,
  chuyển đổi API fixture và Office mở/gắn bài với Mascot đạt.
- Test helper thực sự chạy process: tái dùng, báo lỗi, khôi phục sau crash
  và tự thoát khi chủ bị tắt đột ngột.

Bài cá nhân gặp crash được kiểm tra chỉ đọc: bản PowerPoint đã lưu tồn
tại, đủ 30 slide, SHA-256 khớp metadata. Không sửa/xóa bài đó hoặc đưa
dữ liệu, key, log, dump, WAV hay executable vào commit.

Lệnh kiểm tra bản đóng gói mới `--check-narration-ui <report.json>` dùng
bài và thư viện tạm, GUI Qt thật, model VieNeu thật và watchdog bật. Quy
trình release bắt buộc chạy phép thử này trước khi công bố gói.
