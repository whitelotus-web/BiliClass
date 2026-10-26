# RC170: cấu hình và bản xem Word

Ngày 26/10/2026. Bản mã nguồn để thử tiếp, trên nhánh
`codex/word-preview-rc170`; bộ cài và tag RC169 đã phát hành được giữ nguyên.

- **Cấp học → Khối lớp** dùng cùng danh sách lớp với PowerPoint: Tiểu học
  1–5, THCS 6–9, THPT 10–12. Tài liệu cũ mở lại được suy cấp từ lớp đã lưu.
- **Kiểu chuyển đổi**, bảng màu, các nút kiểu chữ và phông nằm trên một hàng
  cấu hình gọn, chia hai cụm: bốn lựa chọn tròn ở nửa trái; màu, kiểu chữ,
  phông và cỡ ở nửa phải, có vạch phân cách nhẹ. Màn hẹp ưu tiên đủ chỗ
  cho các nút định dạng. Bốn lựa chọn dùng tên ngắn khi cần; rê chuột để xem tên đầy đủ.
  Ô cấu hình đã chọn vẫn ghi đầy đủ kiểu chuyển đổi.
  Bỏ các nhãn lặp màu/kiểu/phông tiếng Anh; ô phông giới hạn chiều rộng để
  dành chỗ cho bố cục. Biểu tượng A có vạch đỏ sát chân chữ; màu áp dụng
  vẫn lấy từ lựa chọn trong bảng màu hoặc giữ nguyên màu gốc.
- **Cỡ chữ** nằm cạnh ô phông, có danh sách cỡ phổ biến và cho nhập trực
  tiếp theo bước 0,5 pt. Mặc định ô hiện **Size gốc**, tooltip **Size**;
  vẫn lấy cỡ tại các vùng gốc khi xuất. Chọn cỡ khác sẽ nhớ cho bài mới;
  chọn **Size gốc** để quay về tự động. Bản Anh không còn tự giảm 1 pt.
- **Màu tiếng Anh** là nút A có gạch màu. Bảng chọn gồm màu chủ đề, màu tiêu
  chuẩn, màu khác và ô **Giữ nguyên màu gốc**. Màu gốc là mặc định ban đầu;
  các màu RGB được kiểm tra trước khi ghi vào Word.
- **Kiểu chữ tiếng Anh** có B, I, U, gạch ngang. Bỏ hai nút x₂/x² khỏi giao
  diện; mã xuất vẫn đọc được cấu hình cũ. Các kiểu kết hợp được. Phông gốc, màu gốc, in nghiêng là
  các giá trị ban đầu; tài liệu mới lấy lựa chọn định dạng gần nhất.
  Nút chưa chọn chỉ hiện biểu tượng; nút đang bật mới có nền và viền, cao
  28 px, rộng 26 px và bo góc nhẹ, căn giữa hàng.
- Bên cạnh màu chữ A là **tô sáng chữ** (highlight), mặc định **Không màu**.
  Bảng 15 màu và Không màu áp dụng cho phần Anh khi xuất cả bốn kiểu;
  giữ lựa chọn gần nhất và dùng thuộc tính tô sáng chuẩn Word. Màu này
  độc lập với dấu xanh báo vùng đã chọn trong bản gốc.
- Ô phông mặc định hiện **Font gốc**, tooltip **Font**, luôn cho chọn trực
  tiếp phông khác; không có ô tích riêng. Chọn **Font gốc** trong danh sách
  để trở về tự động; từng vùng vẫn giữ phông riêng khi xuất. Lựa chọn gần nhất
  được nhớ cho bài mới, tài liệu cũ vẫn giữ cấu hình đã lưu.
- **Bôi đen văn bản** đứng trước. **Tích chọn đoạn/câu** có hai ô vuông con
  **Theo đoạn / Theo câu**, chỉ bật khi chọn cách tích chọn. Hai ô loại trừ
  nhau để mỗi lần chỉ dùng một cách chia nội dung.
  Thanh thao tác dùng hai hàng gọn: cách chọn và Đoạn/Câu ở hàng đầu;
  Chọn tất cả/Bỏ chọn và thu phóng ở hàng sau. Hướng dẫn chuyển vào tooltip.
  Nhả chuột hiện hai nút nhỏ **Chọn / Hủy**, không trích lại nội dung.
  Chọn bằng bàn phím rồi Enter cũng mở khung xác nhận.
- Những vùng đã xác nhận giữ nền xanh nhạt trong bản gốc. Quét lại phần
  đã chọn hiện **Bỏ chọn**; quét phần cũ lẫn mới thì thêm phần mới và gộp
  phần trùng. Thứ tự xuất luôn theo tài liệu, kể cả chọn đoạn cuối trước.
  Dấu nền chỉ thuộc bộ hiển thị, không ghi vào HTML/DOCX hoặc đổi kiểu chữ.
- Các đoạn liền nhau gộp thành một vùng bên phải, giữ xuống dòng; chọn nối
  tiếp sẽ mở rộng vùng đó. Bấm tiêu đề hoặc nội dung vùng để xem đúng vị trí
  trong bản gốc. Ranh giới chỉnh sửa Word được giữ riêng bên trong để tránh
  xáo trộn bảng, ảnh và công thức khi xuất.
- **Dịch toàn bộ** ở bên phải khung tên tệp, mặc định bỏ tích với bài mới.
  Khi bật, mọi phần chữ có thể chỉnh sửa được chọn; khóa cách chọn riêng,
  bỏ vùng và bôi đen. Bấm **Chuyển đổi bài giảng** mới bắt đầu dịch theo
  cấu hình hiện tại. Hình/công thức và phần khóa vẫn giữ nguyên.
  Bỏ tích để trở về các vùng chọn thủ công trước đó; không tự gửi dịch.
- Danh sách font được lấy một lần và truyền sang QML dưới dạng bản sao,
  tránh đọc lại hàng nghìn lần khi chọn phông. Thêm vùng dùng tài liệu đang
  hiển thị để đối chiếu vị trí, không dựng lại bản Qt thứ hai; cập nhật vùng
  không đọc lại gói DOCX để trả toàn bộ đoạn hoặc thử kết nối dịch vụ.
- Bỏ hai dòng hướng dẫn lặp phía trên tài liệu. Chỉ hiện thông báo khi có
  lỗi cần xử lý, bản xem cần dùng chữ thuần hoặc tác vụ đang dừng/tạm dừng.
- **Chọn bài khác / × Hủy bài đang chọn** ở bên phải dòng hướng dẫn,
  ngay trên bài đã chọn, thống nhất ở Word, PowerPoint và Tạo giọng đọc.
  Bỏ nút **Chọn vùng dịch** trong khung tệp.
  Hủy chỉ đưa màn Word về trạng thái chưa chọn tệp; bài/checkpoint trong
  thư viện và các file vẫn còn. Nếu có chỉnh sửa bản dịch chưa lưu thì
  ứng dụng giữ bài lại và nhắc lưu trước khi đổi/hủy.
- Bản xem trên nền giấy trắng có lề, cỡ chữ, phông, đậm/nghiêng, căn đoạn,
  hình nhúng và bảng. Có **− / 100% / +** để đọc và chọn vùng. 100% là mức
  vừa chiều ngang khung ban đầu; nút −/+ đổi từng 10%, bấm giữa về 100%. Ở cách
  tích chọn, từng phần cũng dùng định dạng gốc thay vì chỉ hiện chữ thuần.
  Thanh cuộn của danh sách đoạn/câu luôn hiện khi có nội dung tràn khung.
  Chuyển sang bôi đen tự vừa chiều ngang, kể cả phóng lớn trang gốc khi
  khung rộng hơn trang; lề ngoài khớp với các thẻ ở cách tích chọn.
- Cuộn đến vùng tài liệu sẽ dành gần hết chiều cao cho hai khung gốc và
  bản dịch; phần tải/cấu hình nằm phía trên và cuộn khỏi vùng nhìn.
  Lăn chuột trên tài liệu đưa khung vào đủ tầm nhìn trước rồi mới cuộn
  chữ bên trong. Lăn ngược ở đầu tài liệu để trở lại phần cấu hình.
  Thanh cấu hình đã chọn và nút chuyển đổi vẫn ở dưới, không cuộn đi.
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
