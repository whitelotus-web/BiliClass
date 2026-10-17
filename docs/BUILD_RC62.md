# RC62 — Bấm bài giảng để chọn, 17/10/2026

[GitHub Release RC62](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc62).

- Nguồn: `3788bb365fd49ba9eb1a17e06babd81527f6e82c`.
- ZIP: `BiliClass-RC62-Windows.zip`, 837280209 byte, 4168 tệp.
- ZIP SHA-256: `ee1d04e66504c03717bc33c9da6dd0bd9ff5a204e63371a3cb3c05a4392af29f`.
- EXE SHA-256: `78e769345ae1244a15970c9491f6c3c615ffb62309beddfb9e278a46e2d51d30`.

## Hành vi

Ở Thư viện, bấm nền, tên, thông tin hoặc ảnh bìa để chọn/bỏ chọn bài trong
cả dạng danh sách và thẻ. Bài đã chọn có viền xanh và nền xanh nhạt. Ô chọn
vẫn sử dụng được như trước và chỉ đổi trạng thái một lần mỗi lần bấm.

Nút Mở bài/Tải/Sửa/Xóa và menu thực hiện chức năng riêng, không thay đổi
lựa chọn. Kể cả khi nút bị vô hiệu hóa, bấm vùng nút cũng không chọn nhầm
bài. Di chuyển chuột vượt ngưỡng kéo của hệ thống không bị tính thành bấm
chọn; cuộn vẫn hoạt động. Trang chủ không bật cơ chế chọn nhiều bài này.

Bấm ảnh bìa trước đây mở bài, nay chọn/bỏ chọn theo yêu cầu mới; muốn xem
bài dùng nút **Mở bài**. Không thay đổi định dạng hay dữ liệu bài giảng.

## Kiểm chứng nguồn

17 kiểm thử trong `test_library_view.py`, `test_library_bulk.py` và
`test_release_package.py` qua bằng virtual environment của dự án. Ruff cho
`app` và `biliclass_m0` không lỗi.

Qt thật kiểm tra bấm nền/tên/thông tin, checkbox, ảnh bìa, nút Tải/Sửa/Xóa,
menu thẻ, vùng nút bị vô hiệu hóa và kéo chuột. Lựa chọn đồng bộ giữa hai
kiểu xem; nút Mở bài mở đúng bài đang lọc mà không thay đổi danh sách chọn.
Kiểm tra ảnh bìa PowerPoint thật, cache, tỉ lệ 16:9 và bố cục 1080/1366.
Trên Trang chủ, vùng bấm chọn được tắt.

Qt quản lý 24 bài kiểm tra chọn qua nhiều trang, lọc, tải, thùng rác,
khôi phục/xóa và các lối vào lớp/báo cáo/thuật ngữ. Qt ở 1080×700,
1366×850 và 1680×960 xác nhận thanh cuộn riêng, kéo/lăn chuột trên nội dung,
trạng thái tổng/lọc/chọn và không dịch chiều rộng khi thanh ẩn. Không có
cảnh báo QML trong các lượt kiểm tra.

## Bộ cài và cập nhật

Biên dịch lại 113 module app một lần; runtime/model giữ nguyên từ RC61,
nền tảng đã kiểm chứng tại [RC58](BUILD_RC58.md). Không chạy lại toàn bộ
suite hoặc suy luận model cho thay đổi giao diện này. Mỗi tệp trong ZIP
kiểm SHA-256/CRC; bộ cài kiểm manifest khi cài.

Bản EXE đã cài kiểm năm màn Qt bằng dữ liệu riêng: danh sách, thẻ, cài đặt,
chuyển đổi và Trang chủ; không truyền đường dẫn Python nguồn vào EXE.
Cài tại `F:/Applications/BiliClass/1.0.0rc62`, đóng RC61 bình thường và mở
RC62 vào Thư viện bằng Explorer. Ứng dụng chạy độc lập với launcher;
mười lượt kiểm tra phản hồi qua. Shortcut Desktop/Start menu trỏ RC62.
Đối chiếu bài giảng, WAV và cấu hình trước/sau không thay đổi; tác vụ giọng
đã hoàn thành không tự chạy lại.

Gói ZIP và checksum đã tải lên GitHub, kiểm digest/dung lượng phía máy chủ.
Cơ chế chọn phiên bản hiện tại với đầu vào RC34/RC61 nhận metadata công khai
RC62 đúng dung lượng/SHA-256; RC62 không tự báo cập nhật chính nó. Chưa thử
nâng cấp trên chính máy thứ hai. Tải ZIP, giải nén toàn bộ rồi chạy
**Setup.cmd**, hoặc dùng **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật**.

Thư viện cá nhân, phản hồi học sinh, key, model, EXE và dữ liệu kiểm thử
không nằm trong commit nguồn. Dữ liệu người dùng vẫn ở
`%LOCALAPPDATA%/BiliClass`; giữ các bản cài cũ.
