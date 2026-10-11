# Thư viện mẫu BiliClass

Ngày 11/10/2026. Áp dụng cho bản mã nguồn, chưa nằm trong bộ cài RC12.

## Ba phong cách, bốn kiểu chuyển đổi

Chuẩn lớp học (`standard` / `CLASSROOM`), Trực quan (`visual` / `VISUAL`) và Luyện tập & tương tác (`practice` / `PRACTICE`) là phong cách trình bày. Mỗi phong cách dùng được với bốn kiểu ngôn ngữ. Chọn mẫu không thay kiểu chuyển đổi, môn học hoặc khối lớp.

Prompt mới chỉ ghép module phong cách được chọn. Khi giữ thiết kế PowerPoint đầu vào, bỏ toàn bộ module mẫu và không đính kèm PowerPoint mẫu. Các yêu cầu bảo toàn số/thứ tự slide, hình, công thức, ghi chú, hoạt ảnh và trigger vẫn áp dụng cho bản sao nguồn. Không cam kết giữ hoạt ảnh chỉ từ prompt.

## Hai loại tài nguyên

- **Xem trước:** 12 PNG bố cục (tên bài, kiến thức, hình/chú thích, luyện tập) và 12 PNG kiểu ngôn ngữ. Popup mặc định hiển thị đúng phong cách/kiểu ngôn ngữ đã chọn. Các thumbnail khác cho xem riêng vai trò slide, có chú thích rõ đây là ví dụ phong cách, không phải đầu ra của bài đang nhập.
- **Gửi ChatGPT:** ba PPTX trung tính, mỗi file bốn slide với khung và font chỉnh sửa được. Không có bài hình chữ nhật, cấp số cộng, vòng tuần hoàn nước, công thức/ảnh demo, lời đọc hoặc QUIZ mẫu. Placeholder `[LESSON_TITLE]`, `[SUBJECT]`, `[GRADE]`, `[SOURCE_*]` phải được thay bằng nguồn giáo viên; vùng không dùng phải bỏ. Khung phải sắp lại theo kiểu ngôn ngữ được chọn.

Tài liệu giáo viên là nguồn nội dung của lần chuyển đổi. Ảnh minh họa chỉ nằm trong UI, không đính kèm yêu cầu. Mẫu quyết định phong cách, không cung cấp kiến thức. Tài liệu Word/PDF/ảnh được chia slide theo nguồn; PPTX phải giữ số lượng/thứ tự slide kể cả khi chọn mẫu mới.

`app/assets/templates/reference_library.json` ánh xạ ID ngoài sang ID nội bộ và đường dẫn thật. Mỗi mẫu có layoutMap cục bộ 1–4; không lấy các chỉ số 5–12 của demo tổng hợp để mở một file bốn slide. Thiếu mẫu thì dừng chuẩn bị gói, không âm thầm gửi thiếu mẫu. Hash của mẫu đã sao chép vào gói được kiểm tra khi mở lại. Prompt đã chuẩn bị giữ nguyên qua nâng cấp ứng dụng để tiếp tục đúng yêu cầu cũ.

## Điều chỉnh theo học sinh và môn

Prompt chọn hướng dẫn theo khối: 1–2, 3–5, 6–9, 10–12. Chữ nội dung mục tiêu lần lượt 28–36, 24–32, 22–30, 20–28 pt khi dùng mẫu mới; đây là khoảng ưu tiên, không phải ràng buộc phải đạt bằng cách bỏ nội dung. Bài giữ gốc ưu tiên font nguồn. English phù hợp tuổi, giữ đủ nghĩa và phương pháp đã chọn. Không rõ khối thì không mặc định THPT.

Quy tắc chuyên môn giữ ngữ liệu/trích dẫn cho Văn/Tiếng Việt, ký hiệu và điều kiện cho Toán/Lý/Hóa, nhãn sơ đồ cho Sinh/Khoa học, thời gian/bản đồ cho Sử/Địa, mã/lệnh cho Tin/Công nghệ, tác phẩm/bản nhạc cho Nghệ thuật, tình huống và quy tắc an toàn cho các hoạt động giáo dục. Môn tích hợp nhận các hướng dẫn phù hợp; môn nhập tay dùng nguồn/ngữ cảnh, không ép vào một môn mẫu.

Ba phong cách có quy tắc riêng theo vai trò slide: Chuẩn lớp học phân cấp kiến thức; Trực quan dành chỗ cho hình nguồn và dùng chữ khi không có hình; Luyện tập giữ trình tự đề/lời giải, không tự tạo đáp án. Không ép mọi bài vào một dàn ý cố định. Voice/Mascot vẫn lấy VI/EN trong Notes; QUIZ mới giữ nháp và đáp án phải thuộc các lựa chọn thực tế.

## Nguồn và tái tạo

Bộ thiết kế do người dùng cung cấp trong `BiliClass_ThuVienMau_Tron_Bo.zip`. Chỉ tích hợp tài nguyên mẫu dùng chung, không nhập bài giảng/thư viện cá nhân vào Git.

`scripts/import_template_library.py <zip>` đọc các đường dẫn đã định trong ZIP, sao chép PNG bố cục và chuyển ba PowerPoint sang khung trung tính bằng chỉnh OOXML. Giữ theme/font/khung gốc, loại đối tượng hình khoa học và nội dung demo. Script cũng sửa nhãn môn của demo ngôn ngữ về Vật lí/Physics, đúng với ví dụ vận tốc trong dao động điều hòa.

`scripts/render_template_previews.py` dùng Microsoft PowerPoint trên Windows để dựng 12 PNG kiểu ngôn ngữ đã sửa và kiểm tra mở/dựng cả 12 slide trung tính. Script không nằm trong luồng chuyển đổi thường ngày. Bản đóng gói đã thu toàn bộ `app/assets` nên không cần tải thêm thư viện mẫu khi dùng.

## Kiểm chứng và giới hạn

36 ca mới kiểm tra 12 gói phong cách/kiểu ngôn ngữ, không lẫn demo/Notes/ảnh, nguồn giữ nguyên, chọn quy tắc tuổi/môn, ánh xạ tài nguyên, tiếp tục đúng prompt và phát hiện mẫu bị sửa. 33 ca chuyển đổi/handoff/template hiện có qua. Smoke Qt kiểm tra cả 12 tổ hợp ảnh, thao tác nhập, prompt xem trước khớp gói gửi, luồng một nút với fixture web/voice và bản xem trước Office thật; không QML warning. Các PPTX trung tính mở/dựng được bằng PowerPoint.

Đợt này không gửi lại bài thật lên ChatGPT, không dùng hạn mức tài khoản để thử mọi tổ hợp. Khả năng bấm một lần gửi/nhận bài thật đã được kiểm tra ở đợt Browser AI trước. Chưa nghiệm thu sư phạm mọi môn/khối hoặc bảo toàn toàn bộ hoạt ảnh; giáo viên vẫn xem, kiểm tra và xác nhận bài trước khi dạy. Đây là cơ chế cấu hình thích ứng, không phải bộ kiến thức đầy đủ cho tất cả các môn.
