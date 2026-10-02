# BiliClass — đặc tả sản phẩm V1 đề xuất

Ngày: 29/09/2026. Tổng hợp từ hai văn bản, chín ảnh và làm rõ trực tiếp của người dùng: phục vụ giáo viên THPT, mọi môn học, nhiều bài giảng; trọng tâm là song ngữ Anh–Việt. Các bài/môn/khối minh họa trong ảnh không xác định phạm vi sản phẩm. Phạm vi hiện tại là lập kế hoạch; trạng thái triển khai xem `STATE.md`.

## 1. Kết quả cần đạt

Một giáo viên THPT có thể đưa bài giảng của bất kỳ môn học nào vào ứng dụng, duyệt lớp nội dung Anh–Việt, chọn mức hỗ trợ ngôn ngữ và dùng lại bài ở nhiều lớp. Nội dung chuyên môn luôn do giáo viên kiểm soát. Phát âm, mascot, quiz và báo cáo là công cụ hỗ trợ tiết dạy song ngữ.

Kiến trúc không gắn cứng một môn, một bộ sách hoặc một bài mẫu. Danh mục môn có thể mở rộng; chủ đề/bài học nhập tự do; cấp học và khối cấu hình tự do; ưu tiên THPT nhưng không khóa engine ở lớp 10–12. Có glossary chung và glossary theo môn, nhưng không hứa có sẵn bộ thuật ngữ hoàn chỉnh của mọi môn ngay ngày đầu. Cùng một từ có thể có nghĩa/bản dịch khác nhau theo môn và ngữ cảnh.

Năm nguyên tắc: ưu tiên hoạt động offline; giáo viên kiểm soát; trợ lý dựa trên bài đã chuẩn bị; học sinh không cần tài khoản; không bắt buộc thuê bao hay API trả phí.

Internet có thể cần khi tải bộ cài hoặc gói bổ sung. Phải có cách cài gói từ tệp/USB cho máy không có mạng. Trong giờ học, quiz điện thoại vẫn cần LAN giữa máy giáo viên và điện thoại; QR chỉ mở địa chỉ lớp.

## 2. Người dùng và ba bề mặt sử dụng

| Bề mặt | Công việc chính | Dữ liệu được thấy |
|---|---|---|
| Giáo viên trên laptop | Chuẩn bị bài, điều khiển, xem kết quả | Nội dung nguồn, đáp án, ghi chú, phân tích |
| Máy chiếu | Hiển thị bài hoặc câu hỏi | Chỉ nội dung giáo viên chủ động trình chiếu |
| Điện thoại học sinh | Vào lớp, chọn đáp án, nhận xác nhận | Câu hỏi hiện tại và trạng thái trả lời của mình |

MVP triển khai trên Windows x64, CPU phổ thông, không yêu cầu GPU rời. Mốc hiệu năng tạm dùng Windows 11/RAM 8 GB/SSD và PowerPoint desktop; đây là giả định chờ xác nhận, không phải kết quả khảo sát máy của người dùng.

## 3. Luồng sản phẩm

1. Thiết lập lần đầu: ngôn ngữ → Milo/Lumi → giọng đọc thực sự có trên máy → đọc thử → level mặc định → kiểm tra thiết bị/mạng. Có thể bỏ qua thiết lập mạng khi chỉ soạn bài.
2. Tạo bài: nhập tệp hoặc dán văn bản → môn/khối → level → cách trình chiếu → phân tích.
3. Duyệt: xem nguồn và nội dung đề xuất → sửa dịch/thuật ngữ/concept/quiz → duyệt từng phần.
4. Chuẩn bị: xác nhận nội dung đã duyệt → tạo cache âm thanh → kiểm tra thiếu thành phần → lưu Lesson Pack.
5. Dạy: chọn bài và lớp → chọn màn hình → mở PowerPoint/slide tích hợp → dùng toolbar và mascot.
6. Kiểm tra: mở câu hỏi → học sinh vào LAN/quét QR → trả lời → giáo viên đóng nhận đáp án → giải thích → kiểm tra lại.
7. Kết thúc: xem số liệu theo concept → xem gợi ý có căn cứ → xuất CSV → lưu và đóng phiên.

Nội dung đang sửa không tự thay đổi bài đang dạy. Phiên học dùng một bản nội dung đã chuẩn bị và có số phiên bản cụ thể.

## 4. Hai mức bàn giao

| Nhóm | MVP thử nghiệm một lớp | V1 đầy đủ |
|---|---|---|
| Nhập bài | PPTX, DOCX, PDF có text và văn bản; nhiều bài đại diện | Thêm ảnh/PDF scan OCR và trường hợp nhập nâng cao |
| Song ngữ | Dịch offline, thuật ngữ, ghi nhớ bản dịch; ưu tiên kiểm chứng L0–L2 | Kiểm chứng đủ L0–L5 và bốn layout |
| Lesson Pack | Lưu/mở, nguồn bất biến, revision, duyệt và cache | Chuyển máy, migration, khôi phục và kiểm tra lỗi |
| Dạy học | Companion PowerPoint, chuyển concept thủ công dự phòng, trình chiếu tích hợp đơn giản | Ma trận nhiều màn hình/DPI, xuất deck song ngữ mới |
| Mascot | Cả Milo và Lumi; hành động theo bài, trạng thái cơ bản | Hoàn thiện biểu cảm, phụ kiện môn, khả năng giảm chuyển động |
| Âm thanh | Giọng local đã kiểm tra, cache EN, VI khi máy/gói hỗ trợ | Kiểm tra cài gói, tốc độ, thiếu giọng và tương thích bản cài |
| Lớp học | LAN, QR, không tài khoản, quiz một đáp án/đúng sai/poll | Tái kết nối, 40+ thiết bị, Seat Mode ổn định |
| Báo cáo | Tỷ lệ đúng theo concept, hiểu nhầm theo đáp án, before/after, CSV | So sánh nhóm câu song ngữ và gợi ý level khi đủ bằng chứng |

MVP là mốc thử nghiệm để học từ lớp học thật; không dùng tên V1 đầy đủ trước khi phạm vi cột cuối được nghiệm thu. Từ MVP, luồng nhập và xử lý phải áp dụng được cho môn do giáo viên tự tạo; không điều kiện hóa tính năng theo một môn đã lập trình sẵn.

## 5. Level và layout là hai thuộc tính độc lập

| Level | Chính sách nội dung |
|---|---|
| L0 Familiarize | Nội dung VI, thêm từ khóa EN |
| L1 Exposure | VI chính, thuật ngữ và câu điều hành lớp đơn giản |
| L2 Bridge | VI chính, thêm định nghĩa/câu hỏi/cụm trọng tâm EN |
| L3 Mixed | Các phần VI/EN xen kẽ có chủ đích |
| L4 English First | EN chính, gọi hỗ trợ VI khi cần |
| L5 Immersion | Gần toàn bộ EN; giáo viên vẫn có quyền gọi VI Rescue |

Không định nghĩa level bằng phần trăm tiếng Anh. Layout gồm Keyword Overlay, Line Pair, Split View và English + Rescue. UI gợi ý tổ hợp thích hợp; đổi level/layout không yêu cầu nhập lại tệp.

Level chọn từ nội dung đã duyệt. Nếu bài chưa có câu giải thích EN phù hợp, phải báo phần còn thiếu, không tự sinh lời giải mới khi đang dạy. Một concept có thể có nhiều cách diễn đạt và nhiều tham chiếu slide.

## 6. Hợp đồng nội dung

- Tệp nguồn không bị ghi đè. Mọi bản xuất có tên/đích riêng.
- OCR, tách concept, dịch và câu hỏi gợi ý đều là bản nháp, có liên kết về đoạn/slide nguồn.
- Bản dịch ưu tiên ghi nhớ của giáo viên → từ điển môn → model dịch offline. Nội dung đã khóa không bị tác vụ tạo lại ghi đè.
- Quiz/giải thích/ví dụ lấy từ nguồn, thư viện mẫu đã kiểm tra hoặc giáo viên nhập. Model dịch chỉ dịch; V1 không hứa tạo được giáo án hay quiz chất lượng từ mọi tài liệu.
- Bộ quy tắc có thể gợi ý câu hỏi theo mẫu khi đủ trường dữ liệu; đáp án và mapping hiểu nhầm luôn cần giáo viên duyệt.
- Trợ lý tìm trong Lesson Pack và ngữ cảnh hiện tại; khi không đủ căn cứ trả “Nội dung này chưa có trong Lesson Pack.”
- Lệnh Translate trong lớp ưu tiên cặp VI/EN đã duyệt. Không tự gọi một model mới để thay nội dung chính thức giữa tiết.
- Listening là trạng thái chờ thao tác; V1 không ngụ ý đã có nhận diện giọng nói hay thu âm.

## 7. Quiz và phân tích

Chỉ ba dạng: single choice, đúng/sai, poll. Poll không có đáp án đúng và không được tính vào tỷ lệ đúng. Phiên học có Anonymous Mode hoặc Seat Mode; tên thật là tùy chọn ngoài luồng mặc định.

Trước khi giáo viên công bố, điện thoại/máy chiếu không nhận đáp án đúng, phân tích hiểu nhầm hoặc ghi chú giáo viên. Giáo viên có thể giải thích lại và mở lượt kiểm tra mới; không ghi đè lượt cũ.

“Understanding Radar” dùng thanh tiến trình và nhãn trạng thái. Tên chỉ số trên UI là “Tỷ lệ trả lời đúng”, kèm số câu/số người phản hồi; không đồng nhất với khả năng hiểu toàn diện. Khi mẫu nhỏ hiển thị “Chưa đủ dữ liệu”.

Gợi ý giữ/tăng level là quy tắc minh bạch, không tự thay level. So sánh VI/EN chỉ mang tính mô tả nếu các câu khác độ khó. Chỉ hiển thị “Có thể cần hỗ trợ ngôn ngữ” khi nhiều hoạt động tương đương cho thấy xu hướng, không gán nhãn học sinh yếu tiếng Anh.

## 8. Chưa nằm trong V1

BiliCard/camera nhận thẻ; nhận diện giọng nói; chatbot kiến thức mở; LLM lớn; cloud bắt buộc; tài khoản học sinh; LMS đầy đủ; quản lý trường; điểm danh; thanh toán; ứng dụng mobile native; phục dựng mọi animation PowerPoint; dark mode; báo cáo PDF. Lịch trong trang chủ chỉ là lịch/phiên dạy local đơn giản, không trở thành phân hệ thời khóa biểu.

## 9. Điều kiện hoàn thành V1

Giáo viên không cần Python, terminal, JSON hay nhập IP trong luồng thông thường. Khi đã chuẩn bị đủ gói, chặn Internet nhưng giữ LAN vẫn hoàn thành toàn bộ tiết học, mở lại bài sau khởi động, phát âm, thu quiz và xuất CSV. Thiếu model/voice/mạng phải có thông báo và đường tiếp tục phù hợp. UI đúng ở 1366×768 và 1920×1080, kiểm tra DPI 100/125/150%, có chế độ một màn hình tránh lộ dữ liệu giáo viên.

Mỗi mốc chỉ hoàn thành khi có bản chạy, kiểm tra tự động phù hợp, kiểm thử thao tác thực tế, xử lý lỗi và cập nhật trạng thái. Tài liệu kế hoạch không phải bằng chứng các điều kiện này đã đạt.

## 10. Bổ sung theo tài liệu góp ý mới

Pipeline: Import → Parse → Concept Model → Bilingual Engine → Lesson Intelligence → Teacher Review → Lesson Pack → Readiness Check. Lesson Intelligence chứa explanation VI/EN, easy EN, examples, teacher prompts, questions, VI Rescue, vocabulary, quiz/misconceptions và audio scripts/cache refs; nội dung có nguồn và trạng thái duyệt.

Trạng thái bài: DRAFT → REVIEW_REQUIRED → READY_TO_TEACH. Tiến độ chuẩn bị/audio quản lý riêng. Readiness kiểm tra nguồn, nội dung chưa duyệt, thiếu giải thích, voice/cache; quiz/network chỉ kiểm tra nếu giáo viên chọn quiz. Giáo viên có thể tiếp tục với warning có ghi nhận; override không tự biến nội dung thành đã duyệt và không bỏ kiểm tra file hỏng.

Glossary có UI thêm/sửa/xóa/khóa theo teacher + subject; CSV để mở rộng. ResponseProvider chuẩn hóa nguồn phản hồi; BiliCard là extension sau V1. Khi không có mạng vẫn dạy song ngữ, nhưng không thu đáp án điện thoại qua QR nếu thiếu LAN.

Tài liệu góp ý đề xuất V1 THCS–THPT, khác với yêu cầu trực tiếp ưu tiên THPT trước đó. Đã hỏi làm rõ; tạm giữ ưu tiên THPT và không hard-code cấp học/khối/môn.
