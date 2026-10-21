# RC130 — Con trỏ nhập chữ, Mascot và hình tải PowerPoint

Lớp MouseArea nhận nút Quay lại của chuột phủ cửa sổ giữ con trỏ mũi
tên mặc định ngay cả khi tắt. Reset `cursorShape: undefined` để ô nhập
và các điều khiển bên dưới dùng con trỏ gốc của Qt. Giữ hành động nút
Quay lại, Backspace, focus và bôi đen chữ; không phủ thêm lớp bắt chuột
lên từng ô nhập.

Bật/tắt bảng Mascot dùng cùng một bề mặt cửa sổ trong suốt thay vì
đổi kích thước cửa sổ native. Tránh Windows hiển thị thoáng texture
nhỏ cũ ở góc bảng mới. Bảng vẫn mờ dần trong 110 ms; khi thu gọn,
mask native chỉ nhận chuột ở nhân vật, vùng bảng ẩn cho bấm xuyên.
Vẫn giữ neo ở bốn góc, kéo bảng/nhân vật, ẩn, menu và always-on-top.

Hai hình do người dùng cung cấp được dùng riêng: PowerPoint → VI/EN
ở Chuyển đổi, PowerPoint → micro ở Tạo giọng đọc. Giữ nguyên PNG
RGBA gốc; chỉ bỏ lề trong suốt trong vùng hiển thị QML và giữ tỷ lệ.
Khung tải giữ chiều cao, dành thêm chiều ngang cho hình nhiều chi tiết.

Xác minh bằng `.venv`:

- 11 pytest cấu hình Mascot/giao diện đạt.
- Trước sửa, con trỏ Windows ở bốn ô được báo đều là mũi tên. Sau sửa,
  kiểm con trỏ native sáng/tối, 100% và 150% ở tìm kiếm, tên bài, tên
  thầy/cô, trường, ô nhiều dòng; kiểm hover/focus, nhập chữ, kéo chọn,
  nút xóa tìm kiếm, ô vô hiệu hóa và lớp Quay lại đang bật.
- 384 lần bật/tắt Mascot ở 20/45/90 ms, bốn góc, sáng/tối, 100%/150%:
  cửa sổ native giữ nguyên hình chữ nhật và handle trong các frame
  lấy mẫu; vị trí nhân vật ổn định. Kiểm hit test native: bảng ẩn cho
  bấm xuyên, nhân vật và bảng mở vẫn nhận chuột.
- Qt kiểm kéo bảng, ba cỡ Mascot, menu, tooltip, độ trong suốt,
  minimize/hide/đóng app; luồng chọn thư viện và chuột Back/Backspace
  đạt. Cập nhật kỳ vọng cũ của smoke cho trạng thái Chưa có giọng.
- Qt bố cục Chuyển đổi/Tạo giọng ở bốn cỡ 1080/1366/1920: đúng hình,
  ảnh tải thành công và điều khiển tới được. Đã xem ảnh giao diện.
  Các luồng trên không có cảnh báo QML; dữ liệu thử giữ ngoài Git.
