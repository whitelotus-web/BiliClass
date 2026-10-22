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
Người dùng xác nhận thao tác gặp lỗi là Chọn bài trong Mascot; chưa
mô tả triệu chứng cụ thể, nên chưa kết luận đổi thứ tự là toàn bộ lỗi.

Sau sửa: 46 pytest về phiên dạy, chuyển trạng thái, cache và thiết lập
thư viện đạt; Ruff/compileall đạt. Ba Qt smoke chọn bài, phiên dạy với
Office thật và menu Mascot đạt, không cảnh báo QML. Phép thử Office
giữ nguyên nguồn và WAV mẫu, kiểm mở/đổi bài trước/sau tạo giọng,
file ngoài có giọng nhúng, F5, tạm dừng/đọc tiếp và thu nhỏ app. Chưa
chứng nhận máy chiếu, nhiều màn hình hoặc mọi file PowerPoint lạ.

Kiểm bổ sung bằng sự kiện con trỏ trong cửa sổ Qt riêng: mở popup và
chọn một dòng giữ đúng ID. Mở bản sao bài Hóa có giọng 44 slide người
dùng gửi qua luồng file ngoài, gắn Mascot và F5 đạt; phép thử này không
phát âm thanh hay thay nội dung nguồn. Cả hai bằng chứng không thay
cho việc đối chiếu triệu chứng cụ thể trên phiên của người dùng.

Đã phát hành từ `e9ca1afd949efe0669d38d70fb7310776397a111`;
[Source checks](https://github.com/whitelotus-web/BiliClass/actions/runs/39762126036) đạt cho đúng commit gói.
[Gói RC149](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc149): 1,258,143,948 byte, SHA-256
`d5afb78b3b7980dcf90451cb0b2bb763c9ffd7d062cd73184a3af06a5702613e`. 59 tệp QML/qmldir và bytecode
khớp nguồn; ZIP/digest/tag và updater công khai đạt. Cài/mở Trang chủ
từ Explorer, Mascot mặc định ẩn; hồ sơ/key, bài và
1752 WAV tham chiếu giữ nguyên.
