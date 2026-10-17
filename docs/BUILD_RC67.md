# RC67 — Cấu hình giọng ngay từ đầu và icon bài giảng âm thanh, 17/10/2026

[GitHub Release RC67](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc67).

- Nguồn: `147fa5aec09ace25e1fcd2c374b628963b649b8c`.
- ZIP: `BiliClass-RC67-Windows.zip`, 840256839 byte, 4187 tệp.
- ZIP SHA-256: `e5755f490b33b377e93e6bf9a1efcda8364fdc090b2071d22eef7a6036dd591e`.
- EXE SHA-256: `dd8061f591334f962c054ed4ab01448851ba1aad9770480f5bf7ca7e58793367`.

## Giao diện và vận hành

Ô **Dạy cùng Mascot** trong Quy trình đơn giản trên Trang chủ dẫn thẳng
tới tab **Tạo giọng đọc bài giảng**, không dẫn tới Thư viện. Mở trang không
tự tạo giọng hoặc phát tiếng.

Phần giọng/tốc độ/Anh–Việt–Việt+Anh hiện ngay cả trước khi nhận file.
Thu gọn hình và khoảng cách khung tải trong màn giọng để cả ba lựa chọn
hiện được ở 1080×700; màn Chuyển đổi giữ kích thước khung tải cũ. Có thể
nghe thử giọng và chọn cấu hình trước. Nút tạo bị khóa nếu chưa có bài,
lời đọc phù hợp hoặc tác vụ chưa xong; giải thích hiện ngay trong khung.

Giữ các lựa chọn người dùng đã chỉnh khi nhận PowerPoint, đổi bài thư
viện hoặc bổ sung lời đọc. Với bài một ngôn ngữ, chọn ngôn ngữ đang có;
không tự dịch thêm. Chọn một bản giọng đã lưu nạp cấu hình tương ứng của
bản đó. Các lựa chọn này thuộc phiên cấu hình hiện tại, không ghi đè tùy
chọn giọng chung trong Cài đặt.

Tab dùng PNG thẻ bài giảng có loa do người dùng cung cấp, giữ nguyên byte
và SHA-256 `3dce407cb8593a1eaa2b3f67aa74299585c25b4f791e2a46c504bf29dc4cc034`.
Thành phần NavigationIcon dùng khung 29×29 px; Canvas chỉ giới hạn lề trong
suốt khi vẽ và phủ màu xanh ở trạng thái được chọn. Trạng thái chưa chọn
giữ màu xám của ảnh. Không tạo/sửa ảnh bằng model; không thêm module Qt
hiệu ứng. Các icon khác và icon Giọng đọc của Cài đặt giữ nguyên nguồn.
Canvas vẽ khi ảnh tải xong hoặc trạng thái đổi, không có vòng lặp animation.

## Kiểm chứng nguồn

Ba kiểm thử `test_release_package.py` qua bằng virtual environment. Ruff
cho ứng dụng và hai script Qt sửa trong mốc này không lỗi.

Qt Home kiểm ba kích thước 1080/1366/1680: bấm ô thứ tư mở đúng tab giọng,
sidebar chọn đúng, không tự chạy âm thanh; các luồng chọn file, chuyển
đổi, overview và tiến độ giữ hoạt động.

Qt workspace kiểm cấu hình trước file ở 1080×700 và 1366×850: các lựa chọn
thấy được trong khung cửa sổ và tương tác được, nút tạo vẫn khóa khi chưa
có bài. Chọn Hải Đăng/106%/Việt–Anh rồi nhận file, sửa lời và đổi bài thư
viện vẫn giữ cấu hình; đổi sang bài chỉ có Việt chuyển kiểu đọc phù hợp.
Đo pixel ảnh chụp xác nhận icon mới xanh khi chọn, xám khi bỏ chọn và khung
29 px. Tiếp tục kiểm sửa lời, dừng/tiếp tục với cache, khóa tạo trùng, ZIP
audio và PowerPoint có giọng. Tổng hợp/xử lý âm thanh trong lượt Qt này
dùng WAV fixture, không phải suy luận model.

Các lượt Qt kết quả/preview/mascot và chuyển thư viện liên quan cũng qua;
không có cảnh báo QML. Xem trước ảnh để kiểm tra bố cục cấu hình và icon.

## Đóng gói

Biên dịch 120 module ứng dụng một lần; phần icon bổ sung sau đó chỉ đổi
QML, ảnh và kiểm tra, đối chiếu xác nhận Python không đổi. Engine và model
giữ từ [RC66](BUILD_RC66.md); không chạy lại suy luận model cho thay đổi
giao diện này. Kiểm SHA-256/CRC toàn bộ 4187 tệp ZIP; PNG trong gói giữ
nguyên hash đầu vào. Tài liệu cá nhân, key, giọng của giáo viên, model,
EXE và dữ liệu kiểm thử không vào commit nguồn.

Cài qua manifest tại `F:/Applications/BiliClass/1.0.0rc67`. Tám cấu hình
EXE qua: Home 1366/1080, tab giọng chưa chọn bài 1366/1080, đã chọn bài có
giọng 1366/1080, Thư viện 1080 và Cài đặt 1366. Không có cảnh báo QML;
không truyền đường dẫn Python nguồn vào EXE. Toàn bộ QML và PNG mới trong
bản cài khớp nguồn, PNG mới cũng khớp trực tiếp tệp người dùng đã gửi.

Đóng RC66 bình thường, mở RC67 vào tab tạo giọng qua Explorer; ứng dụng
tiếp tục chạy sau khi tiến trình khởi chạy kết thúc và qua mười lượt kiểm
tra phản hồi. Shortcut Desktop/Start dùng RC67. Đối chiếu trước/sau giữ
nguyên 18 bản ghi bài gồm thùng rác, 1092 WAV, tùy chọn, hash key mã hóa,
tên key và lịch sử mức dùng. Checkpoint 354/354 đã xong không tự chạy lại.

Đã phát hành ZIP và checksum trên GitHub; kích thước/digest phía máy chủ
khớp bản được kiểm tra. Chưa kiểm cài trên máy Windows thứ hai.
Bộ cập nhật hiện tại với metadata công khai chọn đúng RC67 cho đầu vào
RC34/RC66, khớp dung lượng và SHA-256; RC67 không tự báo cập nhật chính nó.
