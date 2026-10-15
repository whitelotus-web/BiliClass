# RC43 — nhãn, tiêu đề và công thức dùng chung

Ngày 16/10/2026. Google Dịch vẫn là luồng dịch mặc định; dựng và kiểm tra
PowerPoint tại máy. Không bật lại gửi tài liệu qua Browser AI.

## Thay đổi đã triển khai

- Số La Mã đứng riêng như I/II được xem là nhãn trung lập, không thêm một
  bản dịch trùng bên dưới. Không áp dụng quy tắc này cho cả câu có số mục.
- Công thức độc lập, kể cả biểu thức cos/sin và công thức OMML, dùng chung
  một lần khi xếp Việt trên–Anh dưới. Câu văn chứa công thức vẫn cần dịch;
  không gộp câu văn thành nhãn trung lập. Trong bố cục hai cột, một biểu thức
  nằm trong khung nội dung hỗn hợp có thể còn xuất hiện ở cả hai cột.
- Nhận diện thêm tiêu đề mục ngắn, chữ lớn/in đậm thay vì chỉ dựa vị trí
  hoặc placeholder. Những mục tương đương ở đầu/cuối trang được xếp cùng
  kiểu Việt trên–Anh dưới. Đây là quy tắc bảo thủ, chưa phải hiểu toàn bộ
  bố cục như người thiết kế.
- Khung chữ ngắn trên nền ảnh toàn trang giữ chiều cao nguồn, tránh nới
  hộp chữ ra ngoài dải trang trí đã vẽ trong ảnh. Cỡ chữ được fit trong hộp.
- Đo và sửa thêm khung chữ trong nhóm không xoay. Đổi phiên bản môi trường
  cache để không tái sử dụng kết quả QA cũ bỏ qua khung con trong nhóm.

## Kiểm chứng và giới hạn

- 75 ca kiểm tra liên quan đạt: cùng slide, giữ nguồn qua Google, lời đọc,
  sửa bố cục, xem trước và render cache. Qt smoke đạt: không cảnh báo QML,
  hàng đợi xem trước, thứ tự slide/voice, tên đầy đủ và hành vi mascot.
- Thử trên nguồn Bài 3 thật 48 trang với cache bản dịch đã có, không gửi
  lại Google: 51 trang sau khi chia nội dung dày thành trang tiếp nối.
  Render PowerPoint thật đã xem trang mục và trang công thức. Nhãn II chỉ
  còn một, hai mục cùng kiểu xếp dòng, nhãn Nội dung bài học nằm trong nền
  vàng, công thức độc lập không bị nhân đôi dưới công thức gốc.
- Kiểm tra cấu trúc/cặp dịch không có FAIL. QA hình học toàn bài phát hiện
  **1 trang FAIL về tràn chữ**, 50 trang CHECK; lượt tự sửa không cải thiện
  lỗi còn lại. Không chứng nhận tất cả trang đẹp, nội dung ảnh đã dịch,
  hiệu ứng/đáp án ẩn đã kiểm chứng hoặc bài đã sẵn sàng dạy.
- Bài/ảnh render, cache và báo cáo thật nằm ngoài Git. Không tự sửa hàng
  loạt thư viện giáo viên; bài đã lưu cũ không tự biến thành bản mới.

## OCR và voice độc lập: hướng tiếp theo, chưa tích hợp

Chữ trong ảnh hiện chưa có OCR ở luồng Google. Có thể bổ sung PaddleOCR
PP-OCRv5 Latin (có tiếng Việt) tại máy, lấy hộp chữ và độ tin cậy rồi dịch
những vùng đã nhận chắc. Ưu tiên chú thích/vùng trống và đối chiếu vùng mờ;
không tự xóa trục đồ thị, thay công thức hoặc đoán dữ liệu trong ảnh.

Đề xuất voice mặc định tối đa hai nút Việt/Anh mỗi slide, theo lựa chọn
ngôn ngữ của giáo viên; tránh gắn loa vào từng dòng. BiliClass điều khiển
mascot và lời đọc chi tiết; bản PPTX tải về sẽ cần đóng gói audio thật để
phát độc lập. Hiện nút tải bài **chưa nhúng audio**.

Đã làm mẫu kỹ thuật một trang với hai WAV VieNeu có sẵn, nhúng bằng
PowerPoint AddMediaObject2(LinkToFile=False, SaveWithDocument=True), không
tự phát khi vào trang. Đóng/mở lại PPTX xác nhận hai đối tượng media, thời
lượng hợp lệ, WAV nội bộ đúng hash, không liên kết đến file WAV ngoài.
Đây chưa phải tính năng xuất hoàn chỉnh và chưa thử bấm phát trên máy khác.

Nguồn kỹ thuật:

- [PaddleOCR: các ngôn ngữ PP-OCRv5](https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.html)
- [Microsoft: Shapes.AddMediaObject2](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.shapes.addmediaobject2)
- [Microsoft: PlaySettings.PlayOnEntry](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.playsettings.playonentry)
