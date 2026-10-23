# BiliClass 1.0.0rc165

## Lời đọc và kết nối PowerPoint

Đọc số bài ở bên trái trước tiêu đề cùng hàng, dù hai khung chữ lệch nhẹ
theo chiều dọc. Nhãn “Nội dung” bên trái được đọc trước danh sách bên phải,
kể cả danh sách có nhiều khung chữ hoặc nằm trong nhóm. Bỏ các hình trang
trí rỗng khi xác định hàng chữ. Thứ tự xuất/chuyển đổi và ID hình gốc giữ
nguyên; ghi chú và lời đọc giáo viên đã sửa vẫn được ưu tiên.

Bài đã nhập có phiên bản trích xuất cũ được nâng cấp khi chuẩn bị tạo
giọng. Chỉ thay lời đọc tự suy ra nếu tập từ/dấu câu giữ nguyên; không sửa
kịch bản thủ công. Giọng không còn khớp lời đọc mới cần tạo lại. WAV cũ và
PowerPoint nguồn không bị sửa; file đã xuất trước đây cần xuất lại sau khi
tạo giọng mới.

Mỗi lần bấm Mở PowerPoint từ Thư viện, Chuyển đổi hoặc Tạo giọng đều hiện
lại mascot và gắn bài đang mở. Nhận diện cửa sổ hỗ trợ Office ẩn phần mở
rộng và một số dạng tiêu đề không có ngoặc, vẫn từ chối tên bài gần giống
và trường hợp nhiều cửa sổ không xác định được chính xác.

Chuẩn bị loa trên bài dài báo tiến độ theo từng slide. Mốc chờ khởi động
45 giây tính từ tiến độ mới nhất, thay vì tổng thời gian xử lý. Khi thực
sự không tiến triển, thông báo nêu bước bị kẹt và ghi chẩn đoán cục bộ;
chỉ ngắt tiến trình trợ giúp riêng, không kết thúc PowerPoint của người
dùng. Nếu PowerPoint đang có hộp thoại chặn thao tác, cần đóng hộp thoại
rồi mở bài lại.

## Kiểm chứng nguồn trên Windows hiện tại

- 127 kiểm thử lời đọc, nhập bài, PowerPoint, chuyển bài, hoàn thành bài,
  điều khiển và thời gian khởi động đạt. Thêm 55 kiểm thử thứ tự/nhập bài
  đạt sau chỉnh tình huống hình trang trí.
- Qt và PowerPoint desktop thật: cả ba luồng Thư viện, Chuyển đổi và Tạo
  giọng đều khôi phục mascot đã ẩn, gắn đúng bài, theo dõi trình chiếu bắt
  đầu từ PowerPoint, chuyển trước/sau bằng mascot và dừng phiên được.
  Không cảnh báo QML; file nguồn thử giữ nguyên.
- Đối chiếu đọc file PowerPoint trong Downloads ở chế độ chỉ đọc; thử cả
  số bài/tiêu đề lệch hàng và nhãn nội dung đứng giữa danh sách.
- Thêm kiểm thử thứ tự lời đọc, nhận diện PowerPoint và chờ khởi động vào
  Source checks trên GitHub. Dữ liệu cá nhân, model, báo cáo và bản dựng
  tiếp tục nằm ngoài Git.
- 29 kiểm thử installer/package/updater và thời gian khởi động đạt ở
  lượt chốt; Ruff toàn bộ app/scripts/tests và compileall đạt.

Đây là kiểm chứng trên máy hiện tại. Máy nhận vẫn cần thử lại RC165 với
Office và cấu hình màn hình của chính máy đó. Bộ cài RC164 sửa lần 2 chỉ
sửa trình cài đặt, không chứa các thay đổi ứng dụng RC165.
