# Browser AI · tài khoản web Free và Plus

Ngày 10/10/2026 — tham khảo cơ chế profile/health/cooldown/renderer nền và lựa chọn suy luận của VeoSuite, áp dụng cho Chrome riêng của BiliClass. Tách lỗi mạng khỏi mất phiên, giữ quota qua kiểm tra đăng nhập; chỉ kiểm tra một profile cần kiểm tra khi rảnh. Bỏ thu nhỏ Chrome nền, giữ renderer hoạt động và kiểm tra profile đang bận trước mở. Đọc lại mức suy luận đã chọn trước gửi. Bài đã tải có thể nhập tiếp khi tài khoản hết phiên/hết lượt. Giữ cấu trúc Cài đặt và luồng bốn phương pháp → PPTX → voice/mascot. Xem [thiết kế và cách vận hành](BROWSER_VEOSUITE_REFERENCE.md).

Ngày 09/10/2026: bài mới dùng bốn **Kiểu chuyển đổi** qua web Chrome, không chọn level/bố cục độc lập hay kết nối OAuth cũ. Cấu trúc tab Browser AI giữ nguyên. Prompt yêu cầu giữ số slide PPTX, lời đọc VI:/EN: và câu hỏi QUIZ: riêng; xem [quy trình mới](FOUR_FORMAT_WORKFLOW.md). Ngày 04/10 đã đăng nhập và nhận PPTX thật, tạo audio/xem trước và trình chiếu; các lỗi truy cập phía dưới ghi lại quá trình sửa trước đó, không phải kết luận cuối cùng. Chưa chứng nhận chất lượng bốn phương pháp trên bài thật; RC12 chưa bao gồm mã mới.

Mã nguồn ngày 04/10/2026 mặc định dùng **web ChatGPT trong Google Chrome riêng**. Người dùng đang thử Free; luồng OAuth dùng hạn mức gói trước đó không phù hợp với mục tiêu này. OpenAI tài liệu hóa quyền dùng hạn mức qua kết nối trực tiếp cho [Plus/Pro đủ điều kiện](https://developers.openai.com/siwc/quickstart). Không kết luận mọi lỗi workspace trước đó đều do Free.

Release RC12 chưa có thay đổi này. Tự gửi/nhận qua web là tính năng thử nghiệm, phụ thuộc giao diện và quyền của tài khoản. Kiểm thử giả lập không chứng minh tài khoản thật đã đăng nhập hoặc tạo được PowerPoint.

Đợt chuyển sang Chrome ngày 04/10/2026 dùng Chrome cài trên máy, không thêm dịch vụ browser trả phí hoặc API key. Tham khảo cách quản lý hồ sơ và xác nhận thao tác từ các dự án browser; không cài Donut/Browserbase vào BiliClass. Chi phí/hạn mức ChatGPT vẫn theo tài khoản của giáo viên.

**Kết quả thử thật ngày 04/10/2026:** người dùng gặp vòng lặp xác minh Cloudflare cả trong phiên do BiliClass mở và browser thường. Chưa xác định được nguyên nhân mạng/browser/tài khoản; chưa kết nối thành công. Không coi đây là lỗi riêng của Free hoặc bảo đảm Plus sẽ giải quyết được.

Lần thử Chrome tiếp theo trả lỗi **400 Invalid content type: text/html** trên trang đăng nhập. Đã đổi bước đăng nhập sang Chrome thường, chưa gắn phần điều khiển browser; chỉ gắn sau khi người dùng xác nhận để kiểm tra phiên đã lưu. **Sau đó người dùng đã đăng nhập được và log xác nhận phiên đã lưu**. Chưa nghiệm thu chuyển đổi PowerPoint thật qua tài khoản này; lần xác nhận ban đầu chưa đọc được gói.

## Chrome riêng và phiên đã lưu

BiliClass mở Chrome thường với hồ sơ riêng theo từng tài khoản để người dùng đăng nhập. Trong bước này không có Playwright hoặc cổng DevTools. Sau khi xác nhận, Chrome đóng để ghi phiên rồi mở lại cùng hồ sơ; lúc này BiliClass mới kết nối Playwright qua DevTools chỉ tại `127.0.0.1`, cổng tự chọn. Đây là giao diện debug được [Chrome hỗ trợ với thư mục dữ liệu riêng](https://developer.chrome.com/blog/remote-debugging-port) và [Playwright hỗ trợ qua CDP](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp). Không đọc hồ sơ Chrome cá nhân, không copy cookie từ Edge, không sửa fingerprint hoặc giải CAPTCHA. Không cần ChromeDriver hoặc tải thêm một browser lớn.

Hồ sơ Edge/Chrome cũ được giữ; mỗi tài khoản dùng thư mục mới `profiles/<id>/chrome`. Sau nâng cấp, trạng thái đăng nhập cũ bị gỡ và cần đăng nhập lại một lần. Cookie và dữ liệu web được Chrome tự lưu; BiliClass chỉ đọc điều khiển tài khoản trên trang, không xuất token.

Tác vụ dùng cùng Chrome/hồ sơ với đăng nhập, không đổi sang headless. Trên Windows, chỉ cửa sổ của đúng tiến trình Chrome do BiliClass mở được ẩn; cửa sổ Chrome khác không bị tác động. Đăng nhập vẫn mở cửa sổ hiện để người dùng thao tác. Trên hệ điều hành khác, việc thu nhỏ còn phụ thuộc window manager. Khi hết phiên/cần xác minh, quay lại cửa sổ đăng nhập. Khi đóng, BiliClass yêu cầu Chrome thoát để ghi dữ liệu trước khi giải phóng khóa hồ sơ.

## Đăng nhập và thêm tài khoản

1. **Cài đặt → Browser AI → Đăng nhập ChatGPT**. Nhập thông tin trên trang ChatGPT trong cửa sổ Chrome riêng.
2. Khi đã vào màn hình chat, quay lại BiliClass và bấm **Kiểm tra và lưu** trên chính nút đăng nhập. Có thể đóng cửa sổ Chrome riêng để bắt đầu kiểm tra. App mở lại cùng hồ sơ ở chế độ thu nhỏ và kiểm tra phiên còn dùng được; chỉ lúc đó mới báo đã kết nối. Bấm xác nhận hoặc đóng Chrome tự nó không được coi là đăng nhập thành công.
3. Mỗi tài khoản hiện thành một dòng: tên/email, gói nếu web ghi rõ và đèn trạng thái. Không suy đoán Free/Plus từ nút nâng cấp hay model. Chưa nhận diện được gói sẽ ghi **Chưa rõ gói**. Khi cần, adapter đọc thêm trường gói hiện tại trong Settings → Account; không bấm nâng cấp.
4. Nút chính đổi thành **Thêm tài khoản**. Mỗi tài khoản có hồ sơ Chrome riêng. Bỏ menu **⋯** và thông tin chính sách lựa chọn. **Xóa profile** xuất hiện ngay trên từng dòng, chỉ xóa hồ sơ browser tương ứng trên máy; bài đã lưu trong thư viện vẫn được giữ.
5. Khi mất phiên, dòng tài khoản cảnh báo và hiện **Đăng nhập lại**. Lỗi mạng/browser hiện **Kiểm tra lại**; không tự xóa cookie hay yêu cầu mật khẩu chỉ vì mạng chập chờn. Hết lượt dùng là trạng thái riêng: vẫn đăng nhập, hiện cảnh báo hạn mức thay vì yêu cầu đăng nhập lại.

Khi mở tab và mỗi năm phút lúc tool hoạt động, kiểm tra lần lượt các phiên đã từng lưu, thu nhỏ Chrome, chỉ đọc giao diện; không gửi prompt hoặc tải tài liệu. Bỏ qua kiểm tra định kỳ khi có tác vụ chuyển đổi/đăng nhập. Đèn phản ánh lần kiểm tra gần nhất, không phải kết nối tức thời liên tục.

Thêm tài khoản mà chưa đăng nhập được: giữ hồ sơ đang thử để **Đăng nhập lại** trên dòng đó mở đúng hồ sơ, kể cả sau khi đóng/mở tool. Phiên đã lưu khác không bị xóa bởi lần thêm chưa thành công. Khi web báo phiên hết hạn/cần xác minh, trạng thái sẵn sàng bị gỡ; đăng nhập thành công sẽ xác nhận lại. Hạn mức là trạng thái riêng, không đồng nghĩa đăng xuất.

Đóng cửa sổ khi chưa đăng nhập không được coi là thành công. Chờ người dùng đăng nhập tối đa 10 phút; hồ sơ vẫn được giữ khi quá thời gian. Khi đang kiểm tra phiên, nút chính cho phép Hủy. Đóng BiliClass cũng hủy tác vụ và đóng Chrome riêng. Phiên web thuộc thư viện trên máy, không đưa vào Git, backup thư viện hoặc gói bài; không xuất cookie/token hay lưu mật khẩu bằng mã của BiliClass. Dữ liệu OAuth cũ được giữ riêng.

Nếu thấy trang xác minh Cloudflare, bạn tự hoàn tất trong Chrome; BiliClass chưa đọc hoặc điều khiển trang trong bước đăng nhập này. Nếu bước kiểm tra phiên vẫn gặp xác minh, app lưu lỗi và hiện **Dùng gửi/nhận thủ công**. Nút này chỉ chuyển cách gửi tài liệu khi người dùng chủ động chọn; không đánh dấu đã đăng nhập, không nhập phiên browser cá nhân vào tool. Nếu nhận diện được trang lỗi 400, app báo lỗi 400 thay vì phiên hết hạn, gỡ trạng thái sẵn sàng và giữ hồ sơ để thử lại. Không bấm CAPTCHA tự động hay đổi kỹ thuật để né xác minh.

Nếu browser thường cũng bị kẹt, cách thủ công chưa dùng được. Thử kiểm tra bằng mạng di động hoặc cửa sổ riêng tư theo [hướng dẫn đăng nhập OpenAI](https://help.openai.com/en/articles/7426629-why-cant-i-log-in-to-chatgpt). Nếu vẫn lặp, báo [OpenAI Support](https://help.openai.com/en/articles/8184038-captchas-in-chatgpt) kèm ảnh lỗi. Không tự xóa cookie, tắt VPN hay đổi mạng của người dùng từ BiliClass.

## Chọn Free/Plus

- Bài mới tự chọn tài khoản còn kết nối, chưa báo hết lượt: ưu tiên Plus/các gói trả phí đã nhận diện, rồi Free; tài khoản chưa biết gói đứng sau gói đã biết. Không hiện chính sách này trong giao diện. Các lựa chọn cố định cũ được chuyển về tự động khi mở tool.
- Nếu web báo hết lượt hoặc mất kết nối **trước khi gửi prompt**, thử tài khoản kế tiếp một lần. Lưu trạng thái hạn mức/mất phiên để các bài mới bỏ qua tài khoản đó. Khi kiểm tra lại đọc được phiên mà không còn cảnh báo hạn mức, cho phép thử lại; không suy ra số lượt còn lại.
- Khi mở phiên chuyển đổi, đọc lại nhãn gói hiện có. Nếu Plus đã xuống Free, cập nhật thành Free. Quan sát này áp dụng cho lựa chọn bài sau; bài đang gửi giữ nguyên tài khoản.
- Sau khi đã bắt đầu gửi prompt, không đổi tài khoản tự động khi hết quota, lỗi mạng hoặc cần xác minh. Tiếp tục dùng đúng cuộc trò chuyện/tài khoản đã ghi; trạng thái gửi không rõ thì dừng, không gửi trùng. Nếu bài đã gửi đang hết lượt, chờ hạn mức được cấp lại; không đăng nhập lại chỉ để giải quyết quota.
- Số dư/quota reset chưa có nguồn đọc đáng tin cậy trong adapter nên **ẩn dòng hạn mức**, không tạo số dư hoặc phần trăm giả. Chỉ hiện cảnh báo hết lượt khi đọc được thông báo của web. Bảng [OpenAI Docs về hạn mức Work/Codex](https://learn.chatgpt.com/docs/pricing) không được dùng để suy ra số dư chat web của từng profile.

## Chuyển đổi bài

Nhập nguồn → chọn một trong bốn **Kiểu chuyển đổi**, giữ thiết kế gốc hoặc mẫu → **Chuyển đổi bằng ChatGPT**. App chuẩn bị prompt và tệp, chọn model trong các lựa chọn web đang hiển thị và được phép dùng; bật nút Think/Thinking nếu có toggle nhận diện được. Nếu không có nút hoặc giao diện đổi, giữ lựa chọn mặc định. Không cam kết suy luận cao nhất khi không xác nhận được điều khiển; không mở khóa model trả phí.

Free có công cụ/tải tệp với giới hạn riêng theo [hướng dẫn OpenAI](https://help.openai.com/en/articles/9275245-chatgpt-free-tier-faq). Có thể không tạo được PPTX trong một phiên hoặc phải chờ quota. BiliClass không bảo đảm Free có cùng chất lượng/tính năng với Plus.

Prompt yêu cầu PowerPoint chỉnh sửa được, bảo toàn nội dung/hình nguồn theo lựa chọn, Speaker Notes VI:/EN: để đọc và CHECK: cho phần chưa chắc. Nhận tệp → kiểm tra PPTX → lưu bản gốc trả về → chuẩn bị âm thanh nháp nếu bật → xem trình chiếu → giáo viên xác nhận **Dùng để dạy**. Không tự duyệt nội dung hoặc phát âm thanh nháp. Lỗi một giọng đọc không bỏ PowerPoint đã nhận.

Sau khi xác nhận **Dùng để dạy**, mở chính tệp nhận về trong Microsoft PowerPoint, toàn màn hình và chỉ đọc. Mascot đã bật sẽ tự xuất hiện ở dạng trong suốt, thu gọn; kéo để di chuyển, bấm để mở **Đọc tiếng Anh**, **Dừng đọc**, **Trước/Sau**. Nội dung đọc theo slide thực tế, dùng Speaker Notes/cặp ngôn ngữ đã nhận, không dịch lại. Đổi slide hoặc đóng trình chiếu dừng lời đọc trước; kết quả tổng hợp đến muộn không được phát sai slide. Slide chưa có English không bật nút đọc. Không tự phát loa khi vào bài. Cần Microsoft PowerPoint cài trên máy cho luồng này.

Khi bắt đầu trình chiếu, mascot được đặt trên màn hình PowerPoint thực tế, kể cả khi vị trí cũ thuộc màn hình khác. Sau đó vẫn kéo tự do qua các màn hình và lưu vị trí mới; không liên tục kéo mascot ngược về màn hình chiếu.

Đợt sửa trình chiếu 04/10/2026 được kiểm tra bằng `scripts/qt_teaching_smoke.py`: Qt thật, PowerPoint thật, giọng English cục bộ, ba slide thử, điều khiển view Office bên ngoài worker cùng nút mascot, đóng rồi mở lại, SHA của cả hai bản nguồn không đổi. `scripts/verify_navigation_mascot.py` kiểm tra trong suốt/kéo/lưu vị trí/menu. 30 kiểm thử PowerPoint/conversion/handoff/voice passed. Chưa chứng nhận Presenter View, máy chiếu hay bản đóng gói mới. Hộp hỏi lưu thay đổi thiết lập trình chiếu đã được tránh cho riêng deck chỉ đọc; không tắt cảnh báo toàn bộ Office.

Khi gặp xác minh, đăng nhập hết hạn hoặc giới hạn: dừng, hiện thông báo, giữ trạng thái. Không dùng stealth, giải CAPTCHA hoặc endpoint web nội bộ. **Gửi/nhận thủ công** trong Tùy chọn thêm là dự phòng. Bài đã nhập thư viện có thể mở lại ngay cả khi xóa tài khoản; không gửi lại và không tạo bài trùng.

Ở trang chuyển đổi, **Đăng nhập và tiếp tục** mở đúng hồ sơ/cuộc trò chuyện đã ghi; sau khi xác nhận đăng nhập, tool tự tiếp tục bài đó. Chỉ tiếp tục khi người dùng bấm nút này; đóng/hủy/chưa xác nhận đăng nhập không khởi động chuyển đổi. Bài đã gửi không chuyển sang tài khoản khác.

Trong bước đăng nhập, Chrome tự tải trang và được giữ để người dùng hoàn tất; không tự khởi động lại luồng đăng nhập. Sau xác nhận hoặc trong tác vụ chuyển đổi, adapter chờ tài liệu chính và các điều khiển sẵn sàng thay vì chờ toàn bộ tài nguyên trang. Timeout tải trang không tự tải lại phiên đăng nhập. Kiểm tra prompt còn nguyên và mọi đính kèm hiển thị trước khi Gửi. Yêu cầu xuất PPTX bổ sung được ghi trước khi gửi và chờ câu trả lời mới; không nhận tệp từ câu trả lời cũ. Nhận hạn mức qua thông báo của web, tránh nhầm chữ “giới hạn/hạn mức” trong bài học thành lỗi.

### Tự phục hồi và đính kèm bài thật

Ngày 04/10/2026, lần chuyển đổi thật đầu tiên dừng trước gửi vì `set_input_files` timeout sau 10 giây dù Chrome đã nhận tệp PPTX khoảng 16 MB. Tiếp theo phát hiện ô ProseMirror thêm dòng trắng và thư viện web đổi tên tệp tải lên thành `tai-lieu-goc(2).pptx`. Đã sửa ba chỗ: chọn input phù hợp với loại tệp; timeout của sự kiện input chuyển sang quan sát đính kèm thực tế, không đặt tệp lần hai trong cùng trang; chấp nhận tên đánh số do web ghi rõ. Làm sạch các đính kèm tên nội bộ của tool trong composer chưa gửi, không xóa thư viện web/tệp nguồn hoặc thao tác trong câu trả lời. Chỉ gửi khi mọi đính kèm hiển thị, không còn tiến độ tải và nút Gửi sẵn sàng. Kiểm tra prompt giữ nguyên mọi ký tự ngoài khoảng trắng; xuống dòng do editor không bị coi là mất nội dung.

Lỗi mạng/browser/tải kết quả tạm thời được tự thử lại tối đa hai lần, chờ 2 và 5 giây. Chỉ khôi phục khi chưa gửi, hoặc đã xác nhận cuộc trò chuyện đang chờ; bài đã gửi mở đúng URL và không gửi lại prompt. Trạng thái `submitting` chưa xác nhận, xác minh người dùng, mất phiên, hết lượt, lỗi giao diện/nội dung và hết thời gian tạo bài không được tự lặp vô hạn. Hủy dừng cả thời gian chờ phục hồi. Chỉ sau khi các lần thử không thành công mới cảnh báo cần can thiệp. Cách thủ công nằm trong **Tùy chọn khác**, không phải một bước của luồng tự động.

Giao diện thực tế trả tệp bằng nút tên `.pptx`, không có anchor tải. Adapter nhận nút trong câu trả lời cuối, mở thẻ tệp rồi kích hoạt **Download file** của đúng tên kết quả. Chỉ so khớp trong vùng preview chứa một nút tải; không bấm nút tải tệp nguồn hoặc artifact khác. Dùng Enter trên nút tải để tránh lớp mở thẻ tệp của web đè lên icon. Download được kiểm tra đuôi, kích thước, cấu trúc ZIP/PPTX trước khi lưu. Lỗi tải không bị báo nhầm thành mất đăng nhập.

Sau sửa, **đã gửi và nhận PowerPoint thật qua tài khoản web đã lưu**: nguồn 15.992.900 byte; kết quả 15.386.284 byte, 12 slide, 25 mục media và 12 trang ghi chú. Số slide/media bằng nguồn; điều này không chứng minh bố cục, công thức hoặc bản dịch hoàn toàn đúng. App đã lưu bài với 12 đoạn song ngữ, tạo đủ 12 WAV Việt/12 WAV Anh phù hợp văn bản/giọng/tốc độ đã chọn và dựng ảnh xem trước slide đầu bằng Office. Bài vẫn là bản nháp, chưa tự duyệt. Chất lượng sư phạm/bố cục và phát giọng trong tiết dạy cần giáo viên kiểm tra.

## Kiểm tra

- 78 kiểm thử browser/Chrome/dispatch/handoff đã qua, cùng các ca nhận tệp được chạy lại sau sửa nút tải: hồ sơ riêng, khóa/xóa, backup không chứa phiên, ưu tiên Plus, bỏ lựa chọn cố định cũ, hạ gói, gói chưa rõ, lựa chọn model được phép, Think, không nhầm giao diện khách với đăng nhập, dừng vòng lặp xác minh, hủy/tiếp tục xác minh, không gửi lại khi trạng thái chưa chắc, tải lại và giữ tài khoản. Thêm timeout sự kiện upload đã nhận tệp, chặn upload chưa có đính kèm, input ảnh không nhận PPTX, editor thay xuống dòng, tệp web đánh số, nút tệp/preview có artifact khác, lỗi tải không gỡ đăng nhập và phục hồi có giới hạn không gửi trùng.
- Browser test chạy Chrome thật trên trang fixture được chặn mạng hoặc máy chủ localhost; không đăng nhập/tải tài liệu thật lên ChatGPT. Kiểm tra cookie fixture và localStorage còn sau khi đóng/mở tiến trình, không lẫn giữa hai hồ sơ; chỉ dùng endpoint debug cục bộ, hủy trước khởi động không tạo tiến trình. Thử Chrome thường thật không có cổng debug: đóng đúng cửa sổ riêng, giữ cookie fixture khi mở lại và không đóng tiến trình Chrome của hồ sơ khác. Adapter chỉ gắn phần điều khiển sau xác nhận; đóng sớm hoặc hủy không báo thành công. Các ca chờ tải chậm của adapter quan sát cũ vẫn được giữ, không đại diện cho đăng nhập thật.
- Qt Browser AI kiểm tra đóng sớm, đăng nhập/xác nhận, thêm tài khoản, từng dòng thông tin và nút **Xóa profile**; ẩn menu/chính sách/số dư chưa biết. Luồng fixture Plus hết lượt trước gửi → Free gửi đúng một lần → mất phiên → đăng nhập và tiếp tục cùng cuộc trò chuyện; nhận PPTX/audio giả lập và xem trước bằng Office thật; kiểm tra lại phiên, cảnh báo mất kết nối, xóa từng hồ sơ và mở lại bài không cần tài khoản. Các tab Chung/Song ngữ/Giọng đọc/Mascot được giữ. Smoke Qt đăng nhập OAuth cũ cũng qua, không có cảnh báo QML.
- OAuth cũ có smoke riêng để tránh làm hỏng dữ liệu và yêu cầu đã có: [thiết kế và chẩn đoán cũ](CHATGPT_PLAN_AUTH.md).

Còn cần nghiệm thu thật: đọc gói trên giao diện thực tế, lựa chọn suy luận, chất lượng kết quả và giới hạn lượt dùng; sau đó thử tài khoản Plus, tài liệu/môn khác và bản đóng gói. Đăng nhập và gửi/nhận một PPTX thật đã được xác nhận; kết quả đó không chứng minh mọi tài liệu hoặc tài khoản đều hoạt động.
