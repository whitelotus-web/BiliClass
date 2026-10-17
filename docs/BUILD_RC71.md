# RC71 — Tự phân loại lời đọc và tiếp tục lưu bài an toàn

Ngày 17/10/2026. Giữ khung tải PowerPoint đã khôi phục ở RC70 và các tab
Cài đặt. Không thay engine/model giọng hoặc tự bắt đầu tạo giọng khi mở bài.

## Thay đổi

- Nhãn VI/EN áp dụng cho cả các dòng tiếp theo, kể cả tiêu đề ngắn và công
  thức; một dòng chưa rõ ngôn ngữ không làm mất cả cặp. Khi mở bài tạo
  giọng, tự rà lại các trường cũ bị gộp Việt–Anh. Bài chỉ có tiếng Việt
  vẫn là tiếng Việt; không tự tạo bản dịch không có trong nguồn.
- Lời đọc bổ sung của bài đã chuyển đổi lưu riêng, không sửa chữ/ảnh trong
  PowerPoint hoặc làm sai chữ ký kiểm chứng nội dung slide. Dùng cùng lời
  đọc hiệu lực cho kế hoạch tạo giọng, nghe thử, ZIP, loa nhúng và Mascot.
  Giữ dữ liệu đọc theo hiệu ứng gốc; sửa lời Anh thủ công của một trang chỉ
  thay kịch bản trang đó. Bản giọng cũ được giữ; nội dung đã đổi báo cần
  cập nhật và tái dùng các WAV còn khớp.
- **Thao tác khác → Kiểm tra / sửa lời đọc** sửa được trực tiếp cả bài
  chuyển đổi và bài nhập riêng. Cảnh báo ghi rõ thiếu lời Việt/Anh, mở đúng
  trang cần bổ sung. Không bắt người dùng chuyển sang màn chỉnh nội dung.
- Trạng thái radio và tóm tắt thống nhất theo bài/giọng/tốc độ đang chọn:
  chưa chọn bài, chưa có lời đọc, chưa tạo, đang tạo, đã tạo hoặc cần tạo tiếp.
- **Hủy bài đang chọn** bỏ lựa chọn khỏi màn tạo giọng. Khi đang tạo thì
  chờ dừng an toàn rồi bỏ lựa chọn, giữ bài trong thư viện và các WAV đã xong.
- Kiểm dung lượng trước khi tạo công việc Google. Giữ đúng mã lỗi
  `StorageProblem/storage` thay vì bắt nhầm thành lỗi định dạng PowerPoint.
  Lưu điểm tiếp tục sau QA: khi ổ đầy ở bước lưu, lần tiếp theo xác minh
  hash/cấu hình rồi chỉ lưu bản đã kiểm, không dịch hay dàn trang lại.

## Kiểm chứng

- 116 tình huống unit liên quan đã kiểm theo nhóm: tách lời, lời đọc của
  bài cũ, sửa script, chữ ký slide, cache/bản giọng, ZIP/loa nhúng, Mascot,
  đầu vào, tiến trình, thiếu dung lượng và tiếp tục từ bản đã kiểm, đóng
  gói, chuyển thư viện. Ca điểm tiếp tục xác nhận chỉ một lượt transport
  giả lập và một lượt QA cho hai lần chạy có lỗi lưu ở giữa.
- Qt workspace thật kiểm cấu hình trước/sau chọn bài ở 1080×700/1366×850,
  sửa lời ngay trên bài chuyển đổi, trạng thái, hủy khi rảnh/đang tạo, tạo
  tiếp từ cache và tải ZIP/PowerPoint; không có cảnh báo QML. WAV kiểm thử
  là fixture, không dùng để đánh giá phát âm của model.
- Bộ unit native Office có chẩn đoán RPC disconnected như các mốc trước;
  fallback hoàn thành. Không dùng kết quả này để chứng nhận bố cục mọi tệp.
- Kiểm đọc dữ liệu Bài 5 cũ: nhận diện Anh từ 17 lên 69/70 slide, giữ 69
  slide Việt và trang không có lời. Tiếng Anh native đã có ở 69 slide;
  lỗi nằm ở nhận diện trường lời đọc, không phải phần dịch bị mất.

## Vận hành trên máy này

Lỗi 98% của bài đang dở là `StorageProblem` ở `Library.store_source`, khi
ổ C chỉ còn khoảng 100 MB và tệp kết quả gần 100 MB. Bản PowerPoint đã tạo
và dữ liệu kiểm tra vẫn còn. Người dùng đã đồng ý chuyển toàn bộ thư viện
sang `F:/BiliClassData`; sao chép/xác minh bằng luồng chuyển thư viện có
sẵn, chỉ dọn tệp cũ khớp hash sau khi mở thư viện đích thành công.

Thông tin chuyển, khôi phục bài và gói cài sẽ bổ sung sau kiểm bản cuối.
