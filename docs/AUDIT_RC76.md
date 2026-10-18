# RC76 — Rà soát toàn hệ thống và ổn định phiên dạy

Ngày 18/10/2026. Tiếp tục các thay đổi RC73–75 theo yêu cầu giáo viên.
Phạm vi: chuyển đổi/nhập bài, lời đọc, xuất PPTX, thư viện, dữ liệu,
PowerPoint/Mascot, lớp học, cấu hình và đóng gói. Kiểm tra kỹ thuật không
chứng nhận mọi bản dịch, bố cục hoặc phát âm của bài giáo viên.

## Lỗi và điểm nghẽn đã xử lý

- Lệnh media trước đây dùng tên ngôn ngữ, được xử lý trước khi Office đọc
  slide hiện tại. RC76 gửi cả SlideID và mã lượt đọc; helper cập nhật player
  theo slide thực trước khi phát/tạm dừng/tiếp tục. Lệnh từ slide cũ bị từ
  chối; phản hồi cũ không khởi động lại lời đọc sau khi người dùng đã dừng.
- Khi XML có loa nhưng Office không trả được player, bản cũ có thể đứng ở
  “Đang chuẩn bị”. Nay luôn trả kết quả lỗi. Nếu đúng lời/giọng/tốc độ đã có
  WAV hợp lệ, Mascot dừng media native rồi dùng cache; không tổng hợp giọng
  mới trong giờ dạy. Thiếu cả cache thì hiện lỗi rõ. Giữ ý định tạm dừng nếu
  người dùng bấm lần hai khi player đang chuẩn bị.
- Đối chiếu tên file đầy đủ khi tìm cửa sổ slideshow/Presenter View. Không
  gắn `Lesson.pptx` vào `Lesson extra.pptx`; khi trùng tên mơ hồ, không tự
  chọn một cửa sổ. Callback chuột/phím đọc một snapshot bất biến gồm cửa sổ,
  SlideID và vùng loa, tránh trộn hai slide khi đổi ngữ cảnh.
- Chuyển hiệu ứng trong cùng slide không làm mất trạng thái đọc toàn slide.
  Phạm vi “phần đang hiện” vẫn bỏ lượt đọc cũ khi hiệu ứng thay đổi.
- Lỗi SQLite khi lưu phím được báo trên giao diện; giữ cấu hình trước đó
  và không gửi cấu hình chưa lưu đến phiên PowerPoint.
- Hook chờ thông điệp Windows thay cho vòng thức mỗi 8 ms. Mười lượt đo
  mỗi phiên bản, mỗi lượt 0,6 giây với hook thật nhưng không gắn cửa sổ:
  trung bình 60,60 → 17,21 lần chờ/giây; đóng chậm nhất 61,81 ms ở bản mới.
  Độ phân giải CPU đo được là 0 ở cả hai; không suy ra phần trăm giảm CPU,
  pin hoặc độ trễ phím trong lớp. Chứng cứ: `reports/rc76/hook-lifecycle.json`.
- Helper Office theo dõi tiến trình ứng dụng mẹ. Khi ứng dụng thoát đột
  ngột, helper kết thúc hook và đóng riêng bài chỉ đọc do nó mở. Thử crash
  parent thật đạt: helper thoát sau 0,328 giây, nguồn không đổi. Không kết
  thúc tiến trình Office của giáo viên. Script tái lập:
  `scripts/verify_teaching_parent_exit.py`; báo cáo tại
  `reports/rc76/teaching-parent-exit.json`.
- Bộ kiểm tra nguồn và bộ cài dùng nền Windows cho UI trên Windows.
  Offscreen không chỉ thiếu HWND/hộp thoại native: lượt dựng ảnh đã cho chữ
  thành ô vuông, làm sai kích thước và phép kiểm căn giữa sidebar. Cùng mã
  UI chạy lại nền Windows hiển thị đúng font và đạt. Không sửa UI hoặc nới
  assert để che sai khác này. Luôn ghi kết quả từng đợt cả khi thất bại,
  gồm bước lỗi và các bước đã đạt; `-IntegrationOnly` ghi rõ phạm vi khi chỉ
  chạy lại Qt/Office, không giả là đã chạy lại pytest.
- Phép thử Trang chủ chụp frame đã resize trước khi đo hình học. Bản thử
  không render có thể đo layout cũ khi cửa sổ bị che; giữ nguyên điều kiện
  các bước quy trình phải hiện trong màn hình ở 1080/1366/1680.

## Kiểm chứng

Lượt nền trước sửa: 883 core + 104 Browser AI + 14 Browser Translation đạt.
Phép thử lưu file thất bại khi ép offscreen: không có hộp thoại Win32 để
đọc. Đây là sai môi trường thử, không phải bằng chứng ô tên file bị trống.
Lượt core cuối 898 ca đạt; nhóm Browser AI 104 và Browser Translation 14
đạt, tổng 1.016 ca. Nhóm 44 ca liên quan media/binding/phím cũng đạt.
Có một `StarletteDeprecationWarning` về httpx của dependency
test; chưa đổi runtime trong mốc này. Không có lỗi từ warning đó.
11 luồng Qt chạy nền Windows đạt, không cảnh báo QML: chuyển đổi, workspace
giọng, hộp thoại lưu native, kết quả/xem trước/mascot, dữ liệu/giọng, Trang
chủ, Thư viện, phiên dạy, cấu hình phím, lớp học và độ đáp ứng chuyển đổi.
Phiên dạy xác minh cả lệnh phát bị trễ sau khi chuyển slide thật, mở F5,
pause/resume, đổi bài và bảo toàn nguồn. Input bàn phím/chuột thật có giới
hạn riêng ở dưới.

8 bài corpus tự tạo, 9 slide đầu ra, render/đo bằng Office: nguồn và media
được giữ, không còn FAIL kỹ thuật trong các fixture. CHECK về hình/hiệu ứng,
notes và chữ nhỏ vẫn giữ để người xem đánh giá. Lượt parent-exit tích hợp
cuối đạt 0,359 giây. Kết quả tích hợp:
`reports/verification/20261018-213805/result.json`; core cuối:
`reports/rc76-final-core.log`; hai nhóm browser ở
`reports/verification/20261018-212035/`. Reports và corpus không ở Git.

Lệnh kiểm đầy đủ: `scripts/verify_source.ps1 -Qt -Office` với Python của
`.venv`. Khi chỉ kiểm tích hợp: thêm `-IntegrationOnly`, dùng kết quả core
và browser đã ghi riêng; không cộng số ca lặp thành ca kiểm thử mới.

Thử bấm Space qua Computer Use vào slideshow mẫu bị Windows trả
`GetCursorPos failed: Access is denied (0x80070005)`; không phát sinh sự kiện
đọc hoặc đổi slide. Dừng thao tác desktop và đóng fixture qua harness. Không
ghi phần phím/chuột thật RC76 là đạt; chứng cứ input thật RC74 là lịch sử,
không thay thế lượt xác minh này. Không thay đổi bảo mật Windows để thử lại.

Chạy 60 phút với Qt thật, nền offscreen/software, 120 bài tổng hợp, 7.199
lượt chuyển qua năm trang và refresh catalog định kỳ: không cảnh báo QML;
UI gap lớn nhất 234 ms, p95 cuối 32 ms. Sau warmup, handle ổn định 365;
thread về 21. Đây là workload điều hướng/catalog trên source trước RC76,
không bao gồm Office, suy luận TTS hoặc Wi-Fi. Không gọi đây là kiểm thử
60 phút toàn bộ tác vụ RC76. Báo cáo: `reports/rc76/long-session.json`.

Lớp học: 50 client loopback, đủ 50 câu trả lời; gửi trùng/nối lại không nhân
phản hồi; 35/50 đúng, báo cáo 70%; khởi động lại giữ phiên. P95 xác nhận
558,2 ms, max 565 ms khi chạy cùng các bài thử khác; không dùng làm benchmark
so sánh hoặc kết quả Wi-Fi trường. Báo cáo: `reports/app/classroom-load.json`.

## Phần còn cần thiết bị/người đánh giá

1. 30–50 điện thoại trên Wi-Fi trường, máy chiếu Extend/Duplicate và rút/cắm
   màn hình. Loopback và cửa sổ native hiện tại không thay thế được các ca này.
2. Windows/Office sạch và máy ít RAM: cài/cập nhật/gỡ, model offline, phiên dài.
3. Nghe sáu giọng, kiểm nghĩa/thuật ngữ, công thức, ảnh và bố cục bài thật.
4. PPTX có nhiều PCM và loa chung có thể lớn; chưa đổi codec hoặc giảm chất
   lượng âm thanh. Toggle/phím gán lại cần phiên gắn Mascot; PPTX mở độc lập
   vẫn theo player PowerPoint native, như giới hạn đã ghi ở RC74.
5. Quyền truy cập kho nguồn/kênh phát hành đang khác mô tả “private” trong
   quy ước. Không đổi visibility hoặc phát hành công khai trong đợt này.

Quy trình nghiệm thu thiết bị: [ACCEPTANCE_FIELD](ACCEPTANCE_FIELD.md).
Không bỏ cảnh báo chất lượng hoặc tự duyệt bài để làm kết quả trông đạt.

## Gói RC76 đã xác minh sau audit

Đã build từ source `a5fb229ad07825a60e86b7bf8a39f3f542b0efb6`, tái dùng
runtime RC75 đã kiểm manifest, biên dịch lại toàn bộ module ứng dụng.
ZIP 871.096.996 byte, SHA-256
`4f76cd2c09410d0d1bae76351d6b08711a617d58afec490d12942f7894100a20`.
Cài vào vùng Unicode riêng, Qt Windows, VieNeu Anh/Việt thật ngoại tuyến,
template, lớp học/backup và gỡ giữ thư viện đều đạt. Chứng cứ:
`reports/release/1.0.0rc76-761e19c4/installer.json`. Không thay bộ cài chính
hoặc phát hành Release RC76; các yêu cầu loa mới tiếp tục ở RC77.
