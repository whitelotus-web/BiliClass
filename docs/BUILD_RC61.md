# RC61 — Thanh cuộn và trạng thái Thư viện, 17/10/2026

[GitHub Release RC61](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc61).

- Nguồn: `98228c076f5f0bc91e5ab7ca7084f5ec5065d006`.
- ZIP: `BiliClass-RC61-Windows.zip`, 837279567 byte, 4168 tệp.
- ZIP SHA-256: `51b354c3bde26a2c87880e36518502fb6c5796d61200cb98a4867cf5947cdd0e`.
- EXE SHA-256: `f87287c23f3656a884245441ca75a4350eb0a16fb949c18471366c8a57454994`.

## Thay đổi

Thanh cuộn dùng chung ở Trang chủ/Thư viện được đặt trong lề phải, ngoài
vùng nội dung. Phần hiển thị rộng 6 px, bo tròn, màu dịu; vùng chuột rộng
18 px để dễ kéo. Thanh đổi màu khi rê/kéo, tự ẩn khi nội dung vừa màn hình
và ẩn cùng trang. Không trừ thêm chiều rộng nội dung nên các nút không
xê dịch khi thanh hiện/ẩn.

Thư viện gộp hai bộ đếm thành một trạng thái cạnh **Xóa đã chọn**:
**10 bài** khi xem toàn bộ, **3 kết quả** khi lọc hoặc **Đã chọn 2 bài**
khi tích chọn. Bỏ hàng giải thích dài phía dưới và số lặp trong **Chọn tất
cả**. Chú thích khi rê chuột giải thích tổng số/phạm vi chọn; trình đọc màn
hình cũng có mô tả này. Giữ chọn qua nhiều trang và bỏ chọn khi đổi bộ lọc.

## Kiểm chứng

8 kiểm thử trong `test_library_view.py` và `test_release_package.py` qua.
Ruff cho `app` và `biliclass_m0` không lỗi. Không chạy lại toàn bộ kiểm thử
hoặc suy luận model vì chỉ thay giao diện; runtime/model giữ nguyên từ
[RC60](BUILD_RC60.md), nền tảng đã kiểm chứng ở [RC58](BUILD_RC58.md).

Qt thật kiểm tra thanh cuộn ở 1080×700, 1366×850 và 1680×960: không chồng
lên nút đổi kiểu xem, chia sẻ, xóa hoặc bộ đếm. Khoảng cách từ mép nội dung
đến vùng chuột là 6 px; thanh nhìn thấy rộng 6 px. Kéo chuột thật và lăn
chuột đều di chuyển nội dung. Khi lọc không có bài, thanh ẩn và phần nội
dung không đổi chiều rộng. Trạng thái tổng/lọc/chọn cập nhật đúng, số bài
đã chọn không bị cắt ở ba cỡ cửa sổ.

Qt quản lý 24 bài kiểm tra chọn qua nhiều trang, lọc, tải, thùng rác,
khôi phục/xóa và các lối vào lớp/báo cáo/thuật ngữ. Hàng bộ lọc/thao tác
vẫn vừa ở 1080 và 1366. Luồng danh sách/thẻ với ảnh PowerPoint thật và
Trang chủ hai mascot ở ba cỡ cửa sổ đều qua. Không có cảnh báo QML.

## Bộ cài và cập nhật

Biên dịch lại 113 module app một lần; mỗi tệp trong ZIP kiểm SHA-256/CRC.
Bản EXE đã cài kiểm chín cấu hình Qt: thư viện danh sách/thẻ, cài đặt,
chuyển đổi, Trang chủ ba cấu hình kích thước/nhân vật, lớp và báo cáo.
Dùng dữ liệu riêng và không truyền đường dẫn Python nguồn vào EXE.

Cài tại `F:/Applications/BiliClass/1.0.0rc61`, đóng RC60 bình thường và mở
RC61 bằng Explorer vào Thư viện. Ứng dụng chạy độc lập với launcher;
mười lần kiểm tra phản hồi qua. Shortcut Desktop/Start menu trỏ RC61.
Đối chiếu bài giảng, WAV và cấu hình trước/sau không thay đổi; tác vụ giọng
đã hoàn thành không tự khởi động lại. Giữ các bản cài cũ.

Gói ZIP và checksum đã tải lên GitHub, kiểm digest/dung lượng phía máy chủ.
Cơ chế chọn phiên bản hiện tại với đầu vào RC34/RC60 nhận metadata công khai
RC61 đúng dung lượng/SHA-256; RC61 không tự báo cập nhật chính nó. Chưa thử
nâng cấp trên chính máy thứ hai. Có thể tải ZIP, giải nén toàn bộ và chạy
**Setup.cmd**, hoặc dùng **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật**.

Dữ liệu giáo viên vẫn ở `%LOCALAPPDATA%/BiliClass`. Commit chỉ chứa mã nguồn
và tài liệu; bài cá nhân, phản hồi học sinh, key, model và EXE không nằm trong
commit nguồn.
