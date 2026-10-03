# Changelog

## Mã nguồn đang phát triển — 03/10/2026

- Đánh giá VI/EN/song ngữ/trộn/chưa rõ và hướng dịch từng đoạn; chọn giữ PPTX hoặc tạo bài theo mẫu. Gợi ý không tự duyệt cặp dịch.
- Bổ sung PPTX theo L0–L4: panel ở vùng trống hoặc trang hỗ trợ khi kín/hiệu ứng/xoay; giữ nguyên file hoặc slide Việt/Anh kế tiếp vẫn chọn được. L4 giữ VI Rescue trong dự án; template có bố cục Theo level.
- Dịch phần còn thiếu tối đa 50 đoạn/lượt; giữ cặp/đoạn khóa/duyệt, dùng thuật ngữ và memory giáo viên trước kho nền/model. Hủy hoặc revision đổi chặn áp dụng loạt cũ.
- So sánh render gốc/song ngữ bằng Office theo mapping slide; ảnh tĩnh không kiểm chứng hiệu ứng. Gói bài giữ thuật ngữ/giọng/mascot tham chiếu, không tự thay máy nhận.
- OCR Việt–Anh cục bộ có bước tải một lần và SHA-256; chạy ảnh/PDF scan/slide chỉ ảnh. Chữ OCR vẫn cần sửa dấu/bảng/công thức, không gửi tài liệu ra web. Bốn tab Cài đặt hiện tại được giữ nguyên.
- 171 kiểm thử và lint đạt, Qt smoke đạt; Office mở/render cả năm level, dịch loạt hai chiều và ảnh/PDF OCR Việt chạy bằng engine thật. Chưa nghiệm thu mọi môn/bài thật, chưa phát hành trong rc12. Xem [quy trình nhập bài](docs/INPUT_WORKFLOW.md).

## Mã nguồn đang phát triển — 02/10/2026

- Nhập PowerPoint mới mặc định giữ thiết kế gốc; ẩn chọn mẫu/loại slide để đơn giản hóa thao tác. Thêm xem và trình chiếu bản song ngữ gồm slide Việt/Anh kế tiếp, hoặc chỉ Anh/từ khóa.
- Bản Anh giữ đối tượng, bảng, biểu đồ và hiệu ứng nguồn; sao chép riêng dữ liệu biểu đồ để PowerPoint mở được. Bản dịch quá dài hoặc không khớp ô nguồn được báo trước khi ghi file. Cache bản xem theo nội dung/cấu hình và kiểm tra hash.
- Gói bài chia sẻ lưu cách trình bày; bài cũ giữ lựa chọn hiện tại. Trình chiếu song ngữ vẫn theo đúng đoạn của slide nguồn. Xem [hướng dẫn giữ thiết kế PowerPoint](docs/SOURCE_POWERPOINT.md).
- Thêm ba bộ mẫu Chuẩn lớp học, Trực quan và Luyện tập & tương tác, mỗi bộ có 14 slide PowerPoint tham khảo sửa được.
- Thêm hộp xem mẫu và lựa chọn loại slide trong màn soạn bài. Xem trước, trình chiếu và xuất PPTX dùng chung bố cục mẫu; cặp Việt–Anh dài được phân trang cùng nhau.
- Đổi loại slide giữ nội dung và trạng thái duyệt, nhưng yêu cầu chuẩn bị lại bài. Gói bài chia sẻ giữ lựa chọn mẫu và loại slide.
- Mẫu chỉ bố trí nội dung do giáo viên cung cấp; chưa tự tạo mục tiêu, lời giải hoặc quiz. Xem [hướng dẫn mẫu bài giảng](docs/TEMPLATES.md).
- Đã kiểm tra 138 bài kiểm thử, Qt smoke và hiển thị 42 slide mẫu. Các thay đổi này chưa nằm trong bản phát hành rc12.
- Sau khi thêm chế độ giữ PowerPoint: 143 bài kiểm thử và kiểm tra mã đều đạt; Qt smoke xác nhận luồng nhập/biên tập và liên kết slide song ngữ. Microsoft PowerPoint mở/render bộ thử 6 slide, với cả 3 slide Việt giống hệt render nguồn. Chữ trong ảnh/biểu đồ chưa tự dịch; cần kiểm tra bài thật trước khi dạy.

## 1.0.0rc12 — 02/10/2026 — bản thử public

- Thêm kiểm tra phiên bản và cập nhật tự động từ GitHub Releases cho bản Windows đóng gói.
- Gói cập nhật được kiểm tra kích thước, SHA-256, manifest và đường dẫn trước khi cài.
- Cài phiên bản mới cạnh bản cũ, giữ thư viện bài học trong `%LOCALAPPDATA%/BiliClass` và tự mở bản mới.
- Cập nhật hướng dẫn cài lần đầu, chia sẻ cho giáo viên thứ hai và quy trình phát triển nhanh từ mã nguồn.

## 1.0.0rc11 — 02/10/2026 — bản thử nội bộ

- Một slide PowerPoint có nhiều khối chữ/bảng được nhập thành nhiều ý để giáo viên dịch và duyệt riêng; bản xuất giữ ảnh thường từ cả slide chỉ có hình. Cặp Việt–Anh được phân trang cùng nhau, đoạn quá dài yêu cầu tách trước khi xuất.
- Bài có lựa chọn kiểu trình bày Chuẩn lớp học/Trực quan/Luyện tập. Bản xuất dùng màu riêng theo lựa chọn; chưa tự suy diễn nội dung, lời giải hay thiết kế lại slide gốc.
- Bản chuẩn bị gắn với revision và hash nguồn; sửa bài làm bản chuẩn bị cũ hết hiệu lực. Mở lớp mới cần duyệt đủ và chốt bản hiện tại; thiếu audio/quiz vẫn dạy bằng chữ. Mở lại phiên cũ dùng snapshot cũ.
- Chọn bài ngay trong Lớp học; báo cáo hiển thị bài, môn, khối, level, revision và có đường về bài gốc; Trang chủ hiện tiết gần đây.
- Kiểm thử mã nguồn và giao diện thực thi trên máy phát triển; chưa nghiệm thu máy thứ hai, Wi-Fi trường hoặc chất lượng dịch/giọng tại tiết dạy thật.

## 1.0.0rc10 — 01/10/2026 — dùng thử

- Trợ giảng nổi mặc định chỉ hiện nhân vật trên nền trong suốt, không viền cửa sổ. Nhấp Milo hoặc Lumi mới mở bảng thao tác; nhấp lại để thu gọn, có nút Ẩn và mở lại từ thanh bên.
- Bảng trợ giảng chỉ mở vùng phản hồi sau khi chọn hành động; mascot có nhịp nổi nhẹ và tôn trọng tùy chọn Giảm chuyển động. Đây vẫn là bốn tư thế ảnh, chưa phải animation nhân vật có khớp riêng.

## 1.0.0rc9 — 01/10/2026 — dùng thử

- Tiếp nhận 19 icon thao tác do người dùng cung cấp, dùng ở các nút phù hợp trong màn soạn bài, thuật ngữ, giọng đọc, lớp học và báo cáo. Nhãn chữ và hành vi nút được giữ nguyên.
- Nút sửa, xóa, lưu nháp, phát, tải lên/xuống, tìm, xem, học sinh và làm mới có biểu tượng rõ hơn. Các biểu tượng chưa có vị trí phù hợp được giữ trong thư viện asset cho lần thiết kế tiếp theo.

## 1.0.0rc8 — 01/10/2026 — dùng thử

- Thêm bốn giọng Việt VieNeu v3 Turbo (nữ Bắc/Nam, nam Bắc/Nam) chạy CPU offline; năm giọng English Kokoro vẫn được chọn riêng. Cài đặt có nghe thử từng giọng Việt, câu mẫu riêng và bốn bộ giọng Việt–Anh gợi ý.
- Bộ model VieNeu và codec MOSS được đóng kèm bản portable; ứng dụng bật chế độ Hugging Face offline trước khi nạp. Bộ nhớ thử nghiệm khoảng 1,1–1,3 GB riêng cho tiến trình tổng hợp VieNeu. Khuyến nghị chuẩn bị âm thanh trước giờ dạy.
- Chưa bật voice cloning hoặc tự phân tích ngôn ngữ trong một câu. Bài học đã có cặp đoạn VI/EN rõ ràng, nên nút đọc từng ngôn ngữ định tuyến đến đúng engine.

## 1.0.0rc7 — 01/10/2026 — dùng thử

- Thiết kế lại tab Mascot: thẻ Milo/Lumi thể hiện vai trò khi dạy, trạng thái chọn rõ, mẫu slide thay đổi theo mascot và bối cảnh slide/giải thích/quiz. Nút xem trên slide đưa người dùng tới mẫu xem trước cả ở màn hình hẹp.
- Thêm tùy chọn hiện mascot khi giải thích và khi quiz; áp dụng trong màn chiếu, bàn điều khiển và trợ giảng nổi theo đúng bối cảnh. Vị trí, cỡ, nhãn môn và trạng thái hình phản ánh ngay trong bản xem trước trước khi lưu.
- Giọng nghe thử dùng giọng English đã chọn ở tab Giọng đọc, không gắn cứng vào nhân vật. Phụ kiện hiện tại là nhãn môn; chưa có bộ trang phục hoặc animation riêng cho từng môn.

## 1.0.0rc6 — 30/09/2026 — dùng thử

- Thêm năm giọng English Kokoro 82M v1.0 chạy CPU hoàn toàn offline: Emma/Bella/Michael (Mỹ), Emma/George (Anh). Mỗi giọng có nghe thử riêng, chọn giọng độc lập với mascot; tốc độ và cache WAV gắn với đúng voice/model.
- Một model dùng chung được đóng trong bản portable và installer. Các đoạn đã duyệt có thể chuẩn bị audio trước khi dạy; SAPI Windows vẫn phục vụ tiếng Việt nếu máy có giọng phù hợp.
- Kiểm tra tạo mẫu cả năm giọng khi chặn socket mạng, thời gian nạp/đọc, cache; kèm thông báo giấy phép Kokoro/sherpa/ONNX Runtime/eSpeak NG. Bản này vẫn cần giáo viên đánh giá cảm nhận và phát âm thuật ngữ thực tế.

## 1.0.0rc5 — 30/09/2026 — dùng thử

- Tab Chung đưa nút tải/bỏ logo lên ngay sau Bộ môn giảng dạy, trước nút Lưu thông tin. Ô xem trước đọc hồ sơ đã lưu (tên, trường, bộ môn, logo và trạng thái hiện/ẩn), không phản ánh nháp chưa lưu.
- Mascot trên màn chiếu tôn trọng ẩn/hiện, trái/phải, kích thước, nhãn môn và giảm chuyển động; kích thước cũng áp dụng trong bàn điều khiển và cửa sổ trợ giảng nổi.
- Kiểm tra lại luồng Cài đặt, soạn bài và dạy/lớp với thư viện riêng, không thay RC4 đang mở.

## 1.0.0rc4 — 30/09/2026 — dùng thử

- Hồ sơ Chung lưu nhiều bộ môn và logo trường; môn/khối chọn cho từng bài, tên lớp nhập khi mở tiết. Giá trị lớp/level toàn cục của bản cũ không còn tự áp vào bài mới.
- Song ngữ trong Cài đặt giải thích L0–L4 và bốn kiểu trình bày. Chọn level và bố cục khi tạo từng bài, vẫn đổi được khi biên tập.
- Bốn kiểu hiển thị và PowerPoint xuất thống nhất: từ khóa Anh cùng dòng Việt, hai dòng với Anh in nghiêng, hai cột Việt–Anh hoặc English toàn phần kèm VI Rescue. Từ khóa chỉ chèn khi khớp thuật ngữ do giáo viên chuẩn bị.
- Logo hiện ở xem trước, màn lớp và PowerPoint khi bật hồ sơ, được sao lưu cùng thư viện. Sửa bố cục trình biên tập ở màn 1366×768.

## 1.0.0rc3 — 30/09/2026 — dùng thử

- Cài đặt được chia thành Chung, Song ngữ, Giọng đọc, Mascot, Lớp học và Dữ liệu.
- Hồ sơ giáo viên/trường/lớp có thể hiển thị trên màn bài giảng và deck xuất, hoặc ẩn; level mặc định L0–L4 cho bài mới, bài L5 cũ vẫn mở được.
- Nghe thử giọng English ngoại tuyến, chọn mascot và thông số lớp học mặc định; dữ liệu giữ chức năng sao lưu/khôi phục và gói dịch.
- Kiểm tra thao tác sáu tab bằng thư viện riêng, không thay đổi thư viện đang dùng.

## 1.0.0rc2 — 30/09/2026 — dùng thử

- Phiên lớp đã lưu tự chọn cổng mới khi cổng cũ bị chiếm, cập nhật QR và hướng dẫn mã khôi phục. Danh tính/chỗ ngồi/câu đã trả lời được giữ.
- Thử hiển thị 125% và toàn màn hình trên màn hình phụ thật của máy phát triển; kiểm tra nâng cấp RC1→RC2 với thư viện bài riêng.
- Đóng gói bản mới ở `dist/rc2` để người dùng đang mở RC1 không bị gián đoạn.

## 1.0.0rc1 — 30/09/2026 — dùng thử

- Dịch hai chiều offline, bảo vệ số/biểu thức/thuật ngữ, memory duyệt theo môn và lựa chọn gợi ý gần giống; đủ 24 tổ hợp level/layout.
- Trợ giảng và quiz do giáo viên chuẩn bị/duyệt; PowerPoint companion, màn hình lớp riêng, Milo/Lumi bốn tư thế và trợ giảng nổi.
- Lớp học LAN/QR, trang học sinh, ba loại câu hỏi, ACK/chống đếm trùng, đổi lựa chọn/reconnect/mã khôi phục, công bố đáp án theo giáo viên.
- Báo cáo có mẫu số, concept/recheck/so sánh ngôn ngữ có điều kiện, CSV tổng hợp và từng phản hồi.
- OCR ảnh/PDF scan Windows cách ly tiến trình, deck song ngữ mới, Lesson Pack v3 kèm âm thanh portable, backup/migration/khôi phục và log.
- Bộ cài theo tài khoản, gói model kiểm tra hash nạp từ USB, hướng dẫn F1 và tài liệu RC1.
- Sửa lỗi cửa sổ hướng dẫn mở muộn che thao tác, Uvicorn cần console trong bản windowed, lựa chọn học sinh khi mất mạng và origin khi mở lại phiên.
- 109 tests, 12 bước soạn bài Qt, 9 nhóm dạy/lớp Qt; pipeline 7 nhóm của executable và bản cài đã qua trên máy hiện tại. Chưa nghiệm thu Windows sạch/điện thoại/máy chiếu/mạng trường/giáo viên thật; xem docs/APP_RESULTS.md.

## 0.3.0 — 29/09/2026 — nội bộ

- Giọng SAPI Windows theo ngôn ngữ và tốc độ, nghe preview, chuẩn bị cache WAV cho đoạn đã duyệt.
- Kiểm tra chuẩn bị bài: nguồn, review, giọng và audio độc lập, không yêu cầu quiz/LAN.
- Hủy tác vụ tại ranh giới bước xử lý, không áp dụng kết quả muộn sau hủy.
- Preview toàn màn hình, dừng audio khi đóng/chuyển đoạn.
- 57 tests dữ liệu và 10 bước workflow Qt đã qua trên máy hiện tại.

## 0.2.0 — 29/09/2026 — nội bộ

- Thư viện bài local SQLite v2; migration v1; môn/khối/cấp tự nhập.
- Nhập PPTX/DOCX/PDF text/TXT và nội dung dán; nguồn tiếng Việt hoặc Anh.
- Builder song ngữ, dịch baseline local hai chiều, duyệt/khóa, snapshot gốc.
- Autosave nháp 1,8 giây, 30 revision gần nhất, restore và split đoạn.
- Glossary exact theo môn/giáo viên; chưa fuzzy/substitution.
- Preview văn bản với level/layout độc lập và VI Rescue.
- Pack draft v2 nhận v1, kiểm tra hash/đường dẫn, copy cần duyệt lại.
- Hình Milo/Lumi PNG trong suốt cho Home/Settings.
- Tests dữ liệu và luồng GUI; scripts đóng gói/kiểm tra executable.

Chưa hoàn thành M4/MVP/V1. Phạm vi và giới hạn cụ thể: docs/STATE.md.

## M0 — 29/09/2026

Workbench riêng thử Qt/PowerPoint/TTS/model/LAN và đóng gói. Quyết định tiếp tục nền tảng có điều kiện; kiểm thử thực địa còn mở.
