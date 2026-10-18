# Changelog

## 1.0.0rc74 — 18/10/2026 — Phím đọc và loa trong trình chiếu

- Cách/Enter/Ctrl+Cách phát, tạm dừng và đọc tiếp Anh/Việt/hai ngôn ngữ trong bài gắn với Mascot; giữ ←/→ để điều hướng, dùng ↑/↓ cho âm lượng lời đọc.
- Gán lại phím trong Cài đặt Mascot, kiểm tra trùng và số phím, khôi phục mặc định; thêm bảng hướng dẫn phím và slider âm lượng trên Mascot.
- Bấm loa trực tiếp dùng cùng trạng thái với phím; hiện badge Ⅱ khi phát, giữ điều khiển video nguồn, tránh chồng giọng, bỏ lệnh thuộc slide cũ và không tự tạo voice.
- Chi tiết phạm vi và kiểm chứng: [BUILD_RC74](docs/BUILD_RC74.md).

## 1.0.0rc73 — 18/10/2026 — Hoàn tất giọng, PowerPoint và khôi phục

- Mặc định tạo giọng Anh lần đầu, nhớ lựa chọn gần nhất; diễn giải cấu hình, nút Hủy/Dừng đỏ, popup dùng lại/tạo lại giữ WAV cũ khi dừng/lỗi.
- Màn hoàn tất có xem slide/nghe giọng đã lưu, mở PowerPoint trực tiếp và về đúng bài trong thư viện; không tự phát hoặc tự duyệt nội dung.
- Đồng bộ tên tải theo tên bài và bản ngôn ngữ/giọng trong ngoặc; gán tên trước khi mở hộp lưu Windows.
- Nhúng loa đọc trọn lời đã lưu theo slide; không bỏ giọng chỉ vì có hiệu ứng. Đặt loa vào vùng trống, có phương án nhỏ gọn và báo phần chưa nhúng được. Mascot có chế độ đọc theo hiệu ứng riêng, nhận đúng cửa sổ F5 và phản ánh phát/dừng native.
- Sao lưu ZIP64, restore gói cũ lớn, checkpoint chuyển thư viện, dung lượng/trạng thái sao lưu và chẩn đoán không chứa dữ liệu riêng.
- Office worker có giới hạn thời gian, dừng đúng tiến trình và giữ cache từng slide; slide tĩnh tái dùng render qua ngày. Thêm corpus, CI và quy trình dựng từ source đã commit.
- Chi tiết kiểm chứng và giới hạn: [BUILD_RC73](docs/BUILD_RC73.md), [tiến độ](docs/IMPLEMENTATION_RC73.md).

## 1.0.0rc72 — 18/10/2026 — Dữ liệu và rà soát toàn hệ thống

- Chuẩn hóa lời đọc trước khi lưu bài mới; tránh lịch sử giả khi nhận cùng request từ nhiều kết nối.
- Giảm đọc lặp khi chốt chuyển thư viện; giữ xác minh trước mở và trước dọn dữ liệu cũ.
- Sao lưu/khôi phục theo khối, dùng ổ đích cho dữ liệu tạm; cùng giới hạn, giữ bản tốt khi lỗi và công bố thư viện sau kiểm tra.
- Sửa hai smoke giao diện đã cũ; bổ sung ca dữ liệu và kế hoạch hoàn thiện có tiêu chí nghiệm thu.
- Chi tiết: [BUILD_RC72](docs/BUILD_RC72.md), [kế hoạch](docs/OPTIMIZATION_PLAN_RC72.md).

## 1.0.0rc71 — 17/10/2026 — Lời đọc và khôi phục lưu bài

- Tự tách nhãn VI/EN và các dòng tiếp theo; sửa lời đọc riêng, giữ nội dung PowerPoint.
- Thống nhất trạng thái tạo giọng, thêm hủy bài đang chọn và giữ cache khi dừng.
- Kiểm dung lượng sớm, giữ đúng lỗi storage, tiếp tục lưu từ bản đã QA.
- Chi tiết: [BUILD_RC71](docs/BUILD_RC71.md).

## 1.0.0rc35 — 15/10/2026 — Tối ưu cache, nhập bài và xử lý thiếu dung lượng

- Chân thanh bên ghi “Copyright © 2026 Nguyễn Diệu Linh”; tên trường nằm trên dòng riêng, giữ “Vân Cốc” cùng dòng.
- Giữ audio gốc VieNeu và tạo các biến thể nhanh/chậm từ audio đó; không suy luận lại khi chỉ đổi tốc độ. Giữ khóa và các WAV đã có, không đổi giọng hoặc engine của người dùng.
- Nhập bài bằng kết nối SQLite riêng của worker, ghi một bản hoàn chỉnh trong một lần; khôi phục theo request ID không tạo trùng. Kiểm tra tệp khi mở bài nằm ngoài luồng giao diện; không đọc PowerPoint hai lần cho cùng một phép xác minh.
- Lưu nguồn qua tệp tạm có kiểm tra SHA-256 rồi mới công bố; phát hiện và khôi phục bản sao lưu dở từ đầu vào còn nguyên. Không giữ một tệp cắt cụt mang tên hash hợp lệ sau khi hết dung lượng.
- Phân biệt câu Anh chứa nhãn nguồn “Đ” với câu Việt; cảnh báo chuỗi nguồn chỉ được phân loại riêng khi đối chiếu đúng đoạn và tọa độ. URL/mã rác vẫn bị loại khỏi lời đọc Việt và Anh.
- Kiểm tra native theo cỡ chữ thật; không bỏ qua đối tượng có nhánh tương thích. Giữ nguyên runs/XML của vùng English khi bản trả về xác nhận giữ nguyên. Tiêu đề trong chế độ từ khóa vẫn Việt trên/Anh dưới; hỗ trợ thống nhất font cho cặp tiêu đề ở hai hộp riêng.
- Khi sửa tràn chữ, xử lý khoảng cách dòng cố định quá lớn và placeholder ngang. Ảnh kiểm tra đã xác minh được dùng lại qua các lượt sửa; xem một slide không làm mất cache của các slide khác.
- Kiểm tra dung lượng trước khi tạo yêu cầu, mở browser hoặc suy luận voice; lỗi hết chỗ không bị coi là mất đăng nhập. Bổ sung thời gian các thao tác local trong bản ghi tiến độ riêng tại máy.
- Chỉ đọc command line của tiến trình Chrome khi kiểm tra profile bận, tránh truy vấn chi tiết mọi tiến trình Windows trước mỗi lượt mở browser.
- Đây là mốc tối ưu từng phần. Không chứng nhận mọi bài đã hết lỗi hoặc toàn bộ thời gian dịch vụ web đã nhanh hơn; bài nhiều công thức/hiệu ứng còn cần xử lý và kiểm tra.

## 1.0.0rc30 — 14/10/2026 — Theo dõi bài dài và khôi phục bước hoàn tất

- Sửa dừng sớm ở mốc 15 phút: khi web còn xử lý, tiếp tục theo dõi từng khoảng 5 phút trong cùng lượt đã gửi, có giới hạn tổng 60 phút theo dõi thực. Không tạo yêu cầu mới hoặc tải lại tài liệu để gia hạn.
- Sửa Tiếp tục dùng lại khoảng chờ đã hết: đọc lại kết quả; nếu lượt vẫn chạy thì tiếp tục, nếu đã xong thì nhận tệp. Bài timeout cũ được kiểm tra tự động một lần sau nâng cấp; lệnh Dừng của giáo viên vẫn được giữ.
- Tự đọc lại cuộc trò chuyện tối đa ba lần khi trạng thái đang chạy không thay đổi trong ba phút. Nếu luồng bị ngắt sau hai lần kết nối lại và đã chờ ít nhất 15 phút, xác minh nguyên prompt cuối rồi thử khôi phục bàn giao một lần; ưu tiên nhận file sẵn có, chỉ yêu cầu xuất bản đã tạo khi cần. Không dừng lượt khỏe, không gửi lại bài gốc, không lặp xuất tệp vô hạn.
- Trong giai đoạn chờ chưa đếm được số phần hoàn tất, hiện Đang xử lý với thanh chuyển động và đồng hồ thay cho phần trăm 25% đứng yên. Các giai đoạn có mốc thực vẫn hiện phần trăm; tác vụ thật sự tạm dừng thì đồng hồ đứng đúng trạng thái.
- Prompt hoàn tất yêu cầu dùng bản đã tạo, tránh dựng lại/kiểm kê/render lại cả bài khi chỉ còn bước bàn giao. Tạo voice vẫn là bước riêng sau khi lưu PPTX.

## 1.0.0rc29 — 14/10/2026 — Thời gian chuyển đổi và giới hạn chờ

- Thêm thời gian xử lý HH:MM:SS trên màn chuyển đổi, tự cập nhật mỗi giây; đứng lại khi tạm dừng/hoàn tất và cộng tiếp phần đã lưu khi tiếp tục. Không đếm ngược thời gian hoàn tất do dịch vụ web không cung cấp dự báo đáng tin cậy.
- Lưu thời gian chờ theo từng yêu cầu đã gửi. Kết nối lại hoặc khởi động lại không mở thêm 15 phút chờ cho cùng yêu cầu; vẫn nhận file đã sẵn sàng khi mở lại. Không tự nối lại vô hạn sau khi hết ngân sách chờ hoặc hết hai lần khôi phục luồng.
- Nhận biết cuộc trò chuyện dừng ở hoạt động xử lý mà chưa có câu trả lời cuối: sau một khoảng không thay đổi, chỉ yêu cầu hoàn tất tệp một lần khi xác minh nguyên prompt của lượt cuối. Không tải lại/gửi lại bài gốc hoặc lấy nhầm tệp đính kèm đầu vào.
- Hỗ trợ thẻ tệp dạng link mở preview và preview trong tab mới, chỉ kích hoạt nút tải của đúng tên tệp; không nhận nhầm tệp đính kèm nguồn hoặc thẻ khác.
- Thời gian từng giai đoạn được giữ qua các lần tiếp tục; thông báo phân biệt đang chạy với đã tạm dừng. Giữ bước tạo voice riêng sau khi lưu PowerPoint.
- Ghi nhận hướng tối ưu dịch theo cụm và dựng file tại máy tại [kế hoạch tăng tốc](docs/CONVERSION_SPEED_PLAN.md). Chưa bật xử lý đa tab/tài khoản hoặc loại bỏ profile Gemini chỉ từ đề xuất này.

## 1.0.0rc21 — 13/10/2026 — Tiến trình rõ ràng và sửa bước gửi

- Kích hoạt nút Gửi trực tiếp một lần, tránh phím Enter bị ô soạn thảo giữ lại hoặc tooltip che nút. Vẫn lưu ý định gửi trước thao tác và không bấm lại khi chưa rõ kết quả.
- Khi tìm lại yêu cầu bị mất xác nhận, mở nội dung người dùng bị thu gọn rồi so khớp toàn bộ prompt; không nhận nhầm bài cùng mẫu nhưng khác tên/nội dung.
- Giao diện “Tạo bài giảng song ngữ” diễn giải công việc theo nội dung/bố cục/kiểm tra/trình chiếu; không hiện thao tác prompt/browser/ChatGPT ở tiến trình và chân cửa sổ.
- Giữ phần trăm theo các mốc thực tế, bỏ dòng giải thích phần trăm; tác vụ đã dừng ghi rõ tạm dừng, lỗi đăng nhập/xác minh/hạn mức vẫn có hướng xử lý.
- Giữ thử lại tự động có giới hạn, model/suy luận, kiểm tra chất lượng, giọng đọc nền và quyền duyệt bài của giáo viên. Không bảo đảm mọi lỗi hoặc mọi bài trên web đều tự hoàn tất.

## 1.0.0rc20 — 13/10/2026 — Logo hồ sơ và copyright

- Hiện logo trường đã lưu cạnh tên giáo viên ở chân thanh bên; giữ đúng tỷ lệ ảnh, tự cập nhật khi thay/bỏ logo và dùng chữ cái tên khi không có ảnh.
- Thêm dòng “Copyright 2026: Nguyễn Diệu Linh - Giáo viên Tin học - Trường THPT Vân Cốc” ở chân cửa sổ, tách riêng khỏi trạng thái tác vụ; tự xuống dòng khi cần.
- Đổi vị trí Browser AI và Song ngữ trong Cài đặt; giữ định danh tab để các đường dẫn mở Browser AI vẫn đúng.
- Mỗi profile có nút Mở tài khoản, dùng lại luồng Chrome đăng nhập hiện có với đúng profile, không thêm tài khoản mới; khóa thao tác trong lúc profile/tác vụ đang được sử dụng.
- Giữ cấu trúc Cài đặt và nội dung PowerPoint/prompt hiện có.

## 1.0.0rc19 — 13/10/2026 — Giữ phiên và tách giọng đọc nền

- Chrome riêng khôi phục phiên khi mở lại; giữ cookie phiên qua các lượt xử lý nền, kiểm tra profile bận/cấu hình hỏng trước khi chạy.
- Nhận, kiểm tra và lưu PowerPoint trước; giọng đọc tự chuẩn bị ở nền với trạng thái riêng, không chặn xem bài hoặc mất bài khi TTS lỗi.
- Ưu tiên lượt tạo giọng khi thầy cô cần đọc, tránh hai lần tạo cùng WAV, giữ cache khi dừng và tiếp tục âm thanh của bài đã lưu sau khởi động lại.
- Ghi thời gian từng bước để chẩn đoán chờ lâu; giữ model, retry cùng chat, duyệt slide và cấu trúc Cài đặt hiện tại. Bằng chứng/phạm vi: docs/SESSION_AND_SPEED.md.

## 1.0.0rc18 — 13/10/2026 — Tự khôi phục Browser AI

- Gửi bằng bàn phím sau khi kiểm tra tài liệu/prompt, lưu ý định gửi và theo dõi xác nhận; timeout không bấm gửi lần hai.
- Tự khôi phục Chrome có giới hạn, tìm lại chat duy nhất có nguyên văn prompt khi URL chưa kịp lưu; giữ tài khoản/chat đã gửi và không gửi trùng.
- Tự tiếp tục tác vụ đã được lưu sau khởi động lại, gồm phần nhập bài/lời đọc từ PPTX đã nhận. Tác vụ đã bấm Dừng hoặc đã lưu xong không tự chạy lại.
- Tách lỗi bài khỏi đăng nhập; lỗi phiên chỉ hiện trên đúng profile, bỏ thông báo lỗi chung bị lặp. Giữ sáu giọng VieNeu và kiểm tra slide/duyệt bài hiện có.
- Chrome fixture và Qt xác minh khôi phục/cancel/không gửi trùng; bộ cài chạy kiểm tra riêng không dùng cache phát triển. Giới hạn và bằng chứng tại docs/BROWSER_RECOVERY.md và docs/STATE.md.

## 1.0.0rc15 — 12/10/2026 — Quản lý thư viện và tải bài

- Thư viện có Sửa/Xóa trên từng bài, ngày/giờ tạo và sắp xếp mới tạo/tạo lâu nhất/mới cập nhật. Bài cũ lấy ngày từ lịch sử còn giữ; ngày ước tính được ghi rõ.
- Xóa đưa vào thùng rác để khôi phục, giữ nguồn/audio/lịch sử/báo cáo; bài trong thùng rác không còn tham gia bộ nhớ dịch của thư viện.
- Màn slide có Trở lại thư viện và Tải PowerPoint: lưu đúng tệp đang xem, không dựng lại hoặc làm mất hình/hiệu ứng. Không cho ghi đè vào thư viện nguồn.
- Nhận/gửi gói .biliclass giữ trong menu chia sẻ; các thao tác phụ gom vào Thao tác khác. Bỏ nút Chuyển đổi lại dễ bị hiểu là gửi lại AI ở màn slide.
- Đổi tên giữ ngày tạo và trạng thái kiểm tra nội dung; đổi môn vẫn cần duyệt lại. Gói bài nhập vào có ngày tạo tại máy nhận.

## 1.0.0rc14 — 12/10/2026 — Smart Slides & English Reader

- Bổ sung quy tắc tiêu đề độc lập, giữ hình/công thức/dữ kiện và tối ưu font/nền/bố cục cho cả bốn kiểu.
- English Reader lấy dữ liệu có cấu trúc từ đối tượng thực trên slide, gồm bảng, nhóm và AlternateContent; không chỉ đọc EN trong Notes. Vùng chưa chắc có needs_review.
- Một nút mascot đọc hàng đợi English của slide hiện tại, tạm dừng/tiếp tục/dừng/đọc lại, không tự phát và hủy khi đổi slide/bước hoạt ảnh. Dùng TTS/cache offline hiện có, WAV/MCI thực.
- Kiểm tra/render theo slide, báo FAIL/CHECK, chặn xác nhận khi còn FAIL; bài mới yêu cầu ChatGPT sửa tối đa một lượt trong cùng cuộc trò chuyện rồi kiểm tra lại.
- Chặn nhãn/mã rác và lời đọc cũ khi tệp thay đổi; không đọc đối tượng hoạt ảnh chưa xác định chắc. Không chứng nhận OCR/công thức/hiệu ứng bằng việc mở/render được PPTX.
- Chi tiết kiểm chứng và phần chưa hỗ trợ: [SMART_SLIDES_READER](docs/SMART_SLIDES_READER.md).

## 1.0.0rc13 — 11/10/2026 — bản thử cho luồng Browser AI

- Chuyển tài liệu qua ChatGPT web/Chrome, nhận PPTX và chuẩn bị giọng đọc; profile riêng từng tài khoản, không cần API key.
- Bốn kiểu chuyển đổi thay level/bố cục riêng; kéo thả/chọn tài liệu, môn/cấp/khối, ghi chú thêm và xem prompt.
- Giữ PowerPoint đầu vào hoặc ba mẫu mới; 24 ảnh xem trước, mẫu gửi AI không chứa nội dung bài minh họa; prompt điều chỉnh theo môn và lớp 1–12.
- PowerPoint toàn màn hình theo đúng slide, đọc Anh/Việt offline và mascot trong suốt có thể kéo.
- Thu gọn runtime, bỏ dịch/OCR/OAuth cũ khỏi bộ cài chính. Giữ hai bộ giọng Kokoro/VieNeu, cập nhật GitHub và dữ liệu cá nhân riêng.
- Bộ cài ghi version/commit và SHA-256; script kiểm tra cài/gỡ bằng dữ liệu riêng, templates/previews, hai giọng thật và tiến trình lớp học, không dựa vào cache phát triển.
- Hướng dẫn tải bộ cài, đăng nhập trên máy khác, thử và sửa code qua GitHub. Chưa chứng nhận mọi máy Windows/môn học hoặc tài khoản ChatGPT.

## Mã nguồn đang phát triển — 03/10/2026

- Đánh giá VI/EN/song ngữ/trộn/chưa rõ và hướng dịch từng đoạn; chọn giữ PPTX hoặc tạo bài theo mẫu. Gợi ý không tự duyệt cặp dịch.
- Bổ sung PPTX theo L0–L4: panel ở vùng trống hoặc trang hỗ trợ khi kín/hiệu ứng/xoay; giữ nguyên file hoặc slide Việt/Anh kế tiếp vẫn chọn được. L4 giữ VI Rescue trong dự án; template có bố cục Theo level.
- Dịch phần còn thiếu tối đa 50 đoạn/lượt; giữ cặp/đoạn khóa/duyệt, dùng thuật ngữ và memory giáo viên trước kho nền/model. Hủy hoặc revision đổi chặn áp dụng loạt cũ.
- So sánh render gốc/song ngữ bằng Office theo mapping slide; ảnh tĩnh không kiểm chứng hiệu ứng. Gói bài giữ thuật ngữ/giọng/mascot tham chiếu, không tự thay máy nhận.
- OCR Việt–Anh cục bộ có bước tải một lần và SHA-256; chạy ảnh/PDF scan/slide chỉ ảnh. Chữ OCR vẫn cần sửa dấu/bảng/công thức, không gửi tài liệu ra web. Bốn tab Cài đặt hiện tại được giữ nguyên.
- 171 kiểm thử và lint đạt, Qt smoke đạt; Office mở/render cả năm level, dịch loạt hai chiều và ảnh/PDF OCR Việt chạy bằng engine thật. Chưa nghiệm thu mọi môn/bài thật, chưa phát hành trong rc12. Xem [quy trình nhập bài](docs/INPUT_WORKFLOW.md).
- Đóng gói một bản phát triển riêng và ghi commit/version. Sửa xung đột hai DLL ONNX Runtime trong gói; kiểm tra `.exe` đạt dịch, giọng Anh/Việt, OCR, lớp học, xuất bài, backup và Qt. Chưa đưa bản này lên Releases.

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
