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
đã lưu: 0 yêu cầu dịch mới, đủ 38 slide, nguồn giữ nguyên. Có ảnh
PowerPoint cho tất cả trang, gồm 11 ảnh dựng mới và 27 ảnh đã kiểm
chứng có XML trang không đổi; kết quả 0 FAIL / 38 CHECK. Đã xem
riêng trang bìa, mục lục và slide 33 có nhãn câu/lời giải; xác nhận
phần lời giải nằm trong nền sau sửa. Ngữ pháp và các từ viết tắt
trong lời giải vẫn cần rà soát, chẳng hạn dịch “mặt” thành “surface”
khi nguồn dùng để chỉ mặt phẳng; chưa coi đây là bản dịch đã duyệt.

Chưa có đồng bộ hai chiều khi sửa/lưu PowerPoint bên ngoài. Cảnh
báo về công thức, nội dung trong ảnh, hiệu ứng hoặc nghĩa chuyên
môn vẫn cần đối chiếu; không coi phép đo không còn FAIL là đã
chứng nhận toàn bộ bài. Chưa thêm hàng đợi hay xử lý nhiều bài.

Gói Windows 1.0.0rc139 dựng từ nguồn
`95eb7cde02e9d4f4b66a3a855b90fcf3f586cf5e`, dùng runtime RC138 đã
đối chiếu. 4.676 tệp ứng dụng và 56 tệp QML khớp nguồn; bytecode
các module thay đổi, nội dung từng tệp trong ZIP và SHA-256 đạt.
`BiliClass-RC139-Windows.zip`: 1.258.057.362 byte; SHA-256
`87b057aba03c7b0dcae219ae37e1af6ef8b39af5082a68fc9f9dddec3d1a2c09`.

Thử EXE ở dữ liệu cô lập, bỏ PYTHONPATH/PYTHONHOME và đường dẫn
model phát triển: mở đúng Home, lưu ảnh 1366 × 850, không cảnh báo
QML. Đỉnh cây tiến trình 486,1 MB RSS / 789,1 MB private ở mẫu
khởi động này trên i7-8700/RAM 32 GB; không phải phép đo tạo giọng,
PowerPoint hoặc chứng nhận máy cấu hình yếu.

Đã cập nhật cùng ID bài Toán 38 slide vừa khôi phục lên revision 2
với bố cục đã kiểm tra. Giữ nguyên tệp nguồn bản trước và lịch sử,
toàn bộ bài khác và 2.986 tệp WAV; bài này chưa có giọng. Bài 18
slide đã đủ 180/180 giọng của RC138 không bị thay bố cục/lời đọc.

Đã cài tại `F:/Applications/BiliClass/1.0.0rc139` và mở từ Explorer
vào Home, độc lập Codex. Cửa sổ hiện, không thu nhỏ, phản hồi tốt;
Mascot nổi ẩn ở khởi động. Shortcut Desktop/Start menu và nhóm
taskbar cùng định danh ứng dụng, icon trỏ đúng EXE mới. Đối chiếu
trước/sau cài giữ hồ sơ, logo, hash API key, tùy chọn giọng, tất cả
bài và 1.533 WAV đang được bản ghi bài tham chiếu.

Đã phát hành [v1.0.0rc139](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc139).
Digest và số byte asset GitHub khớp ZIP cục bộ; tag trỏ đúng commit
dựng gói. Kiểm đường cập nhật công khai từ RC118 chọn đúng RC139
với cùng digest/kích thước. Lượt gọi ngay sau công bố còn đọc danh
sách cũ; kiểm lại sau khi GitHub cập nhật đã đạt, không đổi logic
updater để lách dữ liệu phát hành chưa lan truyền.
