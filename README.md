# BiliClass

Kho kiến thức có nguồn và bộ nhớ giáo viên đang được bổ sung trong bản mã nguồn: xem [cách vận hành](docs/KNOWLEDGE.md). Bản RC12 đóng gói chưa có tính năng này.

Mã nguồn ngày 09/10/2026 có **bốn Kiểu chuyển đổi** thay level và bố cục riêng: Hai cột song ngữ, Song ngữ từng câu, Tích hợp từ khóa, Tiếng Anh 100%. Luồng chính dùng web ChatGPT qua Chrome: tài liệu → một phương pháp → chuyển đổi → xem → dùng để dạy với voice/mascot. Xem [quy trình và kế hoạch thu gọn](docs/FOUR_FORMAT_WORKFLOW.md). Bản đóng gói RC12 chưa có thay đổi này.

Browser AI dùng **Google Chrome với hồ sơ riêng cho từng tài khoản**, tự lưu phiên, ưu tiên Plus còn dùng được rồi Free trước khi gửi bài. Ngày 04/10/2026 đã đăng nhập và nhận một PowerPoint thật 12 slide, chuẩn bị giọng Việt–Anh và mở trình chiếu cùng mascot. Chưa chứng nhận chất lượng mọi bài, mọi tài khoản hoặc máy khác; số dư hạn mức chưa có dữ liệu tin cậy. Yêu cầu đã gửi giữ tài khoản/cuộc trò chuyện, không tự gửi trùng. OAuth/offline cũ còn giữ để đọc luồng cũ, ngoài bước nhập mới. Xem [trạng thái kiểm tra](docs/STATE.md).

Ứng dụng Windows chuẩn bị và dạy **song ngữ Anh–Việt đa môn THPT**. Bản thử hiện tại: **1.0 RC12**, cập nhật 02/10/2026.

## Dùng thử

Tải [BiliClass RC12](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc12) hoặc chọn bản phát hành mới nhất trong [GitHub Releases](https://github.com/whitelotus-web/BiliClass/releases), giải nén toàn bộ rồi chạy `Setup.cmd` để cài lần đầu. Bản portable cũng có thể chạy `BiliClass/BiliClass.exe`; giữ nguyên cả thư mục, gồm `_internal` và `models`. Gói thử kèm model dịch, năm giọng English Kokoro và bốn giọng Việt VieNeu offline. Không cần Python. Sau khi cài, app tự kiểm tra GitHub khi mở và có nút **Kiểm tra cập nhật**; khi có bản mới, bấm **Cập nhật**, chờ app tự đóng/mở lại. Thư viện bài học nằm riêng và được giữ lại.

App dùng thư viện của người dùng trong `%LOCALAPPDATA%/BiliClass`, không tự chèn bài mẫu. `BILICLASS_DATA` đổi thư mục dữ liệu. Các kiểm thử dùng thư viện tạm riêng.

[Hướng dẫn sử dụng](docs/USER_GUIDE.md) · [Trạng thái và giới hạn](docs/STATE.md) · [Kết quả kiểm tra](docs/APP_RESULTS.md) · [Phiếu nghiệm thu tại lớp](docs/FIELD_ACCEPTANCE.md).

## Chức năng

- Nhập PPTX/DOCX/PDF/TXT/PNG/JPG; đánh giá ngôn ngữ theo đoạn. OCR Việt–Anh cục bộ có bước chuẩn bị model một lần; chữ OCR cần kiểm tra, nguồn giữ nguyên.
- Dịch offline Việt ↔ Anh; dịch phần còn thiếu theo loạt, giữ cặp sẵn có và đoạn duyệt/khóa. Ưu tiên thuật ngữ/memory giáo viên trước kho nền/model; bản nháp cần kiểm tra và duyệt.
- Bài mới chọn một trong bốn kiểu chuyển đổi. Prompt giữ số lượng/thứ tự slide PPTX, hình/công thức/hoạt ảnh tối đa; trường hợp chưa xử lý được phải báo rõ. Tài liệu khác dựng theo mẫu. Khi nhận, tool cảnh báo số slide khác nguồn; chưa tự chứng nhận bản dịch/hiệu ứng đúng.
- Bài cũ theo level vẫn đọc được. Năm giọng Kokoro English và bốn giọng VieNeu Việt chạy offline/cache WAV; PowerPoint toàn màn hình kết hợp Milo/Lumi trong suốt, đọc theo slide thực tế. Chế độ Tiếng Anh 100% giữ lời đọc Việt ở ghi chú riêng.
- Cài đặt Chung, Giọng đọc, Mascot và Browser AI giữ cấu trúc hiện tại. Song ngữ hướng dẫn bốn phương pháp. Câu hỏi ChatGPT trong ghi chú được nhận thành bản nháp liên kết slide, cần duyệt riêng.
- QR/LAN, học sinh trả lời trên trình duyệt, ba loại câu hỏi, gửi lại/đổi đáp án/kết nối lại; kết quả chỉ công bố khi giáo viên chọn.
- Báo cáo có mẫu số, recheck, gợi ý level có điều kiện, CSV; Lesson Pack kèm audio, deck song ngữ mới, sao lưu/khôi phục.

RC12 đã qua smoke test, kiểm thử updater và tự kiểm tra đóng gói trên máy phát triển; chưa được nghiệm thu trên Windows sạch, laptop 8 GB, điện thoại/máy chiếu và mạng trường thực tế. Model dịch và cảm nhận chất lượng giọng cần giáo viên kiểm tra. Phạm vi còn lại được ghi rõ trong [backlog](docs/TASKS.md).

RC12 thêm kiểm tra phiên bản, tải gói có checksum, cài phiên bản mới cạnh phiên bản cũ và giữ thư viện bài học; tiếp tục tách nhiều ý trên một slide PowerPoint thành các đoạn để duyệt, xuất cặp Việt–Anh cùng trang, giữ ảnh thường từ slide gốc, cho chọn kiểu bài và yêu cầu **Chốt bản chuẩn bị** trước khi mở lớp mới. Biểu đồ, video và hiệu ứng PowerPoint vẫn cần đối chiếu hoặc trình chiếu bản gốc.

Để hai giáo viên thử trên hai máy, xem [quy trình chia sẻ bản thử](docs/TEACHER_TESTING.md). Kho Git công khai chứa mã và tài liệu; dữ liệu bài học, báo cáo học sinh, model và bản `.exe` không nằm trong lịch sử Git. Tải bản cài tại [Release RC12](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc12) hoặc xem [toàn bộ Releases](https://github.com/whitelotus-web/BiliClass/releases).

## Phát triển

Để thử thay đổi nhanh, đóng BiliClass đang mở rồi chạy mã nguồn bằng `powershell -ExecutionPolicy Bypass -File scripts/run.ps1 --page settings` trong thư mục dự án. Cửa sổ có nhãn **Bản phát triển từ mã nguồn**; sau mỗi lần sửa Python/QML, đóng cửa sổ này và chạy lại lệnh. Không cần đóng gói `.exe` ở mỗi lượt. Bản `dist/rc12` giữ nguyên cho đến lần đóng gói phát hành tiếp theo; không mở đồng thời hai bản vì chúng dùng chung thư viện cá nhân.

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
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -IncludeTrialModel -DistRoot (Join-Path $PWD 'dist/rc12')
.\.venv\Scripts\python.exe -m scripts.package_release (Join-Path $PWD 'dist/rc12')
```

Model thử từ `.runtime/models`; có thể cấu hình `BILICLASS_MODEL_DIR`. `scripts/download_models.py` là bước tải chủ động khi thiết lập, không chạy lúc dạy. Giấy phép/thành phần đóng gói: [THIRD_PARTY](docs/THIRD_PARTY.md).

## Hồ sơ

[Kế hoạch](docs/BUILD_PLAN.md) · [Sản phẩm](docs/PRODUCT_SPEC.md) · [Thiết kế](docs/DESIGN_SPEC.md) · [Kiến trúc](docs/ARCHITECTURE.md) · [Dữ liệu](docs/DATA_SCHEMA.md) · [Quyết định](docs/DECISIONS.md) · [Mascot](docs/MASCOT_ASSETS.md).
