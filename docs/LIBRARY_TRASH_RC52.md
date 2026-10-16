# Thư viện gọn và thùng rác — RC52

Ô tích 16 px nằm trong vùng bấm cao 32 px. Bốn bộ lọc và Chọn tất cả / Bỏ
chọn / Tải đã chọn / Xóa đã chọn cùng hàng, kể cả cửa sổ 1080×700. Bộ lọc
có nhãn ngắn, tooltip và menu đủ rộng để đọc tên đầy đủ; nút ↺ xóa bộ lọc.
Giữ tìm kiếm, sắp xếp và phạm vi chọn qua nhiều trang của RC51.

Thùng rác có ô chọn từng bài, chọn tất cả/bỏ chọn, khôi phục hoặc xóa nhóm,
khôi phục tất cả/xóa tất cả, và nút riêng từng bài. Hộp xác nhận xóa vĩnh
viễn chụp đúng danh sách và ghi số bài. Không tự xóa thư viện thật khi thử.

Backend giữ khóa ghi SQLite từ khi kiểm tra danh sách đến khi ghi; lỗi ở
một bài hủy cả nhóm. Chỉ bài còn trong thùng rác được khôi phục/xóa vĩnh
viễn. Xóa bài kéo theo lịch sử chỉnh sửa; báo cáo lớp, bản sao lưu và tệp
nguồn/WAV dùng chung không bị xóa. Đây không phải chức năng xóa an toàn ổ
đĩa hay thu gom cache. Tiết chưa kết thúc hoặc tác vụ đang chạy chặn thao tác.

Kiểm chứng: 42 kiểm thử liên quan qua. Qt trên thư viện 24 bài kiểm tra
chọn qua nhiều trang, bộ lọc, vị trí và giới hạn hàng công cụ ở 1080×700 /
1366×850, hủy xóa, khôi phục nhóm, xóa vĩnh viễn và khôi phục tất cả; không
có QML warning. Các bài/âm thanh thật không dùng làm dữ liệu kiểm thử.
[Thông tin executable/bộ cài RC52](BUILD_RC52.md). Nguồn và binary là hai
phần riêng, không thay nội dung bản phát hành RC51 đã công bố.
