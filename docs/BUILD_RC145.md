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

Kiểm tra GitHub phát hiện fixture `Editor` của phép thử lưu vị trí loa
thiếu tín hiệu trạng thái phát mới. Đã cập nhật fixture và chạy lại
5 ca liên quan; không sửa/hạ yêu cầu kiểm tra và không đổi mã ứng dụng.
CI bổ sung kiểm hợp đồng xóa/hoàn tác. Gói Windows được dựng từ
`6474d93d468964e4b12faef304632096f6cc17a1`; thay đổi kiểm thử sau đó
phải giữ nguyên cây `app` và phiên bản trước khi nhận kết quả CI.

402 ca portable và corpus cấu trúc tại máy đạt. Source checks GitHub
đạt tại `139c722`; đã đối chiếu cây ứng dụng và `pyproject.toml` với
commit gói, không có khác biệt. [RC145 đã phát hành](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc145),
ZIP 1.258.099.188 byte, SHA-256
`a4c10fdfffb91c01cab88a1bad7d0ad8c34886068c0ad6bd1280410ff2a079e9`.
57 QML và bytecode ứng dụng khớp nguồn gói; toàn bộ ZIP, digest/tag
và kiểm cập nhật công khai đạt. Đã cài và mở Home từ Explorer,
Mascot mặc định ẩn; hồ sơ, cấu hình/key, nguồn và 1.752 WAV giữ nguyên.
Một bài được đưa vào thùng rác trong lúc kiểm cài: đã chứng minh
chỉ thêm đúng dấu xóa, toàn bộ nội dung gốc và nguồn khớp; giữ thao
tác xóa đó, không tự khôi phục hoặc ghi đè bài người dùng đang thử.
