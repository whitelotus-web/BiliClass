# RC135 — Tiến độ chuyển đổi trong màn cấu hình

Bấm Chuyển đổi bài giảng giữ nguyên màn cấu hình và các thông tin
đã nhập. Thanh tiến độ, phần trăm, thời gian xử lý và thông báo từng
bước nằm ngay dưới các lựa chọn, cùng kiểu màn tạo giọng. Chỉ nhóm
cấu hình bị khóa khi chạy; nút `■ Dừng` nằm ở thanh dưới như tạo giọng,
hiện `Đang dừng…` và khóa trong khi chờ bước hiện tại kết thúc.
Dừng giữ phần đã xử lý và yêu cầu đã chuẩn bị để tiếp tục, kể cả khi
vừa bấm chuyển đổi mà thư mục công việc chưa trả về giao diện.
Từ mục khác, bấm trạng thái tác vụ quay về phần tiến độ
trong màn này. Lỗi/tiếp tục cũng dùng cùng khung; không đổi phần dịch,
lưu kết quả, giọng đọc hay màn hoàn tất để chọn bước tiếp theo.

Luồng nhận tệp thủ công cũ giữ màn hướng dẫn riêng. Cài đặt vẫn giữ
các tab hiện tại. Bản này bao gồm hai icon loa nhỏ VI/EN từ RC134.

Xác minh bằng `.venv`: 65 pytest về đầu vào/chuyển đổi/tiến độ đạt.
Qt với PowerPoint thật và API giả lập đạt: giữ nguyên cấu hình lúc
bấm chuyển đổi, tiến độ trong khung, quay về tác vụ, Dừng/Tiếp tục
không gọi lại phần đã dịch, dừng ngay trong bước chuẩn bị vẫn giữ
yêu cầu, hoàn tất và tải đúng bài. Đã xem nền sáng/tối ở
1080/1366/1920; Qt smoke bố cục ở 700/768/850/1080 px cũng đạt,
không cảnh báo QML. Kiểm tra dùng dữ liệu thử, không gửi bài cá nhân.
