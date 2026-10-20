# RC105 — Loading gọn và mượt hơn

Bỏ dãy ba vòng tròn/đường nối cuối màn hình; chỉ giữ trạng thái đang làm
và thanh loading mảnh, cân lại khoảng cách với logo. Thanh chạy bằng
XAnimator của Qt trên luồng kết xuất, chu kỳ 1,15 giây thay 1,55 giây.
Khi cửa sổ chính vẽ xong, loading mờ ra trong 110 ms rồi đóng; khoảng
đóng giảm từ 180 xuống 120 ms. Không thêm thời gian chờ để trình diễn.

Tôn trọng lựa chọn tắt chuyển động của Windows: dùng thanh tĩnh và đóng
ngay khi sẵn sàng. Ảnh gốc, các bước nội bộ và việc tách tiến trình giữ
nguyên. Không sửa luồng thư viện, chuyển đổi, giọng đọc hay Mascot.

Phạm vi cải thiện là cách hiển thị và chuyển tiếp loading. Thời gian
chuẩn bị giao diện chính vẫn phụ thuộc máy/thư viện; không coi tốc độ
thanh chuyển động là phần trăm công việc hay số đo tốc độ khởi động.

Kiểm tra trước đóng gói: 5 kiểm thử vòng đời qua; Qt Windows dùng thư
viện tạm xác nhận ảnh/bước thật, chuyển động độc lập, ready/EOF đóng
tiến trình và cửa sổ chính tiếp quản. Ảnh thực tế đã kiểm tra bố cục.
Ruff và kiểm tra khoảng trắng qua. Không chạy lại các bộ chuyển đổi,
giọng đọc hay thư viện vì mã các luồng đó không đổi.
