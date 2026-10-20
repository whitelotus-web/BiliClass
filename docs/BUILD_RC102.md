# RC102 — Tránh giữ luồng giao diện khi chờ ổ đĩa

Nhật ký cục bộ RC99/RC101 ghi nhận các lần giao diện ngừng phản hồi hơn
5 giây trong `Library.trash_lessons` và `GoogleSettings.refresh` khi mở
thư mục/cơ sở dữ liệu key. Sao lưu chạy nền cùng lúc làm rõ thời gian
đợi ổ đĩa; không dùng việc dọn ổ làm lý do giữ các thao tác này trên Qt.

## Thay đổi

- Xóa vào thùng rác, khôi phục và xóa vĩnh viễn dùng kết nối SQLite riêng
  trên worker; giao diện giữ chọn cho tới khi thay đổi đã lưu. Lỗi giữ
  lựa chọn còn hợp lệ để thử lại. Giữ nguyên các tệp PowerPoint/âm thanh.
- Khóa ghi trước khi đọc toàn bộ nhóm bài cần xóa, tránh thay đổi đồng
  thời bị ghi đè. Giữ giao dịch cả nhóm và bảo vệ tiết học đang hoạt động.
- Thanh trạng thái hiện tác vụ; chặn bấm lặp và bỏ lệnh hủy giữa một giao
  dịch ghi không thể hủy. Cửa sổ vẫn nhận tìm kiếm, đổi kích thước và vẽ.
- Thông tin key, hạn mức, OCR và PowerPoint được đọc ở worker rồi công bố
  một ảnh trạng thái đã che key. Các yêu cầu làm mới lặp được gộp; kết quả
  cũ không ghi đè lần lưu mới. Lưu/đổi tên/xóa/thử lại key cũng chạy nền.
- Đổi thẻ/danh sách và cách sắp xếp cập nhật từ bộ nhớ ngay, gộp lưu nền;
  đổi nhanh hoặc thoát ngay giữ lựa chọn cuối. Không ghi SQLite trên Qt
  khi đổi cách xem, kể cả lúc tác vụ thư viện đang chờ khóa ghi.
- Chỉ xóa ô nhập key sau khi lưu và đọc lại thành công. Hiện đang đọc cấu
  hình ở lần đầu; giữ trạng thái gần nhất nếu làm mới gặp lỗi tạm thời.
- Hoàn tất một tác vụ khác không đánh dấu sao lưu tự động là đã xong.
  Sao lưu đợi tác vụ nặng đang chạy và dùng ưu tiên CPU thấp hơn.
- Đóng ứng dụng chờ worker đọc cấu hình kết thúc trước khi dọn đối tượng.
  Giữ phạm vi bản nộp RC101 và các tối ưu chuyển đổi/giọng/thư viện trước đó.

## Kiểm chứng

- 65 kiểm thử nhóm thư viện, Google, sao lưu và đổi nơi lưu qua ban đầu.
- Bộ kiểm thử lõi cuối: 1.111 qua; một cảnh báo thư viện phụ thuộc.
  Không chạy hai nhóm tích hợp trình duyệt ngoài phạm vi sửa này.
- Qt Windows với dữ liệu riêng: một kết nối khác giữ khóa ghi 1,2 giây;
  xóa 20 bài vẫn có nhịp giao diện, đổi kích thước/tìm kiếm được. Thử thêm
  khôi phục, xóa vĩnh viễn, nhóm không hợp lệ, bấm lặp và yêu cầu hủy.
- Cố tình trì hoãn đọc/lưu key, gộp mười yêu cầu đọc, kết quả cũ tới sau
  một lần lưu mới và lỗi đọc lại sau lưu. Mẫu nhập không mất khi thất bại;
  không có key thô trong trạng thái QML. Khoảng ngắt nhịp lớn nhất 0,219 giây
  trong lượt kiểm tra này; không có cảnh báo QML.
- Qt với Office và API giả lập qua: chuyển đổi, hủy/tiếp tục, xem trước,
  tên tải và bước tạo giọng. Qt thư viện/ảnh bìa thật, ba kích thước, kéo/
  chọn, đổi tên key giữ bộ đếm qua. Kiểm tra ẩn lớp học và khôi phục phạm
  vi phát triển qua. Đây là bằng chứng trên máy hiện tại, không khẳng định
  mọi thao tác trên mọi máy sẽ không thể ngừng phản hồi.

Bằng chứng riêng trong `reports/rc102`, không đưa dữ liệu/log cá nhân vào Git.

## Đóng gói

```powershell
.venv/Scripts/python.exe -m scripts.build_from_runtime --baseline dist/rc101-submission-final --output dist/rc102-responsive
./scripts/verify_release.ps1 -DistRoot dist/rc102-responsive
```

Mã/commit, checksum và kết quả cài được ghi sau khi hoàn tất. Bài chỉ chứa
ảnh/công thức vẫn cần đối chiếu; không thêm mô hình sinh câu hỏi hoặc nút
đọc riêng từng đoạn trong mốc sửa luồng giao diện này.
