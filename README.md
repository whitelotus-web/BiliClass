# BiliClass

Ứng dụng Windows chuyển tài liệu của giáo viên thành bài giảng Anh–Việt, rồi trình chiếu bằng PowerPoint với giọng đọc và mascot trợ giảng. Hỗ trợ cấu hình từ lớp 1 đến lớp 12 và môn tự nhập.

## Luồng hiện tại — RC74

RC74 thêm phím đọc và nút phát/tạm dừng trong phiên PowerPoint gắn với Mascot: Cách = Anh, Enter = Việt, Ctrl+Cách = hai ngôn ngữ; ←/→ điều hướng, ↑/↓ âm lượng lời đọc. Gán phím tại Cài đặt → Mascot; xem bảng phím ngay trên Mascot. [Kiểm chứng và phạm vi](docs/BUILD_RC74.md).

RC73 hoàn thiện cấu hình giọng, màn hoàn tất, mở PowerPoint và tải bài có loa; thêm sao lưu ZIP64, khôi phục có checkpoint và Office worker riêng. [Phạm vi kiểm chứng và bộ cài](docs/BUILD_RC73.md) · [Tiến độ kế hoạch](docs/IMPLEMENTATION_RC73.md) · [Hướng dẫn sử dụng](docs/USER_GUIDE.md). Bản dựng tại máy và bản trên GitHub Releases có vòng phát hành riêng; xem version trong ứng dụng/gói đang dùng.

BiliClass dùng **Google Cloud Translation** dịch phần chữ và sắp xếp PowerPoint tại máy. Browser ChatGPT/Gemini tạm ẩn. Giọng VieNeu chạy ngoại tuyến, là bước tùy chọn sau khi đã có bài song ngữ.

1. Cài đặt → Google Dịch: thêm key, mỗi dòng `Tên dự án | API_KEY`, rồi lưu. Có thể nhận key từ kho GitHub riêng tư nếu máy đã đăng nhập GitHub có quyền; không có mật khẩu BiliClass bổ sung.
2. Chọn PowerPoint `.pptx` tối đa 200 MB, chọn **Song ngữ Việt–Anh** hoặc **Tiếng Anh 100%**; giữ thiết kế gốc hoặc dùng mẫu Universal 2026/mẫu PowerPoint riêng.
3. Chuyển đổi và xem lại bài. Song ngữ cùng slide tự chọn cách xếp theo vùng; vùng quá kín có thể dùng trang tiếp nối song ngữ. Hình, công thức, nội dung OCR và hiệu ứng phức tạp vẫn cần đối chiếu.
4. Tải PowerPoint ngay hoặc chọn người đọc/tốc độ để tạo giọng Anh, Việt hay Việt–Anh. Lần đầu mặc định Tiếng Anh, lần sau nhớ lựa chọn gần nhất. Tạo trùng có popup dùng lại/tạo lại. Tên tải có sẵn tên bài và ngôn ngữ/bản giọng trong ngoặc.
5. Khi đủ giọng, chọn **Mở PowerPoint**, **Kiểm tra slide và giọng**, tải PPTX/audio hoặc xem trong Bài giảng. PowerPoint mở trực tiếp; bấm F5 rồi bấm loa. Loa đọc trọn lời đã lưu của slide khi bấm, kể cả phần xuất hiện sau. Mascot có lựa chọn đọc theo phần đang hiện. Việc mở không tự duyệt nội dung/bố cục. Muốn học sinh trả lời câu hỏi, dùng Lớp học; kết quả nằm trong **Lớp học → Kết quả lớp học**.

Thư viện có tìm/lọc, một nút biểu tượng đổi Danh sách/Thẻ lớn với trang đầu 16:9 và chọn nhiều bài để tải ZIP hoặc đưa vào thùng rác. Thuật ngữ & kiến thức dùng để tra cứu và quản lý cách dùng từ riêng. [Thay đổi thư viện và dạy học](docs/WORKFLOW_RC51.md). [Rà soát và tối ưu RC58](docs/AUDIT_RC58.md). [Trang chủ RC60](docs/HOME_RC60.md).

RC61 đưa thanh cuộn Trang chủ/Thư viện ra lề riêng, thu gọn phần hiển thị còn 6 px. Thư viện chỉ giữ một trạng thái ngắn: số bài, số kết quả lọc hoặc số bài đã chọn; giải thích chọn qua nhiều trang nằm trong chú thích khi rê chuột.

RC62 cho phép bấm nền, tên, thông tin hoặc ảnh bìa của bài trong Thư viện để chọn/bỏ chọn, ở cả danh sách và thẻ. Bài đã chọn có viền xanh; Mở bài/Tải/Sửa/Xóa vẫn là các thao tác riêng. Bấm ảnh bìa chọn bài; dùng **Mở bài** để xem bài.

RC63 rút gọn Google Dịch, hiển thị rõ số key và số nhóm đếm; tổng giới hạn tại máy tính theo nhóm, không nhân theo số Gmail/key. Bấm trạng thái bài giảng để xem lý do, kiểm tra/tự sửa kỹ thuật hoặc mở bước xác nhận của giáo viên. Tự sửa không tự duyệt bản dịch.

RC64 đồng bộ thanh cuộn mảnh ở các trang và hộp nội dung dài. Thanh trang nằm ở lề phải; khung nhập/xem có khoảng chừa riêng, không che chữ hoặc nút. Khung tải lên ở trang Chuyển đổi có hình PowerPoint ở bên trái, tự cân với phần hướng dẫn và nút chọn file.

RC65 bỏ khung tải lên lặp ở Trang chủ, dùng bộ icon cung cấp cho **Quy trình đơn giản**. Tab **Tạo giọng đọc bài giảng** nằm giữa Chuyển đổi và Bài giảng: chọn PowerPoint có sẵn hoặc bài trong thư viện, dùng cùng bộ tạo giọng; không tự dịch hay đổi thiết kế. Bài một ngôn ngữ chỉ tạo giọng ngôn ngữ đang có; bài Song ngữ cần lời Việt và Anh.

**Cài đặt → Dữ liệu → Chuyển thư viện sang nơi khác** chuyển cả bài, giọng, thuật ngữ và cấu hình vào `BiliClass-Data` dưới thư mục đã chọn. Xác minh, đóng sạch và mở lại với nơi mới; chỉ dọn các tệp cũ đã đối chiếu sau khi thư viện mới mở thành công. Nơi chọn được nhớ qua lần khởi động/cập nhật. Không tự chuyển dữ liệu thật khi nâng cấp. Hộp tải/xuất/sao lưu gợi ý tên tự động và nhớ thư mục lưu gần nhất; thầy cô vẫn chọn đích trước khi lưu.

500.000 ký tự không phải hạn mức riêng cho từng key. Bộ đếm BiliClass theo nhóm dự án chỉ phản ánh lượng dùng cục bộ; hãy đặt quota trong Google Cloud. Key mã hóa theo tài khoản Windows; không nằm trong bộ cài/repo công khai hoặc bản sao lưu thư viện. Chuyển key qua kho riêng tư là snapshot khi bấm, không đồng bộ quota trực tiếp giữa các máy.

## Cài và cập nhật

Cần Windows 10/11 64-bit, Internet khi dịch và Microsoft PowerPoint desktop để trình chiếu giữ hiệu ứng. Giải nén toàn bộ ZIP của bản đã kiểm chứng rồi chạy **Setup.cmd**; gói có runtime, model giọng, OCR và template, không cần Python/Codex.

**Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật** nhận bản đã công bố trên kênh phát hành. Bản dựng tại máy chưa công bố không tự xuất hiện ở đây. Dữ liệu mặc định ở `%LOCALAPPDATA%/BiliClass`, hoặc thư mục đã chọn trong Cài đặt → Dữ liệu; được giữ riêng khi cập nhật. [Thông tin bộ cài và giới hạn kiểm chứng RC72](docs/BUILD_RC72.md).

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

[Hướng dẫn sử dụng](docs/USER_GUIDE.md) · [Thử trên hai máy](docs/TEACHER_TESTING.md) · [Bốn kiểu chuyển đổi](docs/FOUR_FORMAT_WORKFLOW.md) · [Thư viện mẫu](docs/TEMPLATE_LIBRARY.md) · [Trạng thái kỹ thuật](docs/STATE.md) · [Rà soát & kế hoạch tối ưu RC55](docs/AUDIT_OPTIMIZATION_RC55.md) · [Thành phần bên thứ ba](docs/THIRD_PARTY.md).

Bản thử đã kiểm tra trên máy phát triển với Microsoft PowerPoint và Chrome. Cần thử thêm Windows sạch, máy ít RAM, máy chiếu/mạng lớp và chất lượng nhiều môn. Kiểm thử kỹ thuật không tự chứng nhận mọi bài giảng hoặc mọi tài khoản ChatGPT.
