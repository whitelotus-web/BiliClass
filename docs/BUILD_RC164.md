# RC164 — bộ cài Windows đầy đủ

Ngày bàn giao: 23/10/2026. Mã nguồn dựng ứng dụng và launcher:
`8588f9974454e917c786082a021c9f0255dafa7d`.
[Source checks](https://github.com/whitelotus-web/BiliClass/actions/runs/39895053663)
đạt cho đúng commit này. Phiên bản app và Windows Details: `1.0.0rc164`.

Thư mục bàn giao tại máy: `F:\BiliClass-BoCai-RC164`.

- `BiliClass-Setup.exe`: 52.736 byte; giao diện cài tiếng Việt.
- `BiliClass-RC164-Windows.zip`: 1.259.523.770 byte, đủ 4.687 file ứng dụng,
  runtime, model Việt–Mỹ/OCR, mẫu và giấy phép. Giữ ZIP cạnh EXE;
  launcher đọc trực tiếp, không cần giải nén trước.
- Hướng dẫn ngắn, hướng dẫn đầy đủ, BUILD_INFO, SHA256 và bản ghi kiểm tra.

SHA-256 launcher:
`76ef3eae1906fec21d14739a2638872a0a5bbff8a50f9229c0f6b35bb5928159`.

SHA-256 payload:
`9877cf512263f18ec57af524247c0bdb7fe36a02c010a78d3e526eecbbbcf13e`.

Dựng một lần sau khi kiểm thử: xác minh toàn bộ runtime nền RC155, biên
dịch lại toàn bộ app, thay tài nguyên bằng nguồn hiện tại. Đối chiếu đủ
188 module bytecode và 253 tài nguyên với nguồn. ZIP kiểm tra từng file
theo manifest; không chứa thư viện, key hoặc hồ sơ cá nhân.

Kiểm chứng trên máy Windows hiện tại, dùng thư mục cài/dữ liệu riêng:

- 25 kiểm thử installer/package/updater; gồm payload lỗi/thiếu/trùng tên,
  đường dẫn thoát thư mục, sai phiên bản, cài lặp, giữ dữ liệu khác,
  launcher native và gỡ giữ thư viện. Ruff/compileall/diff-check đạt.
- Chính `BiliClass-Setup.exe` đã cài đủ gói ZIP vào thư mục Unicode trên F,
  không tạo shortcut/đăng ký thử lên tài khoản giáo viên.
- EXE đã cài mở Trang chủ, Chuyển đổi, Tạo giọng, Thư viện và Cài đặt;
  không cảnh báo QML, mặc định ẩn tính năng lớp học thử nghiệm.
- Pipeline EXE thật: DOCX/PPTX, mẫu/xem trước, SQLite/lịch sử/gói bài,
  tạo WAV Anh và Việt bằng model kèm theo, tốc độ/cache, tiến trình lớp
  học/WebSocket nội bộ và sao lưu/khôi phục.
- Qt thật tạo đủ hai lời đọc Việt–Anh từ bài thử; nguồn giữ nguyên,
  watchdog hoạt động, không cảnh báo QML, không phát âm thanh ra loa.
- Bản frozen dựng ảnh xem trước bằng PowerPoint desktop và OCR một
  slide chỉ có ảnh; không sửa PPTX nguồn thử.
- Gỡ bản cài thử thành công; `library.db` riêng vẫn còn. Các lượt này
  bỏ PYTHONPATH/PYTHONHOME và đường dẫn model/cache phát triển, tắt tải
  Hugging Face, dùng Temp riêng trên F.

Gói không yêu cầu Python trên máy nhận. PowerPoint desktop vẫn cần cho
xem/trình chiếu; chuyển đổi cần mạng và key Google Cloud Translation riêng.
Đây là kiểm tra độc lập trên máy Windows hiện tại, chưa phải chứng nhận
trên máy Windows sạch thứ hai. Không phát hành lên GitHub Releases trong
lượt bàn giao local này. EXE/model/ZIP/báo cáo thử nằm ngoài Git.

## Dung lượng và giữ môi trường sau bàn giao

Gói đầy đủ 1,26 GB, khi cài khoảng 2,12 GB (đơn vị GB thập phân).
Giọng Việt–Mỹ và OCR chiếm khoảng 826 MB trong ZIP, gần 66% gói nén.
Dung lượng cài đặt khác với RAM sử dụng; bộ cài giữ đầy đủ model chạy
ngoại tuyến theo yêu cầu bàn giao.

Mã nguồn chuẩn tiếp tục ở F. Giữ nguyên thư mục bàn giao
`F:\BiliClass-BoCai-RC164`, runtime đầy đủ `dist/rc164-full`, bản dự phòng
`dist/rc155-input-consistency`, `.git`, cả hai virtual environment, model
nguồn, thư viện cá nhân `F:\BiliClassData` và bản sao lưu của giáo viên.
Cache runtime/giọng đang dùng trên C cũng được giữ; không chuyển mã nguồn
sang C. ZIP/model/báo cáo và bản dựng tiếp tục nằm ngoài Git.

Dọn các thư mục trung gian PyInstaller/C# đã hoàn tất; cache tải gói
pip/npm/uv; bốn cache dependency nguồn cũ có metadata xác nhận thuộc dự án.
Không xóa phiên đăng nhập, Downloads hoặc file PowerPoint của giáo viên.
Số dung lượng thu hồi đo bằng dung lượng trống thực tế của ổ đĩa; không
cộng kích thước biểu kiến của các bản hardlink thành dung lượng đã dọn.

Sau dọn, pipeline nguồn với dữ liệu thử riêng đạt: DOCX/PPTX, mẫu bài,
SQLite/lịch sử/gói bài, WAV Anh và Việt ngoại tuyến, tốc độ/cache,
tiến trình lớp học và sao lưu/khôi phục. Qt mở Cài đặt thành công,
không cảnh báo QML. Các báo cáo cục bộ nằm tại `reports/rc164/cleanup`.
