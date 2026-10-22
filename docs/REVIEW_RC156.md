# RC156 — bản nguồn chờ thử

Ngày 23/10/2026. Không tạo bản cài, ZIP hay bản phát hành RC156.
Bản phát hành gần nhất vẫn là RC155. Giáo viên thử bản nguồn trước,
chỉ đóng gói khi có yêu cầu tiếp theo.

## Thay đổi

- F1 mở đầu bằng bốn bước chọn bài, chuyển đổi, tạo giọng và mở để dạy.
  Bảy mục theo việc cần làm, tìm không dấu, xử lý không có kết quả;
  Ctrl+F đưa con trỏ vào ô tìm. Có hình hướng dẫn phím và chuột Mascot.
  Đóng hướng dẫn giữ nguyên công việc đang mở.
- Thư viện bỏ số bài ở góc thanh tác vụ, để thùng rác ở cuối hàng.
  Loa trên thẻ căn theo lề phải ảnh. Vùng tên dành hai dòng; các thẻ
  cùng hàng đều cao và nút mở/tạo giọng cùng vị trí.
- Chay-BiliClass.cmd mở mã nguồn tại thư mục dự án, tắt các tính năng
  thử nghiệm để giáo viên thử cùng phạm vi với bản phát hành.
- Cập nhật hai kỳ vọng kiểm thử cũ: thông báo chọn cặp giọng và khoảng
  nghỉ giữa đoạn 1,1 giây đã áp dụng từ RC148. Không đổi bộ xử lý âm thanh.

## Kiểm chứng tại máy phát triển

Dùng môi trường ảo của dự án. Ruff và compileall đạt. Lượt pytest-core
có 1.581 đạt, hai kỳ vọng cũ nêu trên không đạt; sau cập nhật, chạy lại
hai module liên quan đạt 18/18. Báo cáo và ảnh kiểm chứng lưu riêng trong
reports/rc156, không đưa vào Git.

Qt F1 và thư viện đạt với giao diện sáng/tối, danh sách/thẻ, màn hình
1080/1366. F1 và nút thanh bên mở cùng hướng dẫn; tìm kiếm và đóng hộp
không chuyển trang. Kiểm tra thẻ gồm tên dài hai dòng, bốn trạng thái
giọng, lề phải icon, chiều cao/nút cùng hàng và điều khiển bằng bàn phím.

Qt đầu vào Chuyển đổi/Tạo giọng đạt ở trạng thái chưa chọn, một/nhiều
bài, xem trước/chuyển slide và bỏ riêng bài. Hàng đợi chuyển đổi/tạo
giọng và luồng giọng hoàn tất đạt, dùng tài liệu/WAV thử riêng;
không gửi dữ liệu giáo viên đến dịch vụ dịch trong các kiểm tra này.

Mở Trang chủ từ bản nguồn bằng scripts/run.ps1 đạt, không có cảnh báo
QML; cửa sổ ghi rõ RC156 và Bản nguồn. Không thay đổi các tab Cài đặt.

## Giới hạn

Chưa kiểm chứng tốc độ trên máy cấu hình thấp. Dung lượng yêu cầu cho
sao lưu phụ thuộc bài giảng, âm thanh và lịch sử của từng thư viện;
không phải dung lượng RAM hoặc kích thước bản cài. Bản nguồn vẫn cần
môi trường phát triển sẵn có. Không đưa thư viện, model hay tệp thực thi
vào commit này.
