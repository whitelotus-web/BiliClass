# Browser AI · tài khoản web Free và Plus

Mã nguồn ngày 04/10/2026 mặc định dùng **web ChatGPT trong Google Chrome riêng**. Người dùng đang thử Free; luồng OAuth dùng hạn mức gói trước đó không phù hợp với mục tiêu này. OpenAI tài liệu hóa quyền dùng hạn mức qua kết nối trực tiếp cho [Plus/Pro đủ điều kiện](https://developers.openai.com/siwc/quickstart). Không kết luận mọi lỗi workspace trước đó đều do Free.

Release RC12 chưa có thay đổi này. Tự gửi/nhận qua web là tính năng thử nghiệm, phụ thuộc giao diện và quyền của tài khoản. Kiểm thử giả lập không chứng minh tài khoản thật đã đăng nhập hoặc tạo được PowerPoint.

Đợt chuyển sang Chrome ngày 04/10/2026 dùng Chrome cài trên máy, không thêm dịch vụ browser trả phí hoặc API key. Tham khảo cách quản lý hồ sơ và xác nhận thao tác từ các dự án browser; không cài Donut/Browserbase vào BiliClass. Chi phí/hạn mức ChatGPT vẫn theo tài khoản của giáo viên.

**Kết quả thử thật ngày 04/10/2026:** người dùng gặp vòng lặp xác minh Cloudflare cả trong phiên do BiliClass mở và browser thường. Chưa xác định được nguyên nhân mạng/browser/tài khoản; chưa kết nối thành công. Không coi đây là lỗi riêng của Free hoặc bảo đảm Plus sẽ giải quyết được.

## Chrome riêng và phiên đã lưu

BiliClass mở tiến trình Chrome với hồ sơ riêng theo từng tài khoản và kết nối Playwright qua DevTools chỉ tại `127.0.0.1`, cổng tự chọn. Đây là giao diện debug được [Chrome hỗ trợ với thư mục dữ liệu riêng](https://developer.chrome.com/blog/remote-debugging-port) và [Playwright hỗ trợ qua CDP](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp). Không đọc hồ sơ Chrome cá nhân, không copy cookie từ Edge, không sửa fingerprint hoặc giải CAPTCHA. Không cần ChromeDriver hoặc tải thêm một browser lớn.

Hồ sơ Edge/Chrome cũ được giữ; mỗi tài khoản dùng thư mục mới `profiles/<id>/chrome`. Sau nâng cấp, trạng thái đăng nhập cũ bị gỡ và cần đăng nhập lại một lần. Cookie và dữ liệu web được Chrome tự lưu; BiliClass chỉ đọc điều khiển tài khoản trên trang, không xuất token.

Tác vụ dùng cùng Chrome/hồ sơ với đăng nhập, chạy trong cửa sổ thu nhỏ thay vì headless. Browser vẫn là một tiến trình riêng trên máy và có thể hiện trên taskbar; không cam kết vô hình. Khi hết phiên/cần xác minh, quay lại cửa sổ đăng nhập. Khi đóng, BiliClass yêu cầu Chrome thoát để ghi dữ liệu trước khi giải phóng khóa hồ sơ.

## Đăng nhập và thêm tài khoản

1. **Cài đặt → Browser AI → Đăng nhập ChatGPT**. Nhập thông tin trên trang ChatGPT trong cửa sổ Chrome riêng.
2. Sau khi đăng nhập, app đóng Chrome, mở lại cùng hồ sơ ở chế độ thu nhỏ và kiểm tra phiên còn dùng được. Chỉ lúc đó mới báo đã kết nối; không cần bấm Lưu.
3. Tab hiện tên/email nếu đọc được từ menu tài khoản, gói nếu web ghi rõ và thời điểm lưu. Không suy đoán Free/Plus từ nút nâng cấp hay model. Chưa nhận diện được gói sẽ ghi **Chưa xác định trên web**.
4. Nút chính đổi thành **Thêm tài khoản**. Mỗi tài khoản có hồ sơ Chrome riêng. Menu **⋯** cho đăng nhập lại, chọn tài khoản và xóa hồ sơ tại máy.

Thêm tài khoản mà chưa đăng nhập được: giữ hồ sơ đang thử để nút chính mở lại đúng tài khoản đó, kể cả sau khi đóng/mở tool. Tài khoản đã dùng cho bài mới và lựa chọn cố định Free không bị thay đổi bởi lần thêm chưa thành công. Khi web báo phiên hết hạn/cần xác minh, trạng thái sẵn sàng bị gỡ; đăng nhập thành công sẽ xác nhận lại. Hạn mức là trạng thái riêng, không đồng nghĩa đăng xuất.

Đóng cửa sổ khi chưa xác nhận đăng nhập không được coi là thành công. Chờ đăng nhập tối đa 10 phút; có thể bấm Hủy. Phiên web thuộc thư viện trên máy, không đưa vào Git, backup thư viện hoặc gói bài; không xuất cookie/token hay lưu mật khẩu bằng mã của BiliClass. Dữ liệu OAuth cũ được giữ riêng.

Nếu thấy trang xác minh Cloudflare, app báo đang chờ người dùng xác minh. Cửa sổ Chrome được giữ để bạn hoàn tất xác minh, tối đa 10 phút hoặc tới khi bấm Hủy. Nếu chưa xác minh được, app lưu đúng lỗi và hiện **Dùng gửi/nhận thủ công**. Nút này chỉ chuyển cách gửi tài liệu khi người dùng chủ động chọn; không đánh dấu đã đăng nhập, không nhập phiên browser cá nhân vào tool. Khi xác minh thành công qua thao tác của người dùng, app tiếp tục nhận diện đăng nhập; không bấm CAPTCHA tự động hay đổi kỹ thuật để né xác minh.

Nếu browser thường cũng bị kẹt, cách thủ công chưa dùng được. Thử kiểm tra bằng mạng di động hoặc cửa sổ riêng tư theo [hướng dẫn đăng nhập OpenAI](https://help.openai.com/en/articles/7426629-why-cant-i-log-in-to-chatgpt). Nếu vẫn lặp, báo [OpenAI Support](https://help.openai.com/en/articles/8184038-captchas-in-chatgpt) kèm ảnh lỗi. Không tự xóa cookie, tắt VPN hay đổi mạng của người dùng từ BiliClass.

## Chọn Free/Plus

- Mặc định **Tự động · ưu tiên Plus** cho bài mới: ưu tiên tài khoản trả phí đã nhận diện và đăng nhập thành công trước Free; tài khoản chưa biết gói đứng sau gói đã biết.
- Trong **⋯ → Cố định tài khoản để dùng / kiểm thử**, chọn Free để thử dù đã có Plus. Lựa chọn được lưu qua lần mở app.
- Muốn dùng ưu tiên lại, chọn **Tự động · ưu tiên Plus**.
- Khi mở phiên chuyển đổi, đọc lại nhãn gói hiện có. Nếu Plus đã xuống Free, cập nhật thành Free. Quan sát này áp dụng cho lựa chọn bài sau; bài đang gửi giữ nguyên tài khoản.
- Sau khi bài đã bắt đầu, không đổi tài khoản tự động khi hết quota, lỗi mạng hoặc cần xác minh. Tiếp tục dùng đúng cuộc trò chuyện/tài khoản đã ghi; trạng thái gửi không rõ thì dừng, không gửi trùng.
- Số dư/quota reset chưa có nguồn đọc đáng tin cậy trong adapter. UI nói rõ chưa có số liệu, không tạo phần trăm giả.

## Chuyển đổi bài

Nhập nguồn → chọn L0–L4, bố cục, giữ thiết kế gốc hoặc mẫu → **Chuyển đổi bằng ChatGPT**. App chuẩn bị prompt và tệp, chọn model trong các lựa chọn web đang hiển thị và được phép dùng; bật nút Think/Thinking nếu có toggle nhận diện được. Nếu không có nút hoặc giao diện đổi, giữ lựa chọn mặc định. Không cam kết suy luận cao nhất khi không xác nhận được điều khiển; không mở khóa model trả phí.

Free có công cụ/tải tệp với giới hạn riêng theo [hướng dẫn OpenAI](https://help.openai.com/en/articles/9275245-chatgpt-free-tier-faq). Có thể không tạo được PPTX trong một phiên hoặc phải chờ quota. BiliClass không bảo đảm Free có cùng chất lượng/tính năng với Plus.

Prompt yêu cầu PowerPoint chỉnh sửa được, bảo toàn nội dung/hình nguồn theo lựa chọn, Speaker Notes VI:/EN: để đọc và CHECK: cho phần chưa chắc. Nhận tệp → kiểm tra PPTX → lưu bản gốc trả về → chuẩn bị âm thanh nháp nếu bật → xem trình chiếu → giáo viên xác nhận **Dùng để dạy**. Không tự duyệt nội dung hoặc phát âm thanh nháp. Lỗi một giọng đọc không bỏ PowerPoint đã nhận.

Khi gặp xác minh, đăng nhập hết hạn hoặc giới hạn: dừng, hiện thông báo, giữ trạng thái. Không dùng stealth, giải CAPTCHA hoặc endpoint web nội bộ. **Gửi/nhận thủ công** trong Tùy chọn thêm là dự phòng. Bài đã nhập thư viện có thể mở lại ngay cả khi xóa tài khoản; không gửi lại và không tạo bài trùng.

Ở trang chuyển đổi, **Đăng nhập và tiếp tục** mở đúng hồ sơ/cuộc trò chuyện đã ghi; sau khi xác nhận đăng nhập, tool tự tiếp tục bài đó. Chỉ tiếp tục khi người dùng bấm nút này; đóng/hủy/chưa xác nhận đăng nhập không khởi động chuyển đổi. Bài đã gửi không chuyển sang tài khoản khác.

Adapter chờ tài liệu chính và các điều khiển sẵn sàng thay vì chờ toàn bộ tài nguyên trang. Nếu tài liệu đầu tiên tải chậm, cửa sổ đăng nhập Chrome vẫn mở để người dùng hoàn tất; không tự đóng và không tự khởi động lại luồng đăng nhập. Timeout tải trang không tự tải lại phiên đăng nhập. Kiểm tra prompt còn nguyên và mọi đính kèm hiển thị trước khi Gửi. Yêu cầu xuất PPTX bổ sung được ghi trước khi gửi và chờ câu trả lời mới; không nhận tệp từ câu trả lời cũ. Nhận hạn mức qua thông báo của web, tránh nhầm chữ “giới hạn/hạn mức” trong bài học thành lỗi.

## Kiểm tra

- 35 kiểm thử browser/Chrome và 12 handoff đã qua: hồ sơ riêng, khóa/xóa, backup không chứa phiên, ưu tiên Plus, cố định Free, hạ gói, gói chưa rõ, lựa chọn model được phép, Think, không nhầm giao diện khách với đăng nhập, dừng vòng lặp xác minh, hủy/tiếp tục xác minh, không gửi lại khi trạng thái chưa chắc, tải lại và giữ tài khoản. Thêm các ca thử tài khoản mới thất bại, gỡ trạng thái phiên hết hạn, chỉ nhận câu trả lời mới, thông báo quota tách nội dung bài, xuất PPTX bổ sung và prompt biến mất trước khi gửi.
- Browser test chạy Chrome thật trên trang fixture được chặn mạng; không đăng nhập/tải tài liệu thật lên ChatGPT. Kiểm tra cookie fixture và localStorage còn sau khi đóng/mở tiến trình, không lẫn giữa hai hồ sơ; chỉ dùng endpoint debug cục bộ, hủy trước khởi động không tạo tiến trình. Kiểm tra phiên mất sau lần mở lại không được đánh dấu sẵn sàng; tài liệu tải chậm vẫn chờ đăng nhập hoặc người dùng Hủy.
- Qt Browser AI: đóng cửa sổ chưa đăng nhập; lỗi Cloudflare và chọn dự phòng không báo giả đã kết nối; Free tự lưu; thêm Plus thất bại rồi mở lại đúng hồ sơ; cố định Free; chuyển đổi bị xác minh rồi đăng nhập và tự tiếp tục cùng tài khoản/bài; nhận PPTX và audio giả lập; xem trước bằng Office thật; mở lại bài khi đã xóa tài khoản. Các tab Chung/Song ngữ/Giọng đọc/Mascot được giữ.
- OAuth cũ có smoke riêng để tránh làm hỏng dữ liệu và yêu cầu đã có: [thiết kế và chẩn đoán cũ](CHATGPT_PLAN_AUTH.md).

Còn cần nghiệm thu thật: đăng nhập Free, lựa chọn suy luận trên giao diện thực tế, một bài PPTX nhỏ, chất lượng kết quả và giới hạn lượt dùng; sau đó thử tài khoản Plus và bản đóng gói.
