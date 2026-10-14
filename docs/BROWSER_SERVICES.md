# Browser AI: ChatGPT và Gemini từ RC28

Trong Cài đặt → Browser AI có hai lựa chọn loại trừ nhau: ChatGPT/Gemini.
Chọn dịch vụ rồi Thêm tài khoản, đăng nhập trong Chrome riêng, đóng cửa sổ
hoặc bấm Kiểm tra và lưu. Tên, gói nếu xác định được và trạng thái đăng nhập
hiển thị theo mỗi profile. Mỗi tài khoản có thư mục và khóa riêng; tài khoản
ChatGPT cũ vẫn giữ nguyên profile, trạng thái và bài đã gửi khi nâng cấp.

Tích tài khoản cần dùng để cố định bài mới vào đúng tài khoản đó. Nếu tài
khoản được tích chưa đăng nhập/hết lượt, tool báo rõ, không tự chọn người
khác. Chọn Tự chọn tài khoản đang kết nối để dùng ưu tiên gói trả phí còn
quyền trước Free trong cùng dịch vụ. Chỉ đổi tài khoản trước khi gửi; lượt
đã gửi hoặc chưa rõ xác nhận luôn được giữ đúng dịch vụ/profile/cuộc trò
chuyện. Đổi ChatGPT/Gemini không chuyển bài đang dở sang dịch vụ mới.

## Model và suy luận

Mỗi lượt gửi chính, yêu cầu xuất tệp hoặc sửa bài của yêu cầu mới kiểm tra
model/suy luận trước khi gửi. Đọc menu web thật, loại mục bị khóa/nâng cấp,
chọn phương án mạnh nhất mà adapter nhận diện được, rồi đọc lại lựa chọn.
ChatGPT bật Think khi tài khoản có Think, chọn effort High/Extended/Extra
high nếu được cung cấp. Gemini ưu tiên Pro hơn Thinking/Fast, so sánh phiên
bản trong cùng nhóm và chọn suy luận phức tạp/effort cao nếu có điều khiển.
Model có suy luận tích hợp được ghi là suy luận của model đã xác nhận khi
web không có effort riêng. Không thay tên menu bằng tên model tự đoán, mua
gói, truy cập model bị khóa hoặc báo High khi web chưa xác nhận.

Nếu menu mới không đọc/xác nhận được, tool dừng và giữ bài. Không bảo đảm
tên model hoặc effort cố định cho mọi tài khoản/ngày: giao diện, rollout,
hạn mức và quyền tài khoản do dịch vụ quyết định. Tên ví dụ do người dùng
nêu là mục tiêu khi chúng thực sự được hiển thị và được phép dùng.

## Gửi và nhận

Cấu hình môn/khối, bốn kiểu ngôn ngữ, thiết kế gốc/mẫu và lưu ý giáo viên
dùng cùng hợp đồng prompt. Gemini có thêm chỉ dẫn xuất PowerPoint trực tiếp
hoặc Canvas → Google Slides → File → Download → Microsoft PowerPoint. Chỉ
nhận tệp của câu trả lời mới nhất, kiểm tra đuôi/bytes/PPTX trước khi lưu.
Google Slides có thể thay đổi hiệu ứng/đối tượng của tệp gốc; bước kiểm tra
nguồn và slide vẫn áp dụng, không tự chứng nhận đã giữ nguyên.

Tệp Gemini tối đa 100 MB và tối đa 10 tệp/lượt theo [hướng dẫn tải tài liệu
của Google](https://support.google.com/gemini/answer/14903178?hl=en).
[Canvas](https://support.google.com/gemini/answer/16047321?hl=en) hỗ trợ xuất
slide sang Google Slides; [tài liệu tác vụ Gemini](https://support.google.com/gemini/answer/17094507?hl=en)
liệt kê PPTX trong các tệp có thể tạo. Khả năng cụ thể phải có trong phiên
tài khoản của giáo viên; khi không nhận được tệp, giữ chat và báo giới hạn,
không chuyển HTML/PDF/dàn ý thành kết quả PowerPoint giả.

Chrome và thao tác web UI được dùng trực tiếp; không API key, không gọi
endpoint riêng, không đọc/xuất cookie hoặc token. Đăng nhập/xác minh Google
vẫn do giáo viên thực hiện. Gói model giọng dùng trên máy, tách khỏi hai
dịch vụ: nhận và lưu PPTX rồi dừng, chỉ tạo voice sau khi bấm nút.

## Phạm vi kiểm chứng

Kiểm thử Chrome thật dùng trang fixture được route cục bộ: tải tệp, chọn
Gemini Pro và effort cao, đọc lại lựa chọn, nhận PPTX trực tiếp/qua menu
Google Slides, khôi phục gửi chưa rõ xác nhận không gửi thêm; lựa chọn
model chưa xác nhận chặn gửi. Qt nguồn chạy chọn dịch vụ/profile và toàn
luồng chuyển đổi với Office preview thật, web/voice fixture.

Chưa nghiệm thu tạo bài bằng tài khoản Gemini thật trên máy: cần giáo viên
thêm profile và đăng nhập Google lần đầu. Fixture chứng minh logic của tool,
không chứng minh mọi rollout/menu Gemini hoặc mọi bài giảng thực đều chạy
thành công. Khi gặp giao diện mới, giữ trạng thái và báo lỗi cần kiểm tra.
