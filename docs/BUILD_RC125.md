# RC125 — Căn giữa nghe giọng và tách kết quả theo tab

Căn giữa nhóm Nghe giọng Anh/Việt và Dừng nghe dưới slide kết quả.
Chiều rộng chỉ tính những nút hiện theo ngôn ngữ của bản giọng, nên
bản Anh, Việt và cả hai đều căn giữa. Nút tải ở trang kết quả và khung
giọng đã hoàn tất ghi rõ “Tải PowerPoint có giọng”. Giữ luồng xuất có
nhúng giọng hiện có.

Nút cam “Mở bài vừa tạo giọng” chỉ hiện tại tab Tạo giọng đọc khi có
kết quả giọng. Tab Chuyển đổi giữ nút kết quả chuyển đổi riêng, không
hiện nút kết quả giọng. Hai kết quả được giữ riêng khi chuyển qua lại
hai tab. Bản này gồm cả bố cục và mô tả cấu hình tạo giọng của RC124.

Kiểm bằng `.venv`: 6 pytest cấu hình/kết quả giọng gần nhất đạt.
Qt thật dùng thư viện tạm, slide và WAV fixture, không tạo giọng qua
dịch vụ. Kiểm căn giữa cả ba tổ hợp nút nghe ở 1080/1366/1920, giao
diện sáng/tối và tỷ lệ hiển thị 100%/150%. Kiểm chưa có kết quả,
chỉ có kết quả giọng và có hai kết quả khác bài; mỗi tab mở lại đúng
bài tương ứng, giữ đúng biến thể giọng. Không có cảnh báo QML.

Chân trang đặt khung Cấu hình đã chọn và nút tạo trong cùng một hàng;
nút cam ở hàng riêng dưới khung. Khi nút cam xuất hiện, nút Tạo giọng
đọc/Chuyển đổi bài giảng vẫn căn giữa theo chiều cao của khung cấu hình.
Qt kiểm cả hai tab khi có hoặc chưa có nút cam, ở ba kích thước và hai tỷ lệ.

Nguồn `1.0.0rc125`, commit
`15284499ec35ea57a71c8c3e7a5c0e47dff99793`. Dựng một lần sau kiểm,
dùng runtime RC124 có manifest SHA256. Gói
`dist/rc125-narration-actions/BiliClass-RC125-Windows.zip`, 1.255.959.841
byte, SHA256
`e31e03eaeb968a3999e6ae423f56576c1ddba1be97b4e646057f6b2f53a26f5a`.
Đối chiếu 4.667 file và 54 QML/qmldir khớp nguồn. Smoke bản đóng gói
tab Tạo giọng 1366×850 đạt, không cảnh báo QML.

Cài tại `F:/Applications/BiliClass/1.0.0rc125`, mở từ Explorer vào tab
Tạo giọng. Cửa sổ chính và Mascot phản hồi bình thường, kiểm tra icon,
taskbar và shortcut đạt. Sau cài/mở giữ nguyên 9 bài và tệp nguồn,
1.183 WAV, logo, API key mã hóa và cấu hình giọng. Đóng RC123 bình
thường; giữ phiên RC80 độc lập và PowerPoint đang mở. Không cài RC124.
