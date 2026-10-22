# RC142 — Nội dung trong Title, bảng và chữ trong ảnh

Nguồn 1.0.0rc142 sửa đường đọc nội dung và bố trí bản dịch của bài
Toán 16 slide vừa thử. Không coi loại placeholder Title là bằng chứng
đủ để nhận một tiêu đề: đoạn dài, nhiều đoạn, câu hỏi và câu dẫn đề
được nhận như thân bài, kể cả khi tác giả dùng khung Title.

Ở trang hỏi/đáp có đồng hồ, nguyên nhân cụ thể còn là bảng: bộ đọc
lấy mặc định 18 pt thay vì cỡ chữ 44 pt của từng ô, rồi phóng các run
khi chuẩn hóa theo canvas lớn. Nay đọc font từng ô, giữ lưới bảng,
ghép ngắt dòng thủ công trong cùng một câu để dịch đủ ý và không lặp
đánh số ở dòng Anh. Ô chừa chỗ cho ảnh/nhãn và giữ cỡ chữ theo nguồn.
Ô chỉ có Office Math vẫn nhận tọa độ và tỉ lệ của bảng. Câu hỏi về
phần vòng quay giữ đúng chiều clockwise/counterclockwise; nhãn Giải
dùng Solution, Sản phẩm trong bài Toán dùng Expected result.

Đoạn ISS trong ảnh trước đây bị bỏ vì hiệu ứng xuất hiện và vì hai
bộ đọc không đồng ý trên dòng dài. Bộ đọc nay cắt dòng dài tại khoảng
trắng thật trước khi nhận diện, so lại chữ/số và gom đoạn văn cùng
hàng. Kết quả chưa xác minh hoàn toàn là bản nháp; chỉ đặt vào vùng
trống kiểm từ ảnh PowerPoint, không che ảnh gốc hoặc tự đưa vào lời
đọc. Hiệu ứng xuất hiện toàn ảnh có ánh xạ chắc được nhân cho bản
dịch trong cùng click; trigger/phạm vi chưa biết vẫn được bỏ qua.
Bản nháp không dùng để che chữ trong chế độ English 100%.

Căn công thức nay thay cỡ chữ thật khi PowerPoint bỏ qua fontScale,
giữ nguyên cây ký hiệu. Bộ đo nhận cả từng ô bảng bằng ID bảng và
tọa độ ô, không đọc thuộc tính Id không dùng được của cell Shape.
Ô định dạng nhưng rỗng không bị báo tràn. Cache phép đo đổi phiên bản
để không dùng lại kết quả cũ. Chi tiết giữ riêng vị trí từng ô; nút
Trước/Sau đồng bộ lại lựa chọn lỗi, không gửi yêu cầu xem lặp.
Cả Chuyển đổi và Tạo giọng đọc có Kiểm tra lại khi còn CHECK, đồng
thời không thông báo đã sửa nội dung chỉ vì phép đo không còn FAIL.

Kiểm trên bản sao của bài 16 slide: media nguồn giữ nguyên theo hash;
739 run ký hiệu toán gốc có trong đầu ra. Đã dựng và xem ảnh PowerPoint,
không còn FAIL trong các phép đo tràn chữ hiện có. Vẫn có CHECK cho
ảnh, công thức, lời đọc và hiệu ứng; một số trang dày chữ vẫn cần xem
trước khi chiếu. Chưa chứng nhận mọi thuật ngữ hoặc nghe toàn bộ giọng.

185 pytest liên quan trong `.venv` qua. Nhóm portable đúng workflow
GitHub có 384 ca qua; hai nhóm có giao nhau, không cộng làm tổng riêng.
Corpus cấu trúc không Office qua. Qt chẩn đoán sáng/tối, hai cỡ màn,
cả hai công cụ, điều hướng hai chiều qua; Qt chuyển đổi với API fixture
và PowerPoint thật qua, không QML warning. Ruff toàn kho và compileall
qua. Bài/âm thanh/ảnh/báo cáo cá nhân không vào Git; không thêm hàng đợi
hoặc xử lý nhiều bài đồng thời, giữ các tab Cài đặt hiện có.

Đã phát hành [RC142](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc142)
từ commit `1c6b045cd67604f9869b360d55500d390de759de`. Gói dựng một
lần từ runtime RC141 đã đối chiếu hash; bytecode các module mới/sửa
và 56 QML khớp commit. ZIP 1.258.085.562 byte, SHA-256
`98d1ca26d6eb409b73fd997511936417748f508b82ace55e01168118273c30a1`.
GitHub xác nhận digest; tag và updater công khai trỏ đúng bản này.
[Source checks](https://github.com/whitelotus-web/BiliClass/actions/runs/39715228190)
của commit dựng đã thành công.

Bản độc lập khởi động Home và nhận lại đoạn văn trong ảnh bằng bộ
model đóng gói, dùng dữ liệu cô lập, bỏ đường dẫn runtime/model phát
triển; giữ số liệu và click xuất hiện đúng. Đã cài/mở Home từ Explorer,
Mascot ẩn, cửa sổ phản hồi, icon/shortcut đúng; không QML warning.
Hồ sơ, API key, tùy chọn, bài và 1.746 WAV tham chiếu khớp trước/sau
cài. Bài thật đang được tạo giọng đã thay đổi trong lúc rà soát: chặn
ghi đè theo trạng thái mới, giữ bản dịch/bố cục cải thiện thành bản
xem riêng, không gán giọng cũ cho lời mới.

Theo yêu cầu dọn ổ, đã xóa 18 ZIP cũ sau khi đối chiếu size/digest
với bản đã phát hành trên GitHub, 18 thư mục build tạm của các mốc đó
và tám thư viện thử trung gian của lượt này. Giữ bản cuối, metadata
build, runtime nền/RC142, ứng dụng cài, thư viện, nguồn và âm thanh,
model cá nhân. Nhật ký chi tiết ở ngoài Git. Không thêm hàng đợi hoặc
đồng bộ sửa/lưu bên ngoài trong đợt này.
