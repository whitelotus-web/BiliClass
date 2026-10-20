# RC115 — Dàn chữ trong dải nền và chữ Mascot dễ đọc

Luồng chuyển đổi song ngữ nhận diện vùng đặt chữ từ phần nền thực sự
được vẽ: khung chữ nhật/bo góc có màu và hình nền dùng PNG trong suốt.
Vùng trong suốt và bóng đổ không còn được tính là chỗ đặt chữ. Hai cột
Việt–Anh cùng giới hạn trên/dưới, dùng chung lề và khoảng cách; thân bài
căn trên. Bước hoàn thiện chừa chỗ cho hình minh họa bên phải, không
dời hình. Cơ chế tách trang tiếp nối theo cặp đoạn đầy đủ vẫn được giữ.

Thêm lỗi kỹ thuật `panel_text_escape` để bắt hộp chữ vượt dải nền ngay
cả khi PowerPoint đo chữ vừa chính hộp chữ đó. Bước căn lại dùng chung
cho bài mới và bản cũ: kéo khung chữ BiliClass về đúng dải, đo/căn bằng
PowerPoint trên bản sao. Không cho bước nới hộp chữ mở rộng khỏi dải.
Giữ văn bản, media, cấu trúc cặp lời và vị trí của mục tiêu motion/trigger.
Bản cũ có sơ đồ cặp được rà thêm khi mở/tải dù phép kiểm tra trước đây
chưa báo FAIL; lượt sửa ghi nhận phiên bản và hash nguồn để không lặp
vô hạn. Giữ kiểm tra đồng thời và lịch sử nguồn/giọng sẵn có.

Đây là sửa quy tắc chung, không phải vá tọa độ một bài. Kiểm tra trên
các khối nền tạo bằng code và ảnh có bóng trong suốt; thử lại ví dụ bốn
mục tiêu của Bài 6 bằng luồng chuyển đổi với bản dịch đã lưu, không gửi
lại yêu cầu dịch. Kết quả render giữ đủ hai ngôn ngữ trong bốn dải, không
còn lỗi tràn hộp/dải; chữ không bị nhân vật minh họa che. Không tuyên bố
mọi thiết kế/công thức nguồn đều đạt chuẩn; lỗi thật vẫn không được xóa.

Logo trường trong giao diện dùng mặt nạ tròn chỉ khi góc ngoài vòng tròn
trống hoặc trắng. Logo vuông/ngang có chi tiết ở góc giữ đầy đủ. Dùng
chung ở thanh bên, xem trước hồ sơ và cửa sổ bài giảng; không chỉnh,
ghi đè hay thay đổi màu ảnh logo gốc hoặc file bài trình chiếu.

Chữ nút Mascot ở 60 px tăng lên 12 px, icon 16 px, nhãn ngắn “Đang chiếu”
và “Chiếu · F5”, có giải thích đầy đủ khi rê chuột. Chữ và icon vô hiệu
hóa rõ hơn trên nền tối; câu trạng thái tự xuống dòng theo chiều cao.
Các cỡ lớn giữ tỉ lệ và nhãn phù hợp, không bị cắt chữ.

Kiểm tra: 141 ca chuyển đổi, bố cục, nguồn, căn chữ, phân trang, phục hồi,
logo và giao diện đạt; Ruff đạt. Qt smoke với font thật của ứng dụng,
DPI 100%/150%, cỡ Mascot 60/65/66/80/94/95/110/129/130/150/160 px đạt,
không cảnh báo QML. Kiểm tra chữ “Đang chiếu” không bị cắt, các lựa chọn
vẫn cân giữa, mask logo không làm đổi byte ảnh gốc. Đã xem render ví dụ
chuyển đổi, giao diện với logo thật và bảng Mascot nhỏ.

Gói từ commit `8a43de22e984bd523ed5a0098c8ea3a0cb20cf66`, ZIP
1.249.974.070 byte, SHA-256
`3c545410f2ea1d51595bc4a62305e0b9be4a98b1a8cc757690b37cef1ccd4672`.
Manifest và ZIP đã xác minh; 51 QML/qmldir khớp nguồn đã kiểm tra.
Bản đóng gói chạy smoke giao diện tối với logo thật trong thư viện tạm,
thoát mã 0. GitHub xác nhận digest và phát hành `v1.0.0rc115`.

Đã cài, mở RC115 độc lập qua Explorer tại Cài đặt. Cửa sổ chính và
Mascot đạt ba thăm dò phản hồi liên tiếp sau một lần timeout khởi động
500 ms; shortcut, biểu tượng và danh tính taskbar đúng. Hash nguồn và
revision của 18 bản ghi bài (gồm thùng rác), 1.658 WAV được tham chiếu,
cấu hình giọng, khóa dịch mã hóa và ảnh logo gốc khớp trước/sau cài.
PowerPoint độc lập và RC80 được giữ nguyên.
