# Tự hoàn thiện bài giảng theo nội dung

Mục tiêu là tự xử lý nội dung và sửa bố cục, thay vì yêu cầu giáo viên
đọc cảnh báo rồi tự tìm cách khắc phục. Không dùng việc đổi nhãn trạng
thái để thay thế kiểm tra nội dung thực tế.

## Luồng chung

1. Đọc cấu trúc và ảnh của từng trang; giữ liên kết từ mỗi khối tới
   vị trí trong bản gốc. Phân biệt nội dung chỉnh sửa được, công thức,
   bảng, ảnh chứa nội dung và hình minh họa. Giữ các mảnh cùng đề bài,
   đáp án, lời giải trong một nhóm.
2. Nhận dạng chữ trong ảnh bằng OCR local và kiểm tra chéo. Nhận dạng
   một vài nhãn không đồng nghĩa đã đọc được toàn bộ đề bài. Công thức
   và số liệu chưa xác minh phải giữ nguyên hình gốc.
3. Dịch các đơn vị nội dung có nghĩa, giữ liên kết với số liệu/công
   thức. Tạo lời đọc từ nội dung chính đã xác minh; không biến nhãn
   nhỏ trong hình thành tiêu đề hoặc lời giảng.
4. Chọn vùng chứa theo lượng nội dung, tách trang khi cần; giữ nhóm
   liên quan và cỡ chữ đọc được. Không ép mọi dạng bài vào cùng một
   bố cục hay chỉ thu nhỏ toàn bộ ảnh.
5. Dựng ảnh kết quả, so khớp nội dung nguồn, kiểm tra thiếu đoạn,
   số liệu, công thức, thứ tự, tràn khung và cỡ chữ. Sửa có giới hạn,
   dùng lại phần đã đúng, kiểm tra lại trước khi hoàn tất.

Đây là dữ liệu nội dung và vòng kiểm tra chung, không phải bộ luật
riêng cho từng môn hay từng hình thức đề bài.

## Đã thực hiện trong RC100

- OCR cho mẫu mới đọc cả ảnh có hiệu ứng; chế độ giữ thiết kế gốc vẫn
  loại ảnh ẩn theo hiệu ứng để tránh lộ đáp án.
- Bảo toàn vị trí tương đối của ảnh nhỏ trên trang chỉ có ảnh. Nhãn
  lời giải không còn bị xếp riêng xuống góc như hình trang trí.
- Nhãn OCR không được tự nhận làm tiêu đề.
- Ghi nhận phạm vi nội dung ảnh chưa xác minh, phân biệt với ảnh
  không phát hiện chữ. Không tự coi bản đó đã dịch đủ.
- Hoàn tất chuyển đổi hiện ảnh xem trước ngay; mở xem bài không chờ
  chuẩn bị metadata xong mới chuyển trang. Ghi nhớ kết quả kiểm tra
  không có nhãn ảnh để không quét cả PowerPoint lại mỗi lần mở.

## Phần còn phải hoàn thiện

OCR hiện tại vẫn không đọc chắc toàn bộ câu dài, bảng và công thức
trong các bài ghép ảnh. Đợt thử local không đủ tin cậy để hạ điều kiện
xác minh rồi công bố nội dung đã hoàn chỉnh. RC100 chưa có nhận dạng
ngữ nghĩa đầy đủ cho các trang đó, chưa tự tái dựng mọi bài ảnh thành
nội dung song ngữ hoàn chỉnh và chưa chuyển đổi lại thư viện cũ.

Ưu tiên tiếp là OCR theo vùng nội dung, cấu trúc bảng/công thức,
đối chiếu mức bao phủ nguồn–đích và sửa tự động theo kết quả dựng ảnh.
Chỉ sau kiểm chứng trên tập đầu vào đa dạng mới bật sửa tự động cho
bài cũ, với kiểm tra revision và giữ bản trước để khôi phục.
