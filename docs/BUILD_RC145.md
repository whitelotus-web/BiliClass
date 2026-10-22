# RC145 — Nghe/dừng cùng nút, xóa và hoàn tác

Mỗi ngôn ngữ dùng một nút nghe/dừng với biểu tượng stop khi phát.
Cùng thành phần ở kết quả tạo giọng và xem trước trong cấu hình;
không còn nút dừng riêng. Chiều rộng giữ nguyên, chữ Việt không bị
cắt. Chỉ trạng thái của đúng bài, slide, bản giọng và phiên phát mới
đổi nút. Đổi ngôn ngữ dừng giọng trước; hết lời, lỗi, dừng ngoài hoặc
đổi slide cập nhật lại nút. Nghe đúng WAV đã lưu, không tổng hợp mới.

Thư viện có **Hoàn tác xóa** ngay bên phải **Chia sẻ & quản lý** sau
lần xóa thành công. Khôi phục những bài còn trong thùng rác của lần
xóa gần nhất, kể cả cả nhóm. Không hết hạn bằng đồng hồ; trạng thái
nhanh thuộc cửa sổ hiện tại, Thùng rác vẫn dùng được sau khởi động lại.
Xóa lỗi hoặc hủy xác nhận giữ lượt trước; hoàn tác lỗi vẫn thử lại được.
Biên nhận giữ ID/thời điểm xóa, kiểm lại trong khóa ghi SQLite để
không nhầm với một lần xóa mới ở cửa sổ khác. Tất cả ghi chạy nền.

Trang xem bài có icon thùng rác bên phải **Tạo giọng đọc**, dùng
chung hộp xác nhận và xử lý xóa của Thư viện. Sau khi xóa thành công,
về Thư viện và hiện hoàn tác. Không xóa PowerPoint/WAV hay lịch sử.
Các chặn tác vụ/trình chiếu/lớp học đang chạy được giữ nguyên.

65 pytest liên quan trong `.venv` đạt, gồm biên nhận, xóa lại cùng
ID, lô không còn hợp lệ và khóa trước khi kiểm tra. Qt kết quả giọng
kiểm tra chuột/bàn phím, Anh/Việt, chuyển ngôn ngữ, hết lời/lỗi,
đổi slide và hoạt động đọc khác; sáng/tối, ba cỡ cửa sổ. Qt xóa/hoàn
tác kiểm tra xóa một/nhóm, hủy/lỗi, khôi phục lỗi rồi thử lại, thao
tác bận, vị trí nút và điều hướng từ trang xem; giữ nguyên metadata,
nguồn/WAV trên fixture. Qt độ phản hồi vẫn qua khi SQLite bị khóa;
không cảnh báo QML. Ruff toàn kho và compileall được kiểm trước commit.

Smoke RC71 cũ dừng tại nhãn “Việt + Anh” đã đổi từ trước thành
“Cả Anh và Việt”; không dùng lần chạy đó làm bằng chứng đạt.
Luồng kết quả/cấu hình hiện tại được kiểm bằng smoke kết quả giọng.
Không thay dữ liệu cá nhân, mô hình, bốn tab Cài đặt hoặc thêm hàng đợi.
