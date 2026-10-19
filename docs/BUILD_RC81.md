# RC81 — Tách mở PowerPoint và tạo giọng, làm nhẹ cấu hình Mascot

## Thay đổi

- Thư viện có hai nút rõ: **Mở PowerPoint** mở/gắn Mascot và giữ nguyên
  trang; **Tạo giọng đọc** vào cấu hình cho đúng bài, không mở PowerPoint,
  tổng hợp giọng hay đổi liên kết phiên dạy. Cả danh sách/thẻ có nút này;
  danh sách hẹp xuống hàng thao tác để giữ không gian cho tên bài.
- Mở sản phẩm đã lưu không chạy lại toàn bộ Office repair. Kiểm nguồn,
  bản giọng và cảnh báo bố cục vẫn còn; chuyển đổi và xuất vẫn giữ luồng
  hoàn thiện có kiểm chứng. Không tự duyệt nội dung hay phát âm thanh.
- Sau chuyển đổi, trước/sau tạo giọng và trong Thư viện đều dùng nút
  **Mở PowerPoint** trực tiếp: mở bài đang chọn và gắn Mascot, giữ nguyên
  trang, chỉ trình chiếu khi bấm F5. Bản giọng đã chọn được giữ đúng khi
  thay bài đang gắn. Xác nhận duyệt toàn bài chỉ còn ở lối kiểm tra riêng.
- Cả bản không giọng cũng mở bằng bản sao riêng cho phiên dạy. Tránh
  PowerPoint khóa file preview khiến mở lại/tạo bản tiếp theo báo Access
  denied trên Windows; đóng phiên chỉ dọn đúng bản sao, giữ nguồn/cache.
- Độ trong suốt cập nhật từ bộ nhớ bằng tín hiệu riêng, không ghi SQLite
  hay phát `Bridge.changed` trên mỗi nấc kéo. Gom lần ghi, lưu ở worker
  riêng với thời hạn và số lần thử giới hạn; giá trị mới nhất thắng khi
  đang ghi bản trước. Đóng app hoàn tất giá trị đang chờ; lỗi không xóa
  cấu hình đã lưu trước đó. Nền trong không đổi alpha chữ/nút/vùng bấm.
- Bỏ bộ chọn góc; mặc định phải dưới khi mở ứng dụng, vị trí kéo được
  giữ trong phiên và có nút về góc. Không lấy lại góc trái/vị trí kéo cũ
  từ bản trước. Bộ chọn vị trí **loa trên slide** giữ nguyên.
- Bảng trợ giảng theo cùng kích thước Mascot: Nhỏ/Vừa/Lớn điều chỉnh cả
  nhân vật, chiều rộng bảng, cỡ chữ và chiều cao nút; giới hạn theo màn
  hình để còn đọc/bấm được. Bỏ cấu hình cỡ bảng độc lập. Lưu cấu hình
  không tự thu bảng đang mở; giữ liên kết và trạng thái dạy.
- Thông tin phụ kiện nằm cạnh nhóm lựa chọn hiển thị trên màn hình rộng,
  tự xuống hàng khi hẹp; không còn nhãn môn dưới nhân vật ở bản xem trước
  trong Cài đặt, đồng bộ với Mascot nổi.

## Kiểm chứng

921 ca core đạt, một warning dependency Starlette/httpx; lint và compile
đạt. 17 luồng Qt đạt, không warning QML, gồm Settings/navigation bổ sung.
Office thật xác nhận mở/gắn đúng bài ở cả bốn điểm, giữ trang, đổi phiên
đang mở, mở lại bản không giọng, F5 chủ động, native pause/resume, đổi loa
và loại lệnh từ slide cũ. Dùng WAV im lặng để kiểm lệnh, không coi đây là
đánh giá phát âm hoặc âm thanh qua máy chiếu thực tế.

Kéo 71 mức khi SQLite bị khóa vẫn có nhịp UI, khoảng nhịp dài nhất 0,016 s,
không phát `Bridge.changed`, chỉ lưu lựa chọn cuối khi khóa được nhả. Ba cỡ
bảng, click nền 100%/30%, vị trí phụ kiện ở 1080/1366 và nhãn preview ẩn đạt.
Hai fixture cũ còn trông đợi tự chuyển sang trang giọng được sửa theo yêu
cầu giữ trang; fixture Settings dùng lại đúng ID bài/đoạn đang kiểm tra.

Dùng dữ liệu thử riêng, không đưa thư viện/key/WAV cá nhân vào nguồn hay
bộ cài. Nhóm Browser giữ bằng chứng cũ, không tính là lượt mới. Chưa coi
phép đo này là cam kết tăng tốc mọi bài PowerPoint hoặc chứng nhận phần
còn lại của kế hoạch audit. Gói cài/commit/checksum được ghi sau khi kiểm.
