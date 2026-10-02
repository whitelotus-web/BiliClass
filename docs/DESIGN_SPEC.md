# Quy chuẩn giao diện BiliClass

Phiên bản kế hoạch 29/09/2026. Đối tượng: giáo viên và học sinh THPT. Mục tiêu: dễ chuẩn bị, kiểm soát rõ nội dung Anh–Việt, thao tác ít khi đang dạy. Nội dung bài học trên chín ảnh chỉ minh họa bố cục.

## 1. Hướng thiết kế

Giữ nền sáng, navy đậm, xanh dương làm màu hành động, cam cho thương hiệu/Milo; Lumi nâu với phụ kiện navy. Mascot thân thiện nhưng không làm giao diện THPT giống trò chơi cho trẻ nhỏ. Giao diện soạn bài ưu tiên khả năng đọc và mật độ vừa phải; trình chiếu ưu tiên nhìn xa.

Điều hướng chính: Trang chủ, Bài học, Lớp học, Báo cáo, Cài đặt. Hồ sơ giáo viên là thiết lập local, không ngụ ý tài khoản cloud. Giao diện được chọn phải thống nhất logo; ưu tiên dấu sách mở xanh và chữ Bili navy/Class cam trong các ảnh màn hình.

## 2. Đối chiếu ảnh với màn hình cần xây

| Ảnh | Giữ lại | Điều chỉnh cho sản phẩm |
|---|---|---|
| 01 — Milo | Cáo cam, hoodie navy, thân thiện, bốn biểu cảm mẫu | Tạo asset nền trong riêng; thu gọn khi dạy; chữ nằm trong UI |
| 02 — Lumi | Rái cá nâu, khăn navy, bình tĩnh, phụ kiện nhẹ | Cùng hành động với Milo; giọng tách biệt; không trộn logo |
| 03 — Settings | Hai lựa chọn cạnh nhau, cỡ/vị trí/phụ kiện | Có đọc thử voice ở tab riêng, giảm chuyển động, auto-hide |
| 04 — Results | Chỉ số ngắn, thanh concept, gợi ý, CSV | Tỷ lệ có mẫu số, không đánh đồng điểm đúng với hiểu bài; thiếu dữ liệu có trạng thái riêng |
| 05 — Quiz | Teacher/projector tách rõ, số đã trả lời, phân bố đáp án | Projector/phone không lộ đúng/sai trước công bố; URL LAN thật; số liệu nhất quán |
| 06 — Presentation | Bài giảng lớn, thanh công cụ dưới, VI/EN rõ | Mascot mặc định nhỏ; không ghi đè bố cục PowerPoint; tách teacher-only controls |
| 07 — Builder | Danh sách slide, nguồn ở giữa, phần song ngữ bên phải | Trọng tâm duyệt dịch/thuật ngữ; không làm editor slide đa phương tiện đầy đủ |
| 08 — Import | Thả tệp hoặc dán text, cấu hình ít bước | Môn mở rộng, khối 10–12; tên mascot đúng; level và layout không lặp một setting |
| 09 — Home | Tạo bài/Bắt đầu dạy, bài gần đây | Lời chào trung tính “thầy cô”; nội dung theo dữ liệu thật; không dùng card giả khi chưa có bài |

## 3. Tokens đề xuất

| Token | Giá trị ban đầu |
|---|---|
| Background / surface | `#F5F9FF` / `#FFFFFF` |
| Primary / primary hover | `#0866F5` / `#0752CA` |
| Text / text secondary | `#102450` / `#596B8C` |
| Border / active background | `#DFE9F6` / `#EAF3FF` |
| Brand accent | `#FF812E` |
| Success / warning / danger | `#159765` / `#B87506` / `#D63B4C` |
| Spacing | 4, 8, 12, 16, 24, 32, 48 đơn vị logic |
| Radius | Input/button 10–12; card 16; bubble 18–24 |
| Font | Font có đầy đủ tiếng Việt; thử Be Vietnam Pro/Noto Sans và chốt gói/quyền phân phối ở M0 |
| Body / secondary | 15–16 / 13–14 đơn vị logic; line height 1.45–1.6 |
| Page title | 28–36, trọng lượng 650–750 |
| Projector | Body khởi điểm 30–40; heading 44–64, thử ở khoảng cách lớp thật |
| Controls | Cao 40–44 trên desktop; vùng chạm học sinh ít nhất 48 |

Các mã màu là đề xuất chứ không phải đo pixel từ ảnh. Kiểm tra tương phản bằng công cụ trước khi chốt; không chỉ dùng màu để truyền trạng thái. Dùng icon đồng bộ một bộ, nhãn chữ cho hành động chính; không dùng emoji hệ điều hành làm icon điều khiển cốt lõi.

## 4. Kích thước và bố cục

- Thiết kế chính 1440×900, kiểm chứng 1366×768 và 1920×1080; test Windows scale 100/125/150%. Kích thước hiệu dụng sau DPI mới quyết định layout.
- Sidebar khoảng 192–216; màn hình hẹp chuyển thanh icon có tooltip. Nội dung dùng khoảng cách 20–28.
- Builder: thumbnail 144–176, vùng trung tâm co giãn, inspector 300–340. Khi thiếu chỗ, inspector thành panel chuyển tab/drawer, thumbnail thu gọn; không ép ba cột nhỏ không đọc được.
- Trình chiếu theo tỉ lệ màn hình thực tế; có safe area, nội dung không bị toolbar/mascot che. Companion không ép slide nguồn đổi tỉ lệ.
- Student: ưu tiên chiều rộng 360–430, một cột, chữ dễ đọc, không cuộn ngang.

## 5. Luồng màn hình và trạng thái bắt buộc

| Màn hình | Hành động chính | Trạng thái phải thiết kế |
|---|---|---|
| First run | Chọn mascot/voice, đọc thử, mức EN | Chưa có voice/model, bỏ qua mạng, cài gói từ tệp |
| Home | Tạo bài mới / Bắt đầu dạy | Chưa có bài, bài đang chuẩn bị, đã sẵn sàng |
| Import | Chọn tệp/dán text, môn/khối, phân tích | Sai định dạng, quá lớn, tiến độ/hủy, tệp chỉ chứa ảnh |
| Builder | Duyệt cặp VI/EN, sửa, khóa thuật ngữ, chuẩn bị | Nháp, đang xử lý, cần duyệt, đã duyệt, thiếu bản EN, chưa lưu, conflict job |
| Level/Layout preview | Chọn mức EN và cách trình bày | Hiển thị phần nội dung tăng/giảm; thiếu câu đã duyệt |
| Prepare | Tạo audio/đóng pack | Thiếu voice, thành công một phần, sẵn sàng, nội dung vừa đổi |
| Classroom setup | Chọn bài/lớp/màn hình, bắt đầu | Chưa có mạng, chọn mạng khác, kiểm tra projector, không có quiz |
| Presentation | Đổi level, phát EN, Rescue, trợ lý | Audio đang phát, pause, mất sync, đổi slide thủ công |
| Student join | Vào lớp / nhập số nếu cần | Mã hết hạn, trùng số, mất mạng, vào lại |
| Student question | Chọn và gửi | Chờ câu, đã nhận, câu đã đóng, chờ kết quả |
| Teacher quiz | Mở/đóng/công bố/tiếp | Đếm phản hồi, offline participant, timeout, câu không chấm điểm |
| Report | Xem kết quả và xuất CSV | Chưa có quiz, ít dữ liệu, có recheck, gợi ý chưa đủ bằng chứng |

## 6. Builder đặt song ngữ ở trung tâm

Vùng giữa có tab “Bản gốc / Xem song ngữ”, giữ ngữ cảnh slide/page. Vùng phải ưu tiên “Nội dung Anh–Việt / Thuật ngữ / Hỗ trợ giảng dạy”; quiz nằm trong hỗ trợ, không chiếm vị trí mặc định.

Mỗi đoạn có nguồn VI, bản EN, tình trạng review, sửa trực tiếp, nút đọc thử và khóa. Khi đang có nguồn EN, cho đảo chiều nếu giáo viên cần; không dịch công thức/ký hiệu theo mặc định. Hiện “Ghi nhớ cho môn này” có phạm vi rõ; chưa chọn thì chỉ sửa bài hiện tại.

Đổi level cho xem trước phần nào sẽ hiện. Layout là lựa chọn khác với level. CTA cuối luồng: “Chuẩn bị để dạy”; lưu nháp/auto-save có trạng thái rõ. Không bắt thêm quiz, câu hỏi hoặc ví dụ để hoàn tất một bài song ngữ.

## 7. Hai mascot và bộ asset

Milo/Lumi dùng chung state machine: idle, wave, speaking, listening, thinking, correct, retry, question, celebrate, minimized. MVP có thể dùng pose tĩnh với chuyển động nhẹ; trạng thái nói phải đi theo playback thật. Reduced motion dùng pose tĩnh, dừng animation khi ẩn hoặc app không hiển thị.

Kích thước mặc định trong lớp 80–120 đơn vị logic, có kéo/ẩn/thu gọn. Nhân vật lớn dùng tiết chế ở onboarding/Home, không chiếm phần lớn slide. Tùy chọn ẩn hoàn toàn phải dễ tìm để phù hợp lớp THPT.

Đầu ra asset cần có ở giai đoạn thiết kế:

- Logo SVG và icon app; một bộ icon điều khiển nhất quán.
- Milo và Lumi riêng nền trong, có avatar, pose mặc định và các trạng thái; không nhúng chữ vào ảnh.
- Anchor vị trí tay/chân/bubble nhất quán để animation không nhảy khung; kích thước xuất có bản 1×/2×.
- Phụ kiện môn là lớp riêng; khởi đầu generic và các nhóm môn tiêu biểu, môn chưa có phụ kiện dùng mascot chuẩn.
- Bảng provenance/điều kiện sử dụng, tên asset, kích thước, trạng thái; kiểm tra mép alpha trên nền sáng/tối.

Chưa tạo asset mới trong lượt lập kế hoạch. Chín ảnh tham chiếu được lưu nguyên trạng; không coi chúng là sprite sheet có thể cắt dùng ngay.

## 8. Trình chiếu và thao tác

Toolbar ngắn: level, EN, phát âm, giải thích, ví dụ/câu hỏi, VI Rescue, quiz và mascot. Nhóm ít dùng có thể nằm trong menu. Có nhãn/tooltip và bàn phím; phím tắt cuối cùng phải qua kiểm thử xung đột PowerPoint.

Ở hai màn hình Extend: laptop hiển thị điều khiển, projector chỉ nhận nội dung công khai. Ở Duplicate hoặc một màn hình: app không thể làm một cửa sổ chỉ thấy riêng trên laptop; dùng chế độ chiếu an toàn, tạm ẩn dữ liệu giáo viên và không tự mở bảng đáp án. Kiểm tra cách bố trí màn hình trước tiết học.

Mascot là trợ lý thao tác theo bài: phát EN, phát âm, giải thích, ví dụ, hỏi lớp, Rescue. Nếu có ô tra cứu, nhãn là “Tìm trong bài học”; không gợi ý khả năng trả lời mọi kiến thức.

## 9. Định nghĩa hoàn thành thiết kế

Mỗi màn hình có bố cục, token, nội dung thật, hành động và trạng thái lỗi/trống/loading. Kiểm tra ảnh thực thi với ảnh tham chiếu theo phân cấp, khoảng cách và khả năng đọc; không bắt chước lỗi nội dung trong ảnh. Chuẩn bị bộ màn hình ít nhất Home, Import, Builder, Level/Layout, Presentation, Quiz/Student, Results và Settings trước khi hoàn thiện toàn UI.

## 10. Bổ sung luồng duyệt và glossary

Glossary Management trong Cài đặt: môn/giáo viên, thuật ngữ VI/EN, thêm/sửa/xóa/khóa, nhập/xuất CSV sau. Builder có trạng thái DRAFT/REVIEW_REQUIRED/READY_TO_TEACH và nút duyệt rõ ràng. Readiness hiển thị nguồn, phần chưa duyệt, explanation, voice/cache; quiz và mạng chỉ khi được chọn. Warning cho phép tiếp tục có ghi nhận. Cấp học/khối là trường cấu hình, không chỉ dropdown 10–12.
