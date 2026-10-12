# Smart Bilingual Slides & Mascot English Reader

Mốc RC14 · 12/10/2026 · task `biliclass-smart-slides-mascot-reader`. Triển khai trong ứng dụng hiện có; giữ các tab Cài đặt và bốn kiểu chuyển đổi.

## Cách dùng

Nhập tài liệu, chọn cấu hình rồi bấm Chuyển đổi bài giảng. Prompt bổ sung quy tắc tiêu đề độc lập Việt trên/Anh dưới, hình/công thức được dời nhưng giữ tỷ lệ/dữ kiện, điều chỉnh font/hộp chữ/nền trong phạm vi thiết kế đã chọn. Bản nguồn không bị ghi đè.

Với yêu cầu mới tạo từ giao diện RC14, tool kiểm tra và render từng slide kết quả bằng PowerPoint. Khi có lỗi kỹ thuật, hình chồng vùng chữ hoặc thân bài Việt thiếu bản Anh, tool yêu cầu ChatGPT sửa **tối đa một lượt**, trong đúng tài khoản/cuộc trò chuyện, kèm báo cáo và tối đa tám ảnh kiểm tra. Bản nháp trước sửa được giữ. Không đổi tài khoản, gửi lại bài gốc hoặc lặp sửa vô hạn. Một lượt sửa dùng thêm hạn mức của tài khoản web; nếu web yêu cầu đăng nhập/xác minh/hết lượt thì báo và giữ công việc để tiếp tục.

Ở màn kết quả có tổng FAIL/CHECK và lỗi của slide đang xem. **Kiểm tra toàn bộ slide** áp dụng cho bài cũ/đã nhận về. FAIL chặn xác nhận Dùng để dạy; CHECK cần thầy cô đối chiếu. PASS kỹ thuật, nếu có, chỉ mô tả kiểm tra tự động, không chứng nhận ngữ nghĩa, OCR, công thức hay hiệu ứng. Tổng thể vẫn CHECK cho tới đối chiếu trực quan; không dùng việc mở được PPTX để chứng nhận chất lượng.

Khi trình chiếu PowerPoint, nhấp mascot → **Đọc tiếng Anh**. Một lần bấm đọc hàng đợi từ tiêu đề đến nội dung/câu hỏi/A–D xác định được trên slide hiện tại. Có Tạm dừng, Tiếp tục, Dừng đọc, Đọc lại; không tự phát khi mở/đổi slide. Đổi slide hoặc bước hoạt ảnh, đổi bài, thoát trình chiếu đều hủy lời đọc. Mascot đồng bộ trạng thái nói. Giọng/tốc độ tiếp tục dùng tab Giọng đọc hiện có; không gọi dịch vụ TTS trả phí.

## Dữ liệu và cơ chế kiểm tra

`app/slide_speech.py` tạo `slide_speech.slides[].englishSpeechSegments` từ các đối tượng native thực sự, gồm ID ổn định, slide ID, text, shape/table/paragraph/cell, thứ tự, loại, trạng thái và quy tắc hiển thị. Dùng nhận diện ngôn ngữ, nhãn/run English và khai báo SPEECH được đối chiếu với substring của đối tượng. Không lấy toàn bộ chữ Latin hoặc chỉ EN trong Notes làm lời đọc.

Nhận cả group, table và `mc:AlternateContent`: lấy nhánh Choice một lần, tránh đọc thêm bản Fallback. Đây là phần quan trọng với công thức và văn bản của PowerPoint mới mà iterator thông thường bỏ qua. Hình/công thức/biểu đồ chưa xác minh có đoạn rỗng `needs_review`; không tạo lời đọc giả. Nội dung lặp ở hai đối tượng khác nhau vẫn được giữ; khai báo trùng cùng nguồn không bị đọc hai lần.

Notes được yêu cầu có dòng `SPEECH: {"version":1,"segments":[...]}`, tham chiếu ID/paragraph/cell/text thật. Không đưa dòng này, CHECK, QUIZ, URL kỹ thuật hay mã rác vào tiếng Việt/English. Lời EN chỉ có tiêu đề trong khi slide có thân bài sẽ bị đánh dấu thiếu/lệch, không tự PASS.

`app/slide_quality.py` đối chiếu cấu trúc, ký tự bất thường, vị trí ngoài slide, vùng có thể chồng, chữ nhỏ và đáp án tick dạng văn bản so với QUIZ. PowerPoint render mọi slide, đo text bounds và tương phản khi có màu nền/chữ đặc xác định được. Ảnh PNG và báo cáo JSON nằm trong thư mục dữ liệu/temp, không vào Git.

Theo dõi click thật qua [PowerPoint GetClickIndex](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.getclickindex). Entrance/Exit nguyên đối tượng, on-click đơn giản có thời gian chờ kết thúc trước khi đọc. Paragraph build, trigger tương tác, tự chạy, chuyển động/lặp hoặc hiệu ứng chưa ánh xạ chắc sẽ bị bỏ qua khi đọc. Không coi số click là đủ để biết mọi đối tượng đang hiện.

`app/english_reader.py` tái sử dụng synthesize/cache Kokoro/SAPI English, chia theo câu/cụm trong giới hạn engine. Hàng đợi chỉ có một worker; kết quả cũ sau Stop/đổi slide không được phát. WAV phát bằng MCI Windows có vị trí pause/resume thật. Dùng bản sao tên ngắn cho bộ phát, giữ nguyên tệp cache và dọn đúng tệp/thư mục tạm sở hữu.

Dữ liệu đọc gắn hash PPTX; tệp đổi trong lúc trình chiếu bị chặn lời đọc cũ. Gói bài nhập lại bỏ dữ liệu đọc/chất lượng khai báo để dựng từ PPTX thực, tránh tin lời đọc JSON không khớp. Chưa nhúng nút mascot/audio vào PPTX độc lập.

## Kiểm chứng và giới hạn

- Các kiểm thử tự động phủ bốn mode, keyword xen câu, bảng/nhóm, AlternateContent, title-only Notes, thứ tự A–D, lặp có ý nghĩa, dữ liệu khai báo giả, ảnh/công thức, mã rác, đáp án mâu thuẫn, chunking, click/ẩn, pause/resume/cancel/lỗi và một lượt sửa browser có dấu chống gửi trùng.
- Qt/Office thật đã qua luồng nhập/cấu hình/nhận/xem/duyệt bài. Qt English Reader đã phát WAV Kokoro thật qua nút mascot, pause/resume, đọc title + body, dừng khi đổi slide, báo khi không có English, giữ hash nguồn.
- Đã kiểm tra bản Vật lý 65 slide trong thư viện tại máy, hash `9c04e591bb27e86f3a13f1ede891fe1eeaf835a0c49e8042505ac3c32e9acaf7`, render 65/65 và lưu báo cáo/ảnh riêng. Slide 2/16/38/65 có chuỗi bất thường; 9/12 có vùng cần kiểm tra; 13/14/48/50 cần bổ sung/đối chiếu phần thân/công thức. Đây là phát hiện hồi quy, không tuyên bố đã sửa xong bản bài đó.
- Lượt ChatGPT sửa bài sau báo cáo được kiểm thử bằng fixture browser; chưa gửi lại bài 65 slide thật để chứng nhận chất lượng bản sửa ở mốc này.
- Chưa OCR tự động xác minh mọi chữ trong ảnh; chưa chứng nhận công thức, đồ thị/nhãn/trục, tương phản trên nền ảnh phức tạp, mọi animation/video/audio hoặc chất lượng mọi môn. Các vùng này giữ CHECK/needs_review; cần giáo viên kiểm tra. Tick bằng ảnh/đồ họa chưa được dùng để tự kết luận đáp án.
- Nút đọc và mascot thuộc BiliClass đang điều khiển PowerPoint. Nhúng audio/nút phát vào PPTX dùng độc lập là phần riêng, chưa có trong RC14.

## Chạy kiểm tra

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_slide_speech.py tests/test_english_reader.py tests/test_slide_refinement.py
powershell -ExecutionPolicy Bypass -File scripts/run.ps1 --page new
.\.venv\Scripts\python.exe -m scripts.qt_english_reader_smoke
.\.venv\Scripts\python.exe -m scripts.qt_chatgpt_handoff_smoke
```

Smoke dùng dữ liệu riêng, không gửi lên ChatGPT, không sửa thư viện giáo viên. Cần model giọng, Chrome cho kiểm thử browser và PowerPoint cho kiểm thử native; dùng cache runtime/voices của dự án nếu đã chuẩn bị.
