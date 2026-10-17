# RC64 — Thanh cuộn đồng bộ và hình tải PowerPoint, 17/10/2026

[GitHub Release RC64](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc64).

- Nguồn: `6b658ffe77fe105795a177c59db94bdf89e796ef`.
- ZIP: `BiliClass-RC64-Windows.zip`, 837926742 byte, 4171 tệp.
- ZIP SHA-256: `6079b444053dbdc2bfade7126d723cc6c8969b552c9a7a7c3dcc9aef877f95b5`.
- EXE SHA-256: `2784ad26023396c5baf39a3782de0a8159b1b6c790cfedd0bf58b19c6fb7d911`.

## Giao diện

Chuyển các ScrollView sang hai thành phần dùng chung: `ContentScrollView`
quản lý vùng chừa và `SlimScrollBar` hiển thị thanh mảnh. Trang chủ, Thư
viện, Chuyển đổi, tiến trình, kết quả, Cài đặt, Lớp học, Báo cáo và kho thuật
ngữ/kiến thức dùng cùng cách hiển thị. Phần thanh thấy được rộng 6 px,
bo tròn, màu dịu; vùng chuột rộng 18 px để dễ kéo.

Thanh của trang nằm ngoài mép nội dung 6 px. Chỉ cắt vùng xem nội dung,
không cắt cả điều khiển; thanh không trở thành một phần tử mới trong
ColumnLayout. Vì vậy trang Cài đặt/Báo cáo giữ bố cục, thanh không che ô
chọn hoặc tràn xuống khu vực nút cố định dưới màn Chuyển đổi.

Khung nhập/xem dài trong biên tập, trợ giảng, hộp hướng dẫn, kiểm tra và
thùng rác chừa dải 24 px bên phải. Thanh ngang, khi cần cho nội dung không
xuống dòng, có dải riêng phía dưới. Thanh tự ẩn khi nội dung vừa khung và
không làm thay đổi chiều rộng khi ẩn/hiện. Giữ kéo thanh, con lăn và việc
đưa con trỏ đến cuối nội dung dài.

Khung tải lên ở trang Chuyển đổi có hình PowerPoint do người dùng cung cấp
ở bên trái. Giữ nguyên tệp PNG có nền trong suốt, chỉ giới hạn vùng hiển
thị để bỏ lề trong suốt; giữ tỷ lệ hình. Hình cân theo chiều dọc với phần
hướng dẫn/nút và giảm kích thước ở cửa sổ nhỏ. Nút chọn file cân giữa với
phần chữ bên phải. Tên tệp dài vẫn thu gọn; kéo thả và giới hạn 200 MB giữ
nguyên. Khung tải ở Trang chủ giữ cách bố trí hiện có.

## Kiểm chứng nguồn

17 kiểm thử `test_library_view.py`, `test_library_bulk.py` và
`test_release_package.py` qua bằng virtual environment của dự án. Ruff
cho `app`, `biliclass_m0` và script kiểm tra cuộn mới không lỗi.

Qt thật kiểm tra tám màn ở 1080×700, 1366×850 và 1680×960: khoảng cách thanh
với nội dung, thanh của trang ẩn không còn hiển thị, không đổi chiều rộng
khi lọc hết bài và thanh Chuyển đổi không chạm nút dưới. Dùng chuột thật
kéo thanh/lăn trên Chuyển đổi, Thư viện và khung nhập dài. Kiểm tra con trỏ
ở cuối văn bản, vùng thanh ngang của nội dung không xuống dòng và việc
dùng chung thanh khi chuyển tab Cài đặt.

Các luồng Qt liên quan kiểm tra ảnh bìa PowerPoint thật, chọn bài/nút/thẻ,
cache; quản lý 24 bài qua nhiều trang, lọc, tải và thùng rác; lối vào lớp,
báo cáo, thuật ngữ; xác nhận/sửa bài; xem trước, giọng và mascot; Trang chủ
ba kích thước. Sau khi thêm hình, kiểm tra lại cuộn và luồng tải lên/Trang
chủ, gồm chọn/đổi file, kéo thả và chặn file quá lớn. Xem ảnh chụp ở 1080
và 1366 để đối chiếu cân hình/chữ. Không có cảnh báo QML trong các lượt qua.

## Đóng gói

Biên dịch 114 module Python ứng dụng một lần. Phần hình và QML không đổi
mã Python; đối chiếu Git xác nhận mã Python trong gói khớp commit nguồn
nêu trên. Sao chép QML và hình riêng, không ghi đè các hardlink runtime cũ.
Giữ runtime/model từ [RC63](BUILD_RC63.md), nền tảng đã kiểm chứng ở
[RC58](BUILD_RC58.md); không chạy lại toàn bộ suite hoặc suy luận model
cho thay đổi giao diện này.

Kiểm SHA-256/CRC toàn bộ 4171 tệp trong ZIP. Tệp hình đóng gói giữ nguyên
SHA-256 `7c66bbc68bc11fdea955583d23fe83e4282f01b95dea13121496da2041e4419b`
của hình đầu vào. Dữ liệu cá nhân, key, bài giảng, phản hồi học sinh, model,
EXE và dữ liệu kiểm thử không nằm trong commit nguồn.

Bản cài kiểm manifest và qua 13 cấu hình Qt bằng dữ liệu riêng: danh
sách/thẻ, Cài đặt, chuyển đổi hai kích thước, Trang chủ, Google Dịch hai
kích thước, biên tập, kết quả, Lớp học, Báo cáo và thuật ngữ. Không truyền
đường dẫn Python nguồn vào EXE; không có cảnh báo QML. Đối chiếu toàn bộ
QML đã cài và hình khớp nguồn.

Cài tại `F:/Applications/BiliClass/1.0.0rc64`, đóng RC63 bình thường, mở
RC64 vào Chuyển đổi bằng Explorer. Ứng dụng vẫn chạy sau khi launcher đóng
và qua mười lượt kiểm tra phản hồi. Shortcut Desktop/Start menu trỏ RC64.
Đối chiếu trước/sau: bài giảng, 1092 WAV, cấu hình, key mã hóa, tên key và
lịch sử mức dùng không đổi; tác vụ giọng 354/354 không tự chạy lại.

ZIP/checksum đã tải lên GitHub và khớp digest/dung lượng phía máy chủ.
Cơ chế chọn phiên bản hiện tại với đầu vào RC34/RC63 nhận metadata công
khai RC64 đúng dung lượng/SHA-256; RC64 không tự báo cập nhật chính nó.
Chưa thử cài trên máy thứ hai. Tải ZIP, giải nén toàn bộ rồi chạy
**Setup.cmd**, hoặc kiểm tra cập nhật trong **Cài đặt → Thông tin BiliClass**.
