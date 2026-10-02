# Đề xuất nâng cấp BiliClass: tài liệu nguồn → bài giảng song ngữ

Ngày 02/10/2026. Trạng thái: **đề xuất nền; một phần luồng đã bắt đầu triển khai trong mã nguồn RC11**. Đã tách ý PPTX theo khối chữ, giữ ảnh thường khi xuất, ghép cặp VI/EN khi phân trang, có lựa chọn kiểu bài và chốt chuẩn bị trước khi mở lớp mới. Chưa có engine bố cục tám nhóm, ghép đầu vào song ngữ tự động, OCR Việt độc lập Windows hay gói môn. Kết hợp ba tài liệu người dùng gửi về mẫu bài giảng, offline và dữ liệu theo môn với kế hoạch vận hành ngày 01/10. Những đoạn “Giao Codex” trong tài liệu là nội dung tham khảo, không tự động trở thành yêu cầu thực thi.

Phạm vi giữ nguyên toàn bộ tab Cài đặt, đặc biệt Chung, Song ngữ, Giọng đọc và Mascot. Đề xuất liên quan phát âm/ngữ cảnh trợ giảng nằm ở dữ liệu bài học và luồng dạy; không làm lại giao diện cấu hình hay nhân vật.

## 1. Hướng sản phẩm đề xuất

**Một bài học có cấu trúc, nhiều cách dạy; nội dung bám vào nguồn giáo viên cung cấp.**

- Luồng đầy đủ: nhập nguồn → kiểm tra trích xuất → tạo cặp Việt–Anh → duyệt → dựng bài theo mẫu và Level → chuẩn bị → dạy → báo cáo.
- Hai cách trình chiếu trong V1: bài theo mẫu BiliClass và PowerPoint gốc với trợ giảng đi kèm. Bản theo mẫu là hướng chính cho trải nghiệm L0–L4 đầy đủ, đồng thời có thể dạy khi không cài PowerPoint.
- Với PPTX, đưa hai bản xem trước dễ so sánh, giữ nguồn gốc và ưu tiên gợi ý giữ bản gốc nếu có nhiều hiệu ứng/video/đối tượng khó tái tạo. Word/PDF/ảnh/text được gợi ý dựng theo mẫu. Giáo viên được đổi lựa chọn.
- Đề xuất lõi không có chi phí API bắt buộc, chạy offline sau khi cài đủ tài nguyên. Tài liệu học không cần gửi ra dịch vụ bên ngoài. Đây là mục tiêu phải nghiệm thu, chưa phải kết luận toàn bộ khả năng hiện tại đã đạt.
- “Enhance My Slides” — sửa trực tiếp bố cục PowerPoint để chèn song ngữ — để sau V1, thử trước trên tập slide đơn giản. Không thêm lựa chọn này khi chưa có kết quả đáng tin cậy.

Giữ slide Việt nguyên trạng không thể làm tiếng Việt biến mất ở L4. Chế độ này chỉ áp Level cho phần trợ giảng thêm vào. Màn hình cần nói rõ giới hạn; không gắn nhãn “English First” đầy đủ nếu chữ Việt trên nguồn vẫn hiện. Xem trước bằng ảnh slide cũng không tương đương chạy được hiệu ứng hoặc video gốc.

## 2. Phần kế thừa được và khoảng trống thực tế

| Mã hiện có | Có thể dùng lại | Cần nâng |
|---|---|---|
| `app/importers.py` | Nhập nhiều định dạng, nguồn tham chiếu, cảnh báo đối tượng | PPTX đang gom chữ theo slide; cần giữ hình, bảng, thứ tự, công thức và liên kết của chúng với ý đang dạy |
| `app/translation.py`, `app/text_quality.py` | Dịch local, bảo vệ ký hiệu/thuật ngữ, báo đoạn quá dài | Dịch theo câu/ý đã ghép nguồn, xử lý đầu vào đã song ngữ, tái sử dụng kết quả theo phiên bản |
| `app/presentation_policy.py` | Bốn layout hiện có, quy tắc trợ giảng theo Level | Hiện ẩn/hiện Việt–Anh chủ yếu do layout quyết định; cần quy tắc gợi ý Level–layout ở từng bài, có override rõ ràng |
| `app/deck_export.py` | Xuất PPTX mới có thể sửa, không đè nguồn | Hiện thiên về chữ; cắt VI/EN độc lập theo số ký tự có thể làm lệch cặp ý. Cần chung kế hoạch phân trang theo nội dung và đo kích thước chữ |
| `app/ocr.py` | OCR local và dựng trang PDF bằng PDFium | Hiện phụ thuộc gói OCR Windows đã cài; cần lựa chọn OCR Việt đóng gói được và kiểm thử ảnh thực tế |
| `app/library.py`, `app/ui.py` | Thuật ngữ theo môn và dùng lại bản dịch đã duyệt | Scope theo bài/giáo viên/gói, sửa thuật ngữ theo ID, xử lý xung đột và phiên bản gói |
| `app/pack.py`, `app/model_packs.py` | Gói bài, gói dịch, kiểm tra cấu trúc/hash | Mở rộng có version cho nguồn đa tài liệu, tài sản hình và snapshot thuật ngữ; không tạo thêm hệ lưu trữ song song |

Đây là đối chiếu mã nguồn, chưa chạy nghiệm thu thiết bị trong lượt đánh giá này.

## 3. Cấu trúc bài là nền chung, không phải một model AI

Tên kỹ thuật “Lesson DNA” có thể dùng trong tài liệu nội bộ. Giáo viên chỉ cần thấy **Cấu trúc bài**.

```text
Nguồn gốc + hình/bảng/công thức + vị trí trong nguồn
                         ↓
Khối nội dung có ID: ý, cặp Việt–Anh, tài sản, trạng thái duyệt
                         ↓
Cấu trúc bài đã xác nhận
                         ↓
Kiểu dạy + hình thức trình bày + Level + bố cục song ngữ
                         ↓
Kế hoạch trình chiếu chung → trình chiếu trong app / PPTX xuất
```

Mỗi block cần có ID bền, thứ tự, loại nội dung, nguồn và vị trí, cặp ngôn ngữ tương ứng, hình/công thức liên quan, trạng thái duyệt, lịch sử sửa. Câu hỏi có đáp án riêng, hỗ trợ/phát âm có nội dung riêng. Block là đơn vị nội dung; slide là đơn vị hiển thị. Một block có thể cần nhiều slide, một slide có thể chứa vài block ngắn.

Thêm bảng kê sau nhập: những phần đã trích được, phần giữ dạng hình, phần cần giáo viên xử lý. Tránh mất hình/công thức âm thầm khi bản dịch chữ vẫn thành công. Nội dung không chắc loại nào giữ nhãn “Chưa phân loại”, cho đổi bằng một thao tác.

Quy tắc như chữ lớn hoặc dấu hỏi chỉ cung cấp tín hiệu. Chúng không chứng minh đó là tiêu đề hay câu hỏi học tập. Phân loại gợi ý phải giữ nguyên văn và vị trí nguồn; điểm tin cậy kỹ thuật không thay thế duyệt chuyên môn.

Một bài có thể tham chiếu PPTX chính và PDF/ảnh bổ sung. Khi hai nguồn khác nhau về định nghĩa, số liệu hoặc đáp án, hiển thị để giáo viên chọn; không tự ghép thành một khẳng định mới. Tài liệu nguồn xác định phạm vi bài, không tự bảo đảm mọi nội dung trong đó đều đúng.

Với đầu vào đã song ngữ, giữ các bản có sẵn, gợi ý ghép đúng cặp rồi dịch phần còn thiếu. Không dịch lại toàn bộ hoặc tự coi cặp có sẵn là đã duyệt. Bản dịch khác nghĩa cần đánh dấu để đối chiếu.

## 4. Ba kiểu dạy dùng chung thư viện bố cục

| Kiểu dạy | Ưu tiên | Điều kiện |
|---|---|---|
| Chuẩn lớp học | Khái niệm → minh họa → luyện tập khi có | Mặc định, dùng rộng cho nhiều môn |
| Trực quan | Hình, sơ đồ, tiến trình, chú thích | Chỉ gợi ý khi có hình phù hợp hoặc giáo viên bổ sung |
| Luyện tập & tương tác | Ví dụ → bước làm → bài tập → kiểm tra | Chỉ dựng phần có nội dung và đáp án đủ để duyệt |

Ba kiểu trên là cách chọn/sắp các khối. Theme là màu, font, khoảng cách. Layout song ngữ là cách đặt hai ngôn ngữ. Level là mức hỗ trợ/ngôn ngữ xuất hiện. Giữ chúng độc lập trong dữ liệu nhưng UI tự gợi ý để giáo viên không phải chỉnh nhiều thông số.

Làm trước tám nhóm bố cục: (1) mở bài/mục tiêu, (2) thuật ngữ, (3) khái niệm/giải thích, (4) hình và chú thích, (5) công thức/quy tắc, (6) ví dụ theo bước, (7) luyện tập/câu hỏi, (8) tổng kết. Sau đó mở rộng so sánh, timeline, quy trình và các biến thể khác để đạt 12–14 nhóm khi có nhu cầu kiểm chứng. Không cần làm 30–36 slide mẫu độc lập ngay đầu.

Preset không bắt mọi bài có đủ tám phần. Nguồn không có mục tiêu, lời giải, quiz hoặc tổng kết thì bỏ phần đó hoặc để giáo viên bổ sung. Câu luyện tập chưa có lời giải không được tự đổi thành “ví dụ đã giải”.

Yêu cầu chất lượng trình chiếu:

- VI/EN phân trang cùng đơn vị ý; không cắt riêng mỗi ngôn ngữ theo ký tự.
- Đo chữ theo vùng bố trí, font và tỷ lệ màn hình; chia trang trước khi giảm xuống dưới cỡ chữ tối thiểu đã thử trên máy chiếu.
- Giữ công thức/mã nguồn/số liệu nguyên dạng. Công thức khó chuyển giữ hình hoặc bản gốc để đối chiếu; không giả nhận dạng thành công.
- Hình có chú thích/nguồn; sơ đồ gốc không được thay bằng hình trang trí không cùng nội dung.
- Dùng chung kế hoạch bố cục cho app và PPTX; vẫn cần so sánh bản render do hai bộ hiển thị có thể khác font/ngắt dòng.

Một bài trong app đổi Level mà không phải tạo lại nội dung đã duyệt. PPTX xuất là bản chốt theo Level và thời điểm xuất; không hứa một file PPTX có mọi tương tác động, mascot hay quiz LAN khi mở độc lập.

## 5. Level và thuật ngữ phải giữ đúng ý

Đề xuất gợi ý theo bài: L0 Việt + từ khóa Anh; L1 thêm cụm chỉ dẫn lớp học; L2 cặp ý Việt–Anh với Việt chính; L3 tăng phần Anh, Việt hỗ trợ; L4 Anh chính, Việt khi cần. Đây là gợi ý, không đổi ngầm các bài cũ hay thiết lập hiện tại. Bốn layout sẵn có đủ để bắt đầu; chưa cần thêm layout thứ năm chỉ vì tên trong tài liệu khác.

Level không làm kiến thức môn học dễ hơn và không chỉ là tỷ lệ phần trăm chữ Anh. Đổi layout không làm mất duyệt nội dung; chỉ cần kiểm tra lại bố cục/bản chuẩn bị. Tạo câu giải thích mới hoặc rút gọn ý là thay đổi nội dung và cần duyệt. L2 thiếu bản Anh đơn giản đã duyệt thì dùng bản dịch đầy đủ với nhãn khả năng rõ ràng, không tự báo đã đơn giản hóa.

Gói dữ liệu nên có bốn tầng: ngôn ngữ chung, mẫu câu lớp học, dữ liệu theo môn, dữ liệu bài hiện tại. Gói theo môn chứa thuật ngữ/cách đọc/ký hiệu/gợi ý phân loại và bố cục; không cần nhét toàn bộ sách giáo khoa. Thiếu gói môn vẫn dùng được nguồn và bộ dịch chung.

Không áp một chuỗi ưu tiên cứng cho cả kiến thức và dịch thuật:

1. Nội dung đã được giáo viên duyệt/khóa trong bài là bản đang dùng; không tự ghi đè khi cài gói mới.
2. Khi tạo bản dịch mới, lựa chọn khóa riêng của bài/giáo viên là ràng buộc thuật ngữ.
3. Dùng lại bản dịch đã duyệt cùng môn và ngữ cảnh nếu không xung đột các ràng buộc đó; gần giống chỉ là gợi ý.
4. Thuật ngữ môn, thuật ngữ chung và model bổ sung phần thiếu. Xung đột phải được hiển thị, không âm thầm thay một cụm trong câu cũ.

Một lần sửa câu không tự cập nhật toàn môn. Cho chọn “Chỉ bài này” hoặc “Lưu vào thuật ngữ của tôi”. Gói chia sẻ có phiên bản, tác giả/nguồn và điều kiện phân phối; phần sửa riêng của giáo viên nằm ngoài gói gốc để cập nhật không làm mất lựa chọn cá nhân.

Danh sách “Thuật ngữ cần kiểm tra” nên đưa ứng viên có vị trí nguồn và lý do, không nhận vơ đã tìm được mọi thuật ngữ. Không hiển thị phần trăm tin cậy nếu chưa có cách đo phù hợp.

Nội dung nhìn thấy và lời đọc tách riêng. Ví dụ giữ `x²` trên slide, nhưng lời đọc là bản đã chọn theo ngôn ngữ/ngữ cảnh. Bản đọc là dữ liệu của block; đổi cách đọc chỉ làm hết hiệu lực audio liên quan. Giai đoạn đầu dùng hai engine hiện có và quy tắc đã duyệt, không nâng cấp tab Giọng đọc.

## 6. Trợ giảng và quiz có nguồn cụ thể

Nút “Giải thích” ưu tiên nội dung đã duyệt liên kết trực tiếp với block đang dạy. Chỉ dùng tìm kiếm khi giáo viên cần tìm rộng hơn trong bài; kết quả cho thấy đoạn nguồn trước khi chọn. Không tự lấy kết quả đứng đầu thay cho lời giải thích của block hiện tại.

SQLite FTS5/BM25 là lựa chọn đáng thử cho tìm trong bài. Cần kiểm tra runtime có FTS5 và xử lý dấu tiếng Việt/alias; BM25 xếp hạng theo từ, không chứng minh câu trả lời đúng nghĩa. Nếu không có kết quả phù hợp, cho biết phần đó chưa được chuẩn bị. Chỉ tìm trong bài/revision hiện hành và nội dung được phép hiện; đáp án chưa công bố không đi vào màn học sinh.

V1 có thể gợi ý câu hỏi điền từ/ghép thuật ngữ từ cặp đã duyệt. Câu hỏi suy luận, phương án nhiễu, ví dụ mới và lời giải mới cần giáo viên soạn hoặc duyệt một đề xuất riêng. Quy tắc không thay được kiến thức chuyên môn. Không tự suy ra misconception từ một đáp án sai chưa có ánh xạ do giáo viên xác nhận.

Local LLM là phần mở rộng sau này. Nó có thể gợi ý phân loại/tóm tắt nhưng vẫn phải tuân cùng cấu trúc dữ liệu và quy trình duyệt; không cần cấm tuyệt đối LLM tham gia điền dữ liệu. Core không phụ thuộc có cài model này hay không.

## 7. Offline, tài nguyên và đóng gói

Mục tiêu đúng là **không phí API bắt buộc**, không phải “không tốn gì”. Tải/cài tài nguyên một lần, dung lượng, RAM/CPU và lựa chọn Office vẫn là các yếu tố thực tế. Chưa chốt con số bộ cài 1–3 GB hoặc tốc độ khi chưa đo đúng gói model/backend.

- Giữ `pypdf` + `pypdfium2` hiện có làm điểm xuất phát, không thay bằng PyMuPDF chỉ vì tài liệu gợi ý. PyMuPDF có lựa chọn AGPL hoặc giấy phép thương mại; quyết định phân phối phải được đánh giá riêng.
- Đánh giá Tesseract kèm dữ liệu Việt/Anh để bổ sung OCR độc lập gói Windows. Có hỗ trợ ngôn ngữ không có nghĩa đọc chuẩn công thức, bảng hoặc ảnh chụp xấu. Kiểm thử nguồn thực tế và giữ đường chọn/cắt vùng thủ công.
- Chuẩn bị bản cài qua USB gồm app + các gói dữ liệu cần thiết. Model, tokenizer, bộ âm vị, voice và font phải có sẵn; không được dựa vào cache tài khoản máy phát triển.
- Internet tắt vẫn dạy được. Quiz nhiều điện thoại cần LAN/Wi-Fi nội bộ; không đồng nghĩa tắt tất cả mạng. Chế độ theo mẫu trong app không bắt buộc cài Office; PowerPoint gốc có yêu cầu riêng của PowerPoint.
- OCR/dịch/render/audio chạy qua hàng đợi có tiến độ, hủy và thử lại theo phần. Với máy 8 GB, tránh nạp đồng thời tất cả model; thử batch dịch trong một job và giải phóng khi xong.
- Cache theo nội dung + phiên bản engine/gói thuật ngữ/quy tắc liên quan. Đổi theme không dịch lại, đổi Level không OCR lại, đổi một câu chỉ tạo lại phần phụ thuộc. Không tự áp gói thuật ngữ mới vào bài đang dạy.
- Gói `.biliclass` chứa nguồn/tài sản/nội dung đã duyệt và dữ liệu cần để tái lập bài; gói môn có thể dùng `.bilipack` nhưng phải có loại/phiên bản/schema/hash rõ. Gói môn là dữ liệu, không tải mã thực thi. Model/voice pack và dữ liệu học sinh có vòng đời riêng, không mặc nhiên đi cùng gói bài.

Nghiệm thu offline trong môi trường kiểm thử cô lập, không đổi firewall máy người dùng: chặn Internet cho app và worker nhưng giữ loopback/LAN; dùng hồ sơ sạch và gói cài đã chuẩn bị; chạy từ lần mở đầu đến báo cáo. Mô phỏng lời gọi mạng trong unit test là chưa đủ. Thử thiếu từng gói để app báo đúng khả năng; chạy bộ đầy đủ khi tất cả gói đã cài. Không khẳng định máy 8 GB đạt nếu mới đo trên máy RAM lớn.

## 8. Thứ tự triển khai điều chỉnh từ P0–P4

| Mốc | Kết quả phải nhìn thấy | Điều kiện qua |
|---|---|---|
| P0 — Nền dữ liệu và trạng thái | Bài, block, revision, phiên lớp và bản chuẩn bị thống nhất; sơ đồ dữ liệu mới có đường nâng từ bài cũ | Migration/backup trên bản sao; giữ ID/duyệt/nguồn/báo cáo cũ; phiên đã kết thúc không thay đổi |
| P1a — Nhập và đối chiếu | Một PPTX và một tài liệu chữ dựng được cấu trúc, giữ hình/công thức/đọc đúng thứ tự | Không mất phần nguồn âm thầm; ghép VI/EN sẵn có; giáo viên sửa phân loại/tách/gộp được |
| P1b — Một mẫu chạy hết luồng | Mẫu Chuẩn lớp học từ nhập → duyệt → L0–L4 → chiếu → xuất PPTX | Cặp ý cùng trang, không tràn chữ, không cần PowerPoint để dạy trong app; sửa một ý không làm lại cả bài |
| P1c — Mở rộng có chứng cứ | Ba kiểu dạy dùng chung tám nhóm bố cục; OCR Việt và ba gói môn thí điểm | Thử Toán, Sinh, Sử để bao phủ công thức, hình/quy trình và tường thuật; thiếu gói môn vẫn hoạt động |
| P2 — Chuẩn bị và offline | Manifest có revision, nguồn, nội dung, tài nguyên và khả năng dạy thực tế | Full flow offline với hồ sơ sạch; thiếu audio/quiz vẫn có chế độ dạy phù hợp; benchmark RAM/latency thật |
| P3 — Lớp học và trợ giảng | Tất cả cửa sổ theo đúng block và session; quiz dùng lại hệ LAN | Chuyển slide/block không phát sai nội dung; reconnect không nhân đôi; đáp án chỉ hiện đúng lúc |
| P4 — Thư viện, báo cáo, gói chia sẻ | Thuật ngữ/CSV, cài gói có preview xung đột, tìm trong bài, báo cáo nối bài/revision | Cập nhật gói không ghi đè sửa riêng; báo cáo cũ nguyên vẹn; bài chia sẻ tái lập được nội dung đã chốt |

Trước P1c không cần làm đủ mười gói môn hoặc 14 loại slide. Một luồng mẫu thật chạy tốt quan trọng hơn số lượng template. Các ca nghiệm thu bổ sung: PDF scan Việt với công thức, đầu vào đã song ngữ nhưng đảo thứ tự, slide chữ dài, ảnh có chữ Việt ở L4, nguồn có video, thiếu font, đổi model/thuật ngữ sau khi đã chuẩn bị bài.

## Nguồn kiểm chứng và tài liệu tham khảo

Ba tệp người dùng gửi ngày 02/10/2026:

- “Có, nhưng mình không khuyên tạo 3 file PowerPoint cố định…” — attachments/d4735d82-891e-425f-83e5-b4bc13987061/Pasted text.txt.
- “Có. BiliClass hoàn toàn có thể được thiết kế để không phụ thuộc API trả phí…” — attachments/3739ca4a-128f-4fdd-9364-a9a632ebb061/Pasted text.txt.
- “Không cần nạp toàn bộ kiến thức tất cả các môn…” — attachments/c48c0497-14e8-43ea-9c97-c7089a35e8a5/Pasted text.txt.

Nguồn chính thức đã đối chiếu cho các khả năng bên ngoài mã nguồn:

- [PyMuPDF: License and Copyright](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright): AGPL và lựa chọn giấy phép thương mại; không suy rộng kết luận cấp phép cho toàn bộ BiliClass.
- [Tesseract: dữ liệu ngôn ngữ theo phiên bản](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html): có dữ liệu `vie`/`eng`; độ chính xác trên bài giảng vẫn cần đo.
- [SQLite FTS5](https://www.sqlite.org/fts5.html): tìm toàn văn, tokenizer và BM25; kiểm tra có extension trong runtime đóng gói trước khi triển khai.

Không coi các ước lượng kích thước/tốc độ, khẳng định giấy phép tổng quát hay ví dụ sinh nội dung trong tài liệu tham khảo là kết quả đã kiểm chứng của sản phẩm.
