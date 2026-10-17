# RC63 — Kiểm tra bài giảng và Google Dịch gọn hơn, 17/10/2026

[GitHub Release RC63](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc63).

- Nguồn: `53228435f3551125cb9e6955f980110d3bba3fe9`.
- ZIP: `BiliClass-RC63-Windows.zip`, 837284272 byte, 4168 tệp.
- ZIP SHA-256: `dd24a1ed9f5494d332a6e682c39d90e091b506f8fdbe90caaac8f4bc7f34adaf`.
- EXE SHA-256: `5203f32d84ea68163c53155233f62d3e8fa2de445cde7f0d107e76c71e6905c8`.

## Nhãn và cách xử lý bài giảng

Thay nhãn chung bằng **N slide cần sửa**, **Chờ xác nhận**, **Chưa dịch đủ**,
**Đã duyệt nội dung** hoặc **Sẵn sàng dạy**. Bấm nhãn mở đúng bài và cửa sổ
giải thích; thao tác này không chọn/bỏ chọn bài trong thư viện.

Cửa sổ hiển thị kết quả kiểm tra kỹ thuật hiện có, cho kiểm tra lại hoặc
**Tự sửa và kiểm tra** bằng bộ sửa PowerPoint đã có. Có lối mở chỉnh sửa
nội dung, tạo bản xem trước nếu thiếu và mở bước xác nhận cả bài để dạy.
Còn lỗi kỹ thuật hoặc thiếu nội dung thì chưa cho xác nhận.

**Chờ xác nhận** nghĩa là nội dung chưa được thầy cô duyệt, không phải tác
vụ đang chạy. Tự sửa kỹ thuật không tự duyệt ý nghĩa bản dịch; bước xác
nhận của thầy cô vẫn cần thực hiện rõ ràng. Không chạy sửa hàng loạt trên
thư viện cá nhân khi cài hoặc mở ứng dụng.

## Google Dịch

Sau khi lưu key, thu gọn ô nhập; dùng **Thêm key** để mở lại. Đưa hướng dẫn
dài, giới hạn và OCR vào **Hướng dẫn & nâng cao**. Giữ nguyên các tab Cài
đặt và các nút đồng bộ cấu hình riêng hiện có.

Tóm tắt mức dùng ghi số key, số nhóm và tổng giới hạn cục bộ theo nhóm.
Hai key chưa khai báo dự án vẫn dùng một nhóm lịch sử, không cộng cùng
một lượng đã dùng hai lần. Chỉ các nhóm đã tách mới có giới hạn cục bộ
riêng. Lưu lại giới hạn không xóa key hoặc đặt lại bộ đếm.

Số này không phải số dư Google Cloud. Gmail riêng chưa chứng minh quyền
hưởng ưu đãi riêng: key gắn yêu cầu với dự án để tính mức dùng/chi phí;
phải kiểm tra dự án và Billing để biết cấu hình thực tế. Không tự nhân
mức miễn phí hoặc đoán lại lịch sử dùng từng key. Xem
[xác thực Google Translation](https://docs.cloud.google.com/translate/docs/authentication)
và [bảng giá chính thức](https://cloud.google.com/products/translate/pricing).

## Kiểm chứng nguồn

56 kiểm thử liên quan qua bằng virtual environment của dự án: trạng thái
duyệt, tổng mức dùng theo nhóm, Google Translation, đồng bộ key, thư viện,
sửa slide, quy trình dạy và metadata bộ cài. Ruff cho mã ứng dụng và các
tệp Python mới không lỗi. Không chạy lại toàn bộ suite hoặc suy luận model
vì runtime/model không thay đổi.

Qt thật kiểm tra bấm nhãn, định tuyến kiểm tra/sửa, chặn xác nhận khi còn
lỗi và giữ bước duyệt chủ động của thầy cô. Phần định tuyến sửa dùng dữ
liệu lỗi mô phỏng và slot thay thế, không thay cho kiểm chứng sửa slide
PowerPoint thực; bộ sửa được kiểm tra riêng bằng các kiểm thử liên quan.

Qt Google Dịch kiểm tra hai key dùng chung một giới hạn, thu gọn hướng dẫn,
lưu giới hạn không xóa lịch sử, bố cục 1080/1366. Luồng chuyển đổi dùng
PowerPoint thật và phản hồi API mô phỏng, không tiêu hạn mức Google thật.
Các lượt Qt khác kiểm tra Trang chủ ba kích thước, ảnh bìa PowerPoint,
chọn bằng nền/thẻ/nút, danh sách/thẻ/cache và quản lý 24 bài qua nhiều
trang, lọc, tải, thùng rác, khôi phục/xóa và lối vào lớp/báo cáo/thuật ngữ.
Không có cảnh báo QML trong các lượt kiểm tra.

## Đóng gói

Biên dịch lại 114 module ứng dụng một lần; giữ runtime/model từ
[RC62](BUILD_RC62.md), nền tảng đã kiểm chứng tại [RC58](BUILD_RC58.md).
Kiểm SHA-256 và CRC của toàn bộ 4168 tệp trong ZIP. Bộ cài kiểm manifest
khi cài; ba tệp QML thay đổi đã đối chiếu khớp nguồn sau khi cài.

Bản EXE đã cài qua bảy cấu hình Qt bằng dữ liệu riêng: danh sách 1080,
thẻ 1366, Cài đặt 1366, chuyển đổi 1080, Trang chủ 1080 và Google Dịch ở
1080/1366. Không truyền đường dẫn Python nguồn vào EXE; không có cảnh báo
QML. Dữ liệu key trong kiểm thử là giả, tách khỏi dữ liệu thật.

Cài tại `F:/Applications/BiliClass/1.0.0rc63`, đóng RC62 bình thường và mở
RC63 vào Thư viện bằng Explorer. Ứng dụng chạy độc lập với launcher, qua
mười lượt kiểm tra phản hồi; shortcut Desktop/Start menu trỏ RC63.
Đối chiếu trước/sau xác nhận nội dung DB bài giảng, 1092 WAV, cấu hình,
key mã hóa, tên key và lịch sử mức dùng không đổi. Tác vụ giọng đã hoàn
thành 354/354 đoạn không tự chạy lại.

Gói ZIP và checksum đã tải lên GitHub, kiểm digest/dung lượng phía máy chủ.
Cơ chế chọn phiên bản hiện tại, với đầu vào RC34/RC62, nhận metadata công
khai RC63 đúng dung lượng/SHA-256; RC63 không tự báo cập nhật chính nó.
Đây là kiểm tra bộ chọn phiên bản hiện tại với metadata công khai, chưa
phải thử cài trên máy thứ hai. Tải ZIP, giải nén toàn bộ rồi chạy
**Setup.cmd**, hoặc kiểm tra cập nhật trong **Cài đặt → Thông tin BiliClass**.

Thư viện cá nhân, phản hồi học sinh, key, model, EXE và dữ liệu kiểm thử
không nằm trong commit nguồn. Dữ liệu người dùng vẫn ở
`%LOCALAPPDATA%/BiliClass`; giữ các bản cài cũ.
