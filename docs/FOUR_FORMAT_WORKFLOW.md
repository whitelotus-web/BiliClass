# BiliClass: bốn kiểu chuyển đổi và kế hoạch thu gọn

Ngày 10/10/2026. Đây là quy trình trong mã nguồn hiện tại, chưa phải bộ cài RC12.

## Quy trình chính

Nhập giáo án/tài liệu → chọn **Kiểu chuyển đổi** → chọn giữ PowerPoint gốc hoặc mẫu BiliClass → Chuyển đổi → xem trình chiếu → xác nhận Dùng để dạy.

Kéo thả một tài liệu hoặc chọn tệp trên máy; cũng có thể dán nội dung. PPTX tối đa **200 MB**; DOCX/PDF/TXT/PNG/JPG tối đa **50 MB**. Đây là giới hạn của BiliClass; quyền tải tệp/lượt dùng của tài khoản web vẫn được kiểm tra riêng. Khi chọn được, hiện tên tài liệu và **Đã nhận tệp**. Nếu bị từ chối, lỗi hiện ngay ô tài liệu, giữ tệp trước và khóa nút chuyển đổi đến khi chọn lại/bỏ tệp, tránh gửi nhầm nguồn.

Thông tin gồm tên bài, môn, cấp học và khối. Chọn Tiểu học chỉ hiện khối **1–5**, THCS **6–9**, THPT **10–12**; đổi cấp sẽ chọn khối đầu tiên của cấp mới. Không nhập tự do khối ngoài cấp. Tên bài dài không làm co mất ô cấp/khối. Bốn kiểu chuyển đổi hiện thành bốn ô chọn, mỗi ô có **Xem mẫu bố cục**; xem mẫu không đổi lựa chọn cho đến khi bấm **Chọn kiểu này**.

**Môn học** chọn từ danh sách chung các môn của ba cấp, theo bảng chữ cái tiếng Việt. **Khác** ở cuối, hiện ô nhập tay cho môn chưa có. Môn chọn sẵn hoặc tên nhập tay dùng đúng trong prompt và bài lưu; không đổi môn theo cấp học. Xem phạm vi và nguồn trong [Danh sách môn học](SCHOOL_SUBJECTS.md).

**Thiết kế bài giảng** có hai ô chọn: **Giữ thiết kế PowerPoint gốc** hoặc **Tạo theo mẫu mới**. Có thể chọn giữ gốc trước khi nhập; khi có PPTX, dùng đúng bản sao PowerPoint đầu vào và yêu cầu bảo toàn thiết kế, hình, thứ tự slide và hiệu ứng, chỉ điều chỉnh ngôn ngữ/bố cục cần thiết cho phương pháp đã chọn. Không đủ chỗ/không giữ được hiệu ứng thì ChatGPT phải ghi CHECK để giáo viên kiểm tra. Tool không chứng nhận đầu ra giống nguồn 100% chỉ từ việc chọn ô này.

Mặc định giữ thiết kế PPTX; nếu giáo viên đã chọn mẫu mới trước khi nhập thì giữ lựa chọn đó. Word/PDF/ảnh/nội dung dán dùng mẫu mới vì không có thiết kế PowerPoint gốc. Khi tạo theo mẫu, chọn mẫu BiliClass và xem slide minh họa lớn.

Ô **Ghi chú thêm cho ChatGPT** không bắt buộc, nhận tối đa 6.000 ký tự. Các lưu ý được ghép đúng một lần vào mục **LƯU Ý BỔ SUNG CỦA GIÁO VIÊN**, sau phương pháp/thiết kế, giữ xuống dòng và lưu trong cấu hình yêu cầu. Không tự chép lời dặn lên slide; mâu thuẫn với phương pháp/thiết kế cần ghi CHECK. Quá giới hạn thì báo lỗi và khóa chuyển đổi, không cắt mất ghi chú.

Ô **Prompt gửi ChatGPT** có Hiện/Ẩn, cập nhật theo thông tin, kiểu chuyển đổi và thiết kế đang chọn. Dùng cùng bộ tạo prompt với yêu cầu gửi thật, gồm tên tệp gốc và đúng một phương pháp. Xem prompt không tạo gói hoặc mở browser. Nút **Chuyển đổi bài giảng** luôn nằm ở cuối màn hình; chỉ bật khi có tài liệu/nội dung, tên bài và môn.

Browser AI tự gửi prompt và bản sao tài liệu qua web ChatGPT đã đăng nhập, nhận PPTX, đọc ghi chú và chuẩn bị âm thanh Việt–Anh theo giọng đã lưu. Không còn “Tùy chọn thêm”, bộ chọn gửi/nhận thủ công hoặc bật/tắt chuẩn bị giọng trong luồng nhập mới. Yêu cầu thủ công đã lưu vẫn đọc được để không làm mất bài cũ. Không có lựa chọn API/OAuth/model dịch offline trong luồng nhập mới. Nếu web mất phiên/cần xác minh/hết lượt, tool giữ yêu cầu và thông báo để xử lý rồi tiếp tục; không cam kết tự vượt xác minh hoặc hạn mức.

Giới hạn PPTX 200 MB dùng đồng bộ khi chọn, tạo gói, đính kèm browser, tải/nhận kết quả và lưu nguồn. Vẫn giữ giới hạn kiểm tra ZIP 250 MB giải nén/10.000 entry; bộ nhập/trích xuất nội dung cũ giữ 50 MB. Gói bài portable có giới hạn tổng riêng; không đồng nhất hạn mức này với một PPTX.

Chrome do tool khởi chạy trên chính máy dùng kết nối loopback và `is_local=True`, phù hợp [tài liệu Playwright](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp-option-is-local). Điều này tránh chuyển tệp theo đường remote bị giới hạn 50 MB; không thay quyền dùng của tài khoản hoặc bước xác minh web.

## Bốn cấu hình duy nhất cho bài mới

| Kiểu chuyển đổi | Chữ trên slide | Lời đọc trợ lý |
| --- | --- | --- |
| Hai cột song ngữ | Việt trái – Anh phải; dịch đầy đủ 1:1 từng ý | Cặp Việt–Anh bám slide |
| Song ngữ từng câu | Việt trên – Anh ngay dưới từng câu/bước | Cặp Việt–Anh bám slide |
| Tích hợp từ khóa | Câu Việt xen thuật ngữ Anh; lần đầu Việt (English), lần sau có thể dùng thuật ngữ Anh | Việt đọc ý chính; Anh đọc thuật ngữ/cụm ngắn đã tích hợp |
| Tiếng Anh 100% | Thay toàn bộ chữ Việt bằng Anh tại vị trí tương ứng; không có vùng Việt cứu trợ trên slide | Anh đọc nội dung; Việt tương ứng lưu riêng trong ghi chú |

Không chọn level và bố cục độc lập nữa. Bài cũ và gói đang xử lý vẫn đọc được theo cấu hình cũ; không tự chuyển đổi bài đã duyệt. Trường level/layout nội bộ trong bài mới chỉ là bộ chuyển tiếp cho các thành phần cũ, không là lựa chọn bổ sung và không thay đổi phương pháp trong prompt.

Prompt triển khai ở `app/conversion_formats.py`, theo bốn phương pháp người dùng cung cấp. Các yêu cầu chung bảo toàn kiến thức, công thức, số liệu, hình ảnh và hoạt ảnh được ghép với đúng một phương pháp.

## Giữ giáo án gốc

- PPTX: đúng số lượng/thứ tự slide, mỗi slide gốc tương ứng một slide đầu ra. Không thêm slide hỗ trợ, không tự tóm tắt hoặc bỏ nội dung. Quy tắc số slide cũng áp dụng nếu chọn mẫu cho một PPTX.
- Chỉnh chữ trong đối tượng gốc khi có thể, bảo toàn tối đa hoạt ảnh, Trigger, liên kết, video/âm thanh. Không biến cả slide thành ảnh.
- Slide kín/chữ Việt trong ảnh/hiệu ứng không giữ được: ghi rõ slide và hạn chế trong CHECK/báo cáo. Không âm thầm thu chữ quá nhỏ hoặc tuyên bố đã bảo toàn 100%.
- Word/PDF/ảnh/nội dung dán: dựng thành slide theo trình tự tài liệu và mẫu, không ép giữ số trang thành số slide.
- Tool so sánh số slide nguồn/kết quả khi nhận PPTX từ yêu cầu mới và cảnh báo nếu khác. Đây chưa phải kiểm chứng tự động độ đúng bản dịch hoặc bảo toàn hoạt ảnh.

## Voice, mascot và câu hỏi

Ghi chú gốc được giữ, khối `BILICLASS_NOTES:` thêm ở cuối chứa lời đọc với dòng `VI:` và `EN:`. Tool lấy khối cuối để tránh đọc lẫn ghi chú cũ. `CHECK:` và `QUIZ:` không được trộn vào âm thanh.

Các slide trọng tâm có thể có một câu hỏi bám nguồn trong dòng `QUIZ:` chứa JSON: `kind=single`, `vi`, `en`, các `options` có `vi/en`, đáp án `correct=A/B/C/D` và `rationale_vi/rationale_en`. Không đủ căn cứ thì bỏ câu hỏi, ghi CHECK. Không thêm slide quiz vào PowerPoint gốc.

Tool nhận câu hỏi hợp lệ vào đúng slide ở trạng thái nháp, bỏ câu không hợp lệ và báo vị trí cần kiểm tra. Xác nhận cả PowerPoint không tự duyệt câu hỏi; giáo viên duyệt trong Trợ giảng & Quiz trước khi sử dụng với lớp. Dữ liệu đáp án không phải lời đọc slide.

Trình chiếu dùng Microsoft PowerPoint trên máy, mascot trong suốt kéo tự do và giọng đọc theo slide thực tế. Nhận file không tự sửa file trả về. Khi nội dung thay đổi cần xem/xác nhận bản mới.

## Những phần giữ nguyên

Theo yêu cầu người dùng: **Cài đặt Chung, Giọng đọc, Mascot, Browser AI giữ cấu trúc hiện tại**. Chỉ hướng dẫn ở Song ngữ đổi thành bốn phương pháp. Không tự kết luận các cấu hình giọng/tài khoản đều đã nghiệm thu trên mọi máy.

Giữ thư viện bài, nguồn, ghi chú, giọng đọc offline/cache, trình chiếu PowerPoint, mascot, câu hỏi đã duyệt, sao lưu/khôi phục và cập nhật ứng dụng. Lớp học và báo cáo vẫn cần cho hoạt động trắc nghiệm; không gỡ chỉ vì chúng không nằm trong nút Chuyển đổi.

## Thu gọn đã triển khai trong mã nguồn

| Phần | Xử lý | Điều kiện trước khi xóa mã/gỡ khỏi bộ cài |
| --- | --- | --- |
| Level L0–L4 + bộ chọn bố cục riêng | Đã gỡ khỏi nhập bài mới; hướng dẫn Song ngữ chỉ còn bốn kiểu | Giữ bộ đọc cho bài/gói cũ; không viết lại bài giáo viên |
| Bộ chọn Browser/offline và chế độ giữ/bổ sung/slide Việt–Anh kế tiếp | Đã gỡ khỏi nhập bài mới | Luồng Browser là mặc định; bài cũ vẫn mở được |
| Bộ chọn level/bố cục trong editor của PPTX nhận về | Đã gỡ các bộ chọn cũ khỏi editor; hiện tên phương pháp, giữ cấu hình đã lưu của bài cũ | Muốn đổi phương pháp thì chuyển đổi/nhận PPTX mới |
| Kết nối ChatGPT OAuth/Responses cũ | Đã gỡ module OAuth/Responses, UI đăng nhập cũ, script và test của tính năng đã nghỉ | Yêu cầu OAuth cũ không tự gửi lại; tài liệu/kết quả/hồ sơ giữ nguyên. Bài AI đã lưu có bộ đọc hỗ trợ riêng, không cần token hoặc mạng |
| Engine dịch offline + tải model dịch/OCR phục vụ chuyển đổi mới | Đã gỡ đường gọi dịch/OCR trong desktop, nút editor/cài model và bước đóng kèm model dịch/OCR. PyInstaller loại engine khỏi bộ cài chính | Bài cũ xem/xuất bằng nội dung đã lưu, không tự dịch lại. Helper nhập/dịch cũ chỉ còn cho công cụ phát triển tùy chọn; giọng Kokoro/VieNeu và model voice giữ |
| Thuật ngữ/kho kiến thức/menu dữ liệu dày | Đã gom thành một mục Dữ liệu trợ giảng: Thầy cô đã duyệt / Kiến thức có nguồn | Giữ nội dung thầy cô đã duyệt và quyền xuất/sao lưu; chỉ gỡ giao diện trùng, không xóa dữ liệu |
| Gợi ý level trong báo cáo/hướng dẫn cũ | Đã đổi thành gợi ý mô tả theo bốn phương pháp, bỏ tăng/giảm level số | Không suy ra năng lực học sinh bằng ánh xạ máy móc level sang kiểu bố cục |
| Lớp học, QR và báo cáo | Giữ là tính năng tùy chọn khi dạy | Câu hỏi/đáp án cần duyệt; tách khỏi bước chuyển đổi để không tăng thao tác nhập bài |

Không xóa model hoặc thư viện cá nhân trên máy. Bộ đọc/export bài cũ, sao lưu, nhập gói và reuse đoạn đã duyệt vẫn giữ. PyJWT không còn là phụ thuộc chính; dịch/OCR Windows chuyển sang extra `legacy-import` phục vụ kiểm chứng nguồn cũ. Dependency lock hiện có dành cho môi trường phát triển kèm extra, không mô tả toàn bộ thành phần được đóng gói.

Giọng Việt: sửa hằng số offline của Hugging Face khi thư viện đã được import trước; ép backend CPU/ONNX tránh dò PyTorch. Cache thư viện native, metadata và dữ liệu múi giờ của phụ thuộc; script `prepare-dev-voices.ps1` sao chép model đã có sang ổ người dùng Windows để tránh nạp từ ổ dự án chậm. Không tải model/mạng trong bước này. `run.ps1` tự nhận cache đã chuẩn bị. Bộ cài cài trên ổ người dùng vẫn chứa model giọng; không có thêm cache mô hình dịch.

Build thu data/binary/submodule và metadata của từng gói cần thiết, thay `collect-all` gây dò mọi tệp của mọi thư viện đã cài. Loại Gradio/Gradio Client của nhánh giao diện web không dùng; kiểm tra SDK thực tế khi chặn hai module vẫn tạo WAV Việt mới hợp lệ, khoảng 18 giây trên cache của máy này. Bộ cài cần kiểm tra riêng cả archive và hai engine voice.

Finalize giữ DLL llvmlite ở đường dẫn tài nguyên `llvmlite/binding` và dependency riêng trong `llvmlite.libs` để chỉnh tốc độ giọng Việt. Script thu giấy phép đọc RECORD/SOURCES, chỉ kiểm tra tệp notice cần sao chép; hai kiểm thử bổ sung xác nhận giữ attribution và không dò mọi tệp model/thư viện.

## Kiểm tra và giới hạn

Ngày 10/10, lỗi không hiện tài liệu được tái hiện với ba PPTX Vật lý 70.906.619, 104.330.108 và 76.958.905 byte, đều vượt giới hạn 50 MB cũ. Sau sửa, `qt_conversion_picker_smoke.py --source-dir <thư mục bài gốc>` mở hộp chọn tệp thật của Windows và nhận đủ chín PPTX Toán/Tin/Vật lý, thêm một mẫu tên Unicode/đuôi viết hoa, đổi tệp rồi hủy hộp chọn mà giữ tài liệu trước. SHA256 toàn bộ nguồn không đổi, không upload. Báo cáo/ảnh nằm ngoài Git trong `reports/conversion-picker/`.

Ca browser mới dùng PPTX 51 MB và máy chủ HTTP local để tải byte thật: tạo gói → đính kèm bằng Chrome thật → tải → kiểm tra → lưu nguồn → mở lại bài → phục hồi cache, chỉ gửi một lần, giữ nguyên SHA256. Web/AI là fixture, không phải ChatGPT thật. Ca này phát hiện và xác nhận sửa thiếu khai báo kết nối Chrome local. Smoke Qt handoff kiểm tra ghi chú trong prompt xem trước bằng đúng prompt gửi/lưu, khối lớp theo cấp, giữ lựa chọn thiết kế, lỗi tệp ngay tại ô nhập, giới hạn ghi chú, bốn mẫu và cửa sổ nhỏ. Smoke Browser AI vẫn qua với preview Office thật; không QML warning.

Kiểm thử phải phủ bốn prompt độc lập, cấu hình lưu/mở lại, nguồn không đổi, PPTX tiếng Anh có lời đọc Việt riêng, câu hỏi liên kết slide/chưa duyệt, dữ liệu CHECK/QUIZ không vào voice và cảnh báo đổi số slide. Smoke Qt kiểm tra bốn lựa chọn → gói gửi → nhận file → xem trước Office → xác nhận bài → giữ câu hỏi nháp.

Web ChatGPT có thể đổi giao diện, mất phiên hoặc giới hạn tài khoản. Nghiệm thu luồng/gói bằng fixture không chứng minh chất lượng AI của bốn bài thật. Cần thử thực tế từng phương pháp bằng tài liệu giáo viên rồi phát hành bộ cài riêng cho máy thứ hai.

Kết quả ngày 09/10 sau thu gọn: lượt pytest toàn bộ có 276 ca qua và một ca Chrome localhost vượt thời gian kết nối. Chạy lại ca đó cùng nhóm báo cáo/lớp học bằng cache thư viện đầy đủ: 39 ca đều qua. Tổng cộng 277 ca đã qua, không phải một lượt chạy toàn bộ sạch. Ruff và kiểm tra diff đã qua.

Qt `qt_streamlined_smoke.py` kiểm tra menu dữ liệu, hai tab, đúng bốn phương pháp và mở bài L5 cũ; `qt_chatgpt_handoff_smoke.py` và `qt_browser_ai_smoke.py` kiểm tra gói gửi/nhận, byte PPTX không đổi, xem trước Office và mở lại bài. Browser dùng web fixture, không gửi bài thật. `qt_teaching_smoke.py` qua với PowerPoint toàn màn hình, mascot kéo/điều khiển và giọng Anh thật. `verify_settings_ui.py` đầy đủ đã qua với phát giọng Anh và Việt thật, giữ/lưu các tab hiện có; không có QML warning.

Ca voice ban đầu chậm khi nạp thư viện/model từ ổ dự án. Sau sửa cấu hình offline và chuẩn bị cache giọng trên ổ người dùng Windows, VieNeu nạp khoảng 18 giây và tạo một câu khoảng 10 giây trên máy này; chưa phải benchmark laptop khác. Không tự tải model hay lấy dữ liệu giáo viên trong bước cache. Các script kiểm tra giao diện dịch offline cũ đã nghỉ; dùng bộ smoke hiện hành nêu trên.

Bản độc lập RC13 đã qua kiểm tra archive, Playwright driver, Qt trang nhập bài (không warning) và self-test bằng `.exe` trên thư mục thử riêng ở ổ người dùng. Self-test có WAV Kokoro/VieNeu thật, tốc độ/cache, bốn prompt và đọc PPTX, lớp học/WebSocket/báo cáo, gói bài/lịch sử và backup/restore; không gửi bài lên AI, không dùng thư viện/model của môi trường nguồn. Release công khai RC12 chưa được thay; chưa chứng nhận Windows sạch hoặc chất lượng đầu ra ChatGPT của bốn phương pháp mới.
