# RC161 — cửa sổ ban đầu nằm trong vùng làm việc Windows

Cửa sổ trước đây luôn nhận kích thước 1366×850 và giới hạn tối thiểu
1080×700, không xét vùng taskbar hoặc số pixel logic còn lại khi Windows
để 125–150%. Laptop thấp hơn có thể bị che taskbar ở trạng thái thường;
phóng to lại vừa vì Windows dùng vùng làm việc khi maximize.

Khi mở, tính kích thước và vị trí theo `QScreen.availableGeometry()`
(pixel logic), có trừ viền native và chừa khoảng trống xung quanh.
Giới hạn tối thiểu cũng được hạ khi màn hình nhỏ. Lấy kích thước viền
lại sau khi cửa sổ hiện; không dùng độ phân giải vật lý làm pixel QML.

Khi đổi màn hình, DPI hoặc vùng taskbar, căn cửa sổ thường lại nếu cần.
Giữ vị trí hợp lệ người dùng đã chọn. Không ép thu nhỏ cửa sổ đang phóng
to, thu vào taskbar hoặc toàn màn hình. Thu về trạng thái thường không
lấy kích thước phóng to làm kích thước khôi phục, không nhỏ dần sau mỗi lượt.

Kiểm tra hình học với 40 tổ hợp màn hình/tỷ lệ/vị trí, gồm màn hình có
tọa độ âm và taskbar ở cạnh khác. Kiểm tra Qt thật tại 100%, 125%, 150%,
200%: mở mới và 3 lượt phóng to/thu về; đối chiếu cả viền Qt và tọa độ
native Windows với vùng làm việc. Giả lập vùng laptop 1366×768 trong
tiến trình kiểm thử, không thay đổi độ phân giải hoặc DPI của máy.
Kiểm tra nút Lưu giọng vẫn tới được bằng cuộn trong cửa sổ thấp.

Luồng desktop thật `python -m app --smoke` tại 150% cũng mở Cài đặt
đúng kích thước đã giới hạn, không cảnh báo QML. Báo cáo và ảnh riêng
ở `reports/rc161`, ngoài Git. Dữ liệu kiểm thử riêng; không sửa thư viện
cá nhân, các tab Cài đặt hay cấu hình màn hình. Chưa tạo bộ cài.

48 kiểm thử hình học/khởi động/Windows identity đạt; bốn lượt Qt ở bốn
tỷ lệ, mỗi lượt kiểm tra 5 trạng thái hình học và nút Lưu giọng. Ruff,
compileall và diff-check đạt. CI thêm hai nhóm hình học/khởi động này.
