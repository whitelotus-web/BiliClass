# RC134 — Thu gọn icon trạng thái giọng

Theo yêu cầu thu nhỏ sau RC133, icon loa VI/EN trong thư viện còn
24 × 22 px, loa gạch chéo xám 18 × 18 px. Nhãn cao 28 px, hai icon
cách nhau 4 px; giữ vùng bấm ngang và tooltip đầy đủ. Tiếp tục dùng
đúng hai ảnh đã gửi, EN xanh dương và VI tím trên cả nền sáng/tối.

RC133 đã đóng gói nhưng chưa cài. RC134 cũng chưa cài vì yêu cầu
tiếp theo về tiến độ chuyển đổi được gộp vào bản RC135 để mở thử.

Xác minh bằng `.venv`: 14 pytest thư viện/giao diện đạt. Qt smoke
thư viện đạt ở 1080/1366/1920, dạng thẻ/danh sách, không cảnh báo
QML. Đã xem icon nhỏ trên nền sáng/tối, gồm VI, EN và cả hai.

Đóng gói một lần từ `4f6d855cac0377b234640156d72dbfabef4aa6b2`:
`BiliClass-RC134-Windows.zip`, 1.258.028.746 byte, SHA-256
`c11a3e70a2ab6ca741b3aeae232eb245144cfdedb8948097d75003bc29bb4445`.
55 tệp QML và hai ảnh nguồn khớp commit; toàn bộ ZIP được xác minh.
Ứng dụng đóng gói mở thư viện thử nghiệm thành công, đã xem ảnh
hai loa nhỏ trên nền tối; không cảnh báo QML.
