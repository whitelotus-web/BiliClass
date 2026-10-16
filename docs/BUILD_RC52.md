# RC52 — phát hành 16/10/2026

[GitHub Release RC52](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc52)

- Nguồn: `a3ba9155c1ae49c98d6a2a6422bbb1a983c16b8b`.
- ZIP: `BiliClass-RC52-Windows.zip`, 837.227.943 byte, 4.165 tệp.
- ZIP SHA-256: `285942cf9845d5394fd8b2ac343a2affb07ac52ea54126f0beb046d7c273bfb0`.
- EXE SHA-256: `e1468144810d5c3dbe395ccfaf2599da6bd5aa0d0d655a0d6f614a74a6e6e437`.

[Thay đổi và cách dùng](LIBRARY_TRASH_RC52.md). Nguồn đã commit/push trước
khi build một lần. Biên dịch 108 module ứng dụng; QML mới và runtime/model
đã xác minh từ RC51 nằm đầy đủ trong ZIP. Dùng lại dữ liệu nén không đổi
để đóng gói nhanh, nhưng đọc kiểm tra SHA-256/CRC mọi tệp trong ZIP mới.
Không sửa bản RC51 đã công bố; không commit EXE/model hay thư viện cá nhân.

42 kiểm thử liên quan và Qt trên thư viện thử qua: một hàng công cụ tại
1080×700 / 1366×850, ô tích 16 px, chọn qua nhiều trang, hủy xóa, khôi phục
nhóm, xóa vĩnh viễn, khôi phục tất cả, danh sách rỗng và bảo vệ bài đang dùng.
Không có QML warning. Cài bằng manifest/checksum vào thư mục phiên bản mới;
executable đã cài mở Thư viện và Cài đặt với dữ liệu thử khi bỏ đường dẫn
Python/model của môi trường phát triển. Không chạy lại inference giọng/OCR:
native runtime và model không đổi so với [kiểm chứng RC51](BUILD_RC51.md).

GitHub xác nhận kích thước/digest của cả ZIP và tệp sha256 trước khi công
khai. Đã kiểm tra qua API công khai: trình cập nhật từ RC34 và RC51 đều
nhận RC52 đúng kích thước và digest. Thông tin source/version trong bundle
và manifest khớp commit trên.

Đã cài tại `%LOCALAPPDATA%/Programs/BiliClass/1.0.0rc52`, mở trang Thư viện
qua Explorer. App nằm ngoài job của launcher và sống sau khi launcher bị
đóng; 10 phép kiểm tra cửa sổ phản hồi qua. Shortcut Desktop/Start menu trỏ
RC52. Khi chuyển phiên bản, toàn bộ 16 bản ghi bài, 992 WAV và tùy chọn cá
nhân giữ nguyên; không tự khởi động lại giọng đã hoàn tất 354/354.

Xóa vĩnh viễn được thử với dữ liệu dùng một lần. Không xóa bài thật trong
quá trình kiểm chứng; báo cáo và tài nguyên dùng chung được giữ lại. Phạm
vi bộ cài là Windows hiện tại, không phải chứng nhận mọi cấu hình máy.
