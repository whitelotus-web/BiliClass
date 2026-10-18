# Triển khai kế hoạch hoàn thiện sau RC72

Yêu cầu ngày 18/10/2026: triển khai toàn bộ kế hoạch, kiểm chứng từng phần,
đồng bộ mã nguồn và mở ứng dụng. Tài liệu này theo dõi việc thực hiện;
mục chưa có bằng chứng không được coi là hoàn tất.

## Danh sách triển khai

- [x] Sao lưu ZIP64 lớn, đọc gói cũ quá 2 GiB, giới hạn tài nguyên/dung lượng,
  trạng thái lỗi/thành công, ngân sách lưu, restore sang ổ khác và đổi đường dẫn.
- [x] Khôi phục chuyển thư viện có checkpoint bền và tiến độ xác minh lúc mở.
- [x] Bộ bài chuẩn sinh tại máy, giữ media/công thức/nội dung; phân biệt lỗi
  nguồn và lỗi chuyển đổi; sửa bố cục bằng vòng lặp hữu hạn và ảnh kiểm chứng.
- [x] Office render/đo/fit có tiến trình riêng, thời hạn, dừng, checkpoint từng slide.
- [x] Mô hình trạng thái dùng chung: đã lưu, cần kiểm tra, giọng cho X/Y đoạn,
  bản chuẩn bị hiện hành; tránh diễn đạt “đủ giọng” cho slide chưa có lời.
- [ ] Giao diện màn nhỏ, bàn phím/focus, cảnh báo mở đúng vị trí, giữ tab Cài đặt.
- [x] Lời đọc có lý do/độ tin cậy, slide cố ý không đọc, giữ chỉnh sửa thủ công,
  cache theo nội dung/giọng/tốc độ; bộ nghe VI/EN/mixed/công thức cho 6 giọng.
- [ ] Cache render qua ngày cho slide tĩnh; phiên chạy dài và đo nguội/nóng.
- [x] Chẩn đoán theo whitelist, không xuất dữ liệu riêng/key/token; phân nhóm lỗi.
- [x] Luồng lớp học/thiết bị/cài đặt có kịch bản nghiệm thu và công cụ đo thực tế.
- [x] Tách lifecycle/Job và thành phần giọng/QML, lint app/script/test sạch, lệnh kiểm chuẩn, CI.
- [x] Build/package/kiểm gói từ code đã commit; nguồn runtime/model có hash.
- [x] Kiểm source theo nhóm, Qt, bản cài và dữ liệu thật; commit/push; cài RC73.

## Bằng chứng đang có

- Sao lưu thư viện thật 8.040.765.784 byte và khôi phục 20 bài; gói cũ
  2.231.885.510 byte khôi phục 17 bài, SQLite integrity đạt. Kết quả tại
  `reports/rc73/large-backup.json`; dữ liệu giữ ngoài Git trên ổ F.
- Fixture kiểm hết ổ, checksum, đường dẫn, checkpoint, phục hồi chuyển dở,
  ngân sách lưu và giữ lần thành công cũ khi backup mới lỗi. Gói ngày đã bị
  thay đổi không được coi là một lần backup thành công mới.
- Qt giọng và chuyển đổi đã kiểm tại 1080×700, 1366×768, 1366×850,
  1920×1080. Tạo giọng/Dừng ở thanh cuối như Chuyển đổi; Dừng/Hủy có chữ,
  icon và màu đỏ; thay list giọng gây nhầm bằng diễn giải cấu hình.
- Yêu cầu mới nhất của người dùng thay mặc định lần đầu thành **Tiếng Anh**;
  lần sau nhớ lựa chọn gần nhất. Bỏ “Khuyên dùng” khỏi Việt + Anh. Bài chỉ
  có một ngôn ngữ vẫn điều chỉnh theo lời đang có, không tự dịch.
- Có popup dùng lại/tạo lại đúng cấu hình đã hoàn tất; tạo lại chỉ công bố
  WAV hợp lệ khi làm xong, dừng/lỗi giữ bản cũ. Chuyển đổi bị khóa lúc tạo
  giọng; Xem tiến độ về tab Giọng và giữ tác vụ hiện tại.
- Đã sinh/kiểm cấu trúc 8 deck tự tạo và bộ VI/EN/xen kẽ/công thức cho 6
  giọng. WAV đã có được dùng cache; kết quả sinh không chứng nhận phát âm.
  Bộ nghe tay: `reports/app/multilingual-voice/listening-review.html`.
- Native corpus render 9 slide đầu ra, không còn FAIL kỹ thuật; CHECK còn
  giữ nguyên cho phần cần đối chiếu. Tách lỗi nguồn (group có overflow)
  với đầu ra. Đã sửa số lượng có khoảng trắng/đơn vị bị lặp trong bảng và
  kiểm lại bằng 41 ca cùng render bảng thực.
- 972 tests đạt theo ba tiến trình; monolithic từng treo sau nhiều phiên
  Chrome, nên quy trình kiểm chuẩn tách core/browser AI/browser translation.
- Có công cụ dựng bản ứng viên từ cache dịch chỉ đọc; thiếu cache dừng trước
  key, quota và mạng. Đã dựng một ứng viên thật bằng 246 đơn vị cache, chưa
  thay bài đã lưu hoặc đánh dấu chất lượng đạt khi chưa kiểm native.
- Đã tách lifecycle/Job khỏi UI, thêm CI source giới hạn phạm vi portable,
  script kiểm chuẩn, build từ baseline có hash và hướng dẫn kênh phát hành.
  CI trên GitHub, corpus native, phiên dài, lint script/test và bản cài còn
  được cập nhật sau khi hoàn tất các vòng kiểm chứng đang chạy.

## Cập nhật luồng giọng / F5

- Tên tải gán trước khi mở dialog Windows, dùng tên bài và bản ngôn ngữ/voice
  trong ngoặc; chung quy tắc ở workspace, thư viện và file trong ZIP.
- Loa mặc định đọc toàn bộ lời đã lưu khi bấm. Bài thật 86 trang có 258 loa,
  phát VI/EN/chung ở năm trang (gồm trang trước thiếu loa) qua native player;
  ảnh F5 thấy loa. Mascot có lựa chọn đọc theo hiệu ứng, không sinh lại voice.
- Màn hoàn tất thu cấu hình, có xem slide/nghe cache, mở PowerPoint trực tiếp,
  tải PPTX/audio và về đúng bài trong thư viện; không tự duyệt nội dung.
- Native player cập nhật trạng thái mascot; nút dừng đỏ, nhận HWND dự phòng
  đúng phiên F5. Mẫu nghe thử dùng sample đóng gói, tránh suy luận sáu giọng.
- 862 core, 104 browser AI, 14 browser translation đạt theo nhóm; Qt giọng
  thêm 150% DPI. Lint script/test đã dọn riêng, giữ AST ở bước format.
- Phiên dài bị gián đoạn ở 49 phút, chưa hoàn tất mục 60 phút. Bản ứng viên
  khôi phục cũ vẫn 44 FAIL/26 CHECK sau native, không được thay bài đã lưu.
  Chi tiết và giới hạn xem [BUILD_RC73](BUILD_RC73.md).

RC73 từ `58ab0d2` đã qua CI, 8 trang EXE và self-test model/tiết học/backup
từ bản cài độc lập. Cài tại `F:/Applications/BiliClass/1.0.0rc73`, shortcut
đã cập nhật; dữ liệu giữ ở ổ F. Không biến các mục nghiệm thu ngoài máy,
phiên dài gián đoạn hoặc bài khôi phục còn FAIL thành trạng thái hoàn tất.

## Nghiệm thu ngoài máy hiện tại

Các thử nghiệm sau cần thiết bị/môi trường thật để kết luận: 30–50 điện thoại
trên Wi-Fi trường, máy chiếu Extend/Duplicate, Windows sạch và nghe chấm phát
âm/thuật ngữ bởi giáo viên. Chuẩn bị kịch bản và bộ đo trong đợt triển khai;
không thay các kết quả này bằng loopback, ảnh chụp hoặc WAV đã sinh.

Kho nguồn hiện công khai trong khi quy ước dự án mô tả kho riêng tư. Việc
tách kênh phát hành và quyền truy cập được chuẩn bị bằng cấu hình; chưa đổi
visibility hay tạo kho mới khi chưa chốt đích với chủ kho.
