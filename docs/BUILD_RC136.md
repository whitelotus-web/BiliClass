# RC136 — Thuật ngữ Hóa, lời đọc công thức và nhãn số Toán

Google Dịch giữ nguyên toàn bộ công thức Hóa, gồm chỉ số OOXML,
điện tích và dấu liên kết. Không gửi riêng chỉ số rồi để dịch máy
làm mất nguyên tố. Đối chiếu số lần xuất hiện của công thức trước
khi lưu bản dịch; công thức thêm/bớt không được áp dụng.
Ngữ cảnh Hóa giữ các tên quốc tế như Alcohol, Iron, Sulfuric acid;
các danh từ thông thường để dịch máy chia số và ghép câu, thay vì
ép `phân tử → molecule` vào mọi vị trí. Thuật ngữ do giáo viên khóa
vẫn được ưu tiên. Bổ sung nhóm chức, liên kết cộng hóa trị, công
thức phân tử/cấu tạo và các tên nguyên tố, chất thông dụng.

Lời Anh đọc rõ ký hiệu, chỉ số, điện tích và số oxi hóa trong tên
như Iron(III); cm⁻¹ đọc inverse centimeters. Tên chất tiếng Anh giữ
nguyên để giọng Anh phát âm. Ký hiệu chỉ nguyên tố được đọc tên khi
câu có ngữ cảnh rõ (element H, các nguyên tố C và H, react with Na).
Giữ đại từ I và biến của bài Toán/Lý; dấu = chỉ đọc double bond khi
có ngữ cảnh liên kết Hóa. Nhãn mục có khoảng trắng như `III .` được
đọc như nhãn mục bình thường. Chỉ các đoạn có cách đọc thay đổi mới
cần khóa cache WAV mới; không xóa âm thanh cũ.

Sửa lỗi thực tế của bài hình học có nhãn ❶ ❷ ❸: ký tự Unicode loại
số được giữ tại máy, kể cả nằm trong câu. Nhãn chỉ có số/ký hiệu
không cần API. Không nới kiểm tra số liệu. Nếu một đoạn khác vẫn
không hợp lệ, tự thử lại đúng một lần với số liệu ẩn khỏi dịch máy;
các đoạn đúng được giữ trong cache, mọi lượt gọi đều tính vào hạn
mức cục bộ, và Dừng vẫn ngăn gửi lượt tiếp theo.

Ô trạng thái giọng trong thư viện có cùng nền 64 × 28 px ở mọi
trạng thái; icon nhỏ, căn giữa, giữ màu và phân biệt VI/EN.

Phạm vi kiểm chứng: chạy lại bản sao 44 slide Hóa với Google thật,
đối chiếu thuật ngữ/công thức và render các slide trọng điểm bằng
PowerPoint. Kiểm tra toàn bộ 130 WAV cũ (48 kHz mono PCM16, không
clipping), tạo chín mẫu bằng Heart ngoại tuyến để kiểm tra đầu vào
đọc và dạng sóng. Đây không phải đánh giá phát âm bởi người nghe.
Chữ/công thức nằm trong ảnh vẫn cần đối chiếu; không coi các cờ
CHECK của bài gốc là đã được xác minh chuyên môn hoàn toàn.

Đối chiếu danh pháp với [IUPAC Alcohols](https://goldbook.iupac.org/terms/view/A00204/PDF),
[bảng nguyên tố](https://iupac.org/what-we-do/periodic-table-of-elements/)
và [IUPAC nomenclature](https://iupac.org/what-we-do/nomenclature/).
Không suy tên chất từ công thức phân tử và không thay nội dung gốc
của thầy cô. Bản dịch/voice cũ cần chuyển đổi/tạo giọng lại để nhận
nội dung sửa; cập nhật ứng dụng không tự viết lại thư viện.

448 pytest trong `.venv` đạt, gồm dịch/cache/hạn mức, bảo toàn slide,
lập giọng, người đọc tiếng Anh và giọng cũ. Qt chuyển đổi và Qt tạo
giọng đạt; Qt kiểm tra năm trạng thái icon ở 1080/1366 px, nền sáng
và tối đạt, không cảnh báo QML. Đúng tệp Toán hình học đang lỗi
được chạy lại trên bản sao với môn Toán: đủ 18 slide, giữ các nhãn
❶ ❷ ❸, không còn lỗi thay số; không có cờ FAIL tự động. Các cờ
CHECK của nguồn phức tạp vẫn được giữ để đối chiếu.

Theo yêu cầu chuẩn bị nộp ngày 25, chưa thêm hàng đợi hoặc chạy
nhiều bài. Bộ thuật ngữ là dữ liệu ngắn có chủ đích, không phải
huấn luyện lại mô hình hay bảo đảm dịch đúng mọi bài Toán/Lý/Hóa.
