# Browser AI · kết nối ChatGPT

Mã nguồn ngày 03/10/2026 đã dùng Sign in with ChatGPT (OAuth) và Responses streaming. Không cần API key hoặc billing API riêng; nếu được cấp quyền, app dùng hạn mức gói ChatGPT. Đây không phải điều khiển DOM/cookie của trang ChatGPT. Release RC12 chưa chứa thay đổi này.

## Thiết lập một lần

1. **Cài đặt → Browser AI → Continue with ChatGPT**.
2. Đăng nhập trong cửa sổ Edge riêng của BiliClass và đồng ý cho BiliClass dùng hạn mức ChatGPT. Mật khẩu chỉ nhập trên trang OpenAI.
3. App nhận callback, kiểm tra token ký số rồi tự lưu phiên được mã hóa bằng DPAPI của tài khoản Windows. Không có bước Lưu riêng. Cửa sổ đăng nhập tự đóng khi nhận callback, hủy hoặc hết thời gian chờ. Khi chuyển đổi, app dùng kết nối đã lưu và không mở cửa sổ browser.

Có thể thêm, chọn, đăng nhập lại hoặc xóa kết nối; xóa thu hồi refresh token khi dịch vụ cho phép rồi xóa phiên tại máy. Nếu mạng lỗi, app báo chưa xác nhận thu hồi và vẫn xóa phiên cục bộ. Nút **Xem hạn mức ChatGPT** mở trang của ChatGPT. Hồ sơ Edge/Chrome cũ vẫn giữ tại máy, không chuyển cookie hay lấy token của Codex. Đăng nhập lại qua nút mới để dùng OAuth.

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
- Đăng nhập thật chưa thành công: người dùng báo trang lỗi trước callback, chưa rõ thông báo cụ thể. Đã chỉnh lại việc chỉ gửi `agent_name_hint` ở đăng ký đầu tiên, chưa xác nhận đó là nguyên nhân lỗi. **Chưa xác nhận catalog/inference/hạn mức bằng tài khoản thật**, chưa nghiệm thu hai giáo viên hoặc build executable mới. Không có tài liệu dạy thật được gửi trong kiểm thử.

Chạy `.venv/Scripts/python.exe -m pytest -q`, `scripts/qt_chatgpt_plan_smoke.py` và `scripts/qt_chatgpt_handoff_smoke.py` bằng môi trường dự án. `scripts/qt_browser_ai_smoke.py` chuyển tới smoke OAuth mới. Script `scripts/chatgpt_connect.py --data <thư-mục-thư-viện>` dành cho kiểm tra đăng nhập thật; không in token.

Thiết kế và các bước còn cần nghiệm thu: [CHATGPT_PLAN_UPGRADE.md](CHATGPT_PLAN_UPGRADE.md). Căn cứ kết nối: [OAuth cho ứng dụng nguồn mở](https://developers.openai.com/siwc/token-sharing-open-source/sign-in), [model và inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference), [giới hạn preview](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
