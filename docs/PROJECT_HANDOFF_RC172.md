# Mở lại dự án BiliClass sau khi tạm gác

Mốc chốt ngày 27/10/2026: **1.0.0rc172**. Thư mục nguồn chuẩn trên máy:
`F:\Dự Án\BiliClass-Tro Ly song ngu`.

## Mã nguồn và bộ cài

- GitHub: https://github.com/whitelotus-web/BiliClass
- Nhánh đang làm: `codex/word-format-preview-rc171`. Tên nhánh giữ từ đợt
  bắt đầu UI Word; mã ứng dụng đã là RC172.
- Tag chuẩn: `v1.0.0rc172`; commit bộ cài
  `8fbe56c42e63e9d368058d9d37d22ce8d0aacab9`.
- Các commit sau tag chỉ ghi nhận nghiệm thu/dọn dẹp/hướng dẫn, không
  âm thầm đổi bộ cài. Giữ các tag cũ, nhất là RC167 để đối chiếu.
- Bộ gửi người khác: `F:\BiliClass-BoCai-RC172`, gửi cả EXE và ZIP cạnh nhau.
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

- `F:\BiliClassData`: thư viện, bài giảng, cấu hình cá nhân.
- `F:\BiliClassBackups`, `F:\BiliClassExports`: sao lưu và kết quả đã xuất.
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
