# RC65 — Tạo giọng độc lập, chuyển thư viện và Trang chủ, 17/10/2026

[GitHub Release RC65](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc65).

- Nguồn: `157028ec7d161697e08086c92edfd701be3fff65`.
- ZIP: `BiliClass-RC65-Windows.zip`, 840039122 byte, 4183 tệp.
- ZIP SHA-256: `7d8144a18327b2a4e94a9704f2b1aa310ecf91a82618040cdbc23dfdc65ca480`.
- EXE SHA-256: `491550717e0dca74552c3cc6323cfa8b6f0fe0eb7f15b2557d61d9850f0141be`.

## Trang chủ và giọng đọc

Bỏ khung tải lên trùng ở Trang chủ. **Quy trình đơn giản** dùng số thứ tự,
icon và mũi tên PNG do người dùng cung cấp; giữ tệp gốc và giới hạn vùng
hiển thị trong QML. Bốn bước là Tải bài giảng, Chuyển ngữ, Nhận bài giảng
mới và Dạy cùng Mascot. Bước đầu mở chọn file ở màn Chuyển đổi. Dải thông
tin bên dưới mô tả đúng hai kiểu chuyển ngữ hiện có, ba phong cách thiết
kế và giọng đọc/mascot; không hứa giữ mọi hiệu ứng khi chưa đối chiếu.

Tab **Tạo giọng đọc bài giảng** nằm sau Chuyển đổi, trước Bài giảng. Chọn
PowerPoint có sẵn hoặc bài trong thư viện; dùng chung màn cấu hình và bộ
xử lý giọng với bước sau chuyển đổi, không sao chép một bộ tạo giọng khác.
Sau chọn bài, phần chọn nguồn thu gọn và phần giọng hiện trước ảnh slide;
có nút mở lại chọn nguồn/xem slide.

Nhập file giữ nguyên byte PowerPoint, nhận diện chữ/ghi chú có nhãn, không
gọi dịch hoặc đổi thiết kế. Chưa có chữ thì báo bổ sung lời đọc; không OCR
ảnh trong bước này. Bài một ngôn ngữ chỉ tạo giọng ngôn ngữ có sẵn. Muốn
Song ngữ phải có cả lời Việt và Anh. Nhận lại đúng file đã nhập dùng lại
bài/các bản giọng cũ. Bản đã tạo đủ vẫn chọn để tải/dạy, khóa tạo trùng.
Xác nhận lời đọc để dạy là thao tác riêng của thầy cô; không tự duyệt hoặc
phát tiếng. Bài nhập để tạo giọng không tự chạy sửa thiết kế khi mở.

## Chuyển thư viện và lưu file

Ứng dụng cài riêng với dữ liệu. Mặc định dữ liệu ở
`%LOCALAPPDATA%/BiliClass`. **Cài đặt → Dữ liệu → Chuyển thư viện sang nơi
khác** chọn thư mục cha, tạo đích `BiliClass-Data` chưa tồn tại; hiện đường
dẫn cụ thể trước khi chuyển. Chặn khi còn tác vụ/giọng/đọc thử/trình chiếu/
lớp học và không trộn/ghi đè thư viện khác.

Sao chép vào vùng tạm ở ổ đích, chụp SQLite nhất quán và kiểm SHA-256 tệp.
Chỉ công bố thư mục hoàn chỉnh, giữ bản nguồn nếu lỗi. Sau khi đóng mọi
kết nối/bộ xử lý, cập nhật phần cuối, đổi các đường dẫn nội bộ trong JSON/
DB sang gốc mới, kiểm DB và lưu lựa chọn vị trí bằng thao tác thay file
nguyên tử. Mở lại ứng dụng để mọi bộ xử lý dùng đúng gốc mới. **Mở thư
viện khác** cũng dùng cách mở lại này.

Lần mở đầu kiểm các tệp đích trước khi mở DB. Chỉ sau khi giao diện thư
viện mới mở thành công mới dọn từng tệp nguồn còn đúng hash đã chuyển.
Tệp nguồn thay đổi bởi tiến trình khác được giữ; không xóa đệ quy thư mục
dữ liệu cũ. Ghi nhận kích hoạt/dọn bằng file nguyên tử để việc dọn bị ngắt
không ngăn DB mới tiếp tục thay đổi bình thường. Cấu hình vị trí nhỏ, log,
runtime phát triển/cập nhật/diagnostics giữ ngoài quá trình chuyển. Nếu ổ
đã chọn mất kết nối, báo đường dẫn cần kết nối lại, không tạo thư viện trống
thay thế. Không tự chuyển thư viện thật trong lúc cài bản nâng cấp.

Tải/xuất/sao lưu gợi ý tên theo bài/bộ bài/bản giọng hoặc ngày sao lưu;
lọc ký tự/tên thiết bị Windows và thêm số nếu tên gợi ý đã tồn tại. Hộp lưu
vẫn cho chọn đường dẫn và xác nhận ghi đè theo Windows. Ghi nhớ thư mục
xuất gần nhất trong thư viện; CSV phân biệt kết quả với từng phản hồi.
Sao lưu thủ công chọn `.bcbackup` ở ngoài thư viện đang mở.

## Kiểm chứng nguồn

86 kiểm thử liên quan qua bằng virtual environment của dự án: chuyển dữ
liệu, đặt tên file, nhập voice, giọng và checkpoint, thư viện/chọn nhiều,
bộ cài, quy trình/duyệt bài, readiness, pack và catalog. Kiểm tra lỗi sao
chép/đích đã tồn tại/đích hỏng/ổ thiếu, giữ bản gốc và không tạo thư viện
trống; đổi đường dẫn JSON/DB, giữ dữ liệu cuối lúc đóng, chỉ dọn đúng tệp
đã đối chiếu. Ruff cho ứng dụng và các tệp Python mới không lỗi.

Qt thật kiểm tra vị trí tab, nhập PowerPoint và giữ byte gốc, chọn ngôn
ngữ, khóa bản đủ, không tự duyệt/đọc; gợi ý tên và nhớ thư mục; nút Dữ liệu,
lỗi chuyển trả giao diện về dùng được, copy thành công yêu cầu thoát. Sau
đóng thử, kiểm hoàn tất/đổi đường dẫn, mở lại DB chứa giọng/key giả và dọn
bản thử cũ. Sự kiện thoát được chặn để kiểm định tuyến; không coi đó là
kiểm tra tự động bấm xuyên qua cả chuỗi khởi động lại tiến trình.

Tạo âm thanh trong lượt Qt này dùng WAV fixture, không phải kiểm tra chất
lượng model. Các lượt Qt khác kiểm tra Trang chủ/icon/bố cục ba kích thước,
thanh cuộn tám màn, quản lý 24 bài/thùng rác/lớp/báo cáo/thuật ngữ, cửa sổ
kiểm tra/xác nhận bài, xem trước/giọng/mascot. Không có cảnh báo QML trong
các lượt qua.

## Đóng gói

Biên dịch 118 module ứng dụng một lần. Mã Python biên dịch khớp commit
nguồn nêu trên; runtime/model giữ từ [RC64](BUILD_RC64.md), nền tảng đã
kiểm chứng ở [RC58](BUILD_RC58.md). Không chạy lại toàn bộ suite hoặc suy
luận model. QML và bộ icon mới được sao chép riêng; không sửa hardlink của
bộ runtime cũ. Toàn bộ 4183 tệp ZIP được kiểm SHA-256/CRC; bộ cài kiểm
manifest khi cài. Dữ liệu cá nhân, API key, phản hồi học sinh, model, EXE
và dữ liệu kiểm thử không nằm trong commit nguồn.

## Kiểm chứng bản cài và phát hành

Bản cài tại `F:/Applications/BiliClass/1.0.0rc65` qua 16 cấu hình Qt với
các màn chính, Trang chủ và màn tạo giọng ở nhiều kích thước. Không có
cảnh báo QML; QML cùng 12 PNG quy trình khớp SHA-256 với nguồn. Các lượt
này dùng dữ liệu cô lập và không nạp mã Python từ checkout.

Thử chuyển thư viện mẫu thực tế từ ổ C sang F, mở EXE đóng gói bằng vị
trí đã nhớ mà không truyền `BILICLASS_DATA`: đọc đúng bài, WAV, tùy chọn và
key giả. Sau thoát kiểm tra, gọi dọn nguồn mẫu thành công. Đây là kiểm tra
khởi động từ vị trí đã lưu; chưa tự động bấm xuyên qua toàn bộ chuỗi chuyển
và khởi động lại trong giao diện.

Đã đóng RC64 bình thường và mở RC65 ở Trang chủ qua Explorer trên máy
hiện tại. Ứng dụng tiếp tục chạy sau khi kết thúc tiến trình khởi chạy,
qua 10 lần kiểm tra phản hồi. Giữ nguyên 17 bản ghi bài gồm cả thùng rác,
1092 WAV, tùy chọn và checkpoint giọng đã hoàn tất 354/354 phần; không tự
chạy lại tạo giọng. Hash key mã hóa, lịch sử dùng dịch và tên key không
đổi. Shortcut Desktop/Start dùng RC65. Thư viện cá nhân vẫn ở vị trí cũ
cho đến khi người dùng chọn nơi chuyển trong Cài đặt.

Đã phát hành `v1.0.0rc65` trên GitHub, kiểm đúng kích thước và digest do
GitHub trả về cho ZIP cùng tệp checksum. Kiểm bộ cập nhật hiện tại với
metadata công khai: phiên bản RC34/RC64 nhận đúng RC65, RC65 không báo cập
nhật lại; đúng commit, dung lượng và SHA-256 nêu trên. Chưa kiểm cài trên
máy Windows thứ hai.
