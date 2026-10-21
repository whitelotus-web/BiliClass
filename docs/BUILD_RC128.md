# RC128 — Nút lưu hồ sơ theo thay đổi chưa lưu

Nút Lưu thông tin chỉ bật khi tên thầy/cô, trường hoặc bộ môn khác
giá trị đã lưu. Sau lưu thành công, nút tự tắt. Sửa rồi hoàn nguyên
giá trị cũng tắt nút. So sánh theo cùng quy tắc loại khoảng trắng và
tên mặc định với backend. Môn Khác để trống vẫn không được lưu.
Logo tự lưu riêng nên không làm nút hồ sơ bật lại. Các nút Lưu trong
Cài đặt dùng màu nền/chữ vô hiệu hóa rõ ràng, giữ nguyên vị trí nút.

Kiểm bằng `.venv`: pytest danh mục môn đạt. Qt thật kiểm gõ phím
vào tên, sửa trường/bộ môn, hoàn nguyên, lưu và trạng thái tắt ngay
sau lưu. Kiểm logo tự lưu, môn tùy chọn gồm dấu phẩy và khôi phục
giá trị sau mở lại. Luồng bố cục Cài đặt sáng/tối ở 1080/1366/1920,
sao lưu/khôi phục thư viện thử và các tab hiện có đều đạt, không cảnh
báo QML. Dữ liệu/ảnh thử giữ ngoài Git.

Bản này gồm các sửa Mascot và cấu hình giọng đã kiểm ở RC127.
Nguồn `1.0.0rc128`, commit
`6cfcf9d7075a0fd89a2b9ba0293857c90c0781d6`. Dựng một lần sau kiểm,
dùng runtime RC127 có manifest SHA256. Gói
`dist/rc128-profile-save/BiliClass-RC128-Windows.zip`, 1.255.961.601
byte, SHA256
`f64c58c40680e027e59757126cfc11ab0b1cfaa3c59a76be1ce4b5a404c4a073`.
Đối chiếu 4.667 file và 54 QML/qmldir khớp nguồn. Smoke bản đóng gói
tab Cài đặt 1366×850 đạt, không cảnh báo QML.

Cài tại `F:/Applications/BiliClass/1.0.0rc128`, mở từ Explorer vào tab
Cài đặt. Cửa sổ chính/Mascot phản hồi, icon và shortcut đúng phiên bản.
Đối chiếu sau cài và mở giữ nguyên 10 bài/tệp nguồn, 1.183 WAV, hồ sơ
thầy cô/trường/bộ môn, logo, API key mã hóa và cấu hình giọng. Đóng
RC126 bình thường; giữ PowerPoint và RC80 độc lập. RC127 không được cài.
