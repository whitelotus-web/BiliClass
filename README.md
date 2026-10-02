# BiliClass

Ứng dụng Windows chuẩn bị và dạy **song ngữ Anh–Việt đa môn THPT**. Bản thử nội bộ hiện tại: **1.0 RC11**, cập nhật 02/10/2026.

## Dùng thử

Mở `dist/rc11/BiliClass/BiliClass.exe`; giữ nguyên cả thư mục, gồm `_internal` và `models`. Hoặc chạy `dist/rc11/Setup.cmd` để cài vào tài khoản Windows rồi nạp hai gói `.bclanguage` trong Cài đặt. Bản portable kèm model dịch dùng thử, năm giọng English Kokoro và bốn giọng Việt VieNeu offline. Không cần Python để mở bản đóng gói. Đóng bản đang mở trước khi chạy RC11 để tránh hai phiên bản cùng sửa thư viện.

App dùng thư viện của người dùng trong `%LOCALAPPDATA%/BiliClass`, không tự chèn bài mẫu. `BILICLASS_DATA` đổi thư mục dữ liệu. Các kiểm thử dùng thư viện tạm riêng.

[Hướng dẫn sử dụng](docs/USER_GUIDE.md) · [Trạng thái và giới hạn](docs/STATE.md) · [Kết quả kiểm tra](docs/APP_RESULTS.md) · [Phiếu nghiệm thu tại lớp](docs/FIELD_ACCEPTANCE.md).

## Chức năng

- Nhập PPTX/DOCX/PDF/TXT/ảnh; OCR theo ngôn ngữ Windows đã cài; nguồn giữ nguyên.
- Dịch offline Việt ↔ Anh, thuật ngữ theo môn, memory đã duyệt, gợi ý gần giống, kiểm tra số/ký hiệu; biên tập và duyệt từng đoạn.
- Chọn L0–L4 và một trong bốn kiểu trình bày cho từng bài, bài L5 cũ vẫn đọc được; nội dung trợ giảng được giáo viên chuẩn bị; năm giọng Kokoro English và bốn giọng VieNeu Việt chạy offline, cache WAV, VI Rescue, Milo/Lumi, PowerPoint companion và cửa sổ lớp riêng.
- Sáu tab Cài đặt: Chung (tên, trường, nhiều bộ môn, logo), Song ngữ (hướng dẫn level/bố cục), Giọng đọc có nghe thử, Mascot có xem trước theo bối cảnh, Lớp học và Dữ liệu.
- QR/LAN, học sinh trả lời trên trình duyệt, ba loại câu hỏi, gửi lại/đổi đáp án/kết nối lại; kết quả chỉ công bố khi giáo viên chọn.
- Báo cáo có mẫu số, recheck, gợi ý level có điều kiện, CSV; Lesson Pack kèm audio, deck song ngữ mới, sao lưu/khôi phục.

RC11 đã qua smoke test và tự kiểm tra đóng gói trên máy phát triển; chưa được nghiệm thu trên Windows sạch, laptop 8 GB, điện thoại/máy chiếu và mạng trường thực tế. Model dịch và cảm nhận chất lượng giọng cần giáo viên kiểm tra. Phạm vi còn lại được ghi rõ trong [backlog](docs/TASKS.md).

RC11 tách nhiều ý trên một slide PowerPoint thành các đoạn để duyệt, xuất cặp Việt–Anh cùng trang, giữ ảnh thường từ slide gốc, cho chọn kiểu bài và yêu cầu **Chốt bản chuẩn bị** trước khi mở lớp mới. Biểu đồ, video và hiệu ứng PowerPoint vẫn cần đối chiếu hoặc trình chiếu bản gốc.

Để hai giáo viên thử trên hai máy, xem [quy trình chia sẻ bản thử](docs/TEACHER_TESTING.md). Kho Git chỉ chứa mã, tài liệu và tài nguyên giao diện; dữ liệu bài học, báo cáo học sinh, model và bản `.exe` không được đưa vào lịch sử Git. Tải gói RC11 ở [trang phát hành riêng tư](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc11) sau khi được cấp quyền xem kho.

## Phát triển

Để thử thay đổi nhanh, đóng BiliClass đang mở rồi chạy mã nguồn bằng `powershell -ExecutionPolicy Bypass -File scripts/run.ps1 --page settings` trong thư mục dự án. Cửa sổ có nhãn **Bản phát triển từ mã nguồn**; sau mỗi lần sửa Python/QML, đóng cửa sổ này và chạy lại lệnh. Không cần đóng gói `.exe` ở mỗi lượt. Bản `dist/rc11` giữ nguyên cho đến lần đóng gói phát hành tiếp theo; không mở đồng thời hai bản vì chúng dùng chung thư viện cá nhân.

Mascot nổi có thể kéo đến vị trí bất kỳ trên màn hình, kể cả sang màn hình khác. Thả chuột để lưu vị trí; nhấp nhanh để mở/thu các nút. Trong bảng nút, **Về góc** đặt lại theo góc đã chọn ở Cài đặt → Mascot. Khi đổi góc mặc định rồi lưu, vị trí kéo cũ cũng được xóa.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements-lock.txt
uv pip install --python .venv/Scripts/python.exe -e . --no-deps
.\.venv\Scripts\python.exe scripts/download_kokoro.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app biliclass_m0 scripts tests
powershell -ExecutionPolicy Bypass -File scripts/run.ps1
```

```powershell
.\.venv\Scripts\python.exe scripts/download_vieneu.py
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -IncludeTrialModel -DistRoot (Join-Path $PWD 'dist/rc11')
.\.venv\Scripts\python.exe -m scripts.package_release (Join-Path $PWD 'dist/rc11')
```

Model thử từ `.runtime/models`; có thể cấu hình `BILICLASS_MODEL_DIR`. `scripts/download_models.py` là bước tải chủ động khi thiết lập, không chạy lúc dạy. Giấy phép/thành phần đóng gói: [THIRD_PARTY](docs/THIRD_PARTY.md).

## Hồ sơ

[Kế hoạch](docs/BUILD_PLAN.md) · [Sản phẩm](docs/PRODUCT_SPEC.md) · [Thiết kế](docs/DESIGN_SPEC.md) · [Kiến trúc](docs/ARCHITECTURE.md) · [Dữ liệu](docs/DATA_SCHEMA.md) · [Quyết định](docs/DECISIONS.md) · [Mascot](docs/MASCOT_ASSETS.md).
