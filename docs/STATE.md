# Trạng thái BiliClass

Ngày 04/10/2026 — sau phản hồi lỗi **400 Invalid content type** và chưa đăng nhập được, tách bước đăng nhập sang Chrome thường với hồ sơ riêng, chưa gắn Playwright/DevTools. Nút chính đổi thành **Kiểm tra và lưu**; sau xác nhận hoặc đóng Chrome, mở lại cùng hồ sơ và xác nhận phiên trước khi lưu. Nhận diện lỗi 400 riêng, gỡ trạng thái sẵn sàng và giữ dữ liệu hồ sơ. 54 kiểm thử browser/Chrome/handoff, smoke Qt web/Office và đăng nhập OAuth cũ đã qua; ca Chrome thường thật chỉ dùng cookie fixture trên localhost. Lần chờ đăng nhập thật chưa có xác nhận trước khi hết thời gian, **chưa kết nối được tài khoản thật và chưa chứng minh khắc phục lỗi web**. Xem [Browser AI](BROWSER_AI.md). Chưa phát hành bộ cài mới.

Ngày 04/10/2026 — chuyển Browser AI sang **Chrome riêng** theo yêu cầu. Bỏ việc luôn ép hồ sơ về Edge; giữ hồ sơ cũ và yêu cầu đăng nhập lại một lần. Mở Chrome cài trên máy qua DevTools cục bộ; tác vụ thu nhỏ dùng cùng chế độ browser với đăng nhập. Chỉ đánh dấu kết nối sau khi đóng/mở lại Chrome và xác nhận phiên đã lưu; không tự đóng xác minh sau một phút. 47 kiểm thử browser/Chrome/handoff và smoke Qt/Office đã qua; dữ liệu đăng nhập và AI là fixture. Chưa xác nhận tài khoản ChatGPT thật. Bằng chứng và giới hạn ghi trong [Browser AI](BROWSER_AI.md). Đây là mã nguồn mới; bộ cài RC12 chưa bao gồm.
Đợt ổn định Browser AI ngày 04/10/2026: browser chạy trên máy và lưu hồ sơ Free/Plus, không thêm API key hay dịch vụ browser trả phí. Giữ tài khoản mới chưa đăng nhập được để mở lại đúng hồ sơ; gỡ trạng thái sẵn sàng khi phiên hết hạn/cần xác minh. Nút **Đăng nhập và tiếp tục** nối lại đúng bài/tài khoản sau khi xác nhận đăng nhập; giữ bước phục hồi qua lần mở tool. Tránh nhận PPTX từ câu trả lời cũ, nhầm nội dung bài về giới hạn với quota, hoặc gửi prompt bị mất trong lúc tải tệp. 38 kiểm thử browser/handoff và smoke Qt web/Office, Qt OAuth cũ đã qua với fixture. Chưa xác nhận đăng nhập/chuyển đổi bằng tài khoản ChatGPT thật. Xem [Browser AI](BROWSER_AI.md).

Thử thật ngày 04/10/2026: xác minh Cloudflare bị lặp cả trong browser riêng của tool và browser thường theo phản hồi người dùng; chưa kết nối được. Đã bổ sung nhận diện, thông báo và dừng trang xác minh bị kẹt sau một phút, lưu lỗi và lựa chọn gửi/nhận thủ công. 21 kiểm thử browser và Qt/Office fixture qua; chưa chứng minh khắc phục được chặn thực tế. Không suy đoán nguyên nhân là Free/Plus. Cần kiểm tra truy cập bình thường trên mạng khác trước khi thử lại tích hợp.

Ngày 04/10/2026: Browser AI mặc định dùng phiên web Free/Plus, mỗi tài khoản một hồ sơ Edge. Có thêm/xóa, ưu tiên Plus cho bài mới, cố định Free để kiểm thử, giữ tài khoản cho bài đã gửi. Nhận PPTX, chuẩn bị âm thanh nháp và xem trước; không tự duyệt. Đã qua kiểm thử browser và Qt/Office với web/AI giả lập; chưa xác nhận tài khoản thật đăng nhập/chuyển đổi được. Luồng OAuth cũ và dữ liệu được giữ riêng. Xem [Browser AI](BROWSER_AI.md). Release RC12 chưa có thay đổi này.

Mã nguồn ngày 03/10/2026 có luồng **tài liệu → level → Chuyển đổi → xem trình chiếu → Dùng để dạy**. App tự đánh giá đầu vào, giữ cặp có sẵn, bổ sung phần thiếu và tạo PPTX; thầy cô xác nhận toàn bài một lần. Các tùy chọn bố cục, dịch từng đoạn, trợ giảng và quiz nằm trong phần mở rộng. Đã qua 178 kiểm thử, Ruff và Qt với model/PowerPoint thật; OCR vẫn sai một số dấu cần sửa. Xem [quy trình hiện tại](INPUT_WORKFLOW.md) và [thiết kế chuyển đổi nhanh](QUICK_CONVERSION.md). Các mục RC12 bên dưới mô tả bản đóng gói cũ, chưa bao gồm những thay đổi này.

Cập nhật: 02/10/2026. Mã nguồn: **1.0.0rc12**; bản đóng gói mới cần kiểm thử riêng. Trọng tâm: chuẩn bị và dạy song ngữ Anh–Việt cho nhiều môn THPT, khối 10–12 và môn tự tạo. Các bài trong ảnh chỉ là ví dụ.

## Đã triển khai trong ứng dụng

- M1: Qt/QML, SQLite v2/WAL, migration có backup, settings, log xoay vòng, tác vụ nền/hủy, thư viện cá nhân và sao lưu tự động hằng ngày.
- M2: PPTX/DOCX/PDF text/TXT, nhóm shape, vị trí nguồn, nguồn bất biến theo hash, biên tập/duyệt hai cột, metadata, tách đoạn, tự lưu 1,8 giây, 30 revision, khôi phục; Lesson Pack schema 3 có nguồn, trợ giảng, quiz và âm thanh portable.
- M3: dịch CPU hai chiều offline; thuật ngữ có phạm vi môn; memory đã duyệt và gợi ý gần giống do giáo viên chọn; bảo vệ số/biểu thức/thuật ngữ; cảnh báo trước duyệt; 24 tổ hợp level/layout. Bản dịch luôn là nháp.
- M4: nội dung trợ giảng do giáo viên chuẩn bị và duyệt; bàn điều khiển, cửa sổ lớp riêng, VI Rescue, Kokoro English offline/cache và SAPI Việt khi có, PowerPoint companion theo slide và điều khiển thủ công; Milo/Lumi với bốn tư thế, trợ giảng nổi và tùy chỉnh hiển thị.
- M5: tiến trình lớp học riêng, QR/LAN, trang học sinh, ẩn danh/số chỗ, một đáp án/đúng-sai/khảo sát, deadline, ACK, chống gửi trùng, đổi đáp án, reconnect và mã khôi phục; đáp án chỉ công bố sau đóng câu.
- M6: lịch sử phiên, tỷ lệ có mẫu số, chủ đề, gợi ý hiểu nhầm, recheck tách lượt, so sánh ngôn ngữ có điều kiện, gợi ý level để giáo viên quyết định; CSV tổng hợp/từng phản hồi và xóa phiên đã kết thúc.
- M7: OCR Windows chạy trong tiến trình cách ly, ảnh/PDF scan có giới hạn và báo thiếu ngôn ngữ; xuất deck song ngữ mới; asset mascot, nhãn môn dự phòng, hướng dẫn F1.
- M8 phần phần mềm: build Windows độc lập, bộ cài theo tài khoản với checksum, gói dịch cài từ máy/USB, thu thập giấy phép, hướng dẫn sử dụng và bộ kiểm tra tích hợp.

RC12 thêm cập nhật tự động từ GitHub Releases, tải gói có checksum, cài phiên bản mới cạnh phiên bản cũ và giữ thư viện bài học. Các thay đổi nền tảng của RC11 vẫn gồm tách nhiều ý trong một slide PowerPoint để duyệt, xuất VI/EN cùng trang và ảnh thường, chốt bản chuẩn bị theo revision, chọn bài ở Lớp học, nối báo cáo với bài gốc. Mẫu bài vẫn ở mức đầu tiên; chưa tái tạo đầy đủ bố cục/hiệu ứng của PowerPoint nguồn.

## Bằng chứng và giới hạn

Các kết quả hiện hành lưu trong `APP_RESULTS.md` và `reports/app/`; `TASKS.md` tách phần đã có mã nguồn khỏi nghiệm thu thực địa chưa làm. RC2 khôi phục phiên lớp khi cổng cũ bị chiếm bằng QR mới, giữ câu trả lời và danh tính. RC3 chia Cài đặt thành sáu tab. RC4 lưu nhiều môn và logo trong hồ sơ chung; môn, khối, level L0–L4 và một trong bốn kiểu trình bày được chọn cho từng bài, tên lớp cho từng tiết. RC5 sắp lại chỗ tải logo và xem trước hồ sơ đã lưu. RC6 thêm năm giọng Kokoro English offline. RC7 bổ sung bản xem trước Mascot theo ngữ cảnh và tùy chọn hiện riêng khi giải thích/quiz. Bài L5 cũ vẫn mở được. Các giá trị lớp/level toàn cục cũ không áp cho bài mới.

Máy hiện tại có PowerPoint 16, năm giọng Kokoro English chạy CPU offline và Windows OCR en-US; chưa có giọng/OCR Việt qua các backend này. App báo đúng khả năng và vẫn cho biên tập/dạy bằng chữ.

Model dịch không phải model sinh giáo án: giải thích/ví dụ/câu hỏi cần chuẩn bị và duyệt. Công thức Office dạng đối tượng, video, biểu đồ và bố cục gốc không được tái tạo bằng text importer; có cảnh báo và bản nguồn để đối chiếu. PowerPoint gốc phụ trách trình chiếu nội dung Office. Deck xuất là deck mới theo mẫu.

## Nghiệm thu còn cần môi trường thật

1. Cài/nâng cấp/gỡ trên Windows sạch không Python; kiểm tra dependency với máy khác.
2. Android/iPhone, ít nhất năm điện thoại và tải lớp mục tiêu trên Wi‑Fi/router/hotspot trường, không Internet.
3. Máy chiếu, DPI, Extend/Duplicate, Presenter View và animation/video trong tài liệu dạy thật.
4. Giáo viên nhiều nhóm môn chấm bản dịch/thuật ngữ và thử trọn tiết; ghi thời gian chuẩn bị, sửa dịch và thao tác.
5. Đánh giá giọng/OCR Việt khi máy được cài thành phần ngôn ngữ phù hợp.

RC12 là bản thử nội bộ cần hai giáo viên kiểm tra thêm. Phiếu thao tác/bằng chứng cho các bước còn mở ở `FIELD_ACCEPTANCE.md`. **Chưa đánh dấu toàn bộ M0/M4/M5/M8 nghiệm thu hoàn tất**, vì kiểm tra trên máy phát triển không thay thế các bước trên. Không cần dịch vụ cloud hoặc tài khoản học sinh để thử chức năng hiện có.
