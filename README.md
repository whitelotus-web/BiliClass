# BiliClass

Ứng dụng Windows chuyển tài liệu của giáo viên thành bài giảng Anh–Việt, rồi trình chiếu bằng PowerPoint với giọng đọc và mascot trợ giảng. Hỗ trợ cấu hình từ lớp 1 đến lớp 12 và môn tự nhập.

RC14 thêm [kiểm tra slide và English Reader](docs/SMART_SLIDES_READER.md): lời đọc theo đối tượng thật trên slide, tạm dừng/tiếp tục và một lượt yêu cầu ChatGPT sửa sau báo cáo render. Chữ trong ảnh, công thức và hiệu ứng chưa chắc vẫn giữ CHECK; không tự chứng nhận mọi slide đã đủ song ngữ.

## Cài để dùng trên máy khác

Tải **BiliClass-RC20-Windows.zip** tại [Release RC20](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc20), giải nén toàn bộ rồi chạy **Setup.cmd**. Không tải “Source code” nếu chỉ muốn cài và dùng. Không cần Python hoặc API key.

RC16 có [thanh tiến trình % và tối ưu xử lý trên máy](docs/CONVERSION_PROGRESS.md): dùng lại ảnh/đo bố cục đã kiểm tra, tránh voice trùng và chờ menu model sẵn sàng. % giữ ở mốc chờ khi ChatGPT đang tạo bài; không đoán % xử lý bên trong web.

Máy cần Windows 10/11 64-bit, Google Chrome để đăng nhập ChatGPT và Microsoft PowerPoint bản desktop để trình chiếu/giữ hiệu ứng. Kết nối Internet cần khi đăng nhập và chuyển đổi; sáu giọng VieNeu chung Việt/Anh và các mẫu đã nằm trong gói. Việc tạo tệp/hạn mức phụ thuộc tài khoản ChatGPT Free/Plus của người dùng.

Sau khi cài, mở BiliClass từ Start menu → **Cài đặt → Browser AI → Thêm tài khoản** và tự đăng nhập ChatGPT trên máy đó. Phiên đăng nhập và bài học riêng không được chuyển qua GitHub. Muốn dùng portable, chạy `BiliClass/BiliClass.exe` và giữ nguyên toàn bộ thư mục `_internal`, `models`, `licenses`.

App tự kiểm tra bản mới khi mở. Khi có phiên bản mới, chọn **Cập nhật**; app tải/xác minh gói rồi cài và mở lại. Dữ liệu nằm riêng tại `%LOCALAPPDATA%/BiliClass` nên được giữ qua cập nhật. Không cần tự tải và cài lại mỗi lần.

RC17 dùng [một giọng VieNeu cho Việt và Anh](docs/MULTILINGUAL_VOICE.md), có sáu giọng nam/nữ, nghe thử tốc độ trước khi lưu.

RC18 [tự khôi phục xác nhận gửi](docs/BROWSER_RECOVERY.md) khi Chrome gián đoạn, tiếp tục đúng chat và không gửi trùng. Tác vụ đã lưu được tiếp tục sau khởi động lại, trừ khi giáo viên bấm Dừng hoặc web yêu cầu can thiệp.

RC19 [giữ phiên Chrome và mở bài trước khi tạo đủ âm thanh](docs/SESSION_AND_SPEED.md). Giọng đọc tự chuẩn bị ở nền, có trạng thái riêng và ưu tiên đoạn đang cần đọc. 100% chuyển đổi nghĩa là đã nhận/kiểm tra/lưu PowerPoint; việc chuẩn bị âm thanh còn lại không chặn xem bài.

## Chuyển đổi và dạy

1. Kéo thả/chọn PPTX, DOCX, PDF, TXT, PNG/JPG hoặc dán nội dung.
2. Điền tên bài, môn, cấp/khối lớp và ghi chú thêm nếu cần.
3. Chọn một kiểu: **Hai cột song ngữ**, **Song ngữ từng câu**, **Tích hợp từ khóa**, **Tiếng Anh 100%**.
4. Với PPTX, chọn giữ thiết kế PowerPoint đầu vào hoặc mẫu mới. Tài liệu khác dùng mẫu mới. Ba mẫu **Chuẩn lớp học**, **Trực quan**, **Luyện tập & tương tác** có ảnh xem trước rõ.
5. Bấm **Chuyển đổi bài giảng**. BiliClass gửi bản sao nguồn và prompt qua Chrome, nhận PPTX, chuẩn bị giọng Việt–Anh. Chỉ cần can thiệp khi web yêu cầu đăng nhập/xác minh, hết lượt hoặc kết quả cần kiểm tra.
6. Xem lại rồi bấm **Dùng để dạy**. PowerPoint trình chiếu toàn màn hình; mascot nổi có thể kéo, nhấp để mở đọc Anh/Việt và điều khiển slide. Quiz nhận từ ChatGPT là bản nháp cần duyệt riêng.

Mẫu gửi ChatGPT chỉ chứa bố cục trống, không chứa kiến thức bài minh họa. Prompt tách quy tắc môn/độ tuổi khỏi kiểu ngôn ngữ, giữ hình/công thức và số lượng/thứ tự slide khi chọn PowerPoint gốc. Nội dung, bản dịch và hiệu ứng vẫn cần giáo viên đối chiếu trước khi dạy.

## Mã nguồn và cập nhật GitHub

**Vẫn sửa code bình thường.** GitHub lưu và đồng bộ các phiên bản; không thay thế môi trường chạy trên máy. Người cùng phát triển clone hoặc tải mã nguồn, cài môi trường một lần, sửa → kiểm tra → commit/push. Trước khi làm tiếp ở máy khác, chạy `git pull --ff-only`; nếu hai người sửa cùng chỗ, cần xử lý xung đột.

Gói cài Windows là tài sản riêng trong Releases. Không cần tạo lại `.exe` sau mỗi lần sửa để thử trên máy phát triển: đóng cửa sổ nguồn rồi chạy lại `scripts/run.ps1`. Chỉ đóng gói khi có mốc đã kiểm tra để người dùng bản cài cập nhật.

Cài Python 3.12 64-bit và [uv](https://docs.astral.sh/uv/getting-started/installation/) rồi chạy trong thư mục mã nguồn:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements-lock.txt
uv pip install --python .venv/Scripts/python.exe -e . --no-deps
.\.venv\Scripts\python.exe scripts/download_vieneu.py
powershell -ExecutionPolicy Bypass -File scripts/run.ps1
```

Model tải một lần cho môi trường nguồn; bộ cài đã có model nên không cần các lệnh trên. File khóa gồm cả các phụ thuộc kiểm chứng cũ; dịch/OCR cũ không đóng trong RC14. Trên ổ dự án chậm, chuẩn bị `scripts/prepare-dev-runtime.ps1` và `scripts/prepare-dev-voices.ps1` một lần; `run.ps1` tự dùng cache hợp lệ.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app biliclass_m0 scripts tests
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -DistRoot (Join-Path $PWD 'dist/rc15')
.\.venv\Scripts\python.exe -m scripts.package_release (Join-Path $PWD 'dist/rc15')
powershell -ExecutionPolicy Bypass -File scripts/verify_release.ps1 -DistRoot (Join-Path $PWD 'dist/rc15')
```

Gói có `BiliClass/BUILD_INFO.json` ghi version/commit và manifest SHA-256 để đối chiếu bản đang thử. Kho Git chỉ giữ code, kiểm thử, tài liệu và tài nguyên dùng chung. Thư viện giáo viên, báo cáo học sinh, browser profile, model, cache và `.exe` không vào lịch sử Git.

## Tài liệu và phạm vi kiểm chứng

[Hướng dẫn sử dụng](docs/USER_GUIDE.md) · [Thử trên hai máy](docs/TEACHER_TESTING.md) · [Bốn kiểu chuyển đổi](docs/FOUR_FORMAT_WORKFLOW.md) · [Thư viện mẫu](docs/TEMPLATE_LIBRARY.md) · [Trạng thái kỹ thuật](docs/STATE.md) · [Thành phần bên thứ ba](docs/THIRD_PARTY.md).

Bản thử đã kiểm tra trên máy phát triển với Microsoft PowerPoint và Chrome. Cần thử thêm Windows sạch, máy ít RAM, máy chiếu/mạng lớp và chất lượng nhiều môn. Kiểm thử kỹ thuật không tự chứng nhận mọi bài giảng hoặc mọi tài khoản ChatGPT.
