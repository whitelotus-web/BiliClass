# Thư mục dự án đã gom — 28/10/2026

Thư mục chính vẫn là `F:\Dự Án\BiliClass-Tro Ly song ngu` để môi trường Python,
Git và cấu hình làm việc hiện tại không đổi đường dẫn. Mã nguồn ở `app/`,
`scripts/`, `tests/`, `docs/`; giữ `.git`, `.venv`, `.runtime` và các runtime đã
ghi trong hồ sơ RC172 để có thể mở lại dự án sau này.

Các tài liệu và dữ liệu riêng trên máy được gom dưới **`DuLieu-CucBo/`**:

| Thư mục | Nội dung |
| --- | --- |
| `01-BaiGiang-TuKiemTra` | Bản xuất bài giảng và tài liệu tham khảo để chủ dự án tự xem, tự quyết định giữ/xóa |
| `02-ThuVien` | Thư viện hoạt động của tool, gồm bài giảng, âm thanh, cấu hình và kết quả Word |
| `03-SaoLuu` | Các bản sao lưu hiện có |
| `04-BoCai` | Bộ cài RC172 mới nhất; gửi EXE và ZIP cạnh nhau |
| `05-Video` | Các dự án video, giọng đọc và sản phẩm hoàn chỉnh |
| `06-HoSo` | Hồ sơ, slide và tài liệu nộp bài |
| `07-ThongTinRieng` | Ghi chú cũ và thông tin truy cập riêng, không đưa lên GitHub |
| `08-UngDungDaCai` | Bản ứng dụng đã cài trên máy |
| `09-HeThong-Windows` | Liên kết tới phần cấu hình/cache bắt buộc của Windows |

Các đường dẫn cũ còn dùng trong cơ sở dữ liệu, shortcut hoặc script video có
liên kết thư mục tương thích. Liên kết không tạo thêm bản sao dữ liệu. Thư mục
bị Windows khóa được tham chiếu từ đây, không ép đóng chương trình hay thay
quyền truy cập để di chuyển. Nhật ký cục bộ ghi rõ phần đã chuyển và phần còn
tham chiếu trong `reports/rc172-release/consolidation-result.json`.

`DuLieu-CucBo/`, `reports/`, `refs/`, model và bộ cài nằm ngoài commit Git.
GitHub tiếp tục lưu mã nguồn/hướng dẫn; bộ cài công khai là release RC172 riêng.
Không thay đổi nội dung hoặc ghi đè bộ cài RC172 trong đợt sắp xếp này.

## Bài giảng chờ tự kiểm tra

Mở `DuLieu-CucBo/01-BaiGiang-TuKiemTra/`. Danh sách file ở `DANH_SACH.csv`;
bài giảng xuất rời ở `Ban-Xuat/`. Đợt dọn này không xóa các bài giảng này.

`02-ThuVien` vẫn giữ nguyên cấu trúc: muốn bỏ bài trong thư viện đang sử dụng,
xóa bằng giao diện Bài giảng của tool để cơ sở dữ liệu và tệp đi cùng nhau.
Video và hồ sơ nộp có thể chứa slide nguồn riêng; giữ cùng bộ video/hồ sơ.

## Mở lại dự án

Làm theo [PROJECT_HANDOFF_RC172.md](PROJECT_HANDOFF_RC172.md). Các đường dẫn
F cũ vẫn dùng được qua liên kết tương thích; vị trí gom mới nên được dùng khi
tự tìm file. Bản gốc tải ở Downloads không thuộc một thư mục dự án xác định
không được tự ý xóa hoặc gom lẫn với tài liệu khác.

## Kết quả kiểm tra sau sắp xếp

Thư viện còn đủ 19 bài như trước khi gom; `PRAGMA quick_check` trả về `ok`.
Trang Word mở, lưu ảnh kiểm tra và không có cảnh báo QML. SHA-256 của EXE và
ZIP RC172 vẫn khớp hồ sơ phát hành. Không có thay đổi mã ứng dụng hoặc bộ cài.

Đã dọn 8 thư mục kiểm thử tự động RC35/36/37 cũ, thu hồi khoảng 1,27 GB;
không xóa 6 bản PowerPoint đã xuất (khoảng 2,09 GB) để chủ dự án tự xem.
Lượt hoàn tất đã chuyển được video hồ sơ vào nhóm `05-Video`. Hai thư mục
thư viện `BiliClassData` và hồ sơ `2026/Biliclass-Bai giang song ngu` còn
được tham chiếu tại chỗ vì thư mục model/tài liệu con bị Windows khóa.
Đường dẫn tương thích BiliClass ở gốc F đã được đặt ẩn, không tạo thêm bản
sao dữ liệu; mở qua `DuLieu-CucBo/` để tránh nhầm là nhiều dự án độc lập.

Năm video hoàn chỉnh được chuyển thành file thật trong
`DuLieu-CucBo/05-Video/00-Video-DeChon/`; chủ dự án tự xem rồi xóa các bản
không muốn giữ. CSV ghi vị trí trước/sau khi gom. Giữ voice, cảnh quay và
nguồn dựng trong các thư mục dự án video bên cạnh để vẫn có thể làm tiếp.
