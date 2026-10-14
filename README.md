# BiliClass

Ứng dụng Windows chuyển tài liệu của giáo viên thành bài giảng Anh–Việt, rồi trình chiếu bằng PowerPoint với giọng đọc và mascot trợ giảng. Hỗ trợ cấu hình từ lớp 1 đến lớp 12 và môn tự nhập.

RC14 thêm [kiểm tra slide và English Reader](docs/SMART_SLIDES_READER.md): lời đọc theo đối tượng thật trên slide, tạm dừng/tiếp tục và một lượt yêu cầu ChatGPT sửa sau báo cáo render. Chữ trong ảnh, công thức và hiệu ứng chưa chắc vẫn giữ CHECK; không tự chứng nhận mọi slide đã đủ song ngữ.

## Cài để dùng trên máy khác

Tải **BiliClass-RC28-Windows.zip** tại [Release RC28](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc28), giải nén toàn bộ rồi chạy **Setup.cmd**. Không tải “Source code” nếu chỉ muốn cài và dùng. Không cần Python hoặc API key.

RC16 có [thanh tiến trình % và tối ưu xử lý trên máy](docs/CONVERSION_PROGRESS.md): dùng lại ảnh/đo bố cục đã kiểm tra, tránh voice trùng và chờ menu model sẵn sàng. % giữ ở mốc chờ khi ChatGPT đang tạo bài; không đoán % xử lý bên trong web.

Máy cần Windows 10/11 64-bit, Google Chrome để đăng nhập ChatGPT và Microsoft PowerPoint bản desktop để trình chiếu/giữ hiệu ứng. Kết nối Internet cần khi đăng nhập và chuyển đổi; sáu giọng VieNeu chung Việt/Anh và các mẫu đã nằm trong gói. Việc tạo tệp/hạn mức phụ thuộc tài khoản ChatGPT Free/Plus của người dùng.

Sau khi cài, mở **Cài đặt → Browser AI**, chọn **ChatGPT hoặc Gemini**, bấm **Thêm tài khoản** và tự đăng nhập trên máy đó. Mỗi profile Chrome độc lập, thêm nhiều tài khoản cho mỗi dịch vụ. Tích chọn tài khoản cụ thể hoặc để tool tự chọn tài khoản đang kết nối của dịch vụ đã chọn. Bài mới gửi prompt/tài liệu qua dịch vụ đó; bài đã gửi giữ dịch vụ/tài khoản/cuộc trò chuyện cũ khi tiếp tục. Không tự chuyển từ Gemini sang ChatGPT hoặc ngược lại khi hết lượt.

RC28 kiểm tra model và suy luận cao nhất đọc được trong các lựa chọn đang được web cấp quyền trước mỗi lượt gửi/sửa. Không mua gói hoặc đoán quyền từ tên Free/Plus/Pro; lựa chọn chưa xác nhận được thì dừng trước khi gửi. Gemini nhận PPTX trực tiếp hoặc xuất qua Google Slides → Microsoft PowerPoint nếu web hỗ trợ. [Cách dùng và giới hạn nghiệm thu](docs/BROWSER_SERVICES.md). Phiên đăng nhập và bài học riêng không được chuyển qua GitHub. Muốn dùng portable, chạy `BiliClass/BiliClass.exe` và giữ nguyên toàn bộ thư mục `_internal`, `models`, `licenses`.

App tự kiểm tra bản mới khi mở. Khi có phiên bản mới, chọn **Cập nhật**; app tải/xác minh gói rồi cài và mở lại. Dữ liệu nằm riêng tại `%LOCALAPPDATA%/BiliClass` nên được giữ qua cập nhật. Không cần tự tải và cài lại mỗi lần.

Nếu bản cũ chưa có **Kiểm tra cập nhật**, cài gói Windows mới một lần để có
nút này. RC23 hiển thị nút và số phiên bản ở cả bản nguồn lẫn bản cài, giữ
nút trên màn hình ở cửa sổ thấp. Bản nguồn có thể cài gói Windows đã phát
hành qua nút cập nhật mà không ghi đè checkout Git.

RC23 thu gọn báo cáo slide vào **Xem chi tiết**, vẫn giữ cảnh báo các slide
cần sửa trước khi dạy. Giọng đọc dùng lại WAV đã có và có
giới hạn luồng CPU để tránh tranh tài nguyên; đọc chi tiết và số đo tại
[Giữ phiên và tối ưu tốc độ](docs/SESSION_AND_SPEED.md).

RC17 dùng [một giọng VieNeu cho Việt và Anh](docs/MULTILINGUAL_VOICE.md), có sáu giọng nam/nữ, nghe thử tốc độ trước khi lưu.

RC18 [tự khôi phục xác nhận gửi](docs/BROWSER_RECOVERY.md) khi Chrome gián đoạn, tiếp tục đúng chat và không gửi trùng. Tác vụ đã lưu được tiếp tục sau khởi động lại, trừ khi giáo viên bấm Dừng hoặc web yêu cầu can thiệp.

RC27 tách thành [hai bước độc lập](docs/SESSION_AND_SPEED.md): nhận/kiểm tra/lưu PowerPoint rồi dừng tại màn bài giảng. Có thể tải hoặc dạy không cần voice. Khi muốn, chọn Anh, Việt hoặc Việt + Anh rồi bấm **Tạo giọng đọc** để chạy trên máy với tiến độ riêng. Mở lại bài không tự tạo âm thanh; thư viện đánh dấu ngôn ngữ đã có giọng.

RC21 sửa bước kích hoạt nút gửi và tìm lại prompt dài bị thu gọn. Màn hình chuyển đổi hiển thị tiến trình chuẩn bị, biên soạn, kiểm tra và lưu bài giảng; các chi tiết vận chuyển nằm trong bản ghi. Tác vụ đã dừng vẫn báo tạm dừng và giữ bài, không giả vờ tiếp tục loading.

## Chuyển đổi và dạy

1. Kéo thả/chọn PPTX, DOCX, PDF, TXT, PNG/JPG hoặc dán nội dung.
2. Điền tên bài, môn, cấp/khối lớp và ghi chú thêm nếu cần.
3. Chọn một kiểu: **Hai cột song ngữ**, **Song ngữ từng câu**, **Tích hợp từ khóa**, **Tiếng Anh 100%**.
4. Với PPTX, chọn giữ thiết kế PowerPoint đầu vào hoặc mẫu mới. Tài liệu khác dùng mẫu mới. Ba mẫu **Chuẩn lớp học**, **Trực quan**, **Luyện tập & tương tác** có ảnh xem trước rõ.
5. Bấm **Chuyển đổi bài giảng**. BiliClass nhận, kiểm tra và lưu PPTX, rồi dừng để bạn xem bài và **Tải PowerPoint**. Voice không bắt buộc. Chỉ cần can thiệp khi web yêu cầu đăng nhập/xác minh, hết lượt hoặc kết quả cần kiểm tra.
6. Nếu cần voice, chọn **Tiếng Anh**, **Tiếng Việt** hoặc **Việt + Anh**, bấm **Tạo giọng đọc**. Tool dùng giọng/tốc độ đã lưu trong Cài đặt, chạy trên máy và dùng lại các đoạn âm thanh đã có. PowerPoint tải về không tự nhúng voice; âm thanh dùng trong trợ giảng BiliClass.
7. Xem lại rồi bấm **Dùng để dạy**, có hoặc không có voice. PowerPoint trình chiếu toàn màn hình; mascot nổi có thể kéo, điều khiển slide và đọc ngôn ngữ đã chuẩn bị. Quiz là bản nháp cần duyệt riêng.

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
