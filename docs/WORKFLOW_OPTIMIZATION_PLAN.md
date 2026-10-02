# Kế hoạch khóa luồng vận hành BiliClass V1

Ngày 01/10/2026. Đây là đánh giá và kế hoạch ban đầu. Đến 02/10/2026, mã nguồn đã triển khai một phần P0–P4: chốt bản chuẩn bị theo revision, chặn mở lớp mới khi chưa chốt, tách nhiều ý PPTX, giữ ảnh thường khi xuất, chọn bài tại Lớp học và nối báo cáo với bài gốc. Các mục còn lại trong bảng mốc vẫn là việc tiếp theo; xem [Changelog](../CHANGELOG.md) và [hướng dẫn thử hai máy](TEACHER_TESTING.md). Phạm vi đợt này: Trang chủ, Bài giảng, Thuật ngữ, Lớp học, trợ giảng khi dạy, Báo cáo và các luồng nhập/xuất/dữ liệu liên quan. Giữ nguyên toàn bộ tab Cài đặt, đặc biệt Chung, Song ngữ, Giọng đọc và Mascot vừa sửa.

Bổ sung ngày 02/10/2026: xem [đề xuất nhập tài liệu, mẫu bài giảng và gói dữ liệu offline](UPGRADE_PROPOSAL_2026-10-02.md). Tài liệu bổ sung chi tiết P1, làm rõ hai cách trình chiếu và điều kiện nghiệm thu; vẫn là đề xuất, chưa triển khai chức năng.

## Mục tiêu

Một giáo viên phải đi được liên tục qua: **nhập bài có sẵn → kiểm tra nguồn và các khối nội dung → tạo bản dịch nháp → sửa/duyệt → chuẩn bị bài → bắt đầu tiết → trình chiếu/trợ giảng/quiz tùy chọn → kết thúc → xem báo cáo và tự quyết định Level lần sau**. Mỗi màn chỉ hiển thị hành động hợp lệ và dẫn tới bước tiếp theo. Bài không có quiz hoặc audio vẫn có đường dạy bằng chữ, kèm nhãn khả năng rõ ràng.

## Đánh giá hiện trạng từ mã nguồn

| Khu vực | Đã có | Lệch cần xử lý |
|---|---|---|
| Trang chủ & thư viện | Bài gần đây, mở bài, tạo bài, nhập gói; thẻ có số đoạn duyệt | Trang chủ mới lấy bốn bài cập nhật gần nhất, chưa có bài cần làm tiếp/bài sẵn sàng/tiết gần đây. Tìm kiếm mới xét tên, môn, khối; chưa có lọc trạng thái hoặc từ khóa. Xem `Main.qml` phần `home/library`. |
| Nhập và cấu trúc bài | Giữ bản nguồn/hash, đọc PPTX/DOCX/PDF/TXT/ảnh, OCR có cảnh báo, UUID đoạn, chỉnh/split | PPTX hiện gom mỗi slide thành một đoạn; PDF mỗi trang thành một đoạn. Chưa có Section/TeachingBlock nhỏ hơn slide và nguồn tham chiếu đủ chi tiết cho nhiều ý trên cùng slide. Xem `importers.py`, `library.py`. |
| Workspace & duyệt | Mở bài vào editor, sửa/duyệt VI–EN, trợ giảng/quiz, autosave, lịch sử, preview | Các chức năng nằm trong một editor và dialog, chưa có tổng quan quy trình/tác vụ còn thiếu. `lesson_status()` trả `READY_TO_TEACH` chỉ từ chữ đã duyệt, dù audio/nguồn/prepare chưa kiểm tra. Xem `Main.qml`, `library.py`, `readiness.py`. |
| Chuẩn bị & bắt đầu lớp | Bảng kiểm nguồn/duyệt/voice/cache, nút tạo audio; lớp LAN và session snapshot | “Chuẩn bị lên lớp” mới xem điều kiện, chưa lưu dấu chuẩn bị theo revision. Nút Bắt đầu lớp không gọi preflight; server chỉ cần **một** đoạn được duyệt. Thiếu chọn bài ngay tại Lớp học và nhãn thiếu voice/mạng trước khi mở QR. Xem `readiness.py`, `ClassroomPage.qml`, `classroom_store.py`. |
| Trợ giảng khi dạy | Nội dung hỗ trợ được chuẩn bị/duyệt theo đoạn; PowerPoint sync slide, mascot và quiz riêng | Chưa có một TeachingContext duy nhất nối bài/revision/block/slide/session cho toàn bộ cửa sổ. Cần làm rõ hành động nào dùng đúng đoạn đang dạy và khi nào hiện “chưa chuẩn bị”. Xem `teaching.py`, `CompanionWindow.qml`, `Main.qml`. |
| Thuật ngữ | Theo môn, khóa, dịch chính xác, memory từ bản đã duyệt cùng môn | Nút “Sửa” hiện điền lại form rồi upsert theo môn+từ VI; đổi môn hoặc từ VI sẽ tạo thêm bản ghi, không sửa bản cũ. Chưa có lọc môn/import CSV. Xem `Main.qml`, `library.py`. |
| Quiz & báo cáo | QR/WebSocket/SQLite, gửi trùng an toàn, reconnect, reveal, recheck, misconception do giáo viên gắn; thống kê có mẫu số | Phần lõi mạnh hơn UI. Trang Báo cáo chưa nối rõ phiên → bài/revision/môn/khối; Trang chủ chưa có đường quay lại kết quả. Tránh gọi “rào cản ngôn ngữ” khi chưa có cặp câu tương đương và đủ mẫu. Xem `classroom_store.py`, `analytics.py`, `ReportsPage.qml`. |
| Gói bài & bảo vệ dữ liệu | Kiểm manifest/hash/path/quota, nguồn/audio portable, nhập thành bản mới cần duyệt; backup gồm cả `library.db` và `classroom.db` | Import luôn tạo bản sao UUID mới, chưa cho giáo viên thấy bài trùng và chọn xử lý. Cần kiểm tra khả năng khôi phục và quan hệ báo cáo–bài sau migration; không cần dời toàn bộ thư mục dữ liệu chỉ để giống sơ đồ tài liệu tham khảo. Xem `pack.py`, `storage.py`. |

## Những điểm cần điều chỉnh so với tài liệu tham khảo

1. **Không dùng một state machine tuyến tính duy nhất.** Tách trạng thái nội dung (`DRAFT`/`REVIEW_REQUIRED`/`APPROVED`), dấu chuẩn bị gắn với revision và năng lực (`text`, `audio VI`, `audio EN`, `quiz`), và trạng thái từng session (`active`/`ended`). Một bài có thể được dạy nhiều lần rồi sửa lại; “Đã giảng N tiết” là lịch sử, không phải trạng thái cuối khóa bài. UI có thể dùng nhãn “Cần duyệt”, “Đã duyệt, cần chuẩn bị”, “Sẵn sàng dạy bằng chữ/âm thanh”.
2. **Bài mới tiếp tục L0–L4 và bốn kiểu bố cục đang có.** L5 chỉ đọc cho bài cũ theo quyết định sản phẩm hiện tại. “Companion Mode” là cách dùng PowerPoint gốc, không phải bố cục chữ thứ năm; “English First” cần xác định khác gì `english_rescue` trước khi thêm enum.
3. **Không tự sinh giải thích/quiz bằng model dịch.** Engine hiện có tạo bản dịch nháp, không phải giáo án đã kiểm chứng. Có thể trích xuất/gợi ý khối, thuật ngữ ứng viên và mẫu cấu trúc, nhưng giải thích, câu hỏi, đáp án phải do giáo viên soạn hoặc xác nhận rõ nguồn và duyệt.
4. **Không duyệt hàng loạt chỉ vì máy không báo lỗi.** Kiểm tra số/ký hiệu/OCR không đo được đúng nghĩa hoặc đúng sư phạm. Duyệt từng block vẫn là chuẩn V1; công cụ có thể gom danh sách cảnh báo và điều hướng nhanh.
5. **Ưu tiên thuật ngữ khóa do giáo viên đặt.** Quy tắc đề xuất: thuật ngữ khóa khớp chính xác → memory đã duyệt cùng môn/ngữ cảnh khi không xung đột → model offline. Nhiều bản memory khác nhau phải cho giáo viên chọn; mọi kết quả vẫn thành nháp. Không tự ghi một cách dịch mới vào glossary toàn môn chỉ từ một lần sửa câu.
6. **Quiz và audio không phải điều kiện cứng cho mọi tiết.** Text và nguồn đã duyệt là ngưỡng tối thiểu. Thiếu voice/cache thì ghi rõ chế độ dạy bằng chữ hoặc cho giáo viên chuẩn bị audio; thiếu quiz vẫn có thể dạy. Mạng chỉ kiểm tra khi mở lớp tương tác, không nằm trong trạng thái lâu dài của lesson.
7. **Giữ F1 cho Trợ giúp.** Tài liệu tham khảo đề xuất F1 phát tiếng Anh, xung đột hotkey hiện tại. Phím tắt khi dạy sẽ thiết kế sau khi khóa thao tác và thử bàn phím thực tế.

## Thứ tự triển khai

### P0 — Khóa hợp đồng và sửa lệch trạng thái (làm đầu tiên)

- Viết hợp đồng cho `Lesson`, `TeachingBlock`, `PreparedRevision`, `TeachingContext`, `ClassSession`; thống nhất tên trạng thái và quy tắc làm mất hiệu lực khi sửa nội dung, đổi Level/bố cục, voice/tốc độ, nguồn hoặc quiz.
- Thay cách tính `READY_TO_TEACH` chỉ theo số đoạn duyệt; tạo chỉ số nội dung đã duyệt và readiness kiểm tra ở thời điểm sử dụng. Chặn mở lớp khi không có bài/không có nội dung dạy đã duyệt; nếu chỉ duyệt một phần, phải nêu rõ phần sẽ dạy và không vô tình coi cả bài đã sẵn sàng.
- Thiết kế migration không mất `segments`, support, questions, revision, gói v1–v3 và báo cáo cũ. Backup trước migration, round-trip một thư viện thực tế **trên bản sao**.
- Tiêu chí xong: cùng một bài ở mọi màn hiện cùng tiến độ; sửa một block làm mất hiệu lực đúng phần chuẩn bị liên quan; phiên đã kết thúc giữ snapshot cũ.

### P1 — Nhập bài và Lesson Workspace

- Giữ form nhập đơn giản nhưng chia các bước rõ: nguồn → thông tin bài → Level/bố cục → xem kết quả trích xuất. Không bắt giáo viên gõ bản song ngữ. Hiện trạng thái OCR/công thức/đối tượng không trích xuất ở đúng block nguồn.
- Chuẩn hóa `TeachingBlock` với ID bền, thứ tự, `source_ref` (slide/trang/đoạn và vị trí khi trích được), VI/EN, provenance, review, liên kết hỗ trợ/quiz/audio. Một slide có thể có nhiều block; không tách mù công thức, bảng hoặc câu ngắn. Cho giáo viên gộp/tách và kiểm tra trật tự sau import.
- Mở bài vào Workspace có **Tổng quan / Nội dung song ngữ / Trợ giảng & Quiz / Chuẩn bị**; dùng lại editor và dialog hiện có trước khi đổi toàn bộ UI. Tổng quan cho biết cần sửa gì và nút “Tiếp tục” đưa tới block đầu tiên chưa duyệt.
- Tiêu chí xong: fixture PPTX có ba ý trên một slide tạo ba block có cùng slide ref; sửa/duyệt/tách/gộp/đóng mở vẫn giữ đúng nguồn và tiến độ; bài PDF OCR không âm thầm được duyệt.

### P2 — Chuẩn bị bài và preflight thật

- “Chuẩn bị bài” tạo manifest gắn với lesson revision, hash nội dung đã duyệt, Level/bố cục và lựa chọn audio; ghi trạng thái từng bước: nguồn, review, hỗ trợ, audio VI/EN, quiz. Cache chỉ phát lại nếu nội dung/giọng/tốc độ còn khớp. Hiện thời gian và lỗi dễ hiểu, có thể thử lại phần lỗi.
- Nút **Bắt đầu lớp** ở Trang chủ, Workspace và Lớp học cùng gọi một preflight. Phân biệt lỗi chặn (chưa có nội dung duyệt, nguồn hỏng nếu cần PowerPoint) và cảnh báo có lựa chọn (không có voice/audio/quiz, LAN chưa dùng). Khi chọn dạy bằng chữ, ghi quyết định vào session và hiển thị rõ.
- Tiêu chí xong: không thể gắn nhãn “sẵn sàng dạy có âm thanh” khi cache thiếu; sau sửa một câu, manifest cũ báo hết hiệu lực; mở lớp text-only được nhưng không giả báo audio ready; không bật QR nếu cổng/LAN chưa dùng được.

### P3 — Luồng dạy trực tiếp và lớp học

- Lớp học khi chưa chạy cho chọn bài đã duyệt ngay tại trang, đặt tên tiết và xem preflight. Khi LIVE, thấy bài/revision/Level, block/slide hiện tại, số đã vào, tình trạng câu hỏi và lối mở màn chiếu/kết thúc; lưu session snapshot độc lập với bài tiếp tục chỉnh.
- Dùng một `TeachingContext` cho editor, PowerPoint companion, cửa sổ trình chiếu, mascot và toolbar: `lesson_id`, `revision`, `block_id`, `slide_ref`, `level`, `session_id`. Theo slide thì chọn block đầu tiên tương ứng và cho giáo viên chuyển các block trong cùng slide; mất PowerPoint thì vẫn chuyển thủ công. Hành động trợ giảng chỉ trả nội dung đã duyệt hoặc câu “Phần này chưa được chuẩn bị”.
- Giữ quiz hiện có: mở/đóng/công bố/kiểm tra lại, reconnect và idempotency. Bổ sung đường “giải thích lại” từ câu hỏi về đúng block/concept, không mở câu khác ngầm.
- Tiêu chí xong: đồng bộ qua ba block trên một slide; đóng PowerPoint giữa tiết không đổi sai câu hỏi/block; đáp án không lộ trước reveal; học sinh mất mạng vào lại không nhân đôi phản hồi.

### P4 — Báo cáo, điều hướng và quản lý thư viện

- Báo cáo gắn tên lớp, bài, môn, khối, revision, thời điểm và chế độ dạy. Cho mở báo cáo từ tiết gần đây trên Trang chủ và quay về bài gốc. Giữ mẫu số, thiếu dữ liệu, recheck và so sánh VI/EN có điều kiện; gợi ý Level chỉ là đề xuất, không tự đổi lesson.
- Trang chủ ưu tiên ba nhóm hành động: **tiếp tục duyệt**, **đã chuẩn bị để dạy**, **tiết gần đây**. Thư viện thêm lọc trạng thái và tìm theo từ khóa đã duyệt sau khi model block hỗ trợ; kết quả tìm có đường tới đúng block.
- Sửa Thuật ngữ thành edit theo ID thật; thêm lọc môn và import CSV có preview/conflict/rollback. Import `.biliclass` báo khi trùng bài gốc; cho nhập bản sao hoặc hủy trước, chỉ bổ sung thay thế có backup và lịch sử rõ ràng. Gói nhập vẫn yêu cầu giáo viên duyệt trên máy nhận.
- Tiêu chí xong: sửa tên thuật ngữ không tạo dòng cũ sót lại; pack lỗi không ghi dữ liệu nửa chừng; nhập trùng không ghi đè im lặng; báo cáo cũ vẫn xem được sau migration.

## Bộ kiểm thử chặn trước khi đóng gói `.exe`

1. Một fixture PPTX Toán nhiều ý trên cùng slide, một DOCX môn khác, một PDF/ảnh cần OCR và một bài dán văn bản; chạy đủ luồng từ nhập → duyệt → chuẩn bị → dạy text-only/voice → quiz → báo cáo.
2. Kiểm tra migration/backup/restore và pack cũ trên thư viện **bản sao**, bao gồm nguồn hỏng, gói trùng, chuyển máy thiếu giọng, mất mạng và cổng bị chiếm.
3. Kiểm tra riêng an toàn lớp học: student DTO chưa reveal không có đáp án/rationale; gửi trùng/reconnect giữ mẫu số; quiz không bắt buộc.
4. Chạy nhanh từ mã nguồn sau mỗi phần. Chỉ đóng gói `.exe` khi một mốc end-to-end qua đủ kiểm thử; cuối cùng vẫn cần thử máy Windows sạch, điện thoại, máy chiếu và tiết dạy thật trước khi gọi V1 hoàn tất.

Ưu tiên **P0 → P1 → P2 → P3 → P4**. Không thêm feature trang trí hoặc làm lại bốn mục Cài đặt vừa hoàn thiện trong đợt này.
