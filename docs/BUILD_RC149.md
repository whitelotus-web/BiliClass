# RC149 — Giữ đúng bài đang chọn trong Mascot

Đã tái hiện một lỗi cụ thể: chọn bài A trong Mascot, thư viện được làm
mới và đổi thứ tự (ví dụ đổi tên A thành Z khi đang sắp tên tăng dần),
sau đó bấm Mở bài đã chọn có thể mở bài B ở vị trí cũ. Đây là lỗi chọn
theo vị trí dòng, không phải bằng chứng mọi lỗi mở file đều có cùng nguyên nhân.

Mascot giữ ID bài đã chọn qua lần làm mới/sắp xếp; lúc bấm mở dùng
đúng ID đó. Nếu bài đã bị xóa/ẩn khỏi thư viện, hiện thông tin và khóa
nút mở, không tự thay bằng bài khác. Khôi phục bài giữ được lựa chọn.
Hộp chọn PowerPoint trong Mascot khai báo rõ chế độ mở một file, cùng
luồng mở/gắn bài với Thư viện. Không thay đổi nội dung, giọng, nguồn,
cache hay các tab Cài đặt.

Phép thử Qt trên dữ liệu riêng tái hiện mở sai ID trước sửa và đúng ID
sau sửa, kiểm xóa/khôi phục, bấm thật nút chọn file trong cửa sổ Qt của
phép thử và hủy hộp chọn Windows không khởi động tác vụ. Không có input
toàn hệ thống; không tự chọn file qua hộp thoại Windows.

Đã chạy phép thử PowerPoint thật trước sửa: các luồng thông thường mở,
đổi bài, F5, file có giọng nhúng và Mascot khi thu nhỏ cửa sổ chính đạt.
Vì người dùng chưa chỉ rõ thao tác/triệu chứng lỗi, chưa kết luận lỗi
đổi thứ tự là toàn bộ lỗi mà người dùng thấy.

Sau sửa: 46 pytest về phiên dạy, chuyển trạng thái, cache và thiết lập
thư viện đạt; Ruff/compileall đạt. Ba Qt smoke chọn bài, phiên dạy với
Office thật và menu Mascot đạt, không cảnh báo QML. Phép thử Office
giữ nguyên nguồn và WAV mẫu, kiểm mở/đổi bài trước/sau tạo giọng,
file ngoài có giọng nhúng, F5, tạm dừng/đọc tiếp và thu nhỏ app. Chưa
chứng nhận máy chiếu, nhiều màn hình hoặc mọi file PowerPoint lạ.

[Trạng thái phát hành RC149: đang kiểm tra.]
