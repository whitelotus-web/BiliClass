# Kết nối trực tiếp ChatGPT qua OAuth · luồng cũ

Từ 04/10/2026, đăng nhập mặc định đã chuyển sang phiên web Free/Plus. Tài liệu dưới đây lưu thiết kế OAuth và chẩn đoán trước đó, không mô tả nút đăng nhập hiện tại. Xem [Browser AI](BROWSER_AI.md). Các yêu cầu OAuth cũ vẫn được giữ và tiếp tục bằng đúng kết nối cũ nếu còn quyền.

Mã nguồn ngày 03/10/2026 đã dùng Sign in with ChatGPT (OAuth) và Responses streaming. Không cần API key hoặc billing API riêng; nếu được cấp quyền, app dùng hạn mức gói ChatGPT. Đây không phải điều khiển DOM/cookie của trang ChatGPT. Release RC12 chưa chứa thay đổi này.

## Thiết lập một lần

1. **Cài đặt → Browser AI → Đăng nhập ChatGPT**. Đây là nút đăng nhập duy nhất; không cần bấm Lưu.
2. Đăng nhập trong cửa sổ Edge riêng của BiliClass và đồng ý cho BiliClass dùng hạn mức ChatGPT. Mật khẩu chỉ nhập trên trang OpenAI.
3. App nhận callback, kiểm tra token ký số rồi tự lưu phiên được mã hóa bằng DPAPI của tài khoản Windows. Sau thành công, tab hiện tên/email từ danh tính đã xác minh, thời điểm lưu và quyền xử lý. Không có bước Lưu riêng. Nút chính đổi thành **Đăng nhập lại** khi có tài khoản, hoặc **Hủy** trong lúc chờ. Chính nút này tiếp tục đăng ký dang dở sau lỗi trao đổi mã; sau lỗi workspace/client không dùng lại mã bị từ chối. Mã cũ được giữ riêng, không trộn với tài khoản mới. Hồ sơ browser lưu dưới LocalAppData của Windows theo mã máy; hồ sơ cũ trên ổ dự án vẫn được giữ.

Cửa sổ browser và khóa hồ sơ được giữ đến khi trao đổi mã, xác minh danh tính và lưu kết nối xong; sau đó cửa sổ tự đóng. Hủy, lỗi hoặc hết thời gian chờ cũng đóng phiên. **Đóng cửa sổ không chứng minh đã kết nối:** chỉ báo thành công và hiện tài khoản sau khi trao đổi/xác minh token xong. Trang trắng quá 60 giây sẽ dừng và báo lỗi; trang đăng nhập đã hiện vẫn có thời gian để người dùng nhập thông tin. Khi chuyển đổi, app dùng kết nối đã lưu và không mở browser.

Đăng nhập lại tài khoản đã lưu luôn dùng mã của tài khoản đó. Khi chưa có tài khoản, chỉ lỗi trao đổi mã `invalid_grant` mới tự tiếp tục mã pending qua nút chính. Browser đóng sớm, hủy hoặc lỗi workspace sẽ bắt đầu đăng ký mới, vì mã pending còn trên máy có thể thuộc lần thử khác. CLI `--resume` vẫn dành cho việc tiếp tục rõ cùng tài khoản/workspace.

Nếu chính lần tiếp tục pending bị từ chối workspace, app mở đăng ký mới một lần trong cùng lượt bấm để người dùng chọn tài khoản/workspace và cấp quyền trên OpenAI. Mỗi lượt có state/nonce/PKCE mới, định danh máy giữ nguyên. Không thực hiện nhánh này với tài khoản đã xác minh, lỗi từ chối consent hoặc lần đăng ký mới đã bị chặn; không lặp đăng nhập để vượt kiểm tra quyền. Tài liệu OpenAI nêu [đăng ký được gắn với user/workspace](https://developers.openai.com/siwc/token-sharing-open-source) và [chọn đăng ký riêng khi dùng tài khoản khác](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions).

Nếu lần trước báo `invalid_state`, `invalid_grant` hoặc trang Authentication Error, lần đăng nhập tiếp theo dùng thư mục hồ sơ Edge mới của BiliClass. Các hồ sơ cũ được giữ nguyên; định danh máy, đăng ký ứng dụng và kết nối đã lưu không bị đổi. Không mở lại URL đăng nhập cũ. Discovery chạy trong lúc người dùng đăng nhập để giảm việc chờ sau callback, nhưng không chặn trước khi mở cửa sổ.

Chẩn đoán nằm tại `<thư-mục-thư-viện>/chatgpt_plan/login-diagnostics.json`, chỉ ghi bước xử lý, thời gian, mã lỗi, HTTP status và request ID đã lọc. Không ghi URL OAuth, state, mã đăng nhập, token, email hay nội dung phản hồi. Tệp chỉ được lưu khi kết thúc thành công/thất bại, không đưa vào Git. Chuỗi `callback_received → exchange_started → failed` với `invalid_grant` cho biết mã bị từ chối ở bước trao đổi, không đủ để kết luận mã hết hạn. Các bước `registration_new`, `registration_pending`, `registration_saved` phân biệt loại đăng nhập; `registration_restarted` đánh dấu một lần cấp quyền mới sau khi pending bị từ chối. Giữ nguyên kiểm tra state/PKCE/nonce khi chẩn đoán.

Menu **⋯** chỉ hiện khi đã có tài khoản, chứa đổi/thêm, chọn kết nối đã lưu, xóa và đường dẫn hạn mức trên ChatGPT. Xóa thu hồi refresh token khi dịch vụ cho phép rồi xóa phiên tại máy; lỗi mạng sẽ báo chưa xác nhận thu hồi. Thông tin hạn mức hiện trực tiếp dưới tài khoản, nhưng hiện chưa có số liệu số dư từ kết nối OAuth này: app báo **Chưa có số liệu hạn mức còn lại từ OpenAI cho kết nối này**. Không suy đoán phần trăm, thời gian reset hoặc gói Plus/Free từ danh tính, scope hay tên model. Tài liệu OpenAI hiện hướng dẫn [quản lý hạn mức trên ChatGPT Settings → Usage](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions). Không đọc cookie hoặc dùng endpoint web nội bộ để lấy số liệu.

Plus/Pro đủ điều kiện theo [tài liệu chính thức](https://developers.openai.com/siwc/quickstart); nhãn gói không thay thế quyền thực tế của ứng dụng/tài khoản. Free hoặc mất quyền không được coi có thể tự xử lý như Plus. App giữ nguyên tài khoản đã chọn; không quay vòng tài khoản, chuyển billing hoặc tự mua gói.

## Chuyển đổi và dạy

1. Nhập PPTX/DOCX/PDF/TXT/PNG/JPG hoặc dán chữ; chọn tên bài, môn/khối, L0–L4 và bố cục. PPTX có thể giữ thiết kế gốc hoặc dùng mẫu; tài liệu khác dùng mẫu.
2. Bấm **Chuyển đổi bằng ChatGPT**. Nguồn được sao chép và băm tại máy; app gửi chữ, vị trí/manifest và ảnh cần đọc qua kết nối đã chọn. Nội dung này sẽ ra ngoài máy khi bấm chuyển đổi.
3. Model được lấy từ catalog được cấp quyền, bỏ model ẩn và ghim model cho yêu cầu. Auto hiện chọn model công khai đầu tiên theo thứ tự dịch vụ; không cam kết đó là model mạnh nhất của giao diện web.
4. AI trả JSON đầy đủ theo nguồn và hỗ trợ theo level. App kiểm tra cấu trúc, nguồn, số lượng/đúng thứ tự khối, văn bản gốc và cặp song ngữ sẵn có. Chỉ nhận sau sự kiện hoàn tất; dữ liệu một phần không được áp dụng.
5. BiliClass dựng PowerPoint tại máy: giữ ảnh/đối tượng nguồn, thêm hỗ trợ vào vùng trống hoặc trang hỗ trợ khi kín. Trong chế độ giữ thiết kế, vị trí nguồn được ưu tiên; bố cục hai cột/đổi form đầy đủ phù hợp hơn với mẫu. L4 có thể thay chữ trong bản xuất bằng English; tệp gốc vẫn riêng và không thay đổi.
6. App chuẩn bị lời đọc bằng voice cục bộ theo level; voice lỗi/thiếu không xóa bài. Xem slide hoặc mở toàn bộ bài, rồi **Dùng để dạy** và xác nhận cả bài. Trước đó nội dung AI và trợ giảng vẫn là nháp. Quiz và kho kiến thức không được tự duyệt.

Ảnh/PDF scan được gửi dưới dạng hình để đọc; chữ mờ phải đánh dấu `SOURCE_MISSING`, chặn chốt bài đến khi thầy cô sửa. Word giữ chữ và ảnh nhúng; không tái tạo nguyên form Word. PowerPoint có ảnh/biểu đồ được render bằng Office khi có; khi không có Office, chỉ gửi hình nhúng đọc được và báo giới hạn. Xem trước và điều khiển trình chiếu cần Microsoft PowerPoint trên máy. Không bảo đảm đọc đúng mọi hình, công thức hoặc giữ được mọi trigger/font; cần đối chiếu bài thật.

## Khi kết nối gián đoạn

Các phần hoàn tất được cache theo nguồn/cấu hình/model/prompt/thuật ngữ. Mất stream chưa rõ kết quả sẽ yêu cầu xác nhận trước khi gửi lại, vì có thể dùng thêm hạn mức. Lỗi quyền/quota dừng và giữ bài, không tự đổi tài khoản. Mở lại yêu cầu đã nhận sẽ mở cùng bài trong thư viện, không gửi AI và không tạo bản trùng. Bài đã nhận có thể dựng lại/chiếu mà không cần kết nối ChatGPT.

**Gửi/nhận thủ công** tạo prompt yêu cầu PPTX và gói nguồn để thầy cô gửi trên web, rồi nhận file tải về. **BiliClass ngoại tuyến** vẫn dùng model dịch tại máy. Yêu cầu web cũ không được tự gửi lại bằng provider OAuth mới. Nhận JSON thủ công chưa có trong giao diện đợt này.

## Bằng chứng hiện tại

- Kiểm thử OAuth giả lập: callback sai trạng thái, PKCE, đăng ký client động, chữ ký/audience/nonce/hết hạn, scope, refresh, không quay vòng tài khoản, DPAPI Windows thật. Phiên Edge có hồ sơ riêng và khóa phiên; Windows job chỉ đóng cây tiến trình tool tạo, không đóng browser cá nhân.
- Kiểm thử Responses: catalog/model ẩn, dữ liệu stream chỉ nhận khi hoàn tất, quota giữa stream, hủy và lỗi HTTP; không gửi các trường API không được hỗ trợ.
- Luồng dữ liệu: PPTX gốc/song ngữ/ảnh/chữ dài, Word có ảnh, PDF scan, ảnh, nguồn thay đổi, hỗ trợ theo level, gói chia sẻ có ảnh, cache/tiếp tục và dữ liệu sai nguồn.
- Qt smoke với AI/audio giả lập: một nút chuyển đổi → PowerPoint render thật → xác nhận cả bài → bàn giao trình chiếu/mascot; mở lại bài không cần tài khoản và không gọi AI nữa. Luồng nhận PPTX thủ công vẫn qua Qt/Office.
- Đăng nhập thật ngày 04/10: sau bản sửa vòng đời browser, chẩn đoán mới dừng ở trang từ chối workspace sau khoảng 60 giây, chưa có `callback_received`; store vẫn không có tài khoản. Lần này nút chính tiếp tục pending sau lỗi `invalid_grant` trước đó. Không còn đủ cơ sở quy lỗi hiện tại cho đóng browser hay mã hết hạn. Đã bổ sung một lần cấp quyền mới khi pending bị từ chối, nhưng chưa xác nhận kết nối thật thành công. **Chưa xác nhận OAuth thành công/catalog/inference/hạn mức bằng tài khoản thật**, chưa nghiệm thu hai giáo viên hoặc build executable mới. Không có tài liệu dạy thật được gửi trong kiểm thử.

Chạy kiểm thử trong `.venv` của dự án. Sau sửa phiên đăng nhập ngày 04/10/2026: **46 kiểm thử OAuth/browser/provider passed**, Ruff không lỗi. Kiểm thử giữ browser/khóa hồ sơ qua discovery, trao đổi mã, xác minh và lưu; hủy hoặc bị từ chối không tạo tài khoản; chẩn đoán không chứa dữ liệu OAuth nhạy cảm. Năm trường hợp mới kiểm tra pending bị chặn rồi cấp quyền thành công hoặc tiếp tục bị chặn, không retry consent đã từ chối, đăng ký mới bị chặn hoặc tài khoản đã lưu bị chặn. `scripts/qt_chatgpt_login_smoke.py` kiểm tra bằng OAuth giả lập: lỗi workspace và lỗi phiên không lưu tài khoản, thử lại/tiếp tục trao đổi mã/đăng nhập lại/hủy qua đúng một nút, thông tin xác minh và hạn mức chưa có số liệu hiện trực tiếp, menu tài khoản và giao diện 1366×850/1080×700. Báo cáo tại máy: `reports/chatgpt-plan/qt-login.json`. CLI `scripts/chatgpt_connect.py --data <thư-mục-thư-viện>` tạo kết nối mới; `--resume` tiếp tục đăng ký dang dở với tài khoản/workspace cũ. Kiểm thử Qt/Office luồng chuyển đổi trước đây ở `scripts/qt_chatgpt_plan_smoke.py` và `scripts/qt_chatgpt_handoff_smoke.py`. Chưa xác nhận OAuth/inference thật.

Thiết kế và các bước còn cần nghiệm thu: [CHATGPT_PLAN_UPGRADE.md](CHATGPT_PLAN_UPGRADE.md). Căn cứ kết nối: [OAuth cho ứng dụng nguồn mở](https://developers.openai.com/siwc/token-sharing-open-source/sign-in), [model và inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference), [giới hạn preview](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
