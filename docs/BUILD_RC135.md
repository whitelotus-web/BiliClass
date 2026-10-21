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

Đóng gói một lần từ `91fe80af45af1693c2cffff7889786e567c2bd2d`:
`BiliClass-RC135-Windows.zip`, 1.258.029.675 byte, SHA-256
`bd5990f96590a4c1a97789cc2a060f38063f40b162f1b804e806edfabe851677`.
55 tệp QML và hai PNG khớp nguồn; bytecode `app.ui` và
`app.conversion_presentation` trong EXE khớp nguồn của commit.
Toàn bộ ZIP được xác minh, 4.675 tệp ứng dụng. Smoke bản đóng gói
ở màn thư viện và chuyển đổi đạt; đã xem hai ảnh, không cảnh báo QML.

Cài tại `F:/Applications/BiliClass/1.0.0rc135`, mở màn Chuyển đổi
qua Explorer độc lập với Codex. Cửa sổ chính và cửa sổ Mascot phản
hồi; biểu tượng native/taskbar và shortcut Desktop/Start đúng RC135.
Đối chiếu trước/sau cài đặt xác nhận nội dung bài, nguồn PowerPoint,
WAV, hồ sơ/logo, khóa API mã hóa và tùy chọn giọng được giữ nguyên.

Đã phát hành [v1.0.0rc135](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc135)
với ZIP và checksum riêng. Digest/size GitHub khớp bản đã kiểm tra;
tag trỏ đúng commit nguồn của gói. Kiểm tra updater công khai từ
RC118 nhận đúng RC135 với cùng SHA-256 và kích thước.
