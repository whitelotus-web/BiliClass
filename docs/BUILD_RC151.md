# RC151 — Tab Thư viện có cạnh phải vát nhẹ

Giữ các thay đổi đã kiểm chứng ở [RC150](BUILD_RC150.md): chọn nhiều
bài đúng công cụ, checkbox chọn bài, ẩn lượt đã hoàn tất. Ba tab
Thư viện có cạnh phải vát nhẹ, phần chữ/icon vẫn ngay ngắn và đủ lề.
Chiều cao tab giảm từ 46 xuống 40 px; giữ cỡ chữ/icon, số bài, bộ lọc và phím bấm; hỗ trợ giao diện sáng/tối.
Gom Mở bài từ máy vào menu ba chấm dọc ở góc phải; giữ nhận gói bài
và thùng rác trong menu. Nút Tạo giọng đã chọn hiện sát phải trên
hàng tab khi có bài được tích chọn; Hoàn tác xóa vẫn truy cập ngay ở bên trái menu góc phải.
Tải/Xóa đã chọn dùng icon tải xuống/thùng rác chung với từng bài;
chú thích và tên cho trình đọc màn hình ghi rõ số bài đang chọn.
Không có bài chọn thì khóa hai nút, giữ số bài chọn hiển thị cạnh đó.

RC150 được giữ làm gói thử nội bộ, không cài/phát hành để tránh đưa
ra hai bản khi người dùng đang chỉnh giao diện. RC151 chứa toàn bộ
thay đổi; chỉ gói này được chuyển sang bước cài và phát hành.

Kiểm tra bổ sung: Ruff/compileall và ba Qt smoke chọn bài/định tuyến/
tab thư viện, xóa/hoàn tác và hàng đợi đạt, không cảnh báo QML.
Menu mở file được bấm trực tiếp trong cửa sổ Qt; nút Tạo giọng nằm
sát phải hàng tab. Đã kiểm nút tải/xóa dạng icon, xóa/hoàn tác nhiều
bài, bàn phím và tài sản gốc được giữ nguyên trên thư viện thử. Đã xem ảnh sáng/tối của cả ba
tab, cạnh vát không chạm chữ/icon. Các kiểm chứng RC150 (516 pytest,
năm Qt smoke, gói nội bộ đúng 60 QML/qmldir và bytecode) giữ nguyên;
không thay bộ xử lý bài/giọng trong lần chỉnh cạnh tab này.

[Trạng thái phát hành RC151: đang kiểm tra.]
