# RC66 — Giọng đọc độc lập và Tổng quan bài giảng, 17/10/2026

[GitHub Release RC66](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc66).

- Nguồn: `fb22679dcc760bb4d3c998dab8eea292611de402`.
- ZIP: `BiliClass-RC66-Windows.zip`, 840058019 byte, 4185 tệp.
- ZIP SHA-256: `9945f1b680000e348fdbddbadce9a6e8f81ce324995c4859f8eee65ec120e3b1`.
- EXE SHA-256: `ccb6e4af99c29e4488997435fc3d784c0bea5cb8ff9271896cfc3521c8e3bc6f`.

## Trang chủ và icon

Tab tạo giọng dùng cùng `navigation/voice.png` và `voice-active.png` với
Cài đặt → Giọng đọc. Tất cả icon thanh bên có khung 29 × 29 px, nguồn ảnh
64 px, không còn cắt icon tím của phần quy trình.

Trang chủ thay cụm tiếp tục chuẩn bị, ba số đếm rời và bảng sức khỏe/mức
dùng dịch bằng **Tổng quan bài giảng**. Bốn ô hiển thị tổng bài, sẵn sàng
dạy, đã có ít nhất một bản giọng và cần hoàn thiện. Hai số giọng và duyệt
nội dung độc lập; không phải các nhóm cộng lại thành tổng. Cần hoàn thiện
là tổng bài trừ bài sẵn sàng dạy. Dữ liệu lấy từ catalog đang dùng, không
quét WAV thêm trên giao diện. Bên dưới có ba bài vừa cập nhật, tên/môn/khối/
số slide và nút mở cả dòng; không lặp lại danh sách đầy đủ hoặc nút xóa ở
Trang chủ. Có trạng thái thư viện trống và lối vào Thư viện. Giữ hero,
mascot lớn và Quy trình đơn giản. Tiến độ chỉ hiện khi có tác vụ đang chạy;
tác vụ giọng dẫn về tab tạo giọng, chuyển đổi dẫn về màn chuyển đổi.

## Tạo giọng độc lập

Chọn bài thư viện chuẩn bị đúng preview, kể cả bài văn bản cũ đã đủ Việt–Anh;
không tự sửa thiết kế khi chọn bài vào luồng tạo giọng. PowerPoint nhập
riêng giữ nguyên byte nguồn, dùng lời đọc theo slide, nhận ghi chú có nhãn
VI/EN kể cả chỉ một ngôn ngữ. Slide ảnh/không có chữ vẫn nhận được để bổ
sung lời thủ công; không tự OCR hoặc dịch. Kiểm SHA-256 nếu file đổi giữa
lúc trích xuất và lưu nguồn.

**Kiểm tra lời đọc** có hai ô Việt/Anh và chọn slide. Với bài nhập riêng để
tạo giọng, lưu lời đọc dưới dạng metadata; không viết lại hình, chữ, hiệu
ứng PowerPoint. Chặn đổi slide khi có thay đổi chưa lưu; đóng ứng dụng khi
còn lời đang sửa giữ hộp sửa để người dùng xử lý. Nội dung sửa có kiểm
revision, bỏ xác nhận/chốt cũ và làm bản giọng cũ cần cập nhật. Nhận lại
cùng file giữ bản sửa và các biến thể giọng. Bài chuyển ngữ trong thư viện
vẫn dùng bộ biên tập nội dung hiện có.

Slide không có lời được báo rõ và bỏ qua khi phát; không dựng lời giả.
Chỉ cho chọn ngôn ngữ đang có, Song ngữ cần ít nhất một phần Việt và Anh.
Xác nhận để dạy chỉ xét các phần có lời của bài nhập tạo giọng; vẫn cần
người dùng xác nhận, không tự duyệt sau khi tạo. Các quy tắc duyệt bài
chuyển ngữ hiện có giữ nguyên. Kiểm tra thiết kế gốc không tự sửa hoặc
ngăn tạo giọng cho bài nhập riêng.

Dùng chung bộ tạo giọng/checkpoint. Dừng thông báo chờ đoạn hiện tại và
giữ WAV; tiếp tục chỉ tạo đoạn thiếu/hỏng. Khóa đổi nguồn, sửa lời và tải
khi đang tạo. Bản đủ khóa tạo trùng, vẫn chọn/tải/dạy. Hiện lỗi bộ giọng/
ổ đĩa cụ thể thay vì chỉ báo cần kiểm tra; lỗi lặp dừng sau ba lần. Màn
riêng thu gọn các phần kết quả chuyển đổi để đưa cấu hình giọng lên trên.

Tải PowerPoint dùng bộ nhúng giọng hiện có. Thêm **Tải audio (.zip)**: WAV
theo slide/ngôn ngữ, file đọc chung Việt–Anh nếu đã chọn, lời đọc UTF-8 và
manifest. Không gọi model khi xuất; kiểm đúng các WAV của biến thể đã chọn,
ghi qua file tạm rồi thay đích, giữ file đích cũ nếu lỗi. ZIP phát thủ công,
không tự đồng bộ hiệu ứng. PowerPoint dày đặc có thể chưa có vùng trống
cho nút loa; có thể dùng ZIP hoặc phát qua BiliClass.

## Kiểm chứng nguồn

89 kiểm thử liên quan qua trong virtual environment: nhập/sửa lời, nguồn
giữ nguyên, revision cũ bị chặn, bản giọng cần cập nhật sau sửa, ghi chú
một ngôn ngữ, slide trống, xác nhận riêng, ZIP/chọn bản giọng và nhúng
PowerPoint; dừng/tiếp tục, cache, thư viện/catalog/chọn nhiều, pack, duyệt
và readiness. Suite liên quan ban đầu 88 kiểm thử qua; kiểm thử lỗi mới
và năm ca workspace chạy lại cùng nhau, nâng tổng ca riêng biệt lên 89.
Ruff cho ứng dụng, script Qt và các tệp kiểm thử mới/sửa trong phạm vi
được kiểm tra không lỗi.

Qt thật với thư viện dùng một lần: nhập slide trống, thêm lời, chặn đổi
slide khi chưa lưu, chọn ngôn ngữ, dừng trong lúc tạo rồi tiếp tục với một
WAV đã cache, khóa tạo trùng và các thao tác xung đột; xuất ZIP cùng
PowerPoint có WAV; chọn bài văn bản cũ chuẩn bị đúng preview. Giọng trong
lượt Qt này dùng WAV fixture, không coi là kiểm chất lượng model.

Các lượt Qt khác kiểm: sáu cấu hình icon hoạt động/chưa chọn và kích thước;
Trang chủ/overview ba kích thước, mở đúng bài và Thư viện, bỏ bảng sức khỏe,
giữ đường vào tiến độ; luồng chuyển thư viện của RC65; kết quả/preview/
mascot/biến thể giọng; kiểm tra và xác nhận bài. Không có cảnh báo QML ở
các lượt qua. Xem ảnh kiểm tra để đối chiếu phần lời đọc và overview.

Chạy model VieNeu CPU ngoại tuyến thật với hai câu ngắn Việt/Anh, không
phát loa: tạo 2/2 đoạn, không lỗi; WAV 48 kHz, 1,28 s và 1,04 s, RMS khác
không. Xuất ZIP và PowerPoint có giọng thành công. Đây là kiểm vận hành
và định dạng/âm lượng mẫu; chưa đánh giá chất lượng phát âm bằng nghe.

## Đóng gói

Biên dịch 120 module ứng dụng một lần. Đối chiếu Python không đổi sau
milestone biên dịch; phần Trang chủ tiếp theo chỉ đổi QML, tài liệu và
script kiểm tra. Runtime/model giữ từ [RC65](BUILD_RC65.md), không tải model
mới. Toàn bộ 4185 tệp trong ZIP kiểm SHA-256/CRC; dữ liệu cá nhân, key,
WAV của người dùng, phản hồi học sinh và dữ liệu kiểm thử không vào commit.

## Bản cài và phát hành

Cài qua manifest tại `F:/Applications/BiliClass/1.0.0rc66`. Đối chiếu SHA-256
toàn bộ QML và hai icon giọng với nguồn. Bảy cấu hình EXE qua: Trang chủ
1366/1080, tạo giọng chưa chọn bài 1366, đã chọn bài có giọng thật 1366/1080,
Thư viện 1080 và Cài đặt 1366. Không truyền đường dẫn Python nguồn vào EXE;
không có cảnh báo QML, ảnh chụp được lưu với dữ liệu kiểm tra cô lập.

Đóng RC65 bình thường và mở RC66 ở Trang chủ qua Explorer. Ứng dụng vẫn
chạy sau khi tiến trình khởi chạy kết thúc và phản hồi qua mười lượt kiểm
tra. Shortcut Desktop/Start trỏ RC66. Đối chiếu trước/sau: 18 bản ghi bài
gồm thùng rác, 1092 WAV, tùy chọn không đổi; checkpoint 354/354 đã xong
không tự chạy lại. Hash key mã hóa, tên key và lịch sử dùng dịch giữ nguyên.
Không chuyển vị trí thư viện cá nhân trong quá trình cài.

ZIP cùng checksum đã phát hành trên GitHub; digest/kích thước phía máy
chủ khớp gói được kiểm tra. Chưa kiểm cài trên máy Windows thứ hai.
Kiểm bộ cập nhật hiện tại với metadata công khai: đầu vào RC34/RC65 nhận
RC66 đúng commit, dung lượng và SHA-256; RC66 không tự báo cập nhật chính nó.
