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

## Gói Windows đã cài và kiểm chứng

- Version: `1.0.0rc72`; mã nguồn build:
  `7445dd334f7f8bc74ee98737641aea940704c4b4`.
- `BiliClass-RC72-Windows.zip`: 840.289.515 byte, 4.187 tệp; đã đối chiếu
  SHA-256/CRC toàn bộ entry. Runtime/model đầy đủ tái dùng từ gói RC71 đã kiểm.
- SHA-256 ZIP: `cd32268ca1a2419f87129c816e5bc9cc07860ddec34bb90e8ae0d2935b53eeb7`.
- SHA-256 EXE: `0bec256e9774ad7627a2edf3d9a5809085b42a6da9e2f81241e93937d7d4057f`.
- Cài tại `F:/Applications/BiliClass/1.0.0rc72`; marker cài đặt là RC72.
  Đây là gói cài trên máy này, chưa công bố thành GitHub Release.

Bản EXE đã cài vượt qua 8 smoke giao diện: Trang chủ, Chuyển đổi, Giọng đọc,
Cài đặt ở 1080×700 và 1366×850; không có QML warning. Self-test tách dữ liệu
và bỏ đường dẫn phát triển đã qua: DOCX/PPTX, bốn prompt/chế độ nhập kết quả,
ba mẫu tích hợp và 12 preview, SQLite/history/gói nháp, tổng hợp WAV ngoại
tuyến thực với VieNeu (VI/EN/mixed/tốc độ/cache), tiến trình lớp học và ACK
WebSocket, xuất bài đã duyệt và round-trip backup. Không tải model hay gọi
API dịch. Có tạo âm thanh thật nhưng chưa nghe nghiệm thu phát âm; đây vẫn
là Windows hiện tại, chưa đại diện Windows sạch.
