# RC162 — nền mascot cho Thông tin BiliClass

Tab Thông tin BiliClass dùng nguyên ảnh hai mascot bên laptop do người dùng
cung cấp. Ảnh được lưu trong tài nguyên giao diện, không phụ thuộc thư mục
Downloads trên máy. PNG 1672×941, 1.59 MB; đối chiếu SHA-256 trùng ảnh gốc.

Logo và chữ BiliClass nằm trên cùng một hàng, căn giữa theo cụm thông tin
bên trái. Phiên bản, nút kiểm tra cập nhật, bản quyền, trường, liên hệ và mô
tả dùng cùng trục giữa. Giới hạn toàn bộ nội dung ở 44.5% chiều rộng ảnh
để không đè lên mascot. Đo cả mép thực của logo và cột chữ khi kiểm tra
căn giữa, tránh trường hợp chỉ căn giữa khung nhưng nội dung vẫn lệch trái.

Ảnh giữ tỷ lệ và hiện đủ hai mascot. Cửa sổ hẹp thu logo, chữ thương hiệu
và cho các dòng thông tin xuống dòng; cuộn dọc khi cần. Nền mở rộng bằng
màu xanh nhạt khi nội dung cao hơn ảnh. Ở cửa sổ rộng, giới hạn khung ảnh
1440 pixel và căn giữa trong trang. Chữ trên ảnh luôn xanh đậm để dễ đọc
trong cả chế độ sáng và tối. Các tab Cài đặt khác được giữ nguyên.

Kiểm tra Qt thật với thư viện thử riêng ở 1080×700, 1366×850, 1920×1080
và cửa sổ laptop 860×620, sáng/tối: ảnh tải được, các nhóm ở đúng vùng,
chữ không tràn ngang, liên hệ tới được bằng cuộn, không cảnh báo QML.
Nút cập nhật đi qua slot thật, kiểm tra một lần và bật lại khi xong;
khóa trong lúc tải bản mới. Chỉ phản hồi mạng của lượt kiểm thử được giả
lập, không tải hay cài phiên bản khác.

21 kiểm thử giao diện sáng/tối và cập nhật đạt. Qt smoke còn kiểm tra các
tab khác, lưu cấu hình và sao lưu/khôi phục trên dữ liệu riêng. Ruff,
compileall và diff-check đạt. Báo cáo và ảnh ở `reports/rc162`, ngoài Git.
Thay đổi này chỉ cập nhật mã nguồn và tài nguyên; chưa tạo bộ cài.
