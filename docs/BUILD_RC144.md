# RC144 — Tự hoàn thiện trước khi báo kết quả

Không đếm các ghi chú chung về OCR, công thức, thứ tự lời đọc hoặc
hiệu ứng như lỗi của toàn bộ bài. Khi chỉ có giới hạn kiểm tra,
kết quả là một dòng trung tính, không có yêu cầu duyệt từng slide.
Chi tiết và phạm vi vẫn giữ nguyên. Lỗi cụ thể, thiếu nội dung, đề
gốc có vấn đề, phép đo chưa chạy hoặc tương phản đo được còn lỗi
vẫn được nêu rõ; nút để tool thử lại có ngay trên khung kết quả.
Cùng thành phần ở Chuyển đổi và Tạo giọng đọc, sáng và tối.

Bộ tự căn chữ trước đây chỉ thay được text box. Nay xử lý riêng từng
ô bảng theo ID bảng và hàng/cột, kể cả khi Office lưu bảng có Math
trong Choice/Fallback. Đếm lỗi từng ô để không bỏ mất một phần cải
thiện. Không áp AutoSize/WordWrap không được Office hỗ trợ lên cell;
đo và giảm cỡ chữ theo lưới gốc, không để Office tự nới hàng làm bảng
chạy ra ngoài slide. Chỉ lấy thân chữ đã chọn từ bản Office, giữ
nguyên lưới, ô khác, media, từ ngữ và cây công thức.

Tự sửa màu chữ khi có bằng chứng thiếu tương phản trên nền đặc,
đo lại trước khi nhận kết quả, và kiểm lại sau căn cỡ chữ. Không
lấy TextRange.Font làm phép đo màu của Office Math vì nó có thể
khác định dạng run thật; phần đó vẫn thuộc giới hạn kiểm tra.

Toàn luồng chạy tự động trước khi hoàn thành; bài cũ có lỗi chưa
được xử lý bằng phiên bản mới được thử khi mở, tối đa ba lượt căn
chữ, giữ bản tốt nhất và dừng khi không tiến bộ. Dấu phiên bản/hash
chặn lặp vô hạn. Bản sửa dùng revision và giữ nguồn/lịch sử; chỉ
giữ WAV khi nội dung đọc không đổi. Cache phép đo đổi phiên bản.
Không tự gán nhãn giáo viên đã duyệt hoặc chứng nhận mọi ý nghĩa.

Đã kiểm tra Qt với PowerPoint thật: mở fixture có hai ô tràn và
chữ thiếu tương phản, không bấm nút sửa; tool tự sửa, đo lại còn
0 lỗi cụ thể, giữ chữ/lưới/ô khác/Math và bản gốc. Qt cảnh báo lỗi
thật và trạng thái 16 slide có ghi chú chung đều qua ở hai công cụ,
sáng/tối, thu gọn/mở rộng, 1080/1366; không QML warning.

Bản sao bài thật 16 slide: nguồn, media và Math giữ nguyên; không
FAIL trong phép đo bố cục. Những ghi chú giới hạn vẫn trong chi tiết,
không đổi thành lời khẳng định đã xác minh mọi chữ trong ảnh. Không
ghi đè bài hoặc âm thanh thật. Không thêm hàng đợi hay chạy nhiều bài.

108 pytest liên quan trong `.venv`, Ruff toàn kho và compileall qua.
Trên bài thật, tool tự sửa thêm tương phản hai ô ở slide 4 rồi đo
lại; bản xem trước vẫn cần được hiểu trong phạm vi phép kiểm tra,
không đồng nghĩa mọi bố cục đều đẹp hoặc toàn bộ nội dung đã đúng.

Đã phát hành [RC144](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc144)
từ `0b6aa21d2fda9965a6581c8ac51adb8f57bd5489`. Source checks GitHub đạt.
ZIP 1.258.096.170 byte; SHA-256
`e8d8c3e3de9c52a1ec30d153d96d2b59ec7b23f9edab69ff498393e4dcccf883`.
Đã so khớp mã QML/bytecode, toàn bộ ZIP, digest và tag công khai;
kiểm cập nhật phát hiện RC144. Bản cài mở Trang chủ từ Explorer,
Mascot ẩn; hồ sơ, cấu hình giọng, thư viện và WAV tham chiếu giữ nguyên.
