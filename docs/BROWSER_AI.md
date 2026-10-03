# Browser AI · ChatGPT

Kế hoạch thay kết nối web bằng Sign in with ChatGPT và chuyển đổi bằng JSON tại máy: [Kế hoạch nâng cấp](CHATGPT_PLAN_UPGRADE.md). Đây là hướng đã thống nhất về phương thức kết nối, **chưa được triển khai**; hướng dẫn dưới đây mô tả bản hiện tại.

Mã nguồn ngày 03/10/2026, chưa có trong gói RC12. Tự động hóa giao diện web là tính năng thử nghiệm, không phải kết nối API. Truy cập thực tế bằng Edge trên máy này trả HTTP 403 và trang xác minh; chưa kiểm chứng chuyển đổi trọn gói bằng tài khoản đã đăng nhập. Kiểm thử browser dùng trang mô phỏng và tệp bài giả lập, không tải bài thật lên ChatGPT.

## Thiết lập một lần

1. Mở **Cài đặt → Browser AI**, bấm **Đăng nhập ChatGPT**.
2. Microsoft Edge mở hồ sơ riêng; tự đăng nhập trên web và xử lý xác minh nếu xuất hiện. Không nhập mật khẩu vào BiliClass.
3. Khi nhận diện đăng nhập thành công, app tự lưu phiên và đóng cửa sổ Edge. Không cần đặt tên, chọn browser, bấm Lưu hoặc xác nhận thêm. Trạng thái lưu trước đó không bảo đảm web sẽ chấp nhận lần chạy tiếp; app kiểm tra lại mỗi lượt.

Tab này chỉ quản lý đăng nhập. **Thêm tài khoản** mở hồ sơ mới; **Đăng nhập lại** mở hồ sơ đã lưu. Mỗi hồ sơ dùng Edge riêng, không dùng hoặc sửa hồ sơ browser thường ngày. Hồ sơ Chrome cũ được giữ nguyên; cần đăng nhập Edge vào thư mục riêng, không chuyển cookie giữa browser. **Xóa** xóa hồ sơ và phiên tại máy, không xóa tài khoản ChatGPT. Khi hồ sơ đang dùng, app chặn mở trùng hoặc xóa.

### Tài khoản và model

Yêu cầu mới ưu tiên tài khoản đã nhận diện có gói Plus hoặc gói trả phí tương đương, sau đó Free. Gói chưa nhận diện được ghi là chưa rõ; chữ “Upgrade to Plus” không được coi là tài khoản Plus. Mỗi lần mở web, app đọc lại gói đang hiển thị và chọn model được nhận diện, đang bật trong menu của tài khoản. Nếu Plus hết hạn và web cho dùng Free, cùng hồ sơ tiếp tục theo quyền Free hiện tại.

Thứ tự chất lượng do tool ưu tiên là Astra, Sol, Pro, Thinking, Terra, GPT khác, rồi Luna/mini/Instant; trong cùng nhóm ưu tiên phiên bản lớn hơn. Chỉ chọn mục đang có quyền truy cập, không bấm mua gói. Không nhận diện được menu/model thì giữ mặc định của web, không báo đã chọn model cao nhất. Đây là quy tắc lựa chọn của tool, không phải bảo đảm mọi tài khoản có cùng danh sách model. Khả năng và quyền truy cập phụ thuộc gói/đợt triển khai theo [Models](https://learn.chatgpt.com/docs/models) và [Model selection](https://learn.chatgpt.com/docs/model-selection).

Yêu cầu đã gửi giữ tài khoản/cuộc trò chuyện ban đầu khi tiếp tục, kể cả khi hồ sơ khác được ưu tiên cho bài mới. Không tự chuyển tài khoản để né hạn mức, không đổi model giữa chừng hoặc gửi trùng bài.

## Từ tài liệu đến bản dạy

1. Nhập PPTX/DOCX/PDF/TXT/PNG/JPG hoặc dán nội dung. Điền tên bài, môn/khối; chọn L0–L4 và kiểu sắp xếp Việt–Anh.
2. Với PPTX, chọn **Giữ PowerPoint gốc** hoặc **Theo mẫu BiliClass**; tài liệu khác dùng mẫu. Mở **Xem slide mẫu** khi cần xem thiết kế.
3. Bấm **Chuyển đổi bằng ChatGPT**. App tạo prompt cùng bản sao nguồn tại máy, rồi dùng tài khoản được ưu tiên để đính kèm và gửi qua web trong browser chạy ngầm. Nếu chọn mẫu, gửi thêm PPTX mẫu. Tài liệu sẽ được tải lên ChatGPT khi bấm nút này. **Tùy chọn thêm** ở màn hình nhập bài chứa lựa chọn gửi/nhận thủ công và chuẩn bị giọng đọc, tự lưu khi đổi; mặc định tự động và có giọng đọc.
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

- **Xác minh/đăng nhập**: mở Browser AI → Đăng nhập lại, xử lý trực tiếp, chờ app tự lưu rồi **Tiếp tục yêu cầu**. App không giải hoặc vượt CAPTCHA.
- **Hạn mức/không tạo được tệp/giao diện web đổi**: app giữ gói và địa chỉ cuộc trò chuyện đã biết để kiểm tra. Không bảo đảm xử lý tự động được mọi phiên, cũng không tự đổi tài khoản.
- **Tải bài liên tiếp**: kiểm thử hai lượt tải sau khi mở lại cùng hồ sơ trên máy này gặp browser đóng trong lượt tải thứ hai (cả Edge và Chrome). Chưa xác định nguyên nhân; đổi tên tệp/thư mục tải không giải quyết được. Kiểm thử chọn model sau khi Plus xuống Free dừng trước khi tải lượt thứ hai, không chứng minh lượt chuyển đổi Free hoàn chỉnh. Chưa nên coi tự động tải nhiều bài là đã ổn định; có thể nhận PowerPoint thủ công khi lỗi.
- **Dừng hoặc hết 15 phút chờ**: giữ yêu cầu. Tiếp tục cùng cuộc trò chuyện, tránh tải/gửi lại bài. Nếu chưa có PPTX, app chỉ gửi tối đa một câu yêu cầu xuất tệp bổ sung trong cùng cuộc trò chuyện.
- **Không rõ đã gửi hay chưa**: trạng thái được lưu trước khi bấm Gửi. Nếu chưa lấy được địa chỉ cuộc trò chuyện, app yêu cầu kiểm tra thay vì tự gửi trùng.
- **Cần gửi/tải thủ công**: trong màn hình nhập bài → Tùy chọn thêm, chọn **Gửi/nhận PowerPoint thủ công**, rồi dùng [hướng dẫn thủ công](CHATGPT_BROWSER.md). Browser mặc định có thể cần đăng nhập riêng với hồ sơ Browser AI. Ngoại tuyến vẫn là lựa chọn trên màn hình nhập bài.

Tệp nguồn hoặc kết quả bị thay đổi sẽ bị kiểm tra hash và không tự dùng lại. Bài đã sửa chữ trong editor không tự sửa tệp PowerPoint nhận từ ChatGPT; nhận bản PPTX mới trước khi xác nhận dạy.

## Dữ liệu và phát triển

Hồ sơ browser và danh sách tài khoản nằm trong `browser_ai/` của thư viện máy; gói nguồn/prompt/cấu hình/nhật ký yêu cầu nằm trong `chatgpt/<request-id>/`. Browser lưu phiên đăng nhập trong hồ sơ riêng. App không thu thập mật khẩu hoặc xuất cookie/token. Các hồ sơ không đưa vào sao lưu thư viện, gói bài, Git hoặc bản build; máy khác đăng nhập lại. Kết quả PowerPoint lưu trong thư viện như nguồn bài, không thay file gốc của giáo viên.

Dependency Playwright được khóa trong requirements và cache phát triển; dùng Microsoft Edge đã cài. Script build thu thập runtime Playwright, nhưng bản đóng gói có tính năng này chưa được build/kiểm thử/phát hành. Để chạy mã nguồn: `scripts/run.ps1 --page browser-ai`.

Kiểm tra ngày 03/10/2026:

- Mốc trước: toàn bộ suite 197 kiểm thử đạt. Đợt đơn giản hóa đăng nhập: 26 kiểm thử Browser AI + handoff đạt, Ruff đạt; bổ sung tự lưu, ưu tiên Plus/Free, quyền chọn model và giữ hồ sơ Chrome cũ. Qt kiểm tra thêm yêu cầu tiếp tục đúng tài khoản. Kiểm thử model Free dừng trước tải bài, giới hạn tải liên tiếp đã nêu trên.
- `tests/test_browser_ai.py`: browser Edge thật với web được mô phỏng, kiểm tra tải đúng tệp, tải PPTX nguyên byte, chống gửi trùng, tiếp tục, xác minh, hash kết quả và khóa hồ sơ. Không chứng minh web ChatGPT thật sẽ chấp nhận phiên.
- `scripts/qt_browser_ai_smoke.py`: Qt thật, một nút thêm/đăng nhập/tự lưu, ưu tiên Plus, xóa tài khoản, tiếp tục đúng hồ sơ, không còn nút chọn browser/Lưu/Kiểm tra; chuyển đổi, render Office thật, hai WAV với model thật, map mascot và xác nhận bài đều đạt. Đăng nhập/ChatGPT dùng kết quả thử trong kiểm thử Qt. Nạp model giọng đọc từ ổ ngoài chậm; giới hạn thời gian kiểm thử là 10 phút, có trace chẩn đoán.
- Probe Edge thực tế không đăng nhập: HTTP 403/xác minh, không gửi prompt hoặc tệp; báo cáo `reports/browser-ai/live-probe.json`. Đăng nhập và nhận PowerPoint thật bằng tài khoản giáo viên là bước còn cần thử.

Bằng chứng/ảnh thử nằm trong `reports/browser-ai/`, thư viện thử trong `.runtime/`, đều ngoài Git. Bản phát triển trên máy giúp thử nhanh mà chưa cần tạo lại `.exe` mỗi lần sửa.
