# RC131 — Thu gọn khoảng cách cấu hình giọng đọc

Bỏ lề trên bổ sung 16/48 px của khung Cấu hình tạo giọng đọc khi chưa
chọn bài. Khung dùng khoảng cách chung 18 px ngay dưới hàng chọn bài
trong thư viện, giống các phần còn lại. Giữ chiều cao, nội dung khung
và hành vi sau khi đã chọn bài.

Xác minh bằng `.venv`: 8 pytest giao diện đạt; Qt smoke Chuyển đổi/
Tạo giọng ở 1080×700, 1366×768, 1366×850 và 1920×1080 đạt, không
cảnh báo QML. Đã xem ảnh bố cục Tạo giọng với khoảng cách mới.

Nguồn `1.0.0rc131`, commit
`73cd4ac805389ecac78682046a905f39bb2e32ed`. Dựng một lần từ runtime
RC130 đã xác minh. Gói `dist/rc131-voice-spacing/BiliClass-RC131-Windows.zip`,
1.257.787.813 byte, SHA256
`5d84d3ece89516475c3ce4e3b313356eb9ede8c1dc1f3a0d834ffe92d25072b4`.
Đối chiếu 4.670 file và 55 QML/qmldir khớp nguồn. Smoke bản đóng gói
tab Tạo giọng 1366×850 thoát 0, không cảnh báo; đã xem ảnh nền tối.

Cài tại `F:/Applications/BiliClass/1.0.0rc131`, mở từ Explorer vào tab
Tạo giọng. Cửa sổ chính/Mascot phản hồi, icon/shortcut đúng phiên bản.
Đối chiếu sau cài/mở giữ nguyên bài/tệp nguồn, 1.183 WAV, hồ sơ,
logo, API key mã hóa và cấu hình giọng. RC130 đóng bình thường.
