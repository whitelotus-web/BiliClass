# RC164 — hoàn thiện bố cục Thông tin BiliClass

Cụm logo được phóng lớn theo vùng trống bên trái ảnh, vẫn căn giữa với
phiên bản và bản quyền. Hai dòng giới thiệu chuyển lên ngay dưới logo,
ngắt dòng sau “trình chiếu”. Khối bản quyền hạ xuống vị trí mô tả cũ;
dòng cuối cách đáy khung 40 pixel.

Khung nền dùng chiều cao vùng hiển thị khi đủ chỗ cho nội dung. Cửa sổ
1366×850 và 1920×1080 hiện cả dòng bản quyền cuối mà không cần cuộn.
Chỉ cắt bớt sóng nền ngoài cùng khi khung rộng, giữ cả hai mascot.
Cửa sổ hẹp vẫn cuộn dọc và giữ tỷ lệ ảnh, không tràn ngang.

Đã kiểm tra Qt thật với thư viện riêng: 1080×700, 1366×850, 1920×1080
và 860×620, sáng/tối; đối chiếu ảnh và tọa độ của logo, mô tả, phiên bản,
bản quyền; không có cảnh báo QML. Nút cập nhật, các tab Cài đặt và luồng
sao lưu/khôi phục vẫn qua Qt smoke. 21 kiểm thử appearance/updater, Ruff,
compileall và diff-check đạt. Báo cáo và ảnh ở `reports/rc164`, ngoài Git.

Mốc mã nguồn: 1.0.0rc164. Mã nguồn, tài nguyên giao diện và kiểm thử được
đẩy lên remote đã cấu hình sau khi kiểm tra. Thư viện cá nhân, file bài
giảng, model, báo cáo thử và executable không đưa vào Git. Chưa tạo bộ
cài; giữ bản nguồn trên F để người dùng duyệt trước bước đóng gói.
