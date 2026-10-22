# RC141 — Dịch và bố cục bài giảng Toán

Lượt rà soát các bài Toán mới phát hiện câu chữ Việt nằm trong
đối tượng Office Math bị coi là công thức thuần, nên một số đáp án
không được dịch. Bộ trích xuất nay tách các run văn bản thường để
dịch và dàn dòng; giữ các cây công thức, biến, phân số và ma trận.
Bản nguồn bất biến được giữ để đối chiếu. Cỡ chữ Office Math được
đọc đúng, thay vì dùng mặc định 18 pt rồi phóng lớn nhầm chữ 48 pt.

Số lượng được hiện cho bộ dịch hiểu ngữ pháp, nhưng giá trị và XML
vẫn khóa bằng ID. Cache tách theo giá trị thực, tránh dùng chung
ngữ pháp số ít/số nhiều cho hai câu có placeholder giống nhau.
Có một lần phục hồi giới hạn nếu dịch làm mất khóa; không lặp lại
cả bài. Biến đếm hình học cũng có ngữ cảnh, không đổi công thức.
Không thay cơ chế khóa toàn bộ công thức Hóa học.

Bổ sung nhãn Activity/Example/Worksheet, Definition/Contents/Answer,
các mệnh đề hình học nguyên văn và cách dùng plane/face/incidence.
Không suy luận đáp án đúng/sai hay sửa giả thiết trong nguồn. Thuật
ngữ giáo viên khóa được ưu tiên. Đối chiếu thuật ngữ hình học với
[OpenStax](https://openstax.org/books/calculus-volume-3/pages/2-5-equations-of-lines-and-planes-in-space).

Khung song ngữ dành chỗ cho nhãn Hoạt động/Ví dụ, dừng trước hàng
kế tiếp và chia lại hai cột trước hình minh họa. Dải đáp án so chi
phí xuống dòng giữa cột và xếp Việt–Anh để giữ cỡ chữ tốt hơn. Chữ
thường tách từ Office Math giữ màu/font gốc và được Office đo lại.
Bộ căn chữ nhận cả freeform có văn bản chỉnh sửa được; trước đây
loại tiêu đề này được báo tràn nhưng bị bỏ qua khi tự sửa. Giữ
nguyên đường bao, ảnh, ký hiệu và các điều kiện bảo vệ công thức.

Chọn vị trí lỗi hoặc mở phần chi tiết tự chuyển ảnh đến đúng slide
ở cả hai công cụ. OCR thấy chữ trong ảnh nhỏ trên trang có chữ
chỉnh sửa được vẫn được đưa vào danh sách cần đối chiếu. Nhận xét
đã kiểm chứng về đề gốc có loại CHECK riêng, không sửa đề/đáp án.
Không coi ảnh đã render hoặc 0 FAIL là chứng nhận đúng nội dung.

Đã dựng và xem 89 ảnh PowerPoint của bốn bản thử 18/20/13/38 slide;
không FAIL trong các phép kiểm tra tràn chữ/bố cục hiện có. 2.017
run ký hiệu toán học có trong đầu ra và media nguồn được giữ theo
hash. Chữ raster và ý nghĩa chuyên môn chưa thể chứng nhận chỉ từ
các phép kiểm tra này. Một số trang dày chữ vẫn cần người xem lại.
Các lỗi giả thiết phát hiện từ nguồn được ghi riêng theo slide,
không tự sửa đề hay đánh dấu giáo viên đã duyệt.

231 pytest liên quan trong `.venv` đạt; sau bổ sung lưu lại kế hoạch
cặp và vùng ảnh, 40 ca thư viện/hoàn thiện/chẩn đoán đạt. Hai nhóm có
giao nhau, không cộng thành số ca riêng. Qt chẩn đoán đạt 16 trạng
thái sáng/tối, thu gọn/mở rộng, hai cỡ màn và cả hai công cụ; kiểm
mở chi tiết/chọn lỗi chuyển đúng ảnh, tương phản tối thiểu 6,31:1.
Qt chuyển đổi giữ cấu hình/loading tại chỗ, dừng/tiếp tục/hủy và xem
kết quả qua với API fixture, Office thật; không cảnh báo QML. Có log
Windows điều chỉnh kích thước cửa sổ theo màn hình. Ruff và compileall
đạt. Không khẳng định đã nghe/chấm toàn bộ giọng đọc hay thử máy yếu.

Ba bản trong thư viện được cập nhật theo revision, giữ ID và nguồn
cũ/lịch sử: hai bản chưa có giọng nhận bản dịch và bố cục đã kiểm;
bản vừa tạo giọng chỉ sửa bố cục, giữ nguyên lời và 147 khóa âm thanh.
Bản có giọng cũ còn lại được giữ; bản dịch thử cải thiện nằm riêng.
Giữ giọng cũ không có nghĩa đã cập nhật giọng theo mọi câu dịch mới.
Đối chiếu SHA-256 trước/sau của 3.090 WAV đạt; các bài khác không đổi.
Kế hoạch cặp Việt–Anh và danh sách ảnh được lưu lại cùng bản kiểm tra,
tránh dùng ánh xạ cũ sau khi thay bản sửa.
Thư viện, bản sao thử, âm thanh, ảnh và báo cáo cá nhân ở ngoài Git.

Gói 1.0.0rc141 dựng một lần từ commit
`6445b69c385936d7e96098306d3be830fe774f14`, dùng runtime RC140 đã
đối chiếu. 4.676 tệp ứng dụng, 56 QML và bytecode các module trọng
yếu khớp commit; ZIP kiểm từng tệp đạt. Dung lượng 1.258.068.730 byte;
SHA-256 `6bfb607306f89e0fdedffffbcc745393f0b0ae4cc962c48179ea857131d86d05`.
Home trong bản độc lập được xem ở dữ liệu cô lập, không PYTHONPATH
hay model phát triển, không cảnh báo QML. Đã cài và mở từ Explorer
tại `F:/Applications/BiliClass/1.0.0rc141`, Home và Mascot ẩn, cửa sổ
phản hồi; đối chiếu hồ sơ/key/tùy chọn, bài và WAV tham chiếu đạt.

Kiểm trên GitHub phát hiện bước Ruff toàn kho dừng ở 32 lỗi định
dạng/import/biến không dùng trong các tệp ngoài nhóm vừa sửa. Đã
sửa trực tiếp, không bỏ bước kiểm tra hay hạ quy tắc. Mẫu COM của
hai kiểm thử cache còn thiếu thuộc tính Text mà bộ chẩn đoán dùng
để trích vùng tràn; bổ sung mẫu đầy đủ, giữ nguyên các khẳng định
hai lỗi tràn phải còn sau khi dùng cache. Các thay đổi app tiếp theo
chỉ là thứ tự import/khoảng trắng; gói RC141 vẫn ghi đúng commit dựng
nêu trên. Không ghi lại artifact để che lịch sử kiểm tra bị đỏ.
Ruff toàn app/scripts/tests, compileall và đúng nhóm portable của
workflow đã chạy lại trong `.venv`: 383/383 qua. Nhóm cache/nhập
slide có 17/17 qua; Qt chẩn đoán chạy lại đạt. Corpus cấu trúc không
Office cũng qua; không dùng kết quả cấu trúc để tuyên bố bố cục đẹp.

Gói đã tải lên bản nháp, chờ kiểm nguồn mới trên GitHub trước khi
phát hành. Không thêm hàng đợi hoặc đồng bộ sửa/lưu bên ngoài.
