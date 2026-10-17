# RC60 — Trang chủ, tải PowerPoint và bố cục Thư viện, 17/10/2026

[GitHub Release RC60](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc60).

- Nguồn: `ce0b9e672392bc9e058784cf3d6a8a353fea4f14`.
- ZIP: `BiliClass-RC60-Windows.zip`, 837278997 byte, 4168 tệp.
- ZIP SHA-256: `dd0a89da731e009ae38464b9200d750f5bfe35c2caa7b35b6a7f926352522ced`.
- EXE SHA-256: `f9ea111140ba1581f7cbec55f710801e8e0d92045dbe58da18dc017b7824e34d`.

## Thay đổi

Trang chủ dùng mascot Milo/Lumi lớn theo nhân vật đã chọn, lời chào và ô
thoại trên nền xanh nhạt. Ô tải PowerPoint dùng chung với màn Chuyển đổi:
nội dung, nút có biểu tượng tải và thông tin giới hạn đều căn giữa. Luồng
chính nhận `.pptx` tối đa 200 MB; chọn/thả sai định dạng hoặc vượt dung
lượng có thông báo. Bỏ số 01/02 và nút quay về Thư viện ở màn Chuyển đổi.

Trong Thư viện, bộ đếm kết quả nằm cạnh **Xóa đã chọn**, **Chia sẻ & quản lý**
ngang dòng mô tả. Bỏ hàng tiêu đề lặp, đưa ô tìm kiếm và nội dung dưới lên
gần mô tả. Bộ đếm vẫn theo bộ lọc; giữ chọn nhiều, tải/xóa, thùng rác,
chuyển danh sách/thẻ và cache ảnh bìa.

[HOME_RC60.md](HOME_RC60.md) mô tả thiết kế và hướng phát triển. Các bộ đọc
Word/PDF/ảnh và API nhập nội dung cũ được giữ trong mã nguồn để phát triển
luồng **Tạo bài giảng từ tài liệu** riêng; bộ chọn chính hiện nhận PPTX.

## Kiểm chứng nguồn

55 kiểm thử liên quan qua: nhập/chuyển đổi định dạng, quy trình rút gọn và
gói phát hành. Ruff không lỗi. Đây là kiểm chứng theo phạm vi giao diện;
không chạy lại toàn bộ 890 kiểm thử của [RC58](BUILD_RC58.md).

Qt thật kiểm tra Trang chủ ở 1080×700, 1366×850 và 1680×960 với cả hai
mascot; chọn/thả tệp, căn giữa nút, chặn quá 200 MB, giữ cấu hình khi đổi tab
và nút xem tiến độ. Bộ chọn tệp Windows kiểm tra tên Unicode/đuôi viết hoa,
đổi và hủy chọn mà không sửa tệp nguồn. Chuyển PowerPoint bằng API fixture
qua luồng xuất bài, không dùng quota Google thật.

Qt quản lý thư viện/lớp kiểm tra 24 bài, chọn qua nhiều trang, bộ lọc, tải,
thùng rác/khôi phục/xóa, các lối vào lớp/báo cáo/thuật ngữ. Hàng bộ lọc,
thao tác và bộ đếm vừa một dòng ở 1080 và 1366; nút chia sẻ ngang mô tả,
ô tìm kiếm cách mép dưới mô tả không quá 14 px. Kiểm tra danh sách/thẻ,
ảnh bìa PowerPoint thật, cache qua các tab và nút bật/tắt mascot đều qua.
Các lượt Qt không có cảnh báo QML.

## Bộ cài và ứng dụng đang chạy

Biên dịch lại 113 module app bằng PyInstaller; runtime/model không đổi so
với bản đã kiểm chứng RC58. Mỗi tệp trong ZIP kiểm SHA-256/CRC. Bản cài
kiểm tra chín cấu hình Qt: thư viện danh sách/thẻ, cài đặt, chuyển đổi,
Trang chủ hai kích thước với Milo và một kích thước với Lumi, lớp và báo
cáo. Dùng dữ liệu riêng, không dùng đường dẫn Python nguồn trong EXE.
Không chạy lại suy luận model vì mốc này chỉ thay giao diện.

Cài tại `F:/Applications/BiliClass/1.0.0rc60`; thư viện vẫn ở
`%LOCALAPPDATA%/BiliClass`. Đã đóng RC58 bình thường và mở RC60 bằng Explorer
vào tab Bài giảng. Ứng dụng sống ngoài job của launcher sau khi launcher
bị đóng; mười lần kiểm tra phản hồi qua. Shortcut Desktop/Start menu trỏ
RC60. 17 bản ghi thư viện, 992 WAV và cấu hình giáo viên/giọng/mascot giữ
nguyên; tác vụ đã hoàn thành 354/354 không tự chạy lại. Giữ các bản cài cũ.

Không đưa thư viện cá nhân, dữ liệu học sinh, key, model hay EXE vào commit
nguồn. EXE/model thuộc gói phát hành riêng.

## Máy khác cập nhật

Vào **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật**, hoặc tải ZIP RC60,
giải nén toàn bộ và chạy **Setup.cmd**. Bộ chọn phiên bản hiện tại với đầu
vào RC34/RC58 nhận đúng metadata công khai RC60, dung lượng và SHA-256;
RC60 không tự báo lại chính nó. Đây là kiểm tra cơ chế chọn phiên bản trên
máy hiện tại, chưa phải thử nâng cấp trên chính máy thứ hai.
