# RC127 — Đóng/mở Mascot và cấu hình khi chưa trình chiếu

Bảng trợ giảng giữ sẵn bố cục ở chiều rộng khi mở, tránh tính lại chữ
trong khung nhỏ của nhân vật. Đổi vị trí/kích thước cửa sổ bằng một
lần cập nhật, giữ neo nhân vật theo kích thước đích. Bỏ việc xếp hàng
gọi hiện cửa sổ sau mỗi thay đổi chiều rộng/cao. Bảng mờ hiện/ẩn trong
110 ms; bấm lại giữa chuyển tiếp đảo chiều ngay, không chặn lượt bấm.
Chỉ thu cửa sổ sau khi bảng ẩn xong; kéo thả vẫn giữ neo và vị trí lưu.

Trạng thái chỉ mở PowerPoint/gán bài cho Mascot không khóa cấu hình
tạo giọng. Chọn bài, vị trí loa và tạo giọng dùng cùng điều kiện chặn:
tác vụ, tạo giọng, trình chiếu thực sự, chuyển trạng thái Office hoặc
tiết học đang chạy. Giữ riêng bài đang gán cho Mascot khi đổi bài ở
màn giọng; chọn bài mới dừng nghe thử. Khi mở lại sản phẩm, kiểm cả
vị trí loa đã lưu để tránh lấy lại bản tạm có vị trí cũ.

Chân trang phân biệt đang nghe thử/chuẩn bị câu mẫu, Mascot đã gán bài
chưa trình chiếu và PowerPoint đang trình chiếu/chuyển trạng thái.
Không còn báo sẵn sàng trong những trạng thái đó.

Kiểm bằng `.venv`: 31 pytest cấu hình giọng và chuyển bài đạt. Qt thật
thử 192 lượt bấm nhanh mỗi tỷ lệ 100%/150%, sáng/tối, cả bốn góc màn
hình. Bản trước tái hiện một khung hình lệch neo 170 px; sau sửa neo
giữ cố định, sai số ở 150% tối đa do làm tròn tọa độ. Kiểm giữ cửa sổ
native, kéo bảng, thu bằng nút, cuộn, tooltip phím và cài đặt. Kiểm
chọn bài/vị trí khi chỉ gán, giữ nguyên bài gán, khóa khi thật sự chiếu
hoặc chuyển trạng thái. Dùng thư viện và dữ liệu thử riêng ngoài Git.
Kiểm cửa sổ Windows thật đạt: luôn nổi, không có owner, thu nhỏ/khôi
phục cửa sổ chính không giấu Mascot, ẩn rõ ràng không bị mở lại, đóng
app thoát cả bảng. Không có cảnh báo QML trong các smoke đạt.

Nguồn `1.0.0rc127`. Dựng một lần sau commit đã kiểm, dùng runtime
RC126 có manifest SHA256. Thông tin gói/cài đặt bổ sung sau xác minh.
