# RC170: cấu hình và bản xem Word

Ngày 26/10/2026. Bản mã nguồn để thử tiếp, trên nhánh
`codex/word-preview-rc170`; bộ cài và tag RC169 đã phát hành được giữ nguyên.

- **Cấp học → Khối lớp** dùng cùng danh sách lớp với PowerPoint: Tiểu học
  1–5, THCS 6–9, THPT 10–12. Tài liệu cũ mở lại được suy cấp từ lớp đã lưu.
- **Kiểu chuyển đổi** hiện bốn lựa chọn tròn trên cùng một hàng.
- **Màu tiếng Anh** là nút A có gạch màu. Bảng chọn gồm màu chủ đề, màu tiêu
  chuẩn, màu khác và ô **Giữ nguyên màu gốc**. Màu gốc là mặc định ban đầu;
  các màu RGB được kiểm tra trước khi ghi vào Word.
- **Kiểu chữ tiếng Anh** có B, I, U, gạch ngang, x₂, x². Các kiểu kết hợp
  được; chỉ số dưới và trên loại trừ nhau. Phông gốc, màu gốc, in nghiêng là
  các giá trị ban đầu; tài liệu mới lấy lựa chọn định dạng gần nhất.
- Ô phông luôn hiện bên cạnh **Font gốc**. Khi tích, ô chỉ đọc và hiện
  phông lấy từ tài liệu (hoặc danh sách nếu có nhiều phông); từng vùng vẫn
  giữ phông riêng khi xuất. Bỏ tích để chọn phông mới, giữ lựa chọn gần nhất.
- **Bôi đen văn bản** đứng trước. **Tích chọn đoạn/câu** có hai ô vuông con
  **Theo đoạn / Theo câu**, chỉ bật khi chọn cách tích chọn. Hai ô loại trừ
  nhau để mỗi lần chỉ dùng một cách chia nội dung.
- Bản xem trên nền giấy trắng có lề, cỡ chữ, phông, đậm/nghiêng, căn đoạn,
  hình nhúng và bảng. Có **− / Vừa khung / +** để đọc và chọn vùng. Ở cách
  tích chọn, từng phần cũng dùng định dạng gốc thay vì chỉ hiện chữ thuần.
- **Phóng to để chọn** mở rộng vùng gốc trong ứng dụng. **Xong / Thu gọn**
  đưa cùng vùng đọc về vị trí cũ, giữ các vùng đã xác nhận và vị trí cuộn.
  Bấm Escape để đóng cửa sổ mở rộng.
- **Bỏ tất cả** nằm cạnh số vùng đã chọn, và trong cửa sổ mở rộng. Chỉ bỏ
  vùng chọn, không xóa tệp nguồn hay bản Word đã xuất trước đó.
- Nút ban đầu là **Chuyển đổi bài giảng**, ở bên phải ô cấu hình đã chọn.
  Kết quả vẫn tự lưu với hậu tố `(Song ngu VI-EN)` như trước.

## Giới hạn và bảo vệ vùng chọn

Đây là bản đọc nội dung theo định dạng Word, không phải bộ máy phân trang
của Microsoft Word. Ngắt trang, đầu/chân trang, đối tượng nổi, SmartArt và
công thức phức tạp có thể khác. Mở Word để đối chiếu bản cuối.

Chỉ đọc hình raster nhúng trong tài liệu; không truy cập ảnh hoặc liên kết
trên mạng. Hình xem trước có giới hạn dung lượng, số lượng và kích thước.
Tài liệu có quá nhiều vùng định dạng chuyển sang chữ thuần để vẫn chọn được.

Vị trí chữ trong bản xem được đối chiếu với nguồn bất biến qua từng đoạn,
kể cả ký tự UTF-16, ảnh và các ô bảng có nội dung giống nhau. Nếu nội dung
xem trước không khớp, ứng dụng yêu cầu chọn lại thay vì gửi nhầm vùng dịch.
Tệp nguồn không bị ghi đè; các phần bảo vệ trong luồng Word vẫn áp dụng.

## Kiểm tra

Các bài kiểm thử Word kiểm tra ánh xạ vùng, định dạng xuất, ảnh/bảng,
emoji, câu nhiều dòng, màu tùy chọn và dữ liệu mặc định. Qt chạy bằng tài
liệu/thư viện tạm, kiểm tra kéo chuột, bảng màu, các nút kiểu chữ, danh sách
lớp, giao diện sáng/tối, bốn kiểu xuất và dừng/tiếp tục. Dịch vụ trong kiểm
thử là dữ liệu giả lập; không dùng khóa hoặc tài liệu cá nhân để gửi lên mạng.
