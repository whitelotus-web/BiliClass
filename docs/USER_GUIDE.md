# BiliClass — Trợ lý dạy học song ngữ

Hướng dẫn RC66, ngày 17/10/2026. Bài giảng, giọng đọc và thư viện cá nhân lưu
trên máy. Chuyển đổi hiện dùng Google Cloud Translation cho phần chữ và dựng
PowerPoint tại máy; Browser ChatGPT/Gemini tạm ẩn.

## Cài và cập nhật

1. Tải **BiliClass-RC65-Windows.zip** tại
   [Release RC65](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc65).
2. Giải nén toàn bộ; không chạy trong cửa sổ ZIP. Chạy **Setup.cmd**.
3. Bộ cài kiểm tra checksum và cài vào
   `%LOCALAPPDATA%/Programs/BiliClass/1.0.0rc65`, không cần quyền quản trị.
4. Mở BiliClass từ Desktop hoặc Start menu. Bản cài có model giọng, OCR và
   template; không cần thư mục runtime của máy phát triển.

Máy đang dùng RC34: vào **Cài đặt → Thông tin BiliClass → Kiểm tra cập nhật**,
chọn Cập nhật khi thấy RC65. Nếu chưa kiểm tra được mạng, tải ZIP và chạy
Setup.cmd như trên. Các bản cài nằm cạnh nhau; thư viện ở
`%LOCALAPPDATA%/BiliClass` được giữ nguyên. Không xóa thư mục dữ liệu này.
Thư viện cá nhân không đưa lên GitHub. Key có thể nhận riêng như hướng dẫn dưới.

## Tạo bài giảng

1. Vào **Chuyển đổi bài giảng** ngay sau Trang chủ, chọn hoặc kéo thả PowerPoint
   `.pptx` tối đa 200 MB. Nút **Chọn file PowerPoint** và vùng kéo thả ở Trang chủ mở cùng luồng này.
2. Chọn môn, cấp/khối và **Song ngữ Việt–Anh** hoặc **Tiếng Anh 100%**.
3. Chọn giữ thiết kế PowerPoint gốc, hoặc tạo theo mẫu BiliClass/PowerPoint
   riêng. Mẫu Universal 2026 có ba phong cách; chọn xem mẫu để kiểm tra trước.
4. Cấu hình key ở **Cài đặt → Google Dịch**, lưu rồi chuyển đổi.
   Dịch chỉ gửi phần chữ; nội dung trong ảnh được OCR nếu nhận diện được.
5. Xem lại bài đã lưu. Công thức, chữ trong ảnh, hiệu ứng phức tạp và slide
   dày chữ vẫn cần đối chiếu. Bài còn lỗi chưa được coi là đã duyệt để dạy.

Key được lưu mã hóa theo tài khoản Windows. Nhiều key có thể dùng theo cấu
hình nhóm/hạn mức, nhưng 500.000 ký tự không phải số dư riêng được BiliClass
đọc từ mỗi key. Kiểm soát hạn mức và chi phí trong Google Cloud của dự án.

Màn Google Dịch hiện số key và số nhóm đếm riêng. Hai key trong cùng nhóm
vẫn có một giới hạn; hai nhóm đã cấu hình có tổng giới hạn tại máy bằng
tổng hai nhóm. Hai Gmail khác nhau không đủ để BiliClass xác nhận hai mức
miễn phí Google. [Bảng giá Google](https://cloud.google.com/products/translate/pricing)
và [API key gắn với dự án](https://docs.cloud.google.com/translate/docs/authentication).
Số dùng đã lưu được giữ nguyên, không chia đoán lại lịch sử theo từng key.
Ô nhập key ẩn sau khi lưu; bấm **Thêm key** để mở. Giới hạn tháng, OCR và
hướng dẫn đồng bộ nằm trong **Hướng dẫn & nâng cao**.

**Bài giảng** là thư viện: tìm, lọc, mở, tải và quản lý bài đã lưu. Đổi qua lại
giữa các mục vẫn giữ tài liệu/cấu hình đang nhập ở mục Chuyển đổi bài giảng.
Trang chủ có mascot lớn, vùng chọn/kéo thả tài liệu và hướng dẫn bốn bước.
Bài đang làm/bài gần đây, tác vụ và tình trạng ứng dụng nằm phía dưới;
bấm **Chi tiết** để xem thống kê dịch cục bộ.

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
đổi bộ đếm hay dự án. Key cùng dự án Google Cloud phải cùng tên nhóm dự án.
Key chỉ nhập riêng không có nhóm vẫn dùng chung bộ đếm lịch sử; hai Gmail
khác nhau không đủ để ứng dụng tự xác minh hai dự án.

Ứng dụng ưu tiên key theo thứ tự đã lưu. Khi Google xác nhận key bị từ chối
hoặc hết quota, chuyển key kế tiếp; lỗi mạng/tốc độ chỉ thử lại có giới hạn.
Khi một nhóm chạm giới hạn cục bộ, các key cùng nhóm đều ngừng nhận yêu cầu
mới. Bản dịch trong cache vẫn dùng lại mà không gửi Google.

**Trang chủ → Tình trạng ứng dụng** và **Cài đặt → Google Dịch** cho biết
ký tự đã ghi nhận trong tháng, phần còn lại theo giới hạn BiliClass và cảnh
báo 80%/95%. Đây là ước tính tại máy, không phải hạn mức/số dư thật từ Google,
không bao gồm máy khác. API key đơn thuần không cung cấp quyền đọc số dư
Cloud; xem quota/chi phí trong Google Cloud. Thông tin PowerPoint/gói giọng/
OCR chỉ xác nhận đã phát hiện thành phần, không thay cho kiểm tra hoạt động.

## Tạo giọng và bước tiếp theo

Giọng là bước tùy chọn sau khi bài đã lưu. Chọn một trong sáu giọng, nghe
thử, chọn tốc độ và tiếng Anh / tiếng Việt / Việt + Anh. Chọn ở đây không
thay cấu hình mặc định trong Cài đặt. Giọng chạy ngoại tuyến trên máy.

- Mỗi bản được phân biệt bằng nội dung, ngôn ngữ, giọng và tốc độ. Các bản
  đã tạo được giữ lại. Bản đã đủ hiện **Đã tạo**, khóa nút tạo trùng nhưng
  vẫn cho chọn để dùng/tải. Bản thiếu hiện **Tiếp tục tạo giọng**.
- Đổi giọng/tốc độ mở tạo bản mới. Nếu WAV bị thiếu/hỏng, tạo tiếp sẽ bổ sung
  phần thiếu. Bộ đếm thời gian chạy trong lượt tạo; không tự mở trình chiếu.
- Khi sẵn sàng, chọn **Tiếp tục: chuẩn bị dạy** ngay dưới phần giọng. Chọn
  đúng bản ở màn chuẩn bị rồi **Bắt đầu dạy**, hoặc tải PowerPoint.
- Bản Việt–Anh mới có ba nút EN, VI và VI+EN trên cùng slide khi nhúng được
  lời đọc tĩnh đã xác minh. Nút chung dùng lại WAV, không tổng hợp lần thứ ba.
  File đã nhúng phát được bằng PowerPoint mà không cần BiliClass.
- Đáp án ẩn và hiệu ứng chưa xác định không được đưa vào lời đọc cả slide.
  Trang không đủ khoảng trống/không có lời đọc tĩnh có thể không nhúng được;
  dùng BiliClass hoặc tải bản không kèm giọng trong trường hợp đó.

## Dạy và mascot

Chọn **Dùng để dạy** hoặc **Tiếp tục: chuẩn bị dạy**, kiểm tra bản giọng,
xác nhận nội dung rồi Bắt đầu dạy. Trình chiếu dùng Microsoft PowerPoint
cài trên máy. Giọng chỉ phát khi bấm đọc; đóng/đổi slide sẽ dừng hàng đợi.

Bấm **Mở trợ giảng nổi** để hiện mascot; bấm lại **Ẩn trợ giảng nổi** để ẩn.
Ẩn từ menu mascot cũng cập nhật trạng thái nút bên trái.

Mascot có nút mở bài và đọc Việt/Anh/chung. Các nút đọc trên mascot chỉ bật
khi có phiên trình chiếu đúng bài. Trong Cài đặt Mascot, chọn tự theo môn của
bài hoặc môn cố định rồi Lưu để áp dụng cho mascot nổi.

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
trong thư viện. BiliClass giữ nguyên PowerPoint và nhận diện lời đọc từ chữ
trên slide/ghi chú có nhãn Việt–Anh. Không tự dịch hoặc OCR ảnh trong bước
này. Chọn giọng, tốc độ và Anh/Việt/Song ngữ, nghe thử rồi tạo; dùng cùng bộ
xử lý với bước tạo giọng sau chuyển đổi. Bài một ngôn ngữ chỉ có lời đọc
ngôn ngữ đó. Bản giọng đủ được khóa tạo trùng, vẫn chọn để tải/dạy. Nhận lại
cùng file sẽ dùng bài đã nhập trước đó và giữ các bản giọng đã tạo.

1. Chọn file hoặc **Dùng bài trong thư viện**. Số slide có lời Việt/Anh
   hiện ngay sau khi nhận bài.
2. Chọn **Kiểm tra lời đọc**. Với PowerPoint nhập riêng để tạo giọng, có
   thể bổ sung/sửa lời Việt và Anh cho từng slide, kể cả slide ảnh. Lời đọc
   lưu riêng, giữ nguyên file và thiết kế gốc; không tự dịch/OCR. Ghi chú
   `VI:` hoặc `EN:` cũng có thể chỉ chứa một ngôn ngữ.
3. **Lưu lời đọc** trước khi đổi slide. Sửa lời làm bản giọng cũ cần cập
   nhật và yêu cầu xác nhận lại trước khi dạy. Slide không có lời sẽ được
   bỏ qua; màn hình cho biết số slide cần bổ sung. Với bài chuyển ngữ đã có
   trong thư viện, dùng **Thao tác khác → Sửa nội dung trợ giảng** để sửa.
4. Chọn giọng, tốc độ, ngôn ngữ và **Tạo giọng đọc**. **Dừng** giữ các đoạn
   đã xong; **Tiếp tục tạo giọng** chỉ tạo những đoạn còn thiếu/hỏng. Khi
   lỗi, thông báo nêu nguyên nhân để kiểm tra bộ giọng hoặc ổ đĩa rồi thử lại.
5. Khi sẵn sàng, tải **PowerPoint** có bản giọng đang chọn hoặc **Tải audio
   (.zip)** gồm WAV theo slide/ngôn ngữ, bản đọc chung Việt–Anh nếu đã chọn,
   và tệp lời đọc. ZIP dùng để phát thủ công, không tự đồng bộ hiệu ứng.
   Nếu slide không có vùng trống để chèn nút loa, có thể tải audio ZIP.

Nút nghe thử lời đọc phát tối đa 250 ký tự đầu của slide với giọng/tốc độ
đang chọn. Tạo xong không tự phát tiếng, tự duyệt hay tự mở trình chiếu.
**Tiếp tục: chuẩn bị dạy** mở bước xác nhận riêng trước khi dùng mascot.

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
