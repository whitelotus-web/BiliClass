# BiliClass — Trợ lý dạy học song ngữ

Hướng dẫn luồng RC75, ngày 18/10/2026. Bài giảng, giọng đọc và thư viện cá nhân lưu
trên máy. Chuyển đổi hiện dùng Google Cloud Translation cho phần chữ và dựng
PowerPoint tại máy; Browser ChatGPT/Gemini tạm ẩn.

## Cài và cập nhật

1. Tải **BiliClass-RC68-Windows.zip** tại
   [Release RC68](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc68).
2. Giải nén toàn bộ; không chạy trong cửa sổ ZIP. Chạy **Setup.cmd**.
3. Bộ cài kiểm tra checksum và cài vào
   `%LOCALAPPDATA%/Programs/BiliClass/1.0.0rc68`, không cần quyền quản trị.
4. Mở BiliClass từ Desktop hoặc Start menu. Bản cài có model giọng, OCR và
   template; không cần thư mục runtime của máy phát triển.

Máy đang dùng RC34: vào **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật**,
chọn Cập nhật khi thấy RC68. Nếu chưa kiểm tra được mạng, tải ZIP và chạy
Setup.cmd như trên. Các bản cài nằm cạnh nhau; thư viện ở
`%LOCALAPPDATA%/BiliClass` được giữ nguyên. Không xóa thư mục dữ liệu này.
Thư viện cá nhân không đưa lên GitHub. Key có thể nhận riêng như hướng dẫn dưới.

## Tạo bài giảng

1. Vào **Chuyển đổi bài giảng** ngay sau Trang chủ, chọn hoặc kéo thả PowerPoint
   `.pptx` tối đa 200 MB. Trang chủ có hướng dẫn quy trình và tổng hợp bài giảng; bước tải tài liệu dẫn vào mục Chuyển đổi.
2. Chọn môn, cấp/khối và **Song ngữ Việt–Anh** hoặc **Tiếng Anh 100%**.
   Môn mặc định lấy từ **Cài đặt → Chung → Bộ môn giảng dạy**, vẫn đổi được
   riêng cho bài đang làm. Cấp học và Khối lớp nhớ lần chọn gần nhất, kể cả
   sau khi đóng rồi mở lại BiliClass.
3. Chọn giữ thiết kế PowerPoint gốc, hoặc tạo theo mẫu BiliClass/PowerPoint
   riêng. Mẫu Universal 2026 có ba phong cách; chọn xem mẫu để kiểm tra trước.
   Khung tải tệp dùng cùng bố cục với Tạo giọng đọc: ảnh PowerPoint bên trái,
   hướng dẫn và nút chọn tệp bên phải. Cấu hình vẫn thu gọn trên cửa sổ thấp;
   có thể cuộn khi hiện nhiều trường. Chọn **Tùy chọn mẫu…** để mở mẫu riêng
   và vai trò trang; các lựa chọn này vẫn được giữ.
4. Cấu hình key ở **Cài đặt → Google Dịch**, lưu rồi chuyển đổi.
   Dịch chỉ gửi phần chữ; nội dung trong ảnh được OCR nếu nhận diện được.
5. Xem lại bài đã lưu. Công thức, chữ trong ảnh, hiệu ứng phức tạp và slide
   dày chữ vẫn cần đối chiếu. Bài còn lỗi chưa được coi là đã duyệt để dạy.

Key được lưu mã hóa theo tài khoản Windows. Mỗi key có bộ đếm cục bộ riêng,
mặc định tối đa **500.000 ký tự/key/tháng**. Ngay dưới key là **Còn lại /
tổng ký tự**, số đã dùng và thanh tiến độ. BiliClass kiểm tra trước mỗi
lượt gửi; nếu key không đủ cho cả lượt thì tự chuyển sang key còn mức.
Sang tháng mới tự dùng bộ đếm mới, giữ lịch sử tháng trước. Tháng tính UTC.

Đây là giới hạn tại BiliClass, không phải số dư được Google trả về. Key
vẫn gắn với dự án Google để tính hạn mức và thanh toán; xem [tài liệu Google](https://docs.cloud.google.com/translate/docs/authentication).
Lịch sử chung trước RC69 được giữ riêng vì chưa có chi tiết theo key; số
đếm từng key ghi từ RC69, không tự chia hoặc gán số cũ cho một key.
Trong tháng nâng cấp, tool trừ dự phòng phần lịch sử chung khỏi mức còn
lại của các key cũ để tránh vượt giới hạn. Dòng dưới key giải thích số dự
phòng; key mới thêm không bị trừ lịch sử cũ. Sang tháng mới mỗi key trở
lại đầy đủ mức đã đặt. Bộ đếm UTC này chưa đồng bộ báo cáo/chu kỳ Google.
Ô nhập key ẩn sau khi lưu; bấm **Thêm key** để mở. Giới hạn tháng, OCR và
hướng dẫn đồng bộ nằm trong **Hướng dẫn & nâng cao**.

**Bài giảng** là thư viện: tìm, lọc, mở, tải và quản lý bài đã lưu. Đổi qua lại
giữa các mục vẫn giữ tài liệu/cấu hình đang nhập ở mục Chuyển đổi bài giảng.
Trang chủ có mascot lớn, hướng dẫn bốn bước và tổng hợp bài giảng. Chuyển đổi
xong tự mở **Tạo giọng đọc bài giảng** với bài vừa tạo, khung chọn nguồn thu gọn.
Có thể **Tải PowerPoint không giọng** ngay, hoặc tạo giọng rồi tải bản có loa.

Sau khi tạo đủ giọng, bấm **Mở PowerPoint** để mở trực tiếp cùng Mascot,
không cần qua popup duyệt. Bấm **Trình chiếu (F5)** trên Mascot khi sẵn sàng.
**Kiểm tra slide và giọng** mở preview/nghe đúng audio đã lưu, không tạo lại.
Có thể tải PPTX/audio hoặc về đúng bài trong thư viện; không tự chuyển tab
hoặc tự phát khi hoàn tất. Nội dung/bố cục chưa rà soát vẫn giữ cảnh báo.

Loa trong PowerPoint đọc toàn bộ lời đã lưu của slide khi bấm, **kể cả phần
xuất hiện sau theo hiệu ứng**. Bản Việt–Anh có ba loa VI, EN, VI+EN. Âm thanh
nhúng trong file, dùng được độc lập. Mascot mặc định cùng cách đọc; chọn
**Đọc phần đang hiện theo hiệu ứng** nếu chỉ muốn đọc phần đã xác định hiện.
Phần chưa xác định không được đọc trong chế độ này. Nút **■ Dừng đọc** dừng
cả native audio và cache; đổi slide cũng dừng giọng cũ. Không sinh giọng trong
phiên dạy. Mascot gắn cố định với bài đang mở, xem bài khác không đổi liên kết.

Tên tải đã có sẵn: **Tên bài (Song ngữ Việt–Anh)** hoặc **Tên bài (Có giọng
Việt–Anh · Mai Anh · 100%)**. Đồng bộ ở tab Giọng, bài đã chuyển đổi và thư
viện/ZIP. Thông báo xuất nêu số slide có loa và trang còn thiếu lời/chỗ đặt;
slide chủ ý không đọc không được tính là đã có audio.

Chọn **Dạy** ở hàng bài giảng hoặc **Mở bài giảng để dạy** trong menu thẻ.
Trên Mascot nổi, **Chọn / đổi bài giảng** nhận bài thư viện hoặc file `.pptx`.
Chọn bài mở bước xác nhận; chỉ xác nhận mở mới thay bài đang gắn. **Kết
thúc trình chiếu** trả về trạng thái chờ, **Ngắt gắn bài** kết thúc phiên
điều khiển. Tệp PowerPoint nguồn không bị ghi đè.

Trong **Cài đặt → Dữ liệu → Quản lý thuật ngữ & kiến thức**, thuật ngữ đã khóa của đúng môn được ưu tiên
khi dịch Google. Đổi thuật ngữ làm mới riêng cache của câu có dùng từ đó;
các câu không liên quan vẫn dùng lại bản dịch cũ. Thuật ngữ chưa khóa và
kiến thức tham khảo không tự ghi đè bản dịch.

Máy thứ hai có thể vào **Cài đặt → Google Dịch → Nhận key từ GitHub**.
Cần Git for Windows và đăng nhập GitHub bằng Git Credential Manager, với quyền
truy cập kho riêng tư `whitelotus-web/BiliClass-Private-Config`. Không có mật
khẩu BiliClass bổ sung. Key được chuyển qua HTTPS rồi mã hóa bằng Windows
trên máy nhận, không chứa trong bộ cài hay repo mã nguồn công khai.
**Đồng bộ key lên GitHub** lưu/gộp cấu hình khi bấm; không chạy nền tự động.
Bộ đếm đã ghi nhận được giữ theo giá trị lớn hơn, nhưng hai máy sau đó vẫn
đếm riêng; không coi đây là đồng bộ trực tiếp quota. Đặt quota trong Google.

## Tên key, giới hạn dịch và Trang chủ

Key được đánh số tự động **Key 1, Key 2…**, giữ số khi đổi tên. Nếu có tên
đầu vào, tên hiện trong ngoặc; bấm **Đổi tên** để sửa tên phụ. Đổi tên không
đổi bộ đếm hay dự án. Xóa rồi thêm lại cùng key giữ số đã dùng trong tháng.
Tên dự án là thông tin nhận diện/đồng bộ, không gộp bộ đếm của các key.

Ứng dụng ưu tiên key theo thứ tự đã lưu. Khi Google xác nhận key bị từ chối
hoặc hết quota, chuyển key kế tiếp; lỗi mạng/tốc độ chỉ thử lại có giới hạn.
Khi một key chạm giới hạn cục bộ, tool dùng key khác; tất cả key hết mức thì
dừng gửi mới và giữ phần đã dịch. Lần gửi chưa rõ kết quả vẫn được tính,
không chuyển key để gửi lặp miễn phí. Cache vẫn dùng lại mà không gửi Google.

**Cài đặt → Google Dịch** cho biết
ký tự đã ghi nhận trong tháng, phần còn lại theo giới hạn BiliClass và cảnh
báo 80%/95%. Đây là ước tính tại máy, không phải hạn mức/số dư thật từ Google,
không bao gồm máy khác. API key đơn thuần không cung cấp quyền đọc số dư
Cloud; xem quota/chi phí trong Google Cloud. Thông tin PowerPoint/gói giọng/
OCR chỉ xác nhận đã phát hiện thành phần, không thay cho kiểm tra hoạt động.

## Tạo giọng và bước tiếp theo

Giọng là bước tùy chọn sau khi bài đã lưu. Chọn một trong sáu giọng, nghe
thử, chọn tốc độ và tiếng Anh / tiếng Việt / Việt + Anh. Chọn ở đây không
thay cấu hình mặc định trong Cài đặt. Giọng chạy ngoại tuyến trên máy.

- Lần đầu mặc định **Tiếng Anh**; lần sau nhớ lựa chọn ngôn ngữ gần nhất.
- Mỗi bản được phân biệt bằng nội dung, ngôn ngữ, giọng và tốc độ. Tạo đúng
  bản đã có mở popup **Dùng bản có sẵn / Tạo lại**. Dừng/lỗi tạo lại giữ WAV cũ.
- Đổi giọng/tốc độ tạo bản khác. Thiếu/hỏng WAV được bổ sung khi tạo tiếp.
  **Nghe thử** dùng câu mẫu Việt–Anh có sẵn, không phải lời của bài.
- Màn hoàn tất hiện số slide có lời cho cấu hình đã chọn; không đồng nhất
  số đoạn đủ WAV với đủ lời ở tất cả slide. Mở **Đổi cấu hình** khi cần tạo thêm.

## Dạy và mascot

Chọn **Dùng để dạy** hoặc **Mở bài giảng để dạy**, kiểm tra bản giọng,
xác nhận nội dung rồi Bắt đầu dạy. Trình chiếu dùng Microsoft PowerPoint
cài trên máy. Giọng chỉ phát khi bấm đọc; đóng/đổi slide sẽ dừng hàng đợi.

Bấm **Mở trợ giảng nổi** để hiện mascot; bấm lại **Ẩn trợ giảng nổi** để ẩn.
Ẩn từ menu mascot cũng cập nhật trạng thái nút bên trái.
Thu nhỏ BiliClass vẫn giữ Mascot nổi độc lập. **Cài đặt → Mascot → Luôn nổi
trên cùng** mặc định bật, giữ Mascot phía trên cửa sổ khác và trình chiếu.
Tắt lựa chọn này cho phép cửa sổ khác che Mascot; bấm **Lưu cài đặt Mascot**
để áp dụng. Bấm Escape chỉ thu gọn công cụ Mascot, không ẩn.

Mascot có nút mở bài và đọc Việt/Anh/chung. Các nút đọc trên mascot chỉ bật
khi có phiên trình chiếu đúng bài. Trong Cài đặt Mascot, chọn tự theo môn của
bài hoặc môn cố định rồi Lưu để áp dụng cho mascot nổi.

Khi cửa sổ trình chiếu hoặc Presenter View của bài đang gắn được chọn:

| Phím mặc định | Chức năng |
| --- | --- |
| Cách | Đọc tiếng Anh |
| Enter | Đọc tiếng Việt |
| Ctrl+Cách | Đọc hai ngôn ngữ |
| ← / → | Lùi / tiến hiệu ứng, hết hiệu ứng thì chuyển slide |
| ↑ / ↓ | Tăng / giảm âm lượng lời đọc 5% |
| Esc | Thoát trình chiếu |

Cùng phím/loa: bấm lần đầu phát, lần hai tạm dừng, lần tiếp theo đọc tiếp
từ chỗ dừng. Loa đang phát hiện hình Ⅱ; chỉ hiện ngôn ngữ thực có trên
slide. **Dừng đọc ■** dừng hẳn; **Đọc lại** phát lại từ đầu. Chọn ngôn ngữ
khác sẽ dừng giọng trước. Phím của giọng chưa có chỉ báo nhắc, không
chuyển slide hoặc tự tạo giọng.

Nhãn VI/EN/VI+EN nằm ở góc nút loa, giữ nguyên khi chuyển sang Ⅱ.
Bấm cả phần nhãn cũng được. Mép slide hẹp dùng dạng nút ngang nhỏ.

Đổi phím tại **Cài đặt → Mascot → Phím đọc khi trình chiếu** rồi Lưu.
Anh/Việt dùng một phím; hai ngôn ngữ dùng Ctrl, Alt hoặc Shift cùng một
phím. Không dùng trùng phím, Esc, F5 hoặc mũi tên. Có nút khôi phục mặc
định. **Hướng dẫn phím** trên Mascot luôn hiển thị phím đã lưu.

Ngoài cửa sổ bài đang gắn, phím giữ chức năng gốc. PPTX mở riêng vẫn
dùng loa/điều khiển native của PowerPoint; muốn dùng phím và badge động,
gắn file qua Mascot. Các phím này không được nhúng thành macro trong PPTX.

## Mascot đi theo bài nào?

Mở bài trong Thư viện → **Dùng để dạy** → hoàn tất chuẩn bị để mở
trình chiếu. Mascot liên kết với phiên PowerPoint đó; chọn đọc Anh, Việt
hoặc Việt–Anh để đọc phần lời đang chọn trên slide hiện tại. Dùng **Theo slide**
để đưa lựa chọn về slide đang chiếu. Chưa mở trình chiếu thì các nút đọc
bị khóa. Đóng trình chiếu sẽ ngừng đọc. Chọn môn trong Cài đặt Mascot đổi
phụ kiện theo cấu hình đã lưu, không chọn bài giảng hay khóa bài vĩnh viễn.

## Thư viện, lớp học và báo cáo

Nhãn trạng thái bài có thể bấm để xem lý do và cách xử lý:

- **N slide cần sửa**: kiểm tra kỹ thuật còn lỗi trên các slide đó. Chọn
  **Kiểm tra lại** hoặc **Tự sửa và kiểm tra**; chi tiết nêu số slide/lỗi.
- **Chờ xác nhận**: đã có nội dung song ngữ nhưng thầy cô chưa xác nhận
  cả bài. Xem bản trình chiếu, rồi **Xem và xác nhận để dạy**. Không cần
  duyệt từng đoạn nếu đã xem cả bài.
- **Chưa dịch đủ**: còn thiếu cặp Việt–Anh; mở **Xem/sửa nội dung** hoặc
  tiếp tục chuyển đổi. **Đã duyệt nội dung** và **Sẵn sàng dạy** phân biệt
  nội dung đã duyệt với bản hiện tại đã chốt.

Tự sửa xử lý lỗi kỹ thuật có thể sửa; không xác nhận thay giáo viên về ý
nghĩa, thuật ngữ hoặc độ đúng của bản dịch. Khi vẫn còn lỗi kỹ thuật, nút
xác nhận bị khóa. Bước xác nhận cuối dùng cơ chế duyệt/chốt đã có trước đây.

Trang chủ hiển thị việc đang làm và ba bài vừa cập nhật. **Bài giảng** là
thư viện đầy đủ: tìm không dấu, lọc môn/khối/trạng thái/giọng, sắp xếp và
phân trang. Bên phải Sắp xếp có một nút đổi kiểu xem: **4 ô vuông** khi đang xem thẻ,
**3 dòng ngang** khi đang xem danh sách. Bấm nút để đổi qua lại; thẻ có ảnh
trang đầu 16:9. Lựa chọn được lưu; ảnh nạp ở nền và giữ nguyên tỉ lệ slide gốc.
Ảnh đã nạp được giữ trong phiên để đổi tab/kiểu xem nhanh; sửa hoặc xóa bài
sẽ làm mới ảnh tương ứng. Sau khi mở lại ứng dụng vẫn cần xác minh cache.
Ô chọn, bộ lọc và tải nhiều bài dùng chung cho hai kiểu xem. Mở bài để chọn bản giọng rồi tải hoặc dạy. Xóa đưa vào Thùng rác,
có thể khôi phục.

**Lớp học** dùng khi muốn học sinh trả lời câu hỏi qua QR/địa chỉ mạng nội bộ.
Chọn bài và câu hỏi đã duyệt, mở lớp, cho học sinh vào cùng mạng rồi mở câu
hỏi. **Báo cáo** xem kết quả theo tiết; chỉ chuyển bài/tạo giọng chưa tạo ra
kết quả học sinh. **Thuật ngữ & kiến thức** quản lý thuật ngữ và kiến thức tham
khảo; khác với mascot nổi.

## Chuyển dữ liệu giữa máy

Tải PowerPoint cho người chỉ cần trình chiếu. Gói `.biliclass` phục vụ chia
sẻ bài/nội dung trợ giảng tùy chọn, có giới hạn kích thước và yêu cầu duyệt
lại trên máy nhận. Dùng Sao lưu / Khôi phục thư viện để chuyển dữ liệu cá
nhân; khôi phục tạo thư mục mới. Ứng dụng/model cài riêng, key nhập riêng.
Không đưa thư viện, câu trả lời học sinh hoặc API key lên GitHub.

## Chọn nhiều bài và tải từ thư viện

Mỗi bài có nút **Tải**. Một bài lưu nhiều bản giọng bên trong; không tạo bản
sao thư viện cho mỗi giọng. Dòng giọng chỉ tóm tắt Anh / Việt / Song ngữ.
Mở bài để chọn người đọc, tốc độ và bản giọng cần dùng trước khi tải.

Ô chọn luôn hiển thị trong Thư viện. Có thể tích ô hoặc bấm nền, tên, thông
tin, ảnh bìa của bài để chọn/bỏ chọn ở cả danh sách và thẻ; viền xanh báo
bài đã chọn. Các nút **Mở bài**, **Tải**, **Sửa**, **Xóa** và menu vẫn thực
hiện chức năng riêng. Kéo chuột trên bài không tính là bấm chọn. Thao tác
chọn này chỉ áp dụng trong Thư viện; Trang chủ giữ cách dùng trước đó.

Tích từng bài hoặc **Chọn tất cả**, rồi **Tải đã chọn**
hoặc **Xóa đã chọn**. Chọn tất cả áp dụng cho mọi kết quả của bộ lọc, kể cả
trang khác; đổi bộ lọc sẽ bỏ chọn. Xóa có xác nhận và đưa vào thùng rác để
khôi phục, không xóa file PowerPoint, âm thanh hoặc báo cáo.

Dòng trạng thái cạnh nút xóa hiện **10 bài** khi xem toàn bộ, **3 kết quả**
khi đang lọc, hoặc **Đã chọn 2 bài** khi tích bài. Rê chuột vào trạng thái
để xem tổng số, hoặc vào **Chọn tất cả** để xem phạm vi chọn. Không còn
hàng giải thích dài bên dưới; thanh cuộn mảnh nằm riêng ngoài lề nội dung.
Các trang Chuyển đổi, kết quả, Cài đặt, Lớp học, Báo cáo và kho thuật ngữ
cũng dùng thanh cuộn này. Khung nhập/xem dài chừa riêng một dải bên phải
để thanh không che chữ; kéo thanh hoặc lăn chuột đều sử dụng được.

Tải nhiều bài tạo một file ZIP, chứa PowerPoint với tên riêng và hướng dẫn
giọng. Có thể kèm bản giọng đang chọn nếu đã tạo đủ; bài thiếu/chưa có giọng
xuất không âm thanh. Tắt tùy chọn này để tải toàn bộ không kèm giọng. Không
tự tạo voice trong lúc tải; lỗi sẽ giữ tệp đích cũ để thử lại.

## Dạy tương tác và xem kết quả

Trong **Lớp học**, chọn bài, bấm **Kiểm tra và chốt bài** để chốt bản chuẩn bị, đặt
tên lớp/tiết, chọn mạng rồi **Mở lớp · Hiện QR**. Soạn và duyệt câu
hỏi qua nút tương ứng; chỉ câu đã duyệt được đưa vào lớp. Dạy slide/mascot
đơn thuần không cần mở lớp. Thiết bị học sinh và giáo viên cần cùng mạng.

Trong **Lớp học → Kết quả lớp học**, tìm theo tên lớp/bài/môn, lọc tiết đang mở/đã kết thúc,
chọn tiết để xem và xuất CSV. Mẫu ít hoặc chưa có câu trả lời không được
coi là kết luận mức hiểu bài. Báo cáo giữ snapshot tiết cũ khi bài thay đổi.

Trong **Cài đặt → Dữ liệu → Quản lý thuật ngữ & kiến thức**, tab **Thuật ngữ của tôi** có tìm không dấu,
lọc môn và phân trang. Tab **Kiến thức có nguồn** dùng để tra cứu và đưa
từng mục vào kho riêng; không tự duyệt toàn bộ gói kiến thức.

## Thùng rác

Trong Bài giảng → Chia sẻ & quản lý → Thùng rác, chọn từng bài hoặc Chọn
tất cả. Có Khôi phục đã chọn / Xóa đã chọn và Khôi phục tất cả / Xóa tất cả.
Mỗi bài cũng có nút Khôi phục và Xóa vĩnh viễn riêng. Xóa vĩnh viễn luôn
yêu cầu xác nhận số bài, xóa bản ghi và lịch sử chỉnh sửa; không khôi phục
được từ thùng rác. Báo cáo lớp, bản sao lưu và tệp nguồn/âm thanh dùng chung
được giữ lại. Tác vụ nhóm chỉ thực hiện khi tất cả bài vẫn còn trong thùng
rác; danh sách đổi hoặc còn tiết học đang mở thì báo lỗi để chọn lại.

## Hướng dẫn chi tiết lớp học và mascot

Xem [Lớp học, kết quả, thuật ngữ và mascot RC58](CLASSROOM_MASCOT_RC58.md):
quy trình sử dụng, điều kiện mạng, cách lưu/kết nối lại và các giới hạn đã kiểm.

## Cải tiến RC58

Kiểm tra tệp giọng trước khi tạo chạy nền, có trạng thái chờ và đồng hồ. Các
bản Anh, Việt và Song ngữ dùng chung đoạn âm thanh phù hợp nên không tạo lại
phần đã có. Mất hoặc hỏng WAV vẫn được phát hiện ở lượt kiểm tra tiếp theo.
Đổi cài đặt mascot hoặc thuật ngữ không làm quét lại giọng của mọi bài.

Khi bấm tạm đóng máy chủ lớp, giao diện tiếp tục phản hồi; đợi đóng xong mới
mở lại. Tiết chưa kết thúc và câu trả lời đã nhận vẫn có thể tiếp tục từ Kết
quả lớp học. Đóng ứng dụng vẫn chờ công việc đang ghi dữ liệu kết thúc an toàn.

RC58 giữ thư mục cài tùy chọn khi tự cập nhật. Nếu ổ lưu dữ liệu thiếu chỗ
tải, ứng dụng thử dùng thư mục cập nhật trên ổ cài đã xác minh còn đủ chỗ.
Không tự chuyển thư viện hoặc xóa bản cài/dữ liệu cũ.

## Trang chủ RC60

Lời chào, mascot lớn và ô thoại theo bố cục ảnh tham khảo. Nhân vật theo
lựa chọn Milo/Lumi đã lưu. Bấm **Chọn file PowerPoint** hoặc kéo thả tệp để vào
Chuyển đổi bài giảng. Khi đang tạo giọng/chuyển đổi, nút đổi thành **Xem tiến
độ** và tạm ngừng nhận tệp mới. Cuộn xuống để mở lại bài, vào lớp hoặc xem
chi tiết tình trạng ứng dụng.

Màn Chuyển đổi bỏ số thứ tự 01/02 và nút trở về Thư viện ở góc phải. Các
bộ đọc Word/PDF/ảnh vẫn trong mã nguồn để phát triển một luồng tạo bài riêng;
không nằm trong bộ chọn tệp PPTX chính hiện tại.


## Tổng quan bài giảng ở Trang chủ

Trang chủ có **Tổng quan bài giảng**: tổng bài, số bài sẵn sàng dạy, đã có
giọng và cần hoàn thiện; bên dưới là ba bài vừa cập nhật để mở nhanh. Nút
**Mở thư viện** đưa tới toàn bộ bài. Mức dùng dịch và trạng thái hệ thống
xem trong Cài đặt. Khung tiến độ chỉ hiện khi còn tác vụ đang chạy.

## Tạo giọng cho PowerPoint có sẵn

Mở **Tạo giọng đọc bài giảng** trên thanh bên, chọn `.pptx` hoặc chọn bài
trong thư viện. Có thể bấm **Dạy cùng Mascot** ở Quy trình đơn giản trên
Trang chủ để mở thẳng tab này. Có thể chọn giọng, tốc độ và kiểu Anh/Việt/
Việt–Anh ngay cả trước khi chọn bài; cấu hình giữ lại sau khi nhận file.
Nút tạo chỉ bật khi bài có lời phù hợp với ngôn ngữ chọn. BiliClass giữ
nguyên PowerPoint và nhận diện lời đọc từ chữ
trên slide/ghi chú có nhãn Việt–Anh. Không tự dịch hoặc OCR ảnh trong bước
này. Chọn giọng, tốc độ và Anh/Việt/Song ngữ, nghe thử rồi tạo; dùng cùng bộ
xử lý với bước tạo giọng sau chuyển đổi. Bài một ngôn ngữ chỉ có lời đọc
ngôn ngữ đó. Lần đầu mặc định **Tiếng Anh**; lần sau nhớ
ngôn ngữ chọn gần nhất. Ô **Cấu hình đã chọn** diễn giải ngôn ngữ/giọng/tốc
độ và các nút loa sẽ có trong PowerPoint. Khi bấm **Tạo giọng đọc** mà đúng
cấu hình đã đủ âm thanh, chọn **Dùng bản có sẵn** hoặc xác nhận **Tạo lại**.
Tạo lại thất bại hoặc dừng vẫn giữ âm thanh cũ. Nhận lại
cùng file sẽ dùng bài đã nhập trước đó và giữ các bản giọng đã tạo.

**Tạo giọng đọc** nằm ở thanh cuối trang, cùng vị trí với **Chuyển đổi bài
giảng**. **Dừng ■** và **Hủy bài đang chọn ×** có màu đỏ; dừng giữ phần đã
tạo, hủy chọn giữ bài trong thư viện. Trong lúc tạo giọng, không bắt đầu
chuyển đổi bài mới. Tab Chuyển đổi ghi rõ tác vụ đang chạy; **Xem tiến độ
tạo giọng** quay lại tab giọng mà không đổi bài hay dừng tác vụ.

Tab Chuyển đổi có ô diễn giải cập nhật theo kiểu ngôn ngữ, giữ thiết kế/mẫu
mới và môn/lớp. Thiết lập Google Dịch và hạn mức nằm trong Cài đặt; thanh
thao tác không còn lặp lối tắt trạng thái hạn mức.

1. Chọn file hoặc **Dùng bài trong thư viện**. Số slide có lời Việt/Anh
   hiện ngay sau khi nhận bài.
2. BiliClass tự kiểm tra số slide có lời theo ngôn ngữ đang chọn; chỉ hiện
   nhắc khi có slide thiếu lời. Muốn xem hoặc sửa, mở **Thao tác khác →
   Kiểm tra / sửa lời đọc**. Có thể bổ sung/sửa trực tiếp lời Việt và Anh cho
   từng slide của bài nhập riêng hoặc bài đã chuyển đổi, kể cả slide ảnh. Lời đọc
   lưu riêng, giữ nguyên file và thiết kế gốc; không tự dịch/OCR. Ghi chú
   `VI:` hoặc `EN:` cũng có thể chỉ chứa một ngôn ngữ. Tool tự tách các dòng
   theo nhãn và rà lại bài cũ bị gộp hai ngôn ngữ; giữ dòng tiêu đề/công thức.
3. **Lưu lời đọc** trước khi đổi slide. Sửa lời làm bản giọng cũ cần cập
   nhật và yêu cầu xác nhận lại trước khi dạy. Slide không có lời sẽ được
   bỏ qua; màn hình ghi rõ thiếu lời Việt hay Anh. Bấm **Kiểm tra / bổ sung**
   để mở ngay slide cần xử lý. Thay đổi ở đây chỉ sửa lời đọc riêng; muốn sửa
   chữ hiển thị trên slide vẫn dùng phần chỉnh nội dung bài giảng.
4. Chọn giọng, tốc độ, ngôn ngữ và **Tạo giọng đọc**. **Dừng** giữ các đoạn
   đã xong; **Tiếp tục tạo giọng** chỉ tạo những đoạn còn thiếu/hỏng. Khi
   lỗi, thông báo nêu nguyên nhân để kiểm tra bộ giọng hoặc ổ đĩa rồi thử lại.
   **Hủy bài đang chọn** dừng an toàn rồi trở về bước chọn nguồn, giữ bài
   trong thư viện và âm thanh đã tạo. Các chế độ đều hiện trạng thái; chế
   độ không có nội dung sẽ ghi **Chưa có lời đọc**.
5. Khi sẵn sàng, tải **PowerPoint** có bản giọng đang chọn hoặc **Tải audio
   (.zip)** gồm WAV theo slide/ngôn ngữ, bản đọc chung Việt–Anh nếu đã chọn,
   và tệp lời đọc. ZIP dùng để phát thủ công, không tự đồng bộ hiệu ứng.
   Nếu slide không có vùng trống để chèn nút loa, có thể tải audio ZIP.

Nút nghe thử lời đọc phát tối đa 250 ký tự đầu của slide với giọng/tốc độ
đang chọn. Tạo xong không tự phát tiếng, tự duyệt hay tự mở trình chiếu.
**Mở bài giảng để dạy** mở bước xác nhận riêng trước khi dùng Mascot.
**Nghe thử** đổi thành **Dừng nghe** trong lúc phát. Khi giọng sẵn sàng,
chỉ một khu vực tải/mở dạy được hiển thị; muốn lấy bản không giọng, mở
**Thao tác khác → Bài giảng → Tải PowerPoint không giọng…**. Các thao tác
mở PowerPoint, xác nhận nội dung và gửi gói bài vẫn có trong nhóm Bài giảng.

## Chuyển toàn bộ thư viện sang ổ khác

Ứng dụng cài riêng với dữ liệu. Dữ liệu mặc định nằm trong
`%LOCALAPPDATA%/BiliClass`; không cần lưu bài và voice cùng ổ cài ứng dụng.

1. Hoàn tất tác vụ và đóng trình chiếu/lớp học/đọc thử.
2. Mở **Cài đặt → Dữ liệu → Chuyển thư viện sang nơi khác**.
3. Chọn ổ/thư mục chứa dữ liệu, ví dụ `D:/DayHoc`; đích sẽ là
   `D:/DayHoc/BiliClass-Data`. Đích cần chưa tồn tại, đủ dung lượng; không
   trộn với thư viện khác.
4. Xem đường dẫn rồi chọn **Chuyển và mở lại**. BiliClass sao chép/kiểm tra,
   đóng các kết nối, cập nhật đường dẫn nội bộ và mở lại với thư viện mới.
5. Bản cũ chỉ dọn các tệp đã đối chiếu sau khi thư viện mới mở thành công;
   tệp cũ thay đổi bởi tác vụ khác được giữ. Cấu hình vị trí nhỏ vẫn ở nơi
   mặc định; runtime phát triển/cập nhật/log không chuyển cùng thư viện.

Nơi lưu được nhớ ở lần mở sau và khi nâng cấp. Nếu dùng ổ rời, kết nối lại
ổ đó trước khi mở BiliClass; không tự tạo thư viện trống thay thế khi mất
ổ. Key mã hóa vẫn dùng trên cùng tài khoản Windows, không biến thành key
công khai. **Mở thư viện khác** cũng mở lại ứng dụng để mọi bộ xử lý dùng
đúng thư mục, thay vì chỉ đổi danh sách bài trong cửa sổ hiện tại.

Khi **Tải/Xuất/Sao lưu**, hộp chọn lưu có sẵn tên theo bài/bộ bài/bản giọng
hoặc ngày sao lưu. Tên loại ký tự không hợp lệ; gợi ý thêm số nếu đã có
file cùng tên. Chọn nơi lưu và BiliClass nhớ thư mục cho lần sau. Nếu đổi
sang một tên đã có, hộp lưu Windows vẫn hỏi trước khi ghi đè. Báo cáo CSV
có tên lớp/tiết và phân biệt kết quả với từng phản hồi.
