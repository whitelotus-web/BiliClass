# RC140 — Đọc rõ lời nhắc kiểm tra bài giảng

Khung kiểm tra bài sau khi chuyển đổi dùng nền vàng nhạt không có
ánh xạ chế độ tối, trong khi chữ đã thành màu trắng theo giao diện.
RC140 dùng bộ màu nền/viền/chữ cảnh báo riêng cho sáng và tối.
Tiêu đề 14 px, mô tả 13 px và xuống dòng theo chiều rộng.

Tách rõ “Cần xem lại trước khi dạy” với “Cần sửa bố cục trước khi
dạy” khi có FAIL. Số slide và kết quả tự căn chỉnh vẫn được giữ.
Lời nhắc chữ trong ảnh ghi rõ slide nguồn và việc cần đối chiếu;
gom vào cùng khung để hai công cụ hiển thị giống nhau. Dữ liệu
bài cũ được diễn đạt lại khi hiển thị, không sửa tệp bài/âm thanh.
Giữ nút Xem vị trí, chọn trang, Xem slide và kiểm tra/tự sửa.

10 pytest chẩn đoán/duyệt bài trong `.venv` đạt. Qt smoke thử cả
Chuyển đổi và Tạo giọng ở sáng/tối, thu gọn/mở rộng, 1080 × 700
và 1366 × 850. Màu chữ thực tế so với nền đạt tương phản tối thiểu
6,31:1; kiểm chữ không bị cắt, mở đúng slide và không cảnh báo QML.
Đã xem ảnh hai giao diện. Ruff các tệp Python đổi và compileall đạt.

Đây là sửa cách hiển thị kết quả kiểm tra; không tự duyệt các cảnh
báo hay cam kết mọi chữ/công thức trong ảnh đã được kiểm chứng.
