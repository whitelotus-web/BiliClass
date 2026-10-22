# RC148 — Thư viện theo giọng đọc và cải thiện đầu ra

Thư viện có ba nhóm Tất cả, Chưa có giọng, Đã có giọng, kèm số bài
theo bộ lọc. Đây là các cách xem cùng một bài, không tạo bản sao.
Chỉ bản giọng hoàn tất và kiểm tra được âm thanh mới vào nhóm Đã có
giọng; bản thiếu đoạn vẫn ở Chưa có giọng. Đổi nhóm bỏ chọn để tránh
tác động lên bài đang ẩn. Giữ bộ lọc môn, lớp, trạng thái và ngôn ngữ.

Tạo giọng đã chọn đưa các bài chưa có giọng vào cùng hàng đợi hiện có.
Giữ đúng ID/revision của bài, không nhập lại thành bản trùng. Bỏ qua
bài đã có giọng hoàn tất, thông báo số bài đã bỏ qua. Thay đổi bài sau
khi chọn sẽ chặn kết quả cũ. Mở bài từ máy dùng luồng mở PowerPoint
và gắn Mascot hiện có; không tự khởi động tạo giọng hay chuyển ngữ.

Hàng đợi của cả Chuyển đổi và Tạo giọng nằm trong khung cấu hình.
Cấu hình vẫn hiện và khóa khi chạy; có phần trăm, thời gian từng bài
và tổng thời gian. Đồng hồ cập nhật cả khi không có thông báo tiến độ,
giữ thời gian đã chạy qua checkpoint, không tính thời gian tạm dừng.
Dừng, Tiếp tục, thử lại bài lỗi và nguồn/WAV giữ cách hoạt động cũ.

Khoảng nghỉ giữa các đoạn tăng từ 450 ms lên 1.100 ms, dùng chung
khi phát qua tool và ghép PowerPoint. WAV gốc không đổi. Cache bản
chiếu/bản tự lưu đổi dấu phiên bản để không dùng nhầm bản ghép cũ;
PowerPoint đã xuất trước đó cần xuất lại để có khoảng nghỉ mới.
Chưa thêm nút chỉnh tốc độ/khoảng nghỉ trực tiếp trên Mascot.

Khóa cả đơn vị có số mũ, gồm cm⁻¹ và số mũ native của PowerPoint,
trước khi dịch. Cache đơn vị cũ không được dùng lại. Công thức cấu
tạo hữu cơ có bằng chứng như CH3–O–CH3 dùng “single bond”, dấu =
dùng “double bond”; không suy tên hợp chất từ công thức phân tử.
Chỉ công thức thay cách đọc mới đổi khóa âm thanh; giữ các WAV đúng
như HCN/CO2. Điểm hình học đánh số không tự thành liên kết hóa học.

Ghép thuật ngữ “liên kết cộng / hoá trị” khi hai dòng OCR đã được
xác minh, gần nhau và cùng cột/căn giữa; giữ dữ liệu OCR gốc. Bản dịch
thuật ngữ ghép được giới hạn gần cột nguồn, bỏ qua khi không có chỗ
an toàn. Đây chưa phải bộ dựng lại mọi bảng trong ảnh. Chữ/nhãn chưa
xác minh và phần trong ảnh chưa đặt được vẫn có thể cần xử lý thêm.

Đã kiểm tra trên bản sao cặp bài Hóa 44 slide do người dùng gửi.
Nguồn và sản phẩm gửi từ máy khác giữ nguyên byte; các media gốc
được giữ trong bản dựng thử. Đã render cả 44 slide của hai bản để
kiểm tra bằng Office, xem trực tiếp các trang có bằng chứng lỗi và
render lại các trang sửa. Phép đo bố cục không chứng nhận đúng toàn
bộ nội dung hay OCR. Không sửa các phương án nhiễu của câu trắc nghiệm.

442 pytest liên quan đạt trong môi trường dự án. Ruff và compileall
đạt. Ba Qt smoke đạt: hàng đợi/thư viện (sáng/tối, 1080/1366 px), xuất
bài và kết quả giọng. Kiểm nhóm tự đổi, bỏ chọn khi đổi tab, tạo hàng
loạt giữ ID và bỏ qua bản đã có giọng, route mở file ngoài vào luồng
Mascot, đồng hồ chạy/dừng/tiếp tục, thứ tự một bài/lần và WAV mẫu.
Không tự động chọn file qua hộp thoại Windows; kiểm mode và receiver
QML bằng URL cục bộ. Không có cảnh báo QML; kiểm route mở file không
thay cho một phiên giảng dạy thật đầy đủ với mọi PowerPoint ngoài tool.

Đã phát hành từ `14c71c608d463280478ccd30587aec4117d621b2`;
[Source checks GitHub](https://github.com/whitelotus-web/BiliClass/actions/runs/39758371644) đạt cho đúng commit gói.
[Gói RC148](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc148) có 1,258,143,596 byte, SHA-256
`bdcb32edd432c080102b377cba9a2058a9259a1635f726fe8f1c0ff345e77d41`. 59 tệp QML/qmldir và bytecode ứng dụng khớp nguồn;
ZIP, digest/tag và phát hiện bản cập nhật công khai đạt. Đã cài và
mở Trang chủ từ Explorer; Mascot khởi động ẩn. Hồ sơ, cấu hình/key,
nguồn và 1752 WAV tham chiếu giữ nguyên.

39 WAV trong bài người dùng gửi dài khoảng 697 giây, không có mẫu
clipping trong phép đo PCM. Đây là kiểm mức tín hiệu, không thay
cho đánh giá nghe/thiết bị loa hoặc chứng nhận cách phát âm từng từ.
