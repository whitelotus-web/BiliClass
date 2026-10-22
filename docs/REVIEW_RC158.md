# RC158 — căn giữa chuyển slide và giảm dung lượng sao lưu

Ngày 23/10/2026. Bản nguồn trên F để giáo viên thử; chưa tạo bản cài,
gói thực thi, bộ model hay release mới. RC155 vẫn là gói phát hành gần nhất.
Kế thừa các sửa luồng và rà soát toàn hệ thống trong [RC157](REVIEW_RC157.md).

## Khung xem trước

Trước đây hàng chuyển slide có nút nghe bên phải nhưng bỏ khoảng đệm
bên trái khi giọng hoàn tất, khiến cụm trước/số slide/sau dạt sang trái.
RC158 đặt cụm đó theo tâm khung slide. Nút nghe ở bên phải; khi cửa sổ
hẹp, nút nghe xuống hàng dưới. Không đổi trạng thái slide hoặc thao tác
nghe. Khung hoàn tất giọng riêng vốn đã căn giữa được giữ nguyên.

Kiểm chứng Qt trên dữ liệu riêng: một/hai nút nghe, sáng/tối, cửa sổ
900/1080/1366/1920; kiểm tra tâm, biên, khoảng cách, ảnh chụp và bấm
trước/sau qua renderer Office thật. Không thao tác trên bài đang mở
của giáo viên. Âm thanh dùng WAV thử và thiết bị phát giả lập.

## Sao lưu

Một nội dung PowerPoint có thể tồn tại đồng thời ở nguồn và lịch sử
chuyển đổi. Trước đây ZIP chứa đủ các bản đó, nên dung lượng yêu cầu
tính theo toàn bộ tệp. RC158 nhóm theo kích thước và SHA-256, ghi nội
dung trùng một lần; manifest vẫn liệt kê đầy đủ đường dẫn và checksum.
Khi khôi phục, mỗi đường dẫn được tạo thành tệp riêng, không dùng liên
kết đến bản khác. Sửa một tệp đã khôi phục không sửa tệp còn lại.

- Không xóa hoặc thay đổi dữ liệu nguồn/lịch sử để giảm dung lượng.
- Định dạng 3 chỉ dùng khi có tệp trùng; thư viện không có tệp trùng
  tiếp tục dùng định dạng 2. Đọc được bản sao định dạng 1 và 2 đã có.
  Bản sao định dạng 3 cần RC158 trở lên để khôi phục.
- Trước sao lưu, chỉ đọc hash của các tệp có cùng kích thước; dữ liệu
  đọc từng khối 1 MiB, không tạo bản sao trung gian của toàn bộ nguồn.
- Dung lượng trống để ghi gói tính theo các nội dung riêng biệt, cộng
  128 MiB dự phòng. Khi khôi phục, tính đủ tất cả bản sao được tạo lại.
  Giới hạn số tệp và 128 GiB áp dụng cả các đường dẫn dùng chung nội dung.
- Kiểm tra đường dẫn, tham chiếu trực tiếp, checksum, cơ sở dữ liệu và
  giới hạn trước khi công bố thư viện khôi phục. Không cho tham chiếu
  vòng, chuỗi, ra ngoài thư mục hoặc đè tên khác chỉ khác hoa/thường.
- Nếu tệp thay đổi trong lúc sao lưu hoặc ghi gặp lỗi, không thay bản
  sao tốt trước đó. Tiến trình hiển thị theo phần trăm trong Cài đặt.

Phân tích **metadata bản sao thành công gần nhất** của máy cho thấy
471 tệp trùng, khoảng 4,00 GB. Nội dung riêng biệt khoảng 7,29 GB thay
vì 11,28 GB; yêu cầu trống dự kiến khoảng 7,42 GB gồm dự phòng. Đây là
ước tính trên bản sao cũ, chưa phải dung lượng được giải phóng hoặc
kết quả chạy sao lưu mới trên thư viện cá nhân. Dung lượng thực tế tùy
dữ liệu mới và khả năng nén. Không dùng con số này làm ước tính RAM
hay kích thước bộ cài.

Kiểm thử chuyên biệt gồm khôi phục đủ tệp/độc lập, nội dung khác nhưng
cùng kích thước, tính dung lượng ghi/khôi phục khác nhau, gói hỏng,
tham chiếu không hợp lệ, giới hạn sau mở rộng và nguồn đổi giữa chừng.
Qt Cài đặt sao lưu/khôi phục thật trên thư viện thử, giữ bài/hồ sơ/WAV
và cả đường dẫn trùng. Báo cáo và ảnh ở `reports/rc158`, ngoài Git.

Kết quả: **1.604 pytest nguồn lõi đạt**, một cảnh báo deprecation
FastAPI test client như RC157; hai nhóm Browser AI cũ tiếp tục nằm ngoài
phạm vi luồng đang dùng. 59 kiểm tra riêng về sao lưu/dữ liệu đạt trước
khi chạy nhóm nguồn lõi. Hai nhóm Qt Cài đặt và hoàn tất/xem trước giọng
đạt, không cảnh báo QML. Ruff, compileall và kiểm tra diff đạt. Không
dùng các phép thử này để khẳng định tốc độ tổng hợp giọng trên máy yếu.

Việc xóa ZIP build cũ vẫn bị hệ thống thực thi chặn (`blocked by policy`);
không ghi nhận là đã dọn thành công. Không dùng thao tác khác để vượt
lệnh chặn đó. Giữ mã nguồn, thư viện cá nhân, môi trường và bộ model.
