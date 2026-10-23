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

Bộ cài đầy đủ RC167 đã được đóng từ commit nguồn
`39b9fd554fcc0ca629b76c2695a9261b4cba2d04`, installer revision 2, lưu riêng
tại `F:\BiliClass-BoCai-RC167`. Ứng dụng được biên dịch lại toàn bộ; runtime
và mô hình của RC166 được đối chiếu hash trước khi tái sử dụng. Kiểm tra
khớp 189 module ứng dụng, 254 tài nguyên và 4.688 file trong gói.

Lần chuẩn bị bộ nộp chạy 160 kiểm thử liên quan chuyển đổi, thuật ngữ,
bố cục, ngữ nghĩa, chuyển động, đóng gói và installer, tất cả đạt. Ruff
đạt. Qt mở trang Chuyển đổi đạt, không cảnh báo QML. Đã cài thật bằng
Setup mới, mở Cài đặt, tạo giọng và chạy pipeline trong runtime đã cài,
rồi gỡ bản thử; thư viện thử được giữ riêng. Sáu bước kiểm tra bộ cài
đều đạt. Đây là kiểm chứng trên máy đóng gói; cần thử trên máy đích khác
trước khi bàn giao rộng rãi.

Key dùng thử được giao qua TXT riêng bên cạnh bộ cài theo yêu cầu người
dùng; không nằm trong EXE, ZIP, mã nguồn hoặc Git. Đã thử một yêu cầu
Google Dịch ngắn thành công. Giới hạn dịch vụ và quota trong Google Cloud
không thể suy ra từ việc gọi dịch thành công; chủ key cần kiểm tra riêng.
Video và bài Newton minh họa được để riêng trong thư mục bàn giao, không
tự nhập vào thư viện người cài.

Bằng chứng máy cục bộ: `reports/rc167-submission/delivery-verification.json`.

SHA-256 của Setup (57.856 byte):
`c60afd360911d50f18d10b75154ee5efcf61aa807042803316b5e514118a8580`.
SHA-256 của ZIP đầy đủ (1.259.534.956 byte):
`483f97d10dc13318f77893dba6dd0415d138873e811806e6a73596b0ee229b4d`.
