# RC139 — Giữ đúng hàng nội dung trong khung nền lớn

Bao gồm các sửa lỗi và chẩn đoán slide của RC138. Khi một khung
nền lớn chứa cả tiêu đề và thân bài, tự căn khung giữ mép trên của
hàng nội dung gốc. Khoảng trống phía trên thuộc phần tiêu đề,
không được dùng để kéo cột Việt–Anh lên. Áp dụng cùng nguyên tắc
ở bước dựng bài và bước sửa/kiểm tra sau đó.

Trường hợp thực tế: trang bìa bài Toán có khung nền xanh nhạt lớn,
tiêu đề chương ở phía trên, danh mục bài ở phía dưới. Trước sửa,
hai cột của danh mục bị kéo từ vị trí gốc lên đầu khung nền và
chạm vào tiêu đề. Không đổi nội dung, hình, công thức hay hiệu ứng
để che lỗi này.

Kiểu chữ cũng theo tỉ lệ kích thước trang. PowerPoint có canvas
1920 × 1080 pt không còn bị áp cùng trần cỡ chữ của trang
960 × 540 pt, làm chữ dịch nhỏ bằng một nửa tỉ lệ chiếu dự kiến.
Đo lại bằng PowerPoint và vòng sửa có giới hạn vẫn chạy sau đó.

Nhãn Câu/Question và Bài giải/Solution giữ khung riêng của chúng;
không lấy cả dải nền câu hỏi làm nơi mở rộng nhãn. Nhãn dùng cặp
xếp trên/dưới trong cùng khung, được đo lại trước khi lưu.
Thân câu hỏi có hộp bao nằm phía sau nhãn được chừa mép trái
trước khi chia hai ngôn ngữ; tránh đưa chữ Việt/Anh vào dưới nhãn.
Khung lời giải lấy màu nền từ nhóm cha cũng được nhận diện. Hai
cột phải nằm trong phần nền thực, thay vì chỉ vừa hộp chữ được
mở rộng đến mép slide. Không suy đoán màu từ theme hay ảnh nền.

Kiểm thử trong `.venv`: 77 pytest về khung nền, song ngữ cùng
slide, hoàn thiện bài cũ và sửa bố cục đạt. Qt chẩn đoán vị trí lỗi
trên cả chuyển đổi và giọng đọc đạt; không cảnh báo QML. RC138
trước đó đạt 402 pytest cùng các luồng Qt tạo/hủy/tiếp tục, vùng
bấm cấu hình và thư viện bản dở/sản phẩm. Gói dùng runtime đã xác
minh của RC138; không đưa dữ liệu cá nhân, model hoặc EXE vào Git.

Đã dựng lại bài Toán thực tế 38 slide trên bản sao bằng bản dịch
đã lưu: 0 yêu cầu dịch mới, đủ 38 slide, nguồn giữ nguyên. Dựng ảnh
bằng PowerPoint cho tất cả trang; kết quả 0 FAIL / 38 CHECK. Đã xem
riêng trang bìa, mục lục và slide 33 có nhãn câu/lời giải; xác nhận
phần lời giải nằm trong nền sau sửa. Ngữ pháp và các từ viết tắt
trong lời giải vẫn cần rà soát, chẳng hạn dịch “mặt” thành “surface”
khi nguồn dùng để chỉ mặt phẳng; chưa coi đây là bản dịch đã duyệt.

Chưa có đồng bộ hai chiều khi sửa/lưu PowerPoint bên ngoài. Cảnh
báo về công thức, nội dung trong ảnh, hiệu ứng hoặc nghĩa chuyên
môn vẫn cần đối chiếu; không coi phép đo không còn FAIL là đã
chứng nhận toàn bộ bài. Chưa thêm hàng đợi hay xử lý nhiều bài.
