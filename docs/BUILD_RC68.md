# RC68 — Từ chuyển đổi tới giọng đọc và phiên dạy gắn với Mascot

Ngày 17/10/2026. Giữ các tab hiện tại; không có tab Dùng để dạy mới.

## Luồng đã thực hiện

Hai đường chuyển đổi Google và Browser chuyển kết quả thành công sang `voice`.
Bài vừa tạo dùng cùng vùng cấu hình của bài chọn từ thư viện, chọn nguồn thu
gọn. Có đường tải bản không giọng riêng, không đổi bản giọng đang chọn. Giữ
các cấu hình, bộ đếm, bản giọng, tải audio ZIP và PowerPoint có loa hiện có.

Nút sau khi tạo giọng đổi thành **Mở bài giảng để dạy**. Giữ xác nhận nội
dung và lựa chọn bản giọng trước khi mở. PowerPoint mở chỉ đọc ở trạng thái
sẵn sàng; Mascot hiện công cụ **Trình chiếu (F5)**. Kết thúc trình chiếu về
trạng thái chờ, bắt đầu lại được. **Ngắt gắn bài** kết thúc helper và chỉ
đóng bản PowerPoint do phiên đó mở; không ghi nguồn, không đóng bài khác.

`TeachingSession` giữ snapshot bài, revision, bản giọng, fingerprint tệp và
ánh xạ slide độc lập với bài đang duyệt. Mở xem bài khác hoặc trở lại thư
viện không đổi liên kết. Thư viện có thao tác dạy; Mascot nổi chọn được bài
thư viện hoặc PPTX. Chọn bài mới chỉ mở bước xác nhận. Chuẩn bị bài mới
thành công mới ngắt helper cũ và gắn helper mới; hủy xác nhận giữ bài cũ.

Mascot hiện ngôn ngữ theo đúng slide thực tế. Bản có loa dùng cùng Player
của PowerPoint cho thao tác ở slide và Mascot, có tạm dừng/tiếp tục/dừng;
theo dõi phát trực tiếp để dừng hàng đọc cache và tránh các loa BiliClass
phát chồng. Slide không đủ vùng nhúng vẫn dạy bằng bản gốc kèm cache nếu
phù hợp. Hàng cache chờ PowerPoint xác nhận dừng media trước khi phát và
chỉ đọc WAV có sẵn; đổi slide, ngắt hoặc dừng hủy kết quả chờ. Không suy
luận giọng trong phiên dạy. Giữ thứ tự Việt–Anh và các bản giọng cũ.

Nút Trước/Sau trên Mascot chuyển trang; điều khiển hiệu ứng vốn có của
PowerPoint qua bàn phím/chuột giữ nguyên. Mascot kéo/về góc giữ cơ chế vị
trí hiện có, menu tự vừa nội dung và cuộn khi dài. Bản có loa đã tải có
thể mở lại từ Mascot mà không cần có cache hoặc bản giọng thư viện trên
máy nhận. Công cụ trợ giảng dùng nội dung đã chuẩn bị của bài đang gắn;
phát triển AI mới chưa nằm trong mốc này.

## Kiểm chứng nguồn

97 kiểm thử liên quan qua bằng `.venv`: PowerPoint, hàng đọc, binding,
cache-only/cancel, nhập và xuất narration, thư viện, chuyển đổi, thời gian
tiến trình, vị trí dữ liệu, vòng đời lớp và bộ cài. Ruff kiểm ứng dụng và
các kiểm thử/script thay đổi.

`qt_teaching_session_smoke.py` dùng Qt và Office thật, dữ liệu cô lập:
voice 1080/1366, không thêm tab; mở chờ/F5/chuyển trang/kết thúc/mở lại;
đọc loa nhúng và pause/resume; nút ngôn ngữ theo slide; duyệt bài khác và
thu nhỏ không đổi binding; chọn/hủy/đổi bài từ Mascot; bài không giọng và
PPTX đã nhúng loa ngoài thư viện; nguồn giữ nguyên. WAV im lặng làm fixture,
không chạy model hoặc đánh giá chất lượng giọng. Không có cảnh báo QML.

Các lượt Qt workspace/kết quả trước đó cũng qua: cấu hình trước file và
giữ lựa chọn; script ảnh/slide trắng; tạo/dừng/tiếp tục; ZIP và PowerPoint;
preview, layout, bản giọng, đồng hồ tạo giọng, subject Mascot. Kiểm Office
riêng xác nhận sẵn sàng, bắt đầu, chuyển, kết thúc và bắt đầu lại không
ghi thay đổi nguồn. Chưa chứng nhận máy chiếu/màn hình vật lý thứ hai.

Office API: [SlideShowView.Player](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.player),
[PpPlayerState](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.ppplayerstate).

## Đóng gói

[Release RC68](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc68).

- Nguồn: `40016092fea0f079a1e495546c23b74687372b93`.
- ZIP `BiliClass-RC68-Windows.zip`: 840272232 byte, 4187 tệp.
- ZIP SHA-256: `9f10a890754f4f06441bdb1ca76f1c77b3405dfdf08e5c09e608b1c3ccd4afec`.
- EXE SHA-256: `ba29e632b5b55413a75c2041ecc64d2478afad6779026a2e4d3661ae07733d4e`.

Biên dịch 121 module ứng dụng một lần; tái sử dụng runtime/model bất biến
của RC67. Kiểm SHA-256/CRC toàn bộ ZIP. Model, EXE, key, dữ liệu cá nhân
và báo cáo kiểm tra nằm ngoài Git.

Cài tại `F:/Applications/BiliClass/1.0.0rc68`. Tám cấu hình EXE qua: Home,
giọng chưa có nguồn và đã chọn bài ở 1080/1366; Thư viện 1080; Cài đặt
1366. Không truyền Python path nguồn cho EXE; QML và icon bản cài khớp
nguồn, không có cảnh báo QML. Engine/model giữ nguyên; không chạy lại suy
luận model cho mốc vận hành này.

Đóng RC67 bình thường và mở RC68 ở tab giọng qua Explorer. Ứng dụng còn
chạy độc lập khi launcher kết thúc và qua mười kiểm tra phản hồi. Giữ
nguyên 18 bản ghi bài (gồm thùng rác), 1095 WAV, tùy chọn, hash key mã
hóa, tên key và lịch sử dịch. Checkpoint 354/354 không tự chạy lại.
Shortcut Desktop/Start chuyển sang RC68. Tài liệu hướng dẫn được cập nhật
đúng luồng mới.

Đã phát hành ZIP/checksum; digest và dung lượng phía GitHub khớp tệp được
kiểm tra. Feed công khai chọn đúng RC68 cho bộ cập nhật RC34/RC67, khớp
dung lượng/hash; RC68 không tự báo cập nhật chính nó. Chưa kiểm cài trên
máy Windows thứ hai.
