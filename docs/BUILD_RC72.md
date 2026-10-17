# RC72 — Hoàn tất RC71 và tối ưu dữ liệu

Ngày 18/10/2026. Kế thừa toàn bộ sửa lỗi giọng đọc/tiếp tục lưu của RC71.
Giữ các tab Cài đặt và thiết kế giao diện hiện tại.

## Thay đổi

- Chuẩn hóa lời đọc trước lần lưu đầu của bài mới; giữ revision 1 và không
  tạo lịch sử giả. Bài được nhận lại theo request ID không tạo bản trùng.
  Chuẩn hóa bài cũ nằm trong giao dịch tìm bài để không ghi từ snapshot cũ
  khi kết nối khác có thể sửa. Bài tạo giọng riêng giữ dữ liệu speech gốc.
- Chốt chuyển thư viện dùng lại hash vừa kiểm cho tệp không đổi; không đọc
  lại tất cả PowerPoint/model/WAV để dựng manifest. JSON đổi đường dẫn ghi
  qua tệp tạm, có callback tiến độ cho bước kiểm cuối.
- Sao lưu/khôi phục theo khối 1 MiB; thư mục tạm ở ổ đích. Chặn gói vượt
  giới hạn khôi phục trước khi thay bản tốt. Thư viện khôi phục chỉ xuất
  hiện sau khi checksum và SQLite hợp lệ.
- Bổ sung ca giới hạn, checksum hỏng, round-trip, bảo toàn gói tốt và chi
  phí đọc tệp. Sửa smoke Thư viện/Trang chủ, nhãn mascot của Lớp học.
- Không đưa tệp chẩn đoán trong `output/` vào Git.

## Phạm vi kiểm chứng

Đã chạy vòng toàn bộ đầu tiên: 928 qua, 2 lỗi. Một lỗi là lịch sử giả khi
nhập bài đồng thời, đã sửa; lỗi kia do đổi version trong lúc lượt kiểm cũ
còn chạy. Nhóm 76 ca nhập bài/giọng/Google/package sau sửa đã qua. Lượt toàn
bộ cuối: **938 passed**, một cảnh báo phụ thuộc FastAPI/Starlette/httpx,
530,46 giây. Ruff nguồn `app`/`biliclass_m0` và compileall đạt.

Chín luồng Qt được rà soát: narration, chuyển dữ liệu, Trang chủ, thư viện,
lớp học, phiên dạy, mặc định chuyển đổi, phản hồi giao diện và Google fixture.
Hai smoke cũ sai kỳ vọng với UI hiện hành đã sửa và chạy lại đạt; không
thay ứng dụng để khớp bài test cũ. Fixture API/WAV không chứng nhận chất
lượng dịch hay phát âm model. Office COM có log RPC disconnected; không
diễn giải test qua là Office ổn trên mọi máy/bài.

50 client WebSocket loopback: đủ 50 phản hồi, 35 đúng (70%); gửi lại và
vào lại không nhân đôi, khởi động lại giữ dữ liệu. ACK p95 174,9 ms, lớn nhất
182,0 ms trong một lượt trên máy này. Chưa phải thử Wi-Fi/điện thoại thật.

Sao lưu tệp thử 24 MiB: peak cấp phát Python 24,45 → 2,29 MiB; tổng backup
+ restore 0,661 → 0,959 giây. Giảm bộ nhớ, không tuyên bố tăng tốc tổng thể.

Mã nguồn, tài liệu và kiểm thử được commit/push riêng với gói Windows.
Gói ghi version/commit/hash, không chứa thư viện cá nhân. Kế hoạch tiếp theo:
[OPTIMIZATION_PLAN_RC72.md](OPTIMIZATION_PLAN_RC72.md).
