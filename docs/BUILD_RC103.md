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

Bản cài, mã/commit và checksum được ghi sau khi hoàn tất.
