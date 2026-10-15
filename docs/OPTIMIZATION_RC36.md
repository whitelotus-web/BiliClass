# BiliClass RC36 — nghe thử, nhận diện ứng dụng và dựng slide tại máy

Ngày 15/10/2026. Bản kiểm thử tại máy; chưa thay RC34 trên kênh cập nhật tự động.

## Thay đổi cho người dùng

- **Nghe thử:** đóng sẵn câu “Xin chào các em. Let's learn together.” cho sáu
  preset VieNeu hiện có. Câu mặc định phát từ WAV đã kiểm tra checksum, không
  đợi nạp mô hình hoặc hàng đợi tạo giọng cho bài. Đổi tốc độ dùng WAV này và
  lưu biến thể. Câu tự nhập vẫn được tổng hợp và cache như trước; lần đầu có
  thể cần nạp mô hình. Nút Dừng chặn kết quả phát âm về muộn.
- **Thông tin BiliClass:** thay tab Song ngữ theo yêu cầu; hiển thị logo sách,
  tên ứng dụng, phiên bản thực tế, bản quyền và kiểm tra cập nhật. Bốn kiểu
  chuyển đổi trong màn tạo bài vẫn giữ nguyên.
- **Icon:** bộ SVG/PNG/ICO đa kích thước dùng cho cửa sổ, taskbar và EXE.
  Script cài đặt tạo shortcut Start menu và Desktop có icon của ứng dụng.
  Shortcut cũ ghim trên taskbar có thể vẫn mang icon cache của Windows.

## Chuyển đổi thực sự vận hành thế nào

Với nguồn PPTX giữ thiết kế gốc, ứng dụng trích văn bản theo ID, gửi nhóm JSON
cho ChatGPT dịch, xác minh bản dịch rồi dựng PowerPoint tại máy. Media gốc
không phải truyền theo các nhóm chữ. Slide cần hiểu ảnh, công thức phức tạp,
hiệu ứng hoặc không đủ chỗ vẫn đi qua nhóm PowerPoint trực quan. Đây là luồng
kết hợp, không phải mọi slide đã chuyển hoàn toàn sang JSON.

RC36 tính khả năng chứa chữ ở cỡ đọc được thay vì loại ngay hộp có font gốc
lớn. Chỉ mở rộng xuống khoảng trống không bị đối tượng khác chiếm; căn hai
cột trong vùng chữ. Sau dịch, co chữ có giới hạn, giữ font và nhấn mạnh, không
co chữ mới xuống dưới 18 pt (vùng gốc vốn nhỏ hơn giữ giới hạn gốc). Không áp
dụng phép co mới cho hộp xoay. Giữ nguyên media/theme/master/layout; vẫn render
và kiểm tra tràn/thiếu bản dịch. Manifest mới là v2; tác vụ v1 đang dở không
tự thay cách dàn hoặc tự gửi lại.

Trên nguồn Bài 6 có 79 slide, 76.958.905 byte, phân loại từ đầu cho thấy:

| Kiểu | RC35: slide xử lý chữ local | RC36: slide xử lý chữ local | RC36: slide cần xử lý trực quan |
|---|---:|---:|---:|
| Hai cột | 4 | 20 | 59 |
| Từng câu | — | 23 | 56 |
| Tích hợp từ khóa | 4 | 50 | 29 |
| Tiếng Anh | 2 | 51 | 28 |

Đây là số đo phân loại nguồn, **không phải** nghiệm thu cả 79 slide hoặc thời
gian chuyển đổi trọn bài. Tác vụ đã chuẩn bị từ bản trước vẫn dùng manifest cũ.

## Bằng chứng kiểm tra

- ChatGPT thật: bài mẫu Phân số một slide, hai cột, hoàn tất **29,42 giây** từ
  bắt đầu chuyển đổi đến dựng/kiểm tra kết quả. Một nhóm JSON, không đính kèm
  PPTX, không gửi sửa. Bản ghi xác nhận bật suy luận; kết quả có thân bài Anh
  đủ, tiêu đề Việt trên/Anh nghiêng dưới, không lỗi tràn/thiếu. Còn CHECK về
  rà soát trực quan; không coi đó là xác nhận nội dung mọi môn.
- Office thật: bốn mẫu nhỏ theo bốn kiểu mở và render được, không FAIL; còn
  CHECK rà soát trực quan và một CHECK lời đọc từ khóa. Không ghi đè thư viện
  hoặc bản gốc của giáo viên.
- Chuẩn bị tệp nghe thử mặc định cho sáu giọng: **1–2 ms**; tạo biến thể nhanh
  lần đầu **0,06–0,60 s** trên máy này. Chưa tính độ trễ thiết bị phát âm.
- 65 kiểm thử nhóm JSON/điều phối/chờ/preview qua; 31 kiểm thử native/layout/
  hồi quy qua trước bổ sung chặn hộp xoay. Các nhóm có thể trùng ca, không cộng
  thành tổng độc lập. Qt Settings đủ tám kiểm tra, có phát âm thử thật; Qt
  chuyển đổi/thư viện chín giai đoạn qua, web/voice dùng fixture.
- Kiểm tra đọc trạng thái tài khoản thật hoàn tất khoảng 10 giây. Bộ Chrome
  fixture mới nhất trước sửa khôi phục tab: **19 qua, 6 lỗi**; các lỗi gồm tab
  trống tích lũy khi khôi phục, profile mới chưa tải trang kịp và ca bị chặn
  trước bước gửi. Vì vậy chưa chứng nhận browser ổn định trên mọi lần chạy.
- Sau khi bỏ tạo tab trống dự phòng trong lúc Chrome còn khôi phục, chạy lại
  hai ca browser liên quan và bảy ca bố cục: **8 qua, 1 lỗi**. Ca hai nhóm
  chữ/slide trả về khác thứ tự qua; ca profile/cookie vẫn timeout ở điều hướng
  đầu tiên. Không bỏ assertion, kéo dài vô hạn hoặc công bố bộ browser đạt.

## Giới hạn phát hành

Chưa có benchmark chuyển đổi toàn bộ bài lớn mới và chưa sửa hết bản nháp
Bài 6 cũ còn 17 FAIL / 62 CHECK trong phép thử RC35. Bài mẫu 29 giây không
chứng minh bài 79 slide sẽ xong cùng thời gian. Không thay đổi model/provider,
không vượt xác minh hoặc hạn mức tài khoản, không tự duyệt bài lỗi. Voice vẫn
là bước tùy chọn sau khi có PowerPoint.

Nguồn, tài nguyên logo/mẫu giọng chung và tài liệu vào Git; bài giáo viên,
profile, log, reports, model và EXE không vào Git. Phiên bản/commit và kết quả
kiểm tra bản đóng gói ghi riêng trong BUILD_INFO tại thư mục ứng dụng thử.
