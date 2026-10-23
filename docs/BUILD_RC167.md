# BiliClass 1.0.0rc167

Một số nhãn lớp học như “DỰ ĐOÁN THỨ NHẤT” được dịch vụ dịch trả về
“PREDICTION NUMBER 1”. Bộ kiểm tra số liệu đúng nguyên tắc nên dừng vì
nguồn không có chữ số 1. Dịch cục bộ các tiêu đề thứ tự đầy đủ của dự
đoán, thí nghiệm, hoạt động, nhiệm vụ, ví dụ, bước và trường hợp sang
chữ thứ tự tiếng Anh, từ thứ nhất đến thứ mười.

Giữ nguyên bộ kiểm tra số liệu và công thức. Thuật ngữ giáo viên khóa
có ưu tiên. Không coi “thứ hai” đứng riêng hoặc trong câu là số thứ tự,
vì có thể là ngày trong tuần. Không áp dụng quy tắc tiêu đề cho câu dài.

Kiểm chứng: 53 kiểm thử thuật ngữ và Google Translation đạt, bao gồm
bảo vệ số liệu, sửa kết quả sai có giới hạn, ưu tiên thuật ngữ giáo viên,
chữ hoa/thường và các nhãn thứ tự mới.

Giữ nhãn đầu/chân trang nhỏ theo cỡ chữ nguồn khi dàn song ngữ; không
phóng nhãn 8–10 pt lên cỡ chữ nội dung. Nhãn ngắn trong dải hẹp giữ
nguyên vị trí, dùng cùng tỉ lệ chữ Việt/Anh và được căn trong dải đó.
Nhận diện nhãn trục là một ký hiệu kèm đơn vị SI, ví dụ “F (N)” và
“a (m/s²)”, để giữ một bản dùng chung. Câu có chữ Việt/Anh kèm đơn vị
vẫn phải chuyển ngữ. Không thay đổi dữ liệu hoặc bỏ qua lỗi bố cục.

Tổng cộng 158 kiểm thử native bilingual, same-slide, thuật ngữ, dịch,
ngữ nghĩa ký hiệu, sửa bố cục và kiểm tra chuyển động đạt. Ruff và
compileall đạt. Qt smoke mở trang Chuyển đổi đạt, không cảnh báo QML.
Luồng chuyển đổi thật của bài STEM 13 trang tạo 14 trang song ngữ
(một trang nội dung dài được tiếp nối), Office kiểm tra 14/14 trang,
không còn lỗi FAIL; các CHECK vẫn yêu cầu đối chiếu thuật ngữ, công
thức, chữ nhỏ và hình ảnh theo hướng dẫn trong ứng dụng.

Đây là mốc mã nguồn phục vụ quay demo. Bộ cài RC166 hiện có được giữ
nguyên; chưa tạo lại bộ cài cho RC167 trong lần chuẩn bị video này.
