# RC87 — Nhãn lớp trên Trang chủ và thanh trạng thái

Trang chủ dùng “Lớp” thay cho “Khối” ở Bài gần đây và thẻ bài đang chọn.
Không đổi số lớp hoặc dữ liệu bài giảng.

Khi một job kết thúc mà callback không đặt thông báo mới, xóa thông báo
mặc định “Đang xử lý tại máy…”. Không xóa thông báo khi job kế tiếp đã
khởi chạy, thông báo thành công cụ thể hoặc lỗi. Thanh dưới ẩn khi không
có thông báo; tác vụ đang chạy vẫn có chỉ báo và nút Dừng tác vụ.

25 test liên quan đạt. Qt kiểm tra Trang chủ ở ba kích thước, job đang
chạy/hoàn tất và lỗi; kiểm tra footer chuyển đổi ở bốn kích thước. Thử
tệp vượt giới hạn chờ đúng kết quả kiểm tra file bất đồng bộ đã có từ RC84.
