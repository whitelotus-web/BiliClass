# RC143 — Loa thư viện và kích thước loa trong PowerPoint

Icon giọng trong thư viện bỏ nền/viền thường, dùng xanh lá cho cả
Việt và Anh; chưa có giọng dùng loa gạch chéo xám. Giữ chữ VI/EN
trong hình, tooltip, vùng bấm 96×28 bằng nhau và viền khi dùng bàn
phím. Cùng thành phần hiển thị ở danh sách và lưới, sáng và tối.

Bài Toán vừa thử có canvas 1920×1080 point. Loa cũ luôn rộng 28 point
nên khi chiếu chỉ còn khoảng 20 px. Nay kích thước và khoảng cách
mép lấy theo chiều cao trang: hình rộng 32/540 chiều cao, hai loa
độc lập có khoảng cách; bản 1920×1080 dùng hình 64 point, tương ứng
khoảng 47 px ở ảnh chiếu rộng 1422 px. Vùng phát và tạm dừng có cùng
kích thước. Kiểm tra giao nội dung dùng đúng hình mới; vẫn báo vị
trí cần xem khi vùng đã chọn có nội dung, không tự dời bài gốc.

Tăng phiên bản cache bản chiếu để lần mở từ thư viện dựng lại hình
loa mới từ WAV đã lưu. Không tạo lại giọng hoặc sửa tệp đã xuất trước
đó; tệp PowerPoint đã tải cần tải lại để nhận hình loa mới.

36 pytest liên quan trong `.venv` qua, gồm tỷ lệ hình trên canvas
4:3/16:9 ở hai kích thước, sáu vị trí, nguồn bất biến, native click,
cache và tùy chọn. Qt smoke kiểm tra bốn trạng thái giọng, hai theme,
hai cách xem, màu pixel thật, vùng bấm, hành động và focus bàn phím;
không QML warning. PowerPoint thật giữ các sequence qua SaveCopyAs,
không tự phát và phát/tạm dừng/đọc tiếp qua media API trên WAV fixture.
Script Office cập nhật số loa độc lập theo hành vi hiện tại: VI và EN.
Chưa nghiệm thu chuột vật lý trên máy chiếu thứ hai.

Trên bản sao bài thật 16 slide có giọng Anh, đã nhúng lại 15 loa,
đo và dựng ảnh PowerPoint. Slide 2 là chữ trong ảnh chưa có lời đọc
được xác minh nên không tự gán giọng. Nguồn và 115 WAV được dùng giữ
nguyên hash; không sửa thư viện. Bản nháp OCR ISS và giới hạn xác minh
nội dung của RC142 giữ nguyên. Không thêm hàng đợi hoặc chạy nhiều bài.

Rà luồng mở bài còn phát hiện thư viện có bản ghi nguồn null làm mở
PowerPoint mới bị lỗi. Bỏ qua bản ghi không có nguồn khi so hash để
tiếp tục nhập đúng tệp mới; giữ đường mở có quản lý và bản sao độc lập.
47 ca mở bài, phiên dạy và nhập giọng qua sau sửa lỗi này.
