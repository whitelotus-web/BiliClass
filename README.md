# BiliClass

Ứng dụng Windows chuyển tài liệu của giáo viên thành bài giảng Anh–Việt, rồi trình chiếu bằng PowerPoint với giọng đọc và mascot trợ giảng. Hỗ trợ cấu hình từ lớp 1 đến lớp 12 và môn tự nhập.

## Luồng hiện tại — RC40

RC39 sửa lỗi đọc PowerPoint kế thừa cỡ chữ từ slide mẫu khiến tác vụ dừng trước bước dịch. Đã kiểm tra bằng API Google thật; [nguyên nhân và phạm vi kiểm chứng](docs/GOOGLE_DOCUMENT_FIX_RC39.md).

RC40 giữ thiết kế gốc khi dịch, đọc thêm chữ kèm công thức và dùng cặp trang Việt–Anh cho slide kín/hiệu ứng. [Cách giữ thiết kế và giới hạn](docs/SOURCE_DESIGN_RC40.md).

BiliClass dùng **Google Cloud Translation NMT** để dịch phần chữ rồi dựng PowerPoint tại máy. **Browser ChatGPT/Gemini được tạm ẩn**, không gửi prompt hoặc tự chạy lại lượt web cũ. Giọng đọc là bước tùy chọn sau khi bài song ngữ đã lưu.

1. Bật Cloud Translation API và thanh toán trên Google Cloud; thêm key trong **Cài đặt → Google Dịch**. Mỗi dòng nhập `Tên dự án | API_KEY`, hoặc chỉ một key. Key cùng dự án phải ở cùng nhóm; các key không có tên nhóm dùng chung nhóm Mặc định.
2. Chọn PowerPoint có chữ chỉnh sửa được, DOCX, PDF có chữ, TXT hoặc dán nội dung. Chọn **Hai cột**, **Từng cặp** hoặc **Tiếng Anh**.
3. Bấm **Chuyển đổi bài giảng**. Phần chữ được chia cụm nhỏ, loại nội dung lặp, dịch bằng hai worker có giới hạn và lưu cache. Số liệu/công thức được bảo vệ; phần trăm và thời gian hiển thị trên cửa sổ.
4. Chọn giữ thiết kế PPTX: giữ nền, hình và hiệu ứng; slide đủ chỗ dùng song ngữ cùng trang, slide chật dùng cặp trang Việt–Anh kế tiếp. Có PowerPoint trên máy thì đo/căn phần chữ mới tối đa hai lượt. Chữ trong ảnh, nhãn biểu đồ và trạng thái hiệu ứng vẫn cần đối chiếu. Mẫu mới chỉ dùng khi giáo viên chọn hoặc nguồn không phải PPTX.
5. Tải PowerPoint ngay, hoặc chọn giọng VI/EN/cả hai rồi **Tạo giọng đọc**. Giọng VieNeu dùng một preset đa ngôn ngữ và tốc độ đã lưu, chạy tại máy. Âm thanh dùng trong BiliClass; tải PPTX không tự nhúng voice.

Google có tín dụng miễn phí cho 500.000 ký tự/tháng theo điều kiện Google; **không phải 500.000 ký tự cho mỗi key**. BiliClass có bộ đếm/ngân sách cục bộ theo nhóm dự án, không đọc được số dư miễn phí hay mức dùng trên máy khác. Đặt thêm quota trên Google Cloud để kiểm soát chi phí. Key mã hóa theo tài khoản Windows, không vào Git, gói bài hoặc bản sao lưu; sang máy khác phải nhập lại.

[Cách dùng, quản lý nhiều key và giới hạn RC38](docs/GOOGLE_TRANSLATION_RC38.md). Đã chạy API thật trên một bài thực tế; kiểm thử hồi quy dùng fixture, không công bố tốc độ hoặc chất lượng bảo đảm cho mọi bài/môn.

## Cài và cập nhật

Máy cần Windows 10/11 64-bit, Internet khi dịch và Microsoft PowerPoint desktop để xem/trình chiếu giữ hiệu ứng. Tải gói Windows tại [GitHub Releases](https://github.com/whitelotus-web/BiliClass/releases), giải nén toàn bộ và chạy **Setup.cmd**. **Mã nguồn mới và gói đã phát hành là hai bản riêng**; RC40 là bản thử tại máy, chưa tự xuất hiện trên kênh cập nhật. Các release browser cũ vẫn dùng cơ chế của phiên bản đó.

Nút **Kiểm tra cập nhật** nằm trong **Cài đặt → Thông tin BiliClass**. Gói Windows có model, không cần Python. Muốn chạy từ source, xem phần dưới; cần thêm Google Cloud Translation API key cho luồng mới. Dữ liệu giáo viên ở `%LOCALAPPDATA%/BiliClass` được giữ riêng khi cập nhật và không nằm trên GitHub.

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
