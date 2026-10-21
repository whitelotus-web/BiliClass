# RC121 — Tab Mascot giãn theo cửa sổ

Bỏ giới hạn 1180 px và căn giữa riêng của nội dung tab Mascot. Nội dung
giờ chiếm toàn bộ chiều rộng vùng Cài đặt, giữ cùng lề với các tab khác.
Ba thẻ chọn/xem trước và các ô cấu hình giãn cùng nhau; bố cục màn hẹp
và lựa chọn đã lưu giữ nguyên.

Kiểm bằng `.venv`: 11 pytest về giao diện/cài đặt đồng hành đạt.
Qt thật kiểm sáng/tối tại 1080/1366/1920, phóng to cửa sổ rồi thu về
1080, cả cỡ hiển thị 100% và 150%. Nội dung không còn dải trống do
giới hạn chiều rộng, không tràn ngang; nút và cuộn vẫn dùng được,
không có cảnh báo QML.

Nguồn `1.0.0rc121`; dựng một lần từ commit đã kiểm, dùng runtime/model
RC120 với manifest SHA256. Commit được ghi trong BUILD_INFO.json.
Gói, dữ liệu cá nhân và báo cáo thử không đưa vào Git.

Gói đã dựng từ `4ef9bf8f8f435f9fd03b0311efac2fc4b8925433`, ZIP có
1.249.991.770 byte, SHA256
`ffce00ebb54c57ed94d8a27774d3d277beb1eaad2bb4f7588d81b7d515d35413`.
4662 tệp ứng dụng và 54 QML/qmldir đã đối chiếu manifest/commit.
EXE thực chạy smoke Cài đặt 1920×1080, không có cảnh báo QML.
Cài vào `F:/Applications/BiliClass/1.0.0rc121`, mở qua Explorer ở trang
Cài đặt; cửa sổ chính/Mascot phản hồi, shortcut/taskbar/icon đúng bản.
RC120 đóng bình thường; phiên khác và PowerPoint được giữ nguyên.
Đối chiếu trước/sau xác nhận bài/nguồn, 1066 WAV được tham chiếu, logo,
khóa mã hóa và tùy chọn giọng giữ nguyên. Gói dùng để test tại máy,
chưa phát hành GitHub Release.
