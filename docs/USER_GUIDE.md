# BiliClass 1.0 RC11 — hướng dẫn dùng thử

Công cụ dạy học Anh–Việt ngoại tuyến, phục vụ các môn THPT và môn tự tạo. Các bài mẫu chỉ dùng để kiểm chứng công cụ.

## Mở và cài ứng dụng

- Chạy ngay RC11: giải nén toàn bộ gói phát hành, đóng BiliClass đang mở, rồi chạy `BiliClass/BiliClass.exe`. Giữ nguyên cả thư mục BiliClass, gồm `_internal` và `models`. Trên máy phát triển, tệp nằm ở `dist/rc11/BiliClass/BiliClass.exe`. Không cần chạy Python hoặc mở terminal.
- Cài vào tài khoản Windows: trong thư mục vừa giải nén, chạy `Setup.cmd`. Bộ cài kiểm tra checksum, đặt chương trình trong `%LOCALAPPDATA%/Programs/BiliClass/<version>` và tạo mục Start menu. Không cần quyền quản trị. RC11 được đặt cạnh phiên bản cũ và dùng chung thư viện cá nhân.
- Bộ cài ứng dụng tách hai gói dịch. Trong Cài đặt → Cài gói dịch từ máy/USB, chọn `vi-en-1.9.bclanguage` và `en-vi-1.9.bclanguage`. Ứng dụng không tự tải model hoặc gửi bài lên Internet.
- Gỡ: dùng PowerShell chạy `Install-BiliClass.ps1 -Uninstall` trong thư mục cài, hoặc bản cạnh Setup. Bài học và bản sao lưu giữ nguyên. Khi chỉ dùng bản portable, không cần bước cài/gỡ.
- Đây là bản thử RC11 chưa ký số. Việc chạy được trên máy phát triển không thay thế kiểm thử cài sạch trên một máy Windows khác.

## Soạn bài

1. Tạo bài mới, nhập tên môn và khối 10–12, rồi chọn L0–L4 và kiểu trình bày riêng cho bài. Môn là ô tự do; không bị giới hạn vào các môn trong hồ sơ hay danh sách ví dụ.
2. Chọn nguồn Việt hoặc Anh, dán văn bản hoặc nhập PPTX/DOCX/PDF/TXT/PNG/JPG. Tối đa 50 MB/tệp. PDF tối đa 300 trang; mỗi lượt OCR tối đa 50 trang scan.
3. Đọc lại văn bản trích xuất. Với OCR, chú ý dấu, số và công thức. Nút **Nguồn** xem bản trích xuất ban đầu; **Tệp nguồn** mở bản sao chỉ đọc để đối chiếu. Công thức dạng đối tượng, ảnh/video/biểu đồ không được tự chuyển thành nội dung tương đương; ứng dụng cảnh báo khi phát hiện ở Office.
4. Nhập bản dịch hoặc dùng dịch ngoại tuyến. Bản dịch máy luôn cần duyệt; giới hạn 2.000 ký tự/đoạn và giới hạn token của model. Có thể tách đoạn Việt/Anh tại hai vị trí con trỏ.
5. Thêm thuật ngữ vào đúng môn. Tên riêng có thể giữ nguyên bằng cặp Việt/Anh giống nhau. Đánh dấu biểu thức phức tạp bằng `$…$` hoặc đoạn mã bằng dấu backtick để giữ nguyên khi dịch. Kiểm tra lại các cảnh báo số/ký hiệu trước khi duyệt.
6. Memory lấy từ đoạn hiện được duyệt trong cùng môn. Gợi ý gần giống chỉ áp dụng khi thầy cô chọn, luôn thành nháp. Gói bài nhập và lịch sử chưa duyệt không tự dạy lại memory.

Nháp tự lưu sau 1,8 giây ngừng nhập. Giữ 30 phiên bản trước. Khôi phục/tách/sửa nguồn hoặc đổi môn yêu cầu duyệt lại các nội dung liên quan. Khóa dịch tự động không cấm thầy cô biên tập thủ công.

## Level, trợ giảng và âm thanh

| Level | Hướng sử dụng |
|---|---|
| L0 | Văn bản Việt, từ khóa Anh |
| L1 | Thêm câu điều hành lớp đã chuẩn bị |
| L2 | Cầu nối, ưu tiên English đơn giản đã duyệt |
| L3 | Hai ngôn ngữ và hỗ trợ xen kẽ |
| L4 | English trước, Việt theo yêu cầu |
| L5 | Chỉ để mở bài cũ; English với hỗ trợ tối thiểu, VI Rescue vẫn có |

Kiểu trình bày gồm: **cùng dòng**, chèn từ English sau thuật ngữ Việt đã chuẩn bị; **hai dòng**, English in nghiêng dưới dòng Việt; **hai cột**, Việt trái và Anh phải; **English toàn phần**, ẩn bản Việt cho đến khi bật VI Rescue. Chọn level và kiểu này khi tạo bài, đổi lại được trong trình biên tập. Level điều chỉnh hỗ trợ ngôn ngữ/trợ giảng; kiểu trình bày quyết định văn bản trên màn hình. Nếu chưa có bản English đơn giản cho L2, bàn điều khiển thông báo đang dùng bản dịch chính. Kiểu cùng dòng không tự suy đoán bản dịch thuật ngữ; cần thêm thuật ngữ khớp nội dung vào đúng môn.

**Trợ giảng & Quiz** cho phép soạn và duyệt giải thích, English đơn giản, ví dụ, câu điều hành lớp, câu hỏi thảo luận, từ vựng và VI Rescue. Trợ giảng chỉ đọc nội dung đã chuẩn bị của đoạn hiện tại; không giả sinh kiến thức từ model dịch.

Trong Cài đặt → **Giọng đọc**, chọn một trong năm giọng Kokoro English offline hoặc bốn giọng VieNeu tiếng Việt, nghe thử từng giọng và đổi tốc độ. Có thể chọn nhanh một bộ giọng Việt–Anh, hoặc chỉnh riêng từng bên. Lần đầu VieNeu có thể mất khoảng nửa phút để nạp model; sau đó cùng câu/giọng/tốc độ lấy từ cache. **Chuẩn bị lên lớp** kiểm tra nguồn, review và tạo WAV cho các đoạn đã duyệt để không phải đợi tổng hợp khi dạy. Cache gắn với đúng văn bản/giọng/tốc độ/phiên bản engine. Gói bài mang theo audio đã chuẩn bị; máy nhận có thể phát cache dù thiếu giọng đó. Sửa văn bản làm audio cũ không còn khớp. Nếu thiếu model, app chỉ hiển thị giọng Windows phù hợp đang có trên máy.

Cài đặt có sáu tab. **Chung** lưu tên thầy/cô, trường, nhiều bộ môn (cách nhau bằng dấu phẩy), logo PNG/JPG và quyền hiện tên/trường/logo trên màn bài giảng/deck xuất. Tải logo ngay sau ô bộ môn; logo tự lưu khi chọn, còn tên/trường/bộ môn cần bấm **Lưu thông tin**. Ô xem trước đọc dữ liệu đã lưu, có trạng thái hiện/ẩn. Không lưu một lớp hay level chung: môn/khối/level/bố cục chọn theo từng bài, còn tên lớp nhập khi mở tiết. **Song ngữ** giải thích L0–L4 và bốn kiểu trình bày, không tự lưu lựa chọn; **Giọng đọc** chọn/nghe thử English; **Mascot** chọn Milo/Lumi, xem mẫu slide/giải thích/quiz, bật tắt theo bối cảnh, chỉnh vị trí, cỡ, nhãn môn và chuyển động; **Lớp học** lưu cách tham gia, sĩ số, thời gian và ngôn ngữ câu hỏi mặc định; **Dữ liệu** quản lý thư viện, bản sao lưu, gói dịch và trạng thái OCR. Logo nằm trong thư viện, được đưa vào bản sao lưu.

Máy kiểm thử có năm giọng Kokoro English, bốn giọng VieNeu tiếng Việt và OCR Windows en-US; chưa có OCR Việt. Thiếu gói nào được báo riêng; không tự dùng giọng/nhận dạng sai ngôn ngữ. Có thể tiếp tục biên tập và dạy bằng chữ.

## Dạy học

- **Xem trước** mở bàn điều khiển: chuyển đoạn, phát âm, gọi trợ giảng, VI Rescue, mở cửa sổ lớp.
- Cửa sổ lớp chỉ trình bày đoạn đã duyệt. Không chứa ghi chú biên tập hoặc đáp án chưa công bố.
- Với Extend, chọn màn hình phụ. Với Duplicate, Windows chiếu toàn bộ màn hình chính, vì vậy dùng cửa sổ lớp toàn màn hình và tránh mở bàn điều khiển khi đang chiếu. Ứng dụng không thể che riêng một cửa sổ khỏi chế độ Duplicate của Windows.
- **Trợ giảng nổi** mặc định chỉ hiện Milo hoặc Lumi trên nền trong suốt, không có khung. Nhấp vào mascot để mở các nút trợ giảng; nhấp lại để thu gọn, bấm **Ẩn** trong bảng để đóng, hoặc mở lại bằng nút mascot ở thanh bên. Khi lưu tab Mascot với **Hiện khi dạy** bật, mascot hiện ngay. Tab Mascot cho xem trước khi dạy, đổi cỡ/vị trí và giảm chuyển động; tùy chọn giải thích/quiz áp dụng cho bối cảnh màn dạy. Nút nghe câu mẫu dùng giọng English đã chọn độc lập trong tab Giọng đọc. RC11 dùng bốn hình tư thế và nhịp nổi mượt; chưa phải hoạt hình có khớp riêng hoặc trang phục riêng từng môn.
- Với PPTX và PowerPoint đã cài: mở bản nguồn chỉ đọc; tiến/lùi/nhảy slide. Office xử lý animation khi tiến. Đoạn tự theo slide khi không có thay đổi chưa lưu; dùng **Theo slide hiện tại** hoặc chọn đoạn thủ công khi cần. BiliClass chỉ đóng bản trình chiếu do mình mở.
- **Xuất PPTX** tạo deck song ngữ mới từ toàn bộ đoạn đã duyệt, chia phần dài thành các slide. Đây là mẫu mới có văn bản chỉnh sửa được, không sao chép animation/bố cục của nguồn. Tệp nguồn giữ nguyên.

## Lớp học và kết quả

1. Soạn câu hỏi và duyệt cả Việt/Anh, lựa chọn, đáp án. Có ba loại: một đáp án đúng, đúng/sai, khảo sát không chấm điểm. Câu hỏi gắn với một đoạn nguồn và tên chủ đề.
2. Mở **Lớp học**, điền lớp, chọn ẩn danh hoặc số chỗ, sĩ số tối đa và đúng IP Wi‑Fi/Ethernet. `127.0.0.1` chỉ thử trên cùng máy.
3. Học sinh cùng LAN quét QR. Không cần tài khoản. Có thể lưu mã khôi phục cá nhân trong mục tương ứng trên điện thoại, dùng khi đổi mạng/trình duyệt; không chia sẻ mã đó.
4. Mở câu, chọn thời gian và ngôn ngữ. Học sinh được đổi đáp án trước khi đóng; gửi lại cùng mã không đếm trùng. Khi mất kết nối, trang báo trạng thái và khóa gửi; đáp án đã xác nhận được lưu.
5. Đóng câu trước khi công bố. Đóng câu chưa làm lộ đáp án. **Kiểm tra lại** tạo lượt riêng.
6. Kết thúc tiết để lưu kết quả; **Ngắt máy chủ** dừng kết nối nhưng giữ phiên chưa kết thúc để mở lại ở Báo cáo. Khôi phục cùng mạng ưu tiên dùng cổng trước đó; nếu cổng bị chiếm, app chọn cổng mới và báo phát QR mới. Khi đổi IP/QR hoặc trình duyệt, học sinh dùng mã khôi phục đã lưu để lấy lại đúng chỗ.
7. Báo cáo có số đúng/số trả lời, số tham gia/đủ điều kiện, số chưa trả lời. Poll không tính điểm. Concept cần ít nhất hai câu và 10 người để phân loại; mẫu ít hiển thị riêng. Metadata hiểu nhầm là gợi ý quan sát, không kết luận chắc chắn.
8. Có CSV tổng hợp và CSV từng phản hồi, không xuất token tham gia. Xóa phiên chỉ được sau khi kết thúc/ngắt máy chủ.

Gợi ý level chỉ dùng các câu khác nhau được thầy cô gắn cùng **mã cặp tương đương**, cùng chủ đề, một câu Việt và một câu Anh. Cần ít nhất hai cặp, mỗi cặp cùng ít nhất 10 người và tham gia từ 80%; không dùng recheck. Ngưỡng và hạn chế được ghi ngay trong báo cáo. Không coi chênh lệch quan sát là tác động riêng của ngôn ngữ.

Nếu không vào lớp: kiểm tra cùng mạng, địa chỉ IP, Firewall mạng riêng và tính năng client isolation của router. Khi cổng hoặc mạng đổi, dùng QR mới hiển thị trong app. Thử tải 50 kết nối trên máy phát triển không chứng minh router trường phục vụ được 50 điện thoại.

## Lưu, chuyển máy và khôi phục

- **Xuất gói bài**: `.biliclass` có lesson, trợ giảng, quiz, nguồn và WAV khớp nội dung. Máy nhập nhận bản sao với review đặt lại; không nhập danh sách học sinh từ phiên lớp.
- Giới hạn gói: 100 MB nén, 200 MB giải nén, 1.000 tệp. Chia nhỏ bài/audio nếu vượt giới hạn.
- **Sao lưu thư viện**: gồm database bài học/lớp học, nguồn, audio và logo trường. Tự lưu mỗi ngày khi mở app, giữ 14 bản tự động; bản sao thủ công không tự xóa. Model có thể cài lại từ gói riêng.
- **Khôi phục bản sao** luôn tạo thư mục mới; chọn **Mở thư viện** để xem. Thư mục đang dùng hiển thị trong Cài đặt. Bản thư viện gốc không bị ghi đè.
- Nhật ký kỹ thuật nằm trong `logs/app.log`; không ghi nội dung bài hoặc token học sinh.

## Phạm vi cần thử tiếp

RC11 đã có các nhóm chức năng trong kế hoạch, năm giọng Kokoro English, bốn giọng VieNeu tiếng Việt và bản xem trước Mascot theo bối cảnh. PPTX nhập được tách nhiều ý thành đoạn để duyệt; bản xuất giữ cặp Việt–Anh trên cùng trang và ảnh thường từ slide nguồn. Trước khi mở lớp mới, cần kiểm tra nguồn, duyệt nội dung và chốt bản chuẩn bị. Nghiệm thu thực địa còn cần: Windows sạch không Python, laptop 8 GB, cấu hình PowerPoint/Presenter View ở trường, máy chiếu và DPI thật, Android/iPhone, Wi‑Fi/hotspot của lớp, OCR Việt khi cài gói tương ứng và đánh giá bản dịch, phát âm của giáo viên nhiều môn. Các kiểm thử tự động không thay cho những bước này.
