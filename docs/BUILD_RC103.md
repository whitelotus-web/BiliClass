# RC103 — Hiện cửa sổ sau khi dựng giao diện

Lần mở RC102 với thư viện thật ghi một nhịp chậm 5,11 giây trong
`QQmlApplicationEngine.load`. Cửa sổ chính đã hiện trong lúc QML còn
dựng các thành phần; phép kiểm tra phản hồi Windows 500 ms thất bại.
Không gộp lần chậm khởi động này với các lỗi ghi SQLite/đọc cấu hình
đã sửa ở [RC102](BUILD_RC102.md).

RC103 giữ cửa sổ ẩn khi dựng QML và chỉ hiện trong lượt vòng lặp sự
kiện kế tiếp sau `Component.onCompleted`. Giữ nguyên nhật ký theo dõi;
đây là sửa thời điểm hiện cửa sổ, không khẳng định giảm thời gian nạp.
Các thay đổi chạy nền, bảo toàn dữ liệu và phạm vi bản nộp RC102 giữ nguyên.

Qt Windows đã qua: thư viện kiểm tra cửa sổ ẩn ngay sau dựng, hiện khi
xử lý sự kiện rồi thực hiện các tác vụ bình thường; thử khóa SQLite và
trì hoãn cấu hình vẫn phản hồi (nhịp ngắt lớn nhất 0,266 giây); vỏ cửa
sổ Windows, biểu tượng, thu nhỏ/phóng to và phạm vi ẩn lớp học đúng.
Các lượt này không có cảnh báo QML.
Ruff và 1.111 kiểm thử lõi qua (một cảnh báo thư viện phụ thuộc; hai
nhóm tích hợp trình duyệt ngoài phạm vi không chạy).

## Bộ cài đã kiểm chứng

- Mã nguồn: `0cff33f7b6d73e3c3378d2989a71b2b656cad583`.
- `BiliClass-RC103-Windows.zip`: 1.246.815.409 byte.
- SHA256: `286764b63ae4a889d04be037ec1b145b45f0f1ce44dd7deb51bac12927418ef6`.
- Cài trong đường dẫn Unicode riêng, bốn lượt mở Qt, thông tin phiên bản,
  biểu tượng/shortcut Windows, mô hình Việt và Mỹ đi kèm, tạo hai loa thật
  trên slide qua. Gỡ bản thử giữ nguyên thư viện thử riêng.
- [Bản phát hành RC103](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc103)
  đã đối chiếu checksum ZIP với digest tài sản trên GitHub.

Đây là kiểm tra trên máy hiện tại, không phải chứng nhận máy Windows sạch.

## Mở với thư viện thật

RC103 đã cài và mở độc lập qua Explorer vào Thư viện, có cửa sổ Mascot,
biểu tượng và shortcut đúng. Ba lần kiểm tra phản hồi sau khi hiện cửa sổ
đều không hết hạn 500 ms (lần đầu 0,407 giây). Đối chiếu nguồn bài,
phiên bản chỉnh sửa, 940 WAV được tham chiếu, cặp/tốc độ giọng và checksum
key đều giữ nguyên. RC102 đóng bằng yêu cầu đóng bình thường.

Nhật ký vẫn ghi khoảng nạp QML 5,05 giây trước khi cửa sổ RC103 hiện;
không xóa hoặc đổi ngưỡng nhật ký để che thời gian khởi động này.
Trong 120 lần kiểm tra cửa sổ khi dọn bản cũ, không lần nào hết hạn
500 ms; phản hồi lâu nhất 0,031 giây. Xong đợt dọn, executable RC103 và
RC102 dự phòng vẫn khớp checksum bộ cài.

## Dọn bản cũ trên máy này

Đã dọn các bộ cài/biên dịch cũ đã nhận diện trong `dist`, `.runtime` và
thư mục cài BiliClass. Giải phóng ròng khoảng 123 GiB, sau khi tính cả
chi phí lưu bộ cài mới. Giữ mã nguồn, Git, môi trường Python, mô hình,
toàn bộ thư viện cá nhân và các bản dự phòng đã chọn. RC80 còn đang chạy
được giữ; một thư mục RC99 rỗng đang bị Windows giữ cũng để nguyên.
Không đóng cưỡng bức các ứng dụng khác.
