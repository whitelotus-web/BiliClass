# Mở lại dự án BiliClass sau khi tạm gác

Mốc ứng dụng ngày 27/10/2026: **1.0.0rc172**; đã gom dữ liệu ngày 28/10/2026.
Xem [sơ đồ lưu trữ hiện tại](PROJECT_STORAGE.md). Thư mục nguồn chuẩn trên máy:
`F:\Dự Án\BiliClass-Tro Ly song ngu`.

## Mã nguồn và bộ cài

Cập nhật tiếp ngày 28/10/2026: **RC173** sửa tải Word, bàn giao bộ cập nhật
sau khi đóng thư viện và bỏ hai nhãn thừa ở thanh tiêu đề. Xem
[BUILD_RC173.md](BUILD_RC173.md); RC172 và RC167 vẫn là tag lịch sử nguyên vẹn.

- GitHub: https://github.com/whitelotus-web/BiliClass
- Nhánh đang làm: `codex/word-format-preview-rc171`. Tên nhánh giữ từ đợt
  bắt đầu UI Word; mã ứng dụng đã là RC172.
- Tag chuẩn: `v1.0.0rc172`; commit bộ cài
  `8fbe56c42e63e9d368058d9d37d22ce8d0aacab9`.
- Các commit sau tag chỉ ghi nhận nghiệm thu/dọn dẹp/hướng dẫn, không
  âm thầm đổi bộ cài. Giữ các tag cũ, nhất là RC167 để đối chiếu.
- Bộ gửi người khác: `DuLieu-CucBo/04-BoCai/BiliClass-BoCai-RC172` trong dự án;
  đường dẫn cũ `F:\BiliClass-BoCai-RC172` là liên kết tương thích. Gửi cả EXE và ZIP cạnh nhau.
  Release công khai: https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc172
- Runtime/model đã kiểm cho lần đóng gói sau: `dist/rc172-release`.
  Không cần giữ mọi runtime/bản dựng cũ để mở mã nguồn làm tiếp.

## Chạy và kiểm tra lại

Mở PowerShell ở thư mục dự án:

```powershell
# Chạy tool độc lập từ source
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run.ps1 --page word

# Kiểm mã nguồn khi làm tiếp
. ./scripts/dev-env.ps1
& ./.venv/Scripts/python.exe -m pytest tests/test_word_batch.py tests/test_word_preview.py tests/test_word_formatting.py tests/test_word_selection.py tests/test_word_document.py -q
& ./.venv/Scripts/python.exe -m scripts.qt_word_batch_smoke reports/word-batch-next
& ./.venv/Scripts/python.exe -m scripts.qt_word_smoke reports/word-next
```

Giữ `.venv`, `requirements*.txt`, script dựng, tài nguyên `app/`, các bộ model
ở `.runtime/models`, `.runtime/kokoro`, `.runtime/vieneu-hf` và runtime/cache
nguồn đang dùng. Script `dev-env.ps1` thay việc phụ thuộc vào file môi trường
tạm trong `reports/`. Nếu chuyển máy, tạo lại `.venv` bằng Python đúng phiên
bản và bộ dependency đã khóa; không dùng nguyên venv từ máy khác.

Trước sửa tiếp: `git fetch origin`, kiểm `git status`, dùng nhánh này hoặc
tạo nhánh mới từ `v1.0.0rc172`. Không reset/force-push lên thay đổi chưa lưu.
Đóng gói một mốc mới sau khi đã kiểm; không ghi đè release/tag RC172.

## Dữ liệu được giữ riêng

- `DuLieu-CucBo/02-ThuVien`: thư viện, bài giảng, cấu hình cá nhân.
- `DuLieu-CucBo/03-SaoLuu`: sao lưu; bản xuất rời nằm trong
  `DuLieu-CucBo/01-BaiGiang-TuKiemTra/Ban-Xuat` để chủ dự án tự kiểm tra.
- Đường dẫn F cũ tiếp tục hoạt động qua liên kết thư mục tương thích.
- Hồ sơ nộp, video, slide và tài liệu gốc ở Downloads/các thư mục video vẫn
  giữ trên máy; không xem các sản phẩm này là rác build.
- Key, phiên đăng nhập, thư viện/model và EXE không đưa vào commit source.
  Việc “lưu dự án lên GitHub” gồm mã/tài nguyên cần phát triển và bộ cài công
  khai, không bao gồm bí mật hoặc tài liệu cá nhân.

## Trạng thái tính năng

Word một file giữ chọn vùng hoặc Dịch toàn bộ. Nhiều file khóa Dịch toàn bộ,
chung cấu hình và tên theo từng file, chạy tuần tự, lưu cạnh nguồn với hậu
tố `(Song ngu VI-EN)`, dừng/tiếp tục/thử lại, kết quả giữ trên màn hình.
Nguồn Word không bị ghi đè. Demo có bốn kiểu, nền đọc sáng/tối độc lập.

RC172 thêm sửa shortcut Unicode/Desktop/Start và pin thuộc đúng gốc cài.
Máy từng mở nhầm RC155 đã xác nhận mở được RC171 trong thư mục install.
Nếu vẫn mở nhầm từ pin cũ, mở EXE phiên bản mới rồi bỏ ghim/ghim lại.
Không cần gỡ thư viện hay xóa key để đổi phiên bản.

Chữ trong ảnh Word chưa có luồng OCR mới. Tự cập nhật vẫn cần mạng/dung
lượng/Windows cho phép cài; nghiệm thu trên máy hiện tại không thay cho
test mọi cấu hình máy/Office. Không có tác vụ nền tiếp tục phát triển sau
khi kết thúc đợt này.

## Dọn ổ khi chốt dự án

Đã dọn 141 thư mục build/cache/dữ liệu nghiệm thu dùng một lần và 31 file
bộ cài cũ đã đối chiếu hash với asset công khai trên GitHub. Giữ RC172 ở
thư mục bộ cài riêng và runtime `dist/rc172-release`. Các thư mục cũ có
junction được giữ thay vì truy đuổi/xóa đích liên kết; một runtime RC170
và bản cài đang chạy cũng được giữ nguyên. Không dọn toàn ổ một cách chung chung.

Dung lượng trống trước/sau lượt dọn trên máy này (số đo thời điểm thực hiện,
có thể đổi khi Windows/các ứng dụng khác ghi dữ liệu):

| Ổ | Trước | Sau | Thu hồi xấp xỉ |
| --- | ---: | ---: | ---: |
| C | 37,66 GB | 51,69 GB | 14,04 GB |
| F | 40,31 GB | 93,45 GB | 53,13 GB |

Dùng GB thập phân; Windows có thể hiển thị GiB nhỏ hơn. Khoảng 67 GB tổng.
Các ghi chú/key riêng còn trong thư mục bộ cài RC167 cũ được giữ, không tải
lên GitHub. Dữ liệu riêng đã được gom hoặc tham chiếu dưới `DuLieu-CucBo/`;
file nguồn chuẩn vẫn ở thư mục dự án ban đầu.

Sau dọn đã chạy lại nguồn bằng `scripts/dev-env.ps1`: trang Word mở thành
công, ảnh kiểm tra lưu được, không cảnh báo QML; cả bộ model giọng Việt và
Anh đều báo sẵn sàng. Log chi tiết của lượt dọn/khởi động nằm ở
`reports/rc172-release/` trên máy, ngoài Git.
