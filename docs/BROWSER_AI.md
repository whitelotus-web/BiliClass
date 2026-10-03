# Browser AI · ChatGPT

Mã nguồn ngày 03/10/2026, chưa có trong gói RC12. Tự động hóa giao diện web là tính năng thử nghiệm, không phải kết nối API. Truy cập thực tế bằng Edge trên máy này trả HTTP 403 và trang xác minh; chưa kiểm chứng chuyển đổi trọn gói bằng tài khoản đã đăng nhập. Kiểm thử browser dùng trang mô phỏng và tệp bài giả lập, không tải bài thật lên ChatGPT.

## Thiết lập một lần

1. Mở **Cài đặt → Browser AI**, nhập tên hồ sơ, chọn Microsoft Edge hoặc Google Chrome đã cài và bấm **Thêm tài khoản**.
2. Bấm **Đăng nhập/Kiểm tra**. Cửa sổ browser riêng mở ChatGPT; tự đăng nhập trên web và xử lý xác minh nếu xuất hiện. Không nhập mật khẩu vào BiliClass.
3. Trở lại app, bấm **Đã đăng nhập · Kiểm tra** để kiểm tra và đóng cửa sổ này. Chọn hồ sơ muốn dùng bằng nút tròn bên cạnh tên. Trạng thái kiểm tra lần trước không bảo đảm phiên chạy ngầm sẽ được web chấp nhận; mỗi lượt đều kiểm tra lại.
4. Giữ bật **Tự gửi tài liệu, chờ và tải PowerPoint qua web ChatGPT**. Có thể bật chuẩn bị giọng đọc/mascot, dùng giọng đã chọn trong tab Giọng đọc rồi lưu.

Mỗi hồ sơ có browser riêng, không dùng hoặc sửa hồ sơ Edge/Chrome thường ngày. Có thể đăng nhập nhiều tài khoản, mỗi lượt dùng tài khoản đang chọn; không tự chuyển tài khoản khi gặp hạn mức. **Xóa** chỉ xóa hồ sơ và phiên đăng nhập tại máy, không xóa tài khoản ChatGPT. Khi hồ sơ đang dùng cho đăng nhập/chuyển đổi, app chặn mở trùng hoặc xóa hồ sơ.

## Từ tài liệu đến bản dạy

1. Nhập PPTX/DOCX/PDF/TXT/PNG/JPG hoặc dán nội dung. Điền tên bài, môn/khối; chọn L0–L4 và kiểu sắp xếp Việt–Anh.
2. Với PPTX, chọn **Giữ PowerPoint gốc** hoặc **Theo mẫu BiliClass**; tài liệu khác dùng mẫu. Mở **Xem slide mẫu** khi cần xem thiết kế.
3. Bấm **Chuyển đổi bằng ChatGPT**. App tạo prompt cùng bản sao nguồn tại máy, rồi dùng tài khoản đã chọn để đính kèm và gửi qua web trong browser chạy ngầm. Nếu chọn mẫu, gửi thêm PPTX mẫu. Tài liệu sẽ được tải lên ChatGPT khi bấm nút này.
4. App chờ liên kết `.pptx`, tải/kiểm tra tệp, giữ nguyên byte kết quả, nhận chữ và Speaker Notes theo slide, chuẩn bị WAV bằng voice cục bộ. Chưa có voice/ghi chú hoặc một đoạn audio lỗi thì vẫn giữ PowerPoint, báo phần chưa có audio.
5. Xem trình chiếu, kiểm tra nội dung/bố cục, bấm **Dùng để dạy** và xác nhận cả bài. Chuẩn bị audio không tự duyệt nội dung hoặc phát ra loa. Không cần duyệt từng đoạn chỉ để mở bản trình chiếu đã nhận.

Chuyển đổi cần Internet và tài khoản web có thể đính kèm/tạo tệp. Sau khi nhận bài và có voice cục bộ, trình chiếu/mascot không cần tiếp tục dùng ChatGPT. Xem ảnh slide và điều khiển trình chiếu cần Microsoft PowerPoint trên máy.

## Prompt định hướng

Prompt đầy đủ được tạo theo từng yêu cầu và có thể mở bằng **Xem prompt đã cấu hình**. Nó gồm tên bài, môn/khối, nguồn, level, bố cục, cách xử lý cặp hiện có và thiết kế nguồn/mẫu.

| Level | Hỗ trợ yêu cầu |
|---|---|
| L0 | Tiếng Việt chính, thêm khoảng 3–5 từ khóa Anh cho mỗi ý lớn. |
| L1 | Từ khóa và chỉ dẫn/câu Anh rất ngắn, phù hợp lớp. |
| L2 | Câu Anh đơn giản cho ý chính, giữ giải thích Việt. |
| L3 | Cặp Việt–Anh đầy đủ, thuật ngữ/điều kiện nhất quán. |
| L4 | English chính, Việt hỗ trợ trong ghi chú/vùng cứu trợ. |

Prompt yêu cầu nhận diện nguồn Việt/Anh/song ngữ/scan, giữ cặp đúng và bổ sung phần thiếu, giữ hình/logo/bảng/công thức/số liệu. Với thiết kế gốc, thêm vào vùng trống hoặc trang hỗ trợ kế tiếp khi kín; không chồng chữ hoặc thay hình nguồn bằng hình không liên quan. Với mẫu, thay toàn bộ nội dung ví dụ bằng bài thật. Không tự thêm đáp án/kiến thức thiếu căn cứ hoặc đoán chữ scan không rõ.

Speaker Notes thật trong PPTX phải có `VI:` và `EN:` cho lời đọc theo level. Ghi chú cần kiểm tra để ở dòng `CHECK:` riêng, không đưa vào lời mascot. App nhận cả các dòng tiếp nối có xuống hàng. Chốt file không tự duyệt quiz hoặc cập nhật kho kiến thức.

Giữ nguyên hình/hiệu ứng là yêu cầu, không phải bảo đảm chất lượng đầu ra của ChatGPT. Bản nhận về cần đối chiếu nguồn, nhất là công thức, đồ thị, scan và hiệu ứng. Khả năng tạo slide của ChatGPT được OpenAI mô tả trong [hướng dẫn tạo slide](https://learn.chatgpt.com/use-cases/generate-slide-decks); cách đọc hình phụ thuộc loại tệp và tài khoản, xem [File Uploads FAQ](https://help.openai.com/en/articles/8555545-file-uploads-faq).

## Khi web dừng hoặc chưa trả tệp

- **Xác minh/đăng nhập**: mở Browser AI → Đăng nhập/Kiểm tra, xử lý trực tiếp, đóng phiên bằng nút kiểm tra rồi **Tiếp tục yêu cầu**. App không giải hoặc vượt CAPTCHA.
- **Hạn mức/không tạo được tệp/giao diện web đổi**: app giữ gói và địa chỉ cuộc trò chuyện đã biết để kiểm tra. Không bảo đảm xử lý tự động được mọi phiên, cũng không tự đổi tài khoản.
- **Dừng hoặc hết 15 phút chờ**: giữ yêu cầu. Tiếp tục cùng cuộc trò chuyện, tránh tải/gửi lại bài. Nếu chưa có PPTX, app chỉ gửi tối đa một câu yêu cầu xuất tệp bổ sung trong cùng cuộc trò chuyện.
- **Không rõ đã gửi hay chưa**: trạng thái được lưu trước khi bấm Gửi. Nếu chưa lấy được địa chỉ cuộc trò chuyện, app yêu cầu kiểm tra thay vì tự gửi trùng.
- **Cần gửi/tải thủ công**: tắt Tự gửi tài liệu rồi dùng [hướng dẫn thủ công](CHATGPT_BROWSER.md). Browser mặc định có thể cần đăng nhập riêng với hồ sơ Browser AI. Ngoại tuyến vẫn là lựa chọn trên màn hình nhập bài.

Tệp nguồn hoặc kết quả bị thay đổi sẽ bị kiểm tra hash và không tự dùng lại. Bài đã sửa chữ trong editor không tự sửa tệp PowerPoint nhận từ ChatGPT; nhận bản PPTX mới trước khi xác nhận dạy.

## Dữ liệu và phát triển

Hồ sơ browser và danh sách tài khoản nằm trong `browser_ai/` của thư viện máy; gói nguồn/prompt/cấu hình/nhật ký yêu cầu nằm trong `chatgpt/<request-id>/`. Browser lưu phiên đăng nhập trong hồ sơ riêng. App không thu thập mật khẩu hoặc xuất cookie/token. Các hồ sơ không đưa vào sao lưu thư viện, gói bài, Git hoặc bản build; máy khác đăng nhập lại. Kết quả PowerPoint lưu trong thư viện như nguồn bài, không thay file gốc của giáo viên.

Dependency Playwright được khóa trong requirements và cache phát triển; dùng Edge/Chrome đã cài. Script build thu thập runtime Playwright, nhưng bản đóng gói có tính năng này chưa được build/kiểm thử/phát hành. Để chạy mã nguồn: `scripts/run.ps1 --page browser-ai`.

Kiểm tra ngày 03/10/2026:

- Toàn bộ suite: 197 kiểm thử đạt; sau sửa khóa hồ sơ/đọc ghi chú, 21 kiểm thử Browser AI + handoff đạt, gồm hai hồi quy mới.
- `tests/test_browser_ai.py`: browser Edge thật với web được mô phỏng, kiểm tra tải đúng tệp, tải PPTX nguyên byte, chống gửi trùng, tiếp tục, xác minh, hash kết quả và khóa hồ sơ. Không chứng minh web ChatGPT thật sẽ chấp nhận phiên.
- `scripts/qt_browser_ai_smoke.py`: Qt thật, thêm/chọn/xóa tài khoản, cấu hình, một lần bấm, nhận PPTX, render Office thật, hai WAV với model thật, map mascot và xác nhận bài. Phần ChatGPT được thay bằng kết quả thử trong kiểm thử Qt.
- Probe Edge thực tế không đăng nhập: HTTP 403/xác minh, không gửi prompt hoặc tệp; báo cáo `reports/browser-ai/live-probe.json`. Đăng nhập và nhận PowerPoint thật bằng tài khoản giáo viên là bước còn cần thử.

Bằng chứng/ảnh thử nằm trong `reports/browser-ai/`, thư viện thử trong `.runtime/`, đều ngoài Git. Bản phát triển trên máy giúp thử nhanh mà chưa cần tạo lại `.exe` mỗi lần sửa.
