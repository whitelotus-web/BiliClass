# BiliClass

Ứng dụng Windows chuyển tài liệu của giáo viên thành bài giảng Anh–Việt, rồi trình chiếu bằng PowerPoint với giọng đọc và mascot trợ giảng. Hỗ trợ cấu hình từ lớp 1 đến lớp 12 và môn tự nhập.

## Phiên bản và tải xuống

Đã phát hành **[RC172 cho Windows](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc172)**.
Mốc mã ứng dụng: tag `v1.0.0rc172`; bộ cài và kiểm chứng ở
[BUILD_RC172.md](docs/BUILD_RC172.md). Dự án đang tạm gác sau mốc này;
[hướng dẫn mở lại](docs/PROJECT_HANDOFF_RC172.md) và
[sơ đồ thư mục đã gom trên máy](docs/PROJECT_STORAGE.md).

### Ghi chú các mốc trước

Nhánh thử **RC169** thêm [Word song ngữ theo vùng chọn và dịch vụ dự phòng](docs/WORD_RC169.md).
RC172 thêm [chuyển đổi nhiều file Word bằng Dịch toàn bộ](docs/WORD_BATCH.md).
Word có bốn kiểu trình bày, xem/sửa trước khi lưu và xuất hiện cùng PowerPoint
trong thư viện, có icon W/P và tab lọc Word. Dịch vụ chính
tạm lỗi sẽ thử dịch vụ đã cấu hình tiếp theo, giữ phần đã đạt. Đây là bản nguồn
để dùng thử; chưa tạo bộ cài RC169 và không thay bộ cài RC167.

Nhánh thử **RC168** thêm bốn lựa chọn dịch và
[thuật ngữ theo môn, bộ nhớ tham khảo](docs/TRANSLATION_KNOWLEDGE_RC168.md).
Kho mở rộng có 1.152 khái niệm, khoảng 0,98 MB dữ liệu tham chiếu, tự đối chiếu
thuật ngữ và thử sửa phần chưa dịch đủ trong nền. RC167 vẫn được giữ làm
mốc ổn định tạm; chưa đóng gói bộ cài mới cho phần nâng cấp này.

**[Tải BiliClass cho Windows](https://github.com/whitelotus-web/BiliClass/releases)** · [RC155 đã kiểm chứng](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc155) · [Hướng dẫn sử dụng](docs/USER_GUIDE.md)

Mã nguồn **RC159 đang chờ giáo viên thử**, chưa tạo gói cài mới.
Sửa ngắt OCR do ảnh khai báo quá lớn và bổ sung sửa bản dịch mất dấu
giữ công thức bằng cách dịch riêng phần chữ. Khi tạo giọng, file kết
quả tự lưu được cập nhật tại chỗ; giữ file gốc và bản giáo viên đã sửa.
Nút Dừng của hàng đợi nằm cạnh Đang xử lý trên thanh dưới.
[Phạm vi RC159](docs/REVIEW_RC159.md).

RC158 căn chỉnh xem trước và sao lưu:
Cụm chuyển slide ở khung xem trước được căn giữa cả khi có nút nghe;
cửa sổ hẹp tự xuống hàng để các nút không chồng nhau. Bản sao lưu mới
chỉ chứa một bản cho mỗi nội dung trùng, khi khôi phục vẫn tạo đủ tệp
ở đúng thư mục. Đọc được các bản sao lưu cũ.
[Phạm vi RC158](docs/REVIEW_RC158.md).

RC157 sửa màn hình hoàn tất:
Chuyển đổi/tạo giọng nhiều bài giữ màn hình hoàn tất với từng kết quả,
**Xem bài**, **Mở thư mục** và **Về Thư viện**; không trở về màn tải file
trống. Giữ kết quả khi đổi trang, mở lại tool hoặc hủy chọn lượt mới.
Thư viện bỏ chiều cao cuộn thừa khi không có kết quả; tìm kiếm, sắp xếp
và đổi trang về đầu danh sách. Tiêu đề/lề Cài đặt theo cùng kích thước
với hai công cụ. Đã rà soát luồng đang dùng bằng 1.585 pytest và các
kiểm tra Qt trên dữ liệu riêng.
[Phạm vi RC157](docs/REVIEW_RC157.md).

RC156 làm gọn hướng dẫn và thư viện:
F1 có bốn bước bắt đầu, tìm kiếm không dấu và hình hướng dẫn phím/chuột.
Thẻ thư viện đều chiều cao, các nút cùng hàng; loa thẳng lề phải ảnh,
thùng rác ở cuối thanh công cụ. Trên máy phát triển, mở bản nguồn bằng
**Chay-BiliClass.cmd** trong thư mục dự án.
[Phạm vi RC156](docs/REVIEW_RC156.md).

RC155 cân chỉnh giao diện Chuyển đổi/Tạo giọng ở trạng thái
chưa tải file, một bài và nhiều bài. Lăn chuột trong bảng Mascot
chuyển hiệu ứng/slide; vùng âm lượng tăng/giảm 5%. Trợ giúp thêm
hình chuột và chỉ dẫn trực quan. [Phạm vi RC155](docs/BUILD_RC155.md).

RC154 đặt chuyển slide ngay dưới hình thu nhỏ ở cả một/nhiều
bài, không cần phóng to. Nút xem trước đồng nhất và hàng đợi bỏ
khung trắng bao ngoài. [Phạm vi RC154](docs/BUILD_RC154.md).

RC153 thống nhất đầu vào nhiều bài ở Chuyển đổi và Tạo giọng:
hàng đợi trên cấu hình, chọn từng bài để xem trước; mỗi bài có số
slide, mở PowerPoint và nút bỏ riêng. Icon tab nhỏ hơn, thứ tự chồng
đúng kiểu hồ sơ; màn khởi động gọn hơn. [Phạm vi RC153](docs/BUILD_RC153.md).

RC152 thay các icon tab theo mẫu, cho tab đang chọn nền xanh,
chữ/icon trắng, đuôi chồng nhẹ và bóng mỏng. Menu từng bài thêm
**Mở trong Explorer** để tìm file đã lưu. [Phạm vi RC152](docs/BUILD_RC152.md).

RC151 thêm tích chọn nhiều bài ngay ở màn Tạo giọng, giữ
hàng đợi đúng công cụ và tự ẩn khi cả lượt đã hoàn tất. Thư viện
có tab kẹp file thấp gọn, cạnh phải vát nhẹ, kèm icon/số bài; menu ba chấm và nút tải/xóa bằng icon. [Phạm vi RC151](docs/BUILD_RC151.md).

RC149 giữ đúng bài đã chọn trong Mascot khi thư viện cập nhật
hoặc đổi thứ tự, tránh mở nhầm bài ở vị trí cũ; bài đã xóa không tự
thay bằng bài khác. [Phạm vi RC149](docs/BUILD_RC149.md).

RC148 thêm ba nhóm **Tất cả / Chưa có giọng / Đã có giọng**,
**Tạo giọng đã chọn** và **Mở bài từ máy** trong Thư viện. Hàng đợi
hiện ngay trong cấu hình, có thời gian từng bài/tổng lượt. Nghỉ giữa
đoạn tăng lên 1,1 giây; giữ đơn vị số mũ khi dịch và cải thiện cách
đọc công thức cấu tạo. [Phạm vi RC148](docs/BUILD_RC148.md).

RC147 chọn nhiều PowerPoint và xử lý lần lượt ở cả **Chuyển đổi** và
**Tạo giọng đọc**; có Dừng/Tiếp tục, chỉ thử lại bài lỗi và giữ phần
đã làm khi mở lại tool. Từng bài tự lưu cạnh đúng file đầu vào,
không ghi đè. [Kiểm chứng và phạm vi RC147](docs/BUILD_RC147.md).

RC146 tự lưu PowerPoint có giọng cạnh file đầu vào khi hoàn tất, giữ file
gốc và các bản đã sửa; có đường dẫn và **Mở thư mục**. Loa trên slide
được vẽ sớm trước bước chuẩn bị media của Office. **Tải về** vẫn chọn
nơi lưu như trước. [Kiểm chứng và phạm vi RC146](docs/BUILD_RC146.md).

RC145 gộp nghe/dừng thành một nút cho mỗi ngôn ngữ; thêm **Hoàn tác xóa**
cạnh **Chia sẻ & quản lý** và icon xóa trong trang xem bài. Xóa/khôi phục
chạy nền, giữ nguồn và WAV. [Kiểm chứng RC145](docs/BUILD_RC145.md).

RC144 tự căn chữ trong từng ô bảng và sửa tương phản khi có bằng chứng,
rồi kiểm tra lại trước khi hoàn thành. Ghi chú chung về ảnh, công thức
và hiệu ứng nằm trong chi tiết; chỉ lỗi cụ thể chưa xử lý xong mới được
nêu nổi bật. Hai công cụ Chuyển đổi và Tạo giọng đọc dùng chung cách
hiển thị. [Phạm vi và kiểm chứng RC144](docs/BUILD_RC144.md).

Gói RC155 đã phát hành từ commit `fe69c0e`, được kiểm tra ZIP, cài và
mở Trang chủ. Mã nguồn và gói tải có vòng phát hành riêng: phiên bản
gói luôn được ghi rõ trong Releases và trong ứng dụng. Các mốc bên
dưới là lịch sử, không phải phiên bản hiện tại.

### Các mốc trước — RC105 trở về trước

RC105 làm gọn loading, bỏ dãy vòng tròn cuối màn hình, chỉnh thanh chuyển
động nhẹ và chuyển sang cửa sổ chính bằng hiệu ứng mờ ngắn. Tôn trọng
lựa chọn tắt chuyển động của Windows. [Kiểm chứng RC105](docs/BUILD_RC105.md).

RC104 thêm màn hình khởi động theo ảnh minh họa được cung cấp, cập nhật
theo bước và tự đóng khi cửa sổ chính vẽ xong. F1 mở hướng dẫn đọc theo
mục, bắt đầu từ bốn cài đặt ban đầu; ghi nhớ mục đang đọc và giữ nguyên
màn hình làm việc. Mascot có ba ô chọn cách đọc ngay trên một hàng.
[Kiểm chứng RC104](docs/BUILD_RC104.md).

RC103 chỉ hiện cửa sổ chính sau khi QML dựng xong và trở về vòng lặp
sự kiện, tránh cửa sổ hiện quá sớm trong lần khởi động nguội.
[Kiểm chứng RC103](docs/BUILD_RC103.md).

RC102 đưa xóa/khôi phục bài và đọc/lưu cấu hình Google Dịch sang chạy nền.
Giao diện báo đang xử lý trong lúc chờ ổ đĩa/cơ sở dữ liệu; thao tác ghi
nguyên khối không bị bấm lặp hoặc báo hủy sau khi đã lưu. Lỗi lưu key giữ
nguyên nội dung nhập. [Kiểm chứng RC102](docs/BUILD_RC102.md).

RC101 thu gọn giao diện bản nộp: chuyển đổi PowerPoint, thư viện, giọng Việt–Mỹ
và Mascot điều khiển trình chiếu. Lớp học, kết quả và các công cụ trợ giảng thử
nghiệm được ẩn trong bản đóng gói, kể cả Cài đặt; mã và dữ liệu vẫn giữ để phát
triển sau. [Phạm vi RC101](docs/BUILD_RC101.md) · [Hướng dẫn hiện tại](docs/USER_GUIDE.md).

RC100 làm gọn thư viện, cố định tìm kiếm/tác vụ, kéo/Shift chọn nhiều bài,
xem trước sau chuyển đổi và tải theo tên bài. Cặp giọng gần nhất được nhớ;
nghe thử và tạo dùng đúng giọng Việt/Mỹ theo ngôn ngữ. Cài đặt dữ liệu có ba
tác vụ chính; chuột phải Mascot có bánh răng và mắt gạch chéo.
[Kiểm chứng RC100](docs/BUILD_RC100.md).

### Các mốc trình chiếu trước

RC83 trả bàn phím về PowerPoint đang gắn khi bấm Mascot/điều khiển. Nút Trước/Sau chuyển ngay slide, bộ đếm theo Office; phím ←/→ vẫn chạy từng hiệu ứng. Chỉ hiện nút đọc theo giọng trên slide. Rê dấu ? xem bảng phím với Space ␣, Enter ↵ và Ctrl + Space ␣. Lệnh chuyển slide đi thẳng tới helper; trạng thái Office không làm mới toàn giao diện, lưu Mascot chạy nền. [Kiểm chứng RC83](docs/BUILD_RC83.md).

RC83 gồm cả thay đổi RC82 đã dựng nội bộ: kéo bảng trợ giảng cùng Mascot, nhấp đúp vùng trống/tiêu đề để thu bảng. Đóng BiliClass tắt cả Mascot; thu nhỏ vẫn giữ Mascot, “−” chỉ ẩn. Bỏ ba công tắc Hiện; chọn phụ kiện theo môn bằng danh sách, độc lập với môn bài giảng. [Kiểm chứng RC82](docs/BUILD_RC82.md).

RC81 tách **Mở PowerPoint** và **Tạo giọng đọc** trong Thư viện. Các nút mở sau chuyển đổi, trước/sau tạo giọng và trong Thư viện đều mở bài và gắn Mascot trực tiếp, giữ nguyên trang; bấm F5 khi sẵn sàng. Mỗi phiên dùng bản sao riêng để tránh khóa nguồn/cache. [Kiểm chứng RC81](docs/BUILD_RC81.md) · [Hướng dẫn sử dụng](docs/USER_GUIDE.md).

Mascot mặc định phải dưới, kéo để di chuyển. Nhỏ/Vừa/Lớn điều chỉnh cả nhân vật và bảng trợ giảng; nền trong tự lưu ở nền, chữ/nút giữ rõ. Cách = Anh, Enter = Việt, Ctrl+Cách = hai ngôn ngữ; ←/→ điều hướng, ↑/↓ âm lượng. Gán phím tại Cài đặt → Mascot.

Loa VI/EN/VI+EN chỉ hiện theo âm thanh thực có, nhãn ghép ở góc biểu tượng. Bấm phát/tạm dừng/đọc tiếp; đổi ngôn ngữ dừng giọng trước. [Kiểm chứng kiểu loa](docs/BUILD_RC75.md). Bản dựng tại máy và bản trên GitHub Releases có vòng phát hành riêng; xem version trong ứng dụng/gói đang dùng.

BiliClass dùng **Google Cloud Translation** dịch phần chữ và sắp xếp PowerPoint tại máy. Browser ChatGPT/Gemini tạm ẩn. Giọng Việt và giọng Mỹ chạy ngoại tuyến, là bước tùy chọn sau khi đã có bài song ngữ.

1. Cài đặt → Google Dịch: thêm key, mỗi dòng một key, rồi lưu. Key chỉ lưu mã hóa trên máy, không đồng bộ hay tải lên GitHub.
2. Chọn PowerPoint `.pptx` tối đa 200 MB, chọn **Song ngữ Việt–Anh** hoặc **Tiếng Anh 100%**; giữ thiết kế gốc hoặc chọn một trong các mẫu BiliClass có sẵn.
3. Chuyển đổi và xem lại bài. Song ngữ cùng slide tự chọn cách xếp theo vùng; vùng quá kín có thể dùng trang tiếp nối song ngữ. Hình, công thức, nội dung OCR và hiệu ứng phức tạp vẫn cần đối chiếu.
4. Tải PowerPoint ngay hoặc chọn người đọc/tốc độ để tạo giọng Anh, Việt hay Việt–Anh. Lần đầu mặc định Tiếng Anh, lần sau nhớ lựa chọn gần nhất. Tạo trùng có popup dùng lại/tạo lại. Tên tải có sẵn tên bài và ngôn ngữ/bản giọng trong ngoặc.
5. Bấm **Mở PowerPoint** để mở/gắn Mascot dù có hoặc chưa có giọng; F5 bắt đầu trình chiếu. Khi đủ giọng, có thể nghe/dừng theo ngôn ngữ trong màn kết quả, tải PPTX/audio hoặc xem trong Bài giảng. Loa đọc trọn lời đã lưu của slide khi bấm, kể cả phần xuất hiện sau. Mascot có lựa chọn đọc theo phần đang hiện. Việc mở không tự chứng nhận mọi nội dung/bố cục.

Thư viện có tìm/lọc, một nút biểu tượng đổi Danh sách/Thẻ lớn với trang đầu 16:9 và chọn nhiều bài để tải ZIP hoặc đưa vào thùng rác. Thuật ngữ & kiến thức dùng để tra cứu và quản lý cách dùng từ riêng. [Thay đổi thư viện và dạy học](docs/WORKFLOW_RC51.md). [Rà soát và tối ưu RC58](docs/AUDIT_RC58.md). [Trang chủ RC60](docs/HOME_RC60.md).

RC61 đưa thanh cuộn Trang chủ/Thư viện ra lề riêng, thu gọn phần hiển thị còn 6 px. Thư viện chỉ giữ một trạng thái ngắn: số bài, số kết quả lọc hoặc số bài đã chọn; giải thích chọn qua nhiều trang nằm trong chú thích khi rê chuột.

RC62 cho phép bấm nền, tên, thông tin hoặc ảnh bìa của bài trong Thư viện để chọn/bỏ chọn, ở cả danh sách và thẻ. Bài đã chọn có viền xanh; Mở bài/Tải/Sửa/Xóa vẫn là các thao tác riêng. Bấm ảnh bìa chọn bài; dùng **Mở bài** để xem bài.

Google Dịch giữ các thao tác nhập/lưu key, hướng dẫn và bộ đếm cục bộ theo key. Bấm trạng thái bài giảng để xem lý do, kiểm tra/tự sửa kỹ thuật hoặc mở bước xác nhận của giáo viên. Tự sửa không tự duyệt bản dịch.

RC64 đồng bộ thanh cuộn mảnh ở các trang và hộp nội dung dài. Thanh trang nằm ở lề phải; khung nhập/xem có khoảng chừa riêng, không che chữ hoặc nút. Khung tải lên ở trang Chuyển đổi có hình PowerPoint ở bên trái, tự cân với phần hướng dẫn và nút chọn file.

RC65 bỏ khung tải lên lặp ở Trang chủ, dùng bộ icon cung cấp cho **Quy trình đơn giản**. Tab **Tạo giọng đọc bài giảng** nằm giữa Chuyển đổi và Bài giảng: chọn PowerPoint có sẵn hoặc bài trong thư viện, dùng cùng bộ tạo giọng; không tự dịch hay đổi thiết kế. Bài một ngôn ngữ chỉ tạo giọng ngôn ngữ đang có; bài Song ngữ cần lời Việt và Anh.

**Cài đặt → Dữ liệu → Chuyển thư viện sang nơi khác** chuyển cả bài, giọng, thuật ngữ và cấu hình vào `BiliClass-Data` dưới thư mục đã chọn. Xác minh, đóng sạch và mở lại với nơi mới; chỉ dọn các tệp cũ đã đối chiếu sau khi thư viện mới mở thành công. Nơi chọn được nhớ qua lần khởi động/cập nhật. Không tự chuyển dữ liệu thật khi nâng cấp. Hộp tải/xuất/sao lưu gợi ý tên tự động và nhớ thư mục lưu gần nhất; thầy cô vẫn chọn đích trước khi lưu.

Bộ đếm BiliClass chỉ phản ánh lượng dùng cục bộ, không phải số dư Google Cloud. Key mã hóa theo tài khoản Windows; không nằm trong bộ cài, repo hoặc bản sao lưu thư viện, không có luồng chuyển key qua GitHub.

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
