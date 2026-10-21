# RC126 — Thu gọn ô chọn ngôn ngữ tạo giọng

Ba ô ngôn ngữ tự lấy chiều cao theo tiêu đề và mô tả, tối thiểu 78 px,
thay chiều cao cố định 112 px. Các ô vẫn cùng chiều cao, không cắt mô
tả khi xuống dòng. Nhóm vị trí loa tiếp tục căn giữa nửa bên phải.
Ở màn rộng phần trống giảm 34 px; màn 1366 có mô tả hai dòng giảm
25 px. Giữ khoảng đệm quanh nội dung và bố cục hai hàng ở màn hẹp.
Các ô chuyển đổi bài giảng giữ kích thước hiện có.

Kiểm bằng `.venv`: 15 pytest cấu hình/lời đọc đạt. Qt thật kiểm giao
diện sáng/tối, 1080/1366/1920, có/chưa chọn bài, tỷ lệ 100%/150%.
Kiểm đủ mô tả, chiều cao các ô bằng nhau, hai nhóm căn giữa và không
giữ khoảng trống lớn dưới mô tả. Đổi ngôn ngữ/sáu vị trí loa vẫn cập
nhật tức thì, không tải lại slide. Không cảnh báo QML. Dữ liệu và ảnh
thử dùng thư viện tạm, giữ ngoài Git.

Nguồn `1.0.0rc126`, commit
`5f9944554bd025af2083f9d4220bbaaa1caed657`. Dựng một lần sau kiểm,
dùng runtime RC125 có manifest SHA256. Gói
`dist/rc126-compact-language/BiliClass-RC126-Windows.zip`, 1.255.959.863
byte, SHA256
`b1f17b1533eea1139f49073adc0770eeea2715955cfe63b5ff01e44327830996`.
Đối chiếu 4.667 file và 54 QML/qmldir khớp nguồn. Smoke bản đóng gói
tab Tạo giọng 1366×850 đạt, không cảnh báo QML.

Cài tại `F:/Applications/BiliClass/1.0.0rc126`, mở từ Explorer vào tab
Tạo giọng. Cửa sổ chính/Mascot phản hồi bình thường; icon, taskbar và
shortcut đúng phiên bản. Đối chiếu sau mở giữ nguyên 9 bài và nguồn,
1.183 WAV, logo, API key mã hóa và cấu hình giọng. Đóng RC125 bình
thường; giữ phiên RC80 độc lập và PowerPoint đang mở.
