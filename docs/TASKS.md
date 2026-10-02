# Backlog và nghiệm thu

Cập nhật 01/10/2026, RC7. Phạm vi: song ngữ Anh–Việt đa môn THPT, khối 10–12. Tách các tiêu chí ghép trong kế hoạch gốc để không đánh dấu phần chưa thử. `[x]` là phần có triển khai/bằng chứng local; `[ ]` giữ các nghiệm thu cần môi trường hoặc dữ liệu thật. Chi tiết kết quả: `APP_RESULTS.md`.

## P — Tiếp nhận

- [x] Đọc ba tài liệu và chín ảnh; giữ bản nguồn, checksum và chỉ mục.
- [x] Ưu tiên làm rõ của người dùng: tất cả môn THPT, cốt lõi Anh–Việt; bài trong ảnh chỉ là ví dụ.
- [x] Đặc tả, thiết kế, kiến trúc, schema, kế hoạch và quyết định kỹ thuật.

## M0 — Kiểm chứng

- [x] Xác nhận PowerPoint 16, Qt, model, SAPI và OCR trên máy phát triển; executable độc lập.
- [x] Năm đầu vào tự soạn phủ Toán/Hóa/Ngữ văn/Lịch sử/môn tự tạo, khối 10–12; 100 lượt model hai chiều bảo toàn số/ký hiệu trong fixture.
- [x] COM tiến/lùi/nhảy, source hash, fallback thủ công; 50 WebSocket client loopback.
- [x] Home/Builder/Presentation, asset/font local, dependency lock và model provenance.
- [ ] Xác nhận máy giáo viên, projector/DPI, Presenter View và mạng trường.
- [ ] Giáo viên chấm thuật ngữ/đa nghĩa/ngữ nghĩa bản dịch và chất lượng giọng đọc; RAM trên máy mục tiêu.
- [ ] Laptop + Android/iPhone trên LAN không Internet, giới hạn hotspot/router.

## M1 — Nền tảng

- [x] Git, môi trường, khóa dependency, app shell, token UI và module xử lý tách khỏi QML.
- [x] Môn mở, khối 10–12 mặc định; settings, log, SQLite migration, asset store, tác vụ/hủy.
- [x] Sao lưu SQLite nhất quán trước migration, backup tự động/thủ công, khôi phục vào thư mục mới.
- [x] Smoke/source workflows, lưu/mở thư viện và xử lý thiếu optional pack trong ứng dụng.

## M2 — Nhập và lưu bài

- [x] PPTX/DOCX/PDF text/TXT, nhóm shape, locator, nguồn SHA-256 bất biến; cảnh báo đối tượng không trích xuất thành text.
- [x] Builder danh sách đoạn/cặp VI–EN, xem nguồn và bản sao tài liệu, sửa metadata.
- [x] Revision/draft/autosave, tách đoạn và khôi phục; prepared Lesson Pack v3 đọc v1/v2/v3.
- [x] Tests đa định dạng, môn tự tạo, pack hỏng/hash/path/schema/quota; audio portable và reset review khi nhập.

## M3 — Lõi song ngữ

- [x] Provider CPU local hai chiều, availability, job/cancel và chống kết quả cũ ghi đè.
- [x] Glossary theo môn; memory từ đoạn đang được duyệt; nhiều cách dịch/gần giống do giáo viên chọn.
- [x] Bảo vệ số, ký hiệu/biểu thức đánh dấu, tên riêng qua thuật ngữ khóa; cảnh báo và review từng đoạn.
- [x] Level L0–L5 độc lập bốn layout; 24 tổ hợp được kiểm tra, nội dung thiếu báo rõ.
- [x] Trợ giảng theo nguồn/nội dung đã chuẩn bị; không giả sinh giáo án bằng model dịch.
- [x] Kiểm tra memory không lấy nháp/history chưa duyệt và không dùng chéo môn.

## M4 — Dạy học

- [x] LessonContext, PowerPoint companion cách ly tiến trình, đồng bộ slide và fallback; native teacher/projector riêng.
- [x] Toolbar, hướng dẫn Extend/Duplicate, không gửi ghi chú/đáp án kín sang projector.
- [x] Milo/Lumi bốn tư thế, trợ giảng nổi, hành động theo đoạn, vị trí/cỡ/ẩn/reduced motion/nhãn môn dự phòng.
- [x] SAPI, liệt kê/chọn giọng thật, cache/invalidation, Pronounce/Speak/Rescue; readiness và audio trong pack.
- [x] Dịch và pack roundtrip năm nhóm môn; bài không quiz vẫn mở/dạy; chuyển cache không đòi cùng voice.
- [ ] Thử các bài trên máy khác khi chặn Internet, màn hình chiếu thật và âm thanh qua thiết bị lớp.
- [ ] Giáo viên ghi phản hồi về tốc độ chuẩn bị, lỗi dịch và thao tác dạy.

## M5 — Tương tác lớp học

- [x] Classroom process và DB riêng; admin loopback có token, listener học sinh LAN.
- [x] QR, anonymous/seat, reconnect token, mã khôi phục, giữ origin khi resume cùng mạng.
- [x] Web học sinh nhẹ, single/true-false/poll, vòng đời câu, deadline theo server.
- [x] ACK/idempotency, đổi đáp án, đóng/công bố, dashboard, chặn lộ đáp án trước công bố.
- [x] 50 client đồng thời, gửi trùng/kết nối lại, stop/resume và báo cáo đúng; browser mô phỏng offline.
- [x] Cổng cũ bị chiếm trên máy thử: đổi cổng/QR, giữ câu trả lời và khôi phục đúng danh tính.
- [ ] Thử điện thoại thật, Wi-Fi đổi IP/cổng bận trên mạng lớp và tải mục tiêu 40–50 máy.

## M6 — Báo cáo

- [x] Tỷ lệ đúng/tham gia có mẫu số; chưa trả lời riêng, poll không chấm.
- [x] Concept bars có điều kiện mẫu, misconception metadata, recheck tách lượt/nhóm tham gia.
- [x] So sánh Việt/Anh chỉ với cặp tương đương do giáo viên gắn nhãn, đủ dữ liệu; gợi ý level minh bạch không tự áp dụng.
- [x] CSV tổng hợp/từng phản hồi chống công thức; không xuất token; mở lịch sử/xóa phiên đã kết thúc.

## M7 — Hoàn thiện V1

- [x] PNG/JPG/PDF scan OCR Windows theo ngôn ngữ thực sự có; tiến trình cách ly/timeout; kiểm tra native EN và trường hợp thiếu VI.
- [x] Fixture định dạng, giới hạn tệp/trang, cảnh báo công thức/đối tượng cần kiểm tra thủ công.
- [x] Toàn bộ tổ hợp level/layout và bảo vệ các nhóm biểu thức; deck song ngữ mới không sửa nguồn.
- [x] Asset mascot trong suốt, nhãn môn generic, onboarding và hướng dẫn F1.
- [ ] Thử OCR tiếng Việt và giọng Việt trên máy đã cài gói Windows tương ứng.

## M8 — Độ bền và phát hành

- [x] Bộ cài theo tài khoản có manifest/hash, gói model riêng và hướng dẫn cài/gỡ; bản portable kèm model.
- [x] Asset/font/student web local, đường dẫn Unicode; unit/integration cho migration/backup/pack hỏng/duplicate/recovery.
- [x] Hướng dẫn ngắn, dữ liệu hiệu năng local, STATE/DECISIONS/schema và hồ sơ kết quả cập nhật RC2.
- [x] Hiển thị 125% trên máy phát triển; cửa sổ lớp toàn màn hình trên màn hình phụ Samsung, không QML warning.
- [x] Nâng cấp RC1→RC2 và gỡ trên máy phát triển, thư viện thử vẫn còn; executable RC2 và pipeline đóng gói qua kiểm tra.
- [x] RC3: sáu tab Cài đặt; hồ sơ thầy cô/trường/lớp có thể hiện trên màn chiếu và deck xuất; mức mặc định L0–L4; nghe thử giọng EN; mặc định lớp; sao lưu trong tab Dữ liệu. Luồng Qt và lưu lại sau mở thư viện qua kiểm tra.
- [x] RC4: thay hồ sơ lớp/level toàn cục bằng nhiều môn và logo trường; chọn khối/level/bố cục theo bài, tên lớp theo tiết; bốn kiểu hiển thị đồng bộ màn dạy và deck xuất. Luồng Qt và bộ kiểm tra dữ liệu riêng đã qua.
- [x] RC5: logo ngay sau ô bộ môn; xem trước hồ sơ đã lưu; Mascot tôn trọng ẩn/hiện, cỡ và trái/phải trên màn chiếu, cỡ ở bàn điều khiển/cửa sổ nổi. Kiểm tra qua luồng Qt.
- [x] RC6: năm giọng Kokoro English offline cùng một model, nghe thử và cache WAV; bộ cài giữ model và license.
- [x] RC7: tab Mascot có thẻ vai trò Milo/Lumi, bản xem trước bối cảnh và tùy chọn hiện khi giải thích/quiz; luồng Qt kiểm tra màn dạy và bố cục hẹp.
- [x] RC8: chín giọng offline gồm bốn VieNeu tiếng Việt và năm Kokoro English; chọn cặp giọng, nghe thử và chuẩn bị WAV; bộ 10 icon điều hướng; lưu Mascot hiện/ẩn cửa sổ nổi ngay và có nút mở lại. Bản `.exe` qua 8 nhóm pipeline.
- [x] RC9: tiếp nhận 19 icon thao tác, gắn chọn lọc cho các nút soạn bài, thuật ngữ, giọng đọc, lớp học và báo cáo; nhãn chữ và luồng cũ giữ nguyên. Luồng Qt 12 bước soạn bài và 8 nhóm Cài đặt qua kiểm tra.
- [x] RC10: mascot nổi mặc định không khung, chỉ hiện nhân vật; nhấp để mở bảng nút và phản hồi, nhấp lại để thu. Kiểm tra ảnh alpha, tương tác chuột, cài đặt và lớp học trên giao diện nguồn.
- [ ] Nếu muốn giống mockup Mascot đầy đủ: thiết kế bộ phụ kiện/trang phục riêng từng môn và kiểm chứng trực tiếp trong tiết dạy thật; hiện RC7 chỉ có nhãn môn.
- [ ] Nghiệm thu cài/nâng cấp/gỡ trên Windows sạch không Python.
- [ ] Chặn Internet giữ LAN, DPI/nhiều màn hình/máy chiếu, điện thoại và router thật.
- [ ] Trọn tiết với giáo viên nhiều nhóm môn và sĩ số mục tiêu; xác nhận không có lỗi chặn dạy.
- [ ] Đánh dấu phát hành V1 sau khi có bằng chứng thực địa; RC7 hiện phục vụ dùng thử và sửa từng phần.

Không hạ tiêu chí Windows sạch/điện thoại/giáo viên thành kiểm tra loopback. Mã nguồn các nhóm tính năng đã có; hoàn tất toàn bộ kế hoạch còn bao gồm những mục nghiệm thu chưa đánh dấu trên.
