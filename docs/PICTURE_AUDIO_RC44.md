# RC44 — mẫu tiêu đề, OCR ảnh và PowerPoint có voice

Ngày 16/10/2026.

## Đã triển khai

- Sáu ảnh xem mẫu mới được render PowerPoint từ cùng bộ dựng local của app:
  ba theme × Song ngữ/English only. Song ngữ có tiêu đề Việt trên, Anh nhỏ
  hơn/in nghiêng cùng font bên dưới. Script tái tạo:
  `scripts/render_conversion_examples.py`.
- So sánh chiều cao dòng với bản dịch thực trước khi chọn cột hoặc xếp
  dòng ở khung hẹp; giữ quy tắc tiêu đề và công thức dùng chung của RC43.
- OCR hình nhúng chạy trong process riêng, CPU giới hạn, có hủy/timeout
  5 phút và cache từng ảnh. Ảnh trùng/crop giống nhau chỉ nhận diện một lần.
  RapidOCR tìm vùng chữ; VietOCR ONNX kiểm tra độc lập chữ Việt. Chỉ chấp
  nhận khi hai bộ đọc đồng ý phần chữ không dấu và điểm đạt ngưỡng thử nghiệm.
  Không coi điểm OCR là chứng nhận nội dung đúng.
- Song ngữ thêm chữ Anh ở vùng trống gần nhãn, ưu tiên dưới rồi bên phải,
  kiểm tra không đè lên chữ/hình khác. English only dùng hộp nền đặc nới
  nhẹ quanh vùng chữ Việt, lấy màu nền từ ảnh và fit chữ Anh trong vùng đó.
  Ảnh gốc không đổi; lớp che/dịch là đối tượng PowerPoint chỉnh sửa được.
- Bỏ qua công thức nghi vấn, nền phức tạp, ảnh xoay/lật, vùng không đủ chỗ,
  chữ chưa được kiểm tra chéo và ảnh có hiệu ứng chưa xác định chắc.
  Vùng alpha trong suốt không được đoán thành nền đặc. Giữ review riêng;
  không tuyên bố các ảnh còn lại đã đạt English 100%.
- Cài đặt Google Dịch có trạng thái OCR và nút chuẩn bị bộ nhận dạng Latin.
  Bản đầy đủ cần cả gói kiểm tra dấu `ocr-vi-en-v2`; gói này được chuẩn bị
  riêng bằng script build và đi cùng model pack, không tự tải qua nhận diện.
  Bản nguồn thiếu v2 giữ chữ OCR ở trạng thái cần đối chiếu, không tự che.
- Khi giọng đọc đã đủ, màn kết quả có lựa chọn tải PPTX kèm voice (mặc định
  tích). Ghép WAV cache theo slide/ngôn ngữ, nhúng vào ZIP PowerPoint và thêm
  tối đa hai loa VI/EN. Không tổng hợp lại giọng hoặc gửi API ở bước tải.
  Có thể bỏ tích để tải đúng bản không voice đang xem.
- Audio nằm trong file, quan hệ nội bộ, bấm để phát; không tự phát khi vào
  slide. Không sửa nguồn/thư viện. Chọn vùng trống để đặt loa; nếu không có
  chỗ, báo rõ và giữ file tải cũ thay vì ghi đè bằng bản lỗi.
- Chỉ nhúng phần đọc tĩnh đã xác định. Không đưa câu/đáp án ẩn theo click
  vào loa theo slide. Với trang có timing, không nhúng lời Việt từ notes vì
  notes có thể chứa lời giải ẩn. Trợ giảng BiliClass vẫn điều khiển lời đọc
  theo trạng thái trình chiếu. File PPTX độc lập không có mascot/lớp học.

## Kiểm chứng

- 111 ca kiểm tra liên quan đạt; sau bổ sung luồng OCR → Google → lớp chữ
  và chỉnh bố trí đã chạy tập 27 ca (có ca chồng, không cộng tổng).
- Qt Google fixture đạt: một lượt API giả lập, đồng hồ/phần trăm, hai kích
  thước cửa sổ, không mở Browser AI và không cảnh báo QML. Qt kết quả đạt:
  tích/bỏ tích voice cập nhật đúng, xem slide trước voice, worker/cache và
  mascot. API fixture không phải số đo Google thật.
- OCR thật trên ảnh chữ Việt: bộ Latin từng đọc sai dấu; bộ VietOCR đọc
  đúng, kiểm tra chéo chấp nhận và tạo overlay ở cả hai lựa chọn. Đã render
  bằng PowerPoint thật và xem ảnh, chưa gọi Google thật trong ca này.
- Nguồn Bài 3 thật 48 slide: 12 ảnh OCR khác nhau, khoảng 21,4 giây lần
  đầu, 0,67 giây khi cache. Chỉ một dòng được tự chấp nhận, tám thông báo
  cần đối chiếu. Đây là đo OCR; không phải benchmark chuyển cả bài và không
  phải tuyên bố mọi chữ trong ảnh đã được dịch.
- File có hai WAV VieNeu thực đã mở lại và phát bằng media player của
  PowerPoint: vị trí phát tăng, duration hợp lệ, Action=12 (play media).
  Giữ media nội bộ, không cần đường dẫn WAV bên ngoài. Chưa chứng nhận
  tương thích mọi phiên bản Office/Windows hoặc khả năng phát âm mọi môn.
- Bài nguồn RC43 còn một trang tràn chữ; bản nâng cấp này không tự sửa
  hàng loạt bài cũ và không chứng nhận tất cả bài tự hoàn thiện.

File bài, ảnh OCR, WAV, báo cáo, model và EXE nằm ngoài Git. Model ONNX của
VietOCR được build bằng môi trường phát triển; runtime app không cần PyTorch.
