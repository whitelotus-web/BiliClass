# Kiểm chứng BiliClass 1.0 RC10

Ngày 01/10/2026, máy Windows phát triển hiện tại. Tất cả thư viện dùng trong kiểm tra được tạo riêng, không ghi bài thử vào thư viện người dùng. Kết quả không phải chứng nhận máy giáo viên/mạng trường.

## Kết quả hiện hành

| Phần | Kết quả | Bằng chứng |
|---|---|---|
| Unit/integration | 117 passed; một cảnh báo chuyển đổi API Starlette/httpx, không test thất bại | `.venv/Scripts/python.exe -m pytest -q`, `tests/` |
| Kiểm tra mã | Ruff không lỗi | `python -m ruff check app biliclass_m0 scripts tests` |
| Workflow soạn bài Qt | 12 bước passed, không QML warning, cửa sổ 1366×768 | `reports/app/ui-workflow.json` |
| Workflow dạy/lớp Qt | 9 nhóm passed, không QML warning | `reports/app/v1-ui.json` |
| Bản RC2 `.exe` | 7 nhóm pipeline passed, exit 0 | `reports/app/rc2-frozen-pipeline.json` |
| Bộ cài RC1 (mốc trước) | Cài trong đường dẫn Unicode, mở khi chưa có model, cài hai model thật từ file, chạy pipeline và gỡ giữ dữ liệu | `reports/app/installer.json`, `installed-v1-pipeline.json` |
| Đa môn | 5 fixture khối 10–12/môn tự tạo, pack roundtrip; 100 lượt model, p95 0,394 giây, không cảnh báo số/ký hiệu trên fixture | `reports/app/multisubject.json` |
| Lớp học tải | 50 WebSocket đồng thời; gửi trùng/reconnect; 35/50 đúng = 70%; stop/resume giữ dữ liệu/cổng | `reports/app/classroom-load.json` |
| ACK trên loopback | p95 182,2 ms; max 191,5 ms trong phép thử nêu trên | `reports/app/classroom-load.json` |
| PowerPoint thật | 3 slide, tiến/nhảy/lùi, đóng tài nguyên sở hữu; SHA nguồn không đổi | `reports/app/powerpoint-companion.json` |
| OCR native | PNG và PDF scan English có số/đơn vị nhận dạng được; en-US là ngôn ngữ có sẵn | `reports/app/ocr.json` |
| Cổng lớp bị chiếm | Tự lấy cổng mới, báo QR mới; danh tính/chỗ ngồi/đáp án B còn nguyên, chưa lộ đáp án đúng | `reports/app/classroom-rebind.json` |
| Hai màn hình | Projector fullscreen trên màn hình Samsung phụ; không cảnh báo QML | `reports/app/displays.json`, `projector-secondary.png` |
| Phóng 125% | Editor hiện đủ nội dung trên máy hiện tại, không cảnh báo QML | `reports/app/editor-dpi125.json`, `editor-dpi125.png` |
| Nâng cấp RC1→RC2 | Cài cạnh bản cũ, mở RC2, giữ bài sau nâng cấp và sau gỡ | `reports/app/upgrade.json`, `upgraded-settings.png` |
| Giao diện RC2 đóng gói | Editor 1366×768 lưu ảnh, không cảnh báo QML | `reports/app/rc2-frozen-editor.json`, `rc2-frozen-editor.png` |
| Sáu tab Cài đặt RC5 | 8 nhóm thao tác Qt: ô logo trước nút Lưu, preview chỉ đọc hồ sơ đã lưu; nhiều môn, giọng đọc, mascot ẩn/hiện/cỡ/trái-phải ở các cửa sổ, lớp, sao lưu và tạo bài; không cảnh báo QML | `reports/app/settings-ui.json`, `settings-*.png` |
| Bản RC3 `.exe` | 7 nhóm pipeline passed, exit 0; màn Cài đặt đóng gói hiện đúng ở 1366×850, không cảnh báo QML | `reports/app/rc3-frozen-pipeline.json`, `rc3-frozen-settings.json`, `rc3-frozen-settings.png` |
| Bộ cài RC3 | Kiểm checksum, cài và mở màn Cài đặt; gỡ vẫn giữ thư viện thử | `reports/app/rc3-installer.json`, `rc3-installed-settings.png` |
| Bốn bố cục RC4 | 48 kiểm tra riêng cho policy/deck và các phần liên quan; logo có trong deck và bản sao lưu | `tests/test_v1_policies.py`, `tests/test_prepared_content.py` |
| Bản RC4 `.exe` | 7 nhóm pipeline passed, exit 0; màn Cài đặt 1366×850 hiển thị đúng chữ Việt khi thư viện thử có bài | `reports/app/rc4-frozen-pipeline.json`, `rc4-frozen-settings-ready.png` |
| Bộ cài RC4 | Manifest kiểm hash 2.388 tệp, cài vào thư mục Unicode riêng, mở màn Cài đặt; gỡ giữ thư viện thử | `reports/app/rc4-installer.json`, `rc4-installed-settings.png` |
| Bản RC5 `.exe` | 7 nhóm pipeline passed, exit 0; ảnh Cài đặt 1366×850 hiện form và preview cùng lúc; thử thêm 1080×700 ở mã nguồn | `reports/app/rc5-frozen-pipeline.json`, `rc5-frozen-settings.png`, `rc5-settings-1080-source.png` |
| Bộ cài RC5 | Manifest kiểm hash 2.388 tệp, cài vào thư mục Unicode riêng, mở màn Cài đặt; gỡ giữ thư viện thử | `reports/app/rc5-installer.json`, `rc5-installed-settings.png` |
| Kokoro RC6 | Năm giọng English tổng hợp WAV khi chặn socket mạng; kiểm tra cache và thời gian nạp trên máy này | `reports/app/kokoro-samples/`, `tests/test_speech_readiness.py` |
| Cài đặt Giọng đọc RC6 | Năm lựa chọn, nghe thử từng giọng, đổi giọng độc lập với Mascot; không cảnh báo QML | `reports/app/settings-voice.png`, `reports/app/settings-ui.json` |
| Bản RC6 `.exe` | 7 nhóm pipeline passed, bao gồm tạo âm thanh Kokoro offline và dùng cache; giao diện Cài đặt chụp ở 1366×850 | `reports/app/rc6-frozen-pipeline-final.json`, `rc6-frozen-settings-final.png` |
| Bộ cài RC6 | Manifest kiểm SHA-256 cho 2.786 tệp gồm model/voices/eSpeak Kokoro; cài thành công vào thư mục Unicode riêng. Bản đã cài qua đủ 7 nhóm pipeline khi nạp hai gói dịch rời; đã gỡ bản cài thử, dữ liệu thử giữ riêng. | `reports/app/rc6-installed-pipeline-with-translation.json`, `dist/_old_releases/rc6/app-manifest.json` |
| Mascot RC7 | Hai thẻ vai trò và bản xem trước theo slide/giải thích/quiz; cấu hình bối cảnh, vị trí, cỡ và nhãn môn áp dụng tới màn dạy. Luồng Qt 8 nhóm passed, ảnh 1366×850 và 1080×700, không cảnh báo QML. | `reports/app/settings-ui.json`, `settings-mascot-top.png`, `settings-mascot-compact-preview.png` |
| Bản RC7 `.exe` | 7 nhóm pipeline passed gồm Kokoro offline; manifest bộ cài chứa 2.786 tệp. | `reports/app/rc7-frozen-pipeline.json`, `dist/_old_releases/rc7/app-manifest.json` |
| RC8 giọng đọc Việt–Anh | Bốn preset VieNeu tiếng Việt và năm Kokoro English; bản đóng gói tổng hợp WAV offline, đổi tốc độ và dùng lại cache. | `reports/app/rc8-frozen-pipeline-final.json`, `reports/app/vieneu-samples/` |
| RC8 icon và mascot | 10 icon do người dùng cung cấp ở điều hướng/Cài đặt; lưu cấu hình mở hoặc ẩn trợ giảng nổi ngay, có nút mở lại; kiểm tra Qt và ảnh từ bản đóng gói. | `reports/app/navigation-mascot.png`, `reports/app/rc8-frozen-settings-final.png` |
| Bản RC8 `.exe` | 8 nhóm pipeline passed; manifest 4.804 tệp gồm giọng Việt, giọng Anh và model; 118 bài kiểm tra mã nguồn passed. | `reports/app/rc8-frozen-pipeline-final.json`, `dist/_old_releases/rc8/app-manifest.json` |
| Icon thao tác RC9 | 19 icon người dùng cung cấp được đóng kèm; gán cho các nút phù hợp ở soạn bài, thuật ngữ, Cài đặt, lớp học và báo cáo, giữ nhãn chữ. Các luồng Qt soạn bài 12 bước, lớp học 9 nhóm và Cài đặt 8 nhóm đều passed, không cảnh báo QML. | `reports/app/ui-workflow.json`, `reports/app/v1-ui.json`, `reports/app/settings-ui.json`, `reports/app/rc9-frozen-settings.png` |
| Bản RC9 `.exe` | 8 nhóm pipeline passed gồm dịch hai chiều, tạo WAV English/Kokoro và Việt/VieNeu offline, lớp học và OCR; manifest SHA-256 cho 4.823 tệp gồm 19 icon thao tác. Bộ test mã nguồn: 118 passed; Ruff không lỗi. | `reports/app/rc9-frozen-pipeline.json`, `dist/_old_releases/rc9/app-manifest.json` |
| Mascot nổi RC10 | Cửa sổ khi thu gọn chỉ rộng bằng nhân vật, góc ảnh có alpha bằng 0; nhấp mascot mở/thu bảng nút, bấm English hiển thị phản hồi. Luồng Qt soạn bài 12 bước, Cài đặt 8 nhóm và dạy/lớp 9 nhóm passed; không cảnh báo QML. | `reports/app/mascot-floating.png`, `reports/app/mascot-menu.png`, `reports/app/mascot-menu-response.png`, `scripts/verify_navigation_mascot.py` |
| Bản RC10 `.exe` | 8 nhóm pipeline passed gồm dịch hai chiều, Kokoro/VieNeu offline, lớp học và OCR; ảnh Cài đặt hiển thị đúng, QML mascot trong gói đã qua thử nhấp mở/thu và phản hồi. Manifest SHA-256 có 4.823 tệp. | `reports/app/rc10-frozen-pipeline.json`, `reports/app/rc10-frozen-settings.png`, `dist/rc10/app-manifest.json` |

Thống kê hiệu năng chỉ áp dụng fixture ngắn và máy hiện tại. Không dùng 100 lần sinh được đầu ra để kết luận bản dịch đúng ngữ nghĩa/sư phạm. Giáo viên cần đánh giá nhiều môn thật.

## Phạm vi workflow

12 bước soạn bài gồm tạo môn tự chọn, nhập đúng khối/nguồn, giữ chỉnh sửa khi rời màn hình, duyệt riêng, dịch hai chiều bằng model thật, khóa editor khi job, tạo/cache WAV SAPI, mở preview, pack/persistence, autosave giữ caret, history restore, memory duyệt cùng môn/mâu thuẫn và hủy tác vụ muộn. Test chờ trạng thái popup thay vì đoán thời gian; onboarding mở sau khi QML dựng xong, tránh timer mở muộn che thao tác.

9 nhóm dạy/lớp gồm biên soạn/duyệt trợ giảng và câu hỏi, truy xuất đúng nội dung, bàn điều khiển, projector, mascot nổi, start server/join, vòng đời câu và báo cáo lưu lại. Hai cửa sổ teacher/projector tách dữ liệu; đây chưa phải thử máy chiếu thực địa.

Pipeline RC2 `.exe` kiểm tra DOCX/PPTX; hai model; SQLite/history/pack; WAV/cache; tiến trình classroom thật và student page/WebSocket ACK/báo cáo; xuất deck/backup restore; OCR tiến trình con. Đã sửa cấu hình Uvicorn formatter không có stdout trong ứng dụng windowed. Native runtime WinRT/PDFium và DLL cần thiết được đóng kèm; không sửa DLL hệ thống.

Browser Playwright đã kiểm tra giao diện 390×844: vào lớp, chọn và đổi đáp án, mất mạng khóa lựa chọn, trở lại giữ lựa chọn đã ACK, đóng câu chưa lộ đáp án và chỉ hiển thị kết quả sau công bố. Ảnh ở `output/playwright/`. Không đồng nhất Chromium giả lập kích thước mobile với iPhone/Android thật.

Mã khôi phục đã thử thêm trong một browser context mới, không có sessionStorage cũ: nhập mã lấy lại đúng danh tính và lựa chọn B đã lưu, chưa hiển thị đáp án đúng. Kết quả `reports/app/browser-recovery.json`, ảnh `output/playwright/student-recovered.png`.

Ảnh RC1 đóng gói `frozen-editor-v1.png` và `frozen-onboarding-v1.png` ở 1366×768 hiển thị đúng chữ Việt–Anh và không có QML warning. RC2 có ảnh editor mới trong bảng trên. Bản hướng dẫn mở sau khi dựng xong cửa sổ, đã kiểm tra đóng hướng dẫn rồi tạo/duyệt bài qua workflow Qt.

## Các kiểm tra dữ liệu quan trọng

- Nguồn bất biến/hash, migration v1→v2 và backup, revision conflict, review/lock, tách đoạn Unicode/UTF-16 và invalidation nội dung liên quan.
- 24 tổ hợp level/layout; thiếu easy English báo fallback; không dùng nội dung chưa duyệt để dạy.
- Pack v1/v2/v3, checksum/path/symlink/quota/ID mapping; audio khớp văn bản và chuyển máy thiếu voice; restore chỉ vào thư mục mới.
- Student không có endpoint admin; snapshot chưa reveal không có đáp án/rationale/misconception; không tin participant ID tự gửi.
- Submission idempotency, trùng mã khác payload bị từ chối, đổi đáp án không tăng mẫu số, deadline, poll không điểm, recheck không ghi đè baseline.
- Báo cáo ít mẫu và so sánh ngôn ngữ có điều kiện; CSV chống công thức, không xuất token; xóa phiên có FK cascade.
- Gói model kiểm tra hash/đường dẫn/loại dữ liệu/provenance, không ghi đè model đã cài.

## Chưa nghiệm thu

Windows sạch/nâng cấp trên máy khác; DPI và accessibility bàn phím toàn diện; máy chiếu/Presenter View/video/animation tài liệu thật; điện thoại và Wi-Fi đổi IP/port bận trên router; mất điện thực tế; giọng/OCR Việt; cảm nhận âm thanh qua loa; RAM/khởi động trên laptop mục tiêu; tiết học không Internet và giáo viên chấm dịch. Các mục này còn mở trong `TASKS.md`.

Các báo cáo `*-v03`, `packaged-pipeline.json` và số liệu M0 là lịch sử; RC2/RC3 dùng tên báo cáo riêng trong bảng trên. Không lấy kết quả offscreen font ô vuông trước đây làm bằng chứng hiển thị đạt.
