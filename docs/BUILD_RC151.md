# RC151 — Tab Thư viện có cạnh phải vát nhẹ

Giữ các thay đổi đã kiểm chứng ở [RC150](BUILD_RC150.md): chọn nhiều
bài đúng công cụ, checkbox chọn bài, ẩn lượt đã hoàn tất. Ba tab
Thư viện có cạnh phải vát nhẹ, phần chữ/icon vẫn ngay ngắn và đủ lề.
Giữ chiều cao, số bài, bộ lọc và phím bấm; hỗ trợ giao diện sáng/tối.

RC150 được giữ làm gói thử nội bộ, không cài/phát hành để tránh đưa
ra hai bản khi người dùng đang chỉnh giao diện. RC151 chứa toàn bộ
thay đổi; chỉ gói này được chuyển sang bước cài và phát hành.

Kiểm tra bổ sung: Ruff/compileall và Qt smoke chọn bài/định tuyến/
tab thư viện đạt, không cảnh báo QML. Đã xem ảnh sáng/tối của cả ba
tab, cạnh vát không chạm chữ/icon. Các kiểm chứng RC150 (516 pytest,
năm Qt smoke, gói nội bộ đúng 60 QML/qmldir và bytecode) giữ nguyên;
không thay bộ xử lý bài/giọng trong lần chỉnh cạnh tab này.

[Trạng thái phát hành RC151: đang kiểm tra.]
