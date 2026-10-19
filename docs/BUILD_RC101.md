# RC101 — Thu gọn phạm vi bản nộp

Phiên bản `1.0.0rc101` giữ các tối ưu thư viện, chuyển đổi, xem trước,
giọng Việt–Mỹ và Mascot từ RC100.

## Giao diện bản đóng gói

- Ẩn Lớp học ở thanh bên, Trang chủ, Cài đặt và lối mở kết quả lớp.
  Đi trực tiếp đến trang lớp/kết quả sẽ trở về Trang chủ.
- Ẩn Giải thích Anh, Ví dụ, Câu hỏi gợi mở và Gợi ý Việt trên Mascot;
  giữ trình chiếu, chuyển slide, hai loa, âm lượng, Cài đặt và Ẩn mini.
- Ẩn lối mở Trợ giảng & Quiz, chốt bản chuẩn bị và các công cụ tương ứng
  trong xem trước; hướng dẫn và ví dụ Cài đặt chỉ mô tả phạm vi được giữ.
- Không có nhãn “đang phát triển” trên giao diện bản nộp.
- Không xóa mã, dữ liệu lớp cũ, câu hỏi, thiết lập hoặc âm thanh.

Đây là lựa chọn phạm vi sản phẩm, không phải cơ chế bảo mật. Mã nguồn
chạy phát triển vẫn bật các phần thử nghiệm. Khi cần phát triển lại,
đặt `BILICLASS_EXPERIMENTAL_TEACHING=1` trước khi khởi động; `0` cho
phép thử giao diện bản nộp từ mã nguồn. Bản đóng gói mặc định tắt,
không có nút bật trong giao diện thầy cô.

## Kiểm chứng trước đóng gói

- 112 kiểm thử chính sách tính năng, cặp giọng và an toàn sao lưu qua
  bằng môi trường ảo của dự án.
- Qt Windows thử cả bật/tắt: thanh bên, tab Cài đặt, điều hướng trực tiếp,
  Mascot, trình sửa và hướng dẫn; không có cảnh báo QML, dữ liệu nguồn và
  WAV không đổi. Kiểm tra tại 1080×700 và 1366×850.
- Qt + Office kiểm tra lại với phạm vi bản nộp: chuyển đổi, xem trước,
  tên tải mới, bước tạo giọng, chọn bài trên Mascot, phát/tạm dừng/đổi
  slide. Qt xác nhận mặc định giọng qua điều hướng và khởi động lại,
  đúng mẫu nghe thử/người đọc/tốc độ; WAV cũ giữ nguyên.
- Nền RC100 có 1.094 kiểm thử cốt lõi qua, không chạy hai nhóm browser
  trong lượt đó. RC101 không tuyên bố đã chạy lại toàn bộ số này.

Bằng chứng chi tiết nằm riêng trong `reports/rc101`, không đưa vào Git.
Chưa chứng nhận máy Windows sạch, màn chiếu thứ hai hoặc click loa vật lý
trên mọi Office. Chưa hoàn tất tái dựng mọi bài chỉ chứa ảnh/công thức
và chưa triển khai đọc từng đoạn bằng nút riêng.

## Đóng gói và bảo toàn dữ liệu

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc100-mascot-menu --output dist/rc101-submission
./scripts/verify_release.ps1 -DistRoot dist/rc101-submission
```

Chỉ dùng nền RC100 đã kiểm chứng, dựng lại mã ứng dụng. Gói cài và bộ
giọng không thuộc commit mã nguồn. Bản nộp phải được thử từ gói cài với
chính sách mặc định, không dựa vào biến môi trường phát triển.

Chỉ dọn bản dựng/cài RC cũ sau khi RC101 qua kiểm chứng; giữ RC100 làm
bản lùi và bỏ qua phiên bản còn tiến trình chạy. Thư viện cá nhân, bài
gốc, WAV, thiết lập, key và bản sao lưu nằm ngoài phạm vi dọn bản RC.

Hiện chức năng xóa vĩnh viễn bài trong thùng rác xóa bản ghi và lịch sử;
không đưa vào Thùng rác Windows. Các tệp nguồn/WAV/xuất, bản sao lưu và
báo cáo riêng vẫn được giữ; không đồng nghĩa đã thu hồi toàn bộ dung lượng.
