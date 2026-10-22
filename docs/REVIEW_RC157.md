# RC157 — giữ kết quả sau khi xử lý nhiều bài

Ngày 23/10/2026. Bản nguồn chờ giáo viên thử; không tạo gói cài hoặc
bản phát hành RC157. RC155 vẫn là gói phát hành gần nhất.

## Vấn đề và hành vi sau sửa

Trước đây, khi mọi bài trong hàng đợi hoàn tất, cả trạng thái Qt và
panel QML đều ẩn hàng đợi. Hai công cụ vì thế quay lại màn hình chọn
file, dù kết quả đã được lưu.

RC157 giữ màn hình **Đã chuyển đổi … bài giảng** hoặc **Đã tạo giọng đọc
cho … bài giảng**. Mỗi bài có **Xem bài** và **Mở thư mục**. Người dùng
chọn lượt khác hoặc bấm **Về Thư viện** khi sẵn sàng. Bài được lưu ngay
khi xử lý xong; nút về Thư viện chỉ đóng lượt, không thực hiện thêm bước
lưu và không xóa bài.

Đổi trang hoặc mở riêng một kết quả vẫn có thể trở lại danh sách bằng
thanh trạng thái. Hủy hộp chọn file mới giữ nguyên kết quả cũ. Lượt hoàn
tất được khôi phục từ journal khi mở lại ứng dụng, cho đến khi người
dùng đóng lượt bằng **Về Thư viện**. Hoàn tất hàng đợi ở nền không tự
chuyển khỏi trang người dùng đang xem.

Rà soát cũng sửa hai tình huống cuối lượt:

- Dừng đến sau khi bài cuối đã lưu: ghi nhận hoàn tất thay vì để trạng
  thái tạm dừng dù không còn bài nào phải xử lý.
- Ghi trạng thái cuối lượt gặp lỗi: vẫn có **Tiếp tục** dù các bài đã
  được lưu hết, để hoàn tất checkpoint mà không chạy lại các bài đó.
  Nếu đóng lượt gặp lỗi ghi, kết quả vẫn hiện để thử lại.

## Các luồng đã kiểm tra

| Luồng | Bằng chứng |
| --- | --- |
| Chưa chọn file, một bài, nhiều bài ở hai công cụ | Qt batch-inputs; ảnh sáng/tối 1080/1366; kiểm tra lề và các nút |
| Chuyển đổi một bài: dừng, tiếp tục, bỏ đầu vào, hoàn tất, xem slide, tải, mở đúng kết quả | Qt google-translation với Office thật và API fixture |
| Tạo giọng một bài: hoàn tất, xem trước, đổi trang, mở lại kết quả đúng bài | Qt completed-voice với Office và WAV fixture |
| Nhiều bài: xử lý lần lượt, lỗi riêng một bài, chỉ thử lại bài lỗi, dừng/tiếp tục | Qt batch-queue và pytest batch-jobs |
| Nhiều bài hoàn tất: giữ màn hình, mở đúng ID từng bài/thư mục, hủy chọn lượt mới, về Thư viện | Qt batch-queue; ảnh sáng/tối 1080/1366 |
| Đổi trang khi đang chạy, kết quả ở nền, mở lại kết quả và khôi phục trạng thái đã lưu | Qt batch-queue |
| Lỗi khi đóng lượt và Dừng đến sau kết quả cuối | Qt batch-queue; pytest tham số cho cả convert/voice |
| Hướng dẫn F1 phản ánh các nút hoàn tất mới | Qt help-guide |

71 pytest liên quan đạt. Ruff và compileall đạt. Corpus cấu trúc đạt,
giữ nguồn/media; không dùng kết quả này để khẳng định mọi nội dung dịch
hay hiệu ứng Office đều đúng. Qt không có cảnh báo QML. Các log lỗi trong
batch-queue gồm lỗi được chủ động tạo để kiểm tra đường khôi phục.

Các phép thử dùng thư viện/tài liệu/WAV riêng, API dịch giả lập, không
gửi bài của giáo viên đến dịch vụ và không phát sinh sử dụng key thật.
Thao tác mở từng kết quả hàng đợi được bắt để kiểm tra đúng ID; không
mở hàng loạt PowerPoint của người dùng. Báo cáo/ảnh nằm trong reports/rc157,
không đưa vào Git. Không đổi các tab Cài đặt, không sửa cơ chế lưu bài,
không tạo thêm bộ model hoặc bản thực thi.
