# RC80 — Cấu hình trực quan và lời đọc tách khỏi chữ trong ảnh

Gồm toàn bộ [RC78](BUILD_RC78.md), [RC79](BUILD_RC79.md), thêm:

- Thư viện gộp Mở bài/Dạy thành **Mở PowerPoint** ở cả danh sách và thẻ.
  Mở trực tiếp và gắn Mascot, đổi bài thì đóng riêng helper phiên trước
  rồi gắn bài mới; không bật F5 hay tự duyệt nội dung. Bộ chọn bài/file
  trên Mascot dùng cùng luồng. Đổi tên/thông tin chuyển vào menu phụ,
  không còn nút Sửa dễ hiểu nhầm là trình sửa slide.
- Bảng Mascot có bánh răng vào đúng tab Mascot, trợ giúp phím thu nhỏ;
  nút chọn bài/F5/tiến lùi/loa ưu tiên ở trên, hai bên cùng lề. Ba cỡ
  bảng độc lập với nhân vật, giới hạn theo màn hình; ẩn nhãn môn dưới
  nhân vật nổi, vẫn giữ phụ kiện và môn trong bảng. Nền mặc định đặc,
  cho trong 0–70%, chỉ alpha nền; chữ/nút/vùng bấm không giảm opacity.
  Hai thiết lập bảng tự lưu riêng, không đổi phiên dạy.
- Chỉ hiện loa có giọng; cùng nút phát/tạm dừng/đọc tiếp, bỏ bộ nút dừng,
  tạm dừng và đọc lại riêng. Tiến/lùi bằng chuột đi qua hiệu ứng như phím
  mũi tên. Quan sát native pause/resume để đồng bộ trạng thái Mascot;
  bấm loa khác dừng cả player đang pause. Chuyển ngôn ngữ trong lúc chờ
  cache giữ yêu cầu mới nhất; bản hai loa cũ đọc chung bằng WAV có sẵn,
  chờ xác nhận dừng native trước phát cache, không tạo thêm giọng.
- Bài cũ có FAIL được thử hoàn thiện cục bộ trước mở/tải, tối đa ba
  lượt, kiểm bằng Office và chỉ nhận bản cải thiện; có dấu phiên bản/hash
  tránh lặp lại khi không tiến triển. Kiểm revision/toàn bộ metadata trước
  ghi, giữ nguồn và lịch sử; hủy không nhận bản đang làm. Không tự xác
  nhận nội dung. Nhãn ngắn **Cần xem lại bố cục**, số slide/chi tiết vẫn có
  trong tooltip/báo cáo. Còn lỗi sau tự căn thì thông báo khi mở/tải.
- Giữ WAV khi sửa bố cục chỉ nếu signature cũ còn đúng, lời đọc theo từng
  ngôn ngữ và các audio key tính lại giống hệt; cập nhật identity bản
  giọng theo nguồn mới. Thay lời/OCR không được nhận lại giọng cũ.
- Cấu hình đã chọn nằm trong khung trắng Cấu hình bài giảng.
- Ba thẻ mẫu có PNG render từ chính bộ PowerPoint đi kèm; chọn trực tiếp
  và xem mẫu. Bỏ lựa chọn mẫu ngoài/role dialog khỏi luồng tạo mới; cấu
  hình mẫu ngoài cũ không áp dụng ngầm cho bài mới hay xem mẫu mới.
- Vị trí loa cùng hàng với ngôn ngữ; mô phỏng trái/giữa/phải, tooltip
  người đọc/tốc độ/giải thích chi tiết. Tóm tắt cấu hình ngắn hơn.
- Trang chủ chào đúng tên hồ sơ, mặc định Thầy cô khi trống; cập nhật
  sau lưu, hiển thị tên dưới dạng chữ thuần và giới hạn chiều cao.
- Khung dịch từ ảnh có dấu nguồn; native speech bỏ đúng khung đó.
  Ghi chú OCR nối cuối được tách khỏi lời đọc, không xóa câu giống nhau
  trong nội dung chính. Với mẫu Universal, giữ dấu theo từng đoạn và
  không đưa phần OCR vào ghi chú đọc; vẫn hiển thị chữ dịch.
- Nhận lại dấu khung dịch ảnh của bài cũ, cập nhật metadata narration
  mà không sửa PPTX hay nội dung bài. Signature đổi nên WAV chứa OCR
  không còn được coi là bản giọng hiện hành. Lời sửa thủ công được giữ.
- EXE có VERSIONINFO: tên/mô tả BiliClass, tác giả/bản quyền Nguyễn
  Diệu Linh, tên tệp và phiên bản. Nguồn phiên bản lấy từ pyproject;
  Windows dùng 1.0.0.80 cho RC80 và chuỗi sản phẩm 1.0.0rc80. Không lấy
  tác giả từ hồ sơ giáo viên. Luồng build đầy đủ và build từ runtime
  đều nhúng cùng resource; không cần cài thêm gì để xem Properties.

## Kiểm chứng

70 ca speech/ảnh/nhập voice/giọng/workspace đạt trước ca template bổ sung.
Ca hồi quy giữ ảnh và nội dung, bỏ đúng OCR, giữ câu trùng trong body,
giữ lời thủ công, stale signature, nhận PPTX cũ. Ca template kiểm chữ
vẫn hiện nhưng vắng khỏi tiếng Anh và ghi chú lời Việt. Resource Windows
kiểm byte Unicode, tác giả và số phiên bản.

914 ca core đạt, một warning dependency Starlette/httpx; 53 ca liên quan
đạt sau các chỉnh cuối về phát loa/cache và nhãn trạng thái. 15 luồng Qt
Windows đạt, gồm bảng Mascot ở ba cỡ, click nền 100%/30%, bánh răng giữ
liên kết bài, không nhãn môn dưới nhân vật và không cảnh báo QML. Luồng
Office thật kiểm nút mở thư viện, chọn/đổi bài từ Mascot, F5 chủ động,
native pause/resume bằng cùng nút ngôn ngữ, đổi loa nhanh, bỏ lệnh slide
cũ và giữ nguồn. Export native, tám corpus và parent-exit đạt.

Sau đổi nhãn Chờ xác nhận thành Đã lưu bài, chạy lại Qt review/usage và
lint đạt. Việc mở PowerPoint không duyệt thay nội dung cho câu hỏi/lớp.
Một bài thật 51 slide đã được nhận bản căn khung công thức đã kiểm chứng:
1 FAIL về 0 FAIL, 51 CHECK; công thức, bản nguồn cũ và lịch sử được giữ.
Đối chiếu riêng thư viện/WAV/key mã hóa trước–sau chỉ có đúng bản sửa
được yêu cầu thay đổi; không đưa dữ liệu/báo cáo cá nhân vào Git.

Nhóm Browser
AI/Translation giữ kết quả RC78 (104/14, một fixture điều hướng phải
chạy lại); không tính là lượt mới cho RC80. Commit/gói/cài đặt được bổ
sung sau kiểm chứng. RC78/RC79
được tạo như các mốc nội bộ trong khi nhận thêm góp ý, không phát hành
riêng. Giới hạn field test/chuột loa độc lập vẫn như BUILD_RC77.
